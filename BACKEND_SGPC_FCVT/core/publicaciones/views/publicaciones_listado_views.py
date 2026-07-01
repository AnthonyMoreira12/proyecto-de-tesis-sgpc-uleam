"""
View para listar publicaciones del sistema.
Permite filtrar por tipo final de publicación.
"""

from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Publicacion, PublicacionAutor
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


class PublicacionListAPIView(PublicacionesJWTAuthAPIViewMixin, APIView):
    def get(self, request):
        tipo = request.query_params.get("tipo") or request.query_params.get(
            "tipo_publicacion_final"
        )

        autores_prefetch = Prefetch(
            "participaciones",
            queryset=(
                PublicacionAutor.objects
                .select_related("autor")
                .order_by("orden", "id")
            ),
        )

        publicaciones = (
            Publicacion.objects
            .select_related(
                "tipo",
                "proyecto",
                "usuario_creador",
                "carrera",
                "carrera__facultad",  # <-- CORRECCIÓN: Buscamos la facultad a través de la carrera
                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
            .prefetch_related(autores_prefetch)
            .order_by("-fecha_publicacion", "-id")
        )

        publicaciones = annotate_tipo_publicacion_final(publicaciones).exclude(
            tipo_publicacion_final="sin_clasificar"
        )

        if tipo:
            tipo = str(tipo).strip().lower()
            if tipo in TIPOS_PUBLICACION_FINALES:
                publicaciones = publicaciones.filter(tipo_publicacion_final=tipo)

        serializer = PublicacionListadoSerializer(
            publicaciones,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)