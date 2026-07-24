from django.db.models import Q
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import Ponencia
from core.publicaciones.mixins.publicaciones_multipart_mixins import (
    PublicacionesMultiPartMixin,
)
from core.publicaciones.serializers.create.publicaciones_ponencia_create_serializers import (
    PonenciaRegistroSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    is_admin_user,
    resolve_user_autor_id,
)


class PonenciaViewSet(
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
        PonenciaRegistroSerializer
    )

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
    ]

    def get_queryset(self):
        queryset = (
            Ponencia.objects
            .select_related(
                "publicacion",
                "publicacion__usuario_creador",
                "publicacion__admin_registrador",
                "publicacion__carrera",
                "publicacion__carrera__facultad",
                "publicacion__area",
                "publicacion__subarea",
                "publicacion__pais",
                "publicacion__ciudad",
                "publicacion__tipo",
                "publicacion__proyecto",
            )
            .order_by(
                "-publicacion__fecha_publicacion",
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

    def _registrar_ponencia(
        self,
        request,
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

        ponencia = serializer.save()

        return Response(
            {
                "message": (
                    "Ponencia registrada correctamente"
                ),
                "id": ponencia.id,
                "publicacion_id": (
                    ponencia.publicacion_id
                ),
                "numero_publicacion": (
                    ponencia.publicacion.numero
                ),
                "anio_publicacion": (
                    ponencia.publicacion.anio_publicacion
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Mantiene el POST estándar del ViewSet.
        """

        return self._registrar_ponencia(
            request
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="registrar",
    )
    def registrar(
        self,
        request,
    ):
        """
        Mantiene compatibilidad con el endpoint:

        /ponencias/registrar/
        """

        return self._registrar_ponencia(
            request
        )