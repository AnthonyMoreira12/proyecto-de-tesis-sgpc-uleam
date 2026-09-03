"""Campañas controladas de actualización de información del SGPC."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CampaniaActualizacion(models.Model):
    """Habilita temporalmente edición controlada sobre datos existentes."""

    TIPO_PERFIL = "perfil"
    TIPO_PUBLICACION = "publicacion"
    TIPO_PROYECTO = "proyecto"

    TIPOS = [
        (TIPO_PERFIL, "Perfil"),
        (TIPO_PUBLICACION, "Publicaciones"),
        (TIPO_PROYECTO, "Proyectos"),
    ]

    ESTADO_BORRADOR = "borrador"
    ESTADO_ACTIVA = "activa"
    ESTADO_FINALIZADA = "finalizada"
    ESTADO_CANCELADA = "cancelada"

    ESTADOS = [
        (ESTADO_BORRADOR, "Borrador"),
        (ESTADO_ACTIVA, "Activa"),
        (ESTADO_FINALIZADA, "Finalizada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    ALCANCE_TODOS = "todos"
    ALCANCE_SEDE = "sede"
    ALCANCE_FACULTAD = "facultad"
    ALCANCE_CARRERA = "carrera"
    ALCANCE_USUARIOS = "usuarios"

    ALCANCES = [
        (ALCANCE_TODOS, "Todos los usuarios"),
        (ALCANCE_SEDE, "Por sede"),
        (ALCANCE_FACULTAD, "Por facultad"),
        (ALCANCE_CARRERA, "Por carrera"),
        (ALCANCE_USUARIOS, "Usuarios específicos"),
    ]

    CAMPOS_PERFIL_PERMITIDOS = {
        "identificacion",
        "sede",
        "carrera",
    }

    CAMPOS_PUBLICACION_PERMITIDOS = {
        "sede",
        "carrera",
        "area",
        "subarea",
        "pais",
        "ciudad",
        "proyecto",
    }

    CAMPOS_PROYECTO_PERMITIDOS = {
        "sede",
        "carrera",
        "descripcion",
        "fecha_inicio",
        "fecha_fin_planificada",
        "fecha_fin_prorrogada",
    }

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default="")

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        db_index=True,
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_BORRADOR,
        db_index=True,
    )

    alcance = models.CharField(
        max_length=20,
        choices=ALCANCES,
        default=ALCANCE_TODOS,
        db_index=True,
    )

    fecha_inicio = models.DateTimeField(null=True, blank=True, db_index=True)
    fecha_fin = models.DateTimeField(null=True, blank=True, db_index=True)

    solo_incompletos = models.BooleanField(default=True)

    campos_habilitados = models.JSONField(default=list)
    filtros_destinatarios = models.JSONField(default=dict, blank=True)

    notificar_internamente = models.BooleanField(default=True)
    crear_aviso = models.BooleanField(default=True)
    enviar_correo = models.BooleanField(default=False)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="campanias_actualizacion_creadas",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    activada_at = models.DateTimeField(null=True, blank=True)
    finalizada_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "campanias_actualizacion"
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["estado", "tipo"],
                name="camp_act_estado_tipo_idx",
            ),
            models.Index(
                fields=["fecha_inicio", "fecha_fin"],
                name="camp_act_fechas_idx",
            ),
        ]

    @classmethod
    def campos_permitidos_para_tipo(cls, tipo):
        if tipo == cls.TIPO_PERFIL:
            return cls.CAMPOS_PERFIL_PERMITIDOS
        if tipo == cls.TIPO_PUBLICACION:
            return cls.CAMPOS_PUBLICACION_PERMITIDOS
        if tipo == cls.TIPO_PROYECTO:
            return cls.CAMPOS_PROYECTO_PERMITIDOS
        return set()

    def clean(self):
        super().clean()
        errors = {}

        self.titulo = str(self.titulo or "").strip()
        self.descripcion = str(self.descripcion or "").strip()

        if not self.titulo:
            errors["titulo"] = "El título de la campaña es obligatorio."

        if self.fecha_inicio and self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            errors["fecha_fin"] = (
                "La fecha de finalización debe ser posterior a la fecha de inicio."
            )

        if not isinstance(self.campos_habilitados, list):
            errors["campos_habilitados"] = "Debe enviar una lista de campos."
        else:
            campos = []
            for raw in self.campos_habilitados:
                campo = str(raw or "").strip()
                if campo and campo not in campos:
                    campos.append(campo)
            self.campos_habilitados = campos

            permitidos = self.campos_permitidos_para_tipo(self.tipo)
            invalidos = sorted(set(campos) - permitidos)
            if invalidos:
                errors["campos_habilitados"] = (
                    "La campaña contiene campos no permitidos para este módulo: "
                    + ", ".join(invalidos)
                )
            if not campos:
                errors["campos_habilitados"] = (
                    "Debe habilitar al menos un campo para la campaña."
                )

        if not isinstance(self.filtros_destinatarios, dict):
            errors["filtros_destinatarios"] = (
                "Los filtros de destinatarios deben enviarse como un objeto."
            )

        if self.estado == self.ESTADO_ACTIVA:
            now = timezone.now()
            if self.fecha_fin and self.fecha_fin <= now:
                errors["fecha_fin"] = "No se puede mantener activa una campaña vencida."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def esta_vigente(self):
        if self.estado != self.ESTADO_ACTIVA:
            return False
        now = timezone.now()
        if self.fecha_inicio and self.fecha_inicio > now:
            return False
        if self.fecha_fin and self.fecha_fin <= now:
            return False
        return True

    def __str__(self):
        return self.titulo


class CampaniaActualizacionUsuario(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_EN_PROGRESO = "en_progreso"
    ESTADO_COMPLETADA = "completada"
    ESTADO_OMITIDA = "omitida"

    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_EN_PROGRESO, "En progreso"),
        (ESTADO_COMPLETADA, "Completada"),
        (ESTADO_OMITIDA, "Omitida"),
    ]

    campania = models.ForeignKey(
        CampaniaActualizacion,
        on_delete=models.CASCADE,
        related_name="participantes",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campanias_actualizacion",
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        db_index=True,
    )

    campos_pendientes = models.JSONField(default=list, blank=True)
    resumen_pendientes = models.JSONField(default=dict, blank=True)

    asignada_at = models.DateTimeField(auto_now_add=True, db_index=True)
    iniciada_at = models.DateTimeField(null=True, blank=True)
    completada_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "campanias_actualizacion_usuarios"
        ordering = ["campania_id", "usuario_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["campania", "usuario"],
                name="uniq_campania_actualizacion_usuario",
            )
        ]
        indexes = [
            models.Index(
                fields=["campania", "estado"],
                name="camp_user_camp_estado_idx",
            ),
            models.Index(
                fields=["usuario", "estado"],
                name="camp_user_usr_estado_idx",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if not isinstance(self.campos_pendientes, list):
            errors["campos_pendientes"] = "Debe ser una lista."
        if not isinstance(self.resumen_pendientes, dict):
            errors["resumen_pendientes"] = "Debe ser un objeto."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.campania_id} · {self.usuario_id} · {self.estado}"
