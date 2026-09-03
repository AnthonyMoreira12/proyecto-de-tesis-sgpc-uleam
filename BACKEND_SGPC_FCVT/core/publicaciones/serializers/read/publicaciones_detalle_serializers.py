from rest_framework import serializers

from core.models import (
    Publicacion,
    PublicacionAutor,
    PublicacionRevision,
)
from core.publicaciones.serializers.base.publicaciones_autores_serializers import (
    PublicacionAutorSerializer,
)
from core.publicaciones.services.publicaciones_estado_services import (
    can_enviar_a_revision,
    can_reenviar_a_revision,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    can_edit_publicacion,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    tipo_publicacion_label,
)


def _to_str(value):
    return (
        ""
        if value is None
        else str(value).strip()
    )


def _to_lower(value):
    value = _to_str(value)

    return (
        value.lower()
        if value
        else ""
    )


def _first_filled(*values):
    for value in values:
        text = _to_str(value)

        if text:
            return text

    return ""


def _resolve_tipo_final_codigo(obj):
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

    tipo = getattr(
        obj,
        "tipo",
        None,
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

    articulo = getattr(
        obj,
        "articulo",
        None,
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

    if (
        tipo_categoria == "ponencia"
        or tipo_codigo == "ponencia"
    ):
        return "ponencia"

    if (
        tipo_categoria == "libro"
        or tipo_codigo == "libro"
    ):
        return "libro"

    if (
        tipo_categoria == "capitulo"
        or tipo_codigo
        in {
            "capitulo",
            "capitulo_libro",
        }
    ):
        return "capitulo_libro"

    return "sin_clasificar"


def _resolve_tipo_final_label(obj):
    codigo = (
        _resolve_tipo_final_codigo(
            obj
        )
    )

    label = tipo_publicacion_label(
        codigo
    )

    if label != "Sin clasificar":
        return label

    tipo = getattr(
        obj,
        "tipo",
        None,
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


class PublicacionDetalleSerializer(
    serializers.ModelSerializer
):
    titulo = serializers.SerializerMethodField()

    tipo = serializers.SerializerMethodField()

    tipo_codigo = (
        serializers.SerializerMethodField()
    )

    tipo_publicacion_final = (
        serializers.SerializerMethodField()
    )

    tipo_publicacion_final_label = (
        serializers.SerializerMethodField()
    )

    sede_id = (
        serializers.SerializerMethodField()
    )

    sede = (
        serializers.SerializerMethodField()
    )

    facultad_id = (
        serializers.SerializerMethodField()
    )

    facultad = (
        serializers.SerializerMethodField()
    )

    carrera_id = (
        serializers.SerializerMethodField()
    )

    carrera = (
        serializers.SerializerMethodField()
    )

    proyecto_id = (
        serializers.SerializerMethodField()
    )

    proyecto = (
        serializers.SerializerMethodField()
    )

    area_id = (
        serializers.SerializerMethodField()
    )

    area = (
        serializers.SerializerMethodField()
    )

    subarea_id = (
        serializers.SerializerMethodField()
    )

    subarea = (
        serializers.SerializerMethodField()
    )

    pais_id = (
        serializers.SerializerMethodField()
    )

    pais = (
        serializers.SerializerMethodField()
    )

    ciudad_id = (
        serializers.SerializerMethodField()
    )

    ciudad = (
        serializers.SerializerMethodField()
    )

    # Estado de gestión
    estado_label = (
        serializers.SerializerMethodField()
    )

    ultima_revision = (
        serializers.SerializerMethodField()
    )

    puede_enviar_revision = (
        serializers.SerializerMethodField()
    )

    puede_reenviar_revision = (
        serializers.SerializerMethodField()
    )

    # Origen de la publicación
    origen_tipo_label = (
        serializers.SerializerMethodField()
    )

    origen_detalle_label = (
        serializers.SerializerMethodField()
    )

    origen_resumen = (
        serializers.SerializerMethodField()
    )

    # Periodo de publicación
    mes_publicacion_label = (
        serializers.SerializerMethodField()
    )

    archivo_pdf = (
        serializers.SerializerMethodField()
    )

    archivo_pdf_url = (
        serializers.SerializerMethodField()
    )

    pdf_url = (
        serializers.SerializerMethodField()
    )

    tiene_pdf = (
        serializers.SerializerMethodField()
    )

    has_pdf = (
        serializers.SerializerMethodField()
    )

    hasPdf = (
        serializers.SerializerMethodField()
    )

    autores = (
        serializers.SerializerMethodField()
    )

    puede_editar = (
        serializers.SerializerMethodField()
    )

    # Se mantienen por compatibilidad con
    # interfaces existentes.
    resumen = (
        serializers.SerializerMethodField()
    )

    descripcion = (
        serializers.SerializerMethodField()
    )

    abstract = (
        serializers.SerializerMethodField()
    )

    detalle = (
        serializers.SerializerMethodField()
    )

    # Ponencia
    tipo_presentacion = (
        serializers.SerializerMethodField()
    )

    tipo_presentacion_otro = (
        serializers.SerializerMethodField()
    )

    nombre_evento = (
        serializers.SerializerMethodField()
    )

    nombre_ponencia = (
        serializers.SerializerMethodField()
    )

    codigo_issn_isbn = (
        serializers.SerializerMethodField()
    )

    link_evento = (
        serializers.SerializerMethodField()
    )

    # Artículo
    tipo_articulo = (
        serializers.SerializerMethodField()
    )

    nombre_articulo = (
        serializers.SerializerMethodField()
    )

    base_datos_indexada = (
        serializers.SerializerMethodField()
    )

    base_datos_otra = (
        serializers.SerializerMethodField()
    )

    codigo_doi = (
        serializers.SerializerMethodField()
    )

    codigo_issn = (
        serializers.SerializerMethodField()
    )

    nombre_revista = (
        serializers.SerializerMethodField()
    )

    numero_revista = (
        serializers.SerializerMethodField()
    )

    link_publicacion = (
        serializers.SerializerMethodField()
    )

    link_revista = (
        serializers.SerializerMethodField()
    )

    factor_impacto = (
        serializers.SerializerMethodField()
    )

    cuartil = (
        serializers.SerializerMethodField()
    )

    sjr = (
        serializers.SerializerMethodField()
    )

    jcr = (
        serializers.SerializerMethodField()
    )

    # Compartido por Ponencia / Libro / Capítulo
    revisor_par_arbitraje = (
        serializers.SerializerMethodField()
    )

    # Libro
    nombre_libro = (
        serializers.SerializerMethodField()
    )

    codigo_isbn = (
        serializers.SerializerMethodField()
    )

    editorial_compilador = (
        serializers.SerializerMethodField()
    )

    link_libro = (
        serializers.SerializerMethodField()
    )

    # Capítulo
    nombre_capitulo = (
        serializers.SerializerMethodField()
    )

    editor_compilador = (
        serializers.SerializerMethodField()
    )

    link_capitulo = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Publicacion

        fields = [
            "id",
            "titulo",

            "tipo",
            "tipo_codigo",
            "tipo_publicacion_final",
            "tipo_publicacion_final_label",

            "estado",
            "estado_label",
            "ultima_revision",
            "puede_enviar_revision",
            "puede_reenviar_revision",

            "sede_id",
            "sede",

            "facultad_id",
            "facultad",

            "carrera_id",
            "carrera",

            "proyecto_id",
            "proyecto",

            "area_id",
            "area",

            "subarea_id",
            "subarea",

            "pais_id",
            "pais",

            "ciudad_id",
            "ciudad",

            "origen_tipo",
            "origen_tipo_label",
            "origen_grado",
            "origen_detalle_label",
            "origen_resumen",

            "anio_publicacion",
            "mes_publicacion",
            "mes_publicacion_label",

            "archivo_pdf",
            "archivo_pdf_url",
            "pdf_url",
            "archivo_pdf_nombre_original",
            "archivo_pdf_tamano_bytes",
            "archivo_pdf_sha256",

            "tiene_pdf",
            "has_pdf",
            "hasPdf",

            "autores",
            "puede_editar",

            "resumen",
            "descripcion",
            "abstract",
            "detalle",

            "tipo_presentacion",
            "tipo_presentacion_otro",
            "nombre_evento",
            "nombre_ponencia",
            "codigo_issn_isbn",
            "link_evento",

            "tipo_articulo",
            "nombre_articulo",
            "base_datos_indexada",
            "base_datos_otra",
            "codigo_doi",
            "codigo_issn",
            "nombre_revista",
            "numero_revista",
            "link_publicacion",
            "link_revista",
            "factor_impacto",
            "cuartil",
            "sjr",
            "jcr",

            "revisor_par_arbitraje",

            "nombre_libro",
            "codigo_isbn",
            "editorial_compilador",
            "link_libro",

            "nombre_capitulo",
            "editor_compilador",
            "link_capitulo",
        ]

        read_only_fields = fields

    def _related_attr(
        self,
        obj,
        relation_name,
        attribute_name,
        default="",
    ):
        """
        Lee de forma segura una relación y uno de sus campos.

        Las relaciones OneToOne inversas pueden lanzar
        RelatedObjectDoesNotExist cuando no existe el subtipo.
        """

        try:
            relation = getattr(
                obj,
                relation_name,
                None,
            )
        except Exception:
            return default

        if relation is None:
            return default

        return getattr(
            relation,
            attribute_name,
            default,
        )

    def _obj_id(
        self,
        relation,
    ):
        if relation is None:
            return None

        return getattr(
            relation,
            "id",
            None,
        )

    def _get_facultad_obj(
        self,
        obj,
    ):
        carrera = getattr(
            obj,
            "carrera",
            None,
        )

        if carrera is None:
            return None

        return getattr(
            carrera,
            "facultad",
            None,
        )

    def _build_file_url(
        self,
        file_field,
    ):
        try:
            if (
                not file_field
                or not getattr(
                    file_field,
                    "name",
                    None,
                )
            ):
                return None

            url = file_field.url

        except (
            AttributeError,
            ValueError,
        ):
            return None

        request = self.context.get(
            "request"
        )

        if request is None:
            return url

        try:
            return (
                request.build_absolute_uri(
                    url
                )
            )
        except Exception:
            return url

    def _get_pdf_file(
        self,
        obj,
    ):
        archivo_pdf = getattr(
            obj,
            "archivo_pdf",
            None,
        )

        if (
            archivo_pdf
            and getattr(
                archivo_pdf,
                "name",
                None,
            )
        ):
            return archivo_pdf

        prefetched = getattr(
            obj,
            "_prefetched_objects_cache",
            {},
        )

        if "archivos" in prefetched:
            archivos = sorted(
                prefetched["archivos"],
                key=lambda item: (
                    getattr(
                        item,
                        "orden",
                        0,
                    ),
                    getattr(
                        item,
                        "id",
                        0,
                    ),
                ),
            )

            for adjunto in archivos:
                archivo = getattr(
                    adjunto,
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

        try:
            adjunto = (
                obj.archivos
                .exclude(
                    archivo=""
                )
                .order_by(
                    "orden",
                    "id",
                )
                .first()
            )

        except Exception:
            return None

        if not adjunto:
            return None

        archivo = getattr(
            adjunto,
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

    def _get_autor_rels(
        self,
        obj,
    ):
        participaciones_ordenadas = getattr(
            obj,
            "participaciones_ordenadas",
            None,
        )

        if (
            participaciones_ordenadas
            is not None
        ):
            return (
                participaciones_ordenadas
            )

        prefetched = getattr(
            obj,
            "_prefetched_objects_cache",
            {},
        )

        if "participaciones" in prefetched:
            return prefetched[
                "participaciones"
            ]

        return (
            PublicacionAutor.objects
            .select_related(
                "autor"
            )
            .filter(
                publicacion=obj
            )
            .order_by(
                "orden",
                "id",
            )
        )

    def _get_articulo(
        self,
        obj,
    ):
        return getattr(
            obj,
            "articulo",
            None,
        )

    def _get_tipo_articulo(
        self,
        obj,
    ):
        articulo = (
            self._get_articulo(
                obj
            )
        )

        return _to_lower(
            getattr(
                articulo,
                "tipo_articulo",
                None,
            )
        )

    def get_titulo(
        self,
        obj,
    ):
        return _first_filled(
            self._related_attr(
                obj,
                "articulo",
                "nombre_articulo",
            ),
            self._related_attr(
                obj,
                "ponencia",
                "nombre_ponencia",
            ),
            self._related_attr(
                obj,
                "libro",
                "nombre_libro",
            ),
            self._related_attr(
                obj,
                "capitulo_libro",
                "nombre_capitulo",
            ),
            "Publicación",
        )

    def get_tipo(
        self,
        obj,
    ):
        return (
            _resolve_tipo_final_label(
                obj
            )
        )

    def get_tipo_codigo(
        self,
        obj,
    ):
        return (
            _resolve_tipo_final_codigo(
                obj
            )
        )

    def get_tipo_publicacion_final(
        self,
        obj,
    ):
        return (
            _resolve_tipo_final_codigo(
                obj
            )
        )

    def get_tipo_publicacion_final_label(
        self,
        obj,
    ):
        return (
            _resolve_tipo_final_label(
                obj
            )
        )

    def get_sede_id(
        self,
        obj,
    ):
        return self._obj_id(
            getattr(
                obj,
                "sede",
                None,
            )
        )

    def get_sede(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                getattr(
                    obj,
                    "sede",
                    None,
                ),
                "nombre",
                None,
            )
        )

    def get_facultad_id(
        self,
        obj,
    ):
        return self._obj_id(
            self._get_facultad_obj(
                obj
            )
        )

    def get_facultad(
        self,
        obj,
    ):
        facultad = (
            self._get_facultad_obj(
                obj
            )
        )

        return _to_str(
            getattr(
                facultad,
                "nombre",
                None,
            )
        )

    def get_carrera_id(
        self,
        obj,
    ):
        return self._obj_id(
            getattr(
                obj,
                "carrera",
                None,
            )
        )

    def get_carrera(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                getattr(
                    obj,
                    "carrera",
                    None,
                ),
                "nombre",
                None,
            )
        )

    def get_proyecto_id(
        self,
        obj,
    ):
        return self._obj_id(
            getattr(
                obj,
                "proyecto",
                None,
            )
        )

    def get_proyecto(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                getattr(
                    obj,
                    "proyecto",
                    None,
                ),
                "nombre",
                None,
            )
        )

    def get_area_id(
        self,
        obj,
    ):
        return self._obj_id(
            getattr(
                obj,
                "area",
                None,
            )
        )

    def get_area(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                getattr(
                    obj,
                    "area",
                    None,
                ),
                "nombre",
                None,
            )
        )

    def get_subarea_id(
        self,
        obj,
    ):
        return self._obj_id(
            getattr(
                obj,
                "subarea",
                None,
            )
        )

    def get_subarea(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                getattr(
                    obj,
                    "subarea",
                    None,
                ),
                "nombre",
                None,
            )
        )

    def get_pais_id(
        self,
        obj,
    ):
        return self._obj_id(
            getattr(
                obj,
                "pais",
                None,
            )
        )

    def get_pais(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                getattr(
                    obj,
                    "pais",
                    None,
                ),
                "nombre",
                None,
            )
        )

    def get_ciudad_id(
        self,
        obj,
    ):
        return self._obj_id(
            getattr(
                obj,
                "ciudad",
                None,
            )
        )

    def get_ciudad(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                getattr(
                    obj,
                    "ciudad",
                    None,
                ),
                "nombre",
                None,
            )
        )

    # ---------------------------------------------------------
    # Origen de la publicación
    # ---------------------------------------------------------

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

    # ========================================================
    # ESTADO
    # ========================================================

    def get_estado_label(
        self,
        obj,
    ):
        display = getattr(
            obj,
            "get_estado_display",
            None,
        )

        if callable(display):
            try:
                value = display()
            except Exception:
                value = None

            if value:
                return str(value)

        return str(
            getattr(
                obj,
                "estado",
                "",
            )
            or ""
        )

    def _get_latest_revision(
        self,
        obj,
    ):
        prefetched = getattr(
            obj,
            "revisiones_ordenadas",
            None,
        )

        if prefetched is not None:
            return (
                prefetched[0]
                if prefetched
                else None
            )

        try:
            return (
                PublicacionRevision.objects
                .select_related(
                    "revisor"
                )
                .filter(
                    publicacion=obj
                )
                .order_by(
                    "-created_at",
                    "-id",
                )
                .first()
            )
        except Exception:
            return None

    def get_ultima_revision(
        self,
        obj,
    ):
        revision = (
            self._get_latest_revision(
                obj
            )
        )

        if revision is None:
            return None

        reviewer = getattr(
            revision,
            "revisor",
            None,
        )

        reviewer_name = ""

        if reviewer is not None:
            try:
                reviewer_name = (
                    reviewer.get_full_name()
                    or ""
                ).strip()
            except Exception:
                reviewer_name = ""

            if not reviewer_name:
                reviewer_name = _to_str(
                    getattr(
                        reviewer,
                        "email",
                        None,
                    )
                )

        return {
            "id": revision.id,
            "decision": (
                revision.decision
            ),
            "decision_label": (
                revision.get_decision_display()
            ),
            "comentario": (
                revision.comentario
            ),
            "estado_anterior": (
                revision.estado_anterior
            ),
            "estado_resultante": (
                revision.estado_resultante
            ),
            "revisor_id": (
                revision.revisor_id
            ),
            "revisor": (
                reviewer_name
                or None
            ),
            "created_at": (
                revision.created_at
            ),
        }

    def _request_user(
        self,
    ):
        request = self.context.get(
            "request"
        )

        return getattr(
            request,
            "user",
            None,
        )

    def get_puede_enviar_revision(
        self,
        obj,
    ):
        try:
            return bool(
                can_enviar_a_revision(
                    self._request_user(),
                    obj,
                )
            )
        except Exception:
            return False

    def get_puede_reenviar_revision(
        self,
        obj,
    ):
        try:
            return bool(
                can_reenviar_a_revision(
                    self._request_user(),
                    obj,
                )
            )
        except Exception:
            return False

    def get_origen_tipo_label(
        self,
        obj,
    ):
        origen_tipo = (
            self._get_origen_tipo(
                obj
            )
        )

        try:
            label = (
                obj.get_origen_tipo_display()
            )
        except Exception:
            label = ""

        return (
            _to_str(label)
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
        origen_tipo = (
            self._get_origen_tipo(
                obj
            )
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
        origen_tipo = (
            self._get_origen_tipo(
                obj
            )
        )

        if origen_tipo == "ninguno":
            return None

        label = (
            self.get_origen_tipo_label(
                obj
            )
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

    # ---------------------------------------------------------
    # Periodo de publicación
    # ---------------------------------------------------------

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

    def get_archivo_pdf(
        self,
        obj,
    ):
        return self._build_file_url(
            self._get_pdf_file(
                obj
            )
        )

    def get_archivo_pdf_url(
        self,
        obj,
    ):
        return self.get_archivo_pdf(
            obj
        )

    def get_pdf_url(
        self,
        obj,
    ):
        return self.get_archivo_pdf(
            obj
        )

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

    def get_autores(
        self,
        obj,
    ):
        relaciones = (
            self._get_autor_rels(
                obj
            )
        )

        return (
            PublicacionAutorSerializer(
                relaciones,
                many=True,
                context=self.context,
            ).data
        )

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

    # ---------------------------------------------------------
    # Compatibilidad
    # ---------------------------------------------------------

    def get_resumen(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                obj,
                "resumen",
                None,
            )
        )

    def get_descripcion(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                obj,
                "descripcion",
                None,
            )
        )

    def get_abstract(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                obj,
                "abstract",
                None,
            )
        )

    def get_detalle(
        self,
        obj,
    ):
        return _to_str(
            getattr(
                obj,
                "detalle",
                None,
            )
        )

    # ---------------------------------------------------------
    # Ponencia
    # ---------------------------------------------------------

    def get_tipo_presentacion(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "ponencia",
                "tipo_presentacion",
            )
        )

    def get_tipo_presentacion_otro(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "ponencia",
                "tipo_presentacion_otro",
            )
        )

    def get_nombre_evento(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "ponencia",
                "nombre_evento",
            )
        )

    def get_nombre_ponencia(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "ponencia",
                "nombre_ponencia",
            )
        )

    def get_codigo_issn_isbn(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "ponencia",
                "codigo_issn_isbn",
            )
        )

    def get_link_evento(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "ponencia",
                "link_evento",
            )
        )

    # ---------------------------------------------------------
    # Artículo
    # ---------------------------------------------------------

    def get_tipo_articulo(
        self,
        obj,
    ):
        return self._get_tipo_articulo(
            obj
        )

    def get_nombre_articulo(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "nombre_articulo",
            )
        )

    def get_base_datos_indexada(
        self,
        obj,
    ):
        if (
            self._get_tipo_articulo(
                obj
            )
            != "regional"
        ):
            return ""

        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "base_datos_indexada",
            )
        )

    def get_base_datos_otra(
        self,
        obj,
    ):
        if (
            self._get_tipo_articulo(
                obj
            )
            != "regional"
        ):
            return ""

        base = self._related_attr(
            obj,
            "articulo",
            "base_datos_indexada",
        )

        if _to_lower(base) != "otra":
            return ""

        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "base_datos_otra",
            )
        )

    def get_codigo_doi(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "codigo_doi",
            )
        )

    def get_codigo_issn(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "codigo_issn",
            )
        )

    def get_nombre_revista(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "nombre_revista",
            )
        )

    def get_numero_revista(
        self,
        obj,
    ):
        return self._related_attr(
            obj,
            "articulo",
            "numero_revista",
            None,
        )

    def get_link_publicacion(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "link_publicacion",
            )
        )

    def get_link_revista(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "link_revista",
            )
        )

    def get_factor_impacto(
        self,
        obj,
    ):
        if (
            self._get_tipo_articulo(
                obj
            )
            != "alto_impacto"
        ):
            return ""

        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "factor_impacto",
            )
        )

    def get_cuartil(
        self,
        obj,
    ):
        if (
            self._get_tipo_articulo(
                obj
            )
            != "alto_impacto"
        ):
            return ""

        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "cuartil",
            )
        )

    def get_sjr(
        self,
        obj,
    ):
        if (
            self._get_tipo_articulo(
                obj
            )
            != "alto_impacto"
        ):
            return ""

        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "sjr",
            )
        )

    def get_jcr(
        self,
        obj,
    ):
        if (
            self._get_tipo_articulo(
                obj
            )
            != "alto_impacto"
        ):
            return ""

        return _to_str(
            self._related_attr(
                obj,
                "articulo",
                "jcr",
            )
        )

    # ---------------------------------------------------------
    # Revisión por pares
    # ---------------------------------------------------------

    def get_revisor_par_arbitraje(
        self,
        obj,
    ):
        return _first_filled(
            self._related_attr(
                obj,
                "ponencia",
                "revisor_par_arbitraje",
            ),
            self._related_attr(
                obj,
                "libro",
                "revisor_par_arbitraje",
            ),
            self._related_attr(
                obj,
                "capitulo_libro",
                "revisor_par_arbitraje",
            ),
        )

    # ---------------------------------------------------------
    # Libro / Capítulo
    # ---------------------------------------------------------

    def get_nombre_libro(
        self,
        obj,
    ):
        return _first_filled(
            self._related_attr(
                obj,
                "libro",
                "nombre_libro",
            ),
            self._related_attr(
                obj,
                "capitulo_libro",
                "nombre_libro",
            ),
        )

    def get_codigo_isbn(
        self,
        obj,
    ):
        return _first_filled(
            self._related_attr(
                obj,
                "libro",
                "codigo_isbn",
            ),
            self._related_attr(
                obj,
                "capitulo_libro",
                "codigo_isbn",
            ),
        )

    def get_editorial_compilador(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "libro",
                "editorial_compilador",
            )
        )

    def get_link_libro(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "libro",
                "link_libro",
            )
        )

    def get_nombre_capitulo(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "capitulo_libro",
                "nombre_capitulo",
            )
        )

    def get_editor_compilador(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "capitulo_libro",
                "editor_compilador",
            )
        )

    def get_link_capitulo(
        self,
        obj,
    ):
        return _to_str(
            self._related_attr(
                obj,
                "capitulo_libro",
                "link_capitulo",
            )
        )