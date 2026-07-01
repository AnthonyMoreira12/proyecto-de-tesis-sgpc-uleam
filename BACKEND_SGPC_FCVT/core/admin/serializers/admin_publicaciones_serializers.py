# Serializers administrativos de publicaciones:
# extienden los serializers de listado y detalle para incluir datos de auditoría,
# usuario creador, administrador registrador, adjuntos, disponibilidad de PDF y autor principal.

from rest_framework import serializers

from core.publicaciones.serializers.read.publicaciones_detalle_serializers import (
    PublicacionDetalleSerializer,
)
from core.publicaciones.serializers.read.publicaciones_listado_serializers import (
    PublicacionListadoSerializer,
)


class _AdminPublicacionFieldsMixin(serializers.Serializer):
    usuario_creador_id = serializers.SerializerMethodField()
    usuario_creador_nombre = serializers.SerializerMethodField()
    usuario_creador_email = serializers.SerializerMethodField()

    registrado_por_admin = serializers.BooleanField(read_only=True)

    admin_registrador_id = serializers.SerializerMethodField()
    admin_registrador_nombre = serializers.SerializerMethodField()
    admin_registrador_email = serializers.SerializerMethodField()

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    adjuntos_total = serializers.SerializerMethodField()
    tiene_pdf = serializers.SerializerMethodField()
    autor_principal = serializers.SerializerMethodField()

    def _get_participaciones(self, obj):
        participaciones = getattr(obj, "participaciones_ordenadas", None)
        if participaciones is not None:
            return participaciones

        cache = getattr(obj, "_prefetched_objects_cache", {})
        if "participaciones" in cache:
            return cache["participaciones"]

        try:
            return obj.participaciones.select_related("autor").order_by("orden", "id")
        except Exception:
            return []

    def get_usuario_creador_id(self, obj):
        return getattr(getattr(obj, "usuario_creador", None), "id", None)

    def get_usuario_creador_nombre(self, obj):
        usuario = getattr(obj, "usuario_creador", None)
        if not usuario:
            return None
        return f"{usuario.nombres or ''} {usuario.apellidos or ''}".strip()

    def get_usuario_creador_email(self, obj):
        return getattr(getattr(obj, "usuario_creador", None), "email", None)

    def get_admin_registrador_id(self, obj):
        return getattr(getattr(obj, "admin_registrador", None), "id", None)

    def get_admin_registrador_nombre(self, obj):
        usuario = getattr(obj, "admin_registrador", None)
        if not usuario:
            return None
        return f"{usuario.nombres or ''} {usuario.apellidos or ''}".strip()

    def get_admin_registrador_email(self, obj):
        return getattr(getattr(obj, "admin_registrador", None), "email", None)

    def get_adjuntos_total(self, obj):
        annotated = getattr(obj, "adjuntos_total", None)
        if annotated is not None:
            try:
                return int(annotated)
            except Exception:
                pass

        cache = getattr(obj, "_prefetched_objects_cache", {})
        if "archivos" in cache:
            try:
                return len(cache["archivos"])
            except Exception:
                return 0

        try:
            return obj.archivos.count()
        except Exception:
            return 0

    def get_tiene_pdf(self, obj):
        archivo_pdf_name = str(getattr(getattr(obj, "archivo_pdf", None), "name", "") or "").strip()
        return bool(archivo_pdf_name) or self.get_adjuntos_total(obj) > 0

    def get_autor_principal(self, obj):
        participaciones = self._get_participaciones(obj)

        principal = None
        fallback = None

        for rel in participaciones:
            autor = getattr(rel, "autor", None)
            if not autor:
                continue

            nombre = f"{autor.nombres or ''} {autor.apellidos or ''}".strip()
            if not nombre:
                nombre = str(getattr(autor, "correo", "") or "").strip() or "Autor"

            if fallback is None:
                fallback = nombre

            if getattr(rel, "orden", None) == 1 or getattr(rel, "rol_autoria", None) == "principal":
                principal = nombre
                break

        return principal or fallback or "—"


class AdminPublicacionListadoSerializer(
    _AdminPublicacionFieldsMixin,
    PublicacionListadoSerializer,
):
    class Meta(PublicacionListadoSerializer.Meta):
        fields = PublicacionListadoSerializer.Meta.fields + [
            "usuario_creador_id",
            "usuario_creador_nombre",
            "usuario_creador_email",
            "registrado_por_admin",
            "admin_registrador_id",
            "admin_registrador_nombre",
            "admin_registrador_email",
            "created_at",
            "updated_at",
            "adjuntos_total",
            "tiene_pdf",
            "autor_principal",
        ]
        read_only_fields = fields


class AdminPublicacionDetalleSerializer(
    _AdminPublicacionFieldsMixin,
    PublicacionDetalleSerializer,
):
    class Meta(PublicacionDetalleSerializer.Meta):
        fields = PublicacionDetalleSerializer.Meta.fields + [
            "usuario_creador_id",
            "usuario_creador_nombre",
            "usuario_creador_email",
            "registrado_por_admin",
            "admin_registrador_id",
            "admin_registrador_nombre",
            "admin_registrador_email",
            "created_at",
            "updated_at",
            "adjuntos_total",
            "tiene_pdf",
            "autor_principal",
        ]
        read_only_fields = fields