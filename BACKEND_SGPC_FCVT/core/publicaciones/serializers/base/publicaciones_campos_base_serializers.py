"""
Mixin con los campos base reutilizables de una publicación.
Centraliza validaciones comunes de origen, fecha de publicación y archivo PDF.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Publicacion


class PublicacionCamposBaseMixin(serializers.Serializer):
    origen_tipo = serializers.ChoiceField(
        choices=[c[0] for c in Publicacion._meta.get_field("origen_tipo").choices],
        required=False,
        default="ninguno",
    )
    origen_grado = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    fecha_publicacion = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
    )
    archivo_pdf = serializers.FileField(
        required=False,
        allow_null=True,
    )

    def _aplicar_reglas_origen(self, attrs):
        origen_tipo = str(attrs.get("origen_tipo") or "ninguno").strip().lower() or "ninguno"

        valid_origenes = {
            choice[0]
            for choice in Publicacion._meta.get_field("origen_tipo").choices
        }

        if origen_tipo not in valid_origenes:
            raise ValidationError({"origen_tipo": ["Opción inválida de origen."]})

        origen_grado = attrs.get("origen_grado", None)
        if origen_grado is not None:
            origen_grado = str(origen_grado).strip() or None

        attrs["origen_tipo"] = origen_tipo

        if origen_tipo == "tic":
            if not origen_grado:
                raise ValidationError(
                    {"origen_grado": ["Debe especificar el grado cuando el origen es TIC."]}
                )
            attrs["origen_grado"] = origen_grado
        else:
            attrs["origen_grado"] = None

        return attrs