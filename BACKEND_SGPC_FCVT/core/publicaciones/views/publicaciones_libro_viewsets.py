from django.db.models import F, Q
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import Libro
from core.publicaciones.mixins.publicaciones_multipart_mixins import (
    PublicacionesMultiPartMixin,
)
from core.publicaciones.serializers.create.publicaciones_libro_create_serializers import (
    LibroRegistroSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    is_admin_user,
    resolve_user_autor_id,
)


class LibroViewSet(
    PublicacionesMultiPartMixin,
    viewsets.ModelViewSet,
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = (
        LibroRegistroSerializer
    )

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
    ]

    def get_queryset(self):
        """
        Devuelve libros ordenados por período de publicación.

        Reglas:
        - año más reciente primero;
        - dentro del mismo año, mes más reciente primero;
        - publicaciones sin mes se ubican después de las que sí
          tienen mes dentro del mismo año;
        - id descendente como criterio final estable.
        """

        queryset = (
            Libro.objects
            .select_related(
                "publicacion",
                "publicacion__usuario_creador",
                "publicacion__admin_registrador",
                "publicacion__carrera",
                "publicacion__carrera__facultad",
                "publicacion__proyecto",
                "publicacion__area",
                "publicacion__subarea",
                "publicacion__tipo",
            )
            .order_by(
                F(
                    "publicacion__anio_publicacion"
                ).desc(
                    nulls_last=True
                ),
                F(
                    "publicacion__mes_publicacion"
                ).desc(
                    nulls_last=True
                ),
                "-id",
            )
        )

        user = self.request.user

        if is_admin_user(user):
            return queryset

        autor_id = resolve_user_autor_id(
            user
        )

        filters = Q(
            publicacion__usuario_creador=user
        )

        if autor_id:
            filters |= Q(
                publicacion__participaciones__autor_id=autor_id
            )

        return (
            queryset
            .filter(filters)
            .distinct()
        )

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        libro = serializer.save()
        publicacion = libro.publicacion

        return Response(
            {
                "message": (
                    "Libro registrado correctamente"
                ),
                "id": libro.id,
                "publicacion_id": (
                    libro.publicacion_id
                ),
                "numero_publicacion": (
                    publicacion.numero
                ),
                "anio_publicacion": (
                    publicacion.anio_publicacion
                ),
                "mes_publicacion": (
                    publicacion.mes_publicacion
                ),
            },
            status=status.HTTP_201_CREATED,
        )