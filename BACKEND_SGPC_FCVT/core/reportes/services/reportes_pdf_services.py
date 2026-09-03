"""Generación PDF para el reporte personal de producción científica.

El PDF está orientado al usuario final: muestra únicamente contexto del
reporte, indicadores, distribuciones y publicaciones; no expone IDs internos
ni detalles de implementación.
"""

from __future__ import annotations

from io import BytesIO

from django.utils import timezone

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4, landscape
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


PRIMARY = "#1F4FD7"
PRIMARY_DARK = "#153A9B"
TEXT = "#172033"
MUTED = "#667085"
LINE = "#D9E0E8"
SOFT = "#F5F7FB"
WHITE = "#FFFFFF"
SUCCESS = "#17803D"


def _require_reportlab():
    if colors is None:
        raise RuntimeError("PDF_ENGINE_UNAVAILABLE")


def _safe(value, fallback="-"):
    text = str(value or "").strip()
    return text or fallback


def _number(value):
    try:
        return f"{int(value or 0):,}".replace(",", ".")
    except (TypeError, ValueError, OverflowError):
        return "0"


def _percent(value):
    try:
        number = float(value or 0)
    except (TypeError, ValueError, OverflowError):
        number = 0

    rounded = round(number, 1)
    text = f"{rounded:.1f}".rstrip("0").rstrip(".")
    return f"{text.replace('.', ',')}%"


def _catalog_label(payload, key, selected_id, default):
    if not selected_id:
        return default

    items = (payload.get("filtros_disponibles", {}) or {}).get(key, []) or []
    selected = str(selected_id)

    for item in items:
        if str(item.get("id")) == selected:
            return _safe(item.get("label"), default)

    return default


def _filter_labels(payload):
    filters = payload.get("filtros_aplicados", {}) or {}
    return {
        "periodo": _safe(filters.get("label"), "Histórico"),
        "tipo": _catalog_label(payload, "tipos", filters.get("tipo_id"), "Todos los tipos"),
        "proyecto": _catalog_label(
            payload,
            "proyectos",
            filters.get("proyecto_id"),
            "Todos los proyectos",
        ),
    }


def _styles():
    sample = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
            textColor=colors.HexColor(TEXT),
            alignment=TA_LEFT,
            spaceAfter=3 * mm,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8.6,
            leading=12,
            textColor=colors.HexColor(MUTED),
            spaceAfter=2 * mm,
        ),
        "section": ParagraphStyle(
            "ReportSection",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor(TEXT),
            spaceBefore=2 * mm,
            spaceAfter=2.5 * mm,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=10.5,
            textColor=colors.HexColor(TEXT),
        ),
        "muted": ParagraphStyle(
            "ReportMuted",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=10,
            textColor=colors.HexColor(MUTED),
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=colors.HexColor(MUTED),
        ),
        "metric_value": ParagraphStyle(
            "MetricValue",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            textColor=colors.HexColor(TEXT),
        ),
        "metric_primary": ParagraphStyle(
            "MetricPrimary",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            textColor=colors.HexColor(PRIMARY),
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=8.5,
            textColor=colors.HexColor(MUTED),
        ),
        "table": ParagraphStyle(
            "TableText",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=6.8,
            leading=9,
            textColor=colors.HexColor(TEXT),
        ),
        "table_bold": ParagraphStyle(
            "TableBold",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=9,
            textColor=colors.HexColor(TEXT),
        ),
    }


def _p(value, style):
    text = _safe(value)
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    return Paragraph(escaped, style)


def _header_footer(canvas, document):
    canvas.saveState()
    width, height = landscape(A4)

    canvas.setStrokeColor(colors.HexColor(LINE))
    canvas.setLineWidth(0.45)
    canvas.line(14 * mm, 12 * mm, width - 14 * mm, 12 * mm)

    canvas.setFillColor(colors.HexColor(MUTED))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(14 * mm, 7.5 * mm, "SGPC ULEAM · Producción científica")
    canvas.drawRightString(
        width - 14 * mm,
        7.5 * mm,
        f"Página {document.page}",
    )

    canvas.restoreState()


def _metadata_block(payload, styles):
    user = payload.get("usuario", {}) or {}
    labels = _filter_labels(payload)
    generated = timezone.localtime().strftime("%d/%m/%Y %H:%M")

    data = [
        [_p("Docente", styles["table_header"]), _p(user.get("nombre"), styles["table_bold"])],
        [_p("Período", styles["table_header"]), _p(labels["periodo"], styles["table"])],
        [_p("Tipo de publicación", styles["table_header"]), _p(labels["tipo"], styles["table"])],
        [_p("Proyecto", styles["table_header"]), _p(labels["proyecto"], styles["table"])],
        [_p("Generado", styles["table_header"]), _p(generated, styles["table"])],
    ]

    table = Table(data, colWidths=[36 * mm, 222 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(SOFT)),
                ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor(LINE)),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _metrics_block(payload, styles):
    summary = payload.get("resumen", {}) or {}
    total = int(summary.get("total_publicaciones") or 0)
    with_pdf = int(summary.get("con_pdf") or 0)
    with_project = int(summary.get("con_proyecto") or 0)

    metrics = [
        (
            "Publicaciones aprobadas",
            _number(total),
            "Incluidas en el período",
            True,
        ),
        (
            "Cobertura documental",
            _percent(summary.get("cobertura_pdf")),
            f"{_number(with_pdf)} de {_number(total)} con PDF",
            False,
        ),
        (
            "Vinculación a proyectos",
            _percent(summary.get("vinculacion_proyectos")),
            f"{_number(with_project)} de {_number(total)} vinculadas",
            False,
        ),
        (
            "Tipos presentes",
            _number(summary.get("total_tipos")),
            "Categorías de publicación",
            False,
        ),
    ]

    cells = []
    for label, value, note, primary in metrics:
        cells.append(
            [
                _p(label, styles["metric_label"]),
                _p(value, styles["metric_primary"] if primary else styles["metric_value"]),
                _p(note, styles["muted"]),
            ]
        )

    table = Table([cells], colWidths=[64.5 * mm] * 4, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(WHITE)),
                ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor(LINE)),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _distribution_table(title, rows, label_key, styles):
    body = [[
        _p(title, styles["table_header"]),
        _p("Publicaciones", styles["table_header"]),
    ]]

    for row in rows:
        body.append(
            [
                _p(row.get(label_key), styles["table"]),
                _p(_number(row.get("total")), styles["table_bold"]),
            ]
        )

    if len(body) == 1:
        body.append([_p("Sin datos", styles["muted"]), _p("0", styles["muted"])])

    table = Table(body, colWidths=[100 * mm, 28 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(SOFT)),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(LINE)),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table




def _chart_title(drawing, title, width):
    drawing.add(
        String(
            8,
            drawing.height - 16,
            title,
            fontName="Helvetica-Bold",
            fontSize=9,
            fillColor=colors.HexColor(TEXT),
        )
    )
    drawing.add(
        String(
            width - 8,
            drawing.height - 16,
            "",
            fontName="Helvetica",
            fontSize=7,
            fillColor=colors.HexColor(MUTED),
            textAnchor="end",
        )
    )


def _line_drawing(rows, *, label_key, title, width=365, height=185):
    drawing = Drawing(width, height)
    _chart_title(drawing, title, width)

    values = [max(0, int(row.get("total") or 0)) for row in rows]
    labels = [str(row.get(label_key) or "") for row in rows]

    if not values:
        drawing.add(String(12, 80, "Sin información para este período", fontSize=8, fillColor=colors.HexColor(MUTED)))
        return drawing

    chart = HorizontalLineChart()
    chart.x = 42
    chart.y = 34
    chart.width = width - 62
    chart.height = height - 68
    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 6.2
    chart.categoryAxis.labels.angle = 0
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(1, max(values) + max(1, round(max(values) * 0.15)))
    chart.valueAxis.valueStep = max(1, round(chart.valueAxis.valueMax / 4))
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 6.2
    chart.lines[0].strokeColor = colors.HexColor(PRIMARY)
    chart.lines[0].strokeWidth = 2
    chart.lines[0].symbol = None
    drawing.add(chart)
    return drawing


def _donut_drawing(rows, *, label_key, title, width=365, height=185):
    drawing = Drawing(width, height)
    _chart_title(drawing, title, width)

    values = [max(0, int(row.get("total") or 0)) for row in rows]
    labels = [str(row.get(label_key) or "Sin tipo") for row in rows]

    if not values or not sum(values):
        drawing.add(String(12, 80, "Sin información para este período", fontSize=8, fillColor=colors.HexColor(MUTED)))
        return drawing

    palette = ["#2F66E8", "#2F855A", "#7554B8", "#B85F2E", "#237B72", "#8A5D1E", "#5C6F82"]
    pie = Pie()
    pie.x = 32
    pie.y = 27
    pie.width = 128
    pie.height = 128
    pie.data = values
    pie.labels = None
    pie.innerRadiusFraction = 0.58
    pie.sideLabels = False
    pie.slices.strokeColor = colors.HexColor(WHITE)
    pie.slices.strokeWidth = 0.8
    for index in range(len(values)):
        pie.slices[index].fillColor = colors.HexColor(palette[index % len(palette)])
    drawing.add(pie)

    total = sum(values)
    y = height - 46
    for index, (label, value) in enumerate(zip(labels[:7], values[:7])):
        color = colors.HexColor(palette[index % len(palette)])
        drawing.add(String(184, y, "●", fontSize=8, fillColor=color))
        short = label if len(label) <= 28 else label[:27] + "…"
        drawing.add(String(198, y, short, fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor(TEXT)))
        drawing.add(
            String(
                width - 10,
                y,
                f"{value} · {(value / total) * 100:.1f}%".replace(".", ","),
                fontName="Helvetica-Bold",
                fontSize=6.5,
                fillColor=colors.HexColor(MUTED),
                textAnchor="end",
            )
        )
        y -= 16

    return drawing


def _horizontal_bar_drawing(rows, *, label_key, title, width=748, height=190, limit=8):
    drawing = Drawing(width, height)
    _chart_title(drawing, title, width)

    items = sorted(
        list(rows or []),
        key=lambda item: int(item.get("total") or 0),
        reverse=True,
    )[:limit]

    if not items:
        drawing.add(String(12, 82, "Sin publicaciones vinculadas a proyectos", fontSize=8, fillColor=colors.HexColor(MUTED)))
        return drawing

    values = [max(0, int(item.get("total") or 0)) for item in items]
    labels = []
    for item in items:
        text = str(item.get(label_key) or "Sin proyecto")
        labels.append(text if len(text) <= 42 else text[:41] + "…")

    chart = HorizontalBarChart()
    chart.x = 230
    chart.y = 24
    chart.width = width - 250
    chart.height = height - 55
    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 6.4
    chart.categoryAxis.labels.boxAnchor = "e"
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(1, max(values) + 1)
    chart.valueAxis.valueStep = max(1, round(chart.valueAxis.valueMax / 5))
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 6.2
    chart.bars[0].fillColor = colors.HexColor(PRIMARY)
    chart.bars[0].strokeColor = colors.HexColor(PRIMARY)
    drawing.add(chart)
    return drawing

def _detail_table(payload, styles):
    items = (payload.get("detalle", {}) or {}).get("items", []) or []
    headers = ["Título", "Tipo", "Período", "Proyecto", "Autores", "PDF"]

    rows = [[_p(header, styles["table_header"]) for header in headers]]

    for item in items:
        rows.append(
            [
                _p(item.get("titulo"), styles["table_bold"]),
                _p(item.get("tipo"), styles["table"]),
                _p(item.get("periodo"), styles["table"]),
                _p(item.get("proyecto") or "Sin proyecto", styles["table"]),
                _p(item.get("autores"), styles["table"]),
                _p("Sí" if item.get("con_pdf") else "No", styles["table"]),
            ]
        )

    if len(rows) == 1:
        rows.append(
            [
                _p("No hay publicaciones para los filtros seleccionados.", styles["muted"]),
                "",
                "",
                "",
                "",
                "",
            ]
        )

    table = Table(
        rows,
        colWidths=[70 * mm, 35 * mm, 24 * mm, 53 * mm, 66 * mm, 12 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(SOFT)),
                ("LINEBELOW", (0, 0), (-1, 0), 0.65, colors.HexColor(LINE)),
                ("GRID", (0, 1), (-1, -1), 0.3, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    if len(rows) == 2 and not items:
        table.setStyle(TableStyle([("SPAN", (0, 1), (-1, 1))]))

    return table


def build_teacher_production_pdf_bytes(payload):
    """Devuelve el PDF personal listo para descargar."""

    _require_reportlab()

    output = BytesIO()
    page_size = landscape(A4)
    document = SimpleDocTemplate(
        output,
        pagesize=page_size,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=13 * mm,
        bottomMargin=18 * mm,
        title="Mi producción científica",
        author="SGPC ULEAM",
        subject="Reporte personal de producción científica",
    )

    styles = _styles()
    user = payload.get("usuario", {}) or {}
    distributions = payload.get("distribuciones", {}) or {}

    story = [
        _p("Mi producción científica", styles["title"]),
        _p(
            "Resumen de publicaciones aprobadas de " + _safe(user.get("nombre"), "usuario"),
            styles["subtitle"],
        ),
        _metadata_block(payload, styles),
        Spacer(1, 4 * mm),
        _metrics_block(payload, styles),
        Spacer(1, 5 * mm),
        _p("Análisis gráfico", styles["section"]),
    ]

    year_chart = _line_drawing(
        distributions.get("por_anio", []) or [],
        label_key="anio",
        title="Evolución por año",
    )
    type_chart = _donut_drawing(
        distributions.get("por_tipo", []) or [],
        label_key="tipo",
        title="Tipos de publicación",
    )

    story.append(
        Table(
            [[year_chart, type_chart]],
            colWidths=[130 * mm, 130 * mm],
            hAlign="LEFT",
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor(LINE)),
                    ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor(LINE)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                    ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
                ]
            ),
        )
    )

    month_rows = distributions.get("por_mes", []) or []
    project_rows = distributions.get("por_proyecto", []) or []

    if month_rows:
        month_chart = _line_drawing(
            month_rows,
            label_key="periodo",
            title="Evolución mensual",
            width=748,
            height=180,
        )
        story.extend(
            [
                Spacer(1, 4 * mm),
                Table(
                    [[month_chart]],
                    colWidths=[260 * mm],
                    hAlign="LEFT",
                    style=TableStyle(
                        [
                            ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor(LINE)),
                            ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
                        ]
                    ),
                ),
            ]
        )

    if project_rows:
        project_chart = _horizontal_bar_drawing(
            project_rows,
            label_key="proyecto",
            title="Proyectos con mayor producción",
        )
        story.extend(
            [
                Spacer(1, 4 * mm),
                Table(
                    [[project_chart]],
                    colWidths=[260 * mm],
                    hAlign="LEFT",
                    style=TableStyle(
                        [
                            ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor(LINE)),
                            ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
                        ]
                    ),
                ),
            ]
        )

    story.extend(
        [
            PageBreak(),
            _p("Publicaciones del período", styles["section"]),
            _detail_table(payload, styles),
        ]
    )

    document.build(
        story,
        onFirstPage=_header_footer,
        onLaterPages=_header_footer,
    )

    return output.getvalue()


def teacher_pdf_filename():
    stamp = timezone.localtime().strftime("%Y%m%d_%H%M%S")
    return f"mi_produccion_cientifica_{stamp}.pdf"
