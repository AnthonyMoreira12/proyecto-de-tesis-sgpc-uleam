"""
ViewSet para la gestión de proyectos del SGPC ULEAM.

Funcionalidades:

- Listado paginado de proyectos.
- Consulta de proyectos según la visibilidad del usuario.
- Búsqueda y filtros por texto, año y estado.
- Consulta de años disponibles.
- Creación, actualización y eliminación administrativa.
- Gestión del equipo investigador.
- Cambio de estado del proyecto.
- Extensión de la fecha de finalización.
- Carga de documentos mediante multipart/form-data.

Permisos:

- Usuarios autenticados:
    - Listar proyectos visibles.
    - Consultar proyectos visibles.
    - Consultar años disponibles.
    - Consultar el equipo investigador.

- Administradores:
    - Crear proyectos.
    - Modificar proyectos.
    - Eliminar proyectos.
    - Gestionar autores.
    - Cambiar estados.
    - Extender fechas.
"""

import logging

from django.db import (
    DatabaseError,
    IntegrityError,
    transaction,
)
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import (
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import Proyecto
from core.proyectos.serializers.proyectos_proyecto_serializers import (
    ProyectoAutorReadSerializer,
    ProyectoAutorResumenSerializer,
    ProyectoListSerializer,
    ProyectoSerializer,
)
from core.proyectos.selectors.proyectos_proyecto_selectors import (
    get_filtered_proyectos_queryset_for_user,
    get_proyectos_available_years_for_user,
    proyectos_base_queryset,
)
from core.proyectos.services.proyectos_proyecto_services import (
    normalize_proyecto_autores_payload,
    require_project_admin,
    resolver_estado_destino,
    sync_proyecto_autores,
    user_is_project_admin,
)


logger = logging.getLogger(__name__)


# ============================================================
# PERMISO ADMINISTRATIVO
# ============================================================

class IsProjectAdministrator(BasePermission):
    """
    Permite el acceso únicamente a administradores de proyectos.
    """

    message = (
        "No tienes permisos administrativos para gestionar "
        "proyectos."
    )

    def has_permission(
        self,
        request,
        view,
    ):
        return user_is_project_admin(
            request.user
        )


# ============================================================
# PAGINACIÓN
# ============================================================

class ProyectoPagination(PageNumberPagination):
    """
    Paginación estándar del listado de proyectos.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# ============================================================
# VIEWSET
# ============================================================

class ProyectoViewSet(viewsets.ModelViewSet):
    """
    Gestiona proyectos institucionales y equipos investigadores.
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    pagination_class = ProyectoPagination

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    ]

    lookup_field = "pk"
    lookup_value_regex = r"\d+"

    # ========================================================
    # RESPUESTA FINAL
    # ========================================================

    def finalize_response(
        self,
        request,
        response,
        *args,
        **kwargs,
    ):
        """
        Evita que el navegador conserve listados o detalles
        desactualizados.
        """
        response = super().finalize_response(
            request,
            response,
            *args,
            **kwargs,
        )

        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, "
            "max-age=0, private"
        )
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response

    # ========================================================
    # PERMISOS
    # ========================================================

    def get_permissions(self):
        """
        Aplica permisos administrativos antes de procesar las
        operaciones de escritura.
        """
        action_name = getattr(
            self,
            "action",
            None,
        )

        request_method = str(
            getattr(
                self.request,
                "method",
                "",
            )
            or ""
        ).upper()

        administrative_actions = {
            "create",
            "update",
            "partial_update",
            "destroy",
            "cambiar_estado",
            "extender_fecha",
        }

        authors_write = bool(
            action_name == "autores"
            and request_method in {
                "PUT",
                "PATCH",
            }
        )

        if (
            action_name in administrative_actions
            or authors_write
        ):
            permission_classes = [
                IsAuthenticated,
                IsProjectAdministrator,
            ]

        else:
            permission_classes = [
                IsAuthenticated,
            ]

        return [
            permission_class()
            for permission_class
            in permission_classes
        ]

    # ========================================================
    # SERIALIZER
    # ========================================================

    def get_serializer_class(self):
        """
        Utiliza una representación ligera para el listado y una
        representación completa para el resto de operaciones.
        """
        if self.action == "list":
            return ProyectoListSerializer

        return ProyectoSerializer

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self):
        """
        Aplica visibilidad, búsqueda y filtros.

        Alias admitidos:

        - q o search
        - anio o year
        - estado o status
        """
        query_params = self.request.query_params

        query = (
            query_params.get("q")
            or query_params.get("search")
            or ""
        )

        year = (
            query_params.get("anio")
            or query_params.get("year")
            or ""
        )

        project_status = (
            query_params.get("estado")
            or query_params.get("status")
            or ""
        )

        return (
            get_filtered_proyectos_queryset_for_user(
                self.request.user,
                q=query,
                anio=year,
                estado=project_status,
            )
        )

    # ========================================================
    # CREACIÓN Y ACTUALIZACIÓN
    # ========================================================

    def perform_create(
        self,
        serializer,
    ):
        """
        Registra al administrador autenticado como creador.
        """
        require_project_admin(
            self.request.user
        )

        serializer.save(
            creado_por=self.request.user
        )

    def perform_update(
        self,
        serializer,
    ):
        """
        Actualiza el proyecto después de verificar permisos.
        """
        require_project_admin(
            self.request.user
        )

        serializer.save()

    # ========================================================
    # UTILIDADES INTERNAS
    # ========================================================

    def _get_locked_project(self):
        """
        Recupera y bloquea exclusivamente el registro del
        proyecto.

        Se utiliza un queryset sin joins para evitar errores de
        PostgreSQL al aplicar FOR UPDATE sobre relaciones
        opcionales.
        """
        lookup_url_kwarg = (
            self.lookup_url_kwarg
            or self.lookup_field
        )

        lookup_value = self.kwargs.get(
            lookup_url_kwarg
        )

        queryset = (
            Proyecto.objects
            .select_for_update(
                of=("self",)
            )
            .all()
        )

        project = get_object_or_404(
            queryset,
            **{
                self.lookup_field: lookup_value,
            },
        )

        self.check_object_permissions(
            self.request,
            project,
        )

        return project

    def _get_project_for_response(
        self,
        project_id,
    ):
        """
        Recupera el proyecto con todas las relaciones necesarias
        para construir la respuesta.
        """
        return get_object_or_404(
            proyectos_base_queryset(),
            pk=project_id,
        )

    def _clear_project_cache(
        self,
        project,
    ):
        """
        Limpia las relaciones precargadas después de modificar el
        equipo investigador.
        """
        if hasattr(
            project,
            "_prefetched_objects_cache",
        ):
            project._prefetched_objects_cache = {}

        if hasattr(
            project,
            "_serializer_participaciones_cache",
        ):
            delattr(
                project,
                "_serializer_participaciones_cache",
            )

    def _extract_authors_payload(
        self,
        request,
    ):
        """
        Obtiene la lista de autores desde cualquiera de los
        formatos admitidos.

        Campos admitidos:

        - autores_data
        - autores
        """
        request_data = request.data

        if isinstance(
            request_data,
            list,
        ):
            return request_data

        if hasattr(
            request_data,
            "get",
        ):
            for field_name in (
                "autores_data",
                "autores",
            ):
                if field_name not in request_data:
                    continue

                field_value = request_data.get(
                    field_name
                )

                if field_value is not None:
                    return field_value

        raise ValidationError(
            {
                "autores_data": (
                    "Debe enviar la lista de autores "
                    "del proyecto."
                )
            }
        )

    def _parse_extension_date(
        self,
        raw_value,
    ):
        """
        Valida la fecha recibida por el endpoint de extensión.
        """
        date_field = serializers.DateField(
            error_messages={
                "invalid": (
                    "La nueva fecha debe tener el formato "
                    "AAAA-MM-DD."
                ),
            }
        )

        try:
            return date_field.run_validation(
                raw_value
            )

        except serializers.ValidationError as exc:
            raise ValidationError(
                {
                    "fecha_fin_prorrogada": (
                        exc.detail
                    )
                }
            ) from exc

    def _get_project_file_reference(
        self,
        project,
    ):
        """
        Captura el almacenamiento y nombre del PDF del proyecto.
        """
        file_field = getattr(
            project,
            "archivo_pdf",
            None,
        )

        if not file_field:
            return None, None

        file_name = getattr(
            file_field,
            "name",
            None,
        )

        storage = getattr(
            file_field,
            "storage",
            None,
        )

        if (
            not file_name
            or storage is None
        ):
            return None, None

        return storage, file_name

    def _schedule_project_file_delete(
        self,
        storage,
        file_name,
    ):
        """
        Elimina el archivo físico solamente después del commit.
        """
        if (
            storage is None
            or not file_name
        ):
            return

        def delete_file():
            try:
                if storage.exists(
                    file_name
                ):
                    storage.delete(
                        file_name
                    )

            except Exception:
                logger.exception(
                    (
                        "No fue posible eliminar el PDF "
                        "del proyecto '%s'."
                    ),
                    file_name,
                )

        transaction.on_commit(
            delete_file
        )

    def _project_serializer_context(
        self,
        *,
        allow_state_transition=False,
    ):
        """
        Construye el contexto del serializer y controla si una
        acción especializada puede cambiar el estado.
        """
        context = self.get_serializer_context()

        if allow_state_transition:
            context[
                "allow_state_transition"
            ] = True

        return context

    def _team_serializer_class(
        self,
        request,
    ):
        """
        Entrega datos personales del equipo únicamente a
        administradores.
        """
        if user_is_project_admin(
            request.user
        ):
            return ProyectoAutorReadSerializer

        return ProyectoAutorResumenSerializer

    def _database_unavailable_response(
        self,
        detail,
    ):
        """
        Devuelve una respuesta controlada ante errores temporales
        de base de datos.
        """
        return Response(
            {
                "detail": detail,
            },
            status=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

    # ========================================================
    # ELIMINACIÓN
    # ========================================================

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Elimina un proyecto dentro de una transacción y protege
        la operación frente a modificaciones simultáneas.
        """
        require_project_admin(
            request.user
        )

        try:
            with transaction.atomic():
                project = self._get_locked_project()

                (
                    file_storage,
                    file_name,
                ) = self._get_project_file_reference(
                    project
                )

                project.delete()

                self._schedule_project_file_delete(
                    file_storage,
                    file_name,
                )

        except ProtectedError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No se puede eliminar el proyecto "
                        "porque está relacionado con otros "
                        "registros protegidos."
                    )
                }
            ) from exc

        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No se puede eliminar el proyecto "
                        "porque mantiene relaciones activas."
                    )
                }
            ) from exc

        except DatabaseError:
            logger.exception(
                "Error de base de datos al eliminar un proyecto."
            )

            return self._database_unavailable_response(
                (
                    "No fue posible eliminar el proyecto "
                    "debido a un error temporal de la "
                    "base de datos."
                )
            )

        except OSError:
            logger.exception(
                (
                    "Error de almacenamiento al eliminar "
                    "un proyecto."
                )
            )

            return Response(
                {
                    "detail": (
                        "No fue posible eliminar el proyecto "
                        "debido a un problema con el "
                        "almacenamiento de archivos."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    # ========================================================
    # AÑOS DISPONIBLES
    # ========================================================

    @action(
        detail=False,
        methods=[
            "get",
        ],
        url_path="anios",
        url_name="anios",
    )
    def anios(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Devuelve los años disponibles según la visibilidad y los
        filtros actuales.
        """
        query = (
            request.query_params.get("q")
            or request.query_params.get("search")
            or ""
        )

        project_status = (
            request.query_params.get("estado")
            or request.query_params.get("status")
            or ""
        )

        try:
            available_years = (
                get_proyectos_available_years_for_user(
                    request.user,
                    q=query,
                    estado=project_status,
                )
            )

        except DatabaseError:
            logger.exception(
                (
                    "Error al calcular los años disponibles "
                    "de proyectos."
                )
            )

            return self._database_unavailable_response(
                (
                    "No fue posible consultar los años "
                    "disponibles de proyectos."
                )
            )

        return Response(
            available_years,
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # AUTORES DEL PROYECTO
    # ========================================================

    @action(
        detail=True,
        methods=[
            "get",
            "put",
            "patch",
        ],
        url_path="autores",
        url_name="autores",
    )
    def autores(
        self,
        request,
        pk=None,
    ):
        """
        Consulta o reemplaza el equipo investigador.

        GET:
            Disponible para usuarios autenticados con acceso al
            proyecto.

        PUT/PATCH:
            Disponible únicamente para administradores.
        """
        if request.method.upper() == "GET":
            project = self.get_object()

            participations = list(
                project.participaciones.all()
            )

            serializer_class = (
                self._team_serializer_class(
                    request
                )
            )

            participation_serializer = (
                serializer_class(
                    participations,
                    many=True,
                    context=self.get_serializer_context(),
                )
            )

            has_main_researcher = any(
                getattr(
                    participation,
                    "rol",
                    None,
                )
                == "principal"
                for participation
                in participations
            )

            return Response(
                {
                    "autores": (
                        participation_serializer.data
                    ),
                    "autores_total": len(
                        participations
                    ),
                    "tiene_investigador_principal": (
                        has_main_researcher
                    ),
                    "equipo_pendiente": (
                        len(participations) == 0
                    ),
                },
                status=status.HTTP_200_OK,
            )

        require_project_admin(
            request.user
        )

        raw_authors = self._extract_authors_payload(
            request
        )

        normalized_authors = (
            normalize_proyecto_autores_payload(
                raw_authors
            )
        )

        try:
            with transaction.atomic():
                locked_project = (
                    self._get_locked_project()
                )

                if (
                    locked_project.estado == "cierre"
                    and not normalized_authors
                ):
                    raise ValidationError(
                        {
                            "autores_data": (
                                "Un proyecto cerrado debe "
                                "conservar su equipo con un "
                                "investigador principal en el "
                                "orden 1."
                            )
                        }
                    )

                sync_proyecto_autores(
                    locked_project,
                    normalized_authors,
                )

                self._clear_project_cache(
                    locked_project
                )

                project_id = locked_project.pk

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al actualizar "
                    "los autores de un proyecto."
                )
            )

            return self._database_unavailable_response(
                (
                    "No fue posible actualizar el equipo "
                    "investigador debido a un error temporal "
                    "de la base de datos."
                )
            )

        updated_project = (
            self._get_project_for_response(
                project_id
            )
        )

        project_serializer = ProyectoSerializer(
            updated_project,
            context=self.get_serializer_context(),
        )

        return Response(
            {
                "proyecto": project_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # CAMBIO DE ESTADO
    # ========================================================

    @action(
        detail=True,
        methods=[
            "patch",
        ],
        url_path="cambiar_estado",
        url_name="cambiar-estado",
    )
    def cambiar_estado(
        self,
        request,
        pk=None,
    ):
        """
        Cambia el estado de un proyecto.

        Cuando no se envía un estado, se aplica la transición
        automática definida en el servicio:

            nuevo -> arrastre
            arrastre -> cierre
            cierre -> arrastre
        """
        require_project_admin(
            request.user
        )

        requested_state = request.data.get(
            "estado",
            "",
        )

        try:
            with transaction.atomic():
                locked_project = (
                    self._get_locked_project()
                )

                destination_state = (
                    resolver_estado_destino(
                        locked_project,
                        requested_state,
                    )
                )

                payload = {
                    "estado": destination_state,
                }

                if destination_state == "cierre":
                    payload["fecha_cierre"] = (
                        locked_project.fecha_cierre
                        or timezone.localdate()
                    )

                else:
                    payload["fecha_cierre"] = None

                project_serializer = ProyectoSerializer(
                    locked_project,
                    data=payload,
                    partial=True,
                    context=self._project_serializer_context(
                        allow_state_transition=True,
                    ),
                )

                project_serializer.is_valid(
                    raise_exception=True
                )

                updated_project = (
                    project_serializer.save()
                )

                project_id = updated_project.pk

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al cambiar "
                    "el estado de un proyecto."
                )
            )

            return self._database_unavailable_response(
                (
                    "No fue posible cambiar el estado del "
                    "proyecto debido a un error temporal "
                    "de la base de datos."
                )
            )

        updated_project = (
            self._get_project_for_response(
                project_id
            )
        )

        response_serializer = ProyectoSerializer(
            updated_project,
            context=self.get_serializer_context(),
        )

        return Response(
            {
                "proyecto": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # EXTENSIÓN DE FECHA
    # ========================================================

    @action(
        detail=True,
        methods=[
            "patch",
        ],
        url_path="extender_fecha",
        url_name="extender-fecha",
    )
    def extender_fecha(
        self,
        request,
        pk=None,
    ):
        """
        Extiende la fecha final de un proyecto y lo coloca en
        estado arrastre.

        Campos admitidos:

        - fecha_fin_prorrogada
        - fecha_fin
        - nueva_fecha_fin
        """
        require_project_admin(
            request.user
        )

        raw_new_date = (
            request.data.get(
                "fecha_fin_prorrogada"
            )
            or request.data.get(
                "fecha_fin"
            )
            or request.data.get(
                "nueva_fecha_fin"
            )
        )

        if not raw_new_date:
            raise ValidationError(
                {
                    "fecha_fin_prorrogada": (
                        "Debe indicar la nueva fecha de "
                        "finalización."
                    )
                }
            )

        new_end_date = self._parse_extension_date(
            raw_new_date
        )

        try:
            with transaction.atomic():
                locked_project = (
                    self._get_locked_project()
                )

                current_reference_date = (
                    getattr(
                        locked_project,
                        "fecha_fin_vigente",
                        None,
                    )
                    or locked_project.fecha_fin_prorrogada
                    or locked_project.fecha_cierre
                    or locked_project.fecha_fin_planificada
                    or locked_project.fecha_inicio
                )

                if (
                    current_reference_date is not None
                    and new_end_date
                    <= current_reference_date
                ):
                    raise ValidationError(
                        {
                            "fecha_fin_prorrogada": (
                                "La nueva fecha debe ser "
                                "posterior a la fecha final "
                                "actual del proyecto."
                            )
                        }
                    )

                payload = {
                    "fecha_fin_prorrogada": new_end_date,
                    "estado": "arrastre",
                    "fecha_cierre": None,
                }

                project_serializer = ProyectoSerializer(
                    locked_project,
                    data=payload,
                    partial=True,
                    context=self._project_serializer_context(
                        allow_state_transition=True,
                    ),
                )

                project_serializer.is_valid(
                    raise_exception=True
                )

                updated_project = (
                    project_serializer.save()
                )

                project_id = updated_project.pk

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al extender "
                    "la fecha de un proyecto."
                )
            )

            return self._database_unavailable_response(
                (
                    "No fue posible extender la fecha del "
                    "proyecto debido a un error temporal "
                    "de la base de datos."
                )
            )

        updated_project = (
            self._get_project_for_response(
                project_id
            )
        )

        response_serializer = ProyectoSerializer(
            updated_project,
            context=self.get_serializer_context(),
        )

        return Response(
            {
                "proyecto": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )