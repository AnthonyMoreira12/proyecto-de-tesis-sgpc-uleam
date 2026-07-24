"""Serializers administrativos de publicaciones."""

from rest_framework import serializers

from core.publicaciones.serializers.read.publicaciones_detalle_serializers import (
    PublicacionDetalleSerializer,
)
from core.publicaciones.serializers.read.publicaciones_listado_serializers import (
    PublicacionListadoSerializer,
)


ADMIN_FIELDS = (
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
    "tiene_pdf_principal",
    "tiene_adjuntos",
    "tiene_pdf",
    "autor_principal_id",
    "autor_principal",
    "autor_principal_email",
    "autores_total",
)


def _merge(base_fields):
    return tuple(dict.fromkeys([*base_fields, *ADMIN_FIELDS]))


def _text(value):
    return str(value or "").strip()


def _name(person):
    if person is None:
        return None

    if callable(getattr(person, "get_full_name", None)):
        name = _text(person.get_full_name())
        if name:
            return name

    name = " ".join(
        part
        for part in [
            _text(getattr(person, "nombres", "")),
            _text(getattr(person, "apellidos", "")),
        ]
        if part
    )
    return (
        name
        or _text(getattr(person, "email", ""))
        or _text(getattr(person, "correo", ""))
        or None
    )


class _AdminFieldsMixin(serializers.Serializer):
    usuario_creador_nombre = serializers.SerializerMethodField()
    usuario_creador_email = serializers.SerializerMethodField()
    admin_registrador_nombre = serializers.SerializerMethodField()
    admin_registrador_email = serializers.SerializerMethodField()
    adjuntos_total = serializers.SerializerMethodField()
    tiene_pdf_principal = serializers.SerializerMethodField()
    tiene_adjuntos = serializers.SerializerMethodField()
    tiene_pdf = serializers.SerializerMethodField()
    autor_principal_id = serializers.SerializerMethodField()
    autor_principal = serializers.SerializerMethodField()
    autor_principal_email = serializers.SerializerMethodField()
    autores_total = serializers.SerializerMethodField()

    def _participations(self, obj):
        ordered = getattr(obj, "participaciones_ordenadas", None)
        if ordered is not None:
            return list(ordered)

        cache = getattr(obj, "_prefetched_objects_cache", {})
        if "participaciones" in cache:
            return list(cache["participaciones"])

        return list(
            obj.participaciones
            .select_related("autor", "autor__usuario")
            .order_by("orden", "id")
        )

    def _principal(self, obj):
        first = None

        for relation in self._participations(obj):
            if getattr(relation, "autor", None) is None:
                continue

            first = first or relation

            if (
                _text(relation.rol_autoria).lower() == "principal"
                or relation.orden == 1
            ):
                return relation

        return first

    def get_usuario_creador_nombre(self, obj):
        return _name(getattr(obj, "usuario_creador", None))

    def get_usuario_creador_email(self, obj):
        user = getattr(obj, "usuario_creador", None)
        return _text(getattr(user, "email", "")) or None

    def get_admin_registrador_nombre(self, obj):
        return _name(getattr(obj, "admin_registrador", None))

    def get_admin_registrador_email(self, obj):
        user = getattr(obj, "admin_registrador", None)
        return _text(getattr(user, "email", "")) or None

    def get_adjuntos_total(self, obj):
        annotated = getattr(obj, "adjuntos_total", None)
        if annotated is not None:
            return int(annotated)

        ordered = getattr(obj, "archivos_ordenados", None)
        if ordered is not None:
            return len(ordered)

        return obj.archivos.count()

    def get_tiene_pdf_principal(self, obj):
        annotated = getattr(obj, "tiene_pdf_principal", None)
        if annotated is not None:
            return bool(annotated)

        return bool(
            _text(
                getattr(
                    getattr(obj, "archivo_pdf", None),
                    "name",
                    "",
                )
            )
        )

    def get_tiene_adjuntos(self, obj):
        annotated = getattr(obj, "tiene_adjuntos", None)
        if annotated is not None:
            return bool(annotated)

        return self.get_adjuntos_total(obj) > 0

    def get_tiene_pdf(self, obj):
        return (
            self.get_tiene_pdf_principal(obj)
            or self.get_tiene_adjuntos(obj)
        )

    def get_autor_principal_id(self, obj):
        relation = self._principal(obj)
        return getattr(relation, "autor_id", None)

    def get_autor_principal(self, obj):
        relation = self._principal(obj)
        return _name(getattr(relation, "autor", None)) or "—"

    def get_autor_principal_email(self, obj):
        relation = self._principal(obj)
        author = getattr(relation, "autor", None)
        return _text(getattr(author, "correo", "")) or None

    def get_autores_total(self, obj):
        return len(self._participations(obj))


class AdminPublicacionListadoSerializer(
    _AdminFieldsMixin,
    PublicacionListadoSerializer,
):
    class Meta(PublicacionListadoSerializer.Meta):
        fields = _merge(PublicacionListadoSerializer.Meta.fields)
        read_only_fields = fields


class AdminPublicacionDetalleSerializer(
    _AdminFieldsMixin,
    PublicacionDetalleSerializer,
):
    class Meta(PublicacionDetalleSerializer.Meta):
        fields = _merge(PublicacionDetalleSerializer.Meta.fields)
        read_only_fields = fields
