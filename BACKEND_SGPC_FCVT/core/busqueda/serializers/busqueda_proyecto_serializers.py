"""
Serializer para resultados rápidos de búsqueda de proyectos.

Expone:

- Información básica del proyecto.
- Carrera y facultad relacionadas.
- Estado y periodo de ejecución.
- Disponibilidad del documento PDF.
- URL absoluta del archivo cuando está disponible.

La facultad siempre se deriva desde proyecto.carrera.facultad.
"""

from rest_framework import serializers

from core.models import Proyecto


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza un valor textual eliminando espacios repetidos.
    """
    return " ".join(
        str(value or "").split()
    )


def _safe_file_url(
    file_field,
    *,
    request=None,
):
    """
    Obtiene de forma segura la URL de un archivo.

    Cuando existe una petición HTTP, devuelve la URL absoluta.
    """
    if not file_field:
        return None

    file_name = getattr(
        file_field,
        "name",
        None,
    )

    if not file_name:
        return None

    try:
        file_url = file_field.url

    except (
        ValueError,
        OSError,
        NotImplementedError,
    ):
        return None

    if request is None:
        return file_url

    try:
        return request.build_absolute_uri(
            file_url
        )

    except (
        ValueError,
        TypeError,
    ):
        return file_url


# ============================================================
# SERIALIZER
# ============================================================

class ProyectoBusquedaSerializer(
    serializers.ModelSerializer
):
    """
    Representación resumida de un proyecto para búsquedas y
    autocompletados.
    """

    carrera_id = serializers.IntegerField(
        read_only=True,
    )

    carrera = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad_id = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad = serializers.SerializerMethodField(
        read_only=True,
    )

    estado_label = serializers.SerializerMethodField(
        read_only=True,
    )

    periodo = serializers.SerializerMethodField(
        read_only=True,
    )

    tiene_pdf = serializers.SerializerMethodField(
        read_only=True,
    )

    archivo_pdf_url = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Proyecto

        fields = [
            "id",
            "nombre",
            "descripcion",
            "estado",
            "estado_label",
            "anio_inicio",
            "anio_fin",
            "periodo",
            "carrera_id",
            "carrera",
            "facultad_id",
            "facultad",
            "tiene_pdf",
            "archivo_pdf_url",
        ]

        read_only_fields = fields

    # ========================================================
    # CARRERA
    # ========================================================

    def get_carrera(
        self,
        obj,
    ):
        """
        Devuelve el nombre de la carrera relacionada.
        """
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        career_name = _normalize_text(
            getattr(
                career,
                "nombre",
                None,
            )
        )

        return career_name or None

    # ========================================================
    # FACULTAD
    # ========================================================

    def get_facultad_id(
        self,
        obj,
    ):
        """
        Obtiene el identificador de la facultad desde la carrera.
        """
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        faculty_id = getattr(
            career,
            "facultad_id",
            None,
        )

        return faculty_id

    def get_facultad(
        self,
        obj,
    ):
        """
        Obtiene el nombre de la facultad desde:

            proyecto.carrera.facultad
        """
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        faculty = getattr(
            career,
            "facultad",
            None,
        )

        if faculty is None:
            return None

        faculty_name = _normalize_text(
            getattr(
                faculty,
                "nombre",
                None,
            )
        )

        return faculty_name or None

    # ========================================================
    # ESTADO
    # ========================================================

    def get_estado_label(
        self,
        obj,
    ):
        """
        Devuelve la etiqueta legible del estado.

        Ejemplos:

        - Nuevo
        - Arrastre
        - Cierre
        """
        get_display = getattr(
            obj,
            "get_estado_display",
            None,
        )

        if callable(get_display):
            display_value = _normalize_text(
                get_display()
            )

            if display_value:
                return display_value

        raw_status = _normalize_text(
            getattr(
                obj,
                "estado",
                None,
            )
        )

        return raw_status or None

    # ========================================================
    # PERIODO
    # ========================================================

    def get_periodo(
        self,
        obj,
    ):
        """
        Construye una representación legible del periodo.
        """
        start_year = getattr(
            obj,
            "anio_inicio",
            None,
        )

        end_year = getattr(
            obj,
            "anio_fin",
            None,
        )

        if (
            start_year is not None
            and end_year is not None
        ):
            if start_year == end_year:
                return str(
                    start_year
                )

            return (
                f"{start_year}–{end_year}"
            )

        if start_year is not None:
            return (
                f"Desde {start_year}"
            )

        if end_year is not None:
            return (
                f"Hasta {end_year}"
            )

        return None

    # ========================================================
    # PDF
    # ========================================================

    def get_tiene_pdf(
        self,
        obj,
    ):
        """
        Indica si el proyecto tiene un PDF principal.
        """
        project_file = getattr(
            obj,
            "archivo_pdf",
            None,
        )

        return bool(
            project_file
            and getattr(
                project_file,
                "name",
                None,
            )
        )

    def get_archivo_pdf_url(
        self,
        obj,
    ):
        """
        Devuelve la URL absoluta del archivo cuando existe.
        """
        return _safe_file_url(
            getattr(
                obj,
                "archivo_pdf",
                None,
            ),
            request=self.context.get(
                "request"
            ),
        )