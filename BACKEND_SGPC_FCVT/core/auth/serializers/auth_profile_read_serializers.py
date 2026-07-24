"""
Serializer de lectura del perfil del usuario autenticado.

Expone:

- Información personal.
- Relación académica.
- Avatar.
- Clasificación y permisos.
- Información sincronizada con Microsoft.
- Estado efectivo de edición del perfil.
- Estado del aviso de perfil incompleto.

La facultad se deriva exclusivamente desde carrera.facultad.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from core.auth.services.auth_profile_services import (
    get_profile_edit_status,
)


User = get_user_model()


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza valores textuales.
    """
    return str(
        value or ""
    ).strip()


def _normalize_optional_text(value):
    """
    Normaliza textos opcionales.
    """
    normalized = _normalize_text(
        value
    )

    return normalized or None


def _safe_non_negative_int(
    value,
    *,
    default=0,
):
    """
    Convierte un valor en entero no negativo.
    """
    if isinstance(value, bool):
        return int(default)

    try:
        parsed = int(value)

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return int(default)

    return max(
        0,
        parsed,
    )


# ============================================================
# SERIALIZER
# ============================================================

class ProfileSerializer(
    serializers.ModelSerializer
):
    """
    Serializer completo y de solo lectura para el perfil.

    No permite actualizar información. Las modificaciones deben
    realizarse mediante ProfileUpdateSerializer.
    """

    # ========================================================
    # IDENTIDAD
    # ========================================================

    full_name = serializers.SerializerMethodField(
        read_only=True,
    )

    rol_label = serializers.SerializerMethodField(
        read_only=True,
    )

    auth_source_label = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    # ========================================================
    # RELACIÓN ACADÉMICA
    # ========================================================

    facultad = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad_id = serializers.SerializerMethodField(
        read_only=True,
    )

    carrera = serializers.SerializerMethodField(
        read_only=True,
    )

    carrera_id = serializers.SerializerMethodField(
        read_only=True,
    )

    # ========================================================
    # AVATAR
    # ========================================================

    avatar_url = serializers.SerializerMethodField(
        read_only=True,
    )

    # ========================================================
    # PERMISOS
    # ========================================================

    es_admin = serializers.SerializerMethodField(
        read_only=True,
    )

    # ========================================================
    # MICROSOFT
    # ========================================================

    microsoft_id = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    ms_graph_id = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    ms_display_name = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    ms_given_name = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    ms_surname = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    ms_mail = serializers.EmailField(
        read_only=True,
        allow_null=True,
    )

    ms_user_principal_name = serializers.EmailField(
        read_only=True,
        allow_null=True,
    )

    ms_job_title = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    ms_department = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    ms_office_location = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    ms_business_phones = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    ms_mobile_phone = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    # ========================================================
    # ESTADO DE EDICIÓN
    # ========================================================

    profile_edit_attempts_left = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    profile_edit_locked = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    profile_edit_lock_reason = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    profile_edit_until = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    profile_edit_available = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    profile_edit_expired = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    profile_edit_seconds_remaining = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    # ========================================================
    # AVISO DE PERFIL
    # ========================================================

    perfil_banner_snooze_until = (
        serializers.DateTimeField(
            read_only=True,
            allow_null=True,
        )
    )

    perfil_banner_snoozed = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    # ========================================================
    # META
    # ========================================================

    class Meta:
        model = User

        fields = [
            # Identidad
            "id",
            "email",
            "nombres",
            "apellidos",
            "full_name",
            "rol",
            "rol_label",
            "identificacion",

            # Relación académica
            "facultad",
            "facultad_id",
            "carrera",
            "carrera_id",

            # Registro y avatar
            "fecha_registro",
            "avatar_url",

            # Autenticación y perfil
            "auth_source",
            "auth_source_label",
            "perfil_completo",
            "perfil_banner_snooze_until",
            "perfil_banner_snoozed",

            # Permisos
            "is_active",
            "is_staff",
            "is_superuser",
            "es_admin",

            # Microsoft
            "microsoft_id",
            "ms_graph_id",
            "ms_display_name",
            "ms_given_name",
            "ms_surname",
            "ms_mail",
            "ms_user_principal_name",
            "ms_job_title",
            "ms_department",
            "ms_office_location",
            "ms_business_phones",
            "ms_mobile_phone",
            "ms_last_sync",

            # Estado de edición
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",
            "profile_edit_until",
            "profile_edit_available",
            "profile_edit_expired",
            "profile_edit_seconds_remaining",
        ]

        read_only_fields = fields

    # ========================================================
    # RELACIONES
    # ========================================================

    def _get_career(self, obj):
        """
        Obtiene la carrera del usuario de manera segura.
        """
        if getattr(
            obj,
            "carrera_id",
            None,
        ) is None:
            return None

        try:
            return obj.carrera

        except (
            ObjectDoesNotExist,
            AttributeError,
        ):
            return None

    def _get_faculty(self, obj):
        """
        Obtiene la facultad derivada desde la carrera.
        """
        career = self._get_career(
            obj
        )

        if career is None:
            return None

        try:
            return career.facultad

        except (
            ObjectDoesNotExist,
            AttributeError,
        ):
            return None

    # ========================================================
    # ESTADO DE EDICIÓN
    # ========================================================

    def _get_edit_status(self, obj):
        """
        Reutiliza el estado calculado dentro de una misma
        serialización para evitar repetir operaciones.
        """
        cache_attribute = (
            "_profile_serializer_edit_status"
        )

        cached_status = getattr(
            obj,
            cache_attribute,
            None,
        )

        if cached_status is not None:
            return cached_status

        status_payload = (
            get_profile_edit_status(
                obj
            )
        )

        setattr(
            obj,
            cache_attribute,
            status_payload,
        )

        return status_payload

    # ========================================================
    # IDENTIDAD
    # ========================================================

    def get_full_name(self, obj):
        """
        Retorna el nombre completo utilizando el método del
        modelo cuando está disponible.
        """
        get_full_name = getattr(
            obj,
            "get_full_name",
            None,
        )

        if callable(get_full_name):
            full_name = _normalize_text(
                get_full_name()
            )

            if full_name:
                return full_name

        full_name = " ".join(
            part
            for part in [
                _normalize_text(
                    getattr(
                        obj,
                        "nombres",
                        "",
                    )
                ),
                _normalize_text(
                    getattr(
                        obj,
                        "apellidos",
                        "",
                    )
                ),
            ]
            if part
        )

        return (
            full_name
            or _normalize_text(
                getattr(
                    obj,
                    "email",
                    "",
                )
            )
        )

    def get_rol_label(self, obj):
        get_display = getattr(
            obj,
            "get_rol_display",
            None,
        )

        if callable(get_display):
            return _normalize_optional_text(
                get_display()
            )

        return _normalize_optional_text(
            getattr(
                obj,
                "rol",
                None,
            )
        )

    def get_auth_source_label(self, obj):
        get_display = getattr(
            obj,
            "get_auth_source_display",
            None,
        )

        if callable(get_display):
            return _normalize_optional_text(
                get_display()
            )

        return _normalize_optional_text(
            getattr(
                obj,
                "auth_source",
                None,
            )
        )

    # ========================================================
    # RELACIÓN ACADÉMICA
    # ========================================================

    def get_facultad(self, obj):
        faculty = self._get_faculty(
            obj
        )

        if faculty is None:
            return None

        return _normalize_optional_text(
            getattr(
                faculty,
                "nombre",
                None,
            )
        )

    def get_facultad_id(self, obj):
        career = self._get_career(
            obj
        )

        if career is None:
            return None

        return getattr(
            career,
            "facultad_id",
            None,
        )

    def get_carrera(self, obj):
        career = self._get_career(
            obj
        )

        if career is None:
            return None

        return _normalize_optional_text(
            getattr(
                career,
                "nombre",
                None,
            )
        )

    def get_carrera_id(self, obj):
        return getattr(
            obj,
            "carrera_id",
            None,
        )

    # ========================================================
    # AVATAR
    # ========================================================

    def get_avatar_url(self, obj):
        """
        Retorna una URL absoluta cuando existe request.
        """
        avatar = getattr(
            obj,
            "avatar",
            None,
        )

        if not avatar:
            return None

        avatar_name = getattr(
            avatar,
            "name",
            None,
        )

        if not avatar_name:
            return None

        try:
            avatar_url = avatar.url

        except (
            ValueError,
            OSError,
        ):
            return None

        request = self.context.get(
            "request"
        )

        if request is None:
            return avatar_url

        try:
            return request.build_absolute_uri(
                avatar_url
            )

        except (
            ValueError,
            TypeError,
        ):
            return avatar_url

    # ========================================================
    # PERMISOS
    # ========================================================

    def get_es_admin(self, obj):
        return bool(
            getattr(
                obj,
                "is_staff",
                False,
            )
            or getattr(
                obj,
                "is_superuser",
                False,
            )
        )

    # ========================================================
    # MICROSOFT
    # ========================================================

    def get_ms_business_phones(self, obj):
        """
        Garantiza que los teléfonos se entreguen como lista.
        """
        phones = getattr(
            obj,
            "ms_business_phones",
            None,
        )

        if phones is None:
            return []

        if isinstance(
            phones,
            (list, tuple),
        ):
            return [
                _normalize_text(phone)
                for phone in phones
                if _normalize_text(phone)
            ]

        normalized_phone = _normalize_text(
            phones
        )

        return (
            [normalized_phone]
            if normalized_phone
            else []
        )

    # ========================================================
    # EDICIÓN DEL PERFIL
    # ========================================================

    def get_profile_edit_attempts_left(
        self,
        obj,
    ):
        status_payload = (
            self._get_edit_status(
                obj
            )
        )

        return _safe_non_negative_int(
            status_payload.get(
                "attempts_left"
            )
        )

    def get_profile_edit_locked(
        self,
        obj,
    ):
        return bool(
            self._get_edit_status(
                obj
            ).get(
                "profile_edit_locked",
                False,
            )
        )

    def get_profile_edit_lock_reason(
        self,
        obj,
    ):
        return _normalize_optional_text(
            self._get_edit_status(
                obj
            ).get(
                "profile_edit_lock_reason"
            )
        )

    def get_profile_edit_until(
        self,
        obj,
    ):
        """
        Retorna la fecha límite efectiva.

        Incluye tanto una ampliación explícita como el plazo
        inicial calculado desde fecha_registro.
        """
        return self._get_edit_status(
            obj
        ).get(
            "profile_edit_until"
        )

    def get_profile_edit_available(
        self,
        obj,
    ):
        return bool(
            self._get_edit_status(
                obj
            ).get(
                "available",
                False,
            )
        )

    def get_profile_edit_expired(
        self,
        obj,
    ):
        return bool(
            self._get_edit_status(
                obj
            ).get(
                "expired",
                False,
            )
        )

    def get_profile_edit_seconds_remaining(
        self,
        obj,
    ):
        """
        Retorna los segundos restantes hasta el vencimiento.
        """
        status_payload = (
            self._get_edit_status(
                obj
            )
        )

        deadline = status_payload.get(
            "profile_edit_until"
        )

        if (
            deadline is None
            or status_payload.get(
                "expired",
                False,
            )
        ):
            return 0

        remaining = (
            deadline
            - timezone.now()
        ).total_seconds()

        return max(
            0,
            int(remaining),
        )

    # ========================================================
    # AVISO DE PERFIL
    # ========================================================

    def get_perfil_banner_snoozed(
        self,
        obj,
    ):
        snooze_until = getattr(
            obj,
            "perfil_banner_snooze_until",
            None,
        )

        return bool(
            snooze_until is not None
            and snooze_until
            > timezone.now()
        )