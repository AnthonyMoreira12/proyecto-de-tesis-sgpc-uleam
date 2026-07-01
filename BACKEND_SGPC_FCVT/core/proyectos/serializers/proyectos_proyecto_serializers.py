from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from core.models import Proyecto
from core.proyectos.services.proyectos_proyecto_services import (
    autores_payload_tiene_principal,
    normalize_proyecto_autores_payload,
    proyecto_tiene_investigador_principal,
    sync_proyecto_autores,
)


class EmptyStringToNoneDateField(serializers.DateField):
    def to_internal_value(self, value):
        if value in ("", None):
            return None
        return super().to_internal_value(value)


class EmptyStringToNoneIntegerField(serializers.IntegerField):
    def to_internal_value(self, value):
        if value in ("", None):
            return None
        return super().to_internal_value(value)


class FlexibleJSONField(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class ProyectoAutorReadSerializer(serializers.Serializer):
    participacion_id = serializers.IntegerField(source="id", read_only=True)
    id = serializers.IntegerField(source="autor.id", read_only=True)
    nombres = serializers.CharField(source="autor.nombres", read_only=True)
    apellidos = serializers.CharField(source="autor.apellidos", read_only=True)
    correo = serializers.EmailField(source="autor.correo", read_only=True, allow_null=True)
    es_externo = serializers.BooleanField(source="autor.es_externo", read_only=True)
    rol = serializers.CharField(read_only=True)
    rol_label = serializers.CharField(source="get_rol_display", read_only=True)
    orden = serializers.IntegerField(read_only=True)
    nombre_completo = serializers.SerializerMethodField()

    def get_nombre_completo(self, obj):
        nombres = getattr(obj.autor, "nombres", "") or ""
        apellidos = getattr(obj.autor, "apellidos", "") or ""
        return f"{nombres} {apellidos}".strip()


class ProyectoListSerializer(serializers.ModelSerializer):
    facultad = serializers.CharField(
        source="carrera.facultad.nombre",
        read_only=True,
    )
    carrera_nombre = serializers.CharField(
        source="carrera.nombre",
        read_only=True,
    )
    estado_label = serializers.CharField(
        source="get_estado_display",
        read_only=True,
    )
    fecha_fin_vigente = serializers.DateField(read_only=True)
    archivo_pdf_url = serializers.SerializerMethodField(read_only=True)
    autores_resumen = serializers.SerializerMethodField()
    autores_total = serializers.SerializerMethodField()
    tiene_investigador_principal = serializers.SerializerMethodField()
    equipo_pendiente = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "estado",
            "estado_label",
            "carrera",
            "carrera_nombre",
            "facultad",
            "fecha_inicio",
            "fecha_fin_planificada",
            "fecha_fin_prorrogada",
            "fecha_fin_vigente",
            "fecha_cierre",
            "anio_inicio",
            "anio_fin",
            "archivo_pdf_url",
            "autores_resumen",
            "autores_total",
            "tiene_investigador_principal",
            "equipo_pendiente",
        ]
        read_only_fields = fields

    def _get_participaciones(self, obj):
        participaciones = getattr(obj, "participaciones", None)

        if participaciones is None:
            return []

        return list(participaciones.all())

    def get_archivo_pdf_url(self, obj):
        archivo = getattr(obj, "archivo_pdf", None)
        if not archivo:
            return None

        try:
            request = self.context.get("request")
            url = archivo.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None

    def get_autores_resumen(self, obj):
        items = []

        for item in self._get_participaciones(obj):
            autor = item.autor
            nombre = f"{autor.nombres} {autor.apellidos}".strip()

            items.append(
                {
                    "id": autor.id,
                    "nombre": nombre,
                    "nombres": autor.nombres,
                    "apellidos": autor.apellidos,
                    "correo": autor.correo,
                    "rol": item.rol,
                    "rol_label": item.get_rol_display(),
                    "orden": item.orden,
                }
            )

        return items

    def get_autores_total(self, obj):
        return len(self._get_participaciones(obj))

    def get_tiene_investigador_principal(self, obj):
        return any(
            item.rol == "principal"
            for item in self._get_participaciones(obj)
        )

    def get_equipo_pendiente(self, obj):
        return self.get_autores_total(obj) == 0


class ProyectoSerializer(serializers.ModelSerializer):
    facultad = serializers.CharField(
        source="carrera.facultad.nombre",
        read_only=True,
    )
    carrera_nombre = serializers.CharField(
        source="carrera.nombre",
        read_only=True,
    )
    creado_por = serializers.PrimaryKeyRelatedField(read_only=True)

    estado = serializers.ChoiceField(
        choices=Proyecto.ESTADOS,
        required=False,
    )
    estado_label = serializers.CharField(
        source="get_estado_display",
        read_only=True,
    )

    fecha_inicio = EmptyStringToNoneDateField(required=False, allow_null=True)
    fecha_fin_planificada = EmptyStringToNoneDateField(required=False, allow_null=True)
    fecha_fin_prorrogada = EmptyStringToNoneDateField(required=False, allow_null=True)
    fecha_cierre = EmptyStringToNoneDateField(required=False, allow_null=True)

    anio_inicio = EmptyStringToNoneIntegerField(required=False, allow_null=True)
    anio_fin = EmptyStringToNoneIntegerField(required=False, allow_null=True)

    fecha_fin_vigente = serializers.DateField(read_only=True)

    autores = ProyectoAutorReadSerializer(
        source="participaciones",
        many=True,
        read_only=True,
    )
    autores_data = FlexibleJSONField(write_only=True, required=False)

    autores_total = serializers.SerializerMethodField()
    tiene_investigador_principal = serializers.SerializerMethodField()
    equipo_pendiente = serializers.SerializerMethodField()

    archivo_pdf_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Proyecto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "estado",
            "estado_label",
            "carrera",
            "carrera_nombre",
            "facultad",
            "fecha_inicio",
            "fecha_fin_planificada",
            "fecha_fin_prorrogada",
            "fecha_fin_vigente",
            "fecha_cierre",
            "anio_inicio",
            "anio_fin",
            "archivo_pdf",
            "archivo_pdf_url",
            "autores",
            "autores_data",
            "autores_total",
            "tiene_investigador_principal",
            "equipo_pendiente",
            "fecha_creacion",
            "creado_por",
        ]
        read_only_fields = [
            "id",
            "carrera_nombre",
            "facultad",
            "fecha_fin_vigente",
            "archivo_pdf_url",
            "autores",
            "autores_total",
            "tiene_investigador_principal",
            "equipo_pendiente",
            "fecha_creacion",
            "creado_por",
            "estado_label",
        ]

    def _get_participaciones(self, obj):
        participaciones = getattr(obj, "participaciones", None)

        if participaciones is None:
            return []

        return list(participaciones.all())

    def get_archivo_pdf_url(self, obj):
        archivo = getattr(obj, "archivo_pdf", None)
        if not archivo:
            return None

        try:
            request = self.context.get("request")
            url = archivo.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None

    def get_autores_total(self, obj):
        return len(self._get_participaciones(obj))

    def get_tiene_investigador_principal(self, obj):
        return any(
            item.rol == "principal"
            for item in self._get_participaciones(obj)
        )

    def get_equipo_pendiente(self, obj):
        return self.get_autores_total(obj) == 0

    def validate_nombre(self, value):
        value = (value or "").strip()

        if not value:
            raise serializers.ValidationError(
                "El nombre del proyecto es obligatorio."
            )

        return value

    def validate_autores_data(self, value):
        return normalize_proyecto_autores_payload(value)

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        fecha_inicio = attrs.get(
            "fecha_inicio",
            getattr(instance, "fecha_inicio", None),
        )
        fecha_fin_planificada = attrs.get(
            "fecha_fin_planificada",
            getattr(instance, "fecha_fin_planificada", None),
        )
        fecha_fin_prorrogada = attrs.get(
            "fecha_fin_prorrogada",
            getattr(instance, "fecha_fin_prorrogada", None),
        )
        fecha_cierre = attrs.get(
            "fecha_cierre",
            getattr(instance, "fecha_cierre", None),
        )

        anio_inicio = attrs.get(
            "anio_inicio",
            getattr(instance, "anio_inicio", None),
        )
        anio_fin = attrs.get(
            "anio_fin",
            getattr(instance, "anio_fin", None),
        )

        estado = attrs.get(
            "estado",
            getattr(instance, "estado", "nuevo"),
        )
        estado = str(estado or "nuevo").strip().lower()

        if estado == "cierre" and not fecha_cierre:
            fecha_cierre = timezone.now().date()
            attrs["fecha_cierre"] = fecha_cierre

        if "estado" in attrs and estado != "cierre":
            fecha_cierre = None
            attrs["fecha_cierre"] = None

        if fecha_inicio and (
            "fecha_inicio" in attrs or not anio_inicio
        ):
            if "anio_inicio" not in attrs or attrs.get("anio_inicio") in ("", None):
                anio_inicio = fecha_inicio.year
                attrs["anio_inicio"] = anio_inicio

        fecha_fin_referencia = (
            fecha_fin_prorrogada
            or fecha_fin_planificada
            or fecha_cierre
        )

        if fecha_fin_referencia and (
            "fecha_fin_prorrogada" in attrs
            or "fecha_fin_planificada" in attrs
            or "fecha_cierre" in attrs
            or not anio_fin
        ):
            if "anio_fin" not in attrs or attrs.get("anio_fin") in ("", None):
                anio_fin = fecha_fin_referencia.year
                attrs["anio_fin"] = anio_fin

        if fecha_inicio and anio_inicio and fecha_inicio.year != anio_inicio:
            raise serializers.ValidationError(
                {
                    "anio_inicio": (
                        "El año de inicio no coincide con la fecha de inicio."
                    )
                }
            )

        if fecha_fin_referencia and anio_fin and fecha_fin_referencia.year != anio_fin:
            raise serializers.ValidationError(
                {
                    "anio_fin": (
                        "El año de finalización no coincide con la fecha final registrada."
                    )
                }
            )

        if anio_inicio and anio_fin and anio_fin < anio_inicio:
            raise serializers.ValidationError(
                {
                    "anio_fin": (
                        "El año de finalización no puede ser menor al año de inicio."
                    )
                }
            )

        if fecha_inicio and fecha_fin_planificada:
            if fecha_fin_planificada < fecha_inicio:
                raise serializers.ValidationError(
                    {
                        "fecha_fin_planificada": (
                            "La fecha de finalización planificada no puede ser menor a la fecha de inicio."
                        )
                    }
                )

        if fecha_inicio and fecha_fin_prorrogada:
            if fecha_fin_prorrogada < fecha_inicio:
                raise serializers.ValidationError(
                    {
                        "fecha_fin_prorrogada": (
                            "La fecha prorrogada no puede ser menor a la fecha de inicio."
                        )
                    }
                )

        if fecha_fin_planificada and fecha_fin_prorrogada:
            if fecha_fin_prorrogada < fecha_fin_planificada:
                raise serializers.ValidationError(
                    {
                        "fecha_fin_prorrogada": (
                            "La fecha prorrogada no puede ser menor a la fecha planificada."
                        )
                    }
                )

        if fecha_cierre and fecha_inicio:
            if fecha_cierre < fecha_inicio:
                raise serializers.ValidationError(
                    {
                        "fecha_cierre": (
                            "La fecha de cierre no puede ser menor a la fecha de inicio."
                        )
                    }
                )

        autores_data = attrs.get("autores_data", None)

        if estado == "cierre":
            if autores_data is not None:
                tiene_principal = autores_payload_tiene_principal(autores_data)
            else:
                tiene_principal = proyecto_tiene_investigador_principal(instance)

            if not tiene_principal:
                raise serializers.ValidationError(
                    {
                        "autores_data": (
                            "Para cerrar el proyecto debe existir al menos un investigador principal."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        autores_data = validated_data.pop("autores_data", None)
        proyecto = Proyecto.objects.create(**validated_data)

        if autores_data is not None:
            sync_proyecto_autores(proyecto, autores_data)

        return proyecto

    @transaction.atomic
    def update(self, instance, validated_data):
        autores_data = validated_data.pop("autores_data", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        if autores_data is not None:
            sync_proyecto_autores(instance, autores_data)

        return instance