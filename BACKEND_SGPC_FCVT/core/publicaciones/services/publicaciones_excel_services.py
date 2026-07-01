"""
Servicio para construir el Excel de publicaciones agrupado por tipo.
Genera una o varias hojas según los filtros aplicados.
"""

from collections import OrderedDict
from io import BytesIO

from django.db.models import Prefetch, Q
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from core.models import Publicacion, PublicacionAutor


TIPO_ORDER = [
    "alto_impacto",
    "regional",
    "ponencia",
    "libro",
    "capitulo",
]

TIPO_SHEET_NAMES = {
    "alto_impacto": "Matriz de artículos de alto impacto",
    "regional": "Matriz de artículos regionales",
    "ponencia": "Matriz de ponencias",
    "libro": "Matriz de libros",
    "capitulo": "Matriz de capítulos de libro",
}

NOTE_MAP = {
    "alto_impacto": (
        "Esta versión toma como base los campos reales del formulario: "
        "origen, datos generales, revista, impacto, cuartil, autores y adjuntos."
    ),
    "regional": (
        "Ajustada al formulario real: origen, datos generales, base de indexación "
        "regional, revista, enlaces, autores y adjuntos."
    ),
    "ponencia": (
        "Ajustada al formulario de ponencias: datos generales, evento, ubicación, "
        "tipo de presentación, autores y PDF opcional."
    ),
    "libro": (
        "Aterrizada al formulario de libro: información editorial, arbitraje, "
        "enlace, autores y PDF obligatorio."
    ),
    "capitulo": (
        "Aterrizada al formulario real: datos del capítulo, libro contenedor, "
        "arbitraje, enlace, autores y adjuntos PDF."
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
    return str(value or "").strip()


def _normalize_lower(value):
    value = _normalize_text(value)
    return value.lower() if value else ""


def _parse_year(value):
    raw = _normalize_text(value)
    if raw.isdigit() and len(raw) == 4:
        return int(raw)
    return None


def _safe_related(instance, attr_name):
    try:
        return getattr(instance, attr_name)
    except Exception:
        return None


def _tipo_bucket(pub):
    articulo = _safe_related(pub, "articulo")
    if articulo:
        return (
            "alto_impacto"
            if getattr(articulo, "tipo_articulo", None) == "alto_impacto"
            else "regional"
        )

    if _safe_related(pub, "ponencia"):
        return "ponencia"

    if _safe_related(pub, "libro"):
        return "libro"

    if _safe_related(pub, "capitulo_libro"):
        return "capitulo"

    return None


def _resolve_tipo_filter(raw_tipo):
    value = _normalize_text(raw_tipo).lower()

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
        "capitulos": "capitulo",
        "capitulo_libro": "capitulo",
        "cap": "capitulo",
    }

    return alias_map.get(value)


def _build_queryset(filters):
    filters = filters or {}

    tipo = _resolve_tipo_filter(filters.get("tipo"))
    anio = _parse_year(filters.get("anio"))
    anio_desde = _parse_year(filters.get("anio_desde"))
    anio_hasta = _parse_year(filters.get("anio_hasta"))
    texto = _normalize_text(filters.get("texto"))
    facultad_id = _normalize_text(filters.get("facultad"))
    carrera_id = _normalize_text(filters.get("carrera"))
    proyecto_id = _normalize_text(filters.get("proyecto"))

    if anio_desde and anio_hasta and anio_desde > anio_hasta:
        anio_desde, anio_hasta = anio_hasta, anio_desde

    qs = (
        Publicacion.objects.select_related(
            "tipo",
            "proyecto",
            "facultad",
            "carrera",
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
                queryset=PublicacionAutor.objects.select_related("autor").order_by("orden"),
                to_attr="participaciones_ordenadas",
            ),
            "archivos",
        )
        .all()
    )

    if anio:
        qs = qs.filter(anio_publicacion=anio)
    else:
        if anio_desde:
            qs = qs.filter(anio_publicacion__gte=anio_desde)
        if anio_hasta:
            qs = qs.filter(anio_publicacion__lte=anio_hasta)

    if facultad_id.isdigit():
        qs = qs.filter(facultad_id=int(facultad_id))

    if carrera_id.isdigit():
        qs = qs.filter(carrera_id=int(carrera_id))

    if proyecto_id.isdigit():
        qs = qs.filter(proyecto_id=int(proyecto_id))

    if texto:
        qs = qs.filter(
            Q(facultad__nombre__icontains=texto)
            | Q(carrera__nombre__icontains=texto)
            | Q(proyecto__nombre__icontains=texto)
            | Q(area__nombre__icontains=texto)
            | Q(subarea__nombre__icontains=texto)
            | Q(origen_tipo__icontains=texto)
            | Q(origen_grado__icontains=texto)
            | Q(articulo__nombre_articulo__icontains=texto)
            | Q(articulo__nombre_revista__icontains=texto)
            | Q(articulo__codigo_doi__icontains=texto)
            | Q(articulo__codigo_issn__icontains=texto)
            | Q(articulo__base_datos_indexada__icontains=texto)
            | Q(articulo__base_datos_otra__icontains=texto)
            | Q(ponencia__nombre_evento__icontains=texto)
            | Q(ponencia__nombre_ponencia__icontains=texto)
            | Q(libro__nombre_libro__icontains=texto)
            | Q(libro__editorial_compilador__icontains=texto)
            | Q(capitulo_libro__nombre_capitulo__icontains=texto)
            | Q(capitulo_libro__nombre_libro__icontains=texto)
            | Q(participaciones__autor__nombres__icontains=texto)
            | Q(participaciones__autor__apellidos__icontains=texto)
            | Q(participaciones__autor__identificacion__icontains=texto)
        ).distinct()

    publicaciones = list(qs.order_by("-fecha_publicacion", "-id"))

    if tipo:
        publicaciones = [pub for pub in publicaciones if _tipo_bucket(pub) == tipo]

    return publicaciones


def _get_participaciones(pub):
    return getattr(pub, "participaciones_ordenadas", []) or []


def _get_archivos(pub):
    try:
        cache = getattr(pub, "_prefetched_objects_cache", {})
        if "archivos" in cache:
            return list(cache["archivos"])
    except Exception:
        pass

    try:
        return list(pub.archivos.all())
    except Exception:
        return []


def _autor_data(pub):
    parts = _get_participaciones(pub)
    principal = ""
    coautores = []

    for part in parts:
        nombre = (
            f"{_normalize_text(part.autor.nombres)} "
            f"{_normalize_text(part.autor.apellidos)}"
        ).strip()

        if not nombre:
            nombre = (
                _normalize_text(part.autor.correo)
                or _normalize_text(part.autor.identificacion)
            )

        if part.orden == 1 or part.rol_autoria == "principal":
            principal = nombre
        else:
            if nombre:
                coautores.append(nombre)

    if not principal and parts:
        first = parts[0]
        principal = (
            f"{_normalize_text(first.autor.nombres)} "
            f"{_normalize_text(first.autor.apellidos)}"
        ).strip() or "—"

    return principal or "—", " | ".join(coautores) or "—"


def _adjuntos_text(pub):
    archivos = _get_archivos(pub)
    if not archivos:
        return "—"

    nombres = [archivo.nombre for archivo in archivos if _normalize_text(archivo.nombre)]
    if nombres:
        return " | ".join(nombres)

    return f"{len(archivos)} PDF"


def _legacy_pdf_text(pub):
    archivo = getattr(pub, "archivo_pdf", None)
    if not archivo:
        return "—"

    name = _normalize_text(getattr(archivo, "name", ""))
    return name or "PDF"


def _has_any_pdf(pub):
    archivos = _get_archivos(pub)
    if archivos:
        return True

    return bool(getattr(pub, "archivo_pdf", None))


def _display_choice(instance, method_name, fallback):
    try:
        method = getattr(instance, method_name, None)
        if callable(method):
            value = method()
            return _normalize_text(value) or fallback
    except Exception:
        pass

    return fallback


def _display_cuartil(articulo):
    value = _normalize_lower(getattr(articulo, "cuartil", None))

    if value == "sin_cuartil":
        return "Sin cuartil"

    if not value:
        return "—"

    return _display_choice(
        articulo,
        "get_cuartil_display",
        value.upper(),
    )


def _display_factor_impacto(articulo):
    value = _normalize_lower(getattr(articulo, "factor_impacto", None))
    if not value:
        return "—"

    return _display_choice(
        articulo,
        "get_factor_impacto_display",
        value.upper(),
    )


def _display_base_indexada(articulo):
    value = _normalize_lower(getattr(articulo, "base_datos_indexada", None))
    if not value:
        return "—"

    return _display_choice(
        articulo,
        "get_base_datos_indexada_display",
        value,
    )


def _base_common(pub):
    return OrderedDict(
        {
            "N°": pub.numero or pub.id,
            "Facultad": _normalize_text(getattr(pub.facultad, "nombre", "")) or "—",
            "Carrera": _normalize_text(getattr(pub.carrera, "nombre", "")) or "—",
            "Proyecto": _normalize_text(getattr(pub.proyecto, "nombre", "")) or "—",
            "Área": _normalize_text(getattr(pub.area, "nombre", "")) or "—",
            "Subárea": _normalize_text(getattr(pub.subarea, "nombre", "")) or "—",
        }
    )


def _row_alto_impacto(pub):
    principal, coautores = _autor_data(pub)
    art = pub.articulo

    row = _base_common(pub)
    row.update(
        {
            "Origen publicación": pub.get_origen_tipo_display() if pub.origen_tipo else "—",
            "Grado / programa": _normalize_text(pub.origen_grado) or "—",
            "Título del artículo": _normalize_text(art.nombre_articulo) or "—",
            "Fecha publicación": pub.fecha_publicacion.isoformat() if pub.fecha_publicacion else "—",
            "Nombre revista": _normalize_text(art.nombre_revista) or "—",
            "N° revista": art.numero_revista if art.numero_revista is not None else "—",
            "ISSN": _normalize_text(art.codigo_issn) or "—",
            "DOI": _normalize_text(art.codigo_doi) or "—",
            "Factor impacto": _display_factor_impacto(art),
            "Cuartil": _display_cuartil(art),
            "SJR": _normalize_text(art.sjr) or "—",
            "Link revista": _normalize_text(art.link_revista) or "—",
            "Link publicación": _normalize_text(art.link_publicacion) or "—",
            "Autor principal": principal,
            "Coautores": coautores,
            "Adjuntos PDF": _adjuntos_text(pub),
        }
    )
    return row


def _row_regional(pub):
    principal, coautores = _autor_data(pub)
    art = pub.articulo

    row = _base_common(pub)
    row.update(
        {
            "Origen publicación": pub.get_origen_tipo_display() if pub.origen_tipo else "—",
            "Grado / programa": _normalize_text(pub.origen_grado) or "—",
            "Título del artículo": _normalize_text(art.nombre_articulo) or "—",
            "Fecha publicación": pub.fecha_publicacion.isoformat() if pub.fecha_publicacion else "—",
            "Base indexada": _display_base_indexada(art),
            "Otra base": (
                _normalize_text(art.base_datos_otra)
                if _normalize_lower(art.base_datos_indexada) == "otra"
                else "—"
            ) or "—",
            "Nombre revista": _normalize_text(art.nombre_revista) or "—",
            "N° revista": art.numero_revista if art.numero_revista is not None else "—",
            "ISSN": _normalize_text(art.codigo_issn) or "—",
            "DOI": _normalize_text(art.codigo_doi) or "—",
            "Link revista": _normalize_text(art.link_revista) or "—",
            "Link publicación": _normalize_text(art.link_publicacion) or "—",
            "Autor principal": principal,
            "Coautores": coautores,
            "Adjuntos PDF": _adjuntos_text(pub),
        }
    )
    return row


def _row_ponencia(pub):
    principal, coautores = _autor_data(pub)
    pon = pub.ponencia
    archivos = _get_archivos(pub)

    row = _base_common(pub)
    row.update(
        {
            "Nombre del evento": _normalize_text(pon.nombre_evento) or "—",
            "Link evento": _normalize_text(pon.link_evento) or "—",
            "País": _normalize_text(getattr(pub.pais, "nombre", "")) or "—",
            "Ciudad": _normalize_text(getattr(pub.ciudad, "nombre", "")) or "—",
            "Nombre ponencia": _normalize_text(pon.nombre_ponencia) or "—",
            "Tipo presentación": pon.get_tipo_presentacion_display() if pon.tipo_presentacion else "—",
            "Fecha presentación": pub.fecha_publicacion.isoformat() if pub.fecha_publicacion else "—",
            "ISSN / ISBN": _normalize_text(pon.codigo_issn_isbn) or "—",
            "Autor principal": principal,
            "Coautores": coautores,
            "PDF adjunto": "Sí" if _has_any_pdf(pub) else "No",
            "Archivo PDF": _adjuntos_text(pub) if archivos else _legacy_pdf_text(pub),
        }
    )
    return row


def _row_libro(pub):
    principal, coautores = _autor_data(pub)
    libro = pub.libro
    archivos = _get_archivos(pub)

    row = _base_common(pub)
    row.update(
        {
            "Nombre del libro": _normalize_text(libro.nombre_libro) or "—",
            "ISBN": _normalize_text(libro.codigo_isbn) or "—",
            "Fecha publicación": pub.fecha_publicacion.isoformat() if pub.fecha_publicacion else "—",
            "Editorial / Compilador": _normalize_text(libro.editorial_compilador) or "—",
            "Revisor / arbitraje": libro.get_revisor_par_arbitraje_display() if libro.revisor_par_arbitraje else "—",
            "Link libro": _normalize_text(libro.link_libro) or "—",
            "Autor principal": principal,
            "Coautores": coautores,
            "PDF libro": _adjuntos_text(pub) if archivos else _legacy_pdf_text(pub),
        }
    )
    return row


def _row_capitulo(pub):
    principal, coautores = _autor_data(pub)
    cap = pub.capitulo_libro

    row = _base_common(pub)
    row.update(
        {
            "Nombre del capítulo": _normalize_text(cap.nombre_capitulo) or "—",
            "Nombre del libro": _normalize_text(cap.nombre_libro) or "—",
            "Fecha publicación": pub.fecha_publicacion.isoformat() if pub.fecha_publicacion else "—",
            "ISBN": _normalize_text(cap.codigo_isbn) or "—",
            "Editor / compilador": _normalize_text(cap.editor_compilador) or "—",
            "Revisor / arbitraje": cap.get_revisor_par_arbitraje_display() if cap.revisor_par_arbitraje else "—",
            "Link capítulo": _normalize_text(cap.link_capitulo) or "—",
            "Autor principal": principal,
            "Coautores": coautores,
            "Adjuntos PDF": _adjuntos_text(pub),
        }
    )
    return row


ROW_BUILDERS = {
    "alto_impacto": _row_alto_impacto,
    "regional": _row_regional,
    "ponencia": _row_ponencia,
    "libro": _row_libro,
    "capitulo": _row_capitulo,
}


def _apply_title_block(ws, title, subtitle, note, total_columns):
    end_col = get_column_letter(total_columns)

    ws.merge_cells(f"A1:{end_col}1")
    c1 = ws["A1"]
    c1.value = title
    c1.font = Font(size=30, bold=True, color=TITLE_TEXT)
    c1.alignment = Alignment(horizontal="center", vertical="center")
    c1.fill = PatternFill("solid", fgColor=TITLE_BG)

    ws.merge_cells(f"A2:{end_col}2")
    c2 = ws["A2"]
    c2.value = subtitle
    c2.font = Font(size=18, bold=True, color=TITLE_TEXT)
    c2.alignment = Alignment(horizontal="center", vertical="center")
    c2.fill = PatternFill("solid", fgColor=TITLE_BG)

    ws.merge_cells(f"A3:{end_col}3")
    c3 = ws["A3"]
    c3.value = note
    c3.font = Font(size=12, bold=False, color="FFFFFF")
    c3.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c3.fill = PatternFill("solid", fgColor=NAVY_2)

    ws.row_dimensions[1].height = 42
    ws.row_dimensions[2].height = 28
    ws.row_dimensions[3].height = 34


def _style_sheet(ws, total_columns, total_rows):
    thin = Side(style="thin", color=BORDER)

    for cell in ws[4]:
        cell.fill = PatternFill("solid", fgColor=HEADER_BG)
        cell.font = Font(bold=True, color=HEADER_TEXT, size=11)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws.row_dimensions[4].height = 36

    for row_idx in range(5, total_rows + 1):
        fill_color = BODY_BG if row_idx % 2 == 1 else BODY_BG_ALT

        for col_idx in range(1, total_columns + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            if col_idx == 1:
                cell.fill = PatternFill("solid", fgColor=NUM_BG)
                cell.font = Font(bold=True, color=TITLE_TEXT, size=11)
            else:
                cell.fill = PatternFill("solid", fgColor=fill_color)
                cell.font = Font(color=TITLE_TEXT, size=11)

        ws.row_dimensions[row_idx].height = 34

    ws.freeze_panes = "A5"


def _autosize_columns(ws):
    manual_widths = {
        1: 7,
        2: 18,
        3: 18,
        4: 18,
        5: 18,
        6: 18,
        7: 22,
        8: 22,
        9: 34,
        10: 16,
        11: 22,
        12: 16,
        13: 18,
        14: 18,
        15: 16,
        16: 16,
        17: 16,
        18: 18,
        19: 18,
        20: 20,
        21: 24,
        22: 20,
        23: 20,
        24: 18,
        25: 18,
    }

    max_col = ws.max_column
    for idx in range(1, max_col + 1):
        ws.column_dimensions[get_column_letter(idx)].width = manual_widths.get(idx, 18)


def build_publicaciones_excel(filters=None):
    publicaciones = _build_queryset(filters or {})

    grouped = {key: [] for key in TIPO_ORDER}

    for pub in publicaciones:
        bucket = _tipo_bucket(pub)
        if bucket in grouped:
            grouped[bucket].append(pub)

    wb = Workbook()
    default_ws = wb.active
    wb.remove(default_ws)

    included = [key for key in TIPO_ORDER if grouped.get(key)]

    if not included:
        ws = wb.create_sheet("Sin resultados")
        ws["A1"] = "Reporte de publicaciones"
        ws["A2"] = "No existen registros para los filtros seleccionados."
        ws["A1"].font = Font(size=16, bold=True)
        ws["A2"].font = Font(size=12)
        return wb

    for bucket in included:
        ws = wb.create_sheet(TIPO_SHEET_NAMES[bucket][:31])

        rows = [ROW_BUILDERS[bucket](pub) for pub in grouped[bucket]]
        headers = list(rows[0].keys()) if rows else []

        title = TIPO_SHEET_NAMES[bucket]
        subtitle = "Dirección de Investigación"
        note = NOTE_MAP.get(bucket, "Reporte de publicaciones científicas.")

        _apply_title_block(ws, title, subtitle, note, len(headers))

        for col_idx, header in enumerate(headers, start=1):
            ws.cell(row=4, column=col_idx, value=header)

        for row_idx, row in enumerate(rows, start=5):
            values = list(row.values())
            for col_idx, value in enumerate(values, start=1):
                ws.cell(row=row_idx, column=col_idx, value=value)

        _style_sheet(ws, total_columns=len(headers), total_rows=ws.max_row)
        _autosize_columns(ws)

    return wb


def workbook_to_bytes(workbook):
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output.getvalue()