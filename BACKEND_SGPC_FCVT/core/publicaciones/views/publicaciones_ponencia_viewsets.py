"""
ViewSet para registro y consulta de ponencias.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Ponencia
from core.publicaciones.mixins.publicaciones_multipart_mixins import (
    PublicacionesMultiPartMixin,
)
from core.publicaciones.serializers.create.publicaciones_ponencia_create_serializers import (
    PonenciaRegistroSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import is_admin_user


class PonenciaViewSet(PublicacionesMultiPartMixin, viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PonenciaRegistroSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = (
            Ponencia.objects
            .select_related(
                "publicacion",
                "publicacion__usuario_creador",
                "publicacion__carrera",
                "publicacion__facultad",
                "publicacion__area",
                "publicacion__subarea",
                "publicacion__pais",
                "publicacion__ciudad",
                "publicacion__tipo",
                "publicacion__proyecto",
            )
            .all()
            .order_by("-publicacion__fecha_publicacion", "-id")
        )

        if is_admin_user(self.request.user):
            return queryset

        return queryset.filter(publicacion__usuario_creador=self.request.user)

    @action(detail=False, methods=["post"], url_path="registrar")
    def registrar(self, request):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        ponencia = serializer.save()

        return Response(
            {
                "message": "Ponencia registrada correctamente",
                "id": ponencia.id,
                "publicacion_id": ponencia.publicacion.id,
            },
            status=status.HTTP_201_CREATED,
        )