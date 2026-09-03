"""
Notificaciones internas del SGPC.

Las notificaciones se generan como consecuencia de eventos del
flujo de publicaciones. El registro interno se guarda dentro de la
transacción principal; el correo se intenta después del COMMIT para
que un fallo SMTP nunca revierta una aprobación, observación,
rechazo, envío o reenvío ya confirmado.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def _norm_optional_text(
    value,
):
    value = str(
        value
        or ""
    ).strip()

    return (
        value
        or None
    )


class Notificacion(models.Model):
    TIPO_PUBLICACION_ENVIADA = (
        "publicacion_enviada"
    )

    TIPO_PUBLICACION_OBSERVADA = (
        "publicacion_observada"
    )

    TIPO_PUBLICACION_APROBADA = (
        "publicacion_aprobada"
    )

    TIPO_PUBLICACION_RECHAZADA = (
        "publicacion_rechazada"
    )

    TIPO_NUEVA_PUBLICACION_REVISION = (
        "nueva_publicacion_revision"
    )

    TIPO_PUBLICACION_REENVIADA = (
        "publicacion_reenviada"
    )

    TIPO_SOLICITUD_EXTENSION_PERFIL = (
        "solicitud_extension_perfil"
    )

    TIPO_EXTENSION_PERFIL_APROBADA = (
        "extension_perfil_aprobada"
    )

    TIPO_EXTENSION_PERFIL_RECHAZADA = (
        "extension_perfil_rechazada"
    )

    TIPO_CAMPANIA_ACTUALIZACION = (
        "campania_actualizacion"
    )

    TIPO_RECORDATORIO_ACTUALIZACION = (
        "recordatorio_actualizacion"
    )

    TIPO_SOLICITUD_MODIFICACION_PUBLICACION = (
        "solicitud_modificacion_publicacion"
    )

    TIPO_MODIFICACION_PUBLICACION_APROBADA = (
        "modificacion_publicacion_aprobada"
    )

    TIPO_MODIFICACION_PUBLICACION_RECHAZADA = (
        "modificacion_publicacion_rechazada"
    )

    TIPOS = [
        (
            TIPO_PUBLICACION_ENVIADA,
            "Publicación enviada",
        ),
        (
            TIPO_PUBLICACION_OBSERVADA,
            "Publicación observada",
        ),
        (
            TIPO_PUBLICACION_APROBADA,
            "Publicación aprobada",
        ),
        (
            TIPO_PUBLICACION_RECHAZADA,
            "Publicación rechazada",
        ),
        (
            TIPO_NUEVA_PUBLICACION_REVISION,
            "Nueva publicación para revisar",
        ),
        (
            TIPO_PUBLICACION_REENVIADA,
            "Publicación corregida y reenviada",
        ),
        (
            TIPO_SOLICITUD_EXTENSION_PERFIL,
            "Solicitud de extensión de perfil",
        ),
        (
            TIPO_EXTENSION_PERFIL_APROBADA,
            "Extensión de perfil aprobada",
        ),
        (
            TIPO_EXTENSION_PERFIL_RECHAZADA,
            "Extensión de perfil rechazada",
        ),
        (
            TIPO_CAMPANIA_ACTUALIZACION,
            "Actualización de información requerida",
        ),
        (
            TIPO_RECORDATORIO_ACTUALIZACION,
            "Recordatorio de actualización",
        ),
        (
            TIPO_SOLICITUD_MODIFICACION_PUBLICACION,
            "Solicitud de modificación de publicación",
        ),
        (
            TIPO_MODIFICACION_PUBLICACION_APROBADA,
            "Modificación de publicación aprobada",
        ),
        (
            TIPO_MODIFICACION_PUBLICACION_RECHAZADA,
            "Modificación de publicación rechazada",
        ),
    ]

    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )

    tipo = models.CharField(
        max_length=40,
        choices=TIPOS,
        db_index=True,
    )

    titulo = models.CharField(
        max_length=200,
    )

    mensaje = models.TextField()

    publicacion = models.ForeignKey(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="notificaciones",
        null=True,
        blank=True,
    )

    leida = models.BooleanField(
        default=False,
        db_index=True,
    )

    visible_en_bandeja = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Permite conservar el registro de envío de correo sin mostrar "
            "una notificación interna cuando la campaña solo usa email."
        ),
    )

    leida_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    email_programado = models.BooleanField(
        default=False,
    )

    email_enviado = models.BooleanField(
        default=False,
        db_index=True,
    )

    email_intentado_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    email_error = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        db_table = "notificaciones"
        ordering = [
            "-created_at",
            "-id",
        ]
        indexes = [
            models.Index(
                fields=[
                    "destinatario",
                    "leida",
                    "created_at",
                ],
                name="notif_dest_leida_fecha_idx",
            ),
            models.Index(
                fields=[
                    "tipo",
                    "created_at",
                ],
                name="notif_tipo_fecha_idx",
            ),
        ]

    def clean(
        self,
    ):
        super().clean()

        errors = {}

        self.tipo = str(
            self.tipo
            or ""
        ).strip().lower()

        self.titulo = str(
            self.titulo
            or ""
        ).strip()

        self.mensaje = str(
            self.mensaje
            or ""
        ).strip()

        self.email_error = (
            _norm_optional_text(
                self.email_error
            )
        )

        if self.metadata is None:
            self.metadata = {}

        valid_types = {
            value
            for value, _label
            in self.TIPOS
        }

        if not self.destinatario_id:
            errors[
                "destinatario"
            ] = (
                "El destinatario es obligatorio."
            )

        if self.tipo not in valid_types:
            errors[
                "tipo"
            ] = (
                "El tipo de notificación es inválido."
            )

        if not self.titulo:
            errors[
                "titulo"
            ] = (
                "El título es obligatorio."
            )

        if not self.mensaje:
            errors[
                "mensaje"
            ] = (
                "El mensaje es obligatorio."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            errors[
                "metadata"
            ] = (
                "Los metadatos deben ser un objeto JSON."
            )

        if (
            self.email_enviado
            and not self.email_programado
        ):
            errors[
                "email_enviado"
            ] = (
                "Un correo no puede figurar como enviado "
                "si no fue programado."
            )

        if errors:
            raise ValidationError(
                errors
            )

    def save(
        self,
        *args,
        **kwargs,
    ):
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def __str__(
        self,
    ):
        return (
            f"{self.destinatario_id} · "
            f"{self.get_tipo_display()} · "
            f"{self.created_at or 'sin fecha'}"
        )


class SolicitudExtensionPerfil(models.Model):
    """Solicitud persistente para ampliar el plazo de edición del perfil."""

    ESTADO_PENDIENTE = "pendiente"
    ESTADO_APROBADA = "aprobada"
    ESTADO_RECHAZADA = "rechazada"

    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_APROBADA, "Aprobada"),
        (ESTADO_RECHAZADA, "Rechazada"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitudes_extension_perfil",
    )

    horas_solicitadas = models.PositiveSmallIntegerField()
    horas_aprobadas = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    motivo = models.TextField()

    estado = models.CharField(
        max_length=16,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        db_index=True,
    )

    plazo_anterior = models.DateTimeField(
        null=True,
        blank=True,
    )
    nuevo_plazo = models.DateTimeField(
        null=True,
        blank=True,
    )

    solicitada_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    resuelta_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    resuelta_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_extension_perfil_resueltas",
    )
    motivo_resolucion = models.TextField(
        blank=True,
        default="",
    )
    ip_solicitud = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "solicitudes_extension_perfil"
        ordering = ["-solicitada_at", "-id"]
        indexes = [
            models.Index(
                fields=["estado", "solicitada_at"],
                name="sol_ext_estado_fecha_idx",
            ),
            models.Index(
                fields=["usuario", "solicitada_at"],
                name="sol_ext_usuario_fecha_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario"],
                condition=models.Q(estado="pendiente"),
                name="uniq_sol_ext_pendiente_usuario",
            ),
            models.CheckConstraint(
                check=models.Q(horas_solicitadas__gt=0),
                name="sol_ext_horas_mayor_cero",
            ),
        ]

    def clean(self):
        super().clean()

        self.motivo = str(self.motivo or "").strip()
        self.motivo_resolucion = str(
            self.motivo_resolucion or ""
        ).strip()

        errors = {}
        if not self.motivo:
            errors["motivo"] = "El motivo es obligatorio."
        elif len(self.motivo) < 20:
            errors["motivo"] = (
                "El motivo debe contener al menos 20 caracteres."
            )
        elif len(self.motivo) > 1000:
            errors["motivo"] = (
                "El motivo no puede superar 1000 caracteres."
            )

        if self.horas_solicitadas not in {24, 48, 72}:
            errors["horas_solicitadas"] = (
                "Seleccione 24, 48 o 72 horas."
            )

        if (
            self.horas_aprobadas is not None
            and self.horas_aprobadas not in {6, 12, 24, 48, 72}
        ):
            errors["horas_aprobadas"] = (
                "Seleccione 6, 12, 24, 48 o 72 horas."
            )

        if self.estado not in {
            self.ESTADO_PENDIENTE,
            self.ESTADO_APROBADA,
            self.ESTADO_RECHAZADA,
        }:
            errors["estado"] = "El estado de la solicitud no es válido."

        if (
            self.estado == self.ESTADO_RECHAZADA
            and not self.motivo_resolucion
        ):
            errors["motivo_resolucion"] = (
                "Indique el motivo del rechazo."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Solicitud {self.pk or '-'} · usuario {self.usuario_id} · "
            f"{self.get_estado_display()}"
        )
