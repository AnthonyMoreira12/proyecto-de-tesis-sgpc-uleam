import os
import magic  # <-- IMPORTANTE PARA LA SEGURIDAD
from django.core.exceptions import ValidationError
from django.db import models


MAX_ADJUNTO_PDF_BYTES = 3 * 1024 * 1024  # 3 MB
MAX_ADJUNTOS_POR_PUBLICACION = 2
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_PDF_CONTENT_TYPES = {"application/pdf"}


def _norm_text(value):
    return str(value or "").strip()


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


def publicacion_archivo_upload_path(instance, filename):
    return os.path.join(
        "publicaciones",
        "adjuntos",
        str(instance.publicacion_id),
        filename,
    )


class PublicacionArchivo(models.Model):
    publicacion = models.ForeignKey(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="archivos",
    )

    nombre = models.CharField(max_length=150)
    archivo = models.FileField(upload_to=publicacion_archivo_upload_path)
    orden = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "publicaciones_archivos"
        ordering = ["orden", "id"]
        indexes = [
            models.Index(fields=["publicacion"]),
        ]

    def clean(self):
        errors = {}

        self.nombre = _norm_text(self.nombre)

        if not self.nombre:
            errors["nombre"] = "El nombre del archivo es obligatorio."

        if not self.archivo:
            errors["archivo"] = "Debe adjuntar un archivo."
        else:
            file_name = str(getattr(self.archivo, "name", "") or "").lower()
            ext = os.path.splitext(file_name)[1]

            if ext not in ALLOWED_PDF_EXTENSIONS:
                errors["archivo"] = "Solo se permiten archivos PDF."

            content_type = (
                getattr(self.archivo, "content_type", None)
                or getattr(getattr(self.archivo, "file", None), "content_type", None)
            )
            if content_type and content_type not in ALLOWED_PDF_CONTENT_TYPES:
                errors["archivo"] = "Solo se permiten archivos PDF."

            file_size = int(getattr(self.archivo, "size", 0) or 0)
            if file_size > MAX_ADJUNTO_PDF_BYTES:
                errors["archivo"] = "El archivo adjunto supera el tamaño máximo de 3 MB."

            # ============================================================
            # VALIDACIÓN ESTRICTA DE BYTES MÁGICOS (SEGURIDAD)
            # ============================================================
            if "archivo" not in errors:
                try:
                    # magic lee los primeros bytes y determina el formato real
                    file_mime = magic.from_buffer(self.archivo.read(2048), mime=True)
                    if file_mime != "application/pdf":
                        errors["archivo"] = "El archivo adjunto no es un PDF válido (Firma MIME incorrecta)."
                    
                    # Reiniciamos el cursor de lectura para que Django pueda guardarlo
                    self.archivo.seek(0)
                except Exception as e:
                    errors["archivo"] = f"Error al validar los bytes del archivo: {str(e)}"

        if self.orden is None or self.orden < 1:
            errors["orden"] = "El orden debe ser mayor o igual a 1."

        if self.publicacion_id:
            qs = PublicacionArchivo.objects.filter(publicacion_id=self.publicacion_id)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.count() >= MAX_ADJUNTOS_POR_PUBLICACION and not self.pk:
                errors["archivo"] = (
                    f"Solo se permiten {MAX_ADJUNTOS_POR_PUBLICACION} adjuntos "
                    "por publicación."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        old_file = None

        if self.pk:
            try:
                old_file = (
                    PublicacionArchivo.objects.only("archivo")
                    .get(pk=self.pk)
                    .archivo
                )
            except PublicacionArchivo.DoesNotExist:
                old_file = None

        self.full_clean()
        result = super().save(*args, **kwargs)

        old_name = getattr(old_file, "name", None)
        new_name = getattr(self.archivo, "name", None)

        if old_name and old_name != new_name:
            _delete_storage_file(old_file)

        return result

    def delete(self, *args, **kwargs):
        file_to_delete = self.archivo
        result = super().delete(*args, **kwargs)
        _delete_storage_file(file_to_delete)
        return result

    def __str__(self):
        return f"{self.nombre} (Pub #{self.publicacion_id})"