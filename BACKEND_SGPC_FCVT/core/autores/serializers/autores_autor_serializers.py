from rest_framework import serializers

from core.models import Autor
from core.autores.services.autores_usuario_sync_services import buscar_autor_existente


class AutorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField(read_only=True)
    usuario_id = serializers.IntegerField(source="usuario.id", read_only=True)
    correo_resuelto = serializers.SerializerMethodField(read_only=True)
    es_admin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Autor
        fields = [
            "id",
            "nombres",
            "apellidos",
            "identificacion",
            "correo",
            "correo_resuelto",
            "institucion",
            "es_externo",
            "usuario",
            "usuario_id",
            "nombre_completo",
            "es_admin",
        ]
        read_only_fields = [
            "id",
            "es_externo",
            "usuario",
            "usuario_id",
            "nombre_completo",
            "correo_resuelto",
            "es_admin",
        ]
        extra_kwargs = {
            "correo": {
                "required": True,
                "allow_blank": False,
                "allow_null": False,
            },
            "identificacion": {
                "required": True,
                "allow_blank": False,
                "allow_null": False,
            },
            "nombres": {
                "required": True,
            },
            "apellidos": {
                "required": True,
            },
            "institucion": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        }

    def get_nombre_completo(self, obj):
        return f"{obj.nombres or ''} {obj.apellidos or ''}".strip()

    def get_correo_resuelto(self, obj):
        usuario = getattr(obj, "usuario", None)
        if usuario and getattr(usuario, "email", None):
            return usuario.email
        return obj.correo or None

    def get_es_admin(self, obj):
        usuario = getattr(obj, "usuario", None)
        if not usuario:
            return False

        return bool(
            getattr(usuario, "is_staff", False)
            or getattr(usuario, "is_superuser", False)
        )

    def validate_nombres(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Los nombres son obligatorios.")
        return value

    def validate_apellidos(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Los apellidos son obligatorios.")
        return value

    def validate_identificacion(self, value):
        if value in (None, ""):
            raise serializers.ValidationError("La identificación es obligatoria.")

        value = str(value).strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "La identificación debe contener solo números."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "La identificación debe tener 10 dígitos numéricos."
            )

        return value

    def validate_correo(self, value):
        if value in (None, ""):
            raise serializers.ValidationError("El correo es obligatorio.")

        value = str(value).strip().lower()

        if not value:
            raise serializers.ValidationError("El correo es obligatorio.")

        return value

    def validate_institucion(self, value):
        value = str(value or "").strip()

        if not value:
            return None

        if len(value) > 255:
            raise serializers.ValidationError(
                "La institución no puede superar 255 caracteres."
            )

        return value

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        nombres = (
            attrs.get("nombres", getattr(instance, "nombres", "")) or ""
        ).strip()

        apellidos = (
            attrs.get("apellidos", getattr(instance, "apellidos", "")) or ""
        ).strip()

        identificacion = attrs.get(
            "identificacion",
            getattr(instance, "identificacion", None) if instance else None,
        )

        correo = attrs.get(
            "correo",
            getattr(instance, "correo", None) if instance else None,
        )

        found = buscar_autor_existente(
            identificacion=identificacion,
            correo=correo,
            nombres=nombres,
            apellidos=apellidos,
            exclude_autor_id=getattr(instance, "id", None),
        )

        if found["exists"]:
            match_type = found["match_type"]

            if match_type == "identificacion":
                raise serializers.ValidationError(
                    {"identificacion": "Ya existe un autor con esta identificación."}
                )

            if match_type == "correo":
                raise serializers.ValidationError(
                    {"correo": "Ya existe un autor con este correo."}
                )

            raise serializers.ValidationError(
                {
                    "detail": (
                        "Ya existe un autor registrado con los mismos nombres y apellidos."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("usuario", None)
        validated_data.pop("es_externo", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("usuario", None)
        validated_data.pop("es_externo", None)
        return super().update(instance, validated_data)