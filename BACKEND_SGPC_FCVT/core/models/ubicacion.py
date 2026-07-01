from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_upper(value):
    value = _norm_optional_text(value)
    return value.upper() if value else None


class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    # ISO-3166
    iso2 = models.CharField(max_length=2, null=True, blank=True, db_index=True)
    iso3 = models.CharField(max_length=3, null=True, blank=True, db_index=True)

    # GeoNames countryId (opcional)
    geoname_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "paises"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["iso2"]),
            models.Index(fields=["iso3"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["iso2"],
                name="unique_pais_iso2",
                condition=Q(iso2__isnull=False)
            ),
            models.UniqueConstraint(
                fields=["iso3"],
                name="unique_pais_iso3",
                condition=Q(iso3__isnull=False)
            ),
        ]

    def clean(self):
        errors = {}

        self.nombre = _norm_text(self.nombre)
        self.iso2 = _norm_upper(self.iso2)
        self.iso3 = _norm_upper(self.iso3)

        if not self.nombre:
            errors["nombre"] = "El nombre del país es obligatorio."

        if self.iso2 and len(self.iso2) != 2:
            errors["iso2"] = "El código ISO2 debe tener exactamente 2 caracteres."

        if self.iso3 and len(self.iso3) != 3:
            errors["iso3"] = "El código ISO3 debe tener exactamente 3 caracteres."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)

    pais = models.ForeignKey(
        Pais,
        on_delete=models.CASCADE,
        related_name="ciudades"
    )

    # GeoNames ID para evitar ambigüedades
    geoname_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    # Región/Provincia opcional
    admin1 = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        db_table = "ciudades"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["pais", "nombre"]),
            models.Index(fields=["geoname_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "pais"],
                name="unique_ciudad_por_pais",
            ),
            models.UniqueConstraint(
                fields=["pais", "geoname_id"],
                name="unique_ciudad_geoname_por_pais",
                condition=Q(geoname_id__isnull=False)
            )
        ]

    def clean(self):
        errors = {}

        self.nombre = _norm_text(self.nombre)
        self.admin1 = _norm_optional_text(self.admin1)

        if not self.nombre:
            errors["nombre"] = "El nombre de la ciudad es obligatorio."

        if not self.pais_id:
            errors["pais"] = "El país es obligatorio."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.pais.nombre})"