"""
Vista para listar publicaciones del sistema.

Permite filtrar por el tipo final normalizado de
publicación y devuelve la información optimizada para
PublicacionListadoSerializer.
"""

from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import (
    Publicacion,
    PublicacionAutor,
)
from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.serializers.read.publicaciones_listado_serializers import (
    PublicacionListadoSerializer,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    TIPOS_PUBLICACION_FINALES,
    annotate_tipo_publicacion_final,
)


def _normalize_tipo(value):
    return str(
        value or ""
    ).strip().lower()


class PublicacionListAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    def _build_queryset(self):
        autores_prefetch = Prefetch(
            "participaciones",
            queryset=(
                PublicacionAutor.objects
                .select_related(
                    "autor"
                )
                .order_by(
                    "orden",
                    "id",
                )
            ),
            to_attr="participaciones_ordenadas",
        )

        queryset = (
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
            .order_by(
                "-fecha_publicacion",
                "-id",
            )
        )

        queryset = (
            annotate_tipo_publicacion_final(
                queryset
            )
            .exclude(
                tipo_publicacion_final=(
                    "sin_clasificar"
                )
            )
        )

        return queryset

    def get(
        self,
        request,
    ):
        tipo = (
            request.query_params.get(
                "tipo"
            )
            or request.query_params.get(
                "tipo_publicacion_final"
            )
        )

        publicaciones = (
            self._build_queryset()
        )

        if tipo:
            tipo = _normalize_tipo(
                tipo
            )

            if (
                tipo
                not in TIPOS_PUBLICACION_FINALES
            ):
                raise ValidationError(
                    {
                        "tipo": [
                            "El tipo de publicación "
                            "seleccionado no es válido."
                        ]
                    }
                )

            publicaciones = (
                publicaciones.filter(
                    tipo_publicacion_final=tipo
                )
            )

        serializer = (
            PublicacionListadoSerializer(
                publicaciones,
                many=True,
                context={
                    "request": request,
                },
            )
        )

        return Response(
            serializer.data
        )