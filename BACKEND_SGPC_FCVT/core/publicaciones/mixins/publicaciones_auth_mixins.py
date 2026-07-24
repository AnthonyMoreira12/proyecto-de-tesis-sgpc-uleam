"""
Mixins de autenticación para las vistas de publicaciones.

Centraliza la configuración JWT utilizada por las
APIView del módulo de publicaciones.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class PublicacionesJWTAuthAPIViewMixin:
    """
    Añade autenticación JWT y exige un usuario autenticado.

    Está pensado para utilizarse con APIView:

        class MiVista(
            PublicacionesJWTAuthAPIViewMixin,
            APIView,
        ):
            ...
    """

    authentication_classes = (
        JWTAuthentication,
    )

    permission_classes = (
        IsAuthenticated,
    )