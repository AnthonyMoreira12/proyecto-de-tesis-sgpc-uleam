"""
ViewSet público para consultar y registrar autores.

Responsabilidades:

- Listar y buscar autores.
- Consultar el detalle de un autor.
- Registrar autores externos desde los formularios.
- Crear o vincular el usuario externo pendiente.
- Validar coincidencias antes del registro.
- Restringir la edición y eliminación a administradores.
- Proteger actualizaciones concurrentes.
- Controlar conflictos de integridad y relaciones protegidas.

Los usuarios autenticados pueden:

- Consultar autores.
- Buscar autores.
- Validar coincidencias.
- Registrar nuevos autores externos.

Solo los administradores pueden:

- Modificar autores existentes.
- Eliminar autores.
"""

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.autores.serializers.autores_autor_serializers import (
    AutorSerializer,
)
from core.autores.services.autores_usuario_sync_services import (
    AutorUsuarioSyncError,
    asegurar_usuario_pendiente_para_autor,
    buscar_autor_existente,
    serializar_autor_match,
)
from core.models import Autor


# ============================================================
# CONFIGURACIÓN
# ============================================================

MAX_SEARCH_LENGTH = 200


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_query(value):
    """
    Normaliza un parámetro textual utilizado en búsquedas.
    """
    return " ".join(
        str(value or "").split()
    )


def _parse_optional_positive_integer(
    value,
    *,
    field_name,
):
    """
    Convierte un parámetro opcional en entero positivo.
    """
    if value in (
        None,
        "",
    ):
        return None

    if isinstance(value, bool):
        raise ValidationError(
            {
                field_name: (
                    "Debe proporcionar un identificador válido."
                )
            }
        )

    try:
        parsed_value = int(
            str(value).strip()
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise ValidationError(
            {
                field_name: (
                    "Debe proporcionar un identificador válido."
                )
            }
        ) from exc

    if parsed_value < 1:
        raise ValidationError(
            {
                field_name: (
                    "Debe proporcionar un identificador válido."
                )
            }
        )

    return parsed_value


def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura
    compatible con Django REST Framework.
    """
    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
        return {
            "detail": list(
                exc.messages
            )
        }

    return {
        "detail": str(exc),
    }


def _is_admin_user(user):
    """
    Comprueba si el usuario posee permisos administrativos.
    """
    if user is None:
        return False

    return bool(
        getattr(
            user,
            "is_staff",
            False,
        )
        or getattr(
            user,
            "is_superuser",
            False,
        )
    )


# ============================================================
# VIEWSET
# ============================================================

class AutoresViewSet(viewsets.ModelViewSet):
    """
    Gestión general de autores.

    Endpoints principales:

    GET
        /api/autores/

    POST
        /api/autores/

    GET
        /api/autores/{id}/

    PUT / PATCH
        /api/autores/{id}/

    DELETE
        /api/autores/{id}/

    GET
        /api/autores/validar-existencia/
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = AutorSerializer

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
    # PERMISOS
    # ========================================================

    def check_write_permission(self):
        """
        Restringe actualización y eliminación a administradores.

        La creación continúa disponible para usuarios
        autenticados porque se utiliza desde los formularios
        de publicaciones para registrar coautores externos.
        """
        if not _is_admin_user(
            self.request.user
        ):
            raise PermissionDenied(
                (
                    "Solo un administrador puede modificar "
                    "o eliminar autores existentes."
                )
            )

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self):
        """
        Devuelve autores ordenados y permite búsqueda mediante
        los parámetros q o search.
        """
        queryset = (
            Autor.objects
            .select_related(
                "usuario",
            )
            .all()
        )

        search_query = _normalize_query(
            self.request.query_params.get(
                "q"
            )
            or self.request.query_params.get(
                "search"
            )
        )

        if search_query:
            if len(search_query) > MAX_SEARCH_LENGTH:
                raise ValidationError(
                    {
                        "q": (
                            "La búsqueda no puede superar "
                            f"los {MAX_SEARCH_LENGTH} caracteres."
                        )
                    }
                )

            queryset = queryset.filter(
                Q(
                    nombres__icontains=(
                        search_query
                    )
                )
                | Q(
                    apellidos__icontains=(
                        search_query
                    )
                )
                | Q(
                    identificacion__icontains=(
                        search_query
                    )
                )
                | Q(
                    correo__icontains=(
                        search_query
                    )
                )
                | Q(
                    institucion__icontains=(
                        search_query
                    )
                )
                | Q(
                    usuario__email__icontains=(
                        search_query
                    )
                )
                | Q(
                    usuario__identificacion__icontains=(
                        search_query
                    )
                )
                | Q(
                    usuario__nombres__icontains=(
                        search_query
                    )
                )
                | Q(
                    usuario__apellidos__icontains=(
                        search_query
                    )
                )
            )

        return queryset.order_by(
            "apellidos",
            "nombres",
            "pk",
        )

    # ========================================================
    # RECUPERACIÓN BLOQUEADA
    # ========================================================

    def _get_locked_author(self):
        """
        Recupera y bloquea un autor para actualización o
        eliminación.

        No utiliza los filtros de búsqueda del listado para
        evitar que un parámetro q provoque un falso 404 en una
        operación de detalle.
        """
        lookup_value = self.kwargs.get(
            self.lookup_field
        )

        try:
            author = (
                Autor.objects
                .select_for_update()
                .select_related(
                    "usuario",
                )
                .get(
                    pk=lookup_value
                )
            )

        except Autor.DoesNotExist as exc:
            raise NotFound(
                "El autor solicitado no existe."
            ) from exc

        self.check_object_permissions(
            self.request,
            author,
        )

        return author

    # ========================================================
    # CREACIÓN
    # ========================================================

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Registra un autor externo y garantiza la creación o
        vinculación de su usuario pendiente.

        Toda la operación se revierte cuando la sincronización
        del usuario no puede completarse.
        """
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            with transaction.atomic():
                # El serializer establece de forma segura:
                #
                # usuario = None
                # es_externo = True
                author = serializer.save()

                try:
                    asegurar_usuario_pendiente_para_autor(
                        author
                    )

                except AutorUsuarioSyncError as exc:
                    raise ValidationError(
                        exc.detail
                    ) from exc

                created_author = (
                    Autor.objects
                    .select_related(
                        "usuario",
                    )
                    .get(
                        pk=author.pk
                    )
                )

        except ValidationError:
            raise

        except DjangoValidationError as exc:
            raise ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No fue posible registrar el autor "
                        "porque existe un conflicto con la "
                        "identificación, el correo o el "
                        "usuario asociado."
                    )
                }
            ) from exc

        response_serializer = self.get_serializer(
            created_author
        )

        response = Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(
                response_serializer.data
            ),
        )

        response["Cache-Control"] = "no-store"

        return response

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Actualiza un autor existente.

        Solo los administradores pueden ejecutar esta operación.
        """
        self.check_write_permission()

        partial = kwargs.pop(
            "partial",
            False,
        )

        try:
            with transaction.atomic():
                author = self._get_locked_author()

                serializer = self.get_serializer(
                    author,
                    data=request.data,
                    partial=partial,
                )

                serializer.is_valid(
                    raise_exception=True
                )

                updated_author = serializer.save()

                # Los autores externos deben conservar
                # coherencia con su usuario pendiente.
                if bool(
                    updated_author.es_externo
                ):
                    try:
                        asegurar_usuario_pendiente_para_autor(
                            updated_author
                        )

                    except AutorUsuarioSyncError as exc:
                        raise ValidationError(
                            exc.detail
                        ) from exc

                updated_author = (
                    Autor.objects
                    .select_related(
                        "usuario",
                    )
                    .get(
                        pk=updated_author.pk
                    )
                )

        except ValidationError:
            raise

        except DjangoValidationError as exc:
            raise ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No fue posible actualizar el autor "
                        "porque los datos entran en conflicto "
                        "con otro autor o usuario."
                    )
                }
            ) from exc

        response_serializer = self.get_serializer(
            updated_author
        )

        response = Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

        response["Cache-Control"] = "no-store"

        return response

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Ejecuta una actualización parcial.
        """
        kwargs["partial"] = True

        return self.update(
            request,
            *args,
            **kwargs,
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
        Elimina un autor únicamente cuando no existen relaciones
        protegidas que dependan de él.

        La cuenta de Usuario relacionada no se elimina
        automáticamente.
        """
        self.check_write_permission()

        try:
            with transaction.atomic():
                author = self._get_locked_author()

                self.perform_destroy(
                    author
                )

        except ProtectedError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No se puede eliminar el autor porque "
                        "está relacionado con publicaciones "
                        "u otros registros del sistema."
                    )
                }
            ) from exc

        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No se puede eliminar el autor porque "
                        "mantiene relaciones activas."
                    )
                }
            ) from exc

        except DatabaseError:
            return Response(
                {
                    "detail": (
                        "No fue posible eliminar el autor "
                        "debido a un error temporal de la "
                        "base de datos."
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
    # VALIDACIÓN DE EXISTENCIA
    # ========================================================

    @action(
        detail=False,
        methods=[
            "get",
        ],
        url_path="validar-existencia",
        url_name="validar-existencia",
    )
    def validar_existencia(
        self,
        request,
    ):
        """
        Busca coincidencias antes de crear o actualizar un autor.

        Parámetros admitidos:

        - identificacion
        - correo
        - nombres
        - apellidos
        - exclude_autor_id
        """
        identification = _normalize_query(
            request.query_params.get(
                "identificacion"
            )
        )

        email = _normalize_query(
            request.query_params.get(
                "correo"
            )
        )

        names = _normalize_query(
            request.query_params.get(
                "nombres"
            )
        )

        surnames = _normalize_query(
            request.query_params.get(
                "apellidos"
            )
        )

        excluded_author_id = (
            _parse_optional_positive_integer(
                request.query_params.get(
                    "exclude_autor_id"
                ),
                field_name=(
                    "exclude_autor_id"
                ),
            )
        )

        if not any(
            [
                identification,
                email,
                names,
                surnames,
            ]
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Debe proporcionar una identificación, "
                        "correo o nombres y apellidos para "
                        "realizar la validación."
                    )
                }
            )

        if bool(names) != bool(surnames):
            raise ValidationError(
                {
                    "detail": (
                        "Para buscar por nombre debe ingresar "
                        "tanto los nombres como los apellidos."
                    )
                }
            )

        for field_name, field_value in {
            "identificacion": identification,
            "correo": email,
            "nombres": names,
            "apellidos": surnames,
        }.items():
            if len(field_value) > MAX_SEARCH_LENGTH:
                raise ValidationError(
                    {
                        field_name: (
                            "El valor no puede superar "
                            f"los {MAX_SEARCH_LENGTH} caracteres."
                        )
                    }
                )

        found = buscar_autor_existente(
            identificacion=(
                identification or None
            ),
            correo=email or None,
            nombres=names,
            apellidos=surnames,
            exclude_autor_id=(
                excluded_author_id
            ),
        )

        response = Response(
            serializar_autor_match(
                found.get(
                    "autor"
                ),
                found.get(
                    "match_type"
                ),
            ),
            status=status.HTTP_200_OK,
        )

        response["Cache-Control"] = "no-store"

        return response 