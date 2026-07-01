"""
Serializer para actualización del avatar del usuario.
Expone únicamente el campo de imagen de perfil.
Valida formato, extensión y tamaño máximo.
Complementa el módulo de perfil al controlar que la imagen subida sea segura,
compatible con el sistema y no supere el límite permitido para almacenamiento.
"""

import os

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


MAX_AVATAR_BYTES = 1 * 1024 * 1024  # 1 MB
ALLOWED_AVATAR_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class AvatarUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=True)

    class Meta:
        model = User
        fields = ["avatar"]

    def validate_avatar(self, value):
        if not value:
            raise serializers.ValidationError("Debe adjuntar una imagen.")

        file_name = str(getattr(value, "name", "") or "").lower()
        ext = os.path.splitext(file_name)[1]

        if ext not in ALLOWED_AVATAR_EXTENSIONS:
            raise serializers.ValidationError(
                "Formato no permitido. Usa JPG, PNG o WEBP."
            )

        content_type = getattr(value, "content_type", None)
        if content_type and content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Formato no permitido. Usa JPG, PNG o WEBP."
            )

        file_size = int(getattr(value, "size", 0) or 0)
        if file_size > MAX_AVATAR_BYTES:
            raise serializers.ValidationError(
                "La imagen supera el tamaño máximo de 1 MB."
            )

        return value