"""
View pública para listar los tipos finales de
publicación disponibles en la búsqueda académica.
"""

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    TIPOS_PUBLICACION_FINALES,
)


class TiposPublicacionListAPIView(
    APIView
):
    """
    Lista los cinco tipos normalizados utilizados
    por la interfaz pública de búsqueda.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny
    ]

    def get(
        self,
        request,
    ):
        data = [
            {
                # Alias histórico utilizado
                # por algunas interfaces.
                "id": codigo,

                # Nombre canónico.
                "codigo": codigo,

                # Alias visible actual.
                "label": label,

                "nombre": label,
            }
            for codigo, label
            in TIPOS_PUBLICACION_FINALES.items()
        ]

        return Response(
            {
                "results": data
            }
        )