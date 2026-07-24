from django.core.exceptions import ValidationError
from django.db import models


def _norm_optional_text(value):
    value = str(value or "").strip()
    return value or None


class MicrosoftMappingRule(models.Model):
    department_contains = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    job_title_contains = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    office_location_contains = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    carrera = models.ForeignKey(
        "core.Carrera",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reglas_microsoft",
    )

    prioridad = models.PositiveIntegerField(
        default=1,
    )

    activo = models.BooleanField(
        default=True,
    )

    class Meta:
        db_table = "microsoft_mapping_rules"
        ordering = ["-prioridad", "id"]
        indexes = [
            models.Index(fields=["activo"]),
            models.Index(fields=["prioridad"]),
            models.Index(fields=["activo", "prioridad"]),
        ]

    @property
    def facultad(self):
        if not self.carrera_id:
            return None

        return self.carrera.facultad

    def clean(self):
        super().clean()

        errors = {}

        self.department_contains = _norm_optional_text(
            self.department_contains
        )
        self.job_title_contains = _norm_optional_text(
            self.job_title_contains
        )
        self.office_location_contains = _norm_optional_text(
            self.office_location_contains
        )

        if not any(
            [
                self.department_contains,
                self.job_title_contains,
                self.office_location_contains,
            ]
        ):
            errors["department_contains"] = (
                "Debe definir al menos una condición "
                "de coincidencia."
            )

        if self.prioridad is None or self.prioridad < 1:
            errors["prioridad"] = (
                "La prioridad debe ser mayor o igual a 1."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        parts = []

        if self.department_contains:
            parts.append(
                f"department~{self.department_contains}"
            )

        if self.job_title_contains:
            parts.append(
                f"job~{self.job_title_contains}"
            )

        if self.office_location_contains:
            parts.append(
                f"office~{self.office_location_contains}"
            )

        criteria = (
            " | ".join(parts)
            if parts
            else "sin criterio"
        )

        return (
            f"Regla {self.pk or 'nueva'} "
            f"(prio {self.prioridad}) - {criteria}"
        )
