"""
Serializers para exponer banners institucionales,
su configuración global y construir URLs absolutas.
"""

import os
from rest_framework import serializers

from core.models.banners import (
    ASIDE_WIDTH_MIN,
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

BANNER_MAX_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_BANNER_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_BANNER_CONTENT_TYPES = {"image/jpeg", "image/png"}


class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    recentLabel = serializers.CharField(
        source="recent_label",
        allow_blank=True,
        required=False,
    )
    eyebrow = serializers.CharField(
        allow_blank=True,
        required=False,
    )
    title = serializers.CharField(
        allow_blank=True,
        required=False,
    )
    text = serializers.CharField(
        allow_blank=True,
        required=False,
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

    def validate_image(self, value):
        if not value:
            return value

        file_name = str(getattr(value, "name", "") or "").lower()
        ext = os.path.splitext(file_name)[1]

        if ext not in ALLOWED_BANNER_EXTENSIONS:
            raise serializers.ValidationError("Solo se permiten imágenes JPG o PNG.")

        content_type = (
            getattr(value, "content_type", None)
            or getattr(getattr(value, "file", None), "content_type", None)
        )
        if content_type and content_type not in ALLOWED_BANNER_CONTENT_TYPES:
            raise serializers.ValidationError("Solo se permiten imágenes JPG o PNG.")

        file_size = int(getattr(value, "size", 0) or 0)
        if file_size > BANNER_MAX_BYTES:
            raise serializers.ValidationError(
                "La imagen del banner supera el tamaño máximo de 2 MB."
            )

        return value

    def get_image_url(self, obj):
        request = self.context.get("request")

        image = getattr(obj, "image", None)
        if not image:
            return None

        image_url = getattr(image, "url", None)
        if not image_url:
            return None

        if request:
            try:
                return request.build_absolute_uri(image_url)
            except Exception:
                return image_url

        return image_url


class BannerConfiguracionSerializer(serializers.ModelSerializer):
    eyebrow = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=60,
    )
    title = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=220,
    )
    text = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    recentLabel = serializers.CharField(
        source="recent_label",
        required=False,
        allow_blank=True,
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
        choices=[DISPLAY_MODE_MIXED, DISPLAY_MODE_BANNER, DISPLAY_MODE_TEXT],
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

    def _coerce_int_like(self, value):
        if value in (None, ""):
            return value

        if isinstance(value, bool):
            return int(value)

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(round(value))

        if isinstance(value, str):
            cleaned = value.strip().lower().replace("px", "").replace(",", ".")
            if cleaned == "":
                return value
            return int(round(float(cleaned)))

        return value

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            mutable = data.copy()
        else:
            mutable = dict(data or {})

        alias_map = {
            "recent_label": "recentLabel",
            "stage_width": "stageWidth",
            "stage_height": "stageHeight",
            "media_pane_width": "mediaPaneWidth",
            "display_mode": "displayMode",
        }

        for old_key, new_key in alias_map.items():
            if old_key in mutable and new_key not in mutable:
                mutable[new_key] = mutable.get(old_key)

        for key in ("stageWidth", "stageHeight", "mediaPaneWidth"):
            if key not in mutable:
                continue

            raw_value = mutable.get(key)

            try:
                mutable[key] = self._coerce_int_like(raw_value)
            except (TypeError, ValueError):
                pass

        return super().to_internal_value(mutable)

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        stage_width = attrs.get(
            "stage_width",
            getattr(instance, "stage_width", STAGE_WIDTH_DEFAULT),
        )
        stage_height = attrs.get(
            "stage_height",
            getattr(instance, "stage_height", STAGE_HEIGHT_DEFAULT),
        )
        media_pane_width = attrs.get(
            "media_pane_width",
            getattr(instance, "media_pane_width", MEDIA_PANE_WIDTH_DEFAULT),
        )
        display_mode = attrs.get(
            "display_mode",
            getattr(instance, "display_mode", DISPLAY_MODE_DEFAULT),
        )

        stage_width = int(stage_width)
        stage_height = int(stage_height)
        media_pane_width = int(media_pane_width)
        display_mode = str(display_mode).strip().lower()

        if not STAGE_WIDTH_MIN <= stage_width <= STAGE_WIDTH_MAX:
            raise serializers.ValidationError(
                {
                    "stageWidth": (
                        f"El ancho debe estar entre {STAGE_WIDTH_MIN} y "
                        f"{STAGE_WIDTH_MAX}px."
                    )
                }
            )

        if not STAGE_HEIGHT_MIN <= stage_height <= STAGE_HEIGHT_MAX:
            raise serializers.ValidationError(
                {
                    "stageHeight": (
                        f"La altura debe estar entre {STAGE_HEIGHT_MIN} y "
                        f"{STAGE_HEIGHT_MAX}px."
                    )
                }
            )

        media_max = max(
            MEDIA_PANE_WIDTH_MIN,
            stage_width - ASIDE_WIDTH_MIN - SPLITTER_WIDTH,
        )

        if not MEDIA_PANE_WIDTH_MIN <= media_pane_width <= media_max:
            raise serializers.ValidationError(
                {
                    "mediaPaneWidth": (
                        "El ancho del panel visual no es válido para el tamaño "
                        "actual del contenedor."
                    )
                }
            )

        valid_display_modes = {
            DISPLAY_MODE_MIXED,
            DISPLAY_MODE_BANNER,
            DISPLAY_MODE_TEXT,
        }

        if display_mode not in valid_display_modes:
            raise serializers.ValidationError(
                {
                    "displayMode": "El modo de visualización no es válido."
                }
            )

        return attrs

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance

    def create(self, validated_data):
        obj = BannerConfiguracion.get_solo()

        for field, value in validated_data.items():
            setattr(obj, field, value)

        obj.save()
        return obj