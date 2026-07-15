"""
View para listar las publicaciones vinculadas al usuario autenticado.
Incluye las creadas por el usuario y las asociadas a su autoría.
"""

from django.db.models import Prefetch, Q
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Publicacion, PublicacionAutor
from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.serializers.read.publicaciones_listado_serializers import (
    PublicacionListadoSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    resolve_user_autor_id,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    TIPOS_PUBLICACION_FINALES,
    annotate_tipo_publicacion_final,
)


class MyPublicacionListAPIView(PublicacionesJWTAuthAPIViewMixin, APIView):
    """
    Lista las publicaciones relacionadas con el usuario autenticado.

    Incluye:
    - Publicaciones creadas directamente por el usuario.
    - Publicaciones donde el usuario aparece como autor vinculado.
    """

    def get(self, request):
        tipo = request.query_params.get("tipo") or request.query_params.get(
            "tipo_publicacion_final"
        )

        autores_prefetch = Prefetch(
            "participaciones",
            queryset=PublicacionAutor.objects.select_related("autor").order_by(
                "orden",
                "id",
            ),
        )

        autor_id = resolve_user_autor_id(request.user)

        filtros = Q(usuario_creador=request.user)

        if autor_id:
            filtros |= Q(participaciones__autor_id=autor_id)

        publicaciones = (
            Publicacion.objects.select_related(
                "tipo",
                "proyecto",
                "carrera",
                "carrera__facultad",
                "usuario_creador",
                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
            .prefetch_related(autores_prefetch)
            .filter(filtros)
            .distinct()
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