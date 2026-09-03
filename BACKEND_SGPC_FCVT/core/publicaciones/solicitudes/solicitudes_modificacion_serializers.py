from rest_framework import serializers

from core.models import Publicacion, SolicitudModificacionPublicacion
from core.publicaciones.solicitudes.solicitudes_modificacion_services import (
    campos_sensibles_permitidos,
    crear_solicitud,
)


class SolicitudModificacionPublicacionSerializer(serializers.ModelSerializer):
    publicacion_titulo = serializers.SerializerMethodField()
    solicitante_nombre = serializers.SerializerMethodField()
    revisor_nombre = serializers.SerializerMethodField()
    campos_permitidos = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudModificacionPublicacion
        fields = [
            "id",
            "publicacion",
            "publicacion_titulo",
            "solicitante",
            "solicitante_nombre",
            "estado",
            "motivo",
            "campos_solicitados",
            "cambios_solicitados",
            "datos_anteriores",
            "publicacion_updated_at_solicitud",
            "revisor",
            "revisor_nombre",
            "comentario_resolucion",
            "resuelto_at",
            "aplicado_at",
            "created_at",
            "updated_at",
            "campos_permitidos",
        ]
        read_only_fields = fields

    def _name(self, user):
        if user is None:
            return ""
        value = f"{getattr(user, 'nombres', '')} {getattr(user, 'apellidos', '')}".strip()
        return value or getattr(user, "email", "") or str(user)

    def get_publicacion_titulo(self, obj):
        publicacion = obj.publicacion
        for attr in ("ponencia", "articulo", "libro", "capitulo_libro"):
            related = getattr(publicacion, attr, None)
            if related is None:
                continue
            for field in ("nombre_ponencia", "nombre_articulo", "nombre_libro", "nombre_capitulo"):
                value = getattr(related, field, None)
                if value:
                    return str(value)
        return f"Publicación #{publicacion.pk}"

    def get_solicitante_nombre(self, obj):
        return self._name(obj.solicitante)

    def get_revisor_nombre(self, obj):
        return self._name(obj.revisor)

    def get_campos_permitidos(self, obj):
        return campos_sensibles_permitidos(obj.publicacion)


class SolicitudModificacionPublicacionCreateSerializer(serializers.Serializer):
    publicacion = serializers.PrimaryKeyRelatedField(
        queryset=Publicacion.objects.select_related("tipo").all()
    )
    motivo = serializers.CharField(max_length=4000)
    cambios_solicitados = serializers.JSONField()

    def create(self, validated_data):
        request = self.context.get("request")
        return crear_solicitud(
            publicacion=validated_data["publicacion"],
            solicitante=request.user,
            motivo=validated_data["motivo"],
            cambios=validated_data["cambios_solicitados"],
            request=request,
        )


class ResolverSolicitudModificacionSerializer(serializers.Serializer):
    comentario = serializers.CharField(required=False, allow_blank=True, max_length=4000)
