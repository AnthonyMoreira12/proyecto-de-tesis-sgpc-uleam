"""
Serializer principal del perfil de usuario.
Expone datos personales, afiliación académica, avatar, estado administrativo,
sincronización con Microsoft y banderas de edición del perfil.
Complementa el módulo de perfil al entregar una respuesta completa y de solo lectura
para mostrar información institucional, permisos, datos sincronizados y restricciones
de edición del usuario autenticado.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    facultad = serializers.CharField(
        source="facultad.nombre",
        read_only=True,
        allow_null=True,
    )
    carrera = serializers.CharField(
        source="carrera.nombre",
        read_only=True,
        allow_null=True,
    )

    facultad_id = serializers.IntegerField(
        source="facultad.id",
        read_only=True,
        allow_null=True,
    )
    carrera_id = serializers.IntegerField(
        source="carrera.id",
        read_only=True,
        allow_null=True,
    )

    avatar_url = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    es_admin = serializers.SerializerMethodField()

    microsoft_id = serializers.SerializerMethodField()
    ms_graph_id = serializers.SerializerMethodField()
    ms_display_name = serializers.SerializerMethodField()
    ms_given_name = serializers.SerializerMethodField()
    ms_surname = serializers.SerializerMethodField()
    ms_mail = serializers.SerializerMethodField()
    ms_user_principal_name = serializers.SerializerMethodField()
    ms_job_title = serializers.SerializerMethodField()
    ms_department = serializers.SerializerMethodField()
    ms_office_location = serializers.SerializerMethodField()
    ms_business_phones = serializers.SerializerMethodField()
    ms_mobile_phone = serializers.SerializerMethodField()

    profile_edit_attempts_left = serializers.SerializerMethodField()
    profile_edit_locked = serializers.SerializerMethodField()
    profile_edit_lock_reason = serializers.SerializerMethodField()
    profile_edit_until = serializers.DateTimeField(read_only=True, allow_null=True)

    perfil_banner_snooze_until = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nombres",
            "apellidos",
            "full_name",
            "rol",
            "identificacion",
            "facultad",
            "carrera",
            "facultad_id",
            "carrera_id",
            "fecha_registro",
            "avatar_url",
            "auth_source",
            "perfil_completo",
            "ms_last_sync",
            "perfil_banner_snooze_until",
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
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",
            "profile_edit_until",
        ]
        read_only_fields = tuple(fields)

    def _safe(self, obj, attr):
        return getattr(obj, attr, None)

    def get_full_name(self, obj):
        return f"{obj.nombres or ''} {obj.apellidos or ''}".strip()

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if not request or not getattr(obj, "avatar", None):
            return None

        avatar_name = getattr(obj.avatar, "name", None)
        avatar_url = getattr(obj.avatar, "url", None)

        if not avatar_name or not avatar_url:
            return None

        try:
            return request.build_absolute_uri(avatar_url)
        except Exception:
            return avatar_url

    def get_es_admin(self, obj):
        return bool(obj.is_staff or obj.is_superuser)

    def get_microsoft_id(self, obj):
        return self._safe(obj, "microsoft_id")

    def get_ms_graph_id(self, obj):
        return self._safe(obj, "ms_graph_id")

    def get_ms_display_name(self, obj):
        return self._safe(obj, "ms_display_name")

    def get_ms_given_name(self, obj):
        return self._safe(obj, "ms_given_name")

    def get_ms_surname(self, obj):
        return self._safe(obj, "ms_surname")

    def get_ms_mail(self, obj):
        return self._safe(obj, "ms_mail")

    def get_ms_user_principal_name(self, obj):
        return self._safe(obj, "ms_user_principal_name")

    def get_ms_job_title(self, obj):
        return self._safe(obj, "ms_job_title")

    def get_ms_department(self, obj):
        return self._safe(obj, "ms_department")

    def get_ms_office_location(self, obj):
        return self._safe(obj, "ms_office_location")

    def get_ms_business_phones(self, obj):
        return self._safe(obj, "ms_business_phones")

    def get_ms_mobile_phone(self, obj):
        return self._safe(obj, "ms_mobile_phone")

    def get_profile_edit_attempts_left(self, obj):
        return int(getattr(obj, "profile_edit_attempts_left", 0) or 0)

    def get_profile_edit_locked(self, obj):
        return bool(getattr(obj, "profile_edit_locked", False))

    def get_profile_edit_lock_reason(self, obj):
        return getattr(obj, "profile_edit_lock_reason", None)