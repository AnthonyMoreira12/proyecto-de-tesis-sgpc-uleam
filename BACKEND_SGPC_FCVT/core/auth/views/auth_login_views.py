"""
View de autenticación para inicio de sesión local.
"""

from django.contrib.auth import authenticate

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.auth.serializers.auth_login_serializers import LoginSerializer
from core.auth.services.auth_author_sync_services import asegurar_autor_para_usuario


def _avatar_url(user, request=None):
    avatar = getattr(user, "avatar", None)
    if not avatar:
        return None

    name = getattr(avatar, "name", None)
    if not name:
        return None

    try:
        url = avatar.url
    except Exception:
        return None

    if request:
        try:
            return request.build_absolute_uri(url)
        except Exception:
            return url

    return url


def build_local_auth_user_payload(user, request=None):
    return {
        "id": user.id,
        "email": user.email,
        "nombres": user.nombres,
        "apellidos": user.apellidos,
        "rol": user.rol,
        "auth_source": getattr(user, "auth_source", "local"),
        "perfil_completo": bool(getattr(user, "perfil_completo", False)),
        "is_staff": bool(getattr(user, "is_staff", False)),
        "is_superuser": bool(getattr(user, "is_superuser", False)),
        "es_admin": bool(
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
        ),
        "facultad_id": getattr(user, "facultad_id", None),
        "carrera_id": getattr(user, "carrera_id", None),
        "avatar_url": _avatar_url(user, request=request),
    }


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"detail": "Credenciales inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not getattr(user, "is_active", False):
            return Response(
                {"detail": "La cuenta está inactiva."},
                status=status.HTTP_403_FORBIDDEN,
            )

        asegurar_autor_para_usuario(user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Inicio de sesión correcto",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": build_local_auth_user_payload(user, request=request),
            },
            status=status.HTTP_200_OK,
        )