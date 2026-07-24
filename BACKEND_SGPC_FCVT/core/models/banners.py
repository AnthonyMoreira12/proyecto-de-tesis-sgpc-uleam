import os

from django.core.exceptions import ValidationError
from django.db import models


DEFAULT_BANNER_EYEBROW = "SGPC ULEAM"
DEFAULT_BANNER_TITLE = "Novedades institucionales"
DEFAULT_BANNER_TEXT = (
    "Se detectó una actualización en los avisos del sistema. "
    "Revise la información antes de continuar."
)
DEFAULT_BANNER_RECENT_LABEL = "Actualización reciente"

STAGE_WIDTH_DEFAULT = 1260
STAGE_WIDTH_MIN = 900
STAGE_WIDTH_MAX = 1500

STAGE_HEIGHT_DEFAULT = 640
STAGE_HEIGHT_MIN = 440
STAGE_HEIGHT_MAX = 900

SPLITTER_WIDTH = 14
MEDIA_PANE_WIDTH_MIN = 420
ASIDE_WIDTH_MIN = 320
MEDIA_PANE_WIDTH_DEFAULT = 806

DISPLAY_MODE_MIXED = "mixed"
DISPLAY_MODE_BANNER = "banner"
DISPLAY_MODE_TEXT = "text"

DISPLAY_MODE_DEFAULT = DISPLAY_MODE_MIXED
DISPLAY_MODE_CHOICES = (
    (DISPLAY_MODE_MIXED, "Banner + texto"),
    (DISPLAY_MODE_BANNER, "Solo banner"),
    (DISPLAY_MODE_TEXT, "Solo texto"),
)
DISPLAY_MODE_VALUES = {
    DISPLAY_MODE_MIXED,
    DISPLAY_MODE_BANNER,
    DISPLAY_MODE_TEXT,
}

BANNER_MAX_BYTES = 2 * 1024 * 1024
ALLOWED_BANNER_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}
ALLOWED_BANNER_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
}


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_multiline_text(value):
    return (
        str(value or "")
        .replace("\r\n", "\n")
        .strip()
    )


def _safe_int(value, fallback):
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return int(fallback)


def _norm_display_mode(value):
    normalized = _norm_text(value).lower()

    if normalized in DISPLAY_MODE_VALUES:
        return normalized

    return DISPLAY_MODE_DEFAULT


def _delete_storage_file(field_file):
    if not field_file:
        return

    name = getattr(field_file, "name", None)
    storage = getattr(field_file, "storage", None)

    if not name or storage is None:
        return

    try:
        if storage.exists(name):
            storage.delete(name)
    except (OSError, ValueError):
        return


def banner_upload_to(instance, filename):
    filename = filename or "banner.jpg"
    base, extension = os.path.splitext(filename)

    extension = extension.lower()

    if extension not in ALLOWED_BANNER_EXTENSIONS:
        extension = ".jpg"

    safe_base = (
        _norm_text(base)
        or "banner"
    )[:80]

    return f"banners/{safe_base}{extension}"


class Banner(models.Model):
    title = models.CharField(
        max_length=220,
        blank=True,
        default="",
        verbose_name="Título del aviso",
    )

    eyebrow = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name="Etiqueta superior",
    )

    text = models.TextField(
        blank=True,
        default="",
        verbose_name="Mensaje del aviso",
    )

    recent_label = models.CharField(
        max_length=60,
        blank=True,
        default="",
        verbose_name="Etiqueta de actualización",
    )

    image = models.ImageField(
        upload_to=banner_upload_to,
        max_length=255,
        verbose_name="Imagen",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado en",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizado en",
    )

    class Meta:
        db_table = "banners"
        ordering = ["-created_at", "-id"]
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

    def clean(self):
        super().clean()

        errors = {}

        self.title = _norm_optional_text(
            self.title
        ) or ""
        self.eyebrow = _norm_optional_text(
            self.eyebrow
        ) or ""
        self.text = _norm_multiline_text(
            self.text
        )
        self.recent_label = _norm_optional_text(
            self.recent_label
        ) or ""

        if not self.image:
            errors["image"] = (
                "La imagen del banner es obligatoria."
            )
        else:
            file_name = _norm_text(
                getattr(self.image, "name", "")
            ).lower()

            extension = os.path.splitext(
                file_name
            )[1]

            if extension not in ALLOWED_BANNER_EXTENSIONS:
                errors["image"] = (
                    "Solo se permiten imágenes JPG o PNG."
                )

            content_type = (
                getattr(
                    self.image,
                    "content_type",
                    None,
                )
                or getattr(
                    getattr(
                        self.image,
                        "file",
                        None,
                    ),
                    "content_type",
                    None,
                )
            )

            if (
                content_type
                and str(content_type).lower()
                not in ALLOWED_BANNER_CONTENT_TYPES
            ):
                errors["image"] = (
                    "Solo se permiten imágenes JPG o PNG."
                )

            try:
                file_size = int(
                    getattr(
                        self.image,
                        "size",
                        0,
                    )
                    or 0
                )
            except (TypeError, ValueError):
                file_size = 0

            if file_size <= 0:
                errors["image"] = (
                    "La imagen del banner está vacía."
                )

            if file_size > BANNER_MAX_BYTES:
                errors["image"] = (
                    "La imagen del banner supera "
                    "el tamaño máximo de 2 MB."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        old_image = None

        if self.pk:
            try:
                old_image = (
                    Banner.objects
                    .only("image")
                    .get(pk=self.pk)
                    .image
                )
            except Banner.DoesNotExist:
                old_image = None

        self.full_clean()

        result = super().save(
            *args,
            **kwargs,
        )

        old_name = getattr(
            old_image,
            "name",
            None,
        )
        new_name = getattr(
            self.image,
            "name",
            None,
        )

        if old_name and old_name != new_name:
            _delete_storage_file(old_image)

        return result

    def delete(self, *args, **kwargs):
        image_to_delete = self.image

        result = super().delete(
            *args,
            **kwargs,
        )

        _delete_storage_file(image_to_delete)

        return result

    def __str__(self):
        return (
            _norm_text(self.title)
            or f"Banner #{self.pk}"
        )


class BannerConfiguracion(models.Model):
    singleton_key = models.PositiveSmallIntegerField(
        default=1,
        unique=True,
        editable=False,
    )

    eyebrow = models.CharField(
        max_length=60,
        default=DEFAULT_BANNER_EYEBROW,
    )

    title = models.CharField(
        max_length=220,
        default=DEFAULT_BANNER_TITLE,
    )

    text = models.TextField(
        default=DEFAULT_BANNER_TEXT,
    )

    recent_label = models.CharField(
        max_length=60,
        default=DEFAULT_BANNER_RECENT_LABEL,
    )

    stage_width = models.PositiveIntegerField(
        default=STAGE_WIDTH_DEFAULT,
    )

    stage_height = models.PositiveIntegerField(
        default=STAGE_HEIGHT_DEFAULT,
    )

    media_pane_width = models.PositiveIntegerField(
        default=MEDIA_PANE_WIDTH_DEFAULT,
    )

    display_mode = models.CharField(
        max_length=16,
        choices=DISPLAY_MODE_CHOICES,
        default=DISPLAY_MODE_DEFAULT,
        verbose_name="Modo de visualización",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "banner_configuracion"
        ordering = ["singleton_key"]
        verbose_name = "Configuración global de banners"
        verbose_name_plural = (
            "Configuración global de banners"
        )

    @classmethod
    def get_solo(cls):
        obj, _created = (
            cls.objects.get_or_create(
                singleton_key=1
            )
        )

        return obj

    def clean(self):
        super().clean()

        errors = {}

        self.singleton_key = 1
        self.eyebrow = (
            _norm_optional_text(self.eyebrow)
            or DEFAULT_BANNER_EYEBROW
        )
        self.title = (
            _norm_optional_text(self.title)
            or DEFAULT_BANNER_TITLE
        )
        self.text = (
            _norm_multiline_text(self.text)
            or DEFAULT_BANNER_TEXT
        )
        self.recent_label = (
            _norm_optional_text(
                self.recent_label
            )
            or DEFAULT_BANNER_RECENT_LABEL
        )
        self.display_mode = _norm_display_mode(
            self.display_mode
        )

        self.stage_width = _safe_int(
            self.stage_width,
            STAGE_WIDTH_DEFAULT,
        )
        self.stage_height = _safe_int(
            self.stage_height,
            STAGE_HEIGHT_DEFAULT,
        )
        self.media_pane_width = _safe_int(
            self.media_pane_width,
            MEDIA_PANE_WIDTH_DEFAULT,
        )

        if not (
            STAGE_WIDTH_MIN
            <= self.stage_width
            <= STAGE_WIDTH_MAX
        ):
            errors["stage_width"] = (
                f"El ancho debe estar entre "
                f"{STAGE_WIDTH_MIN} y "
                f"{STAGE_WIDTH_MAX}px."
            )

        if not (
            STAGE_HEIGHT_MIN
            <= self.stage_height
            <= STAGE_HEIGHT_MAX
        ):
            errors["stage_height"] = (
                f"La altura debe estar entre "
                f"{STAGE_HEIGHT_MIN} y "
                f"{STAGE_HEIGHT_MAX}px."
            )

        media_max = max(
            MEDIA_PANE_WIDTH_MIN,
            self.stage_width
            - ASIDE_WIDTH_MIN
            - SPLITTER_WIDTH,
        )

        if not (
            MEDIA_PANE_WIDTH_MIN
            <= self.media_pane_width
            <= media_max
        ):
            errors["media_pane_width"] = (
                "El ancho del panel visual no es "
                "válido para el contenedor actual."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.singleton_key = 1
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "La configuración global no puede eliminarse."
        )

    def __str__(self):
        return "Configuración global de banners"
