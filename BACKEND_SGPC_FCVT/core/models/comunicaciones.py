"""Comunicaciones globales del SGPC.

Este modelo complementa el carrusel visual de ``Banner`` con comunicados
textuales que no requieren una imagen. Puede utilizarse para mensajes
generales o quedar vinculado a una campaña de actualización, en cuyo caso
solo resulta visible para los participantes de esa campaña.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ComunicacionGlobal(models.Model):
    TIPO_INFORMACION = "informacion"
    TIPO_ACTUALIZACION = "actualizacion"
    TIPO_IMPORTANTE = "importante"
    TIPO_MANTENIMIENTO = "mantenimiento"

    TIPOS = [
        (TIPO_INFORMACION, "Información"),
        (TIPO_ACTUALIZACION, "Actualización del sistema"),
        (TIPO_IMPORTANTE, "Importante"),
        (TIPO_MANTENIMIENTO, "Mantenimiento"),
    ]

    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(
        max_length=24,
        choices=TIPOS,
        default=TIPO_INFORMACION,
        db_index=True,
    )

    campania = models.OneToOneField(
        "core.CampaniaActualizacion",
        on_delete=models.CASCADE,
        related_name="comunicacion_global",
        null=True,
        blank=True,
    )

    etiqueta_accion = models.CharField(max_length=80, blank=True, default="")
    ruta_accion = models.CharField(max_length=255, blank=True, default="")

    fecha_inicio = models.DateTimeField(null=True, blank=True, db_index=True)
    fecha_fin = models.DateTimeField(null=True, blank=True, db_index=True)
    activa = models.BooleanField(default=True, db_index=True)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comunicaciones_globales_creadas",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    desactivada_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "comunicaciones_globales"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["activa", "fecha_inicio", "fecha_fin"],
                name="com_global_vigencia_idx",
            ),
            models.Index(
                fields=["tipo", "created_at"],
                name="com_global_tipo_fecha_idx",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        self.titulo = str(self.titulo or "").strip()
        self.mensaje = str(self.mensaje or "").strip()
        self.etiqueta_accion = str(self.etiqueta_accion or "").strip()
        self.ruta_accion = str(self.ruta_accion or "").strip()

        if not self.titulo:
            errors["titulo"] = "El título de la comunicación es obligatorio."
        if not self.mensaje:
            errors["mensaje"] = "El mensaje de la comunicación es obligatorio."
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            errors["fecha_fin"] = (
                "La fecha de finalización debe ser posterior a la fecha de inicio."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def esta_vigente(self):
        if not self.activa:
            return False
        now = timezone.now()
        if self.fecha_inicio and self.fecha_inicio > now:
            return False
        if self.fecha_fin and self.fecha_fin <= now:
            return False
        return True

    def __str__(self):
        return self.titulo
