import os
import re

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


# ============================================================
# CONFIGURACIÓN
# ============================================================

MAX_AVATAR_BYTES = 1 * 1024 * 1024

ALLOWED_AVATAR_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

CEDULA_PATTERN = re.compile(
    r"^\d{10}$"
)

CEDULA_VALIDATOR = RegexValidator(
    regex=r"^\d{10}$",
    message=(
        "La cédula debe contener exactamente "
        "10 dígitos numéricos."
    ),
    code="invalid_cedula",
)


# ============================================================
# UTILIDADES
# ============================================================

def _norm_text(value):
    return str(
        value or ""
    ).strip()


PERSON_NAME_LOWERCASE_PARTICLES = {
    "da",
    "das",
    "de",
    "del",
    "do",
    "dos",
    "e",
    "la",
    "las",
    "los",
    "van",
    "von",
    "y",
}


def _capitalize_name_fragment(fragment):
    """
    Capitaliza un fragmento de nombre conservando correctamente
    guiones y apóstrofos.
    """
    if not fragment:
        return fragment

    return (
        fragment[:1].upper()
        + fragment[1:].lower()
    )


def _normalize_name_token(token):
    """
    Normaliza una palabra individual de un nombre.

    Ejemplos:
        MARÍA-JOSÉ -> María-José
        O'NEILL -> O'Neill
    """
    normalized_token = token.lower()

    if normalized_token in PERSON_NAME_LOWERCASE_PARTICLES:
        return normalized_token

    fragments = re.split(
        r"([-’'])",
        normalized_token,
    )

    return "".join(
        fragment
        if fragment in {
            "-",
            "'",
            "’",
        }
        else _capitalize_name_fragment(
            fragment
        )
        for fragment in fragments
    )


def _norm_person_name(value):
    """
    Normaliza nombres y apellidos para su almacenamiento y
    presentación uniforme.

    No se utiliza para correos, cargos, departamentos u otros
    textos generales.
    """
    normalized = re.sub(
        r"\s+",
        " ",
        _norm_text(
            value
        ),
    )

    if not normalized:
        return ""

    return " ".join(
        _normalize_name_token(
            token
        )
        for token in normalized.split(" ")
        if token
    )


def _norm_optional_text(value):
    normalized = _norm_text(
        value
    )

    return normalized or None


def _norm_email(value):
    normalized = (
        BaseUserManager.normalize_email(
            str(
                value or ""
            )
        )
        .strip()
        .lower()
    )

    return normalized or None


def _delete_storage_file(field_file):
    if not field_file:
        return

    name = getattr(
        field_file,
        "name",
        None,
    )

    storage = getattr(
        field_file,
        "storage",
        None,
    )

    if not name or storage is None:
        return

    try:
        if storage.exists(
            name
        ):
            storage.delete(
                name
            )

    except (
        OSError,
        ValueError,
    ):
        return


def _validate_avatar(avatar):
    errors = []

    file_name = _norm_text(
        getattr(
            avatar,
            "name",
            "",
        )
    ).lower()

    extension = os.path.splitext(
        file_name
    )[1]

    if (
        extension
        not in ALLOWED_AVATAR_EXTENSIONS
    ):
        errors.append(
            "Solo se permiten imágenes JPG, PNG o WEBP."
        )

    content_type = (
        getattr(
            avatar,
            "content_type",
            None,
        )
        or getattr(
            getattr(
                avatar,
                "file",
                None,
            ),
            "content_type",
            None,
        )
    )

    if (
        content_type
        and str(
            content_type
        ).lower()
        not in ALLOWED_AVATAR_CONTENT_TYPES
    ):
        errors.append(
            "El tipo de contenido de la imagen "
            "no está permitido."
        )

    try:
        file_size = int(
            getattr(
                avatar,
                "size",
                0,
            )
            or 0
        )

    except (
        TypeError,
        ValueError,
        OSError,
    ):
        file_size = 0

    if file_size <= 0:
        errors.append(
            "La imagen del avatar está vacía."
        )

    if file_size > MAX_AVATAR_BYTES:
        errors.append(
            "El avatar supera el tamaño máximo de 1 MB."
        )

    return errors


# ============================================================
# MANAGER
# ============================================================

class UsuarioManager(
    BaseUserManager
):
    use_in_migrations = True

    def create_user(
        self,
        email,
        nombres,
        apellidos,
        password=None,
        **extra_fields,
    ):
        email = _norm_email(
            email
        )

        nombres = _norm_person_name(
            nombres
        )

        apellidos = _norm_person_name(
            apellidos
        )

        if not email:
            raise ValueError(
                "El usuario debe tener un correo electrónico."
            )

        if not nombres:
            raise ValueError(
                "El usuario debe tener nombres."
            )

        if not apellidos:
            raise ValueError(
                "El usuario debe tener apellidos."
            )

        if "identificacion" in extra_fields:
            extra_fields["identificacion"] = (
                _norm_optional_text(
                    extra_fields.get(
                        "identificacion"
                    )
                )
            )

        if "rol" in extra_fields:
            extra_fields["rol"] = (
                _norm_text(
                    extra_fields.get(
                        "rol"
                    )
                ).lower()
            )

        if "auth_source" in extra_fields:
            extra_fields["auth_source"] = (
                _norm_text(
                    extra_fields.get(
                        "auth_source"
                    )
                ).lower()
            )

        extra_fields.setdefault(
            "is_active",
            True,
        )

        user = self.model(
            email=email,
            nombres=nombres,
            apellidos=apellidos,
            **extra_fields,
        )

        if password:
            user.set_password(
                password
            )
        else:
            user.set_unusable_password()

        user.save(
            using=self._db
        )

        return user

    def create_superuser(
        self,
        email,
        nombres,
        apellidos,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault(
            "is_staff",
            True,
        )

        extra_fields.setdefault(
            "is_superuser",
            True,
        )

        extra_fields.setdefault(
            "rol",
            "autor",
        )

        extra_fields.setdefault(
            "auth_source",
            "local",
        )

        extra_fields.setdefault(
            "is_active",
            True,
        )

        extra_fields.setdefault(
            "carrera",
            None,
        )

        extra_fields.setdefault(
            "sede",
            None,
        )

        if (
            extra_fields.get(
                "is_staff"
            )
            is not True
        ):
            raise ValueError(
                "El superusuario debe tener is_staff=True."
            )

        if (
            extra_fields.get(
                "is_superuser"
            )
            is not True
        ):
            raise ValueError(
                "El superusuario debe tener is_superuser=True."
            )

        if not password:
            raise ValueError(
                "El superusuario debe tener contraseña."
            )

        return self.create_user(
            email=email,
            nombres=nombres,
            apellidos=apellidos,
            password=password,
            **extra_fields,
        )


# ============================================================
# MODELO
# ============================================================

class Usuario(
    AbstractBaseUser,
    PermissionsMixin,
):
    class Rol(
        models.TextChoices
    ):
        AUTOR = (
            "autor",
            "Autor",
        )

        AUTOR_EXTERNO = (
            "autor_externo",
            "Autor externo",
        )

    class AuthSource(
        models.TextChoices
    ):
        LOCAL = (
            "local",
            "Local (BD)",
        )

        MICROSOFT = (
            "microsoft",
            "Microsoft 365",
        )

    ROLES = Rol.choices
    AUTH_SOURCES = AuthSource.choices

    email = models.EmailField(
        unique=True,
        max_length=150,
    )

    nombres = models.CharField(
        max_length=100,
    )

    apellidos = models.CharField(
        max_length=100,
    )

    identificacion = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=[
            CEDULA_VALIDATOR,
        ],
    )

    carrera = models.ForeignKey(
        "core.Carrera",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
    )

    sede = models.ForeignKey(
        "core.Sede",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
    )

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.AUTOR,
    )

    microsoft_id = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )

    ms_graph_id = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    ms_display_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    ms_given_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    ms_surname = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    ms_mail = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
    )

    ms_user_principal_name = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
    )

    ms_job_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    ms_department = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    ms_office_location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    ms_business_phones = models.JSONField(
        null=True,
        blank=True,
    )

    ms_mobile_phone = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    ms_raw_claims = models.JSONField(
        null=True,
        blank=True,
    )

    ms_raw_graph = models.JSONField(
        null=True,
        blank=True,
    )

    auth_source = models.CharField(
        max_length=20,
        choices=AuthSource.choices,
        default=AuthSource.LOCAL,
    )

    perfil_completo = models.BooleanField(
        default=False,
    )

    creado_desde_selector = models.BooleanField(
        default=False,
    )

    perfil_banner_snooze_until = models.DateTimeField(
        null=True,
        blank=True,
    )

    ms_last_sync = models.DateTimeField(
        null=True,
        blank=True,
    )

    profile_edit_attempts_left = (
        models.PositiveSmallIntegerField(
            default=3,
        )
    )

    profile_edit_locked = models.BooleanField(
        default=False,
    )

    profile_edit_lock_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    profile_edit_until = models.DateTimeField(
        null=True,
        blank=True,
    )

    fecha_registro = models.DateTimeField(
        default=timezone.now,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    avatar = models.ImageField(
        upload_to="usuarios/avatar/",
        max_length=255,
        null=True,
        blank=True,
    )

    objects = UsuarioManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "nombres",
        "apellidos",
    ]

    class Meta:
        db_table = "usuarios"

        ordering = [
            "apellidos",
            "nombres",
        ]


        indexes = [
            models.Index(
                fields=[
                    "rol",
                ]
            ),

            models.Index(
                fields=[
                    "auth_source",
                ]
            ),

            models.Index(
                fields=[
                    "is_active",
                ]
            ),

            models.Index(
                fields=[
                    "is_staff",
                ]
            ),

            models.Index(
                fields=[
                    "carrera",
                ]
            ),

            models.Index(
                fields=[
                    "sede",
                ]
            ),

            models.Index(
                fields=[
                    "sede",
                    "carrera",
                ]
            ),

            models.Index(
                fields=[
                    "rol",
                    "is_active",
                ]
            ),

            models.Index(
                fields=[
                    "auth_source",
                    "is_active",
                ]
            ),

            models.Index(
                fields=[
                    "creado_desde_selector",
                ]
                
            ),


        ]

    # ========================================================
    # CLASIFICACIÓN
    # ========================================================

    @property
    def es_institucional(self):
        """
        Una cuenta es institucional únicamente cuando proviene
        de Microsoft y tiene rol de autor.
        """
        return bool(
            self.rol
            == self.Rol.AUTOR
            and self.auth_source
            == self.AuthSource.MICROSOFT
        )

    @property
    def es_externo(self):
        """
        Una cuenta es externa únicamente cuando utiliza acceso
        local y tiene rol de autor externo.
        """
        return bool(
            self.rol
            == self.Rol.AUTOR_EXTERNO
            and self.auth_source
            == self.AuthSource.LOCAL
        )

    @property
    def es_admin(self):
        """
        Los permisos administrativos son independientes del tipo
        de cuenta.
        """
        return bool(
            self.is_staff
            or self.is_superuser
        )

    @property
    def es_pendiente_activacion(self):
        """
        Una cuenta externa está pendiente cuando se encuentra
        inactiva y todavía no posee una contraseña utilizable.

        Esto permite diferenciar una cuenta nueva pendiente de
        una cuenta externa desactivada posteriormente.
        """
        return bool(
            self.es_externo
            and not self.is_active
            and not self.has_usable_password()
        )

    # ========================================================
    # RELACIÓN ACADÉMICA
    # ========================================================

    @property
    def facultad(self):
        if (
            not self.es_institucional
            or not self.carrera_id
        ):
            return None

        return self.carrera.facultad

    @property
    def facultad_id(self):
        if (
            not self.es_institucional
            or not self.carrera_id
        ):
            return None

        return self.carrera.facultad_id

    # ========================================================
    # COMPLETITUD DEL PERFIL
    # ========================================================

    def tiene_cedula_valida(self):
        cedula = _norm_text(
            self.identificacion
        )

        return bool(
            CEDULA_PATTERN.fullmatch(
                cedula
            )
        )

    def calcular_perfil_completo(self):
        """
        Reglas de completitud:

        Cuenta externa:
            La identificación es opcional. Si se proporciona,
            su formato se valida en clean(). La cuenta se considera
            completa con los datos básicos obligatorios del modelo.

        Cuenta institucional:
            Requiere cédula válida, sede y carrera.

            Si Microsoft no permite identificar una sede válida,
            el usuario debe completarla desde Cuenta personal.

        Cuenta local no clasificada:
            No se considera completa.
        """
        if self.es_externo:
            return True

        if self.es_institucional:
            return bool(
                self.tiene_cedula_valida()
                and self.sede_id
                and self.carrera_id
            )

        return False

    # ========================================================
    # VALIDACIÓN
    # ========================================================

    def clean(self):
        super().clean()

        errors = {}

        self.email = _norm_email(
            self.email
        )

        self.nombres = _norm_person_name(
            self.nombres
        )

        self.apellidos = _norm_person_name(
            self.apellidos
        )

        self.identificacion = (
            _norm_optional_text(
                self.identificacion
            )
        )

        self.rol = _norm_text(
            self.rol
        ).lower()

        self.auth_source = _norm_text(
            self.auth_source
        ).lower()

        self.microsoft_id = (
            _norm_optional_text(
                self.microsoft_id
            )
        )

        self.ms_graph_id = (
            _norm_optional_text(
                self.ms_graph_id
            )
        )

        self.ms_display_name = (
            _norm_optional_text(
                self.ms_display_name
            )
        )

        self.ms_given_name = (
            _norm_optional_text(
                self.ms_given_name
            )
        )

        self.ms_surname = (
            _norm_optional_text(
                self.ms_surname
            )
        )

        self.ms_mail = _norm_email(
            self.ms_mail
        )

        self.ms_user_principal_name = (
            _norm_email(
                self.ms_user_principal_name
            )
        )

        self.ms_job_title = (
            _norm_optional_text(
                self.ms_job_title
            )
        )

        self.ms_department = (
            _norm_optional_text(
                self.ms_department
            )
        )

        self.ms_office_location = (
            _norm_optional_text(
                self.ms_office_location
            )
        )

        self.ms_mobile_phone = (
            _norm_optional_text(
                self.ms_mobile_phone
            )
        )

        self.profile_edit_lock_reason = (
            _norm_optional_text(
                self.profile_edit_lock_reason
            )
        )

        if not self.email:
            errors["email"] = (
                "El correo electrónico es obligatorio."
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
            self.identificacion
            and not CEDULA_PATTERN.fullmatch(
                self.identificacion
            )
        ):
            errors["identificacion"] = (
                "La cédula debe contener exactamente "
                "10 dígitos numéricos."
            )

        valid_roles = {
            value
            for value, _label
            in self.Rol.choices
        }

        valid_sources = {
            value
            for value, _label
            in self.AuthSource.choices
        }

        if self.rol not in valid_roles:
            errors["rol"] = (
                "El rol seleccionado es inválido."
            )

        if self.auth_source not in valid_sources:
            errors["auth_source"] = (
                "El origen de autenticación seleccionado "
                "es inválido."
            )

        if (
            self.auth_source
            == self.AuthSource.MICROSOFT
            and self.rol
            != self.Rol.AUTOR
        ):
            errors["rol"] = (
                "Un usuario Microsoft debe tener "
                "el rol de autor institucional."
            )

        if (
            self.rol
            == self.Rol.AUTOR_EXTERNO
            and self.auth_source
            != self.AuthSource.LOCAL
        ):
            errors["auth_source"] = (
                "Un autor externo debe utilizar "
                "autenticación local."
            )

        if (
            self.carrera_id is not None
            and not self.es_institucional
        ):
            errors["carrera"] = (
                "Solo los usuarios institucionales "
                "autenticados mediante Microsoft pueden "
                "tener una carrera asignada."
            )

        if (
            self.sede_id is not None
            and not self.es_institucional
        ):
            errors["sede"] = (
                "Solo los usuarios institucionales "
                "pueden tener una sede asignada."
            )

        # =====================================================
        # COHERENCIA SEDE / CARRERA
        # =====================================================

        if self.es_institucional and self.sede_id:
            if not getattr(self.sede, "activa", False):
                errors["sede"] = (
                    "La sede seleccionada no está activa."
                )

        if (
            self.es_institucional
            and self.sede_id
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
                    "habilitada en la sede asignada "
                    "al usuario."
                )

        if (
            self.is_superuser
            and not self.is_staff
        ):
            errors["is_staff"] = (
                "Un superusuario debe tener is_staff=True."
            )

        if (
            self.profile_edit_attempts_left
            is not None
            and self.profile_edit_attempts_left < 0
        ):
            errors[
                "profile_edit_attempts_left"
            ] = (
                "Los intentos restantes no pueden "
                "ser negativos."
            )

        if self.avatar:
            avatar_errors = (
                _validate_avatar(
                    self.avatar
                )
            )

            if avatar_errors:
                errors["avatar"] = (
                    avatar_errors
                )

        self.perfil_completo = (
            self.calcular_perfil_completo()
        )

        if errors:
            raise ValidationError(
                errors
            )

    # ========================================================
    # GUARDADO
    # ========================================================

    def save(
        self,
        *args,
        **kwargs,
    ):
        old_avatar = None
        old_profile_complete = None

        if self.pk:
            try:
                old_user = (
                    Usuario.objects
                    .only(
                        "avatar",
                        "perfil_completo",
                    )
                    .get(
                        pk=self.pk
                    )
                )

                old_avatar = old_user.avatar
                old_profile_complete = (
                    old_user.perfil_completo
                )

            except Usuario.DoesNotExist:
                old_avatar = None
                old_profile_complete = None

        update_fields = kwargs.get(
            "update_fields"
        )

        original_nombres = self.nombres
        original_apellidos = self.apellidos

        excluded_fields = []

        if (
            update_fields is not None
            and "password"
            not in update_fields
        ):
            excluded_fields.append(
                "password"
            )

        if not self.password:
            excluded_fields.append(
                "password"
            )

        self.full_clean(
            exclude=list(
                dict.fromkeys(
                    excluded_fields
                )
            )
        )

        if update_fields is not None:
            normalized_update_fields = list(
                dict.fromkeys(
                    update_fields
                )
            )

            if (
                original_nombres != self.nombres
                and "nombres"
                not in normalized_update_fields
            ):
                normalized_update_fields.append(
                    "nombres"
                )

            if (
                original_apellidos != self.apellidos
                and "apellidos"
                not in normalized_update_fields
            ):
                normalized_update_fields.append(
                    "apellidos"
                )

            if (
                old_profile_complete
                is not None
                and old_profile_complete
                != self.perfil_completo
                and "perfil_completo"
                not in normalized_update_fields
            ):
                normalized_update_fields.append(
                    "perfil_completo"
                )

            kwargs["update_fields"] = (
                normalized_update_fields
            )

        result = super().save(
            *args,
            **kwargs,
        )

        old_name = getattr(
            old_avatar,
            "name",
            None,
        )

        new_name = getattr(
            self.avatar,
            "name",
            None,
        )

        if (
            old_name
            and old_name != new_name
        ):
            _delete_storage_file(
                old_avatar
            )

        return result

    # ========================================================
    # ELIMINACIÓN
    # ========================================================

    def delete(
        self,
        *args,
        **kwargs,
    ):
        avatar_to_delete = (
            self.avatar
        )

        result = super().delete(
            *args,
            **kwargs,
        )

        _delete_storage_file(
            avatar_to_delete
        )

        return result

    # ========================================================
    # REPRESENTACIÓN
    # ========================================================

    def get_full_name(self):
        return (
            f"{_norm_person_name(self.nombres)} "
            f"{_norm_person_name(self.apellidos)}"
        ).strip()

    def get_short_name(self):
        return _norm_person_name(
            self.nombres
        )

    def __str__(self):
        admin_tag = (
            " | admin"
            if self.es_admin
            else ""
        )

        return (
            f"{self.get_full_name()} "
            f"({self.rol}{admin_tag})"
        )