"""
Servicios auxiliares para perfiles tipo Scholar.

Centraliza:
- nombre completo;
- afiliación;
- avatar;
- publicaciones;
- PDF;
- autores;
- autores relacionados;
- información pública del perfil.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    Exists,
    F,
    OuterRef,
    Prefetch,
    Q,
    TextField,
    Value,
)
from django.db.models.functions import (
    Cast,
    Coalesce,
    Concat,
)

from core.models import (
    Publicacion,
    PublicacionArchivo,
    PublicacionAutor,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
    tipo_publicacion_label,
)


# =============================================================
# HELPERS GENERALES
# =============================================================


def _to_str(value):
    return str(
        value or ""
    ).strip()


def _to_lower(value):
    value = _to_str(
        value
    )

    return (
        value.lower()
        if value
        else ""
    )


MESES_PUBLICACION = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def get_publicacion_month_label(
    publicacion,
):
    month = getattr(
        publicacion,
        "mes_publicacion",
        None,
    )

    if month in (None, ""):
        return None

    try:
        month = int(month)
    except (TypeError, ValueError):
        return None

    display = getattr(
        publicacion,
        "get_mes_publicacion_display",
        None,
    )

    if callable(display):
        try:
            label = _to_str(display())

            if label:
                return label
        except Exception:
            pass

    return MESES_PUBLICACION.get(month)


def _academic_identifiers(
    author,
):
    """
    Devuelve únicamente los identificadores académicos
    realmente registrados.
    """

    output = {}

    for field in (
        "orcid",
        "registro_senescyt",
        "google_scholar",
        "scopus_id",
    ):
        value = _to_str(
            getattr(
                author,
                field,
                None,
            )
        )

        if value:
            output[field] = value

    return output


def _safe_related(
    instance,
    relation_name,
):
    if instance is None:
        return None

    try:
        return getattr(
            instance,
            relation_name,
        )

    except (
        ObjectDoesNotExist,
        AttributeError,
    ):
        return None


def build_fullname_expression():
    return Cast(
        Concat(
            Coalesce(
                "nombres",
                Value(""),
            ),
            Value(" "),
            Coalesce(
                "apellidos",
                Value(""),
            ),
            output_field=TextField(),
        ),
        TextField(),
    )


# =============================================================
# AVATAR
# =============================================================


def get_user_avatar_absolute_url(
    request,
    user,
):
    if not user:
        return None

    avatar = getattr(
        user,
        "avatar",
        None,
    )

    if (
        not avatar
        or not getattr(
            avatar,
            "name",
            None,
        )
    ):
        return None

    try:
        url = avatar.url

    except (
        AttributeError,
        ValueError,
    ):
        return None

    if request:
        try:
            return (
                request.build_absolute_uri(
                    url
                )
            )

        except Exception:
            pass

    return url


# =============================================================
# ORGANIZACIÓN
# =============================================================


def get_author_org_label(
    author,
):
    user = getattr(
        author,
        "usuario",
        None,
    )

    institucion = _to_str(
        getattr(
            author,
            "institucion",
            None,
        )
    )

    if not user:
        if institucion:
            return institucion

        if getattr(
            author,
            "es_externo",
            False,
        ):
            return "Autor externo"

        return "ULEAM"

    sede = (
        getattr(
            user,
            "sede",
            None,
        )
        if bool(
            getattr(
                user,
                "es_institucional",
                False,
            )
        )
        else None
    )

    carrera = getattr(
        user,
        "carrera",
        None,
    )

    facultad = (
        getattr(
            carrera,
            "facultad",
            None,
        )
        if carrera
        else None
    )

    parts = []

    if (
        sede
        and getattr(
            sede,
            "nombre",
            None,
        )
    ):
        parts.append(
            sede.nombre
        )

    if (
        carrera
        and getattr(
            carrera,
            "nombre",
            None,
        )
    ):
        parts.append(
            carrera.nombre
        )

    if (
        facultad
        and getattr(
            facultad,
            "nombre",
            None,
        )
    ):
        parts.append(
            facultad.nombre
        )

    if parts:
        return " • ".join(
            parts
        )

    if institucion:
        return institucion

    if getattr(
        author,
        "es_externo",
        False,
    ):
        return "Autor externo"

    return "ULEAM"


def get_author_sede_payload(
    author,
):
    user = getattr(
        author,
        "usuario",
        None,
    )

    if not bool(
        getattr(
            user,
            "es_institucional",
            False,
        )
    ):
        return {
            "sede_id": None,
            "sede": None,
        }

    sede = getattr(
        user,
        "sede",
        None,
    )

    if sede is None:
        return {
            "sede_id": None,
            "sede": None,
        }

    nombre = _to_str(
        getattr(
            sede,
            "nombre",
            None,
        )
    ) or None

    return {
        "sede_id": getattr(
            sede,
            "pk",
            None,
        ),
        "sede": nombre,
    }


# =============================================================
# ARCHIVOS / PDF
# =============================================================


def _build_absolute_url(
    request,
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

    if request:
        try:
            return (
                request.build_absolute_uri(
                    url
                )
            )
        except Exception:
            pass

    return url


def _get_pdf_file(
    publicacion,
):
    # ---------------------------------------------------------
    # 1. PDF principal
    # ---------------------------------------------------------

    archivo_pdf = getattr(
        publicacion,
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

    # ---------------------------------------------------------
    # 2. Adjuntos prefetched
    # ---------------------------------------------------------

    prefetched = getattr(
        publicacion,
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

    # ---------------------------------------------------------
    # 3. Consulta de respaldo
    # ---------------------------------------------------------

    try:
        adjunto = (
            publicacion.archivos
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


def publicacion_has_pdf(
    publicacion,
):
    annotated = getattr(
        publicacion,
        "tiene_adjuntos_pdf",
        None,
    )

    archivo_pdf = getattr(
        publicacion,
        "archivo_pdf",
        None,
    )

    has_main_pdf = bool(
        archivo_pdf
        and getattr(
            archivo_pdf,
            "name",
            None,
        )
    )

    if annotated is not None:
        return bool(
            has_main_pdf
            or annotated
        )

    return bool(
        _get_pdf_file(
            publicacion
        )
    )


def publicacion_pdf_url(
    request,
    publicacion,
):
    return _build_absolute_url(
        request,
        _get_pdf_file(
            publicacion
        ),
    )


# =============================================================
# TÍTULO / MEDIO DE PUBLICACIÓN (VENUE)
# =============================================================


def get_publicacion_title_and_venue(
    publicacion,
):
    articulo = _safe_related(
        publicacion,
        "articulo",
    )

    if articulo:
        return (
            _to_str(
                articulo.nombre_articulo
            )
            or "—",
            _to_str(
                articulo.nombre_revista
            )
            or None,
        )

    ponencia = _safe_related(
        publicacion,
        "ponencia",
    )

    if ponencia:
        return (
            _to_str(
                ponencia.nombre_ponencia
            )
            or "—",
            _to_str(
                ponencia.nombre_evento
            )
            or None,
        )

    libro = _safe_related(
        publicacion,
        "libro",
    )

    if libro:
        return (
            _to_str(
                libro.nombre_libro
            )
            or "—",
            _to_str(
                libro.editorial_compilador
            )
            or None,
        )

    capitulo = _safe_related(
        publicacion,
        "capitulo_libro",
    )

    if capitulo:
        return (
            _to_str(
                capitulo.nombre_capitulo
            )
            or "—",
            _to_str(
                capitulo.nombre_libro
            )
            or None,
        )

    tipo = getattr(
        publicacion,
        "tipo",
        None,
    )

    tipo_nombre = (
        _to_str(
            getattr(
                tipo,
                "nombre",
                None,
            )
        )
        or "Publicación"
    )

    numero = (
        getattr(
            publicacion,
            "numero",
            None,
        )
        or publicacion.id
    )

    return (
        f"{tipo_nombre} #{numero}",
        None,
    )


# =============================================================
# AUTORES
# =============================================================


def _get_publicacion_autor_rels(
    publicacion,
):
    participaciones = getattr(
        publicacion,
        "participaciones_ordenadas",
        None,
    )

    if participaciones is not None:
        return participaciones

    prefetched = getattr(
        publicacion,
        "_prefetched_objects_cache",
        {},
    )

    if "participaciones" in prefetched:
        return sorted(
            prefetched[
                "participaciones"
            ],
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

    return (
        PublicacionAutor.objects
        .select_related(
            "autor",
            "autor__usuario",
        )
        .filter(
            publicacion=publicacion
        )
        .order_by(
            "orden",
            "id",
        )
    )


def _author_name(
    author,
):
    if not author:
        return "—"

    name = (
        f"{_to_str(author.nombres)} "
        f"{_to_str(author.apellidos)}"
    ).strip()

    return (
        name
        or _to_str(
            author.correo
        )
        or _to_str(
            author.identificacion
        )
        or "—"
    )


def get_author_authors_string(
    publicacion,
) -> str:
    names = []

    for rel in _get_publicacion_autor_rels(
        publicacion
    ):
        autor = getattr(
            rel,
            "autor",
            None,
        )

        if not autor:
            continue

        label = _author_name(
            autor
        )

        if (
            label
            and label != "—"
        ):
            names.append(
                label
            )

    return (
        ", ".join(names)
        if names
        else "—"
    )


# =============================================================
# PERFIL
# =============================================================


def build_public_profile_payload(
    *,
    request,
    author,
    is_me=False,
):
    user = getattr(
        author,
        "usuario",
        None,
    )

    name = _author_name(
        author
    )

    org = get_author_org_label(
        author
    )

    avatar = (
        get_user_avatar_absolute_url(
            request,
            user,
        )
    )

    # ---------------------------------------------------------
    # Publicaciones asociadas
    #
    # Se consideran:
    # - relación PublicacionAutor;
    # - publicaciones creadas por el usuario vinculado,
    #   útil para registros históricos incompletos.
    # ---------------------------------------------------------

    filtros = Q(
        participaciones__autor_id=(
            author.id
        )
    )

    if user:
        filtros |= Q(
            usuario_creador=user
        )

    adjuntos_pdf = (
        PublicacionArchivo.objects
        .filter(
            publicacion_id=(
                OuterRef("pk")
            ),
        )
        .exclude(
            archivo=""
        )
    )

    autores_prefetch = Prefetch(
        "participaciones",
        queryset=(
            PublicacionAutor.objects
            .select_related(
                "autor",
                "autor__usuario",
                "autor__usuario__sede",
                "autor__usuario__carrera",
                "autor__usuario__carrera__facultad",
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

    publicaciones_qs = (
        Publicacion.objects
        .select_related(
            "tipo",
            "proyecto",
            "sede",
            "carrera",
            "carrera__facultad",
            "articulo",
            "ponencia",
            "libro",
            "capitulo_libro",
        )
        .prefetch_related(
            autores_prefetch,
            "archivos",
        )
        .annotate(
            tiene_adjuntos_pdf=Exists(
                adjuntos_pdf
            )
        )
        .filter(
            filtros,
            estado=Publicacion.ESTADO_APROBADA,
        )
        .distinct()
    )

    publicaciones_qs = (
        annotate_tipo_publicacion_final(
            publicaciones_qs
        )
        .exclude(
            tipo_publicacion_final=(
                "sin_clasificar"
            )
        )
        .order_by(
            F(
                "anio_publicacion"
            ).desc(
                nulls_last=True
            ),
            F(
                "mes_publicacion"
            ).desc(
                nulls_last=True
            ),
            "-id",
        )
    )

    publicaciones = []

    years = []

    related_authors_map = {}

    for pub in publicaciones_qs:
        title, venue = (
            get_publicacion_title_and_venue(
                pub
            )
        )

        tipo_final = getattr(
            pub,
            "tipo_publicacion_final",
            "sin_clasificar",
        )

        has_pdf = publicacion_has_pdf(
            pub
        )

        pdf_url = publicacion_pdf_url(
            request,
            pub,
        )

        year = getattr(
            pub,
            "anio_publicacion",
            None,
        )

        month = getattr(
            pub,
            "mes_publicacion",
            None,
        )

        month_label = get_publicacion_month_label(
            pub
        )

        if year:
            years.append(
                int(year)
            )

        # -----------------------------------------------------
        # Autores relacionados
        # -----------------------------------------------------

        for rel in _get_publicacion_autor_rels(
            pub
        ):
            related_author = getattr(
                rel,
                "autor",
                None,
            )

            if (
                not related_author
                or related_author.id == author.id
            ):
                continue

            if (
                related_author.id
                not in related_authors_map
            ):
                related_author_user = getattr(
                    related_author,
                    "usuario",
                    None,
                )

                related_sede = (
                    get_author_sede_payload(
                        related_author
                    )
                )

                related_authors_map[
                    related_author.id
                ] = {
                    "id": related_author.id,
                    "name": _author_name(
                        related_author
                    ),
                    "org": (
                        get_author_org_label(
                            related_author
                        )
                    ),
                    "sede_id": related_sede[
                        "sede_id"
                    ],
                    "sede": related_sede[
                        "sede"
                    ],
                    "avatar": (
                        get_user_avatar_absolute_url(
                            request,
                            related_author_user,
                        )
                    ),
                }

        publicaciones.append(
            {
                "id": pub.id,

                "title": title,
                "titulo": title,

                "authors": (
                    get_author_authors_string(
                        pub
                    )
                ),

                "venue": venue,

                "sede_id": getattr(
                    pub,
                    "sede_id",
                    None,
                ),
                "sede": (
                    _to_str(
                        getattr(
                            getattr(
                                pub,
                                "sede",
                                None,
                            ),
                            "nombre",
                            None,
                        )
                    )
                    or None
                ),

                # No existe todavía un modelo de citas
                # científicas en el dominio.
                "citedBy": 0,

                "year": year,
                "anio_publicacion": year,

                "month": month,
                "mes_publicacion": month,
                "mes_publicacion_label": month_label,

                "type": (
                    {
                        "id": pub.tipo_id,
                        "nombre": (
                            pub.tipo.nombre
                        ),
                        "codigo": (
                            pub.tipo.codigo
                        ),
                    }
                    if pub.tipo
                    else None
                ),

                "tipo_publicacion_final": (
                    tipo_final
                ),

                "tipo_publicacion_final_label": (
                    tipo_publicacion_label(
                        tipo_final
                    )
                ),

                "hasPdf": has_pdf,
                "has_pdf": has_pdf,
                "tiene_pdf": has_pdf,

                "pdf_url": pdf_url,
                "archivo_pdf_url": (
                    pdf_url
                ),
            }
        )

    since_year = (
        min(years)
        if years
        else None
    )

    sede_payload = (
        get_author_sede_payload(
            author
        )
    )

    payload = {
        "id": author.id,

        "name": name,
        "org": org,
        "sede_id": sede_payload[
            "sede_id"
        ],
        "sede": sede_payload[
            "sede"
        ],
        "avatar": avatar,

        "verified": None,

        "tags": [],

        # Ya no se fija artificialmente en 2019.
        "sinceYear": since_year,

        # El sistema actualmente no posee un modelo
        # de citas bibliométricas, por lo que estos
        # indicadores se mantienen en cero.
        "metrics": {
            "citesTotal": 0,
            "citesSince": 0,
            "hTotal": 0,
            "hSince": 0,
            "i10Total": 0,
            "i10Since": 0,
        },

        "publications": (
            publicaciones
        ),

        "related_authors": list(
            related_authors_map.values()
        ),

        "autores_relacionados": list(
            related_authors_map.values()
        ),

        # Alias temporal para no romper interfaces antiguas.
        # No representa un rol de autoría.
        "coauthors": list(
            related_authors_map.values()
        ),
    }

    academic_identifiers = _academic_identifiers(
        author
    )

    if academic_identifiers:
        payload["academic_identifiers"] = (
            academic_identifiers
        )

        for field, value in academic_identifiers.items():
            payload[field] = value

    if is_me:
        payload["is_me"] = True

    return payload