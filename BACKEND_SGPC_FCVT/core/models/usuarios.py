import os

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_email(value):
    value = (
        BaseUserManager.normalize_email(
            str(value or "")
        )
        .strip()
        .lower()
    )

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


def _validate_avatar(avatar):
    errors = []

    file_name = _norm_text(
        getattr(avatar, "name", "")
    ).lower()

    extension = os.path.splitext(
        file_name
    )[1]

    if extension not in ALLOWED_AVATAR_EXTENSIONS:
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
        and str(content_type).lower()
        not in ALLOWED_AVATAR_CONTENT_TYPES
    ):
        errors.append(
            "El tipo de contenido de la imagen "
            "no está permitido."
        )

    try:
        file_size = int(
            getattr(avatar, "size", 0)
            or 0
        )
    except (TypeError, ValueError):
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


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(
        self,
        email,
        nombres,
        apellidos,
        password=None,
        **extra_fields,
    ):
        email = _norm_email(email)
        nombres = _norm_text(nombres)
        apellidos = _norm_text(apellidos)

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
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

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

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "El superusuario debe tener is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "El superusuario debe tener "
                "is_superuser=True."
            )

        if not password:
            raise ValueError(
                "El superusuario debe tener contraseña."
            )

        return self.create_user(
            email,
            nombres,
            apellidos,
            password,
            **extra_fields,
        )


class Usuario(
    AbstractBaseUser,
    PermissionsMixin,
):
    class Rol(models.TextChoices):
        AUTOR = "autor", "Autor"
        AUTOR_EXTERNO = (
            "autor_externo",
            "Autor externo",
        )

    class AuthSource(models.TextChoices):
        LOCAL = "local", "Local (BD)"
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
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    carrera = models.ForeignKey(
        "core.Carrera",
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
            models.Index(fields=["rol"]),
            models.Index(fields=["auth_source"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_staff"]),
            models.Index(fields=["carrera"]),
            models.Index(
                fields=["rol", "is_active"],
            ),
            models.Index(
                fields=[
                    "auth_source",
                    "is_active",
                ],
            ),
            models.Index(
                fields=["creado_desde_selector"],
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

        self.email = _norm_email(self.email)
        self.nombres = _norm_text(self.nombres)
        self.apellidos = _norm_text(self.apellidos)
        self.identificacion = _norm_optional_text(
            self.identificacion
        )

        self.rol = _norm_text(
            self.rol
        ).lower()

        self.auth_source = _norm_text(
            self.auth_source
        ).lower()

        self.microsoft_id = _norm_optional_text(
            self.microsoft_id
        )
        self.ms_graph_id = _norm_optional_text(
            self.ms_graph_id
        )
        self.ms_display_name = _norm_optional_text(
            self.ms_display_name
        )
        self.ms_given_name = _norm_optional_text(
            self.ms_given_name
        )
        self.ms_surname = _norm_optional_text(
            self.ms_surname
        )
        self.ms_mail = _norm_email(
            self.ms_mail
        )
        self.ms_user_principal_name = _norm_email(
            self.ms_user_principal_name
        )
        self.ms_job_title = _norm_optional_text(
            self.ms_job_title
        )
        self.ms_department = _norm_optional_text(
            self.ms_department
        )
        self.ms_office_location = _norm_optional_text(
            self.ms_office_location
        )
        self.ms_mobile_phone = _norm_optional_text(
            self.ms_mobile_phone
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
                "El origen de autenticación "
                "seleccionado es inválido."
            )

        if (
            self.auth_source
            == self.AuthSource.MICROSOFT
            and self.rol
            != self.Rol.AUTOR
        ):
            errors["rol"] = (
                "Un usuario Microsoft debe ser autor."
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
            self.rol
            == self.Rol.AUTOR_EXTERNO
            and self.carrera_id is not None
        ):
            errors["carrera"] = (
                "Un usuario externo no debe tener "
                "una carrera institucional asignada."
            )

        if (
            self.profile_edit_attempts_left
            is not None
            and self.profile_edit_attempts_left < 0
        ):
            errors["profile_edit_attempts_left"] = (
                "Los intentos restantes no pueden "
                "ser negativos."
            )

        if self.avatar:
            avatar_errors = _validate_avatar(
                self.avatar
            )

            if avatar_errors:
                errors["avatar"] = avatar_errors

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        old_avatar = None

        if self.pk:
            try:
                old_avatar = (
                    Usuario.objects
                    .only("avatar")
                    .get(pk=self.pk)
                    .avatar
                )
            except Usuario.DoesNotExist:
                old_avatar = None

        update_fields = kwargs.get(
            "update_fields"
        )

        exclude = []

        if (
            update_fields is not None
            and "password"
            not in update_fields
        ):
            exclude.append("password")

        if not self.password:
            exclude.append("password")

        self.full_clean(
            exclude=list(
                dict.fromkeys(exclude)
            )
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

        if old_name and old_name != new_name:
            _delete_storage_file(old_avatar)

        return result

    def delete(self, *args, **kwargs):
        avatar_to_delete = self.avatar

        result = super().delete(
            *args,
            **kwargs,
        )

        _delete_storage_file(
            avatar_to_delete
        )

        return result

    def get_full_name(self):
        return (
            f"{self.nombres} "
            f"{self.apellidos}"
        ).strip()

    def get_short_name(self):
        return _norm_text(
            self.nombres
        )

    def __str__(self):
        admin_tag = (
            " | admin"
            if (
                self.is_superuser
                or self.is_staff
            )
            else ""
        )

        return (
            f"{self.get_full_name()} "
            f"({self.rol}{admin_tag})"
        )
