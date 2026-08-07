from django.core.exceptions import ValidationError
from django.db import models


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_lower(value):
    value = _norm_optional_text(value)
    return value.lower() if value else None


class Ponencia(models.Model):
    TIPO_PRESENTACION = [
        (
            "magistral",
            "Conferencia magistral",
        ),
        (
            "oral",
            "Conferencia oral",
        ),
        (
            "poster",
            "Póster",
        ),
        (
            "otro",
            "Otro",
        ),
    ]

    publicacion = models.OneToOneField(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="ponencia",
    )

    nombre_evento = models.CharField(
        max_length=255,
    )

    nombre_ponencia = models.CharField(
        max_length=255,
    )

    codigo_issn_isbn = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    tipo_presentacion = models.CharField(
        max_length=20,
        choices=TIPO_PRESENTACION,
        null=True,
        blank=True,
    )

    tipo_presentacion_otro = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text=(
            "Valor manual cuando el tipo seleccionado "
            "es 'Otro'."
        ),
    )

    link_evento = models.URLField(
        max_length=500,
        null=True,
        blank=True,
    )

    revisor_par_arbitraje = models.CharField(
        max_length=2,
        choices=[
            ("si", "Sí"),
            ("no", "No"),
        ],
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "ponencias"
        ordering = ["nombre_ponencia"]
        indexes = [
            models.Index(
                fields=["nombre_evento"],
            ),
            models.Index(
                fields=["tipo_presentacion"],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.nombre_evento = _norm_text(
            self.nombre_evento
        )
        self.nombre_ponencia = _norm_text(
            self.nombre_ponencia
        )
        self.codigo_issn_isbn = (
            _norm_optional_text(
                self.codigo_issn_isbn
            )
        )
        self.tipo_presentacion = (
            _norm_lower(
                self.tipo_presentacion
            )
        )
        self.tipo_presentacion_otro = (
            _norm_optional_text(
                self.tipo_presentacion_otro
            )
        )
        self.link_evento = (
            _norm_optional_text(
                self.link_evento
            )
        )
        self.revisor_par_arbitraje = (
            _norm_lower(
                self.revisor_par_arbitraje
            )
        )

        if not self.nombre_evento:
            errors["nombre_evento"] = (
                "El nombre del evento es obligatorio."
            )

        if not self.nombre_ponencia:
            errors["nombre_ponencia"] = (
                "El nombre de la ponencia es obligatorio."
            )

        valid_types = {
            value
            for value, _label
            in self.TIPO_PRESENTACION
        }

        if (
            self.tipo_presentacion
            and self.tipo_presentacion
            not in valid_types
        ):
            errors["tipo_presentacion"] = (
                "El tipo de presentación es inválido."
            )

        if self.tipo_presentacion == "otro":
            if not self.tipo_presentacion_otro:
                errors["tipo_presentacion_otro"] = (
                    "Debe escribir el tipo de presentación "
                    "cuando seleccione 'Otro'."
                )
        else:
            self.tipo_presentacion_otro = None

        if (
            self.revisor_par_arbitraje
            and self.revisor_par_arbitraje
            not in {"si", "no"}
        ):
            errors["revisor_par_arbitraje"] = (
                "El valor debe ser 'si' o 'no'."
            )

        if self.publicacion_id:
            category = _norm_lower(
                getattr(
                    self.publicacion.tipo,
                    "categoria",
                    None,
                )
            )

            if category != "ponencia":
                errors["publicacion"] = (
                    "La publicación asociada no "
                    "corresponde a una ponencia."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_ponencia


class Articulo(models.Model):
    TIPO_ARTICULO = [
        (
            "alto_impacto",
            "Alto impacto",
        ),
        (
            "regional",
            "Regional",
        ),
    ]

    BASES_DATOS = [
        ("latindex", "Latindex"),
        ("scielo", "SciELO"),
        ("redalyc", "Redalyc"),
        ("dialnet", "Dialnet"),
        (
            "google_scholar",
            "Google Scholar",
        ),
        ("otra", "Otra"),
    ]

    FACTOR_IMPACTO = [
        ("sjr", "SJR"),
        ("jcr", "JCR"),
    ]

    CUARTIL = [
        ("q1", "Q1"),
        ("q2", "Q2"),
        ("q3", "Q3"),
        ("q4", "Q4"),
        (
            "sin_cuartil",
            "Sin cuartil",
        ),
    ]

    publicacion = models.OneToOneField(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="articulo",
    )

    tipo_articulo = models.CharField(
        max_length=20,
        choices=TIPO_ARTICULO,
    )

    nombre_articulo = models.CharField(
        max_length=255,
    )

    base_datos_indexada = models.CharField(
        max_length=50,
        choices=BASES_DATOS,
        null=True,
        blank=True,
    )

    base_datos_otra = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    codigo_doi = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    codigo_issn = models.CharField(
        max_length=100,
    )

    nombre_revista = models.CharField(
        max_length=255,
    )

    numero_revista = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    link_revista = models.URLField(
        max_length=500,
        null=True,
        blank=True,
    )

    link_publicacion = models.URLField(
        max_length=500,
        null=True,
        blank=True,
    )

    factor_impacto = models.CharField(
        max_length=20,
        choices=FACTOR_IMPACTO,
        null=True,
        blank=True,
    )

    cuartil = models.CharField(
        max_length=20,
        choices=CUARTIL,
        null=True,
        blank=True,
    )

    sjr = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "articulos"
        ordering = [
            models.F(
                "publicacion__anio_publicacion"
            ).desc(),
            models.F(
                "publicacion__mes_publicacion"
            ).desc(nulls_last=True),
            "-id",
        ]
        indexes = [
            models.Index(
                fields=["tipo_articulo"],
            ),
            models.Index(
                fields=["base_datos_indexada"],
            ),
            models.Index(
                fields=[
                    "factor_impacto",
                    "cuartil",
                ],
            ),
            models.Index(
                fields=["codigo_doi"],
            ),
            models.Index(
                fields=["codigo_issn"],
            ),
            models.Index(
                fields=["nombre_revista"],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.tipo_articulo = _norm_lower(
            self.tipo_articulo
        )
        self.nombre_articulo = _norm_text(
            self.nombre_articulo
        )
        self.base_datos_indexada = _norm_lower(
            self.base_datos_indexada
        )
        self.base_datos_otra = (
            _norm_optional_text(
                self.base_datos_otra
            )
        )
        self.codigo_doi = _norm_optional_text(
            self.codigo_doi
        )
        self.codigo_issn = _norm_text(
            self.codigo_issn
        )
        self.nombre_revista = _norm_text(
            self.nombre_revista
        )
        self.link_revista = _norm_optional_text(
            self.link_revista
        )
        self.link_publicacion = (
            _norm_optional_text(
                self.link_publicacion
            )
        )
        self.factor_impacto = _norm_lower(
            self.factor_impacto
        )
        self.cuartil = _norm_lower(
            self.cuartil
        )
        self.sjr = _norm_optional_text(
            self.sjr
        )

        valid_article_types = {
            value
            for value, _label
            in self.TIPO_ARTICULO
        }

        if self.tipo_articulo not in valid_article_types:
            errors["tipo_articulo"] = (
                "El tipo de artículo es inválido."
            )

        if not self.nombre_articulo:
            errors["nombre_articulo"] = (
                "El nombre del artículo es obligatorio."
            )

        if not self.codigo_issn:
            errors["codigo_issn"] = (
                "El código ISSN es obligatorio."
            )

        if not self.nombre_revista:
            errors["nombre_revista"] = (
                "El nombre de la revista es obligatorio."
            )

        if (
            self.numero_revista is not None
            and self.numero_revista < 1
        ):
            errors["numero_revista"] = (
                "El número de revista debe ser "
                "mayor o igual a 1."
            )

        if self.publicacion_id:
            category = _norm_lower(
                getattr(
                    self.publicacion.tipo,
                    "categoria",
                    None,
                )
            )

            if category != "articulo":
                errors["publicacion"] = (
                    "La publicación asociada debe "
                    "ser de categoría artículo."
                )

        if self.tipo_articulo == "regional":
            self.factor_impacto = None
            self.cuartil = None
            self.sjr = None

            valid_bases = {
                value
                for value, _label
                in self.BASES_DATOS
            }

            if not self.base_datos_indexada:
                errors["base_datos_indexada"] = (
                    "Debe seleccionar una base de datos "
                    "o indexación."
                )
            elif (
                self.base_datos_indexada
                not in valid_bases
            ):
                errors["base_datos_indexada"] = (
                    "La base de datos seleccionada "
                    "es inválida."
                )

            if (
                self.base_datos_indexada
                == "otra"
            ):
                if not self.base_datos_otra:
                    errors["base_datos_otra"] = (
                        "Debe especificar la base de datos "
                        "cuando seleccione 'Otra'."
                    )
            else:
                self.base_datos_otra = None

        elif self.tipo_articulo == "alto_impacto":
            self.base_datos_indexada = None
            self.base_datos_otra = None

            valid_factors = {
                value
                for value, _label
                in self.FACTOR_IMPACTO
            }
            valid_quartiles = {
                value
                for value, _label
                in self.CUARTIL
            }

            if (
                self.factor_impacto
                and self.factor_impacto
                not in valid_factors
            ):
                errors["factor_impacto"] = (
                    "El factor de impacto es inválido."
                )

            if (
                self.cuartil
                and self.cuartil
                not in valid_quartiles
            ):
                errors["cuartil"] = (
                    "El cuartil es inválido."
                )

            if (
                self.factor_impacto == "sjr"
                and not self.sjr
            ):
                errors["sjr"] = (
                    "Debe ingresar el valor SJR "
                    "cuando el factor es SJR."
                )

            if self.factor_impacto != "sjr":
                self.sjr = None

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            self.nombre_articulo
            or f"Artículo #{self.pk}"
        )


class Libro(models.Model):
    SI_NO = [
        ("si", "Sí"),
        ("no", "No"),
    ]

    publicacion = models.OneToOneField(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="libro",
    )

    nombre_libro = models.CharField(
        max_length=255,
    )

    codigo_isbn = models.CharField(
        max_length=100,
    )

    editorial_compilador = models.CharField(
        max_length=255,
    )

    revisor_par_arbitraje = models.CharField(
        max_length=2,
        choices=SI_NO,
    )

    link_libro = models.URLField(
        max_length=500,
    )

    class Meta:
        db_table = "libros"
        ordering = ["nombre_libro"]
        indexes = [
            models.Index(
                fields=["codigo_isbn"],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.nombre_libro = _norm_text(
            self.nombre_libro
        )
        self.codigo_isbn = _norm_text(
            self.codigo_isbn
        )
        self.editorial_compilador = _norm_text(
            self.editorial_compilador
        )
        self.revisor_par_arbitraje = (
            _norm_lower(
                self.revisor_par_arbitraje
            )
        )
        self.link_libro = _norm_text(
            self.link_libro
        )

        if not self.nombre_libro:
            errors["nombre_libro"] = (
                "El nombre del libro es obligatorio."
            )

        if not self.codigo_isbn:
            errors["codigo_isbn"] = (
                "El ISBN es obligatorio."
            )

        if not self.editorial_compilador:
            errors["editorial_compilador"] = (
                "La editorial o compilador "
                "es obligatorio."
            )

        if self.revisor_par_arbitraje not in {
            "si",
            "no",
        }:
            errors["revisor_par_arbitraje"] = (
                "El valor debe ser 'si' o 'no'."
            )

        if not self.link_libro:
            errors["link_libro"] = (
                "El enlace del libro es obligatorio."
            )

        if self.publicacion_id:
            category = _norm_lower(
                getattr(
                    self.publicacion.tipo,
                    "categoria",
                    None,
                )
            )

            if category != "libro":
                errors["publicacion"] = (
                    "La publicación asociada no "
                    "corresponde a un libro."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_libro


class CapituloLibro(models.Model):
    SI_NO = [
        ("si", "Sí"),
        ("no", "No"),
    ]

    publicacion = models.OneToOneField(
        "core.Publicacion",
        on_delete=models.CASCADE,
        related_name="capitulo_libro",
    )

    nombre_capitulo = models.CharField(
        max_length=255,
    )

    nombre_libro = models.CharField(
        max_length=255,
    )

    codigo_isbn = models.CharField(
        max_length=100,
    )

    editor_compilador = models.CharField(
        max_length=255,
    )

    revisor_par_arbitraje = models.CharField(
        max_length=2,
        choices=SI_NO,
    )

    link_capitulo = models.URLField(
        max_length=500,
    )

    class Meta:
        db_table = "capitulos_libros"
        ordering = ["nombre_capitulo"]
        indexes = [
            models.Index(
                fields=["codigo_isbn"],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.nombre_capitulo = _norm_text(
            self.nombre_capitulo
        )
        self.nombre_libro = _norm_text(
            self.nombre_libro
        )
        self.codigo_isbn = _norm_text(
            self.codigo_isbn
        )
        self.editor_compilador = _norm_text(
            self.editor_compilador
        )
        self.revisor_par_arbitraje = (
            _norm_lower(
                self.revisor_par_arbitraje
            )
        )
        self.link_capitulo = _norm_text(
            self.link_capitulo
        )

        if not self.nombre_capitulo:
            errors["nombre_capitulo"] = (
                "El nombre del capítulo es obligatorio."
            )

        if not self.nombre_libro:
            errors["nombre_libro"] = (
                "El nombre del libro es obligatorio."
            )

        if not self.codigo_isbn:
            errors["codigo_isbn"] = (
                "El ISBN es obligatorio."
            )

        if not self.editor_compilador:
            errors["editor_compilador"] = (
                "El editor o compilador es obligatorio."
            )

        if self.revisor_par_arbitraje not in {
            "si",
            "no",
        }:
            errors["revisor_par_arbitraje"] = (
                "El valor debe ser 'si' o 'no'."
            )

        if not self.link_capitulo:
            errors["link_capitulo"] = (
                "El enlace del capítulo es obligatorio."
            )

        if self.publicacion_id:
            category = _norm_lower(
                getattr(
                    self.publicacion.tipo,
                    "categoria",
                    None,
                )
            )

            if category != "capitulo":
                errors["publicacion"] = (
                    "La publicación asociada no "
                    "corresponde a un capítulo."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_capitulo