"""
Serializer para solicitar una extensión del periodo de edición
del perfil.

Este serializer valida únicamente la información enviada por el
usuario. No modifica el perfil, no desbloquea la cuenta y no
concede automáticamente la extensión.

La verificación del estado actual del periodo y el envío del
correo se realizan en auth_profile_extension_services.py.
"""

import unicodedata

from rest_framework import serializers


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROFILE_EXTENSION_DEFAULT_HOURS = 48

PROFILE_EXTENSION_HOUR_CHOICES = (
    (24, "24 horas"),
    (48, "48 horas"),
    (72, "72 horas"),
)

PROFILE_EXTENSION_MIN_REASON_LENGTH = 20
PROFILE_EXTENSION_MAX_REASON_LENGTH = 1000
PROFILE_EXTENSION_MAX_LINES = 20


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_unicode(value):
    """
    Normaliza caracteres Unicode equivalentes.

    NFKC evita diferencias innecesarias entre caracteres
    visualmente iguales.
    """
    return unicodedata.normalize(
        "NFKC",
        str(value or ""),
    )


def _remove_unsafe_control_characters(value):
    """
    Elimina caracteres de control no permitidos.

    Se conservan:

    - Salto de línea.
    - Retorno de carro.
    - Tabulación.
    """
    return "".join(
        character
        for character in value
        if (
            character in {
                "\n",
                "\r",
                "\t",
            }
            or not unicodedata.category(
                character
            ).startswith("C")
        )
    )


def _normalize_reason(value):
    """
    Normaliza el motivo conservando sus párrafos.

    - Convierte CRLF y CR en LF.
    - Elimina espacios repetidos dentro de cada línea.
    - Elimina líneas vacías repetidas.
    - Conserva una línea vacía entre párrafos.
    """
    normalized = _normalize_unicode(
        value
    )

    normalized = (
        normalized
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    normalized = (
        _remove_unsafe_control_characters(
            normalized
        )
    )

    output_lines = []
    previous_line_was_empty = False

    for raw_line in normalized.split("\n"):
        clean_line = " ".join(
            raw_line
            .replace("\t", " ")
            .split()
        )

        if clean_line:
            output_lines.append(
                clean_line
            )

            previous_line_was_empty = False

        elif (
            output_lines
            and not previous_line_was_empty
        ):
            output_lines.append(
                ""
            )

            previous_line_was_empty = True

    while (
        output_lines
        and output_lines[-1] == ""
    ):
        output_lines.pop()

    return "\n".join(
        output_lines
    ).strip()


# ============================================================
# SERIALIZER
# ============================================================

class ProfileEditExtensionRequestSerializer(
    serializers.Serializer
):
    """
    Valida una solicitud de extensión del periodo de edición.

    Campos esperados:

    {
        "motivo": "Descripción de la solicitud",
        "horas_solicitadas": 48
    }
    """

    motivo = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=False,
        min_length=(
            PROFILE_EXTENSION_MIN_REASON_LENGTH
        ),
        max_length=(
            PROFILE_EXTENSION_MAX_REASON_LENGTH
        ),
        error_messages={
            "required": (
                "Debe indicar el motivo de la solicitud."
            ),
            "blank": (
                "Debe indicar el motivo de la solicitud."
            ),
            "null": (
                "Debe indicar el motivo de la solicitud."
            ),
            "min_length": (
                "El motivo debe contener al menos "
                f"{PROFILE_EXTENSION_MIN_REASON_LENGTH} "
                "caracteres."
            ),
            "max_length": (
                "El motivo no puede superar los "
                f"{PROFILE_EXTENSION_MAX_REASON_LENGTH} "
                "caracteres."
            ),
        },
    )

    horas_solicitadas = serializers.ChoiceField(
        required=False,
        allow_null=False,
        default=(
            PROFILE_EXTENSION_DEFAULT_HOURS
        ),
        choices=(
            PROFILE_EXTENSION_HOUR_CHOICES
        ),
        error_messages={
            "required": (
                "Debe seleccionar la cantidad de "
                "horas solicitadas."
            ),
            "null": (
                "Debe seleccionar la cantidad de "
                "horas solicitadas."
            ),
            "invalid_choice": (
                "Seleccione una extensión de "
                "24, 48 o 72 horas."
            ),
        },
    )

    # ========================================================
    # MOTIVO
    # ========================================================

    def validate_motivo(
        self,
        value,
    ):
        """
        Normaliza y valida el motivo antes de enviarlo al
        servicio de correo.
        """
        normalized_reason = _normalize_reason(
            value
        )

        if not normalized_reason:
            raise serializers.ValidationError(
                (
                    "Debe indicar el motivo "
                    "de la solicitud."
                )
            )

        if (
            len(normalized_reason)
            < PROFILE_EXTENSION_MIN_REASON_LENGTH
        ):
            raise serializers.ValidationError(
                (
                    "El motivo debe contener al menos "
                    f"{PROFILE_EXTENSION_MIN_REASON_LENGTH} "
                    "caracteres."
                )
            )

        if (
            len(normalized_reason)
            > PROFILE_EXTENSION_MAX_REASON_LENGTH
        ):
            raise serializers.ValidationError(
                (
                    "El motivo no puede superar los "
                    f"{PROFILE_EXTENSION_MAX_REASON_LENGTH} "
                    "caracteres."
                )
            )

        line_count = len(
            normalized_reason.splitlines()
        )

        if (
            line_count
            > PROFILE_EXTENSION_MAX_LINES
        ):
            raise serializers.ValidationError(
                (
                    "El motivo no puede contener más de "
                    f"{PROFILE_EXTENSION_MAX_LINES} líneas."
                )
            )

        # Evita aceptar textos que solo repitan el mismo
        # carácter, por ejemplo: "aaaaaaaaaaaaaaaaaaaa".
        compact_text = "".join(
            character
            for character in normalized_reason
            if not character.isspace()
        )

        if (
            compact_text
            and len(set(compact_text.lower())) == 1
        ):
            raise serializers.ValidationError(
                (
                    "Escriba un motivo descriptivo "
                    "para la solicitud."
                )
            )

        return normalized_reason

    # ========================================================
    # HORAS
    # ========================================================

    def validate_horas_solicitadas(
        self,
        value,
    ):
        """
        Garantiza que el servicio reciba un número entero.
        """
        if isinstance(
            value,
            bool,
        ):
            raise serializers.ValidationError(
                (
                    "Seleccione una extensión de "
                    "24, 48 o 72 horas."
                )
            )

        try:
            requested_hours = int(
                value
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ) as exc:
            raise serializers.ValidationError(
                (
                    "Seleccione una extensión de "
                    "24, 48 o 72 horas."
                )
            ) from exc

        allowed_hours = {
            choice_value
            for choice_value, _label
            in PROFILE_EXTENSION_HOUR_CHOICES
        }

        if requested_hours not in allowed_hours:
            raise serializers.ValidationError(
                (
                    "Seleccione una extensión de "
                    "24, 48 o 72 horas."
                )
            )

        return requested_hours

    # ========================================================
    # VALIDACIÓN FINAL
    # ========================================================

    def validate(
        self,
        attrs,
    ):
        """
        Garantiza que los campos normalizados estén presentes
        antes de invocar el servicio.
        """
        reason = attrs.get(
            "motivo"
        )

        requested_hours = attrs.get(
            "horas_solicitadas",
            PROFILE_EXTENSION_DEFAULT_HOURS,
        )

        if not reason:
            raise serializers.ValidationError(
                {
                    "motivo": (
                        "Debe indicar el motivo "
                        "de la solicitud."
                    )
                }
            )

        attrs["horas_solicitadas"] = int(
            requested_hours
        )

        return attrs