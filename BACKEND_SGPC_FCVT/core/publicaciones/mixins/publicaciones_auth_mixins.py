from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class PublicacionesJWTAuthAPIViewMixin:
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]