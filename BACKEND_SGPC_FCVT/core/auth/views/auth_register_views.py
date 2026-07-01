"""
View para registro de usuarios externos en el sistema.
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.auth.serializers.auth_register_serializers import RegisterSerializer
from core.auth.services.auth_author_sync_services import asegurar_autor_para_usuario
from core.auth.views.auth_login_views import build_local_auth_user_payload


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        asegurar_autor_para_usuario(user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Usuario registrado correctamente",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": build_local_auth_user_payload(user, request=request),
            },
            status=status.HTTP_201_CREATED,
        )