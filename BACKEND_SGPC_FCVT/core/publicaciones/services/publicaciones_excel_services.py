"""
Servicio de exportación Excel de publicaciones.

Genera una hoja diferente según el tipo:

- Artículos de alto impacto
- Artículos regionales
- Ponencias
- Libros
- Capítulos de libro

Regla institucional:

    Publicacion -> Carrera -> Facultad

Nunca se consulta Publicacion.facultad como campo de BD.
"""

from collections import OrderedDict
from io import BytesIO

from django.db.models import (
    Prefetch,
    Q,
)
from openpyxl import Workbook
from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    PatternFill,
    Side,
)
from openpyxl.utils import (
    get_column_letter,
)

from core.models import (
    Publicacion,
    PublicacionAutor,
)


TIPO_ORDER = [
    "alto_impacto",
    "regional",
    "ponencia",
    "libro",
    "capitulo",
]


TIPO_SHEET_NAMES = {
    "alto_impacto": (
        "Matriz de artículos de alto impacto"
    ),
    "regional": (
        "Matriz de artículos regionales"
    ),
    "ponencia": (
        "Matriz de ponencias"
    ),
    "libro": (
        "Matriz de libros"
    ),
    "capitulo": (
        "Matriz de capítulos de libro"
    ),
}


NOTE_MAP = {
    "alto_impacto": (
        "Artículos de alto impacto: datos institucionales, "
        "revista, impacto, cuartil, autores y archivos."
    ),
    "regional": (
        "Artículos regionales: datos institucionales, "
        "indexación, revista, autores y archivos."
    ),
    "ponencia": (
        "Ponencias: evento, ubicación, presentación, "
        "arbitraje, autores y archivos."
    ),
    "libro": (
        "Libros: información editorial, arbitraje, "
        "autores y archivos."
    ),
    "capitulo": (
        "Capítulos de libro: libro contenedor, arbitraje, "
        "autores y archivos."
    ),
}


TITLE_BG = "E5E7EB"
TITLE_TEXT = "0F172A"
NAVY_2 = "254F87"
HEADER_BG = "9BBADD"
HEADER_TEXT = "11253D"
BODY_BG = "F2F2F2"
BODY_BG_ALT = "ECECEC"
NUM_BG = "DCE9F7"
BORDER = "6F89A6"


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

    value = _normalize_lower(
        value
    )

    return value in {
        "1",
        "true",
        "yes",
        "si",
        "sí",
        "on",
    }


def _safe_related(
    instance,
    attr_name,
):
    if instance is None:
        return None

    try:
        return getattr(
            instance,
            attr_name,
        )
    except Exception:
        return None


def _facultad_from_publicacion(
    publicacion,
):
    carrera = _safe_related(
        publicacion,
        "carrera",
    )

    return _safe_related(
        carrera,
        "facultad",
    )


def _tipo_bucket(
    publicacion,
):
    articulo = _safe_related(
        publicacion,
        "articulo",
    )

    if articulo:
        tipo_articulo = (
            _normalize_lower(
                articulo.tipo_articulo
            )
        )

        if (
            tipo_articulo
            == "alto_impacto"
        ):
            return "alto_impacto"

        if tipo_articulo == "regional":
            return "regional"

    if _safe_related(
        publicacion,
        "ponencia",
    ):
        return "ponencia"

    if _safe_related(
        publicacion,
        "libro",
    ):
        return "libro"

    if _safe_related(
        publicacion,
        "capitulo_libro",
    ):
        return "capitulo"

    return None


def _resolve_tipo_filter(
    raw_tipo,
):
    value = _normalize_lower(
        raw_tipo
    )

    alias_map = {
        "alto_impacto": "alto_impacto",
        "articulo_alto_impacto": "alto_impacto",
        "aai": "alto_impacto",
        "alto-impacto": "alto_impacto",

        "regional": "regional",
        "articulo_regional": "regional",
        "ar": "regional",

        "ponencia": "ponencia",
        "ponencias": "ponencia",
        "pon": "ponencia",

        "libro": "libro",
        "libros": "libro",
        "lib": "libro",

        "capitulo": "capitulo",
        "capítulos": "capitulo",
        "capitulos": "capitulo",
        "capitulo_libro": "capitulo",
        "cap": "capitulo",
    }

    return alias_map.get(
        value
    )


def _filter_id(
    filters,
    *keys,
):
    for key in keys:
        value = _normalize_text(
            filters.get(key)
        )

        if value:
            return value

    return ""


def _build_queryset(filters):
    filters = filters or {}

    tipo = _resolve_tipo_filter(
        filters.get("tipo")
        or filters.get(
            "tipo_publicacion_final"
        )
    )

    anio = _parse_year(
        filters.get("anio")
    )

    anio_desde = _parse_year(
        filters.get("anio_desde")
    )

    anio_hasta = _parse_year(
        filters.get("anio_hasta")
    )

    texto = _normalize_text(
        filters.get("texto")
        or filters.get("q")
    )

    facultad_id = _filter_id(
        filters,
        "facultad",
        "facultad_id",
    )

    carrera_id = _filter_id(
        filters,
        "carrera",
        "carrera_id",
    )

    proyecto_id = _filter_id(
        filters,
        "proyecto",
        "proyecto_id",
    )

    solo_con_pdf = _parse_bool(
        filters.get(
            "solo_con_pdf"
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

            "carrera",
            "carrera__facultad",

            "area",
            "subarea",

            "pais",
            "ciudad",

            "usuario_creador",
            "admin_registrador",

            "articulo",
            "ponencia",
            "libro",
            "capitulo_libro",
        )
        .prefetch_related(
            autores_prefetch,
            "archivos",
        )
        .all()
    )

    # ---------------------------------------------------------
    # Año
    # ---------------------------------------------------------

    if anio:
        queryset = (
            queryset.filter(
                anio_publicacion=anio
            )
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

    # ---------------------------------------------------------
    # Relaciones
    # ---------------------------------------------------------

    if facultad_id.isdigit():
        queryset = queryset.filter(
            carrera__facultad_id=(
                int(facultad_id)
            )
        )

    if carrera_id.isdigit():
        queryset = queryset.filter(
            carrera_id=int(
                carrera_id
            )
        )

    if proyecto_id.isdigit():
        queryset = queryset.filter(
            proyecto_id=int(
                proyecto_id
            )
        )

    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------

    if solo_con_pdf:
        queryset = (
            queryset
            .filter(
                Q(
                    archivo_pdf__isnull=False
                )
                & ~Q(
                    archivo_pdf=""
                )
                | Q(
                    archivos__archivo__isnull=False
                )
                & ~Q(
                    archivos__archivo=""
                )
            )
            .distinct()
        )

    # ---------------------------------------------------------
    # Texto
    # ---------------------------------------------------------

    if texto:
        queryset = (
            queryset
            .filter(
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

                | Q(
                    ponencia__nombre_evento__icontains=texto
                )
                | Q(
                    ponencia__nombre_ponencia__icontains=texto
                )

                | Q(
                    libro__nombre_libro__icontains=texto
                )
                | Q(
                    libro__editorial_compilador__icontains=texto
                )

                | Q(
                    capitulo_libro__nombre_capitulo__icontains=texto
                )
                | Q(
                    capitulo_libro__nombre_libro__icontains=texto
                )

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

    publicaciones = list(
        queryset.order_by(
            "-fecha_publicacion",
            "-id",
        )
    )

    # ---------------------------------------------------------
    # Tipo específico
    # ---------------------------------------------------------

    if tipo:
        publicaciones = [
            publicacion
            for publicacion
            in publicaciones
            if (
                _tipo_bucket(
                    publicacion
                )
                == tipo
            )
        ]

    return publicaciones


def _get_participaciones(
    publicacion,
):
    return (
        getattr(
            publicacion,
            "participaciones_ordenadas",
            None,
        )
        or []
    )


def _get_archivos(
    publicacion,
):
    prefetched = getattr(
        publicacion,
        "_prefetched_objects_cache",
        {},
    )

    if "archivos" in prefetched:
        return sorted(
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

    try:
        return list(
            publicacion.archivos
            .all()
            .order_by(
                "orden",
                "id",
            )
        )

    except Exception:
        return []


def _autor_data(
    publicacion,
):
    participaciones = (
        _get_participaciones(
            publicacion
        )
    )

    principal = ""
    coautores = []

    for participacion in participaciones:
        autor = _safe_related(
            participacion,
            "autor",
        )

        if autor is None:
            continue

        nombre = (
            f"{_normalize_text(autor.nombres)} "
            f"{_normalize_text(autor.apellidos)}"
        ).strip()

        if not nombre:
            nombre = (
                _normalize_text(
                    autor.correo
                )
                or _normalize_text(
                    autor.identificacion
                )
            )

        if (
            participacion.orden == 1
            or participacion.rol_autoria
            == "principal"
        ):
            principal = nombre

        elif nombre:
            coautores.append(
                nombre
            )

    return (
        principal or "—",
        " | ".join(
            coautores
        )
        or "—",
    )


def _adjuntos_text(
    publicacion,
):
    archivos = _get_archivos(
        publicacion
    )

    nombres = [
        _normalize_text(
            archivo.nombre
        )
        for archivo in archivos
        if _normalize_text(
            archivo.nombre
        )
    ]

    if nombres:
        return " | ".join(
            nombres
        )

    return "—"


def _principal_pdf_text(
    publicacion,
):
    archivo = getattr(
        publicacion,
        "archivo_pdf",
        None,
    )

    name = _normalize_text(
        getattr(
            archivo,
            "name",
            None,
        )
    )

    return (
        name
        or "—"
    )


def _pdf_text(
    publicacion,
):
    principal = (
        _principal_pdf_text(
            publicacion
        )
    )

    adjuntos = (
        _adjuntos_text(
            publicacion
        )
    )

    values = []

    if principal != "—":
        values.append(
            principal
        )

    if adjuntos != "—":
        values.append(
            adjuntos
        )

    return (
        " | ".join(values)
        or "—"
    )


def _has_any_pdf(
    publicacion,
):
    archivo = getattr(
        publicacion,
        "archivo_pdf",
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
        return True

    return bool(
        _get_archivos(
            publicacion
        )
    )


def _display_choice(
    instance,
    method_name,
    fallback="—",
):
    try:
        method = getattr(
            instance,
            method_name,
            None,
        )

        if callable(method):
            value = method()

            return (
                _normalize_text(
                    value
                )
                or fallback
            )

    except Exception:
        pass

    return fallback


def _display_cuartil(
    articulo,
):
    value = _normalize_lower(
        articulo.cuartil
    )

    if value == "sin_cuartil":
        return "Sin cuartil"

    if not value:
        return "—"

    return _display_choice(
        articulo,
        "get_cuartil_display",
        value.upper(),
    )


def _display_factor_impacto(
    articulo,
):
    value = _normalize_lower(
        articulo.factor_impacto
    )

    if not value:
        return "—"

    return _display_choice(
        articulo,
        "get_factor_impacto_display",
        value.upper(),
    )


def _display_base_indexada(
    articulo,
):
    value = _normalize_lower(
        articulo.base_datos_indexada
    )

    if not value:
        return "—"

    return _display_choice(
        articulo,
        "get_base_datos_indexada_display",
        value,
    )


def _base_common(
    publicacion,
):
    facultad = (
        _facultad_from_publicacion(
            publicacion
        )
    )

    carrera = _safe_related(
        publicacion,
        "carrera",
    )

    proyecto = _safe_related(
        publicacion,
        "proyecto",
    )

    area = _safe_related(
        publicacion,
        "area",
    )

    subarea = _safe_related(
        publicacion,
        "subarea",
    )

    return OrderedDict(
        {
            "N°": (
                publicacion.numero
                or publicacion.id
            ),
            "Facultad": (
                _normalize_text(
                    getattr(
                        facultad,
                        "nombre",
                        "",
                    )
                )
                or "—"
            ),
            "Carrera": (
                _normalize_text(
                    getattr(
                        carrera,
                        "nombre",
                        "",
                    )
                )
                or "—"
            ),
            "Proyecto": (
                _normalize_text(
                    getattr(
                        proyecto,
                        "nombre",
                        "",
                    )
                )
                or "—"
            ),
            "Área": (
                _normalize_text(
                    getattr(
                        area,
                        "nombre",
                        "",
                    )
                )
                or "—"
            ),
            "Subárea": (
                _normalize_text(
                    getattr(
                        subarea,
                        "nombre",
                        "",
                    )
                )
                or "—"
            ),
        }
    )


def _fecha_text(
    publicacion,
):
    return (
        publicacion.fecha_publicacion.isoformat()
        if publicacion.fecha_publicacion
        else "—"
    )


def _row_alto_impacto(
    publicacion,
):
    principal, coautores = (
        _autor_data(
            publicacion
        )
    )

    articulo = publicacion.articulo

    row = _base_common(
        publicacion
    )

    row.update(
        {
            "Origen publicación": (
                publicacion
                .get_origen_tipo_display()
                if publicacion.origen_tipo
                else "—"
            ),
            "Grado / programa": (
                _normalize_text(
                    publicacion.origen_grado
                )
                or "—"
            ),
            "Título del artículo": (
                articulo.nombre_articulo
            ),
            "Fecha publicación": (
                _fecha_text(
                    publicacion
                )
            ),
            "Nombre revista": (
                articulo.nombre_revista
            ),
            "N° revista": (
                articulo.numero_revista
                if articulo.numero_revista
                is not None
                else "—"
            ),
            "ISSN": (
                articulo.codigo_issn
            ),
            "DOI": (
                _normalize_text(
                    articulo.codigo_doi
                )
                or "—"
            ),
            "Factor impacto": (
                _display_factor_impacto(
                    articulo
                )
            ),
            "Cuartil": (
                _display_cuartil(
                    articulo
                )
            ),
            "SJR": (
                _normalize_text(
                    articulo.sjr
                )
                or "—"
            ),
            "Link revista": (
                _normalize_text(
                    articulo.link_revista
                )
                or "—"
            ),
            "Link publicación": (
                _normalize_text(
                    articulo.link_publicacion
                )
                or "—"
            ),
            "Autor principal": principal,
            "Coautores": coautores,
            "Archivos PDF": (
                _pdf_text(
                    publicacion
                )
            ),
        }
    )

    return row


def _row_regional(
    publicacion,
):
    principal, coautores = (
        _autor_data(
            publicacion
        )
    )

    articulo = publicacion.articulo

    row = _base_common(
        publicacion
    )

    row.update(
        {
            "Origen publicación": (
                publicacion
                .get_origen_tipo_display()
                if publicacion.origen_tipo
                else "—"
            ),
            "Grado / programa": (
                _normalize_text(
                    publicacion.origen_grado
                )
                or "—"
            ),
            "Título del artículo": (
                articulo.nombre_articulo
            ),
            "Fecha publicación": (
                _fecha_text(
                    publicacion
                )
            ),
            "Base indexada": (
                _display_base_indexada(
                    articulo
                )
            ),
            "Otra base": (
                _normalize_text(
                    articulo.base_datos_otra
                )
                if (
                    _normalize_lower(
                        articulo
                        .base_datos_indexada
                    )
                    == "otra"
                )
                else "—"
            )
            or "—",
            "Nombre revista": (
                articulo.nombre_revista
            ),
            "N° revista": (
                articulo.numero_revista
                if articulo.numero_revista
                is not None
                else "—"
            ),
            "ISSN": (
                articulo.codigo_issn
            ),
            "DOI": (
                _normalize_text(
                    articulo.codigo_doi
                )
                or "—"
            ),
            "Link revista": (
                _normalize_text(
                    articulo.link_revista
                )
                or "—"
            ),
            "Link publicación": (
                _normalize_text(
                    articulo.link_publicacion
                )
                or "—"
            ),
            "Autor principal": principal,
            "Coautores": coautores,
            "Archivos PDF": (
                _pdf_text(
                    publicacion
                )
            ),
        }
    )

    return row


def _row_ponencia(
    publicacion,
):
    principal, coautores = (
        _autor_data(
            publicacion
        )
    )

    ponencia = publicacion.ponencia

    pais = _safe_related(
        publicacion,
        "pais",
    )

    ciudad = _safe_related(
        publicacion,
        "ciudad",
    )

    row = _base_common(
        publicacion
    )

    row.update(
        {
            "Nombre del evento": (
                ponencia.nombre_evento
            ),
            "Nombre ponencia": (
                ponencia.nombre_ponencia
            ),
            "Fecha presentación": (
                _fecha_text(
                    publicacion
                )
            ),
            "País": (
                _normalize_text(
                    getattr(
                        pais,
                        "nombre",
                        "",
                    )
                )
                or "—"
            ),
            "Ciudad": (
                _normalize_text(
                    getattr(
                        ciudad,
                        "nombre",
                        "",
                    )
                )
                or "—"
            ),
            "ISSN / ISBN": (
                _normalize_text(
                    ponencia
                    .codigo_issn_isbn
                )
                or "—"
            ),
            "Tipo presentación": (
                _display_choice(
                    ponencia,
                    "get_tipo_presentacion_display",
                )
            ),
            "Tipo presentación - Otro": (
                _normalize_text(
                    ponencia
                    .tipo_presentacion_otro
                )
                or "—"
            ),
            "Revisor / arbitraje": (
                _display_choice(
                    ponencia,
                    "get_revisor_par_arbitraje_display",
                )
            ),
            "Link evento": (
                _normalize_text(
                    ponencia.link_evento
                )
                or "—"
            ),
            "Autor principal": principal,
            "Coautores": coautores,
            "PDF disponible": (
                "Sí"
                if _has_any_pdf(
                    publicacion
                )
                else "No"
            ),
            "Archivos PDF": (
                _pdf_text(
                    publicacion
                )
            ),
        }
    )

    return row


def _row_libro(
    publicacion,
):
    principal, coautores = (
        _autor_data(
            publicacion
        )
    )

    libro = publicacion.libro

    row = _base_common(
        publicacion
    )

    row.update(
        {
            "Nombre del libro": (
                libro.nombre_libro
            ),
            "Fecha publicación": (
                _fecha_text(
                    publicacion
                )
            ),
            "ISBN": libro.codigo_isbn,
            "Editorial / Compilador": (
                libro.editorial_compilador
            ),
            "Revisor / arbitraje": (
                _display_choice(
                    libro,
                    "get_revisor_par_arbitraje_display",
                )
            ),
            "Link libro": (
                libro.link_libro
            ),
            "Autor principal": principal,
            "Coautores": coautores,
            "Archivos PDF": (
                _pdf_text(
                    publicacion
                )
            ),
        }
    )

    return row


def _row_capitulo(
    publicacion,
):
    principal, coautores = (
        _autor_data(
            publicacion
        )
    )

    capitulo = (
        publicacion.capitulo_libro
    )

    row = _base_common(
        publicacion
    )

    row.update(
        {
            "Nombre del capítulo": (
                capitulo.nombre_capitulo
            ),
            "Nombre del libro": (
                capitulo.nombre_libro
            ),
            "Fecha publicación": (
                _fecha_text(
                    publicacion
                )
            ),
            "ISBN": (
                capitulo.codigo_isbn
            ),
            "Editor / compilador": (
                capitulo.editor_compilador
            ),
            "Revisor / arbitraje": (
                _display_choice(
                    capitulo,
                    "get_revisor_par_arbitraje_display",
                )
            ),
            "Link capítulo": (
                capitulo.link_capitulo
            ),
            "Autor principal": principal,
            "Coautores": coautores,
            "Archivos PDF": (
                _pdf_text(
                    publicacion
                )
            ),
        }
    )

    return row


ROW_BUILDERS = {
    "alto_impacto": (
        _row_alto_impacto
    ),
    "regional": (
        _row_regional
    ),
    "ponencia": (
        _row_ponencia
    ),
    "libro": (
        _row_libro
    ),
    "capitulo": (
        _row_capitulo
    ),
}


def _apply_title_block(
    ws,
    title,
    subtitle,
    note,
    total_columns,
):
    end_col = get_column_letter(
        max(total_columns, 1)
    )

    ws.merge_cells(
        f"A1:{end_col}1"
    )

    title_cell = ws["A1"]
    title_cell.value = title

    title_cell.font = Font(
        size=24,
        bold=True,
        color=TITLE_TEXT,
    )

    title_cell.alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    title_cell.fill = PatternFill(
        "solid",
        fgColor=TITLE_BG,
    )

    ws.merge_cells(
        f"A2:{end_col}2"
    )

    subtitle_cell = ws["A2"]
    subtitle_cell.value = subtitle

    subtitle_cell.font = Font(
        size=16,
        bold=True,
        color=TITLE_TEXT,
    )

    subtitle_cell.alignment = (
        Alignment(
            horizontal="center",
            vertical="center",
        )
    )

    subtitle_cell.fill = (
        PatternFill(
            "solid",
            fgColor=TITLE_BG,
        )
    )

    ws.merge_cells(
        f"A3:{end_col}3"
    )

    note_cell = ws["A3"]
    note_cell.value = note

    note_cell.font = Font(
        size=11,
        color="FFFFFF",
    )

    note_cell.alignment = Alignment(
        horizontal="center",
        vertical="center",
        wrap_text=True,
    )

    note_cell.fill = PatternFill(
        "solid",
        fgColor=NAVY_2,
    )

    ws.row_dimensions[1].height = 36
    ws.row_dimensions[2].height = 26
    ws.row_dimensions[3].height = 34


def _style_sheet(
    ws,
    *,
    total_columns,
    total_rows,
):
    thin = Side(
        style="thin",
        color=BORDER,
    )

    for cell in ws[4]:
        cell.fill = PatternFill(
            "solid",
            fgColor=HEADER_BG,
        )

        cell.font = Font(
            bold=True,
            color=HEADER_TEXT,
            size=11,
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )

        cell.border = Border(
            left=thin,
            right=thin,
            top=thin,
            bottom=thin,
        )

    ws.row_dimensions[4].height = 36

    for row_idx in range(
        5,
        total_rows + 1,
    ):
        fill_color = (
            BODY_BG
            if row_idx % 2 == 1
            else BODY_BG_ALT
        )

        for col_idx in range(
            1,
            total_columns + 1,
        ):
            cell = ws.cell(
                row=row_idx,
                column=col_idx,
            )

            cell.border = Border(
                left=thin,
                right=thin,
                top=thin,
                bottom=thin,
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

            if col_idx == 1:
                cell.fill = PatternFill(
                    "solid",
                    fgColor=NUM_BG,
                )

                cell.font = Font(
                    bold=True,
                    color=TITLE_TEXT,
                    size=11,
                )

            else:
                cell.fill = PatternFill(
                    "solid",
                    fgColor=fill_color,
                )

                cell.font = Font(
                    color=TITLE_TEXT,
                    size=11,
                )

        ws.row_dimensions[
            row_idx
        ].height = 34

    ws.freeze_panes = "A5"

    if total_columns:
        ws.auto_filter.ref = (
            f"A4:"
            f"{get_column_letter(total_columns)}"
            f"{total_rows}"
        )


def _autosize_columns(ws):
    for column_index in range(
        1,
        ws.max_column + 1,
    ):
        max_length = 0

        for row_index in range(
            4,
            ws.max_row + 1,
        ):
            value = ws.cell(
                row=row_index,
                column=column_index,
            ).value

            if value is None:
                continue

            text = str(value)

            max_length = max(
                max_length,
                min(
                    len(text),
                    50,
                ),
            )

        width = min(
            max(
                max_length + 3,
                12,
            ),
            45,
        )

        ws.column_dimensions[
            get_column_letter(
                column_index
            )
        ].width = width


def build_publicaciones_excel(
    filters=None,
):
    publicaciones = (
        _build_queryset(
            filters or {}
        )
    )

    grouped = {
        key: []
        for key in TIPO_ORDER
    }

    for publicacion in publicaciones:
        bucket = _tipo_bucket(
            publicacion
        )

        if bucket in grouped:
            grouped[bucket].append(
                publicacion
            )

    workbook = Workbook()

    default_sheet = (
        workbook.active
    )

    workbook.remove(
        default_sheet
    )

    included = [
        key
        for key in TIPO_ORDER
        if grouped.get(key)
    ]

    # ---------------------------------------------------------
    # Sin resultados
    # ---------------------------------------------------------

    if not included:
        ws = workbook.create_sheet(
            "Sin resultados"
        )

        ws["A1"] = (
            "Reporte de publicaciones"
        )

        ws["A2"] = (
            "No existen registros para "
            "los filtros seleccionados."
        )

        ws["A1"].font = Font(
            size=16,
            bold=True,
        )

        ws["A2"].font = Font(
            size=12
        )

        ws.column_dimensions[
            "A"
        ].width = 60

        return workbook

    # ---------------------------------------------------------
    # Hojas por tipo
    # ---------------------------------------------------------

    for bucket in included:
        ws = workbook.create_sheet(
            TIPO_SHEET_NAMES[
                bucket
            ][:31]
        )

        rows = [
            ROW_BUILDERS[
                bucket
            ](
                publicacion
            )
            for publicacion
            in grouped[bucket]
        ]

        if not rows:
            continue

        headers = list(
            rows[0].keys()
        )

        _apply_title_block(
            ws,
            TIPO_SHEET_NAMES[
                bucket
            ],
            "Dirección de Investigación",
            NOTE_MAP.get(
                bucket,
                (
                    "Reporte de "
                    "publicaciones científicas."
                ),
            ),
            len(headers),
        )

        # -----------------------------------------------------
        # Cabeceras
        # -----------------------------------------------------

        for column_index, header in enumerate(
            headers,
            start=1,
        ):
            ws.cell(
                row=4,
                column=column_index,
                value=header,
            )

        # -----------------------------------------------------
        # Datos
        # -----------------------------------------------------

        for row_index, row in enumerate(
            rows,
            start=5,
        ):
            for column_index, value in enumerate(
                row.values(),
                start=1,
            ):
                ws.cell(
                    row=row_index,
                    column=column_index,
                    value=value,
                )

        _style_sheet(
            ws,
            total_columns=len(
                headers
            ),
            total_rows=ws.max_row,
        )

        _autosize_columns(
            ws
        )

    return workbook


def workbook_to_bytes(
    workbook,
):
    output = BytesIO()

    workbook.save(
        output
    )

    output.seek(0)

    return output.getvalue()