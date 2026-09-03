"""
Serializers de notificaciones internas.

La API entrega además una representación legible de la publicación
asociada y los metadatos funcionales de la notificación. Estos últimos
son necesarios para flujos administrativos como las solicitudes de
extensión del plazo de edición del perfil.
"""

from rest_framework import serializers

from core.models import Notificacion
from core.notificaciones.utils import (
    obtener_nombre_tipo_publicacion,
    obtener_titulo_publicacion,
)


def _text(value):
    return str(value or "").strip()


class NotificacionSerializer(serializers.ModelSerializer):
    tipo_label = serializers.SerializerMethodField()
    publicacion_titulo = serializers.SerializerMethodField()
    publicacion_tipo = serializers.SerializerMethodField()
    publicacion_estado = serializers.SerializerMethodField()

    class Meta:
        model = Notificacion
        fields = [
            "id",
            "tipo",
            "tipo_label",
            "titulo",
            "mensaje",
            "publicacion_id",
            "publicacion_titulo",
            "publicacion_tipo",
            "publicacion_estado",
            "leida",
            "leida_at",
            "visible_en_bandeja",
            "metadata",
            "email_programado",
            "email_enviado",
            "created_at",
        ]
        read_only_fields = fields

    def get_tipo_label(self, obj):
        labels = {
            Notificacion.TIPO_PUBLICACION_ENVIADA:
                "Enviada a revisión",
            Notificacion.TIPO_PUBLICACION_OBSERVADA:
                "Correcciones solicitadas",
            Notificacion.TIPO_PUBLICACION_APROBADA:
                "Publicación aprobada",
            Notificacion.TIPO_PUBLICACION_RECHAZADA:
                "Publicación rechazada",
            Notificacion.TIPO_NUEVA_PUBLICACION_REVISION:
                "Nueva publicación para revisar",
            Notificacion.TIPO_PUBLICACION_REENVIADA:
                "Publicación reenviada para revisión",
            Notificacion.TIPO_SOLICITUD_EXTENSION_PERFIL:
                "Solicitud de extensión de perfil",
            Notificacion.TIPO_EXTENSION_PERFIL_APROBADA:
                "Extensión de perfil aprobada",
            Notificacion.TIPO_EXTENSION_PERFIL_RECHAZADA:
                "Extensión de perfil rechazada",
            Notificacion.TIPO_CAMPANIA_ACTUALIZACION:
                "Actualización de información",
            Notificacion.TIPO_RECORDATORIO_ACTUALIZACION:
                "Recordatorio de actualización",
        }

        return labels.get(
            obj.tipo,
            obj.get_tipo_display(),
        )

    def get_publicacion_titulo(self, obj):
        metadata = (
            obj.metadata
            if isinstance(obj.metadata, dict)
            else {}
        )

        snapshot = _text(
            metadata.get("publicacion_titulo")
        )

        if snapshot:
            return snapshot

        return obtener_titulo_publicacion(
            getattr(obj, "publicacion", None)
        )

    def get_publicacion_tipo(self, obj):
        metadata = (
            obj.metadata
            if isinstance(obj.metadata, dict)
            else {}
        )

        snapshot = _text(
            metadata.get("publicacion_tipo")
        )

        if snapshot:
            return snapshot

        return obtener_nombre_tipo_publicacion(
            getattr(obj, "publicacion", None)
        )

    def get_publicacion_estado(self, obj):
        publicacion = getattr(
            obj,
            "publicacion",
            None,
        )

        return _text(
            getattr(publicacion, "estado", None)
        )
