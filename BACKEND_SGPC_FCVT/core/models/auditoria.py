"""Registro general e inmutable de auditoría del SGPC."""

from django.conf import settings
from django.db import models


class AuditoriaSistema(models.Model):
    ACCION_CREAR = "crear"
    ACCION_ACTUALIZAR = "actualizar"
    ACCION_ELIMINAR = "eliminar"
    ACCION_ACTIVAR = "activar"
    ACCION_FINALIZAR = "finalizar"
    ACCION_CANCELAR = "cancelar"
    ACCION_LOGIN = "login"
    ACCION_LOGOUT = "logout"
    ACCION_APROBAR = "aprobar"
    ACCION_RECHAZAR = "rechazar"
    ACCION_OBSERVAR = "observar"
    ACCION_ENVIAR = "enviar"
    ACCION_EXPORTAR = "exportar"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_auditoria",
    )

    accion = models.CharField(max_length=60, db_index=True)
    modulo = models.CharField(max_length=80, db_index=True)

    entidad_tipo = models.CharField(max_length=100, blank=True, default="")
    entidad_id = models.CharField(max_length=80, blank=True, default="", db_index=True)

    descripcion = models.TextField(blank=True, default="")

    datos_anteriores = models.JSONField(default=dict, blank=True)
    datos_nuevos = models.JSONField(default=dict, blank=True)
    contexto = models.JSONField(default=dict, blank=True)

    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default="")
    ruta = models.CharField(max_length=500, blank=True, default="")
    metodo_http = models.CharField(max_length=12, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "auditoria_sistema"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["modulo", "accion", "created_at"],
                name="audit_mod_acc_fecha_idx",
            ),
            models.Index(
                fields=["actor", "created_at"],
                name="audit_actor_fecha_idx",
            ),
            models.Index(
                fields=["entidad_tipo", "entidad_id"],
                name="audit_entidad_idx",
            ),
        ]

    def save(self, *args, **kwargs):
        # Los eventos existentes son deliberadamente inmutables.
        if self.pk:
            raise ValueError("Los registros de auditoría no pueden modificarse.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Los registros de auditoría no pueden eliminarse.")

    def __str__(self):
        return f"{self.created_at} · {self.modulo} · {self.accion}"
