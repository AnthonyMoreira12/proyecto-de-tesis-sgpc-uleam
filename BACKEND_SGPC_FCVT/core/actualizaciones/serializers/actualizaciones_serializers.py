"""Serializers de campañas y seguimiento de actualización."""

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from core.models import CampaniaActualizacion, CampaniaActualizacionUsuario, Publicacion
from core.actualizaciones.services.actualizaciones_services import progreso_campania


class CampaniaActualizacionSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.SerializerMethodField(read_only=True)
    progreso = serializers.SerializerMethodField(read_only=True)
    comunicacion = serializers.SerializerMethodField(read_only=True)
    esta_vigente = serializers.BooleanField(read_only=True)

    class Meta:
        model = CampaniaActualizacion
        fields = [
            "id",
            "titulo",
            "descripcion",
            "tipo",
            "estado",
            "alcance",
            "fecha_inicio",
            "fecha_fin",
            "solo_incompletos",
            "campos_habilitados",
            "filtros_destinatarios",
            "notificar_internamente",
            "crear_aviso",
            "enviar_correo",
            "creado_por",
            "creado_por_nombre",
            "created_at",
            "updated_at",
            "activada_at",
            "finalizada_at",
            "esta_vigente",
            "progreso",
            "comunicacion",
        ]
        read_only_fields = [
            "estado",
            "creado_por",
            "created_at",
            "updated_at",
            "activada_at",
            "finalizada_at",
        ]

    def get_creado_por_nombre(self, obj):
        user = obj.creado_por
        return f"{getattr(user, 'nombres', '')} {getattr(user, 'apellidos', '')}".strip()

    def get_progreso(self, obj):
        return progreso_campania(obj)

    def get_comunicacion(self, obj):
        try:
            item = obj.comunicacion_global
        except ObjectDoesNotExist:
            return None
        return {
            "id": item.pk,
            "titulo": item.titulo,
            "activa": item.activa,
            "esta_vigente": item.esta_vigente,
            "ruta_accion": item.ruta_accion,
        }

    def validate(self, attrs):
        instance = self.instance
        if instance and instance.estado != CampaniaActualizacion.ESTADO_BORRADOR:
            raise serializers.ValidationError(
                {"detail": "Solo las campañas en borrador pueden modificarse."}
            )

        tipo = attrs.get("tipo", getattr(instance, "tipo", None))
        campos = attrs.get(
            "campos_habilitados",
            getattr(instance, "campos_habilitados", []),
        )
        allowed = CampaniaActualizacion.campos_permitidos_para_tipo(tipo)
        if not isinstance(campos, list) or not campos:
            raise serializers.ValidationError(
                {"campos_habilitados": "Debe seleccionar al menos un campo."}
            )
        invalid = sorted(set(str(item).strip() for item in campos) - allowed)
        if invalid:
            raise serializers.ValidationError(
                {
                    "campos_habilitados": (
                        "Campos no permitidos para este tipo de campaña: "
                        + ", ".join(invalid)
                    )
                }
            )

        alcance = attrs.get("alcance", getattr(instance, "alcance", None))
        filters = attrs.get(
            "filtros_destinatarios",
            getattr(instance, "filtros_destinatarios", {}),
        ) or {}
        required_filter = {
            CampaniaActualizacion.ALCANCE_SEDE: "sede_id",
            CampaniaActualizacion.ALCANCE_FACULTAD: "facultad_id",
            CampaniaActualizacion.ALCANCE_CARRERA: "carrera_id",
            CampaniaActualizacion.ALCANCE_USUARIOS: "usuarios",
        }.get(alcance)
        if required_filter and not filters.get(required_filter):
            raise serializers.ValidationError(
                {"filtros_destinatarios": f"Falta el filtro obligatorio: {required_filter}."}
            )

        return attrs


class CampaniaActualizacionUsuarioSerializer(serializers.ModelSerializer):
    campania_titulo = serializers.CharField(source="campania.titulo", read_only=True)
    campania_tipo = serializers.CharField(source="campania.tipo", read_only=True)
    campania_fecha_fin = serializers.DateTimeField(source="campania.fecha_fin", read_only=True)
    campos_habilitados = serializers.JSONField(source="campania.campos_habilitados", read_only=True)
    usuario_nombre = serializers.SerializerMethodField(read_only=True)
    usuario_email = serializers.EmailField(source="usuario.email", read_only=True)

    class Meta:
        model = CampaniaActualizacionUsuario
        fields = [
            "id",
            "campania",
            "campania_titulo",
            "campania_tipo",
            "campania_fecha_fin",
            "campos_habilitados",
            "usuario",
            "usuario_nombre",
            "usuario_email",
            "estado",
            "campos_pendientes",
            "resumen_pendientes",
            "asignada_at",
            "iniciada_at",
            "completada_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_usuario_nombre(self, obj):
        user = obj.usuario
        return f"{getattr(user, 'nombres', '')} {getattr(user, 'apellidos', '')}".strip()


class MiCampaniaActualizacionSerializer(CampaniaActualizacionUsuarioSerializer):
    """Contrato de lectura para el centro ``Información pendiente``.

    En campañas de publicaciones añade ``es_mia`` a cada registro del resumen.
    El indicador se calcula contra la autoría bibliográfica real
    (``PublicacionAutor -> Autor.usuario``), no contra ``usuario_creador``.

    Esto permite que un administrador pueda alternar entre la vista global
    que ya posee y sus propias publicaciones sin modificar el diagnóstico
    almacenado de la campaña.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data.get("campania_tipo") != CampaniaActualizacion.TIPO_PUBLICACION:
            return data

        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not getattr(user, "is_authenticated", False):
            return data

        summary = data.get("resumen_pendientes")
        if not isinstance(summary, dict):
            return data

        records = summary.get("registros")
        if not isinstance(records, list) or not records:
            return data

        record_ids = []
        for record in records:
            if not isinstance(record, dict):
                continue
            try:
                record_id = int(record.get("id"))
            except (TypeError, ValueError, OverflowError):
                continue
            if record_id > 0:
                record_ids.append(record_id)

        own_ids = set(
            Publicacion.objects.filter(
                pk__in=record_ids,
                participaciones__autor__usuario=user,
            )
            .values_list("pk", flat=True)
            .distinct()
        )

        for record in records:
            if not isinstance(record, dict):
                continue
            try:
                record_id = int(record.get("id"))
            except (TypeError, ValueError, OverflowError):
                record_id = None
            record["es_mia"] = bool(record_id and record_id in own_ids)

        return data