"""
Serializer para actualización controlada del perfil del usuario.
Permite editar identificación, facultad, carrera y posponer avisos de perfil.
No gestiona el avatar; eso se maneja en AvatarUpdateSerializer.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from core.models import Facultad, Carrera

User = get_user_model()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    facultad_set = serializers.IntegerField(required=False, allow_null=True)
    carrera_set = serializers.IntegerField(required=False, allow_null=True)
    snooze_hours = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "identificacion",
            "facultad_set",
            "carrera_set",
            "snooze_hours",
        ]

    def validate_identificacion(self, value):
        if value in (None, ""):
            return None

        value = str(value).strip()

        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "La identificación debe tener 10 dígitos numéricos."
            )

        instance = getattr(self, "instance", None)
        qs = User.objects.filter(identificacion=value)

        if instance is not None:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "Esta identificación ya está registrada."
            )

        return value

    def validate_snooze_hours(self, value):
        if value is None:
            return None

        try:
            value = int(value)
        except Exception:
            raise serializers.ValidationError("Las horas deben ser numéricas.")

        if value < 1:
            raise serializers.ValidationError("Las horas deben ser mayores a 0.")

        if value > 24:
            raise serializers.ValidationError("El máximo permitido es 24 horas.")

        return value

    def validate(self, attrs):
        user = self.instance

        is_externo_real = (
            str(getattr(user, "rol", "")).lower() == "autor_externo"
            and str(getattr(user, "auth_source", "")).lower() == "local"
        )

        if is_externo_real:
            attrs["facultad_set"] = None
            attrs["carrera_set"] = None
            return attrs

        facultad_in_payload = "facultad_set" in attrs
        carrera_in_payload = "carrera_set" in attrs

        final_facultad_id = attrs.get("facultad_set", getattr(user, "facultad_id", None))
        final_carrera_id = attrs.get("carrera_set", getattr(user, "carrera_id", None))

        if final_facultad_id is not None:
            facultad_exists = Facultad.objects.filter(pk=final_facultad_id).exists()
            if not facultad_exists:
                raise serializers.ValidationError(
                    {"facultad_set": "La facultad seleccionada no existe."}
                )

        carrera_obj = None

        if final_carrera_id is not None:
            carrera_obj = (
                Carrera.objects.select_related("facultad")
                .filter(pk=final_carrera_id)
                .first()
            )

            if not carrera_obj:
                raise serializers.ValidationError(
                    {"carrera_set": "La carrera seleccionada no existe."}
                )

            if final_facultad_id is None:
                final_facultad_id = carrera_obj.facultad_id
                attrs["facultad_set"] = final_facultad_id

            if carrera_obj.facultad_id != final_facultad_id:
                raise serializers.ValidationError(
                    {"carrera_set": "La carrera no pertenece a la facultad seleccionada."}
                )

        if facultad_in_payload and not carrera_in_payload:
            current_carrera_id = getattr(user, "carrera_id", None)

            if current_carrera_id:
                current_carrera = Carrera.objects.filter(pk=current_carrera_id).first()
                if (
                    final_facultad_id is None
                    or (
                        current_carrera
                        and current_carrera.facultad_id != final_facultad_id
                    )
                ):
                    attrs["carrera_set"] = None
                    final_carrera_id = None

        if bool(final_facultad_id) != bool(final_carrera_id):
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Facultad y carrera deben seleccionarse juntas "
                        "o ambas quedar vacías."
                    )
                }
            )

        return attrs

    def update(self, instance, validated_data):
        update_fields = []

        snooze_hours = validated_data.pop("snooze_hours", None)
        if snooze_hours is not None:
            hours = max(1, min(24, int(snooze_hours)))
            instance.perfil_banner_snooze_until = timezone.now() + timedelta(hours=hours)
            update_fields.append("perfil_banner_snooze_until")

        if "identificacion" in validated_data:
            new_identificacion = validated_data.get("identificacion")
            if instance.identificacion != new_identificacion:
                instance.identificacion = new_identificacion
                update_fields.append("identificacion")

        if "facultad_set" in validated_data:
            new_facultad_id = validated_data.get("facultad_set") or None
            if instance.facultad_id != new_facultad_id:
                instance.facultad_id = new_facultad_id
                update_fields.append("facultad")

        if "carrera_set" in validated_data:
            new_carrera_id = validated_data.get("carrera_set") or None
            if instance.carrera_id != new_carrera_id:
                instance.carrera_id = new_carrera_id
                update_fields.append("carrera")

        if update_fields:
            instance.save(update_fields=list(dict.fromkeys(update_fields)))

        return instance