"""
Vista para consultar y actualizar el detalle de una publicación.

Admite:
- GET
- PUT
- PATCH
- application/json
- multipart/form-data
- application/x-www-form-urlencoded

La modificación de una publicación está limitada a:
- administradores;
- usuario creador;
- autores vinculados con permiso de edición.
"""

from django.db.models import Prefetch
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import (
    Publicacion,
    PublicacionAutor,
)
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
)


class PublicacionDetailAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    PublicacionesMultiPartMixin,
    APIView,
):
    parser_classes = [
        JSONParser,
        FormParser,
        MultiPartParser,
    ]

    # =========================================================
    # QUERY
    # =========================================================

    def _get_publicacion(
        self,
        publicacion_id,
    ):
        autores_prefetch = Prefetch(
            "participaciones",
            queryset=(
                PublicacionAutor.objects
                .select_related("autor")
                .order_by(
                    "orden",
                    "id",
                )
            ),
            to_attr="participaciones_ordenadas",
        )

        return (
            Publicacion.objects
            .select_related(
                "tipo",
                "proyecto",
                "usuario_creador",
                "admin_registrador",
                "carrera",
                "carrera__facultad",
                "area",
                "subarea",
                "pais",
                "ciudad",
                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
            .prefetch_related(
                autores_prefetch,
                "archivos",
            )
            .get(
                pk=publicacion_id
            )
        )

    # =========================================================
    # PERMISOS
    # =========================================================

    def _check_can_edit(
        self,
        request,
        publicacion,
    ):
        if can_edit_publicacion(
            request.user,
            publicacion,
        ):
            return

        raise PermissionDenied(
            "No tiene permisos para editar "
            "esta publicación."
        )

    # =========================================================
    # REQUEST DATA
    # =========================================================

    def _build_plain_data(
        self,
        request,
    ):
        """
        Convierte QueryDict/FormData en un diccionario
        manejable por el serializer sin perder archivos
        ni listas.
        """

        source = request.data
        data = {}

        if hasattr(
            source,
            "lists",
        ):
            for key, values in source.lists():
                if not values:
                    data[key] = ""

                elif len(values) == 1:
                    data[key] = values[0]

                else:
                    data[key] = values

        else:
            data = dict(source)

        if (
            hasattr(request, "FILES")
            and "archivo_pdf"
            in request.FILES
        ):
            data["archivo_pdf"] = (
                request.FILES[
                    "archivo_pdf"
                ]
            )

        return data

    # =========================================================
    # GET
    # =========================================================

    def get(
        self,
        request,
        id,
    ):
        try:
            data = (
                construir_detalle_publicacion(
                    publicacion_id=id
                )
            )

        except Publicacion.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Publicación no encontrada."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # PUT
    # =========================================================

    def put(
        self,
        request,
        id,
    ):
        return self._update(
            request=request,
            publicacion_id=id,
            partial=False,
        )

    # =========================================================
    # PATCH
    # =========================================================

    def patch(
        self,
        request,
        id,
    ):
        return self._update(
            request=request,
            publicacion_id=id,
            partial=True,
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def _update(
        self,
        *,
        request,
        publicacion_id,
        partial,
    ):
        try:
            publicacion = (
                self._get_publicacion(
                    publicacion_id
                )
            )

        except Publicacion.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Publicación no encontrada."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        self._check_can_edit(
            request,
            publicacion,
        )

        plain_data = (
            self._build_plain_data(
                request
            )
        )

        serializer = (
            PublicacionActualizacionSerializer(
                instance=publicacion,
                data=plain_data,
                partial=partial,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        publicacion = serializer.save()

        try:
            data = (
                construir_detalle_publicacion(
                    publicacion_id=(
                        publicacion.pk
                    )
                )
            )

        except Publicacion.DoesNotExist:
            return Response(
                {
                    "error": (
                        "La publicación fue actualizada, "
                        "pero no pudo recuperarse su detalle."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )