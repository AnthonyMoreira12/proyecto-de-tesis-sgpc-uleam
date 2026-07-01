from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
import os
import magic # <-- IMPORTANTE PARA LA SEGURIDAD


MAX_PROYECTO_PDF_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_PDF_CONTENT_TYPES = {"application/pdf"}


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

    if not name or not storage:
        return

    try:
        if storage.exists(name):
            storage.delete(name)
    except Exception:
        pass


def proyecto_pdf_upload_path(instance, filename):
    filename = filename or "proyecto.pdf"
    base, ext = os.path.splitext(filename)
    ext = (ext or "").lower()

    if ext not in ALLOWED_PDF_EXTENSIONS:
        ext = ".pdf"

    safe_base = (_norm_text(base) or "proyecto")[:80]
    proyecto_id = instance.pk or "tmp"

    return os.path.join("proyectos", "pdf", str(proyecto_id), f"{safe_base}{ext}")


class Facultad(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    siglas = models.CharField(max_length=20, unique=True, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "facultades"
        ordering = ["nombre"]

    def clean(self):
        errors = {}

        self.nombre = _norm_text(self.nombre)
        self.siglas = _norm_optional_text(self.siglas)
        self.descripcion = _norm_optional_text(self.descripcion)

        if self.siglas:
            self.siglas = self.siglas.upper()

        if not self.nombre:
            errors["nombre"] = "El nombre de la facultad es obligatorio."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Carrera(models.Model):
    nombre = models.CharField(max_length=255)
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
            )
        ]
        indexes = [
            models.Index(fields=["facultad", "nombre"]),
        ]

    def clean(self):
        errors = {}

        self.nombre = _norm_text(self.nombre)

        if not self.nombre:
            errors["nombre"] = "El nombre de la carrera es obligatorio."

        if not self.facultad_id:
            errors["facultad"] = "La facultad es obligatoria."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.facultad.siglas or self.facultad.nombre})"





class Proyecto(models.Model):
    ESTADOS = [
        ("nuevo", "Nuevo"),
        ("arrastre", "Arrastre"),
        ("cierre", "Cierre"),
    ]

    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)

    carrera = models.ForeignKey(
        "core.Carrera",
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

    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin_planificada = models.DateField(null=True, blank=True)
    fecha_fin_prorrogada = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateField(null=True, blank=True)

    anio_inicio = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    anio_fin = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    archivo_pdf = models.FileField(
        upload_to=proyecto_pdf_upload_path,
        null=True,
        blank=True,
    )

    fecha_creacion = models.DateField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "proyectos"
        ordering = ["-anio_inicio", "nombre", "id"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["anio_inicio"]),
            models.Index(fields=["anio_fin"]),
            models.Index(fields=["estado", "anio_inicio"]),
            models.Index(fields=["carrera"]),
            models.Index(fields=["creado_por"]),
        ]

    @property
    def fecha_fin_vigente(self):
        return self.fecha_fin_prorrogada or self.fecha_fin_planificada

    def clean(self):
        errors = {}

        self.nombre = _norm_text(self.nombre)
        self.descripcion = _norm_optional_text(self.descripcion)

        estados_validos = {value for value, _ in self.ESTADOS}

        if not self.nombre:
            errors["nombre"] = "El nombre del proyecto es obligatorio."

        if not self.carrera_id:
            errors["carrera"] = "La carrera es obligatoria."

        if not self.creado_por_id:
            errors["creado_por"] = "El usuario creador es obligatorio."
        elif not getattr(self.creado_por, "is_staff", False) and not getattr(
            self.creado_por,
            "is_superuser",
            False,
        ):
            errors["creado_por"] = (
                "El usuario creador debe tener privilegios administrativos."
            )

        if self.estado not in estados_validos:
            errors["estado"] = "El estado del proyecto es inválido."

        if self.estado == "cierre" and not self.fecha_cierre:
            self.fecha_cierre = timezone.now().date()

        if self.fecha_inicio and self.fecha_fin_planificada:
            if self.fecha_fin_planificada < self.fecha_inicio:
                errors["fecha_fin_planificada"] = (
                    "La fecha de finalización planificada no puede ser menor a la fecha de inicio."
                )

        if self.fecha_inicio and self.fecha_fin_prorrogada:
            if self.fecha_fin_prorrogada < self.fecha_inicio:
                errors["fecha_fin_prorrogada"] = (
                    "La fecha prorrogada no puede ser menor a la fecha de inicio."
                )

        if self.fecha_fin_planificada and self.fecha_fin_prorrogada:
            if self.fecha_fin_prorrogada < self.fecha_fin_planificada:
                errors["fecha_fin_prorrogada"] = (
                    "La fecha prorrogada no puede ser menor a la fecha planificada."
                )

        if self.fecha_cierre and self.fecha_inicio:
            if self.fecha_cierre < self.fecha_inicio:
                errors["fecha_cierre"] = (
                    "La fecha de cierre no puede ser menor a la fecha de inicio."
                )

        if self.fecha_inicio and not self.anio_inicio:
            self.anio_inicio = self.fecha_inicio.year

        fecha_fin_referencia = (
            self.fecha_fin_prorrogada or self.fecha_fin_planificada or self.fecha_cierre
        )
        if fecha_fin_referencia and not self.anio_fin:
            self.anio_fin = fecha_fin_referencia.year

        if self.anio_inicio is not None and self.anio_inicio < 1:
            errors["anio_inicio"] = "El año de inicio debe ser mayor o igual a 1."

        if self.anio_fin is not None and self.anio_fin < 1:
            errors["anio_fin"] = "El año de finalización debe ser mayor o igual a 1."

        if self.anio_inicio and self.anio_fin and self.anio_fin < self.anio_inicio:
            errors["anio_fin"] = (
                "El año de finalización no puede ser menor al año de inicio."
            )

        # ============================================================
        # VALIDACIÓN estricta de ARCHIVO PDF (Evitar subida de ejecutables maliciosos)
        # ============================================================
        if self.archivo_pdf:
            file_name = str(getattr(self.archivo_pdf, "name", "") or "").lower()
            ext = os.path.splitext(file_name)[1]

            if ext not in ALLOWED_PDF_EXTENSIONS:
                errors["archivo_pdf"] = "Solo se permiten archivos PDF."

            file_size = int(getattr(self.archivo_pdf, "size", 0) or 0)
            if file_size > MAX_PROYECTO_PDF_BYTES:
                errors["archivo_pdf"] = (
                    "El PDF del proyecto supera el tamaño máximo de 5 MB."
                )

            # Si pasa las pruebas básicas, validamos los bytes reales del archivo
            if "archivo_pdf" not in errors:
                try:
                    # magic lee los primeros bytes y determina el formato real
                    file_mime = magic.from_buffer(self.archivo_pdf.read(2048), mime=True)
                    if file_mime != 'application/pdf':
                        errors["archivo_pdf"] = "El archivo subido no es un PDF válido. Detectado contenido no permitido."
                    
                    # Reiniciamos el cursor de lectura para que Django pueda guardarlo
                    self.archivo_pdf.seek(0)
                except Exception as e:
                    errors["archivo_pdf"] = f"No se pudo analizar la firma del archivo: {str(e)}"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        old_pdf = None

        if self.pk:
            try:
                old_pdf = Proyecto.objects.only("archivo_pdf").get(pk=self.pk).archivo_pdf
            except Proyecto.DoesNotExist:
                old_pdf = None

        if not self.anio_inicio:
            if self.fecha_inicio:
                self.anio_inicio = self.fecha_inicio.year
            elif self.fecha_creacion:
                self.anio_inicio = self.fecha_creacion.year
            else:
                self.anio_inicio = timezone.now().year

        fecha_fin_referencia = (
            self.fecha_fin_prorrogada or self.fecha_fin_planificada or self.fecha_cierre
        )
        if fecha_fin_referencia and not self.anio_fin:
            self.anio_fin = fecha_fin_referencia.year

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
        return self.nombre


class ProyectoAutor(models.Model):
    ROLES = [
        ("principal", "Investigador principal"),
        ("coinvestigador", "Coinvestigador"),
        ("colaborador", "Colaborador"),
    ]

    proyecto = models.ForeignKey(
        "core.Proyecto",
        on_delete=models.CASCADE,
        related_name="participaciones",
    )

    autor = models.ForeignKey(
        "core.Autor",
        on_delete=models.CASCADE,
        related_name="proyectos_participaciones",
    )

    rol = models.CharField(max_length=20, choices=ROLES, default="principal")
    orden = models.PositiveIntegerField(default=1)

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
            models.Index(fields=["proyecto", "rol"]),
            models.Index(fields=["autor"]),
        ]

    def clean(self):
        errors = {}

        roles_validos = {value for value, _ in self.ROLES}

        if self.orden is None or self.orden < 1:
            errors["orden"] = "El orden debe ser mayor o igual a 1."

        if self.rol not in roles_validos:
            errors["rol"] = "El rol del autor en el proyecto es inválido."

        if not self.proyecto_id:
            errors["proyecto"] = "El proyecto es obligatorio."

        if not self.autor_id:
            errors["autor"] = "El autor es obligatorio."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.autor} · {self.proyecto} ({self.rol})"