"""
Campos base reutilizables por los serializers de creación
de publicaciones.

Centraliza:

- origen de la publicación;
- grado/programa asociado al TIC;
- fecha de publicación;
- PDF principal.

La validación específica del PDF se mantiene en los
serializers que la necesitan, mientras este mixin define
el campo común.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Publicacion


def _norm_text(value):
    return str(
        value or ""
    ).strip()


def _norm_optional_text(value):
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
    )

    fecha_publicacion = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=(
            "%Y-%m-%d",
            "%d/%m/%Y",
        ),
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
        Aplica exactamente las reglas de Publicacion:

        ninguno
            origen_grado = None

        tic
            origen_grado obligatorio

        maestria
            origen_grado = None

        doctoral
            origen_grado = None
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

        # -----------------------------------------------------
        # TIC
        # -----------------------------------------------------

        if origen_tipo == "tic":
            if not origen_grado:
                raise ValidationError(
                    {
                        "origen_grado": [
                            "Debe especificar el grado "
                            "cuando el origen es un "
                            "Trabajo de Integración Curricular."
                        ]
                    }
                )

        # -----------------------------------------------------
        # Cualquier otro origen
        # -----------------------------------------------------

        else:
            origen_grado = None

        attrs[
            "origen_tipo"
        ] = origen_tipo

        attrs[
            "origen_grado"
        ] = origen_grado

        return attrs