import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


MAX_PROYECTO_PDF_BYTES = 5 * 1024 * 1024
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


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


def _read_header(field_file, size=1024):
    file_obj = getattr(field_file, "file", field_file)

    if file_obj is None or not hasattr(file_obj, "read"):
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

        content = file_obj.read(size)

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


def _validate_pdf(field_file, *, max_bytes, label):
    errors = []

    name = _norm_text(
        getattr(field_file, "name", "")
    )

    extension = os.path.splitext(
        name.lower()
    )[1]

    if extension not in ALLOWED_PDF_EXTENSIONS:
        errors.append(
            f"{label} debe tener extensión .pdf."
        )

    content_type = (
        getattr(field_file, "content_type", None)
        or getattr(
            getattr(field_file, "file", None),
            "content_type",
            None,
        )
    )

    if (
        content_type
        and str(content_type).lower()
        not in ALLOWED_PDF_CONTENT_TYPES
    ):
        errors.append(
            f"{label} debe ser un archivo PDF."
        )

    try:
        file_size = int(
            getattr(field_file, "size", 0)
            or 0
        )
    except (TypeError, ValueError):
        file_size = 0

    if file_size <= 0:
        errors.append(
            f"{label} está vacío."
        )

    if file_size > max_bytes:
        max_mb = max_bytes / (1024 * 1024)

        errors.append(
            f"{label} supera el tamaño máximo "
            f"de {max_mb:g} MB."
        )

    header = _read_header(field_file)

    if header and not header.startswith(b"%PDF-"):
        errors.append(
            f"{label} no contiene una firma PDF válida."
        )

    return errors


def proyecto_pdf_upload_path(instance, filename):
    filename = filename or "proyecto.pdf"
    base, extension = os.path.splitext(filename)

    safe_base = (
        _norm_text(base)
        or "proyecto"
    )[:80]

    if extension.lower() not in ALLOWED_PDF_EXTENSIONS:
        extension = ".pdf"
    else:
        extension = extension.lower()

    project_id = instance.pk or "tmp"

    return os.path.join(
        "proyectos",
        "pdf",
        str(project_id),
        f"{safe_base}{extension}",
    )

class Sede(models.Model):
    nombre = models.CharField(
        max_length=150,
        unique=True,
    )

    codigo = models.SlugField(
        max_length=50,
        unique=True,
    )

    ciudad = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    descripcion = models.TextField(
        null=True,
        blank=True,
    )

    activa = models.BooleanField(
        default=True,
        db_index=True,
    )

    class Meta:
        db_table = "sedes"
        ordering = ["nombre"]
        indexes = [
            models.Index(
                fields=["activa"],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.nombre = _norm_text(self.nombre)
        self.codigo = (
            _norm_text(self.codigo).lower()
        )
        self.ciudad = _norm_optional_text(
            self.ciudad
        )
        self.descripcion = _norm_optional_text(
            self.descripcion
        )

        if not self.nombre:
            errors["nombre"] = (
                "El nombre de la sede es obligatorio."
            )

        if not self.codigo:
            errors["codigo"] = (
                "El código de la sede es obligatorio."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


    
class Facultad(models.Model):
    nombre = models.CharField(
        max_length=255,
        unique=True,
    )

    siglas = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    descripcion = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "facultades"
        ordering = ["nombre"]

    def clean(self):
        super().clean()

        errors = {}

        self.nombre = _norm_text(self.nombre)
        self.siglas = _norm_optional_text(
            self.siglas
        )
        self.descripcion = _norm_optional_text(
            self.descripcion
        )

        if self.siglas:
            self.siglas = self.siglas.upper()

        if not self.nombre:
            errors["nombre"] = (
                "El nombre de la facultad es obligatorio."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
class CarreraSede(models.Model):
    sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        related_name="carreras_sede",
    )

    carrera = models.ForeignKey(
        "Carrera",
        on_delete=models.PROTECT,
        related_name="sedes_carrera",
    )

    activa = models.BooleanField(
        default=True,
        db_index=True,
    )

    class Meta:
        db_table = "carreras_sedes"
        ordering = [
            "sede__nombre",
            "carrera__nombre",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "sede",
                    "carrera",
                ],
                name="unique_carrera_por_sede",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "sede",
                    "activa",
                ],
            ),
            models.Index(
                fields=[
                    "carrera",
                    "activa",
                ],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if not self.sede_id:
            errors["sede"] = (
                "La sede es obligatoria."
            )

        if not self.carrera_id:
            errors["carrera"] = (
                "La carrera es obligatoria."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.carrera} · {self.sede}"
        )

class Carrera(models.Model):
    nombre = models.CharField(
        max_length=255,
    )

    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.CASCADE,
        related_name="carreras",
    )

    class Meta:
        db_table = "carreras"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "facultad"],
                name="unique_carrera_por_facultad",
            ),
        ]
        indexes = [
            models.Index(
                fields=["facultad", "nombre"],
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        self.nombre = _norm_text(self.nombre)

        if not self.nombre:
            errors["nombre"] = (
                "El nombre de la carrera es obligatorio."
            )

        if not self.facultad_id:
            errors["facultad"] = (
                "La facultad es obligatoria."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        faculty_label = (
            self.facultad.siglas
            or self.facultad.nombre
            if self.facultad_id
            else "Sin facultad"
        )

        return f"{self.nombre} ({faculty_label})"


class Proyecto(models.Model):
    ESTADOS = [
        ("nuevo", "Nuevo"),
        ("arrastre", "Arrastre"),
        ("cierre", "Cierre"),
    ]

    nombre = models.CharField(
        max_length=255,
    )

    descripcion = models.TextField(
        null=True,
        blank=True,
    )

    # =========================================================
    # CLASIFICACIÓN INSTITUCIONAL
    # =========================================================

    sede = models.ForeignKey(
        "core.Sede",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="proyectos",
    )

    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.CASCADE,
        related_name="proyectos",
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="proyectos_creados",
        limit_choices_to={"is_staff": True},
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="nuevo",
        db_index=True,
    )

    autores = models.ManyToManyField(
        "core.Autor",
        through="core.ProyectoAutor",
        related_name="proyectos",
        blank=True,
    )

    fecha_inicio = models.DateField(
        null=True,
        blank=True,
    )

    fecha_fin_planificada = models.DateField(
        null=True,
        blank=True,
    )

    fecha_fin_prorrogada = models.DateField(
        null=True,
        blank=True,
    )

    fecha_cierre = models.DateField(
        null=True,
        blank=True,
    )

    anio_inicio = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    anio_fin = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    archivo_pdf = models.FileField(
        upload_to=proyecto_pdf_upload_path,
        max_length=255,
        null=True,
        blank=True,
    )

    fecha_creacion = models.DateField(
        auto_now_add=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "proyectos"

        ordering = [
            "-anio_inicio",
            "nombre",
            "id",
        ]

        indexes = [
            models.Index(
                fields=["estado"]
            ),
            models.Index(
                fields=["anio_inicio"]
            ),
            models.Index(
                fields=["anio_fin"]
            ),
            models.Index(
                fields=[
                    "estado",
                    "anio_inicio",
                ]
            ),
            models.Index(
                fields=["carrera"]
            ),

            # NUEVO
            models.Index(
                fields=["sede"]
            ),

            # NUEVO
            models.Index(
                fields=[
                    "sede",
                    "anio_inicio",
                ]
            ),

            models.Index(
                fields=["creado_por"]
            ),
        ]

    @property
    def facultad(self):
        if not self.carrera_id:
            return None

        return self.carrera.facultad

    @property
    def fecha_fin_vigente(self):
        return (
            self.fecha_fin_prorrogada
            or self.fecha_fin_planificada
        )

    def clean(self):
        super().clean()

        errors = {}

        self.nombre = _norm_text(
            self.nombre
        )

        self.descripcion = _norm_optional_text(
            self.descripcion
        )

        self.estado = _norm_text(
            self.estado
        ).lower()

        valid_states = {
            value
            for value, _label
            in self.ESTADOS
        }

        if not self.nombre:
            errors["nombre"] = (
                "El nombre del proyecto es obligatorio."
            )

        if not self.carrera_id:
            errors["carrera"] = (
                "La carrera es obligatoria."
            )

        # =====================================================
        # SEDE / CARRERA
        # =====================================================

        if (
            self.sede_id
            and self.carrera_id
        ):
            relacion_activa = (
                self.carrera
                .sedes_carrera
                .filter(
                    sede_id=self.sede_id,
                    activa=True,
                )
                .exists()
            )

            if not relacion_activa:
                errors["carrera"] = (
                    "La carrera seleccionada no está "
                    "habilitada en la sede indicada."
                )

        # =====================================================
        # ADMINISTRADOR CREADOR
        # =====================================================

        if not self.creado_por_id:
            errors["creado_por"] = (
                "Debe indicar el administrador creador."
            )

        elif not (
            getattr(
                self.creado_por,
                "is_staff",
                False,
            )
            or getattr(
                self.creado_por,
                "is_superuser",
                False,
            )
        ):
            errors["creado_por"] = (
                "El usuario creador debe tener "
                "privilegios administrativos."
            )

        # =====================================================
        # ESTADO
        # =====================================================

        if self.estado not in valid_states:
            errors["estado"] = (
                "El estado del proyecto es inválido."
            )

        # =====================================================
        # FECHAS
        # =====================================================

        if (
            self.fecha_inicio
            and self.fecha_fin_planificada
            and self.fecha_fin_planificada
            < self.fecha_inicio
        ):
            errors["fecha_fin_planificada"] = (
                "La fecha de finalización planificada "
                "no puede ser menor a la fecha de inicio."
            )

        if (
            self.fecha_inicio
            and self.fecha_fin_prorrogada
            and self.fecha_fin_prorrogada
            < self.fecha_inicio
        ):
            errors["fecha_fin_prorrogada"] = (
                "La fecha prorrogada no puede ser menor "
                "a la fecha de inicio."
            )

        if (
            self.fecha_fin_planificada
            and self.fecha_fin_prorrogada
            and self.fecha_fin_prorrogada
            < self.fecha_fin_planificada
        ):
            errors["fecha_fin_prorrogada"] = (
                "La fecha prorrogada no puede ser menor "
                "a la fecha planificada."
            )

        if (
            self.fecha_cierre
            and self.fecha_inicio
            and self.fecha_cierre
            < self.fecha_inicio
        ):
            errors["fecha_cierre"] = (
                "La fecha de cierre no puede ser menor "
                "a la fecha de inicio."
            )

        if self.fecha_inicio:
            self.anio_inicio = (
                self.fecha_inicio.year
            )

        final_reference = (
            self.fecha_cierre
            or self.fecha_fin_prorrogada
            or self.fecha_fin_planificada
        )

        if final_reference:
            self.anio_fin = (
                final_reference.year
            )

        if (
            self.anio_inicio is not None
            and self.anio_inicio < 1
        ):
            errors["anio_inicio"] = (
                "El año de inicio debe ser mayor "
                "o igual a 1."
            )

        if (
            self.anio_fin is not None
            and self.anio_fin < 1
        ):
            errors["anio_fin"] = (
                "El año de finalización debe ser mayor "
                "o igual a 1."
            )

        if (
            self.anio_inicio
            and self.anio_fin
            and self.anio_fin < self.anio_inicio
        ):
            errors["anio_fin"] = (
                "El año de finalización no puede ser "
                "menor al año de inicio."
            )

        # =====================================================
        # PDF
        # =====================================================

        if self.archivo_pdf:
            pdf_errors = _validate_pdf(
                self.archivo_pdf,
                max_bytes=MAX_PROYECTO_PDF_BYTES,
                label="El PDF del proyecto",
            )

            if pdf_errors:
                errors["archivo_pdf"] = (
                    pdf_errors
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        old_pdf = None

        if self.pk:
            try:
                old_pdf = (
                    Proyecto.objects
                    .only("archivo_pdf")
                    .get(pk=self.pk)
                    .archivo_pdf
                )
            except Proyecto.DoesNotExist:
                old_pdf = None

        if not self.anio_inicio:
            if self.fecha_inicio:
                self.anio_inicio = (
                    self.fecha_inicio.year
                )

            elif self.fecha_creacion:
                self.anio_inicio = (
                    self.fecha_creacion.year
                )

            else:
                self.anio_inicio = (
                    timezone.now().year
                )

        final_reference = (
            self.fecha_cierre
            or self.fecha_fin_prorrogada
            or self.fecha_fin_planificada
        )

        if (
            final_reference
            and not self.anio_fin
        ):
            self.anio_fin = (
                final_reference.year
            )

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
        return self.nombre


class ProyectoAutor(models.Model):
    ROLES = [
        (
            "principal",
            "Investigador principal",
        ),
        (
            "coinvestigador",
            "Coinvestigador",
        ),
        (
            "colaborador",
            "Colaborador",
        ),
    ]

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="participaciones",
    )

    autor = models.ForeignKey(
        "core.Autor",
        on_delete=models.CASCADE,
        related_name="proyectos_participaciones",
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default="principal",
    )

    orden = models.PositiveIntegerField(
        default=1,
    )

    class Meta:
        db_table = "proyectos_autores"
        ordering = ["orden", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["proyecto", "autor"],
                name="unique_autor_por_proyecto",
            ),
            models.UniqueConstraint(
                fields=["proyecto", "orden"],
                name="unique_orden_por_proyecto",
            ),
        ]
        indexes = [
            models.Index(
                fields=["proyecto", "rol"],
            ),
            models.Index(fields=["autor"]),
        ]

    def clean(self):
        super().clean()

        errors = {}

        valid_roles = {
            value
            for value, _label
            in self.ROLES
        }

        if self.orden is None or self.orden < 1:
            errors["orden"] = (
                "El orden debe ser mayor o igual a 1."
            )

        if self.rol not in valid_roles:
            errors["rol"] = (
                "El rol del autor en el proyecto "
                "es inválido."
            )

        if not self.proyecto_id:
            errors["proyecto"] = (
                "El proyecto es obligatorio."
            )

        if not self.autor_id:
            errors["autor"] = (
                "El autor es obligatorio."
            )

        if (
            self.rol == "principal"
            and self.orden != 1
        ):
            errors["orden"] = (
                "El investigador principal debe "
                "ocupar el orden 1."
            )

        if (
            self.orden == 1
            and self.rol != "principal"
        ):
            errors["rol"] = (
                "El autor ubicado en el orden 1 debe "
                "ser investigador principal."
            )

        if self.proyecto_id:
            principal_query = (
                ProyectoAutor.objects
                .filter(
                    proyecto_id=self.proyecto_id,
                    rol="principal",
                )
            )

            if self.pk:
                principal_query = (
                    principal_query.exclude(
                        pk=self.pk
                    )
                )

            if (
                self.rol == "principal"
                and principal_query.exists()
            ):
                errors["rol"] = (
                    "El proyecto ya tiene un "
                    "investigador principal."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.autor} · "
            f"{self.proyecto} ({self.rol})"
        )