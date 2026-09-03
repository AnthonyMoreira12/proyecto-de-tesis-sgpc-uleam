"""Generación PDF para el catálogo institucional de publicaciones.

El PDF utiliza exactamente el mismo queryset centralizado que la exportación
Excel. Por tanto, búsqueda, filtros académicos, período, tipo, origen, PDF y
ordenamiento producen el mismo conjunto de publicaciones en ambos formatos.

Regla institucional: el catálogo general expone únicamente publicaciones que
han terminado el flujo administrativo como aprobadas, porque el queryset base
se construye mediante ``build_publicaciones_queryset(..., solo_mias=False)``.
"""

from __future__ import annotations

from collections import Counter
from io import BytesIO

from django.utils import timezone

from core.models import Carrera, Facultad, Proyecto, Sede
from core.publicaciones.services.publicaciones_excel_services import (
    _autores_text,
    _build_queryset,
    _facultad_from_publicacion,
    _has_any_pdf,
    _normalize_text,
    _origen_publicacion_data,
    _periodo_text,
    _safe_related,
    _tipo_bucket,
)

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import HorizontalBarChart
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.platypus import (
        KeepTogether,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except ImportError:  # pragma: no cover - depende del entorno de despliegue.
    colors = None


# ============================================================
# PALETA INSTITUCIONAL
# ============================================================

PRIMARY = "#1F4FD7"
PRIMARY_DARK = "#153A9B"
TEXT = "#172033"
MUTED = "#667085"
LINE = "#D9E0E8"
SOFT = "#F5F7FB"
WHITE = "#FFFFFF"
SUCCESS = "#17803D"
WARNING = "#A15C06"


TIPO_LABELS = {
    "alto_impacto": "Artículo de alto impacto",
    "regional": "Artículo regional",
    "ponencia": "Ponencia",
    "libro": "Libro",
    "capitulo": "Capítulo de libro",
}

ORIGEN_LABELS = {
    "ninguno": "Ninguno",
    "tic": "Trabajo de integración curricular",
    "maestria": "Tesis de maestría",
    "doctoral": "Tesis doctoral",
    "otro": "Otro",
}

ORDEN_LABELS = {
    "recientes": "Más recientes",
    "antiguas": "Más antiguas",
    "titulo_asc": "Título A-Z",
    "titulo_desc": "Título Z-A",
}

MESES = {
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


# ============================================================
# UTILIDADES GENERALES
# ============================================================


def _require_reportlab():
    if colors is None:
        raise RuntimeError("PDF_ENGINE_UNAVAILABLE")


def _safe(value, fallback="—"):
    text = str(value or "").strip()
    return text or fallback


def _escape(value):
    return (
        _safe(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def _p(value, style):
    return Paragraph(_escape(value), style)


def _object_name(model, value, fallback):
    if not value:
        return fallback

    try:
        return (
            model.objects
            .filter(pk=value)
            .values_list("nombre", flat=True)
            .first()
            or fallback
        )
    except Exception:
        return fallback


def _bool_filter(value):
    return str(value or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "si",
        "sí",
        "on",
    }


# ============================================================
# ESTILOS
# ============================================================


def _styles():
    sample = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "PublicacionesPdfTitle",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=22,
            textColor=colors.HexColor(TEXT),
            alignment=TA_LEFT,
            spaceAfter=2 * mm,
        ),
        "subtitle": ParagraphStyle(
            "PublicacionesPdfSubtitle",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor(MUTED),
            spaceAfter=2 * mm,
        ),
        "section": ParagraphStyle(
            "PublicacionesPdfSection",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.8,
            leading=14,
            textColor=colors.HexColor(TEXT),
            spaceBefore=1 * mm,
            spaceAfter=2.5 * mm,
        ),
        "body": ParagraphStyle(
            "PublicacionesPdfBody",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11.2,
            textColor=colors.HexColor(TEXT),
        ),
        "body_bold": ParagraphStyle(
            "PublicacionesPdfBodyBold",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11.2,
            textColor=colors.HexColor(TEXT),
        ),
        "muted": ParagraphStyle(
            "PublicacionesPdfMuted",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=10.2,
            textColor=colors.HexColor(MUTED),
        ),
        "label": ParagraphStyle(
            "PublicacionesPdfLabel",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=9,
            textColor=colors.HexColor(MUTED),
        ),
        "record_title": ParagraphStyle(
            "PublicacionesPdfRecordTitle",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.2,
            leading=13.2,
            textColor=colors.HexColor(TEXT),
            spaceAfter=1.5 * mm,
        ),
        "badge": ParagraphStyle(
            "PublicacionesPdfBadge",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=colors.HexColor(PRIMARY_DARK),
        ),
        "summary_value": ParagraphStyle(
            "PublicacionesPdfSummaryValue",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=17,
            textColor=colors.HexColor(PRIMARY),
        ),
    }


# ============================================================
# ENCABEZADO Y PIE
# ============================================================


def _header_footer(canvas, document):
    canvas.saveState()
    width, _height = A4

    canvas.setFillColor(colors.HexColor(PRIMARY_DARK))
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(
        15 * mm,
        286 * mm,
        "SGPC ULEAM · Producción científica",
    )

    canvas.setStrokeColor(colors.HexColor(LINE))
    canvas.setLineWidth(0.45)
    canvas.line(15 * mm, 13 * mm, width - 15 * mm, 13 * mm)

    canvas.setFillColor(colors.HexColor(MUTED))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(
        15 * mm,
        8.5 * mm,
        "Catálogo institucional de publicaciones aprobadas",
    )
    canvas.drawRightString(
        width - 15 * mm,
        8.5 * mm,
        f"Página {document.page}",
    )

    canvas.restoreState()


# ============================================================
# FILTROS
# ============================================================


def _filter_summary(filters):
    filters = dict(filters or {})

    values = []

    tipo = str(filters.get("tipo") or "").strip()
    if tipo:
        values.append(("Tipo", TIPO_LABELS.get(tipo, tipo)))

    origen = str(filters.get("origen_tipo") or "").strip()
    if origen:
        values.append(("Origen", ORIGEN_LABELS.get(origen, origen)))

    sede = filters.get("sede") or filters.get("sede_id")
    if sede:
        values.append(("Sede", _object_name(Sede, sede, f"Sede {sede}")))

    facultad = filters.get("facultad") or filters.get("facultad_id")
    if facultad:
        values.append(
            (
                "Facultad",
                _object_name(Facultad, facultad, f"Facultad {facultad}"),
            )
        )

    carrera = filters.get("carrera") or filters.get("carrera_id")
    if carrera:
        values.append(
            (
                "Carrera",
                _object_name(Carrera, carrera, f"Carrera {carrera}"),
            )
        )

    proyecto = filters.get("proyecto") or filters.get("proyecto_id")
    if proyecto:
        values.append(
            (
                "Proyecto",
                _object_name(Proyecto, proyecto, f"Proyecto {proyecto}"),
            )
        )

    anio = filters.get("anio")
    mes = filters.get("mes")
    anio_desde = filters.get("anio_desde")
    anio_hasta = filters.get("anio_hasta")

    if anio:
        periodo = str(anio)
        if mes:
            try:
                mes_label = MESES.get(int(mes), str(mes))
            except (TypeError, ValueError):
                mes_label = str(mes)
            periodo = f"{mes_label} de {anio}"
        values.append(("Período", periodo))
    elif anio_desde or anio_hasta:
        values.append(
            (
                "Período",
                f"{anio_desde or 'Sin mínimo'} – {anio_hasta or 'Sin máximo'}",
            )
        )
    elif mes:
        try:
            mes_label = MESES.get(int(mes), str(mes))
        except (TypeError, ValueError):
            mes_label = str(mes)
        values.append(("Mes", mes_label))

    texto = str(filters.get("texto") or "").strip()
    if texto:
        values.append(("Búsqueda", texto))

    if _bool_filter(filters.get("solo_con_pdf")):
        values.append(("Disponibilidad", "Solo publicaciones con PDF"))

    orden = str(filters.get("orden") or "").strip()
    if orden:
        values.append(("Orden", ORDEN_LABELS.get(orden, orden)))

    return values


def _filters_table(filters, styles):
    applied = _filter_summary(filters)

    if not applied:
        return Table(
            [[_p("Sin filtros adicionales · se incluye todo el catálogo aprobado.", styles["muted"])]],
            colWidths=[180 * mm],
            hAlign="LEFT",
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(SOFT)),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(LINE)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        )

    rows = []
    for index in range(0, len(applied), 2):
        row = []
        for label, value in applied[index:index + 2]:
            row.append(
                [
                    _p(label.upper(), styles["label"]),
                    _p(value, styles["body_bold"]),
                ]
            )
        while len(row) < 2:
            row.append([])
        rows.append(row)

    table = Table(rows, colWidths=[90 * mm, 90 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(SOFT)),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(LINE)),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


# ============================================================
# DATOS DE CADA PUBLICACIÓN
# ============================================================


def _publication_title(publicacion):
    bucket = _tipo_bucket(publicacion)

    if bucket in {"alto_impacto", "regional"}:
        articulo = _safe_related(publicacion, "articulo")
        return _safe(getattr(articulo, "nombre_articulo", None), "Sin título")

    if bucket == "ponencia":
        ponencia = _safe_related(publicacion, "ponencia")
        return _safe(getattr(ponencia, "nombre_ponencia", None), "Sin título")

    if bucket == "libro":
        libro = _safe_related(publicacion, "libro")
        return _safe(getattr(libro, "nombre_libro", None), "Sin título")

    if bucket == "capitulo":
        capitulo = _safe_related(publicacion, "capitulo_libro")
        return _safe(getattr(capitulo, "nombre_capitulo", None), "Sin título")

    return "Sin título"


def _publication_identifier(publicacion):
    bucket = _tipo_bucket(publicacion)

    if bucket in {"alto_impacto", "regional"}:
        articulo = _safe_related(publicacion, "articulo")
        doi = _normalize_text(getattr(articulo, "codigo_doi", None))
        issn = _normalize_text(getattr(articulo, "codigo_issn", None))
        if doi:
            return f"DOI: {doi}"
        if issn:
            return f"ISSN: {issn}"

    if bucket == "ponencia":
        ponencia = _safe_related(publicacion, "ponencia")
        code = _normalize_text(getattr(ponencia, "codigo_issn_isbn", None))
        if code:
            return f"ISSN / ISBN: {code}"

    if bucket == "libro":
        libro = _safe_related(publicacion, "libro")
        code = _normalize_text(getattr(libro, "codigo_isbn", None))
        if code:
            return f"ISBN: {code}"

    if bucket == "capitulo":
        capitulo = _safe_related(publicacion, "capitulo_libro")
        code = _normalize_text(getattr(capitulo, "codigo_isbn", None))
        if code:
            return f"ISBN: {code}"

    return ""


def _publication_context(publicacion):
    bucket = _tipo_bucket(publicacion)

    if bucket in {"alto_impacto", "regional"}:
        articulo = _safe_related(publicacion, "articulo")
        return _normalize_text(getattr(articulo, "nombre_revista", None))

    if bucket == "ponencia":
        ponencia = _safe_related(publicacion, "ponencia")
        return _normalize_text(getattr(ponencia, "nombre_evento", None))

    if bucket == "libro":
        libro = _safe_related(publicacion, "libro")
        return _normalize_text(getattr(libro, "editorial_compilador", None))

    if bucket == "capitulo":
        capitulo = _safe_related(publicacion, "capitulo_libro")
        return _normalize_text(getattr(capitulo, "nombre_libro", None))

    return ""


def _publication_academic(publicacion):
    sede = _safe_related(publicacion, "sede")
    carrera = _safe_related(publicacion, "carrera")
    facultad = _facultad_from_publicacion(publicacion)

    sede_name = _normalize_text(getattr(sede, "nombre", None)) or "Sin sede"
    facultad_name = _normalize_text(getattr(facultad, "nombre", None)) or "Sin facultad"
    carrera_name = _normalize_text(getattr(carrera, "nombre", None)) or "Sin carrera"

    return sede_name, facultad_name, carrera_name


def _publication_project(publicacion):
    proyecto = _safe_related(publicacion, "proyecto")
    return _normalize_text(getattr(proyecto, "nombre", None))


def _publication_record(publicacion):
    bucket = _tipo_bucket(publicacion)
    origen_label, origen_detalle = _origen_publicacion_data(publicacion)
    sede, facultad, carrera = _publication_academic(publicacion)

    return {
        "numero": getattr(publicacion, "numero", None) or getattr(publicacion, "id", None),
        "tipo": TIPO_LABELS.get(bucket, "Publicación"),
        "titulo": _publication_title(publicacion),
        "autores": _autores_text(publicacion),
        "periodo": _periodo_text(publicacion),
        "sede": sede,
        "facultad": facultad,
        "carrera": carrera,
        "proyecto": _publication_project(publicacion),
        "origen": origen_label,
        "origen_detalle": origen_detalle if origen_detalle != "—" else "",
        "identificador": _publication_identifier(publicacion),
        "contexto": _publication_context(publicacion),
        "con_pdf": _has_any_pdf(publicacion),
    }



# ============================================================
# RESUMEN GRÁFICO
# ============================================================


def _catalog_chart_data(publicaciones):
    type_counter = Counter()
    year_counter = Counter()
    site_counter = Counter()

    for publicacion in publicaciones:
        bucket = _tipo_bucket(publicacion)
        type_counter[TIPO_LABELS.get(bucket, "Publicación")] += 1

        year = getattr(publicacion, "anio_publicacion", None)
        if year:
            year_counter[str(year)] += 1

        sede, _facultad, _carrera = _publication_academic(publicacion)
        if sede:
            site_counter[sede] += 1

    type_rows = [
        {"label": label, "total": total}
        for label, total in type_counter.most_common()
    ]
    year_rows = [
        {"label": label, "total": year_counter[label]}
        for label in sorted(year_counter, key=lambda value: int(value))
    ]
    site_rows = [
        {"label": label, "total": total}
        for label, total in site_counter.most_common(8)
    ]
    return type_rows, year_rows, site_rows


def _catalog_line_chart(rows, title, width=248, height=150):
    drawing = Drawing(width, height)
    drawing.add(String(8, height - 14, title, fontName="Helvetica-Bold", fontSize=8.4, fillColor=colors.HexColor(TEXT)))
    values = [int(item.get("total") or 0) for item in rows]
    labels = [str(item.get("label") or "") for item in rows]
    if not values:
        drawing.add(String(10, 65, "Sin información", fontSize=7.2, fillColor=colors.HexColor(MUTED)))
        return drawing

    chart = HorizontalLineChart()
    chart.x = 34
    chart.y = 28
    chart.width = width - 48
    chart.height = height - 55
    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontSize = 5.8
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(1, max(values) + 1)
    chart.valueAxis.valueStep = max(1, round(chart.valueAxis.valueMax / 4))
    chart.valueAxis.labels.fontSize = 5.8
    chart.lines[0].strokeColor = colors.HexColor(PRIMARY)
    chart.lines[0].strokeWidth = 2
    drawing.add(chart)
    return drawing


def _catalog_donut_chart(rows, title, width=248, height=150):
    drawing = Drawing(width, height)
    drawing.add(String(8, height - 14, title, fontName="Helvetica-Bold", fontSize=8.4, fillColor=colors.HexColor(TEXT)))
    values = [int(item.get("total") or 0) for item in rows]
    labels = [str(item.get("label") or "") for item in rows]
    if not values or not sum(values):
        drawing.add(String(10, 65, "Sin información", fontSize=7.2, fillColor=colors.HexColor(MUTED)))
        return drawing

    palette = ["#2F66E8", "#2F855A", "#7554B8", "#B85F2E", "#237B72", "#8A5D1E"]
    pie = Pie()
    pie.x = 20
    pie.y = 20
    pie.width = 98
    pie.height = 98
    pie.data = values
    pie.labels = None
    pie.innerRadiusFraction = 0.58
    pie.slices.strokeColor = colors.HexColor(WHITE)
    pie.slices.strokeWidth = 0.7
    for index in range(len(values)):
        pie.slices[index].fillColor = colors.HexColor(palette[index % len(palette)])
    drawing.add(pie)

    total = sum(values)
    y = height - 38
    for index, (label, value) in enumerate(zip(labels[:6], values[:6])):
        short = label if len(label) <= 22 else label[:21] + "…"
        drawing.add(String(132, y, "●", fontSize=7.5, fillColor=colors.HexColor(palette[index % len(palette)])))
        drawing.add(String(144, y, short, fontSize=5.7, fillColor=colors.HexColor(TEXT)))
        drawing.add(String(width - 8, y, f"{(value / total) * 100:.0f}%", fontName="Helvetica-Bold", fontSize=5.7, fillColor=colors.HexColor(MUTED), textAnchor="end"))
        y -= 15
    return drawing


def _catalog_bar_chart(rows, title, width=505, height=155):
    drawing = Drawing(width, height)
    drawing.add(String(8, height - 14, title, fontName="Helvetica-Bold", fontSize=8.4, fillColor=colors.HexColor(TEXT)))
    if not rows:
        drawing.add(String(10, 65, "Sin información", fontSize=7.2, fillColor=colors.HexColor(MUTED)))
        return drawing

    values = [int(item.get("total") or 0) for item in rows]
    labels = [str(item.get("label") or "") for item in rows]
    labels = [label if len(label) <= 32 else label[:31] + "…" for label in labels]

    chart = HorizontalBarChart()
    chart.x = 180
    chart.y = 20
    chart.width = width - 195
    chart.height = height - 48
    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontSize = 5.8
    chart.categoryAxis.labels.boxAnchor = "e"
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(1, max(values) + 1)
    chart.valueAxis.valueStep = max(1, round(chart.valueAxis.valueMax / 5))
    chart.valueAxis.labels.fontSize = 5.8
    chart.bars[0].fillColor = colors.HexColor(PRIMARY)
    chart.bars[0].strokeColor = colors.HexColor(PRIMARY)
    drawing.add(chart)
    return drawing

# ============================================================
# BLOQUE VISUAL DE PUBLICACIÓN
# ============================================================


def _record_block(record, index, styles):
    badge_table = Table(
        [[
            _p(record["tipo"], styles["badge"]),
            _p(record["periodo"], styles["muted"]),
        ]],
        colWidths=[128 * mm, 45 * mm],
        hAlign="LEFT",
    )
    badge_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#EDF3FF")),
                ("BOX", (0, 0), (0, 0), 0.45, colors.HexColor("#B8C9F5")),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    academic = " · ".join(
        value for value in [record["sede"], record["facultad"], record["carrera"]] if value
    )

    meta_parts = []
    if record["proyecto"]:
        meta_parts.append(f"Proyecto: {record['proyecto']}")
    if record["origen"] and record["origen"] != "—":
        origin = f"Origen: {record['origen']}"
        if record["origen_detalle"]:
            origin += f" · {record['origen_detalle']}"
        meta_parts.append(origin)
    if record["identificador"]:
        meta_parts.append(record["identificador"])
    if record["contexto"]:
        meta_parts.append(record["contexto"])
    meta_parts.append("PDF disponible" if record["con_pdf"] else "Sin PDF asociado")

    content = [
        badge_table,
        Spacer(1, 2.2 * mm),
        _p(f"{index}. {record['titulo']}", styles["record_title"]),
        Table(
            [
                [_p("AUTORES", styles["label"]), _p(record["autores"], styles["body"])],
                [_p("UBICACIÓN ACADÉMICA", styles["label"]), _p(academic, styles["body"])],
                [_p("INFORMACIÓN", styles["label"]), _p(" · ".join(meta_parts), styles["muted"])],
            ],
            colWidths=[34 * mm, 139 * mm],
            hAlign="LEFT",
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            ),
        ),
    ]

    outer = Table(
        [[content]],
        colWidths=[180 * mm],
        hAlign="LEFT",
    )
    outer.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(WHITE)),
                ("BOX", (0, 0), (-1, -1), 0.65, colors.HexColor(LINE)),
                ("LINEABOVE", (0, 0), (-1, 0), 2.2, colors.HexColor(PRIMARY)),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return KeepTogether([outer, Spacer(1, 3.2 * mm)])


# ============================================================
# GENERACIÓN
# ============================================================


def build_publicaciones_pdf_bytes(filters=None):
    """Devuelve el catálogo filtrado como PDF en bytes."""

    _require_reportlab()

    normalized_filters = dict(filters or {})
    publicaciones = list(_build_queryset(normalized_filters))

    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=17 * mm,
        bottomMargin=18 * mm,
        title="Reporte de publicaciones",
        author="SGPC ULEAM",
        subject="Catálogo institucional de producción científica validada",
    )

    styles = _styles()
    generated = timezone.localtime().strftime("%d/%m/%Y %H:%M")

    with_pdf = sum(1 for publicacion in publicaciones if _has_any_pdf(publicacion))
    with_project = sum(1 for publicacion in publicaciones if _publication_project(publicacion))

    summary = Table(
        [[
            [
                _p("PUBLICACIONES", styles["label"]),
                _p(len(publicaciones), styles["summary_value"]),
                _p("registros incluidos", styles["muted"]),
            ],
            [
                _p("CON PDF", styles["label"]),
                _p(with_pdf, styles["summary_value"]),
                _p("documentos disponibles", styles["muted"]),
            ],
            [
                _p("CON PROYECTO", styles["label"]),
                _p(with_project, styles["summary_value"]),
                _p("publicaciones vinculadas", styles["muted"]),
            ],
        ]],
        colWidths=[60 * mm, 60 * mm, 60 * mm],
        hAlign="LEFT",
    )
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(WHITE)),
                ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor(LINE)),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story = [
        _p("Reporte de publicaciones", styles["title"]),
        _p(
            "Catálogo institucional de producción científica validada en el SGPC ULEAM.",
            styles["subtitle"],
        ),
        summary,
        Spacer(1, 4 * mm),
        _p("Filtros aplicados", styles["section"]),
        _filters_table(normalized_filters, styles),
        Spacer(1, 5 * mm),
        _p("Resumen gráfico", styles["section"]),
    ]

    type_rows, year_rows, site_rows = _catalog_chart_data(publicaciones)
    story.append(
        Table(
            [[
                _catalog_donut_chart(type_rows, "Tipos de publicación"),
                _catalog_line_chart(year_rows, "Evolución por año"),
            ]],
            colWidths=[90 * mm, 90 * mm],
            hAlign="LEFT",
            style=TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor(LINE)),
                    ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor(LINE)),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            ),
        )
    )

    if site_rows:
        story.extend([
            Spacer(1, 3 * mm),
            Table(
                [[_catalog_bar_chart(site_rows, "Sedes con mayor producción")]],
                colWidths=[180 * mm],
                hAlign="LEFT",
                style=TableStyle([
                    ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor(LINE)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]),
            ),
        ])

    story.extend([
        PageBreak(),
        _p("Publicaciones incluidas", styles["section"]),
    ])

    if publicaciones:
        for index, publicacion in enumerate(publicaciones, start=1):
            story.append(
                _record_block(
                    _publication_record(publicacion),
                    index,
                    styles,
                )
            )
    else:
        story.append(
            Table(
                [[_p(
                    "No existen publicaciones aprobadas que coincidan con los filtros seleccionados.",
                    styles["muted"],
                )]],
                colWidths=[180 * mm],
                hAlign="LEFT",
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(SOFT)),
                        ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor(LINE)),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                ),
            )
        )

    document.build(
        story,
        onFirstPage=_header_footer,
        onLaterPages=_header_footer,
    )

    return output.getvalue()


def publicaciones_pdf_filename():
    stamp = timezone.localtime().strftime("%Y%m%d_%H%M%S")
    return f"reporte_publicaciones_{stamp}.pdf"