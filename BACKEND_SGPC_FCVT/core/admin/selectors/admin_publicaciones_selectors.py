"""Selectors administrativos para publicaciones."""

from django.db.models import (
    BooleanField,
    Case,
    CharField,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Q,
    Value,
    When,
)
from django.db.models.functions import Coalesce, NullIf

from core.models import (
    Publicacion,
    PublicacionArchivo,
    PublicacionAutor,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
    normalize_tipo_publicacion_final,
)


DEFAULT_ORDERING = ("-updated_at", "-id")

ORDERING_MAP = {
    "updated_desc": DEFAULT_ORDERING,
    "updated_asc": ("updated_at", "id"),
    "created_desc": ("-created_at", "-id"),
    "created_asc": ("created_at", "id"),
    "fecha_desc": ("-fecha_publicacion", "-id"),
    "fecha_asc": ("fecha_publicacion", "id"),
    "anio_desc": ("-anio_publicacion", "-id"),
    "anio_asc": ("anio_publicacion", "id"),
    "titulo_asc": ("titulo_admin", "id"),
    "titulo_desc": ("-titulo_admin", "-id"),
    "numero_desc": ("-numero", "-id"),
    "numero_asc": ("numero", "id"),
}


def _text(value):
    return str(value or "").strip()


def _positive_int(value):
    if (
        value in (
            None,
            "",
            "null",
            "None",
        )
        or isinstance(value, bool)
    ):
        return None

    try:
        parsed = int(value)
    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None

    return parsed if parsed > 0 else None


def _year(value):
    parsed = _positive_int(value)

    if (
        parsed is not None
        and 1900 <= parsed <= 2100
    ):
        return parsed

    return None


def _bool(value):
    if value is None or isinstance(value, bool):
        return value

    value = _text(value).lower()

    if value in {
        "1",
        "true",
        "yes",
        "y",
        "on",
        "si",
        "sí",
    }:
        return True

    if value in {
        "0",
        "false",
        "no",
        "n",
        "off",
    }:
        return False

    return None


def _participations_queryset():
    return (
        PublicacionAutor.objects
        .select_related(
            "autor",
            "autor__usuario",
        )
        .order_by(
            "orden",
            "id",
        )
    )


def _files_queryset():
    return (
        PublicacionArchivo.objects
        .order_by(
            "orden",
            "id",
        )
    )


def _annotate(queryset):
    attachments = (
        PublicacionArchivo.objects
        .filter(
            publicacion_id=OuterRef("pk")
        )
    )

    return queryset.annotate(
        adjuntos_total=Count(
            "archivos",
            distinct=True,
        ),

        tiene_adjuntos=Exists(
            attachments
        ),

        titulo_admin=Coalesce(
            NullIf(
                "articulo__nombre_articulo",
                Value(""),
            ),
            NullIf(
                "ponencia__nombre_ponencia",
                Value(""),
            ),
            NullIf(
                "libro__nombre_libro",
                Value(""),
            ),
            NullIf(
                "capitulo_libro__nombre_capitulo",
                Value(""),
            ),
            NullIf(
                "proyecto__nombre",
                Value(""),
            ),
            Value(
                "",
                output_field=CharField(),
            ),
            output_field=CharField(),
        ),

        tiene_pdf_principal=Case(
            When(
                Q(
                    archivo_pdf__isnull=False
                )
                & ~Q(
                    archivo_pdf=""
                ),
                then=Value(True),
            ),
            default=Value(False),
            output_field=BooleanField(),
        ),
    )


def admin_publicaciones_base_queryset(
    *,
    include_files=True,
):
    queryset = (
        Publicacion.objects
        .select_related(
            "tipo",
            "usuario_creador",
            "admin_registrador",
            "carrera__facultad",
            "proyecto",
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
            Prefetch(
                "participaciones",
                queryset=(
                    _participations_queryset()
                ),
                to_attr=(
                    "participaciones_ordenadas"
                ),
            )
        )
    )

    if include_files:
        queryset = queryset.prefetch_related(
            Prefetch(
                "archivos",
                queryset=(
                    _files_queryset()
                ),
                to_attr=(
                    "archivos_ordenados"
                ),
            )
        )

    queryset = (
        annotate_tipo_publicacion_final(
            queryset
        )
    )

    queryset = _annotate(
        queryset
    )

    return queryset.order_by(
        *DEFAULT_ORDERING
    )


def admin_publicaciones_list_queryset():
    return admin_publicaciones_base_queryset(
        include_files=False
    )


def admin_publicaciones_detail_queryset():
    return admin_publicaciones_base_queryset(
        include_files=True
    )


def filter_admin_publicaciones_queryset(
    queryset,
    *,
    q="",
    tipo="",
    usuario_objetivo_id=None,
    autor_objetivo_id=None,
    admin_registrador_id=None,
    facultad_id=None,
    carrera_id=None,
    anio=None,
    solo_delegadas=None,
    solo_con_pdf=None,
    solo_con_adjuntos=None,
    ordering="",
):
    query = _text(q)

    publication_type = (
        normalize_tipo_publicacion_final(
            tipo
        )
    )

    user_id = _positive_int(
        usuario_objetivo_id
    )

    author_id = _positive_int(
        autor_objetivo_id
    )

    admin_id = _positive_int(
        admin_registrador_id
    )

    faculty_id = _positive_int(
        facultad_id
    )

    career_id = _positive_int(
        carrera_id
    )

    publication_year = _year(
        anio
    )

    delegated = _bool(
        solo_delegadas
    )

    pdf = _bool(
        solo_con_pdf
    )

    attachments = _bool(
        solo_con_adjuntos
    )

    if user_id is not None:
        queryset = queryset.filter(
            usuario_creador_id=user_id
        )

    if author_id is not None:
        queryset = queryset.filter(
            participaciones__autor_id=author_id
        )

    if admin_id is not None:
        queryset = queryset.filter(
            admin_registrador_id=admin_id
        )

    if faculty_id is not None:
        queryset = queryset.filter(
            carrera__facultad_id=faculty_id
        )

    if career_id is not None:
        queryset = queryset.filter(
            carrera_id=career_id
        )

    if publication_year is not None:
        queryset = queryset.filter(
            anio_publicacion=publication_year
        )

    if delegated is True:
        queryset = queryset.filter(
            registrado_por_admin=True
        )

    elif delegated is False:
        queryset = queryset.filter(
            registrado_por_admin=False
        )

    if pdf is True:
        queryset = queryset.filter(
            Q(
                tiene_pdf_principal=True
            )
            | Q(
                tiene_adjuntos=True
            )
        )

    elif pdf is False:
        queryset = queryset.filter(
            tiene_pdf_principal=False,
            tiene_adjuntos=False,
        )

    if attachments is True:
        queryset = queryset.filter(
            tiene_adjuntos=True
        )

    elif attachments is False:
        queryset = queryset.filter(
            tiene_adjuntos=False
        )

    if publication_type:
        queryset = queryset.filter(
            tipo_publicacion_final=(
                publication_type
            )
        )

    if query:
        search = (
            Q(
                tipo__nombre__icontains=query
            )
            | Q(
                tipo__codigo__icontains=query
            )
            | Q(
                titulo_admin__icontains=query
            )
            | Q(
                proyecto__nombre__icontains=query
            )
            | Q(
                carrera__nombre__icontains=query
            )
            | Q(
                carrera__facultad__nombre__icontains=query
            )
            | Q(
                carrera__facultad__siglas__icontains=query
            )
            | Q(
                area__nombre__icontains=query
            )
            | Q(
                subarea__nombre__icontains=query
            )
            | Q(
                pais__nombre__icontains=query
            )
            | Q(
                ciudad__nombre__icontains=query
            )
            | Q(
                usuario_creador__nombres__icontains=query
            )
            | Q(
                usuario_creador__apellidos__icontains=query
            )
            | Q(
                usuario_creador__email__icontains=query
            )
            | Q(
                usuario_creador__identificacion__icontains=query
            )
            | Q(
                admin_registrador__nombres__icontains=query
            )
            | Q(
                admin_registrador__apellidos__icontains=query
            )
            | Q(
                admin_registrador__email__icontains=query
            )
            | Q(
                participaciones__autor__nombres__icontains=query
            )
            | Q(
                participaciones__autor__apellidos__icontains=query
            )
            | Q(
                participaciones__autor__correo__icontains=query
            )
            | Q(
                participaciones__autor__identificacion__icontains=query
            )
            | Q(
                participaciones__autor__institucion__icontains=query
            )
            | Q(
                articulo__nombre_articulo__icontains=query
            )
            | Q(
                articulo__nombre_revista__icontains=query
            )
            | Q(
                articulo__codigo_doi__icontains=query
            )
            | Q(
                articulo__codigo_issn__icontains=query
            )
            | Q(
                ponencia__nombre_evento__icontains=query
            )
            | Q(
                ponencia__nombre_ponencia__icontains=query
            )
            | Q(
                ponencia__codigo_issn_isbn__icontains=query
            )
            | Q(
                libro__nombre_libro__icontains=query
            )
            | Q(
                libro__codigo_isbn__icontains=query
            )
            | Q(
                libro__editorial_compilador__icontains=query
            )
            | Q(
                capitulo_libro__nombre_capitulo__icontains=query
            )
            | Q(
                capitulo_libro__nombre_libro__icontains=query
            )
            | Q(
                capitulo_libro__codigo_isbn__icontains=query
            )
            | Q(
                capitulo_libro__editor_compilador__icontains=query
            )
        )

        numeric = _positive_int(
            query
        )

        if numeric is not None:
            search |= (
                Q(
                    pk=numeric
                )
                | Q(
                    numero=numeric
                )
                | Q(
                    usuario_creador_id=numeric
                )
                | Q(
                    participaciones__autor_id=numeric
                )
            )

        queryset = queryset.filter(
            search
        )

    order_fields = ORDERING_MAP.get(
        _text(ordering).lower(),
        DEFAULT_ORDERING,
    )

    return (
        queryset
        .distinct()
        .order_by(
            *order_fields
        )
    )