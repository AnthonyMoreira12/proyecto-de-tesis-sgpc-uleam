"""
ViewSet para registrar y consultar libros.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Libro
from core.publicaciones.mixins.publicaciones_multipart_mixins import (
    PublicacionesMultiPartMixin,
)
from core.publicaciones.serializers.create.publicaciones_libro_create_serializers import (
    LibroRegistroSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import is_admin_user


class LibroViewSet(PublicacionesMultiPartMixin, viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LibroRegistroSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = (
            Libro.objects
            .select_related(
                "publicacion",
                "publicacion__usuario_creador",
                "publicacion__facultad",
                "publicacion__carrera",
                "publicacion__proyecto",
                "publicacion__area",
                "publicacion__subarea",
                "publicacion__tipo",
            )
            .all()
            .order_by("-publicacion__fecha_publicacion", "-id")
        )

        if is_admin_user(self.request.user):
            return queryset

        return queryset.filter(publicacion__usuario_creador=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        libro = serializer.save()

        return Response(
            {
                "message": "Libro registrado correctamente",
                "id": libro.id,
                "publicacion_id": libro.publicacion.id,
            },
            status=status.HTTP_201_CREATED,
        )