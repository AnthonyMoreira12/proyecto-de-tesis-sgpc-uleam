"""
Serializer para solicitar una extensión del plazo de edición del perfil.

La solicitud no modifica el perfil ni amplía el plazo automáticamente.
Únicamente valida los datos que se enviarán al administrador.
"""

from rest_framework import serializers


class ProfileEditExtensionRequestSerializer(serializers.Serializer):
    motivo = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        min_length=20,
        max_length=1000,
        error_messages={
            "required": "Debe indicar el motivo de la solicitud.",
            "blank": "Debe indicar el motivo de la solicitud.",
            "min_length": "El motivo debe contener al menos 20 caracteres.",
            "max_length": "El motivo no puede superar los 1000 caracteres.",
        },
    )

    horas_solicitadas = serializers.ChoiceField(
        required=False,
        default=48,
        choices=(24, 48, 72),
        error_messages={
            "invalid_choice": "Seleccione una extensión de 24, 48 o 72 horas.",
        },
    )

    def validate_motivo(self, value):
        value = " ".join(str(value).split())

        if len(value) < 20:
            raise serializers.ValidationError(
                "El motivo debe contener al menos 20 caracteres."
            )

        return value