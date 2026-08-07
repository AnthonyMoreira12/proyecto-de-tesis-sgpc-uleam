import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q


MAX_PUBLICACION_PDF_BYTES = 5 * 1024 * 1024
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}
PDF_SIGNATURE = b"%PDF-"
PDF_SIGNATURE_SCAN_BYTES = 1024


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_lower(value):
    value = _norm_optional_text(value)
    return value.lower() if value else None


def _delete_storage_file(field_file):
    if not field_file:
        return

    name = getattr(field_file, "name", None)
    storage = getattr(field_file, "storage", None)

    if not name or storage is None:
        return

    try:
        if storage.exists(name):
            storage.delete(name)
    except (OSError, ValueError):
        return


def _read_header(
    field_file,
    max_bytes=PDF_SIGNATURE_SCAN_BYTES,
):
    file_obj = getattr(
        field_file,
        "file",
        field_file,
    )

    if (
        file_obj is None
        or not hasattr(file_obj, "read")
    ):
        return b""

    original_position = 0

    try:
        if hasattr(file_obj, "tell"):
            original_position = file_obj.tell()
    except (OSError, ValueError):
        original_position = 0

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        content = file_obj.read(max_bytes)

        if isinstance(content, str):
            content = content.encode(
                "utf-8",
                errors="ignore",
            )

        return bytes(content or b"")

    except (OSError, ValueError, TypeError):
        return b""

    finally:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(original_position)
        except (OSError, ValueError):
            pass


def publicacion_pdf_upload_path(
    instance,
    filename,
):
    filename = filename or "publicacion.pdf"
    base, extension = os.path.splitext(filename)

    safe_base = (
        _norm_text(base)
        or "publicacion"
    )[:100]

    if extension.lower() not in ALLOWED_PDF_EXTENSIONS:
        extension = ".pdf"
    else:
        extension = extension.lower()

    publication_id = instance.pk or "tmp"

    return os.path.join(
        "publicaciones",
        "pdf",
        str(publication_id),
        f"{safe_base}{extension}",
    )


class TipoPublicacion(models.Model):
    CATEGORIAS = [
        ("ponencia", "Ponencia"),
        ("articulo", "Artículo"),
        ("libro", "Libro"),
        ("capitulo", "Capítulo"),
    ]

    nombre = models.CharField(
        max_length=100,
        unique=True,
    )

    codigo = models.SlugField(
        max_length=60,
        unique=True,
    )

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
    )

    orden = models.PositiveIntegerField(
        default=1,
    )

    class Meta:
        db_table = "tipos_publicacion"
        ordering = ["orden", "nombre"]
        indexes = [
            models.Index(
                fields=["categoria"],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.nombre = _norm_text(
            self.nombre
        )

        self.codigo = _norm_lower(
            self.codigo
        )

        self.categoria = _norm_lower(
            self.categoria
        )

        valid_categories = {
            value
            for value, _label
            in self.CATEGORIAS
        }

        if not self.nombre:
            errors["nombre"] = (
                "El nombre es obligatorio."
            )

        if not self.codigo:
            errors["codigo"] = (
                "El código es obligatorio."
            )

        if self.categoria not in valid_categories:
            errors["categoria"] = (
                "La categoría es inválida."
            )

        if self.orden is None or self.orden < 1:
            errors["orden"] = (
                "El orden debe ser mayor o igual a 1."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        return super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        return self.nombre


class Publicacion(models.Model):
    ORIGEN_TIPO = [
        (
            "ninguno",
            "Ninguno",
        ),
        (
            "tic",
            "Trabajo de integración curricular",
        ),
        (
            "maestria",
            "Tesis de maestría",
        ),
        (
            "doctoral",
            "Tesis doctoral",
        ),
        (
            "otro",
            "Otro",
        ),
    ]

    MES_PUBLICACION = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]

    proyecto = models.ForeignKey(
        "core.Proyecto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicaciones",
    )

    tipo = models.ForeignKey(
        TipoPublicacion,
        on_delete=models.PROTECT,
        related_name="publicaciones",
    )

    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="publicaciones_creadas",
        limit_choices_to=Q(
            rol__in=[
                "autor",
                "autor_externo",
            ]
        ),
    )

    registrado_por_admin = models.BooleanField(
        default=False,
    )

    admin_registrador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name=(
            "publicaciones_registradas_como_admin"
        ),
        limit_choices_to=Q(
            is_staff=True
        )
        | Q(
            is_superuser=True
        ),
    )

    carrera = models.ForeignKey(
        "core.Carrera",
        on_delete=models.PROTECT,
        related_name="publicaciones",
    )

    area = models.ForeignKey(
        "core.AreaConocimiento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicaciones",
    )

    subarea = models.ForeignKey(
        "core.Subarea",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicaciones",
    )

    pais = models.ForeignKey(
        "core.Pais",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicaciones",
    )

    ciudad = models.ForeignKey(
        "core.Ciudad",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publicaciones",
    )

    origen_tipo = models.CharField(
        max_length=20,
        choices=ORIGEN_TIPO,
        default="ninguno",
    )

    origen_grado = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        help_text=(
            "Especificar el grado o programa cuando "
            "el origen sea TIC, o escribir el origen "
            "cuando se seleccione Otro."
        ),
    )

    archivo_pdf = models.FileField(
        upload_to=publicacion_pdf_upload_path,
        max_length=255,
        null=True,
        blank=True,
    )

    anio_publicacion = models.PositiveIntegerField(
        db_index=True,
    )

    mes_publicacion = models.PositiveSmallIntegerField(
        choices=MES_PUBLICACION,
        null=True,
        blank=True,
    )

    numero = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "publicaciones"
        ordering = [
            "tipo",
            "numero",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tipo",
                    "numero",
                ],
                name="unique_numero_por_tipo",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "anio_publicacion",
                ],
            ),
            models.Index(
                fields=[
                    "anio_publicacion",
                    "mes_publicacion",
                ],
            ),
            models.Index(
                fields=[
                    "carrera",
                    "anio_publicacion",
                ],
            ),
            models.Index(
                fields=[
                    "tipo",
                    "anio_publicacion",
                ],
            ),
            models.Index(
                fields=[
                    "origen_tipo",
                    "anio_publicacion",
                ],
            ),
            models.Index(
                fields=[
                    "usuario_creador",
                ],
            ),
            models.Index(
                fields=[
                    "registrado_por_admin",
                ],
            ),
            models.Index(
                fields=[
                    "admin_registrador",
                ],
            ),
            models.Index(
                fields=[
                    "usuario_creador",
                    "registrado_por_admin",
                ],
            ),
        ]

    @property
    def facultad(self):
        if not self.carrera_id:
            return None

        return self.carrera.facultad

    @property
    def facultad_id(self):
        if not self.carrera_id:
            return None

        return self.carrera.facultad_id

    def clean(self):
        super().clean()

        errors = {}

        self.origen_tipo = (
            _norm_lower(
                self.origen_tipo
            )
            or "ninguno"
        )

        self.origen_grado = (
            _norm_optional_text(
                self.origen_grado
            )
        )

        valid_origins = {
            value
            for value, _label
            in self.ORIGEN_TIPO
        }

        if self.origen_tipo not in valid_origins:
            errors["origen_tipo"] = (
                "El origen de la publicación es inválido."
            )

        # =====================================================
        # TIC U OTRO REQUIEREN EL CAMPO COMPLEMENTARIO
        # =====================================================

        if (
            self.origen_tipo in {
                "tic",
                "otro",
            }
            and not self.origen_grado
        ):
            if self.origen_tipo == "tic":
                errors["origen_grado"] = (
                    "Debe especificar el grado o programa "
                    "cuando el origen es un Trabajo de "
                    "Integración Curricular."
                )
            else:
                errors["origen_grado"] = (
                    "Debe especificar el origen "
                    "de la publicación."
                )

        # Para Ninguno, Maestría y Doctoral no se guarda
        # contenido adicional en origen_grado.
        if self.origen_tipo not in {
            "tic",
            "otro",
        }:
            self.origen_grado = None

        if not self.tipo_id:
            errors["tipo"] = (
                "El tipo de publicación es obligatorio."
            )

        if not self.usuario_creador_id:
            errors["usuario_creador"] = (
                "El usuario creador es obligatorio."
            )

        if not self.carrera_id:
            errors["carrera"] = (
                "La carrera es obligatoria."
            )

        if (
            self.numero is not None
            and self.numero < 1
        ):
            errors["numero"] = (
                "El número debe ser mayor o igual a 1."
            )

        if (
            self.anio_publicacion is None
            or self.anio_publicacion < 1
        ):
            errors["anio_publicacion"] = (
                "El año de publicación es obligatorio "
                "y debe ser mayor o igual a 1."
            )

        if (
            self.mes_publicacion is not None
            and self.mes_publicacion not in range(1, 13)
        ):
            errors["mes_publicacion"] = (
                "El mes de publicación debe estar "
                "entre 1 y 12."
            )

        if (
            self.area_id
            and self.subarea_id
            and self.subarea.area_id
            != self.area_id
        ):
            errors["subarea"] = (
                "La subárea no pertenece al área "
                "seleccionada."
            )

        if (
            self.pais_id
            and self.ciudad_id
            and self.ciudad.pais_id
            != self.pais_id
        ):
            errors["ciudad"] = (
                "La ciudad no pertenece al país "
                "seleccionado."
            )

        if (
            self.proyecto_id
            and self.carrera_id
            and self.proyecto.carrera_id
            != self.carrera_id
        ):
            errors["proyecto"] = (
                "El proyecto no pertenece a la "
                "carrera seleccionada."
            )

        if self.admin_registrador_id:
            self.registrado_por_admin = True

            if not (
                getattr(
                    self.admin_registrador,
                    "is_staff",
                    False,
                )
                or getattr(
                    self.admin_registrador,
                    "is_superuser",
                    False,
                )
            ):
                errors["admin_registrador"] = (
                    "El usuario registrador debe tener "
                    "privilegios administrativos."
                )

        if (
            self.registrado_por_admin
            and not self.admin_registrador_id
        ):
            errors["admin_registrador"] = (
                "Debe indicar qué administrador "
                "registró la publicación."
            )

        if (
            not self.registrado_por_admin
            and self.admin_registrador_id
        ):
            errors["registrado_por_admin"] = (
                "La publicación debe marcarse como "
                "registrada por administrador."
            )

        if self.archivo_pdf:
            file_name = _norm_text(
                getattr(
                    self.archivo_pdf,
                    "name",
                    "",
                )
            ).lower()

            extension = os.path.splitext(
                file_name
            )[1]

            if extension not in ALLOWED_PDF_EXTENSIONS:
                errors["archivo_pdf"] = (
                    "Solo se permiten archivos PDF."
                )

            content_type = (
                getattr(
                    self.archivo_pdf,
                    "content_type",
                    None,
                )
                or getattr(
                    getattr(
                        self.archivo_pdf,
                        "file",
                        None,
                    ),
                    "content_type",
                    None,
                )
            )

            if (
                content_type
                and str(content_type).lower()
                not in ALLOWED_PDF_CONTENT_TYPES
            ):
                errors["archivo_pdf"] = (
                    "El tipo de contenido no "
                    "corresponde a un PDF."
                )

            try:
                file_size = int(
                    getattr(
                        self.archivo_pdf,
                        "size",
                        0,
                    )
                    or 0
                )
            except (TypeError, ValueError):
                file_size = 0

            if file_size <= 0:
                errors["archivo_pdf"] = (
                    "El archivo PDF está vacío."
                )

            if (
                file_size
                > MAX_PUBLICACION_PDF_BYTES
            ):
                errors["archivo_pdf"] = (
                    "El PDF principal supera "
                    "el tamaño máximo de 5 MB."
                )

            header = _read_header(
                self.archivo_pdf
            )

            if (
                header
                and PDF_SIGNATURE not in header
            ):
                errors["archivo_pdf"] = (
                    "El archivo no contiene una "
                    "firma PDF válida."
                )

        if errors:
            raise ValidationError(errors)

    def _assign_next_number(self):
        (
            TipoPublicacion.objects
            .select_for_update()
            .get(
                pk=self.tipo_id
            )
        )

        last_number = (
            Publicacion.objects
            .select_for_update()
            .filter(
                tipo_id=self.tipo_id,
                numero__isnull=False,
            )
            .order_by("-numero")
            .values_list(
                "numero",
                flat=True,
            )
            .first()
        )

        self.numero = (
            int(last_number or 0)
            + 1
        )

    def save(self, *args, **kwargs):
        old_pdf = None

        if self.pk:
            try:
                old_pdf = (
                    Publicacion.objects
                    .only("archivo_pdf")
                    .get(pk=self.pk)
                    .archivo_pdf
                )
            except Publicacion.DoesNotExist:
                old_pdf = None

        if (
            self.numero is None
            and self.tipo_id
        ):
            with transaction.atomic():
                self._assign_next_number()
                self.full_clean()

                result = super().save(
                    *args,
                    **kwargs,
                )
        else:
            self.full_clean()

            result = super().save(
                *args,
                **kwargs,
            )

        old_name = getattr(
            old_pdf,
            "name",
            None,
        )

        new_name = getattr(
            self.archivo_pdf,
            "name",
            None,
        )

        if old_name and old_name != new_name:
            _delete_storage_file(
                old_pdf
            )

        return result

    def delete(self, *args, **kwargs):
        pdf_to_delete = self.archivo_pdf

        result = super().delete(
            *args,
            **kwargs,
        )

        _delete_storage_file(
            pdf_to_delete
        )

        return result

    def __str__(self):
        type_name = (
            self.tipo.nombre
            if self.tipo_id
            else "Publicación"
        )

        number = (
            self.numero
            if self.numero is not None
            else "s/n"
        )

        return f"{type_name} #{number}"