from django.core.exceptions import ValidationError
from django.db import models


def _norm_text(value):
    return str(value or "").strip()


class AreaConocimiento(models.Model):
    # Nombre único del área de conocimiento (ej. Ciencias de la Computación).
    nombre = models.CharField(max_length=150, unique=True)

    class Meta:
        db_table = "areas_conocimiento"
        ordering = ["nombre"]

    def clean(self):
        self.nombre = _norm_text(self.nombre)

        if not self.nombre:
            raise ValidationError({"nombre": "El nombre del área es obligatorio."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Subarea(models.Model):
    # Nombre de la subárea de conocimiento.
    nombre = models.CharField(max_length=150)

    # Área principal a la que pertenece la subárea.
    area = models.ForeignKey(
        AreaConocimiento,
        on_delete=models.CASCADE,
        related_name="subareas"
    )

    class Meta:
        db_table = "subareas_conocimiento"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "area"],
                name="unique_subarea_por_area",
            )
        ]
        indexes = [
            models.Index(fields=["area", "nombre"]),
        ]

    def clean(self):
        errors = {}

        self.nombre = _norm_text(self.nombre)

        if not self.nombre:
            errors["nombre"] = "El nombre de la subárea es obligatorio."

        if not self.area_id:
            errors["area"] = "El área es obligatoria."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.area.nombre})"