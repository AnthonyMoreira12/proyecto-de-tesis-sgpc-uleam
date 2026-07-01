from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_email(value):
    value = _norm_text(value).lower()
    return value or None


class Autor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="autor",
    )

    identificacion = models.CharField(max_length=50, null=True, blank=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(max_length=150, null=True, blank=True)

    institucion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Institución a la que pertenece el autor.",
    )

    es_externo = models.BooleanField(default=False)

    publicaciones = models.ManyToManyField(
        "core.Publicacion",
        through="core.PublicacionAutor",
        related_name="autores",
        blank=True,
    )

    class Meta:
        db_table = "autores"
        ordering = ["apellidos", "nombres"]
        constraints = [
            models.UniqueConstraint(
                fields=["identificacion"],
                condition=Q(identificacion__isnull=False) & ~Q(identificacion=""),
                name="unique_autor_identificacion_no_vacia",
            ),
            models.UniqueConstraint(
                fields=["correo"],
                condition=Q(correo__isnull=False) & ~Q(correo=""),
                name="unique_autor_correo_no_vacio",
            ),
        ]
        indexes = [
            models.Index(fields=["apellidos", "nombres"]),
            models.Index(fields=["correo"]),
            models.Index(fields=["identificacion"]),
            models.Index(fields=["institucion"]),
        ]

    def clean(self):
        errors = {}

        self.identificacion = _norm_optional_text(self.identificacion)
        self.correo = _norm_email(self.correo)
        self.nombres = _norm_text(self.nombres)
        self.apellidos = _norm_text(self.apellidos)
        self.institucion = _norm_optional_text(self.institucion)

        if not self.nombres:
            errors["nombres"] = "Los nombres son obligatorios."

        if not self.apellidos:
            errors["apellidos"] = "Los apellidos son obligatorios."

        if not self.identificacion and not self.correo:
            errors["identificacion"] = (
                "Debe registrar al menos una identificación o un correo."
            )

        if self.institucion and len(self.institucion) > 255:
            errors["institucion"] = "La institución no puede superar 255 caracteres."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}".strip()


class PublicacionAutor(models.Model):
    ROL_AUTORIA = [
        ("principal", "Autor Principal"),
        ("coautor", "Coautor"),
    ]

    publicacion = models.ForeignKey(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="participaciones",
    )

    autor = models.ForeignKey(
        Autor,
        on_delete=models.CASCADE,
        related_name="participaciones",
    )

    rol_autoria = models.CharField(max_length=20, choices=ROL_AUTORIA)
    orden = models.PositiveIntegerField()

    class Meta:
        db_table = "publicaciones_autores"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["publicacion", "autor"],
                name="unique_autor_por_publicacion",
            ),
            models.UniqueConstraint(
                fields=["publicacion", "orden"],
                name="unique_orden_por_publicacion",
            ),
        ]
        indexes = [
            models.Index(fields=["publicacion", "rol_autoria"]),
            models.Index(fields=["autor"]),
        ]

    def clean(self):
        errors = {}

        if self.orden is None or self.orden < 1:
            errors["orden"] = "El orden debe ser mayor o igual a 1."

        if self.rol_autoria not in dict(self.ROL_AUTORIA):
            errors["rol_autoria"] = "Rol de autoría inválido."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.autor} ({self.rol_autoria}) #{self.orden}"