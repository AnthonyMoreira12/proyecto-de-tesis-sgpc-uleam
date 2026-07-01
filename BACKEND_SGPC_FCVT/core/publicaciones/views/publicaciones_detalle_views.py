"""
View para consultar y actualizar el detalle de una publicación.
"""

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Publicacion
from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.mixins.publicaciones_multipart_mixins import (
    PublicacionesMultiPartMixin,
)
from core.publicaciones.serializers.update.publicaciones_actualizacion_serializers import (
    PublicacionActualizacionSerializer,
)
from core.publicaciones.services.publicaciones_detalle_services import (
    construir_detalle_publicacion,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    can_edit_publicacion,
    is_admin_user,
)


class PublicacionDetailAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    PublicacionesMultiPartMixin,
    APIView,
):
    def _get_pub_or_404(self, publicacion_id):
        return (
            Publicacion.objects
            .select_related("usuario_creador", "tipo")
            .get(id=publicacion_id)
        )

    def _check_owner_or_admin(self, request, publicacion: Publicacion):
        if is_admin_user(request.user):
            return

        if getattr(publicacion, "usuario_creador_id", None) == getattr(request.user, "id", None):
            return

        if can_edit_publicacion(request.user, publicacion):
            return

        raise PermissionDenied("No tienes permisos para editar esta publicación.")

    def _build_plain_data(self, request):
        source = request.data
        data = {}

        if hasattr(source, "lists"):
            for key, values in source.lists():
                if len(values) == 0:
                    data[key] = ""
                elif len(values) == 1:
                    data[key] = values[0]
                else:
                    data[key] = values
        else:
            data = dict(source)

        if "archivo_pdf" in request.FILES:
            data["archivo_pdf"] = request.FILES["archivo_pdf"]

        return data

    def get(self, request, id):
        try:
            data = construir_detalle_publicacion(publicacion_id=id)
        except Publicacion.DoesNotExist:
            return Response(
                {"error": "Publicación no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, id):
        return self._update(request, id)

    def patch(self, request, id):
        return self._update(request, id)

    def _update(self, request, id):
        try:
            publicacion = self._get_pub_or_404(id)
        except Publicacion.DoesNotExist:
            return Response(
                {"error": "Publicación no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self._check_owner_or_admin(request, publicacion)

        plain_data = self._build_plain_data(request)

        serializer = PublicacionActualizacionSerializer(
            instance=publicacion,
            data=plain_data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        publicacion = serializer.save()
        data = construir_detalle_publicacion(publicacion_id=publicacion.id)
        return Response(data, status=status.HTTP_200_OK)