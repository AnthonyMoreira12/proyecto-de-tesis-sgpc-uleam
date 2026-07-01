"""
View para listar los tipos finales de publicación disponibles.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    TIPOS_PUBLICACION_FINALES,
)


class TiposPublicacionListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = [
            {"id": codigo, "label": label}
            for codigo, label in TIPOS_PUBLICACION_FINALES.items()
        ]
        return Response({"results": data})  