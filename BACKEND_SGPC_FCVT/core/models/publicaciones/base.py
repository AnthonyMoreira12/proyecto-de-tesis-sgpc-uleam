from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_lower(value):
    value = _norm_text(value).lower()
    return value or None


def _delete_storage_file(field_file):
    if not field_file:
        return

    name = getattr(field_file, "name", None)
    storage = getattr(field_file, "storage", None)

    if not name or not storage:
        return

    try:
        if storage.exists(name):
            storage.delete(name)
    except Exception:
        pass


class TipoPublicacion(models.Model):
    CATEGORIAS = [
        ("ponencia", "Ponencia"),
        ("articulo", "Artículo"),
        ("libro", "Libro"),
        ("capitulo", "Capítulo"),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.SlugField(max_length=60, unique=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "tipos_publicacion"
        ordering = ["orden", "nombre"]
        indexes = [
            models.Index(fields=["categoria"]),
        ]

    def clean(self):
        errors = {}

        self.nombre = _norm_text(self.nombre)
        self.codigo = _norm_lower(self.codigo)
        self.categoria = _norm_lower(self.categoria)

        categorias_validas = {value for value, _ in self.CATEGORIAS}

        if not self.nombre:
            errors["nombre"] = "El nombre es obligatorio."

        if not self.codigo:
            errors["codigo"] = "El código es obligatorio."

        if self.categoria not in categorias_validas:
            errors["categoria"] = "La categoría es inválida."

        if self.orden is None or self.orden < 1:
            errors["orden"] = "El orden debe ser mayor o igual a 1."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Publicacion(models.Model):
    proyecto = models.ForeignKey(
        "core.Proyecto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicaciones"
    )

    tipo = models.ForeignKey(
        "core.TipoPublicacion",
        on_delete=models.PROTECT,
        related_name="publicaciones"
    )

    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="publicaciones_creadas",
        limit_choices_to={"rol": "autor"}
    )

    registrado_por_admin = models.BooleanField(default=False)

    admin_registrador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicaciones_registradas_como_admin",
        limit_choices_to={"is_staff": True},
    )

    carrera = models.ForeignKey(
        "core.Carrera",
        on_delete=models.PROTECT,
        related_name="publicaciones"
    )

    area = models.ForeignKey(
        "core.AreaConocimiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    subarea = models.ForeignKey(
        "core.Subarea",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    pais = models.ForeignKey(
        "core.Pais",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    ciudad = models.ForeignKey(
        "core.Ciudad",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    ORIGEN_TIPO = [
        ("ninguno", "Ninguno"),
        ("tic", "Trabajo de integración curricular"),
        ("maestria", "Tesis de maestría"),
        ("doctoral", "Tesis doctoral"),
    ]

    origen_tipo = models.CharField(
        max_length=20,
        choices=ORIGEN_TIPO,
        default="ninguno"
    )

    origen_grado = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        help_text="Especificar el grado cuando el origen lo requiera (p.ej., TIC)."
    )

    archivo_pdf = models.FileField(
        upload_to="publicaciones/pdf/",
        null=True,
        blank=True
    )

    fecha_publicacion = models.DateField(null=True, blank=True)

    anio_publicacion = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True
    )

    numero = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "publicaciones"
        ordering = ["tipo", "numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo", "numero"],
                name="unique_numero_por_tipo"
            )
        ]
        indexes = [
            models.Index(fields=["anio_publicacion"]),
            models.Index(fields=["carrera", "anio_publicacion"]),
            models.Index(fields=["tipo", "anio_publicacion"]),
            models.Index(fields=["origen_tipo", "anio_publicacion"]),
            models.Index(fields=["usuario_creador"]),
            models.Index(fields=["registrado_por_admin"]),
            models.Index(fields=["admin_registrador"]),
            models.Index(fields=["usuario_creador", "registrado_por_admin"]),
        ]

    def clean(self):
        errors = {}

        self.origen_tipo = _norm_lower(self.origen_tipo) or "ninguno"
        self.origen_grado = _norm_optional_text(self.origen_grado)

        origenes_validos = {value for value, _ in self.ORIGEN_TIPO}
        if self.origen_tipo not in origenes_validos:
            errors["origen_tipo"] = "El origen de la publicación es inválido."

        if self.numero is not None and self.numero < 1:
            errors["numero"] = "El número debe ser mayor o igual a 1."

        if self.fecha_publicacion and self.anio_publicacion:
            if self.fecha_publicacion.year != self.anio_publicacion:
                errors["anio_publicacion"] = (
                    "El año de publicación no coincide con la fecha de publicación."
                )

        if self.area_id and self.subarea_id:
            if self.subarea.area_id != self.area_id:
                errors["subarea"] = "La subárea no pertenece al área seleccionada."

        if self.pais_id and self.ciudad_id:
            if self.ciudad.pais_id != self.pais_id:
                errors["ciudad"] = "La ciudad no pertenece al país seleccionado."

        if self.admin_registrador_id:
            if not self.registrado_por_admin:
                self.registrado_por_admin = True

            if not getattr(self.admin_registrador, "is_staff", False) and not getattr(
                self.admin_registrador,
                "is_superuser",
                False,
            ):
                errors["admin_registrador"] = (
                    "El usuario registrador debe tener privilegios administrativos."
                )

        if self.registrado_por_admin and not self.admin_registrador_id:
            errors["admin_registrador"] = (
                "Debe indicar qué administrador registró la publicación."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        old_pdf = None

        if self.pk:
            try:
                old_pdf = (
                    Publicacion.objects.only("archivo_pdf")
                    .get(pk=self.pk)
                    .archivo_pdf
                )
            except Publicacion.DoesNotExist:
                old_pdf = None

        if self.fecha_publicacion and not self.anio_publicacion:
            self.anio_publicacion = self.fecha_publicacion.year

        if self.numero is None and self.tipo_id:
            with transaction.atomic():
                TipoPublicacion.objects.select_for_update().get(pk=self.tipo_id)

                last = (
                    Publicacion.objects.select_for_update()
                    .filter(tipo_id=self.tipo_id)
                    .order_by("-numero")
                    .first()
                )
                self.numero = 1 if not last else (last.numero or 0) + 1

                self.full_clean()
                result = super().save(*args, **kwargs)
        else:
            self.full_clean()
            result = super().save(*args, **kwargs)

        old_name = getattr(old_pdf, "name", None)
        new_name = getattr(self.archivo_pdf, "name", None)

        if old_name and old_name != new_name:
            _delete_storage_file(old_pdf)

        return result

    def delete(self, *args, **kwargs):
        pdf_to_delete = self.archivo_pdf
        result = super().delete(*args, **kwargs)
        _delete_storage_file(pdf_to_delete)
        return result

    def __str__(self):
        tipo_nombre = self.tipo.nombre if self.tipo_id else "Publicación"
        numero = self.numero if self.numero is not None else "s/n"
        return f"{tipo_nombre} #{numero}"