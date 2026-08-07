"""Serializer administrativo de autores."""

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from core.models import Autor


def _text(value):
    return str(value or "").strip()


class AdminAutorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    usuario_id = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    usuario_nombre = serializers.SerializerMethodField()
    usuario_activo = serializers.SerializerMethodField()
    usuario_es_admin = serializers.SerializerMethodField()
    carrera_id = serializers.SerializerMethodField()
    carrera_nombre = serializers.SerializerMethodField()
    facultad_id = serializers.SerializerMethodField()
    facultad_nombre = serializers.SerializerMethodField()
    total_publicaciones = serializers.SerializerMethodField()

    class Meta:
        model = Autor
        fields = [
            "id",
            "identificacion",
            "nombres",
            "apellidos",
            "nombre_completo",
            "correo",
            "institucion",
            "orcid",
            "registro_senescyt",
            "google_scholar",
            "scopus_id",
            "es_externo",
            "usuario_id",
            "usuario_email",
            "usuario_nombre",
            "usuario_activo",
            "usuario_es_admin",
            "carrera_id",
            "carrera_nombre",
            "facultad_id",
            "facultad_nombre",
            "total_publicaciones",
        ]
        read_only_fields = fields

    def _user(self, obj):
        if getattr(obj, "usuario_id", None) is None:
            return None
        try:
            return obj.usuario
        except (ObjectDoesNotExist, AttributeError):
            return None

    def _career(self, obj):
        user = self._user(obj)
        return getattr(user, "carrera", None) if user else None

    def get_nombre_completo(self, obj):
        name = " ".join(
            part
            for part in [_text(obj.nombres), _text(obj.apellidos)]
            if part
        )
        return name or _text(obj.correo) or f"Autor #{obj.pk}"

    def get_usuario_id(self, obj):
        return getattr(obj, "usuario_id", None)

    def get_usuario_email(self, obj):
        user = self._user(obj)
        return _text(getattr(user, "email", "")) or None

    def get_usuario_nombre(self, obj):
        user = self._user(obj)
        if user is None:
            return None

        if callable(getattr(user, "get_full_name", None)):
            name = _text(user.get_full_name())
            if name:
                return name

        return " ".join(
            part
            for part in [
                _text(getattr(user, "nombres", "")),
                _text(getattr(user, "apellidos", "")),
            ]
            if part
        ) or None

    def get_usuario_activo(self, obj):
        user = self._user(obj)
        return bool(user.is_active) if user is not None else None

    def get_usuario_es_admin(self, obj):
        user = self._user(obj)
        return bool(
            user
            and (
                getattr(user, "is_staff", False)
                or getattr(user, "is_superuser", False)
            )
        )

    def get_carrera_id(self, obj):
        user = self._user(obj)
        return getattr(user, "carrera_id", None) if user else None

    def get_carrera_nombre(self, obj):
        career = self._career(obj)
        return _text(getattr(career, "nombre", "")) or None

    def get_facultad_id(self, obj):
        career = self._career(obj)
        return getattr(career, "facultad_id", None) if career else None

    def get_facultad_nombre(self, obj):
        career = self._career(obj)
        faculty = getattr(career, "facultad", None) if career else None
        return _text(getattr(faculty, "nombre", "")) or None

    def get_total_publicaciones(self, obj):
        annotated = getattr(obj, "total_publicaciones", None)
        if annotated is not None:
            return int(annotated)

        cache = getattr(obj, "_prefetched_objects_cache", {})
        if "participaciones" in cache:
            return len(cache["participaciones"])

        return obj.participaciones.count()
