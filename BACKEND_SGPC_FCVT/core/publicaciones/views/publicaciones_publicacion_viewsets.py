from django.db.models import (
    Prefetch,
    Q,
)
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import (
    PermissionDenied,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import (
    Publicacion,
    PublicacionAutor,
)
from core.publicaciones.serializers.read.publicaciones_detalle_serializers import (
    PublicacionDetalleSerializer,
)
from core.publicaciones.serializers.read.publicaciones_listado_serializers import (
    PublicacionListadoSerializer,
)
from core.publicaciones.serializers.update.publicaciones_actualizacion_serializers import (
    PublicacionActualizacionSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    can_edit_publicacion,
    resolve_user_autor_id,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
)


# =============================================================
# NORMALIZACIÓN DE PARÁMETROS
# =============================================================


def _normalize_text(value):
    return str(
        value or ""
    ).strip()


def _normalize_lower(value):
    value = _normalize_text(
        value
    )

    return (
        value.lower()
        if value
        else ""
    )


def _first_query_param(
    query_params,
    *names,
    default="",
):
    """
    Obtiene el primer parámetro que contenga
    un valor no vacío.

    Permite mantener compatibilidad entre nombres
    antiguos y nuevos utilizados por el frontend.
    """

    for name in names:
        value = query_params.get(
            name,
            None,
        )

        if value not in (
            None,
            "",
        ):
            return value

    return default


def _parse_year(value):
    raw = _normalize_text(
        value
    )

    if (
        raw.isdigit()
        and len(raw) == 4
    ):
        return int(raw)

    return None


def _parse_bool(value):
    if isinstance(
        value,
        bool,
    ):
        return value

    normalized = _normalize_lower(
        value
    )

    return normalized in {
        "1",
        "true",
        "yes",
        "si",
        "sí",
        "on",
    }


def _parse_positive_id(value):
    raw = _normalize_text(
        value
    )

    if not raw.isdigit():
        return None

    parsed = int(raw)

    return (
        parsed
        if parsed > 0
        else None
    )


def _resolve_tipo_filter(value):
    """
    Convierte los códigos enviados por las distintas
    interfaces al código final utilizado por el backend.
    """

    normalized = _normalize_lower(
        value
    )

    if normalized in {
        "",
        "all",
        "todos",
        "todo",
    }:
        return ""

    alias_map = {
        # Artículo de alto impacto
        "aai": (
            "articulo_alto_impacto"
        ),
        "alto_impacto": (
            "articulo_alto_impacto"
        ),
        "alto-impacto": (
            "articulo_alto_impacto"
        ),
        "articulo_alto_impacto": (
            "articulo_alto_impacto"
        ),

        # Artículo regional
        "ar": (
            "articulo_regional"
        ),
        "regional": (
            "articulo_regional"
        ),
        "articulo_regional": (
            "articulo_regional"
        ),

        # Ponencia
        "pon": "ponencia",
        "ponencia": "ponencia",
        "ponencias": "ponencia",

        # Libro
        "lib": "libro",
        "libro": "libro",
        "libros": "libro",

        # Capítulo
        "cap": "capitulo_libro",
        "capitulo": "capitulo_libro",
        "capítulo": "capitulo_libro",
        "capitulos": "capitulo_libro",
        "capítulos": "capitulo_libro",
        "capitulo_libro": (
            "capitulo_libro"
        ),
    }

    return alias_map.get(
        normalized,
        normalized,
    )


class PublicacionViewSet(
    viewsets.ModelViewSet
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated
    ]

    http_method_names = [
        "get",
        "put",
        "patch",
        "head",
        "options",
    ]

    # =========================================================
    # QUERYSET BASE
    # =========================================================

    def get_queryset(self):
        autores_prefetch = Prefetch(
            "participaciones",
            queryset=(
                PublicacionAutor.objects
                .select_related(
                    "autor"
                )
                .order_by(
                    "orden",
                    "id",
                )
            ),
            to_attr=(
                "participaciones_ordenadas"
            ),
        )

        queryset = (
            Publicacion.objects
            .select_related(
                "tipo",

                "proyecto",

                "usuario_creador",
                "admin_registrador",

                "carrera",
                "carrera__facultad",

                "area",
                "subarea",

                "pais",
                "ciudad",

                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
            .prefetch_related(
                autores_prefetch,
                "archivos",
            )
            .order_by(
                "-updated_at",
                "-id",
            )
        )

        return (
            annotate_tipo_publicacion_final(
                queryset
            )
        )

    # =========================================================
    # FILTROS DE CONSULTA
    # =========================================================

    def _apply_request_filters(
        self,
        queryset,
        request,
    ):
        """
        Aplica filtros opcionales enviados por query params.

        Parámetros admitidos:

        - tipo
        - tipo_publicacion_final
        - origen_tipo
        - origen
        - anio
        - anio_desde
        - anio_hasta
        - facultad / facultad_id
        - carrera / carrera_id
        - proyecto / proyecto_id
        - solo_con_pdf
        - texto / q
        """

        params = (
            request.query_params
        )

        # -----------------------------------------------------
        # Tipo de publicación
        # -----------------------------------------------------

        tipo = _resolve_tipo_filter(
            _first_query_param(
                params,
                "tipo",
                "tipo_publicacion_final",
            )
        )

        if tipo:
            queryset = queryset.filter(
                tipo_publicacion_final=tipo
            )

        # -----------------------------------------------------
        # Origen de la publicación
        # -----------------------------------------------------

        origen_tipo = _normalize_lower(
            _first_query_param(
                params,
                "origen_tipo",
                "origen",
            )
        )

        if origen_tipo in {
            "all",
            "todos",
            "todo",
        }:
            origen_tipo = ""

        if origen_tipo:
            valid_origins = {
                value
                for value, _label
                in Publicacion.ORIGEN_TIPO
            }

            if (
                origen_tipo
                not in valid_origins
            ):
                return queryset.none()

            queryset = queryset.filter(
                origen_tipo=origen_tipo
            )

        # -----------------------------------------------------
        # Año exacto o rango de años
        # -----------------------------------------------------

        anio = _parse_year(
            _first_query_param(
                params,
                "anio",
            )
        )

        anio_desde = _parse_year(
            _first_query_param(
                params,
                "anio_desde",
            )
        )

        anio_hasta = _parse_year(
            _first_query_param(
                params,
                "anio_hasta",
            )
        )

        if (
            anio_desde
            and anio_hasta
            and anio_desde > anio_hasta
        ):
            (
                anio_desde,
                anio_hasta,
            ) = (
                anio_hasta,
                anio_desde,
            )

        if anio:
            queryset = queryset.filter(
                anio_publicacion=anio
            )

        else:
            if anio_desde:
                queryset = queryset.filter(
                    anio_publicacion__gte=(
                        anio_desde
                    )
                )

            if anio_hasta:
                queryset = queryset.filter(
                    anio_publicacion__lte=(
                        anio_hasta
                    )
                )

        # -----------------------------------------------------
        # Facultad
        # -----------------------------------------------------

        facultad_id = _parse_positive_id(
            _first_query_param(
                params,
                "facultad",
                "facultad_id",
            )
        )

        if facultad_id:
            queryset = queryset.filter(
                carrera__facultad_id=(
                    facultad_id
                )
            )

        # -----------------------------------------------------
        # Carrera
        # -----------------------------------------------------

        carrera_id = _parse_positive_id(
            _first_query_param(
                params,
                "carrera",
                "carrera_id",
            )
        )

        if carrera_id:
            queryset = queryset.filter(
                carrera_id=carrera_id
            )

        # -----------------------------------------------------
        # Proyecto
        # -----------------------------------------------------

        proyecto_id = _parse_positive_id(
            _first_query_param(
                params,
                "proyecto",
                "proyecto_id",
            )
        )

        if proyecto_id:
            queryset = queryset.filter(
                proyecto_id=proyecto_id
            )

        # -----------------------------------------------------
        # Solo publicaciones con PDF
        # -----------------------------------------------------

        solo_con_pdf = _parse_bool(
            _first_query_param(
                params,
                "solo_con_pdf",
                default="",
            )
        )

        if solo_con_pdf:
            pdf_filter = (
                (
                    Q(
                        archivo_pdf__isnull=False
                    )
                    & ~Q(
                        archivo_pdf=""
                    )
                )
                |
                (
                    Q(
                        archivos__archivo__isnull=False
                    )
                    & ~Q(
                        archivos__archivo=""
                    )
                )
            )

            queryset = (
                queryset
                .filter(
                    pdf_filter
                )
                .distinct()
            )

        # -----------------------------------------------------
        # Búsqueda textual
        # -----------------------------------------------------

        texto = _normalize_text(
            _first_query_param(
                params,
                "texto",
                "q",
            )
        )

        if texto:
            queryset = (
                queryset
                .filter(
                    # Datos institucionales
                    Q(
                        carrera__facultad__nombre__icontains=texto
                    )
                    | Q(
                        carrera__nombre__icontains=texto
                    )
                    | Q(
                        proyecto__nombre__icontains=texto
                    )
                    | Q(
                        area__nombre__icontains=texto
                    )
                    | Q(
                        subarea__nombre__icontains=texto
                    )

                    # Origen
                    | Q(
                        origen_tipo__icontains=texto
                    )
                    | Q(
                        origen_grado__icontains=texto
                    )

                    # Artículos
                    | Q(
                        articulo__nombre_articulo__icontains=texto
                    )
                    | Q(
                        articulo__nombre_revista__icontains=texto
                    )
                    | Q(
                        articulo__codigo_doi__icontains=texto
                    )
                    | Q(
                        articulo__codigo_issn__icontains=texto
                    )

                    # Ponencias
                    | Q(
                        ponencia__nombre_evento__icontains=texto
                    )
                    | Q(
                        ponencia__nombre_ponencia__icontains=texto
                    )

                    # Libros
                    | Q(
                        libro__nombre_libro__icontains=texto
                    )
                    | Q(
                        libro__editorial_compilador__icontains=texto
                    )
                    | Q(
                        libro__codigo_isbn__icontains=texto
                    )

                    # Capítulos
                    | Q(
                        capitulo_libro__nombre_capitulo__icontains=texto
                    )
                    | Q(
                        capitulo_libro__nombre_libro__icontains=texto
                    )
                    | Q(
                        capitulo_libro__codigo_isbn__icontains=texto
                    )

                    # Autores
                    | Q(
                        participaciones__autor__nombres__icontains=texto
                    )
                    | Q(
                        participaciones__autor__apellidos__icontains=texto
                    )
                    | Q(
                        participaciones__autor__identificacion__icontains=texto
                    )
                    | Q(
                        participaciones__autor__correo__icontains=texto
                    )
                )
                .distinct()
            )

        return queryset

    # =========================================================
    # SERIALIZERS
    # =========================================================

    def get_serializer_class(self):
        if self.action in {
            "update",
            "partial_update",
        }:
            return (
                PublicacionActualizacionSerializer
            )

        if self.action == "retrieve":
            return (
                PublicacionDetalleSerializer
            )

        if self.action in {
            "list",
            "mias",
        }:
            return (
                PublicacionListadoSerializer
            )

        return (
            PublicacionDetalleSerializer
        )

    def get_serializer_context(self):
        context = (
            super()
            .get_serializer_context()
        )

        context["request"] = (
            self.request
        )

        return context

    # =========================================================
    # PERMISOS
    # =========================================================

    def _check_can_edit(
        self,
        instance,
    ):
        if can_edit_publicacion(
            self.request.user,
            instance,
        ):
            return

        raise PermissionDenied(
            "No tiene permisos para editar "
            "esta publicación."
        )

    # =========================================================
    # LISTADO GENERAL
    # =========================================================

    def list(
        self,
        request,
        *args,
        **kwargs,
    ):
        queryset = (
            self._apply_request_filters(
                self.get_queryset(),
                request,
            )
        )

        serializer = (
            self.get_serializer(
                queryset,
                many=True,
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # MIS PUBLICACIONES
    # =========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="mias",
    )
    def mias(
        self,
        request,
    ):
        autor_id = (
            resolve_user_autor_id(
                request.user
            )
        )

        user_filters = Q(
            usuario_creador=request.user
        )

        if autor_id:
            user_filters |= Q(
                participaciones__autor_id=(
                    autor_id
                )
            )

        queryset = (
            self.get_queryset()
            .filter(
                user_filters
            )
            .distinct()
        )

        queryset = (
            self._apply_request_filters(
                queryset,
                request,
            )
        )

        serializer = (
            self.get_serializer(
                queryset,
                many=True,
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # DETALLE
    # =========================================================

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):
        instance = (
            self.get_object()
        )

        serializer = (
            PublicacionDetalleSerializer(
                instance,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # ACTUALIZACIÓN INTERNA
    # =========================================================

    def _update_instance(
        self,
        *,
        request,
        instance,
        partial,
    ):
        self._check_can_edit(
            instance
        )

        serializer = (
            PublicacionActualizacionSerializer(
                instance=instance,
                data=request.data,
                partial=partial,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        updated_instance = (
            serializer.save()
        )

        # Reconsultamos para cargar:
        #
        # - relaciones
        # - anotación tipo_publicacion_final
        # - autores prefetched
        # - archivos prefetched

        updated_instance = (
            self.get_queryset()
            .get(
                pk=updated_instance.pk
            )
        )

        output_serializer = (
            PublicacionDetalleSerializer(
                updated_instance,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # PUT
    # =========================================================

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        instance = (
            self.get_object()
        )

        return self._update_instance(
            request=request,
            instance=instance,
            partial=False,
        )

    # =========================================================
    # PATCH
    # =========================================================

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):
        instance = (
            self.get_object()
        )

        return self._update_instance(
            request=request,
            instance=instance,
            partial=True,
        )