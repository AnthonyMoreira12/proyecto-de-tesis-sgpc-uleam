"""
Serializer del modelo Autor.

Responsabilidades:

- Validar y normalizar la información básica del autor.
- Permitir Cédula/DNI opcional para autores externos.
- Detectar coincidencias por identificación, correo u ORCID.
- Gestionar identificadores académicos opcionales.
- Exponer el estado de acceso del Usuario relacionado.
- Proteger los campos usuario y es_externo.
- Crear los autores manuales como autores externos.
- Mantener compatibilidad con los formularios y selectores
  actuales del frontend y del panel administrativo.
"""

import re
import unicodedata

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction

from rest_framework import serializers

from core.autores.services.autores_usuario_sync_services import (
    buscar_autor_existente,
)
from core.models import Autor


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ORCID_PATTERN = re.compile(
    r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"
)


def _model_field_max_length(
    field_name,
    default,
):
    """
    Obtiene el max_length configurado en el modelo.

    Utiliza un valor alternativo cuando el campo no tiene
    longitud máxima definida.
    """
    try:
        model_field = Autor._meta.get_field(
            field_name
        )

    except Exception:
        return int(default)

    max_length = getattr(
        model_field,
        "max_length",
        None,
    )

    return int(
        max_length or default
    )


MAX_NAMES_LENGTH = _model_field_max_length(
    "nombres",
    150,
)

MAX_SURNAMES_LENGTH = _model_field_max_length(
    "apellidos",
    150,
)

MAX_IDENTIFICATION_LENGTH = _model_field_max_length(
    "identificacion",
    50,
)

MAX_EMAIL_LENGTH = _model_field_max_length(
    "correo",
    254,
)

MAX_INSTITUTION_LENGTH = (
    _model_field_max_length(
        "institucion",
        255,
    )
)


MAX_ORCID_LENGTH = _model_field_max_length(
    "orcid",
    19,
)

MAX_SENESCYT_LENGTH = _model_field_max_length(
    "registro_senescyt",
    100,
)

MAX_GOOGLE_SCHOLAR_LENGTH = _model_field_max_length(
    "google_scholar",
    500,
)

MAX_SCOPUS_ID_LENGTH = _model_field_max_length(
    "scopus_id",
    100,
)


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_unicode(value):
    """
    Normaliza caracteres Unicode equivalentes.
    """
    return unicodedata.normalize(
        "NFKC",
        str(value or ""),
    )


def _contains_unsafe_control_characters(value):
    """
    Detecta caracteres de control no apropiados para nombres,
    identificaciones e instituciones.
    """
    return any(
        unicodedata.category(
            character
        ).startswith("C")
        for character in value
    )


def _normalize_single_line(value):
    """
    Normaliza un texto en una sola línea.
    """
    normalized = _normalize_unicode(
        value
    )

    if _contains_unsafe_control_characters(
        normalized
    ):
        raise serializers.ValidationError(
            "El valor contiene caracteres no permitidos."
        )

    return " ".join(
        normalized.split()
    )


def _normalize_email(value):
    """
    Normaliza un correo utilizando el manager del modelo
    Usuario.
    """
    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        return ""

    return (
        User.objects
        .normalize_email(normalized)
        .strip()
        .lower()
    )


def _normalize_orcid(value):
    normalized = _normalize_single_line(
        value
    ).upper()

    return normalized or None


def _is_valid_orcid(value):
    """
    Valida formato y dígito de control ORCID
    (ISO 7064 MOD 11-2).
    """
    normalized = _normalize_orcid(value)

    if (
        not normalized
        or not ORCID_PATTERN.fullmatch(
            normalized
        )
    ):
        return False

    digits = normalized.replace("-", "")
    total = 0

    for character in digits[:-1]:
        total = (
            total
            + int(character)
        ) * 2

    remainder = total % 11
    result = (12 - remainder) % 11
    expected = (
        "X"
        if result == 10
        else str(result)
    )

    return digits[-1] == expected


def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura
    compatible con Django REST Framework.
    """
    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
        return {
            "detail": list(
                exc.messages
            )
        }

    return {
        "detail": str(exc),
    }


def _author_full_name(author):
    """
    Construye el nombre completo de un autor.
    """
    return " ".join(
        part
        for part in [
            str(
                getattr(
                    author,
                    "nombres",
                    "",
                )
                or ""
            ).strip(),

            str(
                getattr(
                    author,
                    "apellidos",
                    "",
                )
                or ""
            ).strip(),
        ]
        if part
    )


# ============================================================
# ESTADO DEL USUARIO VINCULADO
# ============================================================

def _normalize_account_value(value):
    return str(value or "").strip().lower()


def _has_usable_password(user):
    if user is None:
        return False

    try:
        return bool(user.has_usable_password())
    except (AttributeError, TypeError, ValueError):
        return False


def _is_external_local_user(user):
    if user is None:
        return False

    role = _normalize_account_value(
        getattr(user, "rol", "")
    )
    auth_source = _normalize_account_value(
        getattr(user, "auth_source", "")
    )

    return bool(
        role == "autor_externo"
        and auth_source == "local"
    )


def _is_pending_external_user(user):
    """
    Una cuenta externa está pendiente únicamente si todavía no
    posee acceso: está inactiva y no tiene contraseña utilizable.
    """
    return bool(
        _is_external_local_user(user)
        and not getattr(user, "is_active", False)
        and not _has_usable_password(user)
    )


def _resolve_user_state(user):
    if user is None:
        return "sin_usuario"

    if _is_pending_external_user(user):
        return "pendiente"

    if bool(getattr(user, "is_active", False)):
        return "activo"

    return "inactivo"


# ============================================================
# SERIALIZER
# ============================================================

class AutorSerializer(serializers.ModelSerializer):
    """
    Serializer utilizado para listar, crear y actualizar autores.

    Los autores creados manualmente mediante este serializer se
    consideran externos. La creación o sincronización del usuario
    pendiente se realiza posteriormente desde el viewset.
    """

    nombres = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        max_length=MAX_NAMES_LENGTH,
        error_messages={
            "required": (
                "Los nombres son obligatorios."
            ),
            "blank": (
                "Los nombres son obligatorios."
            ),
            "null": (
                "Los nombres son obligatorios."
            ),
            "max_length": (
                "Los nombres no pueden superar "
                f"los {MAX_NAMES_LENGTH} caracteres."
            ),
        },
    )

    apellidos = serializers.CharField(
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        max_length=MAX_SURNAMES_LENGTH,
        error_messages={
            "required": (
                "Los apellidos son obligatorios."
            ),
            "blank": (
                "Los apellidos son obligatorios."
            ),
            "null": (
                "Los apellidos son obligatorios."
            ),
            "max_length": (
                "Los apellidos no pueden superar "
                f"los {MAX_SURNAMES_LENGTH} caracteres."
            ),
        },
    )

    identificacion = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        max_length=MAX_IDENTIFICATION_LENGTH,
        error_messages={
            "max_length": (
                "La Cédula / DNI no puede superar "
                f"los {MAX_IDENTIFICATION_LENGTH} caracteres."
            ),
        },
    )

    correo = serializers.EmailField(
        required=True,
        allow_blank=False,
        allow_null=False,
        trim_whitespace=True,
        max_length=MAX_EMAIL_LENGTH,
        error_messages={
            "required": (
                "El correo electrónico es obligatorio."
            ),
            "blank": (
                "El correo electrónico es obligatorio."
            ),
            "null": (
                "El correo electrónico es obligatorio."
            ),
            "invalid": (
                "Ingrese un correo electrónico válido."
            ),
            "max_length": (
                "El correo electrónico no puede superar "
                f"los {MAX_EMAIL_LENGTH} caracteres."
            ),
        },
    )

    institucion = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        max_length=MAX_INSTITUTION_LENGTH,
        error_messages={
            "max_length": (
                "La institución no puede superar "
                f"los {MAX_INSTITUTION_LENGTH} caracteres."
            ),
        },
    )

    orcid = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        max_length=MAX_ORCID_LENGTH,
        error_messages={
            "max_length": (
                "El ORCID no puede superar "
                f"los {MAX_ORCID_LENGTH} caracteres."
            ),
        },
    )

    registro_senescyt = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        max_length=MAX_SENESCYT_LENGTH,
        error_messages={
            "max_length": (
                "El número de registro SENESCYT no puede superar "
                f"los {MAX_SENESCYT_LENGTH} caracteres."
            ),
        },
    )

    google_scholar = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=MAX_GOOGLE_SCHOLAR_LENGTH,
        error_messages={
            "invalid": (
                "Ingrese un enlace válido al perfil de Google Scholar."
            ),
            "max_length": (
                "El enlace de Google Scholar no puede superar "
                f"los {MAX_GOOGLE_SCHOLAR_LENGTH} caracteres."
            ),
        },
    )

    scopus_id = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        max_length=MAX_SCOPUS_ID_LENGTH,
        error_messages={
            "max_length": (
                "El Scopus ID no puede superar "
                f"los {MAX_SCOPUS_ID_LENGTH} caracteres."
            ),
        },
    )

    usuario = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    usuario_id = serializers.IntegerField(
        read_only=True,
    )

    es_externo = serializers.BooleanField(
        read_only=True,
    )

    usuario_activo = serializers.SerializerMethodField(
        read_only=True,
    )

    usuario_pendiente = serializers.SerializerMethodField(
        read_only=True,
    )

    usuario_estado = serializers.SerializerMethodField(
        read_only=True,
    )

    usuario_creado_desde_selector = serializers.SerializerMethodField(
        read_only=True,
    )

    usuario_tiene_password_utilizable = serializers.SerializerMethodField(
        read_only=True,
    )

    nombre_completo = serializers.SerializerMethodField(
        read_only=True,
    )

    correo_resuelto = serializers.SerializerMethodField(
        read_only=True,
    )

    es_admin = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Autor

        fields = [
            "id",
            "nombres",
            "apellidos",
            "identificacion",
            "correo",
            "correo_resuelto",
            "institucion",
            "orcid",
            "registro_senescyt",
            "google_scholar",
            "scopus_id",
            "es_externo",
            "usuario",
            "usuario_id",
            "usuario_activo",
            "usuario_pendiente",
            "usuario_estado",
            "usuario_creado_desde_selector",
            "usuario_tiene_password_utilizable",
            "nombre_completo",
            "es_admin",
        ]

        read_only_fields = [
            "id",
            "es_externo",
            "usuario",
            "usuario_id",
            "usuario_activo",
            "usuario_pendiente",
            "usuario_estado",
            "usuario_creado_desde_selector",
            "usuario_tiene_password_utilizable",
            "nombre_completo",
            "correo_resuelto",
            "es_admin",
        ]

    # ========================================================
    # CAMPOS CALCULADOS
    # ========================================================

    def get_nombre_completo(
        self,
        obj,
    ):
        """
        Devuelve nombres y apellidos en una sola cadena.
        """
        model_full_name = getattr(
            obj,
            "nombre_completo",
            None,
        )

        if callable(model_full_name):
            resolved_name = str(
                model_full_name() or ""
            ).strip()

            if resolved_name:
                return resolved_name

        if isinstance(
            model_full_name,
            str,
        ) and model_full_name.strip():
            return model_full_name.strip()

        return _author_full_name(
            obj
        )

    def get_correo_resuelto(
        self,
        obj,
    ):
        """
        Prioriza el correo del Usuario vinculado.

        Cuando el autor no tiene usuario, utiliza autor.correo.
        """
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if user is not None:
            user_email = _normalize_email(
                getattr(
                    user,
                    "email",
                    None,
                )
            )

            if user_email:
                return user_email

        author_email = _normalize_email(
            getattr(
                obj,
                "correo",
                None,
            )
        )

        return author_email or None

    def get_usuario_activo(
        self,
        obj,
    ):
        user = getattr(obj, "usuario", None)
        return bool(
            getattr(user, "is_active", False)
            if user is not None
            else False
        )

    def get_usuario_pendiente(
        self,
        obj,
    ):
        return _is_pending_external_user(
            getattr(obj, "usuario", None)
        )

    def get_usuario_estado(
        self,
        obj,
    ):
        return _resolve_user_state(
            getattr(obj, "usuario", None)
        )

    def get_usuario_creado_desde_selector(
        self,
        obj,
    ):
        user = getattr(obj, "usuario", None)
        return bool(
            getattr(user, "creado_desde_selector", False)
            if user is not None
            else False
        )

    def get_usuario_tiene_password_utilizable(
        self,
        obj,
    ):
        return _has_usable_password(
            getattr(obj, "usuario", None)
        )

    def get_es_admin(
        self,
        obj,
    ):
        """
        Indica si el usuario vinculado tiene privilegios
        administrativos.
        """
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if user is None:
            return False

        return bool(
            getattr(
                user,
                "is_staff",
                False,
            )
            or getattr(
                user,
                "is_superuser",
                False,
            )
        )

    # ========================================================
    # VALIDACIONES DE CAMPOS
    # ========================================================

    def validate_nombres(
        self,
        value,
    ):
        normalized_names = _normalize_single_line(
            value
        )

        if not normalized_names:
            raise serializers.ValidationError(
                "Los nombres son obligatorios."
            )

        if len(normalized_names) > MAX_NAMES_LENGTH:
            raise serializers.ValidationError(
                (
                    "Los nombres no pueden superar "
                    f"los {MAX_NAMES_LENGTH} caracteres."
                )
            )

        return normalized_names

    def validate_apellidos(
        self,
        value,
    ):
        normalized_surnames = (
            _normalize_single_line(
                value
            )
        )

        if not normalized_surnames:
            raise serializers.ValidationError(
                "Los apellidos son obligatorios."
            )

        if (
            len(normalized_surnames)
            > MAX_SURNAMES_LENGTH
        ):
            raise serializers.ValidationError(
                (
                    "Los apellidos no pueden superar "
                    f"los {MAX_SURNAMES_LENGTH} caracteres."
                )
            )

        return normalized_surnames

    def validate_identificacion(
        self,
        value,
    ):
        """
        La Cédula/DNI es opcional para autores externos.

        Si se proporciona, se conserva como documento de
        identificación del Autor. Puede ser una cédula ecuatoriana,
        un DNI extranjero u otro identificador equivalente.
        """
        if value in (
            None,
            "",
        ):
            return None

        normalized_identification = (
            _normalize_single_line(
                value
            )
        )

        if not normalized_identification:
            return None

        if (
            len(normalized_identification)
            > MAX_IDENTIFICATION_LENGTH
        ):
            raise serializers.ValidationError(
                "La Cédula / DNI no puede superar "
                f"los {MAX_IDENTIFICATION_LENGTH} caracteres."
            )

        return normalized_identification

    def validate_correo(
        self,
        value,
    ):
        normalized_email = _normalize_email(
            value
        )

        if not normalized_email:
            raise serializers.ValidationError(
                (
                    "El correo electrónico "
                    "es obligatorio."
                )
            )

        if len(normalized_email) > MAX_EMAIL_LENGTH:
            raise serializers.ValidationError(
                (
                    "El correo electrónico no puede "
                    f"superar los {MAX_EMAIL_LENGTH} "
                    "caracteres."
                )
            )

        return normalized_email

    def validate_institucion(
        self,
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        normalized_institution = (
            _normalize_single_line(
                value
            )
        )

        if not normalized_institution:
            return None

        if (
            len(normalized_institution)
            > MAX_INSTITUTION_LENGTH
        ):
            raise serializers.ValidationError(
                (
                    "La institución no puede superar "
                    f"los {MAX_INSTITUTION_LENGTH} "
                    "caracteres."
                )
            )

        return normalized_institution

    def validate_orcid(
        self,
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        normalized = _normalize_orcid(
            value
        )

        if not _is_valid_orcid(
            normalized
        ):
            raise serializers.ValidationError(
                "El ORCID no tiene un formato o dígito "
                "de control válido."
            )

        return normalized

    def validate_registro_senescyt(
        self,
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        normalized = _normalize_single_line(
            value
        )

        return normalized or None

    def validate_google_scholar(
        self,
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        return str(value).strip() or None

    def validate_scopus_id(
        self,
        value,
    ):
        if value in (
            None,
            "",
        ):
            return None

        normalized = _normalize_single_line(
            value
        )

        return normalized or None

    # ========================================================
    # VALIDACIÓN DE COINCIDENCIAS
    # ========================================================

    def validate(
        self,
        attrs,
    ):
        """
        Evita duplicados por identificadores confiables.

        No se bloquean personas únicamente porque tengan los
        mismos nombres y apellidos, ya que diferentes autores
        pueden compartir el mismo nombre.
        """
        instance = getattr(
            self,
            "instance",
            None,
        )

        instance_id = getattr(
            instance,
            "pk",
            None,
        )

        identification = attrs.get(
            "identificacion",
            getattr(
                instance,
                "identificacion",
                None,
            )
            if instance is not None
            else None,
        )

        email = attrs.get(
            "correo",
            getattr(
                instance,
                "correo",
                None,
            )
            if instance is not None
            else None,
        )

        orcid = attrs.get(
            "orcid",
            getattr(
                instance,
                "orcid",
                None,
            )
            if instance is not None
            else None,
        )

        identification_match = (
            buscar_autor_existente(
                identificacion=identification,
                exclude_autor_id=instance_id,
            )
        )

        email_match = buscar_autor_existente(
            correo=email,
            exclude_autor_id=instance_id,
        )

        orcid_match = buscar_autor_existente(
            orcid=orcid,
            exclude_autor_id=instance_id,
        )

        identification_author = (
            identification_match.get(
                "autor"
            )
        )

        email_author = email_match.get(
            "autor"
        )

        orcid_author = orcid_match.get(
            "autor"
        )

        matched_authors = {
            author.pk: author
            for author in (
                identification_author,
                email_author,
                orcid_author,
            )
            if author is not None
        }

        if len(matched_authors) > 1:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "La Cédula/DNI, el correo y/o el ORCID "
                        "pertenecen a autores diferentes. "
                        "Revise los datos ingresados."
                    )
                }
            )

        if identification_author is not None:
            raise serializers.ValidationError(
                {
                    "identificacion": (
                        "Ya existe un autor registrado "
                        "con esta Cédula / DNI."
                    )
                }
            )

        if email_author is not None:
            raise serializers.ValidationError(
                {
                    "correo": (
                        "Ya existe un autor registrado "
                        "con este correo electrónico."
                    )
                }
            )

        if orcid_author is not None:
            raise serializers.ValidationError(
                {
                    "orcid": (
                        "Ya existe un autor registrado "
                        "con este ORCID."
                    )
                }
            )

        return attrs

    # ========================================================
    # CREACIÓN
    # ========================================================

    def create(
        self,
        validated_data,
    ):
        """
        Crea un autor manual como externo y sin usuario inicial.

        El viewset invocará posteriormente el servicio que crea
        o vincula su usuario pendiente.
        """
        validated_data.pop(
            "usuario",
            None,
        )

        validated_data.pop(
            "es_externo",
            None,
        )

        validated_data["usuario"] = None
        validated_data["es_externo"] = True

        try:
            with transaction.atomic():
                return super().create(
                    validated_data
                )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible crear el autor "
                        "porque existe un conflicto con "
                        "la Cédula/DNI, el correo, el ORCID o "
                        "el usuario relacionado."
                    )
                }
            ) from exc

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza los campos editables sin permitir que el
        cliente modifique la relación con Usuario o el tipo
        externo del autor.
        """
        validated_data.pop(
            "usuario",
            None,
        )

        validated_data.pop(
            "es_externo",
            None,
        )

        try:
            with transaction.atomic():
                return super().update(
                    instance,
                    validated_data,
                )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible actualizar el autor "
                        "porque existe un conflicto con "
                        "la Cédula/DNI, el correo, el ORCID o "
                        "el usuario relacionado."
                    )
                }
            ) from exc