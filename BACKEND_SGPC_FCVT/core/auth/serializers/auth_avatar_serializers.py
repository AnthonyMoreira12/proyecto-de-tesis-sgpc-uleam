"""
Serializer para actualizar el avatar del usuario autenticado.

Responsabilidades:

- Exponer únicamente el campo avatar.
- Validar extensión y tipo MIME.
- Verificar el contenido real mediante Pillow.
- Rechazar archivos vacíos, dañados o animados.
- Limitar peso, dimensiones y cantidad de píxeles.
- Mantener el puntero del archivo listo para su almacenamiento.

La eliminación del avatar anterior se gestiona desde el modelo Usuario.
"""

import os
import warnings

from django.contrib.auth import get_user_model
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

MAX_AVATAR_BYTES = 1 * 1024 * 1024
MAX_AVATAR_WIDTH = 6000
MAX_AVATAR_HEIGHT = 6000
MAX_AVATAR_PIXELS = 20_000_000

ALLOWED_AVATAR_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_AVATAR_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}

FORMAT_EXTENSIONS = {
    "JPEG": {
        ".jpg",
        ".jpeg",
    },
    "PNG": {
        ".png",
    },
    "WEBP": {
        ".webp",
    },
}

FORMAT_CONTENT_TYPES = {
    "JPEG": {
        "image/jpeg",
    },
    "PNG": {
        "image/png",
    },
    "WEBP": {
        "image/webp",
    },
}


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza un valor textual.
    """
    return str(
        value or ""
    ).strip()


def _normalize_content_type(value):
    """
    Normaliza un tipo MIME.
    """
    normalized = _normalize_text(
        value
    ).lower()

    return normalized or None


def _get_file_object(uploaded_file):
    """
    Obtiene el objeto de archivo interno cuando está disponible.
    """
    return getattr(
        uploaded_file,
        "file",
        uploaded_file,
    )


def _rewind_file(uploaded_file):
    """
    Devuelve el puntero del archivo al inicio.

    Esto es necesario después de que Pillow haya leído el
    contenido para permitir que Django lo almacene correctamente.
    """
    file_object = _get_file_object(
        uploaded_file
    )

    seek_method = getattr(
        file_object,
        "seek",
        None,
    )

    if callable(seek_method):
        try:
            seek_method(0)

        except (
            OSError,
            ValueError,
        ):
            pass


def _get_file_size(uploaded_file):
    """
    Obtiene el tamaño del archivo como entero seguro.
    """
    try:
        return int(
            getattr(
                uploaded_file,
                "size",
                0,
            )
            or 0
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return 0


def _inspect_image(uploaded_file):
    """
    Verifica el contenido real de la imagen.

    Retorna:
        dict:
            format
            width
            height
            frames
    """
    file_object = _get_file_object(
        uploaded_file
    )

    _rewind_file(
        uploaded_file
    )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter(
                "error",
                Image.DecompressionBombWarning,
            )

            with Image.open(
                file_object
            ) as image:
                detected_format = str(
                    image.format or ""
                ).upper()

                image.verify()

        _rewind_file(
            uploaded_file
        )

        with warnings.catch_warnings():
            warnings.simplefilter(
                "error",
                Image.DecompressionBombWarning,
            )

            with Image.open(
                file_object
            ) as image:
                width = int(
                    image.width
                )

                height = int(
                    image.height
                )

                frames = int(
                    getattr(
                        image,
                        "n_frames",
                        1,
                    )
                    or 1
                )

                detected_format = str(
                    image.format
                    or detected_format
                    or ""
                ).upper()

        return {
            "format": detected_format,
            "width": width,
            "height": height,
            "frames": frames,
        }

    except Image.DecompressionBombError as exc:
        raise serializers.ValidationError(
            (
                "La imagen contiene una cantidad de píxeles "
                "demasiado elevada."
            )
        ) from exc

    except Image.DecompressionBombWarning as exc:
        raise serializers.ValidationError(
            (
                "La imagen tiene dimensiones excesivas "
                "para utilizarse como avatar."
            )
        ) from exc

    except UnidentifiedImageError as exc:
        raise serializers.ValidationError(
            (
                "El archivo adjunto no contiene una "
                "imagen válida."
            )
        ) from exc

    except (
        OSError,
        ValueError,
        SyntaxError,
    ) as exc:
        raise serializers.ValidationError(
            (
                "La imagen está dañada o no puede "
                "ser procesada."
            )
        ) from exc

    finally:
        _rewind_file(
            uploaded_file
        )


# ============================================================
# SERIALIZER
# ============================================================

class AvatarUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Actualiza exclusivamente la imagen de perfil.
    """

    avatar = serializers.ImageField(
        required=True,
        allow_null=False,
        allow_empty_file=False,
        write_only=True,
        error_messages={
            "required": (
                "Debe adjuntar una imagen."
            ),
            "null": (
                "Debe adjuntar una imagen."
            ),
            "blank": (
                "Debe adjuntar una imagen."
            ),
            "empty": (
                "La imagen adjunta está vacía."
            ),
            "invalid_image": (
                "El archivo adjunto no es una "
                "imagen válida."
            ),
        },
    )

    class Meta:
        model = User

        fields = [
            "avatar",
        ]

    def validate_avatar(
        self,
        value,
    ):
        """
        Valida el archivo antes de almacenarlo.
        """
        if not value:
            raise serializers.ValidationError(
                "Debe adjuntar una imagen."
            )

        # ====================================================
        # NOMBRE Y EXTENSIÓN
        # ====================================================

        file_name = _normalize_text(
            getattr(
                value,
                "name",
                "",
            )
        )

        if not file_name:
            raise serializers.ValidationError(
                (
                    "No fue posible determinar el nombre "
                    "del archivo."
                )
            )

        extension = os.path.splitext(
            file_name.lower()
        )[1]

        if extension not in ALLOWED_AVATAR_EXTENSIONS:
            raise serializers.ValidationError(
                (
                    "Formato no permitido. Utilice una "
                    "imagen JPG, PNG o WEBP."
                )
            )

        # ====================================================
        # TIPO MIME DECLARADO
        # ====================================================

        content_type = _normalize_content_type(
            getattr(
                value,
                "content_type",
                None,
            )
        )

        if (
            content_type is not None
            and content_type
            not in ALLOWED_AVATAR_CONTENT_TYPES
        ):
            raise serializers.ValidationError(
                (
                    "El tipo de contenido del archivo "
                    "no está permitido."
                )
            )

        # ====================================================
        # TAMAÑO
        # ====================================================

        file_size = _get_file_size(
            value
        )

        if file_size <= 0:
            raise serializers.ValidationError(
                "La imagen adjunta está vacía."
            )

        if file_size > MAX_AVATAR_BYTES:
            raise serializers.ValidationError(
                (
                    "La imagen supera el tamaño máximo "
                    "permitido de 1 MB."
                )
            )

        # ====================================================
        # CONTENIDO REAL
        # ====================================================

        image_info = _inspect_image(
            value
        )

        detected_format = image_info[
            "format"
        ]

        width = image_info[
            "width"
        ]

        height = image_info[
            "height"
        ]

        frames = image_info[
            "frames"
        ]

        if (
            detected_format
            not in ALLOWED_AVATAR_FORMATS
        ):
            raise serializers.ValidationError(
                (
                    "El contenido real de la imagen "
                    "no corresponde a JPG, PNG o WEBP."
                )
            )

        # ====================================================
        # COHERENCIA DE EXTENSIÓN
        # ====================================================

        allowed_extensions_for_format = (
            FORMAT_EXTENSIONS.get(
                detected_format,
                set(),
            )
        )

        if (
            extension
            not in allowed_extensions_for_format
        ):
            raise serializers.ValidationError(
                (
                    "La extensión del archivo no coincide "
                    "con el formato real de la imagen."
                )
            )

        # ====================================================
        # COHERENCIA DE MIME
        # ====================================================

        allowed_content_types_for_format = (
            FORMAT_CONTENT_TYPES.get(
                detected_format,
                set(),
            )
        )

        if (
            content_type is not None
            and content_type
            not in allowed_content_types_for_format
        ):
            raise serializers.ValidationError(
                (
                    "El tipo de contenido declarado no "
                    "coincide con el formato real."
                )
            )

        # ====================================================
        # DIMENSIONES
        # ====================================================

        if width <= 0 or height <= 0:
            raise serializers.ValidationError(
                (
                    "La imagen no tiene dimensiones "
                    "válidas."
                )
            )

        if (
            width > MAX_AVATAR_WIDTH
            or height > MAX_AVATAR_HEIGHT
        ):
            raise serializers.ValidationError(
                (
                    "La imagen supera las dimensiones "
                    f"máximas de {MAX_AVATAR_WIDTH} × "
                    f"{MAX_AVATAR_HEIGHT} píxeles."
                )
            )

        total_pixels = (
            width * height
        )

        if total_pixels > MAX_AVATAR_PIXELS:
            raise serializers.ValidationError(
                (
                    "La imagen contiene demasiados "
                    "píxeles para utilizarse como avatar."
                )
            )

        # ====================================================
        # ANIMACIÓN
        # ====================================================

        if frames > 1:
            raise serializers.ValidationError(
                (
                    "No se permiten imágenes animadas "
                    "como avatar."
                )
            )

        _rewind_file(
            value
        )

        return value