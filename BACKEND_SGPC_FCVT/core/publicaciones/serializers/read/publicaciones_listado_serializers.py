"""
Serializer de lectura para los listados de publicaciones.

Es utilizado por:

- GET /publicaciones/
- GET /publicaciones/mias/

La respuesta mantiene compatibilidad con el frontend actual
y expone identificadores reales para que los filtros puedan
alinearse completamente con el backend.
"""

from django.urls import reverse
from rest_framework import serializers

from core.models import (
    Publicacion,
    PublicacionAutor,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    can_edit_publicacion,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    tipo_publicacion_label,
)


# ============================================================
# UTILIDADES
# ============================================================

def _to_str(
    value,
):
    return str(
        value or ""
    ).strip()


def _to_lower(
    value,
):
    value = _to_str(
        value
    )

    return (
        value.lower()
        if value
        else ""
    )


def _safe_related(
    instance,
    attr_name,
):
    """
    Obtiene de forma segura una relación inversa OneToOne.

    Cuando una publicación no posee uno de sus subtipos,
    Django puede lanzar RelatedObjectDoesNotExist.
    """

    if instance is None:
        return None

    try:
        return getattr(
            instance,
            attr_name,
        )

    except Exception:
        return None


def _build_person_name(
    autor,
):
    """
    Construye el nombre visible de un autor.
    """

    if autor is None:
        return ""

    nombres = _to_str(
        getattr(
            autor,
            "nombres",
            None,
        )
    )

    apellidos = _to_str(
        getattr(
            autor,
            "apellidos",
            None,
        )
    )

    full_name = (
        f"{nombres} {apellidos}"
    ).strip()

    if full_name:
        return full_name

    correo = _to_str(
        getattr(
            autor,
            "correo",
            None,
        )
    )

    if correo:
        return correo

    return _to_str(
        getattr(
            autor,
            "identificacion",
            None,
        )
    )


# ============================================================
# RESOLUCIÓN DEL TIPO
# ============================================================

def _resolve_tipo_final_codigo(
    obj,
):
    """
    Obtiene el código canónico del tipo final.

    Prioridad:

    1. Anotación tipo_publicacion_final del queryset.
    2. Subtipo real asociado.
    3. TipoPublicacion base.
    """

    annotated = _to_lower(
        getattr(
            obj,
            "tipo_publicacion_final",
            None,
        )
    )

    if (
        annotated
        and annotated != "sin_clasificar"
    ):
        return annotated

    tipo = _safe_related(
        obj,
        "tipo",
    )

    tipo_codigo = _to_lower(
        getattr(
            tipo,
            "codigo",
            None,
        )
    )

    tipo_categoria = _to_lower(
        getattr(
            tipo,
            "categoria",
            None,
        )
    )

    articulo = _safe_related(
        obj,
        "articulo",
    )

    tipo_articulo = _to_lower(
        getattr(
            articulo,
            "tipo_articulo",
            None,
        )
    )

    if (
        tipo_categoria == "articulo"
        or tipo_codigo
        in {
            "articulo",
            "articulo_regional",
            "articulo_alto_impacto",
        }
    ):
        if tipo_articulo == "alto_impacto":
            return "articulo_alto_impacto"

        if tipo_articulo == "regional":
            return "articulo_regional"

        if tipo_codigo in {
            "articulo_alto_impacto",
            "articulo_regional",
        }:
            return tipo_codigo

    ponencia = _safe_related(
        obj,
        "ponencia",
    )

    if (
        ponencia is not None
        or tipo_categoria == "ponencia"
        or tipo_codigo == "ponencia"
    ):
        return "ponencia"

    libro = _safe_related(
        obj,
        "libro",
    )

    if (
        libro is not None
        or tipo_categoria == "libro"
        or tipo_codigo == "libro"
    ):
        return "libro"

    capitulo = _safe_related(
        obj,
        "capitulo_libro",
    )

    if (
        capitulo is not None
        or tipo_categoria == "capitulo"
        or tipo_codigo
        in {
            "capitulo",
            "capitulo_libro",
        }
    ):
        return "capitulo_libro"

    return "sin_clasificar"


def _resolve_tipo_final_label(
    obj,
):
    codigo = _resolve_tipo_final_codigo(
        obj
    )

    label = tipo_publicacion_label(
        codigo
    )

    if (
        label
        and label != "Sin clasificar"
    ):
        return label

    tipo = _safe_related(
        obj,
        "tipo",
    )

    return (
        _to_str(
            getattr(
                tipo,
                "nombre",
                None,
            )
        )
        or "Publicación"
    )


# ============================================================
# SERIALIZER
# ============================================================

class PublicacionListadoSerializer(
    serializers.ModelSerializer
):
    # ========================================================
    # INFORMACIÓN PRINCIPAL
    # ========================================================

    titulo = serializers.SerializerMethodField()
    autor = serializers.SerializerMethodField()

    # ========================================================
    # PROYECTO Y UBICACIÓN ACADÉMICA
    # ========================================================

    proyecto_id = serializers.SerializerMethodField()
    proyecto = serializers.SerializerMethodField()

    facultad_id = serializers.SerializerMethodField()
    facultad = serializers.SerializerMethodField()

    carrera_id = serializers.SerializerMethodField()
    carrera = serializers.SerializerMethodField()

    # ========================================================
    # TIPO
    # ========================================================

    tipo = serializers.SerializerMethodField()
    tipo_codigo = serializers.SerializerMethodField()

    tipo_publicacion_final = (
        serializers.SerializerMethodField()
    )

    tipo_publicacion_final_label = (
        serializers.SerializerMethodField()
    )

    # ========================================================
    # ORIGEN
    # ========================================================

    origen_tipo_label = (
        serializers.SerializerMethodField()
    )

    origen_detalle_label = (
        serializers.SerializerMethodField()
    )

    origen_resumen = (
        serializers.SerializerMethodField()
    )

    # ========================================================
    # PERIODO DE PUBLICACIÓN
    # ========================================================

    mes_publicacion_label = (
        serializers.SerializerMethodField()
    )

    # ========================================================
    # PDF
    # ========================================================

    tiene_pdf = serializers.SerializerMethodField()
    has_pdf = serializers.SerializerMethodField()
    hasPdf = serializers.SerializerMethodField()

    archivo_pdf_url = (
        serializers.SerializerMethodField()
    )

    pdf_url = serializers.SerializerMethodField()

    pdf_endpoint = (
        serializers.SerializerMethodField()
    )

    # ========================================================
    # PERMISOS
    # ========================================================

    puede_editar = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Publicacion

        fields = [
            "id",
            "numero",

            "titulo",
            "autor",

            "proyecto_id",
            "proyecto",

            "facultad_id",
            "facultad",

            "carrera_id",
            "carrera",

            "anio_publicacion",
            "mes_publicacion",
            "mes_publicacion_label",

            "tipo",
            "tipo_codigo",
            "tipo_publicacion_final",
            "tipo_publicacion_final_label",

            "origen_tipo",
            "origen_tipo_label",
            "origen_grado",
            "origen_detalle_label",
            "origen_resumen",

            "tiene_pdf",
            "has_pdf",
            "hasPdf",
            "archivo_pdf_url",
            "pdf_url",
            "pdf_endpoint",

            "puede_editar",
        ]

        read_only_fields = fields

    # ========================================================
    # PARTICIPACIONES DE AUTORES
    # ========================================================

    def _get_autor_rels(
        self,
        obj,
    ):
        """
        Utiliza primero el prefetch generado por el servicio.

        Solo consulta la base de datos si el serializer se usa
        desde una vista que no precargó las participaciones.
        """

        ordered = getattr(
            obj,
            "participaciones_ordenadas",
            None,
        )

        if ordered is not None:
            return list(
                ordered
            )

        prefetched = getattr(
            obj,
            "_prefetched_objects_cache",
            {},
        )

        if "participaciones" in prefetched:
            return sorted(
                prefetched["participaciones"],
                key=lambda item: (
                    item.orden,
                    item.id,
                ),
            )

        return list(
            PublicacionAutor.objects
            .filter(
                publicacion=obj
            )
            .select_related(
                "autor"
            )
            .order_by(
                "orden",
                "id",
            )
        )

    # ========================================================
    # ARCHIVOS
    # ========================================================

    def _get_archivos(
        self,
        obj,
    ):
        prefetched = getattr(
            obj,
            "_prefetched_objects_cache",
            {},
        )

        if "archivos" in prefetched:
            return sorted(
                prefetched["archivos"],
                key=lambda item: (
                    item.orden,
                    item.id,
                ),
            )

        return list(
            obj.archivos.all().order_by(
                "orden",
                "id",
            )
        )

    def _get_pdf_file(
        self,
        obj,
    ):
        """
        Prioridad:

        1. Publicacion.archivo_pdf.
        2. Primer PublicacionArchivo válido.
        """

        primary = getattr(
            obj,
            "archivo_pdf",
            None,
        )

        if (
            primary
            and getattr(
                primary,
                "name",
                None,
            )
        ):
            return primary

        for attachment in self._get_archivos(
            obj
        ):
            archivo = getattr(
                attachment,
                "archivo",
                None,
            )

            if (
                archivo
                and getattr(
                    archivo,
                    "name",
                    None,
                )
            ):
                return archivo

        return None

    def _build_file_url(
        self,
        field_file,
    ):
        if (
            not field_file
            or not getattr(
                field_file,
                "name",
                None,
            )
        ):
            return None

        try:
            file_url = field_file.url

        except (
            ValueError,
            AttributeError,
        ):
            return None

        request = self.context.get(
            "request"
        )

        if request is None:
            return file_url

        try:
            return request.build_absolute_uri(
                file_url
            )

        except Exception:
            return file_url

    # ========================================================
    # TÍTULO
    # ========================================================

    def get_titulo(
        self,
        obj,
    ):
        articulo = _safe_related(
            obj,
            "articulo",
        )

        ponencia = _safe_related(
            obj,
            "ponencia",
        )

        libro = _safe_related(
            obj,
            "libro",
        )

        capitulo = _safe_related(
            obj,
            "capitulo_libro",
        )

        proyecto = _safe_related(
            obj,
            "proyecto",
        )

        return (
            _to_str(
                getattr(
                    articulo,
                    "nombre_articulo",
                    None,
                )
            )
            or _to_str(
                getattr(
                    ponencia,
                    "nombre_ponencia",
                    None,
                )
            )
            or _to_str(
                getattr(
                    libro,
                    "nombre_libro",
                    None,
                )
            )
            or _to_str(
                getattr(
                    capitulo,
                    "nombre_capitulo",
                    None,
                )
            )
            or _to_str(
                getattr(
                    proyecto,
                    "nombre",
                    None,
                )
            )
            or "Sin título"
        )

    # ========================================================
    # AUTORES
    # ========================================================

    def get_autor(
        self,
        obj,
    ):
        participaciones = self._get_autor_rels(
            obj
        )

        nombres = []

        for participacion in participaciones:
            autor = getattr(
                participacion,
                "autor",
                None,
            )

            nombre = _build_person_name(
                autor
            )

            if nombre:
                nombres.append(
                    nombre
                )

        return ", ".join(
            nombres
        )

    # ========================================================
    # PROYECTO
    # ========================================================

    def get_proyecto_id(
        self,
        obj,
    ):
        return getattr(
            obj,
            "proyecto_id",
            None,
        )

    def get_proyecto(
        self,
        obj,
    ):
        proyecto = _safe_related(
            obj,
            "proyecto",
        )

        return _to_str(
            getattr(
                proyecto,
                "nombre",
                None,
            )
        )

    # ========================================================
    # FACULTAD
    # ========================================================

    def get_facultad_id(
        self,
        obj,
    ):
        carrera = _safe_related(
            obj,
            "carrera",
        )

        return getattr(
            carrera,
            "facultad_id",
            None,
        )

    def get_facultad(
        self,
        obj,
    ):
        carrera = _safe_related(
            obj,
            "carrera",
        )

        facultad = _safe_related(
            carrera,
            "facultad",
        )

        return _to_str(
            getattr(
                facultad,
                "nombre",
                None,
            )
        )

    # ========================================================
    # CARRERA
    # ========================================================

    def get_carrera_id(
        self,
        obj,
    ):
        return getattr(
            obj,
            "carrera_id",
            None,
        )

    def get_carrera(
        self,
        obj,
    ):
        carrera = _safe_related(
            obj,
            "carrera",
        )

        return _to_str(
            getattr(
                carrera,
                "nombre",
                None,
            )
        )

    # ========================================================
    # TIPO
    # ========================================================

    def get_tipo(
        self,
        obj,
    ):
        return _resolve_tipo_final_label(
            obj
        )

    def get_tipo_codigo(
        self,
        obj,
    ):
        tipo = _safe_related(
            obj,
            "tipo",
        )

        return _to_str(
            getattr(
                tipo,
                "codigo",
                None,
            )
        )

    def get_tipo_publicacion_final(
        self,
        obj,
    ):
        return _resolve_tipo_final_codigo(
            obj
        )

    def get_tipo_publicacion_final_label(
        self,
        obj,
    ):
        return _resolve_tipo_final_label(
            obj
        )

    # ========================================================
    # ORIGEN
    # ========================================================

    def _get_origen_tipo(
        self,
        obj,
    ):
        return (
            _to_lower(
                getattr(
                    obj,
                    "origen_tipo",
                    None,
                )
            )
            or "ninguno"
        )

    def get_origen_tipo_label(
        self,
        obj,
    ):
        origen_tipo = self._get_origen_tipo(
            obj
        )

        try:
            display = (
                obj.get_origen_tipo_display()
            )

        except Exception:
            display = ""

        return (
            _to_str(
                display
            )
            or {
                "ninguno": "Ninguno",
                "tic": (
                    "Trabajo de integración "
                    "curricular"
                ),
                "maestria": (
                    "Tesis de maestría"
                ),
                "doctoral": (
                    "Tesis doctoral"
                ),
                "otro": "Otro",
            }.get(
                origen_tipo,
                origen_tipo,
            )
        )

    def get_origen_detalle_label(
        self,
        obj,
    ):
        origen_tipo = self._get_origen_tipo(
            obj
        )

        if origen_tipo == "tic":
            return "Grado / programa"

        if origen_tipo == "otro":
            return "Origen especificado"

        return None

    def get_origen_resumen(
        self,
        obj,
    ):
        origen_tipo = self._get_origen_tipo(
            obj
        )

        if origen_tipo == "ninguno":
            return None

        label = self.get_origen_tipo_label(
            obj
        )

        detalle = _to_str(
            getattr(
                obj,
                "origen_grado",
                None,
            )
        )

        if (
            origen_tipo
            in {
                "tic",
                "otro",
            }
            and detalle
        ):
            return (
                f"{label} · {detalle}"
            )

        return label

    # ========================================================
    # PERIODO DE PUBLICACIÓN
    # ========================================================

    def get_mes_publicacion_label(
        self,
        obj,
    ):
        mes = getattr(
            obj,
            "mes_publicacion",
            None,
        )

        if mes in (
            None,
            "",
        ):
            return None

        try:
            return obj.get_mes_publicacion_display()
        except (
            AttributeError,
            ValueError,
        ):
            return None

    # ========================================================
    # PDF
    # ========================================================

    def get_tiene_pdf(
        self,
        obj,
    ):
        return bool(
            self._get_pdf_file(
                obj
            )
        )

    def get_has_pdf(
        self,
        obj,
    ):
        return self.get_tiene_pdf(
            obj
        )

    def get_hasPdf(
        self,
        obj,
    ):
        return self.get_tiene_pdf(
            obj
        )

    def get_archivo_pdf_url(
        self,
        obj,
    ):
        return self._build_file_url(
            self._get_pdf_file(
                obj
            )
        )

    def get_pdf_url(
        self,
        obj,
    ):
        return self.get_archivo_pdf_url(
            obj
        )

    def get_pdf_endpoint(
        self,
        obj,
    ):
        """
        Devuelve la ruta autenticada oficial para visualizar
        el PDF de la publicación.
        """

        try:
            endpoint = reverse(
                "publicacion-pdf-inline",
                kwargs={
                    "id": obj.id,
                },
            )

        except Exception:
            endpoint = (
                f"/publicaciones/"
                f"{obj.id}/pdf/"
            )

        request = self.context.get(
            "request"
        )

        if request is None:
            return endpoint

        try:
            return request.build_absolute_uri(
                endpoint
            )

        except Exception:
            return endpoint

    # ========================================================
    # PERMISOS
    # ========================================================

    def get_puede_editar(
        self,
        obj,
    ):
        request = self.context.get(
            "request"
        )

        user = getattr(
            request,
            "user",
            None,
        )

        if (
            user is None
            or not getattr(
                user,
                "is_authenticated",
                False,
            )
        ):
            return False

        try:
            return bool(
                can_edit_publicacion(
                    user,
                    obj,
                )
            )

        except Exception:
            return False