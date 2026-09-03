"""
Historial de auditoría de publicaciones.

Este modelo registra eventos relevantes del ciclo de gestión de una
publicación: creación, edición y transiciones de estado.

No sustituye a PublicacionRevision:
- PublicacionRevision conserva la decisión formal del revisor.
- PublicacionHistorial conserva la trazabilidad general de acciones.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import Publicacion


def _norm_optional_text(value):
    value = str(value or "").strip()
    return value or None


class PublicacionHistorial(models.Model):
    EVENTO_CREADA = "creada"
    EVENTO_EDITADA = "editada"
    EVENTO_ENVIADA_REVISION = "enviada_revision"
    EVENTO_OBSERVADA = "observada"
    EVENTO_APROBADA = "aprobada"
    EVENTO_RECHAZADA = "rechazada"
    EVENTO_REENVIADA_REVISION = "reenviada_revision"

    EVENTOS = [
        (
            EVENTO_CREADA,
            "Publicación creada",
        ),
        (
            EVENTO_EDITADA,
            "Publicación editada",
        ),
        (
            EVENTO_ENVIADA_REVISION,
            "Enviada a revisión",
        ),
        (
            EVENTO_OBSERVADA,
            "Publicación observada",
        ),
        (
            EVENTO_APROBADA,
            "Publicación aprobada",
        ),
        (
            EVENTO_RECHAZADA,
            "Publicación rechazada",
        ),
        (
            EVENTO_REENVIADA_REVISION,
            "Reenviada a revisión",
        ),
    ]

    publicacion = models.ForeignKey(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="historial",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historial_publicaciones_realizado",
    )

    actor_nombre = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    actor_email = models.EmailField(
        null=True,
        blank=True,
    )

    evento = models.CharField(
        max_length=30,
        choices=EVENTOS,
        db_index=True,
    )

    estado_anterior = models.CharField(
        max_length=20,
        choices=Publicacion.ESTADOS,
        null=True,
        blank=True,
    )

    estado_resultante = models.CharField(
        max_length=20,
        choices=Publicacion.ESTADOS,
        null=True,
        blank=True,
    )

    comentario = models.TextField(
        null=True,
        blank=True,
    )

    detalle = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        db_table = "publicaciones_historial"
        ordering = [
            "-created_at",
            "-id",
        ]
        indexes = [
            models.Index(
                fields=[
                    "publicacion",
                    "created_at",
                ],
                name="pubhist_pub_fecha_idx",
            ),
            models.Index(
                fields=[
                    "evento",
                    "created_at",
                ],
                name="pubhist_evt_fecha_idx",
            ),
            models.Index(
                fields=[
                    "actor",
                    "created_at",
                ],
                name="pubhist_act_fecha_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.evento = str(
            self.evento
            or ""
        ).strip().lower()

        self.estado_anterior = (
            str(
                self.estado_anterior
                or ""
            ).strip().lower()
            or None
        )

        self.estado_resultante = (
            str(
                self.estado_resultante
                or ""
            ).strip().lower()
            or None
        )

        self.actor_nombre = _norm_optional_text(
            self.actor_nombre
        )

        self.actor_email = _norm_optional_text(
            self.actor_email
        )

        self.comentario = _norm_optional_text(
            self.comentario
        )

        if self.detalle is None:
            self.detalle = {}

        valid_events = {
            value
            for value, _label
            in self.EVENTOS
        }

        valid_states = {
            value
            for value, _label
            in Publicacion.ESTADOS
        }

        if not self.publicacion_id:
            errors["publicacion"] = (
                "La publicación es obligatoria."
            )

        if self.evento not in valid_events:
            errors["evento"] = (
                "El evento de auditoría es inválido."
            )

        if (
            self.estado_anterior is not None
            and self.estado_anterior not in valid_states
        ):
            errors["estado_anterior"] = (
                "El estado anterior es inválido."
            )

        if (
            self.estado_resultante is not None
            and self.estado_resultante not in valid_states
        ):
            errors["estado_resultante"] = (
                "El estado resultante es inválido."
            )

        if not isinstance(
            self.detalle,
            dict,
        ):
            errors["detalle"] = (
                "El detalle de auditoría debe ser un objeto JSON."
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

    def __str__(self):
        return (
            f"Publicación {self.publicacion_id} · "
            f"{self.get_evento_display()} · "
            f"{self.created_at or 'sin fecha'}"
        )