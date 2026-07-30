"""
Serializer de lectura del perfil del usuario autenticado.

Expone la clasificación efectiva de la cuenta y oculta Facultad y
Carrera para cuentas externas o inconsistentes. La facultad se deriva
exclusivamente desde carrera.facultad.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from core.auth.services.auth_profile_services import get_profile_edit_status


User = get_user_model()


def _normalize_text(value):
    return str(value or "").strip()


def _normalize_optional_text(value):
    normalized = _normalize_text(value)
    return normalized or None


def _safe_non_negative_int(value, *, default=0):
    if isinstance(value, bool):
        return int(default)
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return int(default)
    return max(0, parsed)


def _normalized_role(user):
    return _normalize_text(getattr(user, "rol", "")).lower()


def _normalized_auth_source(user):
    return _normalize_text(getattr(user, "auth_source", "")).lower()


def _is_external_user(user):
    return bool(
        user is not None
        and _normalized_role(user) == "autor_externo"
        and _normalized_auth_source(user) == "local"
    )


def _is_institutional_user(user):
    return bool(
        user is not None
        and _normalized_role(user) == "autor"
        and _normalized_auth_source(user) == "microsoft"
    )


def _has_valid_cedula(user):
    cedula = _normalize_text(getattr(user, "identificacion", None))
    return bool(len(cedula) == 10 and cedula.isdigit())


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    rol_label = serializers.SerializerMethodField(read_only=True)
    auth_source_label = serializers.SerializerMethodField(read_only=True)
    es_externo = serializers.SerializerMethodField(read_only=True)
    es_institucional = serializers.SerializerMethodField(read_only=True)
    tipo_cuenta_label = serializers.SerializerMethodField(read_only=True)
    perfil_completo = serializers.SerializerMethodField(read_only=True)

    facultad = serializers.SerializerMethodField(read_only=True)
    facultad_id = serializers.SerializerMethodField(read_only=True)
    carrera = serializers.SerializerMethodField(read_only=True)
    carrera_id = serializers.SerializerMethodField(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)
    es_admin = serializers.SerializerMethodField(read_only=True)

    microsoft_id = serializers.CharField(read_only=True, allow_null=True)
    ms_graph_id = serializers.CharField(read_only=True, allow_null=True)
    ms_display_name = serializers.CharField(read_only=True, allow_null=True)
    ms_given_name = serializers.CharField(read_only=True, allow_null=True)
    ms_surname = serializers.CharField(read_only=True, allow_null=True)
    ms_mail = serializers.EmailField(read_only=True, allow_null=True)
    ms_user_principal_name = serializers.EmailField(
        read_only=True, allow_null=True
    )
    ms_job_title = serializers.CharField(read_only=True, allow_null=True)
    ms_department = serializers.CharField(read_only=True, allow_null=True)
    ms_office_location = serializers.CharField(read_only=True, allow_null=True)
    ms_business_phones = serializers.SerializerMethodField(read_only=True)
    ms_mobile_phone = serializers.CharField(read_only=True, allow_null=True)

    profile_edit_attempts_left = serializers.SerializerMethodField(
        read_only=True
    )
    profile_edit_locked = serializers.SerializerMethodField(read_only=True)
    profile_edit_lock_reason = serializers.SerializerMethodField(
        read_only=True
    )
    profile_edit_until = serializers.SerializerMethodField(read_only=True)
    profile_edit_available = serializers.SerializerMethodField(read_only=True)
    profile_edit_expired = serializers.SerializerMethodField(read_only=True)
    profile_edit_seconds_remaining = serializers.SerializerMethodField(
        read_only=True
    )

    perfil_banner_snooze_until = serializers.DateTimeField(
        read_only=True, allow_null=True
    )
    perfil_banner_snoozed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nombres",
            "apellidos",
            "full_name",
            "rol",
            "rol_label",
            "identificacion",
            "es_externo",
            "es_institucional",
            "tipo_cuenta_label",
            "facultad",
            "facultad_id",
            "carrera",
            "carrera_id",
            "fecha_registro",
            "avatar_url",
            "auth_source",
            "auth_source_label",
            "perfil_completo",
            "perfil_banner_snooze_until",
            "perfil_banner_snoozed",
            "is_active",
            "is_staff",
            "is_superuser",
            "es_admin",
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
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",
            "profile_edit_until",
            "profile_edit_available",
            "profile_edit_expired",
            "profile_edit_seconds_remaining",
        ]
        read_only_fields = fields

    def _get_career(self, obj):
        # Solo las cuentas institucionales exponen información académica.
        if not _is_institutional_user(obj):
            return None
        if getattr(obj, "carrera_id", None) is None:
            return None
        try:
            return obj.carrera
        except (ObjectDoesNotExist, AttributeError):
            return None

    def _get_faculty(self, obj):
        career = self._get_career(obj)
        if career is None:
            return None
        try:
            return career.facultad
        except (ObjectDoesNotExist, AttributeError):
            return None

    def _get_edit_status(self, obj):
        cache_attribute = "_profile_serializer_edit_status"
        cached_status = getattr(obj, cache_attribute, None)
        if cached_status is not None:
            return cached_status
        status_payload = get_profile_edit_status(obj)
        setattr(obj, cache_attribute, status_payload)
        return status_payload

    def get_full_name(self, obj):
        get_full_name = getattr(obj, "get_full_name", None)
        if callable(get_full_name):
            full_name = _normalize_text(get_full_name())
            if full_name:
                return full_name
        full_name = " ".join(
            part
            for part in [
                _normalize_text(getattr(obj, "nombres", "")),
                _normalize_text(getattr(obj, "apellidos", "")),
            ]
            if part
        )
        return full_name or _normalize_text(getattr(obj, "email", ""))

    def get_rol_label(self, obj):
        if _is_external_user(obj):
            return "Autor externo"
        if _is_institutional_user(obj):
            return "Autor institucional"
        get_display = getattr(obj, "get_rol_display", None)
        return (
            _normalize_optional_text(get_display())
            if callable(get_display)
            else _normalize_optional_text(getattr(obj, "rol", None))
        )

    def get_auth_source_label(self, obj):
        if _is_external_user(obj):
            return "Cuenta local"
        if _is_institutional_user(obj):
            return "Microsoft 365"
        get_display = getattr(obj, "get_auth_source_display", None)
        return (
            _normalize_optional_text(get_display())
            if callable(get_display)
            else _normalize_optional_text(getattr(obj, "auth_source", None))
        )

    def get_es_externo(self, obj):
        return _is_external_user(obj)

    def get_es_institucional(self, obj):
        return _is_institutional_user(obj)

    def get_tipo_cuenta_label(self, obj):
        if _is_external_user(obj):
            return "Cuenta externa"
        if _is_institutional_user(obj):
            return "Cuenta institucional"
        return "Cuenta sin clasificación válida"

    def get_perfil_completo(self, obj):
        if _is_external_user(obj):
            return _has_valid_cedula(obj)
        if _is_institutional_user(obj):
            return bool(_has_valid_cedula(obj) and obj.carrera_id)
        return False

    def get_facultad(self, obj):
        faculty = self._get_faculty(obj)
        return (
            _normalize_optional_text(getattr(faculty, "nombre", None))
            if faculty is not None
            else None
        )

    def get_facultad_id(self, obj):
        career = self._get_career(obj)
        return getattr(career, "facultad_id", None) if career else None

    def get_carrera(self, obj):
        career = self._get_career(obj)
        return (
            _normalize_optional_text(getattr(career, "nombre", None))
            if career is not None
            else None
        )

    def get_carrera_id(self, obj):
        career = self._get_career(obj)
        return getattr(career, "pk", None) if career else None

    def get_avatar_url(self, obj):
        avatar = getattr(obj, "avatar", None)
        if not avatar or not getattr(avatar, "name", None):
            return None
        try:
            avatar_url = avatar.url
        except (ValueError, OSError):
            return None
        request = self.context.get("request")
        if request is None:
            return avatar_url
        try:
            return request.build_absolute_uri(avatar_url)
        except (ValueError, TypeError):
            return avatar_url

    def get_es_admin(self, obj):
        return bool(
            getattr(obj, "is_staff", False)
            or getattr(obj, "is_superuser", False)
        )

    def get_ms_business_phones(self, obj):
        phones = getattr(obj, "ms_business_phones", None)
        if phones is None:
            return []
        if isinstance(phones, (list, tuple)):
            return [
                _normalize_text(phone)
                for phone in phones
                if _normalize_text(phone)
            ]
        normalized_phone = _normalize_text(phones)
        return [normalized_phone] if normalized_phone else []

    def get_profile_edit_attempts_left(self, obj):
        return _safe_non_negative_int(
            self._get_edit_status(obj).get("attempts_left")
        )

    def get_profile_edit_locked(self, obj):
        return bool(
            self._get_edit_status(obj).get("profile_edit_locked", False)
        )

    def get_profile_edit_lock_reason(self, obj):
        return _normalize_optional_text(
            self._get_edit_status(obj).get("profile_edit_lock_reason")
        )

    def get_profile_edit_until(self, obj):
        return self._get_edit_status(obj).get("profile_edit_until")

    def get_profile_edit_available(self, obj):
        return bool(self._get_edit_status(obj).get("available", False))

    def get_profile_edit_expired(self, obj):
        return bool(self._get_edit_status(obj).get("expired", False))

    def get_profile_edit_seconds_remaining(self, obj):
        status_payload = self._get_edit_status(obj)
        deadline = status_payload.get("profile_edit_until")
        if deadline is None or status_payload.get("expired", False):
            return 0
        remaining = (deadline - timezone.now()).total_seconds()
        return max(0, int(remaining))

    def get_perfil_banner_snoozed(self, obj):
        snooze_until = getattr(obj, "perfil_banner_snooze_until", None)
        return bool(snooze_until is not None and snooze_until > timezone.now())
