"""
Serializer público para resultados rápidos de búsqueda de proyectos.

Expone únicamente información académica necesaria para mostrar proyectos en
resultados generales y autocompletados:

- Nombre y descripción resumida.
- Estado y periodo de ejecución.
- Sede, carrera y facultad derivada.
- Fechas principales del proyecto.
- Disponibilidad y URL absoluta del PDF.
- Alias estables utilizados por el frontend.

No se expone el Usuario que registró el proyecto, porque ese dato representa
la gestión interna y no necesariamente al investigador responsable.
"""

from rest_framework import serializers

from core.models import Proyecto


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """Normaliza un texto eliminando espacios repetidos."""
    return " ".join(str(value or "").split())


def _optional_text(value):
    """Devuelve texto normalizado o ``None``."""
    normalized = _normalize_text(value)
    return normalized or None


def _safe_file_url(file_field, *, request=None):
    """Obtiene una URL segura y, cuando es posible, absoluta."""
    if not file_field or not getattr(file_field, "name", None):
        return None

    try:
        file_url = file_field.url
    except (ValueError, OSError, NotImplementedError):
        return None

    if request is None:
        return file_url

    try:
        return request.build_absolute_uri(file_url)
    except (ValueError, TypeError):
        return file_url


def _site(project):
    """Obtiene la sede institucional del proyecto."""
    return getattr(project, "sede", None) if project is not None else None


def _career(project):
    """Obtiene la carrera relacionada con el proyecto."""
    return getattr(project, "carrera", None) if project is not None else None


def _faculty(project):
    """Obtiene la facultad mediante ``proyecto.carrera.facultad``."""
    career = _career(project)
    return getattr(career, "facultad", None) if career is not None else None


def _resolved_end_date(project):
    """
    Resuelve la fecha final más representativa del proyecto.

    Prioridad:

    1. Fecha de cierre.
    2. Fecha de fin prorrogada.
    3. Fecha de fin planificada.
    """
    if project is None:
        return None

    return (
        getattr(project, "fecha_cierre", None)
        or getattr(project, "fecha_fin_prorrogada", None)
        or getattr(project, "fecha_fin_planificada", None)
    )


def _resolved_period(project):
    """Construye una representación pública y legible del periodo."""
    if project is None:
        return None

    start_year = getattr(project, "anio_inicio", None)
    end_year = getattr(project, "anio_fin", None)

    if start_year is None:
        start_date = getattr(project, "fecha_inicio", None)
        start_year = getattr(start_date, "year", None)

    if end_year is None:
        end_date = _resolved_end_date(project)
        end_year = getattr(end_date, "year", None)

    if start_year is not None and end_year is not None:
        if int(start_year) == int(end_year):
            return str(start_year)

        return f"{start_year}–{end_year}"

    if start_year is not None:
        return f"Desde {start_year}"

    if end_year is not None:
        return f"Hasta {end_year}"

    return None


# ============================================================
# SERIALIZER
# ============================================================

class ProyectoBusquedaSerializer(serializers.ModelSerializer):
    """
    Representación pública y estable de un proyecto.

    Se conservan los nombres originales en español y se añaden aliases para
    que el frontend no tenga que reconstruir el contrato.
    """

    # Alias de identificación y tipo de resultado.
    proyecto_id = serializers.IntegerField(source="pk", read_only=True)
    kind = serializers.SerializerMethodField(read_only=True)

    # Nombre y descripción.
    name = serializers.SerializerMethodField(read_only=True)
    title = serializers.SerializerMethodField(read_only=True)
    snippet = serializers.SerializerMethodField(read_only=True)

    # Sede, carrera y facultad.
    sede_id = serializers.SerializerMethodField(read_only=True)
    sede = serializers.SerializerMethodField(read_only=True)
    carrera_id = serializers.SerializerMethodField(read_only=True)
    carrera = serializers.SerializerMethodField(read_only=True)
    facultad_id = serializers.SerializerMethodField(read_only=True)
    facultad = serializers.SerializerMethodField(read_only=True)

    # Estado y periodo.
    estado_label = serializers.SerializerMethodField(read_only=True)
    periodo = serializers.SerializerMethodField(read_only=True)
    fecha_fin_resuelta = serializers.SerializerMethodField(read_only=True)

    # Archivo PDF.
    tiene_pdf = serializers.SerializerMethodField(read_only=True)
    has_pdf = serializers.SerializerMethodField(read_only=True)
    hasPdf = serializers.SerializerMethodField(read_only=True)
    archivo_pdf_url = serializers.SerializerMethodField(read_only=True)
    pdf_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Proyecto

        fields = [
            "id",
            "proyecto_id",
            "kind",

            # Nombre y descripción
            "nombre",
            "name",
            "title",
            "descripcion",
            "snippet",

            # Estado
            "estado",
            "estado_label",

            # Fechas y periodo
            "fecha_inicio",
            "fecha_fin_planificada",
            "fecha_fin_prorrogada",
            "fecha_cierre",
            "fecha_fin_resuelta",
            "anio_inicio",
            "anio_fin",
            "periodo",

            # Sede, carrera y facultad
            "sede_id",
            "sede",
            "carrera_id",
            "carrera",
            "facultad_id",
            "facultad",

            # PDF
            "tiene_pdf",
            "has_pdf",
            "hasPdf",
            "archivo_pdf_url",
            "pdf_url",
        ]

        read_only_fields = fields

    # ========================================================
    # IDENTIDAD Y TEXTO
    # ========================================================

    def get_kind(self, obj):
        return "project"

    def get_name(self, obj):
        return _optional_text(getattr(obj, "nombre", None)) or "Proyecto"

    def get_title(self, obj):
        return self.get_name(obj)

    def get_snippet(self, obj):
        return _optional_text(getattr(obj, "descripcion", None)) or ""

    # ========================================================
    # SEDE, CARRERA Y FACULTAD
    # ========================================================

    def get_sede_id(self, obj):
        site = _site(obj)
        return getattr(site, "pk", None) if site is not None else None

    def get_sede(self, obj):
        site = _site(obj)
        return _optional_text(getattr(site, "nombre", None))

    def get_carrera_id(self, obj):
        career = _career(obj)
        return getattr(career, "pk", None) if career is not None else None

    def get_carrera(self, obj):
        career = _career(obj)
        return _optional_text(getattr(career, "nombre", None))

    def get_facultad_id(self, obj):
        faculty = _faculty(obj)
        return getattr(faculty, "pk", None) if faculty is not None else None

    def get_facultad(self, obj):
        faculty = _faculty(obj)
        return _optional_text(getattr(faculty, "nombre", None))

    # ========================================================
    # ESTADO Y PERIODO
    # ========================================================

    def get_estado_label(self, obj):
        get_display = getattr(obj, "get_estado_display", None)

        if callable(get_display):
            display_value = _optional_text(get_display())
            if display_value:
                return display_value

        return _optional_text(getattr(obj, "estado", None))

    def get_periodo(self, obj):
        return _resolved_period(obj)

    def get_fecha_fin_resuelta(self, obj):
        return _resolved_end_date(obj)

    # ========================================================
    # PDF
    # ========================================================

    def get_tiene_pdf(self, obj):
        project_file = getattr(obj, "archivo_pdf", None)
        return bool(project_file and getattr(project_file, "name", None))

    def get_has_pdf(self, obj):
        return self.get_tiene_pdf(obj)

    def get_hasPdf(self, obj):
        return self.get_tiene_pdf(obj)

    def get_archivo_pdf_url(self, obj):
        return _safe_file_url(
            getattr(obj, "archivo_pdf", None),
            request=self.context.get("request"),
        )

    def get_pdf_url(self, obj):
        return self.get_archivo_pdf_url(obj)