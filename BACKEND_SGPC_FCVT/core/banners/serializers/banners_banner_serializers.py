"""
Serializers del módulo de banners institucionales.

Este módulo gestiona:

- Serialización de banners.
- Validación segura de imágenes.
- Construcción de URLs absolutas.
- Configuración visual global del componente.
- Compatibilidad entre nombres camelCase y snake_case.
- Validación dinámica del ancho del panel visual.
"""

import os
import unicodedata
import warnings
from decimal import Decimal, InvalidOperation

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers

from core.models.banners import (
    ASIDE_WIDTH_MIN,
    BANNER_TEXT_MAX_LENGTH,
    DEFAULT_BANNER_EYEBROW,
    DEFAULT_BANNER_RECENT_LABEL,
    DEFAULT_BANNER_TEXT,
    DEFAULT_BANNER_TITLE,
    DISPLAY_MODE_BANNER,
    DISPLAY_MODE_DEFAULT,
    DISPLAY_MODE_MIXED,
    DISPLAY_MODE_TEXT,
    MEDIA_PANE_WIDTH_DEFAULT,
    MEDIA_PANE_WIDTH_MIN,
    SPLITTER_WIDTH,
    STAGE_HEIGHT_DEFAULT,
    STAGE_HEIGHT_MAX,
    STAGE_HEIGHT_MIN,
    STAGE_WIDTH_DEFAULT,
    STAGE_WIDTH_MAX,
    STAGE_WIDTH_MIN,
    Banner,
    BannerConfiguracion,
)


# ============================================================
# CONFIGURACIÓN DE IMÁGENES
# ============================================================

BANNER_MAX_BYTES = 2 * 1024 * 1024

BANNER_MAX_WIDTH = 8000
BANNER_MAX_HEIGHT = 8000
BANNER_MAX_PIXELS = 32_000_000

ALLOWED_BANNER_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}

ALLOWED_BANNER_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
}

ALLOWED_PIL_FORMATS = {
    "JPEG",
    "PNG",
}

FORMAT_EXTENSIONS = {
    "JPEG": {
        ".jpg",
        ".jpeg",
    },
    "PNG": {
        ".png",
    },
}

FORMAT_CONTENT_TYPES = {
    "JPEG": {
        "image/jpeg",
    },
    "PNG": {
        "image/png",
    },
}


# ============================================================
# CONFIGURACIÓN DE TEXTOS
# ============================================================

def _model_max_length(
    model,
    field_name,
    default,
):
    """
    Obtiene el max_length real de un campo del modelo.
    """
    try:
        model_field = model._meta.get_field(
            field_name
        )

    except (
        LookupError,
        AttributeError,
    ):
        return int(default)

    max_length = getattr(
        model_field,
        "max_length",
        None,
    )

    return int(
        max_length or default
    )


BANNER_TITLE_MAX_LENGTH = _model_max_length(
    Banner,
    "title",
    220,
)

BANNER_EYEBROW_MAX_LENGTH = _model_max_length(
    Banner,
    "eyebrow",
    60,
)

BANNER_RECENT_LABEL_MAX_LENGTH = _model_max_length(
    Banner,
    "recent_label",
    60,
)


# ============================================================
# UTILIDADES DE TEXTO
# ============================================================

def _normalize_unicode(value):
    """
    Normaliza caracteres Unicode equivalentes.
    """
    return unicodedata.normalize(
        "NFKC",
        str(value or ""),
    )


def _contains_unsafe_control_characters(
    value,
    *,
    allow_line_breaks=False,
):
    """
    Detecta caracteres de control no permitidos.
    """
    allowed_controls = (
        {
            "\n",
            "\r",
            "\t",
        }
        if allow_line_breaks
        else set()
    )

    return any(
        (
            unicodedata.category(
                character
            ).startswith("C")
            and character not in allowed_controls
        )
        for character in value
    )


def _normalize_single_line(value):
    """
    Normaliza un texto destinado a una sola línea.
    """
    normalized = _normalize_unicode(
        value
    )

    if _contains_unsafe_control_characters(
        normalized
    ):
        raise serializers.ValidationError(
            "El texto contiene caracteres no permitidos."
        )

    return " ".join(
        normalized.split()
    )


def _normalize_multiline(value):
    """
    Normaliza un texto permitiendo párrafos y saltos de línea.
    """
    normalized = _normalize_unicode(
        value
    )

    normalized = (
        normalized
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    if _contains_unsafe_control_characters(
        normalized,
        allow_line_breaks=True,
    ):
        raise serializers.ValidationError(
            "El texto contiene caracteres no permitidos."
        )

    normalized_lines = []

    for raw_line in normalized.split("\n"):
        clean_line = " ".join(
            raw_line
            .replace("\t", " ")
            .split()
        )

        normalized_lines.append(
            clean_line
        )

    while (
        normalized_lines
        and not normalized_lines[-1]
    ):
        normalized_lines.pop()

    return "\n".join(
        normalized_lines
    ).strip()


# ============================================================
# UTILIDADES DE ARCHIVOS
# ============================================================

def _get_file_object(uploaded_file):
    """
    Obtiene el archivo interno del objeto subido.
    """
    return getattr(
        uploaded_file,
        "file",
        uploaded_file,
    )


def _rewind_file(uploaded_file):
    """
    Restablece el puntero del archivo al inicio.
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


def _normalize_content_type(value):
    """
    Normaliza un tipo MIME.
    """
    normalized = str(
        value or ""
    ).strip().lower()

    if ";" in normalized:
        normalized = normalized.split(
            ";",
            1,
        )[0].strip()

    return normalized or None


def _inspect_banner_image(uploaded_file):
    """
    Verifica el contenido real de una imagen mediante Pillow.
    """
    file_object = _get_file_object(
        uploaded_file
    )

    if not hasattr(
        file_object,
        "read",
    ):
        raise serializers.ValidationError(
            "El archivo recibido no es válido."
        )

    _rewind_file(
        uploaded_file
    )

    detected_format = None

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
                "para utilizarse como banner."
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

    return {
        "format": detected_format,
        "width": width,
        "height": height,
        "frames": frames,
    }


# ============================================================
# UTILIDADES DE VALIDACIÓN
# ============================================================

def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura DRF.
    """
    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
        return {
            "detail": list(
                exc.messages
            )
        }

    return {
        "detail": str(exc),
    }


def _safe_image_url(
    image,
    request=None,
):
    """
    Obtiene una URL segura de la imagen.
    """
    if not image:
        return None

    image_name = getattr(
        image,
        "name",
        None,
    )

    if not image_name:
        return None

    try:
        image_url = image.url

    except (
        ValueError,
        OSError,
        NotImplementedError,
    ):
        return None

    if request is None:
        return image_url

    try:
        return request.build_absolute_uri(
            image_url
        )

    except (
        ValueError,
        TypeError,
    ):
        return image_url


# ============================================================
# SERIALIZER DE BANNERS
# ============================================================

class BannerSerializer(
    serializers.ModelSerializer
):
    """
    Serializer para crear, consultar y modificar banners.
    """

    title = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=False,
        trim_whitespace=True,
        max_length=BANNER_TITLE_MAX_LENGTH,
    )

    eyebrow = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=False,
        trim_whitespace=True,
        max_length=BANNER_EYEBROW_MAX_LENGTH,
    )

    text = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=False,
        trim_whitespace=False,
        max_length=BANNER_TEXT_MAX_LENGTH,
    )

    recentLabel = serializers.CharField(
        source="recent_label",
        required=False,
        allow_blank=True,
        allow_null=False,
        trim_whitespace=True,
        max_length=BANNER_RECENT_LABEL_MAX_LENGTH,
    )

    image = serializers.ImageField(
        required=False,
        allow_null=False,
        allow_empty_file=False,
        error_messages={
            "empty": (
                "La imagen adjunta está vacía."
            ),
            "invalid_image": (
                "El archivo adjunto no es una imagen válida."
            ),
        },
    )

    image_url = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Banner

        fields = [
            "id",
            "title",
            "eyebrow",
            "text",
            "recentLabel",
            "image",
            "image_url",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "image_url",
            "created_at",
            "updated_at",
        ]

    # ========================================================
    # VALIDACIÓN DE TEXTOS
    # ========================================================

    def validate_title(
        self,
        value,
    ):
        return _normalize_single_line(
            value
        )

    def validate_eyebrow(
        self,
        value,
    ):
        return _normalize_single_line(
            value
        )

    def validate_text(
        self,
        value,
    ):
        normalized_text = _normalize_multiline(
            value
        )

        if (
            len(normalized_text)
            > BANNER_TEXT_MAX_LENGTH
        ):
            raise serializers.ValidationError(
                (
                    "El texto del banner no puede superar "
                    f"los {BANNER_TEXT_MAX_LENGTH} caracteres."
                )
            )

        return normalized_text

    def validate_recentLabel(
        self,
        value,
    ):
        return _normalize_single_line(
            value
        )

    def validate(
        self,
        attrs,
    ):
        """
        La imagen es obligatoria al crear un banner.

        Durante una actualización puede omitirse para conservar
        la imagen actual, pero no puede enviarse como null.
        """
        if (
            self.instance is None
            and "image" not in attrs
        ):
            raise serializers.ValidationError(
                {
                    "image": (
                        "La imagen del banner es obligatoria."
                    )
                }
            )

        if (
            "image" in attrs
            and attrs.get("image") is None
        ):
            raise serializers.ValidationError(
                {
                    "image": (
                        "La imagen del banner no puede ser nula."
                    )
                }
            )

        return attrs

    # ========================================================
    # VALIDACIÓN DE IMAGEN
    # ========================================================

    def validate_image(
        self,
        value,
    ):
        """
        Valida extensión, MIME, peso, formato real y dimensiones.
        """
        if value is None:
            raise serializers.ValidationError(
                "La imagen del banner no puede ser nula."
            )

        file_name = str(
            getattr(
                value,
                "name",
                "",
            )
            or ""
        ).strip()

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

        if extension not in ALLOWED_BANNER_EXTENSIONS:
            raise serializers.ValidationError(
                (
                    "Solo se permiten imágenes "
                    "JPG o PNG."
                )
            )

        content_type = _normalize_content_type(
            getattr(
                value,
                "content_type",
                None,
            )
            or getattr(
                getattr(
                    value,
                    "file",
                    None,
                ),
                "content_type",
                None,
            )
        )

        if (
            content_type is not None
            and content_type
            not in ALLOWED_BANNER_CONTENT_TYPES
        ):
            raise serializers.ValidationError(
                (
                    "El tipo de contenido debe ser "
                    "JPG o PNG."
                )
            )

        file_size = _get_file_size(
            value
        )

        if file_size <= 0:
            raise serializers.ValidationError(
                "La imagen adjunta está vacía."
            )

        if file_size > BANNER_MAX_BYTES:
            raise serializers.ValidationError(
                (
                    "La imagen del banner supera el "
                    "tamaño máximo de 2 MB."
                )
            )

        image_info = _inspect_banner_image(
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
            not in ALLOWED_PIL_FORMATS
        ):
            raise serializers.ValidationError(
                (
                    "El contenido real del archivo no "
                    "corresponde a JPG o PNG."
                )
            )

        if (
            extension
            not in FORMAT_EXTENSIONS.get(
                detected_format,
                set(),
            )
        ):
            raise serializers.ValidationError(
                (
                    "La extensión del archivo no coincide "
                    "con su formato real."
                )
            )

        if (
            content_type is not None
            and content_type
            not in FORMAT_CONTENT_TYPES.get(
                detected_format,
                set(),
            )
        ):
            raise serializers.ValidationError(
                (
                    "El tipo MIME no coincide con el "
                    "contenido real de la imagen."
                )
            )

        if width <= 0 or height <= 0:
            raise serializers.ValidationError(
                (
                    "La imagen no contiene dimensiones "
                    "válidas."
                )
            )

        if (
            width > BANNER_MAX_WIDTH
            or height > BANNER_MAX_HEIGHT
        ):
            raise serializers.ValidationError(
                (
                    "La imagen supera las dimensiones máximas "
                    f"de {BANNER_MAX_WIDTH} × "
                    f"{BANNER_MAX_HEIGHT} píxeles."
                )
            )

        if (
            width * height
            > BANNER_MAX_PIXELS
        ):
            raise serializers.ValidationError(
                (
                    "La imagen contiene demasiados píxeles "
                    "para utilizarse como banner."
                )
            )

        if frames > 1:
            raise serializers.ValidationError(
                (
                    "No se permiten imágenes animadas "
                    "como banner."
                )
            )

        _rewind_file(
            value
        )

        return value

    # ========================================================
    # URL
    # ========================================================

    def get_image_url(
        self,
        obj,
    ):
        return _safe_image_url(
            getattr(
                obj,
                "image",
                None,
            ),
            request=self.context.get(
                "request"
            ),
        )

    # ========================================================
    # CREACIÓN Y ACTUALIZACIÓN
    # ========================================================

    def create(
        self,
        validated_data,
    ):
        try:
            with transaction.atomic():
                return super().create(
                    validated_data
                )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible crear el banner "
                        "debido a un conflicto de integridad."
                    )
                }
            ) from exc

    def update(
        self,
        instance,
        validated_data,
    ):
        try:
            with transaction.atomic():
                return super().update(
                    instance,
                    validated_data,
                )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible actualizar el banner "
                        "debido a un conflicto de integridad."
                    )
                }
            ) from exc


# ============================================================
# SERIALIZER DE CONFIGURACIÓN
# ============================================================

class BannerConfiguracionSerializer(
    serializers.ModelSerializer
):
    """
    Serializer de la configuración global de banners.

    La API expone camelCase para mantener compatibilidad con
    Vue, mientras que el modelo conserva snake_case.
    """

    eyebrow = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=False,
        max_length=60,
    )

    title = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=False,
        max_length=220,
    )

    text = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=False,
        trim_whitespace=False,
        max_length=BANNER_TEXT_MAX_LENGTH,
    )

    recentLabel = serializers.CharField(
        source="recent_label",
        required=False,
        allow_blank=True,
        allow_null=False,
        max_length=60,
    )

    stageWidth = serializers.IntegerField(
        source="stage_width",
        required=False,
        min_value=STAGE_WIDTH_MIN,
        max_value=STAGE_WIDTH_MAX,
    )

    stageHeight = serializers.IntegerField(
        source="stage_height",
        required=False,
        min_value=STAGE_HEIGHT_MIN,
        max_value=STAGE_HEIGHT_MAX,
    )

    mediaPaneWidth = serializers.IntegerField(
        source="media_pane_width",
        required=False,
        min_value=MEDIA_PANE_WIDTH_MIN,
    )

    displayMode = serializers.ChoiceField(
        source="display_mode",
        required=False,
        choices=[
            DISPLAY_MODE_MIXED,
            DISPLAY_MODE_BANNER,
            DISPLAY_MODE_TEXT,
        ],
    )

    class Meta:
        model = BannerConfiguracion

        fields = [
            "eyebrow",
            "title",
            "text",
            "recentLabel",
            "stageWidth",
            "stageHeight",
            "mediaPaneWidth",
            "displayMode",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
        ]

    # ========================================================
    # NORMALIZACIÓN DE ENTRADA
    # ========================================================

    def _coerce_integer_like(
        self,
        value,
    ):
        """
        Convierte valores numéricos utilizados por controles
        visuales del frontend.

        Ejemplos admitidos:

        - 1200
        - "1200"
        - "1200px"
        - "1200.4"

        Los booleanos no se aceptan como enteros.
        """
        if value in (
            None,
            "",
        ):
            return value

        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                "Los booleanos no son dimensiones válidas."
            )

        if isinstance(
            value,
            int,
        ):
            return value

        if isinstance(
            value,
            float,
        ):
            return int(
                round(value)
            )

        cleaned = (
            str(value)
            .strip()
            .lower()
            .replace("px", "")
            .replace(",", ".")
        )

        if not cleaned:
            return value

        try:
            decimal_value = Decimal(
                cleaned
            )

        except InvalidOperation as exc:
            raise ValueError(
                "El valor no contiene un número válido."
            ) from exc

        if not decimal_value.is_finite():
            raise ValueError(
                "El valor numérico no es finito."
            )

        return int(
            decimal_value.to_integral_value(
                rounding="ROUND_HALF_UP"
            )
        )

    def to_internal_value(
        self,
        data,
    ):
        """
        Acepta nombres camelCase y snake_case.
        """
        if hasattr(
            data,
            "copy",
        ):
            mutable_data = data.copy()

        else:
            mutable_data = dict(
                data or {}
            )

        alias_map = {
            "recent_label": "recentLabel",
            "stage_width": "stageWidth",
            "stage_height": "stageHeight",
            "media_pane_width": "mediaPaneWidth",
            "display_mode": "displayMode",
        }

        for old_key, new_key in alias_map.items():
            if (
                old_key in mutable_data
                and new_key not in mutable_data
            ):
                mutable_data[new_key] = (
                    mutable_data.get(
                        old_key
                    )
                )

        dimension_fields = {
            "stageWidth": (
                "El ancho del contenedor debe ser "
                "un número válido."
            ),
            "stageHeight": (
                "La altura del contenedor debe ser "
                "un número válido."
            ),
            "mediaPaneWidth": (
                "El ancho del panel visual debe ser "
                "un número válido."
            ),
        }

        conversion_errors = {}

        for field_name, message in (
            dimension_fields.items()
        ):
            if field_name not in mutable_data:
                continue

            try:
                mutable_data[field_name] = (
                    self._coerce_integer_like(
                        mutable_data.get(
                            field_name
                        )
                    )
                )

            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                conversion_errors[
                    field_name
                ] = message

        if conversion_errors:
            raise serializers.ValidationError(
                conversion_errors
            )

        if "displayMode" in mutable_data:
            mutable_data["displayMode"] = str(
                mutable_data.get(
                    "displayMode"
                )
                or ""
            ).strip().lower()

        return super().to_internal_value(
            mutable_data
        )

    # ========================================================
    # TEXTOS
    # ========================================================

    def validate_eyebrow(
        self,
        value,
    ):
        return _normalize_single_line(
            value
        )

    def validate_title(
        self,
        value,
    ):
        return _normalize_single_line(
            value
        )

    def validate_text(
        self,
        value,
    ):
        return _normalize_multiline(
            value
        )

    def validate_recentLabel(
        self,
        value,
    ):
        return _normalize_single_line(
            value
        )

    # ========================================================
    # VALIDACIÓN CONJUNTA
    # ========================================================

    def validate(
        self,
        attrs,
    ):
        instance = getattr(
            self,
            "instance",
            None,
        )

        stage_width = int(
            attrs.get(
                "stage_width",
                getattr(
                    instance,
                    "stage_width",
                    STAGE_WIDTH_DEFAULT,
                ),
            )
        )

        stage_height = int(
            attrs.get(
                "stage_height",
                getattr(
                    instance,
                    "stage_height",
                    STAGE_HEIGHT_DEFAULT,
                ),
            )
        )

        media_pane_width = int(
            attrs.get(
                "media_pane_width",
                getattr(
                    instance,
                    "media_pane_width",
                    MEDIA_PANE_WIDTH_DEFAULT,
                ),
            )
        )

        display_mode = str(
            attrs.get(
                "display_mode",
                getattr(
                    instance,
                    "display_mode",
                    DISPLAY_MODE_DEFAULT,
                ),
            )
        ).strip().lower()

        if not (
            STAGE_WIDTH_MIN
            <= stage_width
            <= STAGE_WIDTH_MAX
        ):
            raise serializers.ValidationError(
                {
                    "stageWidth": (
                        "El ancho debe estar entre "
                        f"{STAGE_WIDTH_MIN} y "
                        f"{STAGE_WIDTH_MAX}px."
                    )
                }
            )

        if not (
            STAGE_HEIGHT_MIN
            <= stage_height
            <= STAGE_HEIGHT_MAX
        ):
            raise serializers.ValidationError(
                {
                    "stageHeight": (
                        "La altura debe estar entre "
                        f"{STAGE_HEIGHT_MIN} y "
                        f"{STAGE_HEIGHT_MAX}px."
                    )
                }
            )

        media_maximum = max(
            MEDIA_PANE_WIDTH_MIN,
            (
                stage_width
                - ASIDE_WIDTH_MIN
                - SPLITTER_WIDTH
            ),
        )

        if not (
            MEDIA_PANE_WIDTH_MIN
            <= media_pane_width
            <= media_maximum
        ):
            raise serializers.ValidationError(
                {
                    "mediaPaneWidth": (
                        "El ancho del panel visual debe "
                        f"estar entre {MEDIA_PANE_WIDTH_MIN} "
                        f"y {media_maximum}px para el ancho "
                        "actual del contenedor."
                    )
                }
            )

        valid_display_modes = {
            DISPLAY_MODE_MIXED,
            DISPLAY_MODE_BANNER,
            DISPLAY_MODE_TEXT,
        }

        if (
            display_mode
            not in valid_display_modes
        ):
            raise serializers.ValidationError(
                {
                    "displayMode": (
                        "El modo de visualización "
                        "no es válido."
                    )
                }
            )

        return attrs

    # ========================================================
    # PERSISTENCIA DEL SINGLETON
    # ========================================================

    def update(
        self,
        instance,
        validated_data,
    ):
        try:
            with transaction.atomic():
                changed_fields = []

                for field_name, value in (
                    validated_data.items()
                ):
                    if (
                        getattr(
                            instance,
                            field_name,
                            None,
                        )
                        == value
                    ):
                        continue

                    setattr(
                        instance,
                        field_name,
                        value,
                    )

                    changed_fields.append(
                        field_name
                    )

                if changed_fields:
                    instance.save(
                        update_fields=list(
                            dict.fromkeys(
                                changed_fields
                                + ["updated_at"]
                            )
                        )
                    )

                return instance

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible actualizar la "
                        "configuración de banners."
                    )
                }
            ) from exc

    def create(
        self,
        validated_data,
    ):
        """
        Mantiene un único registro de configuración.
        """
        try:
            with transaction.atomic():
                configuration = (
                    BannerConfiguracion.get_solo()
                )

                return self.update(
                    configuration,
                    validated_data,
                )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible crear la "
                        "configuración de banners."
                    )
                }
            ) from exc