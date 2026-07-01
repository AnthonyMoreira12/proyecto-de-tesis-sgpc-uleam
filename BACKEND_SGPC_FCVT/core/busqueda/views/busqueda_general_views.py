from rest_framework.response import Response
from rest_framework.views import APIView

from core.busqueda.selectors.busqueda_general_selectors import (
    buscar_autores,
    buscar_proyectos,
    buscar_publicaciones,
    buscar_usuarios,
)
from core.busqueda.serializers.busqueda_autor_serializers import AutorBusquedaSerializer
from core.busqueda.serializers.busqueda_proyecto_serializers import ProyectoBusquedaSerializer
from core.busqueda.serializers.busqueda_publicacion_serializers import PublicacionBusquedaSerializer
from core.busqueda.serializers.busqueda_usuario_serializers import UsuarioBusquedaSerializer


class BusquedaGeneralAPIView(APIView):
    def get(self, request):
        q = (request.GET.get("q") or "").strip()

        try:
            limit = int(request.GET.get("limit") or 8)
        except (TypeError, ValueError):
            limit = 8

        limit = max(1, min(limit, 20))

        if not q:
            return Response(
                {
                    "usuarios": [],
                    "proyectos": [],
                    "publicaciones": [],
                    "autores": [],
                }
            )

        usuarios = buscar_usuarios(q, limit=limit)
        proyectos = buscar_proyectos(q, limit=limit)
        publicaciones = buscar_publicaciones(q, limit=limit)
        autores = buscar_autores(q, limit=limit)

        return Response(
            {
                "usuarios": UsuarioBusquedaSerializer(
                    usuarios,
                    many=True,
                    context={"request": request},
                ).data,
                "proyectos": ProyectoBusquedaSerializer(
                    proyectos,
                    many=True,
                ).data,
                "publicaciones": PublicacionBusquedaSerializer(
                    publicaciones,
                    many=True,
                    context={"request": request},
                ).data,
                "autores": AutorBusquedaSerializer(
                    autores,
                    many=True,
                ).data,
            }
        )