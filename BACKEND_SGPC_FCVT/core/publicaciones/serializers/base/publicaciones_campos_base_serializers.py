"""
Campos base reutilizables por los serializers de creación
de publicaciones.

Centraliza:

- origen de la publicación;
- grado o programa asociado al TIC;
- origen escrito manualmente cuando se selecciona Otro;
- año de publicación obligatorio;
- mes de publicación opcional;
- PDF principal.

La fecha diaria dejó de formar parte del registro de
publicaciones. El periodo se representa mediante año y,
cuando esté disponible, mes.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Publicacion


def _norm_text(value):
    """
    Convierte el valor recibido en texto limpio.
    """

    return str(
        value or ""
    ).strip()


def _norm_optional_text(value):
    """
    Convierte cadenas vacías en None.
    """

    value = _norm_text(
        value
    )

    return (
        value
        or None
    )


class PublicacionCamposBaseMixin(
    serializers.Serializer
):
    """
    Campos comunes utilizados por:

    - ArticuloRegistroSerializer
    - PonenciaRegistroSerializer
    - LibroRegistroSerializer
    - CapituloLibroRegistroSerializer
    """

    origen_tipo = serializers.ChoiceField(
        choices=Publicacion.ORIGEN_TIPO,
        required=False,
        default="ninguno",
    )

    origen_grado = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
    )

    anio_publicacion = serializers.IntegerField(
        required=True,
        min_value=1900,
        write_only=True,
        error_messages={
            "required": (
                "Debe ingresar el año de publicación."
            ),
            "invalid": (
                "El año de publicación debe ser un número entero válido."
            ),
            "min_value": (
                "El año de publicación no puede ser anterior a 1900."
            ),
        },
    )

    mes_publicacion = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=12,
        write_only=True,
        error_messages={
            "invalid": (
                "El mes de publicación debe ser un número entero válido."
            ),
            "min_value": (
                "El mes de publicación debe estar entre 1 y 12."
            ),
            "max_value": (
                "El mes de publicación debe estar entre 1 y 12."
            ),
        },
    )

    archivo_pdf = serializers.FileField(
        required=False,
        allow_null=True,
    )

    # =========================================================
    # ORIGEN
    # =========================================================

    def _aplicar_reglas_origen(
        self,
        attrs,
    ):
        """
        Aplica las reglas del origen de la publicación.

        Reglas:

        ninguno
            origen_grado = None

        tic
            origen_grado es obligatorio y representa
            el grado o programa relacionado.

        maestria
            origen_grado = None

        doctoral
            origen_grado = None

        otro
            origen_grado es obligatorio y contiene
            el origen escrito por el usuario.
        """

        origen_tipo = (
            _norm_text(
                attrs.get(
                    "origen_tipo"
                )
            ).lower()
            or "ninguno"
        )

        valid_origins = {
            value
            for value, _label
            in Publicacion.ORIGEN_TIPO
        }

        if (
            origen_tipo
            not in valid_origins
        ):
            raise ValidationError(
                {
                    "origen_tipo": [
                        "El origen de la publicación "
                        "no es válido."
                    ]
                }
            )

        origen_grado = (
            _norm_optional_text(
                attrs.get(
                    "origen_grado"
                )
            )
        )

        # =====================================================
        # TRABAJO DE INTEGRACIÓN CURRICULAR
        # =====================================================

        if origen_tipo == "tic":
            if not origen_grado:
                raise ValidationError(
                    {
                        "origen_grado": [
                            "Debe especificar el grado "
                            "o programa cuando el origen "
                            "es un Trabajo de Integración "
                            "Curricular."
                        ]
                    }
                )

        # =====================================================
        # OTRO ORIGEN
        # =====================================================

        elif origen_tipo == "otro":
            if not origen_grado:
                raise ValidationError(
                    {
                        "origen_grado": [
                            "Debe escribir el origen "
                            "de la publicación."
                        ]
                    }
                )

        # =====================================================
        # ORÍGENES PREDETERMINADOS SIN CAMPO COMPLEMENTARIO
        # =====================================================

        else:
            origen_grado = None

        attrs[
            "origen_tipo"
        ] = origen_tipo

        attrs[
            "origen_grado"
        ] = origen_grado

        return attrs