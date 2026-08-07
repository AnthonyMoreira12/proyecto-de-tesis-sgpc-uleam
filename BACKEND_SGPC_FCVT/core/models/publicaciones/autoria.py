import re

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


ORCID_PATTERN = re.compile(
    r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"
)


def _norm_orcid(value):
    value = _norm_optional_text(value)
    return value.upper() if value else None


def _is_valid_orcid(value):
    """Valida formato y dígito de control ORCID (ISO 7064 MOD 11-2)."""
    value = _norm_orcid(value)

    if not value or not ORCID_PATTERN.fullmatch(value):
        return False

    digits = value.replace("-", "")
    total = 0

    for char in digits[:-1]:
        total = (total + int(char)) * 2

    remainder = total % 11
    result = (12 - remainder) % 11
    expected = "X" if result == 10 else str(result)

    return digits[-1] == expected


class Autor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="autor",
    )

    identificacion = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    nombres = models.CharField(
        max_length=100,
    )

    apellidos = models.CharField(
        max_length=100,
    )

    correo = models.EmailField(
        max_length=150,
        null=True,
        blank=True,
    )

    institucion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=(
            "Institución a la que pertenece el autor."
        ),
    )

    orcid = models.CharField(
        max_length=19,
        null=True,
        blank=True,
        help_text=(
            "Identificador ORCID del autor en formato "
            "0000-0000-0000-0000."
        ),
    )

    registro_senescyt = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=(
            "Número de registro de investigador SENESCYT."
        ),
    )

    google_scholar = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text=(
            "Enlace al perfil de Google Scholar."
        ),
    )

    scopus_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=(
            "Identificador de autor en Scopus."
        ),
    )

    es_externo = models.BooleanField(
        default=False,
    )

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
                condition=(
                    Q(identificacion__isnull=False)
                    & ~Q(identificacion="")
                ),
                name=(
                    "unique_autor_identificacion_no_vacia"
                ),
            ),
            models.UniqueConstraint(
                fields=["correo"],
                condition=(
                    Q(correo__isnull=False)
                    & ~Q(correo="")
                ),
                name="unique_autor_correo_no_vacio",
            ),
            models.UniqueConstraint(
                fields=["orcid"],
                condition=(
                    Q(orcid__isnull=False)
                    & ~Q(orcid="")
                ),
                name="unique_autor_orcid_no_vacio",
            ),
        ]
        indexes = [
            models.Index(
                fields=["apellidos", "nombres"],
            ),
            models.Index(fields=["correo"]),
            models.Index(fields=["identificacion"]),
            models.Index(fields=["institucion"]),
            models.Index(fields=["registro_senescyt"]),
            models.Index(fields=["scopus_id"]),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.identificacion = _norm_optional_text(
            self.identificacion
        )
        self.correo = _norm_email(
            self.correo
        )
        self.nombres = _norm_text(
            self.nombres
        )
        self.apellidos = _norm_text(
            self.apellidos
        )
        self.institucion = _norm_optional_text(
            self.institucion
        )
        self.orcid = _norm_orcid(
            self.orcid
        )
        self.registro_senescyt = _norm_optional_text(
            self.registro_senescyt
        )
        self.google_scholar = _norm_optional_text(
            self.google_scholar
        )
        self.scopus_id = _norm_optional_text(
            self.scopus_id
        )

        if not self.nombres:
            errors["nombres"] = (
                "Los nombres son obligatorios."
            )

        if not self.apellidos:
            errors["apellidos"] = (
                "Los apellidos son obligatorios."
            )

        if (
            not self.identificacion
            and not self.correo
        ):
            errors["identificacion"] = (
                "Debe registrar al menos una "
                "identificación o un correo."
            )

        if self.orcid and not _is_valid_orcid(self.orcid):
            errors["orcid"] = (
                "El ORCID no tiene un formato o dígito "
                "de control válido."
            )

        if (
            self.usuario_id
            and self.usuario
        ):
            if (
                self.usuario.rol
                == "autor_externo"
            ):
                self.es_externo = True

            if (
                self.usuario.email
                and not self.correo
            ):
                self.correo = (
                    self.usuario.email.lower()
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.nombres} "
            f"{self.apellidos}"
        ).strip()


class PublicacionAutor(models.Model):
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

    orden = models.PositiveIntegerField()

    class Meta:
        db_table = "publicaciones_autores"
        ordering = ["orden", "id"]
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
            models.Index(fields=["autor"]),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if not self.publicacion_id:
            errors["publicacion"] = (
                "La publicación es obligatoria."
            )

        if not self.autor_id:
            errors["autor"] = (
                "El autor es obligatorio."
            )

        if self.orden is None or self.orden < 1:
            errors["orden"] = (
                "El orden debe ser mayor o igual a 1."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.autor} #{self.orden}"