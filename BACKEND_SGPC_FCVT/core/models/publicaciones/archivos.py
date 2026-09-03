import hashlib
import os
import re
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import get_valid_filename


MAX_ADJUNTO_PDF_BYTES = 3 * 1024 * 1024
MAX_ADJUNTOS_POR_PUBLICACION = 2

ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}

PDF_SIGNATURE = b"%PDF-"
PDF_SIGNATURE_SCAN_BYTES = 1024
PDF_TRAILER = b"%%EOF"
PDF_TRAILER_SCAN_BYTES = 4096


def _norm_text(value):
    return str(value or "").strip()


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


def _read_header(
    field_file,
    max_bytes=PDF_SIGNATURE_SCAN_BYTES,
):
    file_obj = getattr(
        field_file,
        "file",
        field_file,
    )

    if (
        file_obj is None
        or not hasattr(file_obj, "read")
    ):
        return b""

    original_position = 0

    try:
        if hasattr(file_obj, "tell"):
            original_position = file_obj.tell()
    except (OSError, ValueError):
        original_position = 0

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        content = file_obj.read(max_bytes)

        if isinstance(content, str):
            content = content.encode(
                "utf-8",
                errors="ignore",
            )

        return bytes(content or b"")

    except (OSError, ValueError, TypeError):
        return b""

    finally:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(original_position)
        except (OSError, ValueError):
            pass


def _has_pdf_signature(field_file):
    header = _read_header(
        field_file,
        max_bytes=PDF_SIGNATURE_SCAN_BYTES,
    )

    if not header:
        return False

    return PDF_SIGNATURE in header


def _read_tail(
    field_file,
    max_bytes=4096,
):
    file_obj = getattr(
        field_file,
        "file",
        field_file,
    )

    if (
        file_obj is None
        or not hasattr(file_obj, "read")
        or not hasattr(file_obj, "seek")
    ):
        return b""

    original_position = 0

    try:
        if hasattr(file_obj, "tell"):
            original_position = file_obj.tell()
    except (OSError, ValueError):
        original_position = 0

    try:
        file_obj.seek(0, os.SEEK_END)
        total = file_obj.tell()
        start = max(0, int(total) - int(max_bytes))
        file_obj.seek(start)
        content = file_obj.read()

        if isinstance(content, str):
            content = content.encode(
                "utf-8",
                errors="ignore",
            )

        return bytes(content or b"")

    except (OSError, ValueError, TypeError):
        return b""

    finally:
        try:
            file_obj.seek(original_position)
        except (OSError, ValueError):
            pass


def _compute_sha256(field_file):
    file_obj = getattr(
        field_file,
        "file",
        field_file,
    )

    if (
        file_obj is None
        or not hasattr(file_obj, "read")
    ):
        return None

    original_position = 0

    try:
        if hasattr(file_obj, "tell"):
            original_position = file_obj.tell()
    except (OSError, ValueError):
        original_position = 0

    digest = hashlib.sha256()

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        while True:
            chunk = file_obj.read(64 * 1024)

            if not chunk:
                break

            if isinstance(chunk, str):
                chunk = chunk.encode(
                    "utf-8",
                    errors="ignore",
                )

            digest.update(bytes(chunk))

        return digest.hexdigest()

    except (OSError, ValueError, TypeError):
        return None

    finally:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(original_position)
        except (OSError, ValueError):
            pass


def _safe_original_filename(field_file):
    raw = os.path.basename(
        str(
            getattr(field_file, "name", "")
            or ""
        )
    )

    return raw[:255] or None


def publicacion_archivo_upload_path(
    instance,
    filename,
):
    _ = get_valid_filename(
        os.path.basename(
            str(filename or "archivo.pdf")
        )
    )

    return os.path.join(
        "publicaciones",
        "adjuntos",
        str(instance.publicacion_id or "tmp"),
        f"{uuid4().hex}.pdf",
    )



class PublicacionArchivo(models.Model):
    publicacion = models.ForeignKey(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="archivos",
    )

    nombre = models.CharField(
        max_length=150,
    )

    archivo = models.FileField(
        upload_to=publicacion_archivo_upload_path,
        max_length=255,
    )

    nombre_original = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        editable=False,
    )

    tamano_bytes = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    sha256 = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        editable=False,
    )

    orden = models.PositiveIntegerField(
        default=1,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "publicaciones_archivos"
        ordering = ["orden", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["publicacion", "orden"],
                name=(
                    "unique_archivo_orden_por_publicacion"
                ),
            ),
        ]
        indexes = [
            models.Index(
                fields=["publicacion"],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.nombre = _norm_text(self.nombre)

        if not self.nombre:
            errors["nombre"] = (
                "El nombre del archivo es obligatorio."
            )

        if not self.publicacion_id:
            errors["publicacion"] = (
                "La publicación es obligatoria."
            )

        if not self.archivo:
            errors["archivo"] = (
                "Debe adjuntar un archivo PDF."
            )
        else:
            file_name = _norm_text(
                getattr(
                    self.archivo,
                    "name",
                    "",
                )
            )

            extension = os.path.splitext(
                file_name.lower()
            )[1]

            if extension not in ALLOWED_PDF_EXTENSIONS:
                errors["archivo"] = (
                    "Solo se permiten archivos "
                    "con extensión PDF."
                )

            content_type = (
                getattr(
                    self.archivo,
                    "content_type",
                    None,
                )
                or getattr(
                    getattr(
                        self.archivo,
                        "file",
                        None,
                    ),
                    "content_type",
                    None,
                )
            )

            if (
                "archivo" not in errors
                and content_type
                and str(content_type).lower()
                not in ALLOWED_PDF_CONTENT_TYPES
            ):
                errors["archivo"] = (
                    "El tipo de contenido no corresponde "
                    "a un archivo PDF."
                )

            try:
                file_size = int(
                    getattr(
                        self.archivo,
                        "size",
                        0,
                    )
                    or 0
                )
            except (TypeError, ValueError):
                file_size = 0

            if (
                "archivo" not in errors
                and file_size <= 0
            ):
                errors["archivo"] = (
                    "El archivo PDF está vacío."
                )

            if (
                "archivo" not in errors
                and file_size > MAX_ADJUNTO_PDF_BYTES
            ):
                errors["archivo"] = (
                    "El archivo adjunto supera "
                    "el tamaño máximo de 3 MB."
                )

            if (
                "archivo" not in errors
                and not _has_pdf_signature(self.archivo)
            ):
                errors["archivo"] = (
                    "El archivo adjunto no contiene "
                    "una firma PDF válida."
                )

            tail = _read_tail(
                self.archivo,
                max_bytes=PDF_TRAILER_SCAN_BYTES,
            )

            if (
                "archivo" not in errors
                and (
                    not tail
                    or PDF_TRAILER not in tail
                )
            ):
                errors["archivo"] = (
                    "El archivo adjunto no contiene una estructura "
                    "PDF completa (marcador %%EOF ausente)."
                )

        if (
            self.sha256
            and not re.fullmatch(
                r"[0-9a-f]{64}",
                str(self.sha256).lower(),
            )
        ):
            errors["sha256"] = (
                "La huella SHA-256 del archivo no es válida."
            )

        if self.orden is None or self.orden < 1:
            errors["orden"] = (
                "El orden debe ser mayor o igual a 1."
            )

        if self.publicacion_id and not self.pk:
            current_count = (
                PublicacionArchivo.objects
                .filter(
                    publicacion_id=self.publicacion_id
                )
                .count()
            )

            if (
                current_count
                >= MAX_ADJUNTOS_POR_PUBLICACION
            ):
                errors["archivo"] = (
                    "Solo se permiten hasta "
                    f"{MAX_ADJUNTOS_POR_PUBLICACION} "
                    "archivos adjuntos por publicación."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        old_file = None

        if self.pk:
            try:
                old_file = (
                    PublicacionArchivo.objects
                    .only("archivo")
                    .get(pk=self.pk)
                    .archivo
                )
            except PublicacionArchivo.DoesNotExist:
                old_file = None

        old_name = getattr(
            old_file,
            "name",
            None,
        )

        current_name = getattr(
            self.archivo,
            "name",
            None,
        )

        file_changed = bool(
            self.archivo
        ) and (
            not self.pk
            or current_name != old_name
            or not self.sha256
        )

        if file_changed:
            self.nombre_original = (
                _safe_original_filename(
                    self.archivo
                )
            )

            try:
                self.tamano_bytes = int(
                    getattr(
                        self.archivo,
                        "size",
                        0,
                    )
                    or 0
                )
            except (TypeError, ValueError):
                self.tamano_bytes = None

            self.sha256 = _compute_sha256(
                self.archivo
            )

        self.full_clean()

        result = super().save(
            *args,
            **kwargs,
        )

        new_name = getattr(
            self.archivo,
            "name",
            None,
        )

        if old_name and old_name != new_name:
            _delete_storage_file(old_file)

        return result

    def delete(self, *args, **kwargs):
        file_to_delete = self.archivo

        result = super().delete(
            *args,
            **kwargs,
        )

        _delete_storage_file(file_to_delete)

        return result

    def __str__(self):
        return (
            f"{self.nombre} "
            f"(Pub #{self.publicacion_id})"
        )