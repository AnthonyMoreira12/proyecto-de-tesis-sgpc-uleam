"""
Serializer para registro de usuarios externos.
Valida contraseña, normaliza email e identificación y crea el usuario local.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        min_length=8,
        max_length=128,
    )

    class Meta:
        model = User
        fields = ("email", "nombres", "apellidos", "identificacion", "password")
        extra_kwargs = {
            "identificacion": {"required": False, "allow_null": True},
        }

    def validate_email(self, value):
        value = (value or "").strip().lower()

        if not value:
            raise serializers.ValidationError("El correo electrónico es obligatorio.")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo.")

        return value

    def validate_identificacion(self, value):
        if value in (None, ""):
            return None

        value = str(value).strip()

        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "La identificación debe tener 10 dígitos numéricos."
            )

        if User.objects.filter(identificacion=value).exists():
            raise serializers.ValidationError(
                "Esta identificación ya está registrada."
            )

        return value

    def validate(self, attrs):
        attrs["nombres"] = str(attrs.get("nombres") or "").strip()
        attrs["apellidos"] = str(attrs.get("apellidos") or "").strip()

        if not attrs["nombres"]:
            raise serializers.ValidationError(
                {"nombres": "Los nombres son obligatorios."}
            )

        if not attrs["apellidos"]:
            raise serializers.ValidationError(
                {"apellidos": "Los apellidos son obligatorios."}
            )

        provisional_user = User(
            email=attrs.get("email"),
            nombres=attrs.get("nombres", ""),
            apellidos=attrs.get("apellidos", ""),
            identificacion=attrs.get("identificacion"),
            rol="autor_externo",
            auth_source="local",
        )

        try:
            validate_password(attrs["password"], user=provisional_user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        validated_data.setdefault("rol", "autor_externo")
        validated_data.setdefault("auth_source", "local")
        validated_data.setdefault("is_active", True)
        validated_data["perfil_completo"] = bool(validated_data.get("identificacion"))

        try:
            user = User.objects.create_user(password=password, **validated_data)
            return user
        except IntegrityError as exc:
            error_text = str(exc).lower()

            if "email" in error_text:
                raise serializers.ValidationError(
                    {"email": "Ya existe un usuario con este correo."}
                )

            if "identificacion" in error_text:
                raise serializers.ValidationError(
                    {"identificacion": "Esta identificación ya está registrada."}
                )

            raise serializers.ValidationError(
                {"detail": "No se pudo completar el registro por conflicto de unicidad."}
            )