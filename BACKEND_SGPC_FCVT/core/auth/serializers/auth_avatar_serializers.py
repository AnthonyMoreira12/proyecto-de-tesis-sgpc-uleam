"""
Serializer para actualizar el avatar del usuario autenticado.

Responsabilidades:

- Exponer únicamente el campo avatar.
- Limitar el archivo a 1 MB.
- Validar extensión y tipo MIME.
- Inspeccionar el contenido real mediante Pillow.
- Rechazar imágenes dañadas, animadas o excesivamente grandes.
- Comprobar la correspondencia entre extensión, MIME y formato.
- Restaurar el puntero del archivo antes de almacenarlo.
"""

import os
import warnings
from io import BytesIO

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
# NORMALIZACIÓN
# ============================================================

def _normalize_text(value):
    """
    Convierte un valor en texto limpio.
    """
    return str(
        value or ""
    ).strip()


def _normalize_content_type(value):
    """
    Normaliza el tipo MIME declarado por el navegador.
    """
    normalized = _normalize_text(
        value
    ).lower()

    return normalized or None


def _get_file_size(uploaded_file):
    """
    Obtiene de forma segura el peso declarado del archivo.
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
        OSError,
    ):
        return 0


def _rewind_file(uploaded_file):
    """
    Coloca nuevamente el puntero del archivo en la posición cero.

    Se intenta reposicionar tanto el UploadedFile como su archivo
    interno para mantener compatibilidad con archivos temporales
    y archivos cargados en memoria.
    """
    candidates = [
        uploaded_file,
        getattr(
            uploaded_file,
            "file",
            None,
        ),
    ]

    for candidate in candidates:
        if candidate is None:
            continue

        seek = getattr(
            candidate,
            "seek",
            None,
        )

        if not callable(seek):
            continue

        try:
            seek(0)

        except (
            OSError,
            ValueError,
            AttributeError,
        ):
            continue


def _read_file_bytes(uploaded_file):
    """
    Lee el contenido del archivo para inspeccionarlo.

    Se lee como máximo un byte adicional al límite permitido para
    detectar archivos cuyo tamaño declarado no sea confiable.
    """
    _rewind_file(
        uploaded_file
    )

    try:
        raw_bytes = uploaded_file.read(
            MAX_AVATAR_BYTES + 1
        )

    except (
        OSError,
        ValueError,
        AttributeError,
    ) as exc:
        raise serializers.ValidationError(
            (
                "No fue posible leer la imagen "
                "seleccionada."
            )
        ) from exc

    finally:
        _rewind_file(
            uploaded_file
        )

    if not raw_bytes:
        raise serializers.ValidationError(
            "La imagen adjunta está vacía."
        )

    if len(raw_bytes) > MAX_AVATAR_BYTES:
        raise serializers.ValidationError(
            (
                "La imagen supera el tamaño máximo "
                "permitido de 1 MB."
            )
        )

    return raw_bytes


# ============================================================
# INSPECCIÓN DEL CONTENIDO
# ============================================================

def _inspect_image(raw_bytes):
    """
    Inspecciona la imagen mediante Pillow.

    La primera apertura ejecuta verify() para comprobar la
    estructura completa. La segunda apertura obtiene formato,
    dimensiones y número de fotogramas.
    """
    detected_format = ""
    width = 0
    height = 0
    frames = 1

    try:
        with warnings.catch_warnings():
            warnings.simplefilter(
                "error",
                Image.DecompressionBombWarning,
            )

            with Image.open(
                BytesIO(raw_bytes)
            ) as image:
                detected_format = _normalize_text(
                    image.format
                ).upper()

                image.verify()

        with warnings.catch_warnings():
            warnings.simplefilter(
                "error",
                Image.DecompressionBombWarning,
            )

            with Image.open(
                BytesIO(raw_bytes)
            ) as image:
                detected_format = (
                    _normalize_text(
                        image.format
                    ).upper()
                    or detected_format
                )

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
        TypeError,
    ) as exc:
        raise serializers.ValidationError(
            (
                "La imagen está dañada o no puede "
                "ser procesada."
            )
        ) from exc

    return {
        "format": detected_format,
        "width": width,
        "height": height,
        "frames": frames,
    }


# ============================================================
# SERIALIZER
# ============================================================

class AvatarUpdateSerializer(
    serializers.ModelSerializer
):
    """
    Valida exclusivamente la imagen del avatar.

    La actualización de la fila del Usuario y la eliminación del
    archivo anterior se gestionan desde UpdateAvatarView.
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
                "El archivo adjunto no contiene "
                "una imagen válida."
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
        if value is None:
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

        declared_content_type = (
            _normalize_content_type(
                getattr(
                    value,
                    "content_type",
                    None,
                )
            )
        )

        if (
            declared_content_type is not None
            and declared_content_type
            not in ALLOWED_AVATAR_CONTENT_TYPES
        ):
            raise serializers.ValidationError(
                (
                    "El tipo de contenido del archivo "
                    "no está permitido."
                )
            )

        # ====================================================
        # PESO
        # ====================================================

        declared_size = _get_file_size(
            value
        )

        if declared_size <= 0:
            raise serializers.ValidationError(
                "La imagen adjunta está vacía."
            )

        if declared_size > MAX_AVATAR_BYTES:
            raise serializers.ValidationError(
                (
                    "La imagen supera el tamaño máximo "
                    "permitido de 1 MB."
                )
            )

        # ====================================================
        # CONTENIDO REAL
        # ====================================================

        raw_bytes = _read_file_bytes(
            value
        )

        image_info = _inspect_image(
            raw_bytes
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
        # CORRESPONDENCIA DE EXTENSIÓN
        # ====================================================

        valid_extensions = (
            FORMAT_EXTENSIONS.get(
                detected_format,
                set(),
            )
        )

        if extension not in valid_extensions:
            raise serializers.ValidationError(
                (
                    "La extensión del archivo no corresponde "
                    "con el formato real de la imagen."
                )
            )

        # ====================================================
        # CORRESPONDENCIA DE MIME
        # ====================================================

        valid_content_types = (
            FORMAT_CONTENT_TYPES.get(
                detected_format,
                set(),
            )
        )

        if (
            declared_content_type is not None
            and declared_content_type
            not in valid_content_types
        ):
            raise serializers.ValidationError(
                (
                    "El tipo de contenido declarado no "
                    "corresponde con el formato real "
                    "de la imagen."
                )
            )

        # ====================================================
        # ANIMACIÓN
        # ====================================================

        if frames != 1:
            raise serializers.ValidationError(
                (
                    "No se permiten imágenes animadas "
                    "como foto de perfil."
                )
            )

        # ====================================================
        # DIMENSIONES
        # ====================================================

        if width <= 0 or height <= 0:
            raise serializers.ValidationError(
                (
                    "No fue posible determinar las "
                    "dimensiones de la imagen."
                )
            )

        if (
            width > MAX_AVATAR_WIDTH
            or height > MAX_AVATAR_HEIGHT
        ):
            raise serializers.ValidationError(
                (
                    "La imagen supera las dimensiones "
                    "máximas permitidas de "
                    f"{MAX_AVATAR_WIDTH} × "
                    f"{MAX_AVATAR_HEIGHT} píxeles."
                )
            )

        total_pixels = width * height

        if total_pixels > MAX_AVATAR_PIXELS:
            raise serializers.ValidationError(
                (
                    "La imagen contiene demasiados píxeles. "
                    "Utilice una imagen de menor resolución."
                )
            )

        # La vista debe recibir el archivo preparado desde el
        # inicio para guardarlo correctamente.
        _rewind_file(
            value
        )

        return value