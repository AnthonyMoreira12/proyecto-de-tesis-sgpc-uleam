"""
Modelo de revisión administrativa de publicaciones.

Cada registro representa una decisión formal tomada por un
administrador sobre una publicación que se encontraba En revisión.

La auditoría general del sistema se implementará posteriormente en
una fase independiente. Este modelo conserva específicamente la
decisión científica/administrativa y su comentario.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .base import Publicacion


def _norm_optional_text(value):
    value = str(value or "").strip()
    return value or None


class PublicacionRevision(models.Model):
    DECISION_OBSERVADA = "observada"
    DECISION_APROBADA = "aprobada"
    DECISION_RECHAZADA = "rechazada"

    DECISIONES = [
        (
            DECISION_OBSERVADA,
            "Observada",
        ),
        (
            DECISION_APROBADA,
            "Aprobada",
        ),
        (
            DECISION_RECHAZADA,
            "Rechazada",
        ),
    ]

    publicacion = models.ForeignKey(
        "core.Publicacion",
        on_delete=models.PROTECT,
        related_name="revisiones",
    )

    revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="revisiones_publicaciones_realizadas",
    )

    decision = models.CharField(
        max_length=20,
        choices=DECISIONES,
        db_index=True,
    )

    comentario = models.TextField(
        null=True,
        blank=True,
    )

    estado_anterior = models.CharField(
        max_length=20,
        choices=Publicacion.ESTADOS,
    )

    estado_resultante = models.CharField(
        max_length=20,
        choices=Publicacion.ESTADOS,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        db_table = "publicaciones_revisiones"
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
                name="pubrev_pub_fecha_idx",
            ),
            models.Index(
                fields=[
                    "decision",
                    "created_at",
                ],
                name="pubrev_dec_fecha_idx",
            ),
            models.Index(
                fields=[
                    "revisor",
                    "created_at",
                ],
                name="pubrev_rev_fecha_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.decision = str(
            self.decision
            or ""
        ).strip().lower()

        self.estado_anterior = str(
            self.estado_anterior
            or ""
        ).strip().lower()

        self.estado_resultante = str(
            self.estado_resultante
            or ""
        ).strip().lower()

        self.comentario = _norm_optional_text(
            self.comentario
        )

        valid_decisions = {
            value
            for value, _label
            in self.DECISIONES
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

        if not self.revisor_id:
            errors["revisor"] = (
                "El revisor es obligatorio."
            )
        else:
            reviewer = self.revisor

            if not (
                getattr(
                    reviewer,
                    "is_staff",
                    False,
                )
                or getattr(
                    reviewer,
                    "is_superuser",
                    False,
                )
            ):
                errors["revisor"] = (
                    "El revisor debe tener privilegios "
                    "administrativos."
                )

        if self.decision not in valid_decisions:
            errors["decision"] = (
                "La decisión de revisión es inválida."
            )

        if self.estado_anterior not in valid_states:
            errors["estado_anterior"] = (
                "El estado anterior es inválido."
            )

        if self.estado_resultante not in valid_states:
            errors["estado_resultante"] = (
                "El estado resultante es inválido."
            )

        # Las decisiones formales de esta fase nacen siempre desde
        # una publicación En revisión.
        if (
            self.estado_anterior
            and self.estado_anterior
            != Publicacion.ESTADO_EN_REVISION
        ):
            errors["estado_anterior"] = (
                "Una decisión de revisión formal solo puede "
                "registrarse desde el estado En revisión."
            )

        expected_result_states = {
            self.DECISION_OBSERVADA: (
                Publicacion.ESTADO_OBSERVADA
            ),
            self.DECISION_APROBADA: (
                Publicacion.ESTADO_APROBADA
            ),
            self.DECISION_RECHAZADA: (
                Publicacion.ESTADO_RECHAZADA
            ),
        }

        expected_state = (
            expected_result_states.get(
                self.decision
            )
        )

        if (
            expected_state
            and self.estado_resultante
            != expected_state
        ):
            errors["estado_resultante"] = (
                "El estado resultante no corresponde con "
                "la decisión de revisión."
            )

        if (
            self.decision
            in {
                self.DECISION_OBSERVADA,
                self.DECISION_RECHAZADA,
            }
            and not self.comentario
        ):
            errors["comentario"] = (
                "Debe registrar un comentario o motivo "
                "para observar o rechazar la publicación."
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
            f"{self.get_decision_display()} · "
            f"{self.created_at or 'sin fecha'}"
        )