# Serializer de inicio de sesión:
# valida las credenciales básicas del usuario, recibiendo correo electrónico y contraseña para autenticación.

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)