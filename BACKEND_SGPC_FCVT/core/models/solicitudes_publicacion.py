"""Solicitudes para modificar datos sensibles de publicaciones aprobadas."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class SolicitudModificacionPublicacion(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_APROBADA = "aprobada"
    ESTADO_RECHAZADA = "rechazada"
    ESTADO_CANCELADA = "cancelada"

    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_APROBADA, "Aprobada"),
        (ESTADO_RECHAZADA, "Rechazada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    publicacion = models.ForeignKey(
        "core.Publicacion",
        on_delete=models.PROTECT,
        related_name="solicitudes_modificacion",
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="solicitudes_modificacion_publicaciones",
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        db_index=True,
    )
    motivo = models.TextField()
    campos_solicitados = models.JSONField(default=list, blank=True)
    cambios_solicitados = models.JSONField(default=dict)
    datos_anteriores = models.JSONField(default=dict, blank=True)
    publicacion_updated_at_solicitud = models.DateTimeField()

    revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_modificacion_publicaciones_revisadas",
    )
    comentario_resolucion = models.TextField(null=True, blank=True)
    resuelto_at = models.DateTimeField(null=True, blank=True)
    aplicado_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "solicitudes_modificacion_publicaciones"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["estado", "created_at"],
                name="solmodpub_estado_fecha_idx",
            ),
            models.Index(
                fields=["publicacion", "created_at"],
                name="solmodpub_pub_fecha_idx",
            ),
            models.Index(
                fields=["solicitante", "created_at"],
                name="solmodpub_sol_fecha_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["publicacion", "solicitante"],
                condition=Q(estado="pendiente"),
                name="unique_solmodpub_pendiente_usuario",
            ),
        ]

    def clean(self):
        super().clean()
        self.motivo = str(self.motivo or "").strip()
        self.comentario_resolucion = (
            str(self.comentario_resolucion or "").strip() or None
        )

        errors = {}
        if not self.publicacion_id:
            errors["publicacion"] = "La publicación es obligatoria."
        if not self.solicitante_id:
            errors["solicitante"] = "El solicitante es obligatorio."
        if not self.motivo:
            errors["motivo"] = "Debe indicar el motivo de la solicitud."
        if not isinstance(self.campos_solicitados, list) or not self.campos_solicitados:
            errors["campos_solicitados"] = "Debe solicitar al menos un campo."
        if not isinstance(self.cambios_solicitados, dict) or not self.cambios_solicitados:
            errors["cambios_solicitados"] = "Debe indicar los cambios solicitados."
        if not isinstance(self.datos_anteriores, dict):
            errors["datos_anteriores"] = "Los datos anteriores deben ser un objeto JSON."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Solicitud #{self.pk or '-'} · publicación {self.publicacion_id} · {self.estado}"
