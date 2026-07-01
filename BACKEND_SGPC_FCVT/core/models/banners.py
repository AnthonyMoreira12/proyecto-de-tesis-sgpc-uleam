from django.core.exceptions import ValidationError
from django.db import models
import os


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

BANNER_MAX_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_BANNER_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_BANNER_CONTENT_TYPES = {"image/jpeg", "image/png"}


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    return _norm_text(value)


def _norm_multiline_text(value):
    return str(value or "").replace("\r\n", "\n").strip()


def _safe_int(value, fallback):
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(fallback)


def _norm_display_mode(value):
    normalized = str(value or "").strip().lower()
    return normalized if normalized in DISPLAY_MODE_VALUES else DISPLAY_MODE_DEFAULT


def _delete_storage_file(field_file):
    if not field_file:
        return

    name = getattr(field_file, "name", None)
    storage = getattr(field_file, "storage", None)

    if not name or not storage:
        return

    try:
        if storage.exists(name):
            storage.delete(name)
    except Exception:
        pass


def banner_upload_to(instance, filename):
    filename = filename or "banner.jpg"
    base, ext = os.path.splitext(filename)
    ext = (ext or "").lower()

    if ext not in ALLOWED_BANNER_EXTENSIONS:
        ext = ".jpg"

    safe_base = (base or "banner").strip()[:80]
    return f"banners/{safe_base}{ext}"


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

    def __str__(self):
        titulo = _norm_text(self.title)
        return titulo or f"Banner #{self.pk}"

    def clean(self):
        super().clean()

        self.title = _norm_optional_text(self.title)
        self.eyebrow = _norm_optional_text(self.eyebrow)
        self.text = _norm_multiline_text(self.text)
        self.recent_label = _norm_optional_text(self.recent_label)

        if not self.image:
            raise ValidationError({"image": "La imagen del banner es obligatoria."})

        file_name = (getattr(self.image, "name", "") or "").lower()
        ext = os.path.splitext(file_name)[1]

        if ext not in ALLOWED_BANNER_EXTENSIONS:
            raise ValidationError({"image": "Solo se permiten imágenes JPG o PNG."})

        content_type = (
            getattr(self.image, "content_type", None)
            or getattr(getattr(self.image, "file", None), "content_type", None)
        )
        if content_type and content_type not in ALLOWED_BANNER_CONTENT_TYPES:
            raise ValidationError({"image": "Solo se permiten imágenes JPG o PNG."})

        file_size = int(getattr(self.image, "size", 0) or 0)
        if file_size > BANNER_MAX_BYTES:
            raise ValidationError(
                {"image": "La imagen del banner supera el tamaño máximo de 2 MB."}
            )

    def save(self, *args, **kwargs):
        old_image = None

        if self.pk:
            try:
                old_instance = Banner.objects.only("image").get(pk=self.pk)
                old_name = getattr(old_instance.image, "name", None)
                new_name = getattr(self.image, "name", None)

                if old_name and old_name != new_name:
                    old_image = old_instance.image
            except Banner.DoesNotExist:
                pass

        self.full_clean()
        super().save(*args, **kwargs)

        if old_image:
            _delete_storage_file(old_image)

    def delete(self, *args, **kwargs):
        image_file = self.image
        super().delete(*args, **kwargs)
        _delete_storage_file(image_file)


class BannerConfiguracion(models.Model):
    singleton_key = models.PositiveSmallIntegerField(
        default=1,
        unique=True,
        editable=False,
    )

    eyebrow = models.CharField(max_length=60, default=DEFAULT_BANNER_EYEBROW)
    title = models.CharField(max_length=220, default=DEFAULT_BANNER_TITLE)
    text = models.TextField(default=DEFAULT_BANNER_TEXT)
    recent_label = models.CharField(max_length=60, default=DEFAULT_BANNER_RECENT_LABEL)

    stage_width = models.PositiveIntegerField(default=STAGE_WIDTH_DEFAULT)
    stage_height = models.PositiveIntegerField(default=STAGE_HEIGHT_DEFAULT)
    media_pane_width = models.PositiveIntegerField(default=MEDIA_PANE_WIDTH_DEFAULT)
    display_mode = models.CharField(
        max_length=16,
        choices=DISPLAY_MODE_CHOICES,
        default=DISPLAY_MODE_DEFAULT,
        verbose_name="Modo de visualización",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "banner_configuracion"
        ordering = ["singleton_key"]
        verbose_name = "Configuración global de banners"
        verbose_name_plural = "Configuración global de banners"

    def __str__(self):
        return "Configuración global de banners"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(singleton_key=1)
        return obj

    def clean(self):
        super().clean()

        self.singleton_key = 1
        self.eyebrow = _norm_optional_text(self.eyebrow) or DEFAULT_BANNER_EYEBROW
        self.title = _norm_optional_text(self.title) or DEFAULT_BANNER_TITLE
        self.text = _norm_multiline_text(self.text) or DEFAULT_BANNER_TEXT
        self.recent_label = (
            _norm_optional_text(self.recent_label) or DEFAULT_BANNER_RECENT_LABEL
        )
        self.display_mode = _norm_display_mode(self.display_mode)

        self.stage_width = _safe_int(self.stage_width, STAGE_WIDTH_DEFAULT)
        self.stage_height = _safe_int(self.stage_height, STAGE_HEIGHT_DEFAULT)
        self.media_pane_width = _safe_int(
            self.media_pane_width,
            MEDIA_PANE_WIDTH_DEFAULT,
        )

        if not STAGE_WIDTH_MIN <= self.stage_width <= STAGE_WIDTH_MAX:
            raise ValidationError(
                {
                    "stage_width": (
                        f"El ancho debe estar entre {STAGE_WIDTH_MIN} y "
                        f"{STAGE_WIDTH_MAX}px."
                    )
                }
            )

        if not STAGE_HEIGHT_MIN <= self.stage_height <= STAGE_HEIGHT_MAX:
            raise ValidationError(
                {
                    "stage_height": (
                        f"La altura debe estar entre {STAGE_HEIGHT_MIN} y "
                        f"{STAGE_HEIGHT_MAX}px."
                    )
                }
            )

        media_max = max(
            MEDIA_PANE_WIDTH_MIN,
            self.stage_width - ASIDE_WIDTH_MIN - SPLITTER_WIDTH,
        )

        if not MEDIA_PANE_WIDTH_MIN <= self.media_pane_width <= media_max:
            raise ValidationError(
                {
                    "media_pane_width": (
                        "El ancho del panel visual no es válido para el tamaño "
                        "actual del contenedor."
                    )
                }
            )

        if self.display_mode not in DISPLAY_MODE_VALUES:
            raise ValidationError(
                {
                    "display_mode": "El modo de visualización no es válido."
                }
            )

    def save(self, *args, **kwargs):
        self.singleton_key = 1
        self.full_clean()
        return super().save(*args, **kwargs)