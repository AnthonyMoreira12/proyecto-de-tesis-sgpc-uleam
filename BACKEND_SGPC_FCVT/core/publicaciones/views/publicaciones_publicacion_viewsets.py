from django.db.models import (
    Prefetch,
    Q,
)
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import (
    PermissionDenied,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import (
    Publicacion,
    PublicacionAutor,
)
from core.publicaciones.serializers.read.publicaciones_detalle_serializers import (
    PublicacionDetalleSerializer,
)
from core.publicaciones.serializers.read.publicaciones_listado_serializers import (
    PublicacionListadoSerializer,
)
from core.publicaciones.serializers.update.publicaciones_actualizacion_serializers import (
    PublicacionActualizacionSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    can_edit_publicacion,
    resolve_user_autor_id,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
)


class PublicacionViewSet(
    viewsets.ModelViewSet
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated
    ]

    http_method_names = [
        "get",
        "put",
        "patch",
        "head",
        "options",
    ]

    # =========================================================
    # QUERYSET
    # =========================================================

    def get_queryset(self):
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
            to_attr=(
                "participaciones_ordenadas"
            ),
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
                "-updated_at",
                "-id",
            )
        )

        return (
            annotate_tipo_publicacion_final(
                queryset
            )
        )

    # =========================================================
    # SERIALIZERS
    # =========================================================

    def get_serializer_class(self):
        if self.action in {
            "update",
            "partial_update",
        }:
            return (
                PublicacionActualizacionSerializer
            )

        if self.action == "retrieve":
            return (
                PublicacionDetalleSerializer
            )

        if self.action in {
            "list",
            "mias",
        }:
            return (
                PublicacionListadoSerializer
            )

        return (
            PublicacionDetalleSerializer
        )

    def get_serializer_context(self):
        context = (
            super()
            .get_serializer_context()
        )

        context["request"] = (
            self.request
        )

        return context

    # =========================================================
    # PERMISOS
    # =========================================================

    def _check_can_edit(
        self,
        instance,
    ):
        if can_edit_publicacion(
            self.request.user,
            instance,
        ):
            return

        raise PermissionDenied(
            "No tiene permisos para editar "
            "esta publicación."
        )

    # =========================================================
    # MIS PUBLICACIONES
    # =========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="mias",
    )
    def mias(
        self,
        request,
    ):
        autor_id = (
            resolve_user_autor_id(
                request.user
            )
        )

        filters = Q(
            usuario_creador=request.user
        )

        if autor_id:
            filters |= Q(
                participaciones__autor_id=(
                    autor_id
                )
            )

        queryset = (
            self.get_queryset()
            .filter(filters)
            .distinct()
        )

        serializer = (
            PublicacionListadoSerializer(
                queryset,
                many=True,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # DETALLE
    # =========================================================

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):
        instance = (
            self.get_object()
        )

        serializer = (
            PublicacionDetalleSerializer(
                instance,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # UPDATE INTERNO
    # =========================================================

    def _update_instance(
        self,
        *,
        request,
        instance,
        partial,
    ):
        self._check_can_edit(
            instance
        )

        serializer = (
            PublicacionActualizacionSerializer(
                instance=instance,
                data=request.data,
                partial=partial,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        updated_instance = (
            serializer.save()
        )

        # Reconsultamos para cargar:
        #
        # - relaciones
        # - anotación tipo_publicacion_final
        # - autores prefetched
        # - archivos prefetched

        updated_instance = (
            self.get_queryset()
            .get(
                pk=updated_instance.pk
            )
        )

        output_serializer = (
            PublicacionDetalleSerializer(
                updated_instance,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # PUT
    # =========================================================

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        instance = (
            self.get_object()
        )

        return self._update_instance(
            request=request,
            instance=instance,
            partial=False,
        )

    # =========================================================
    # PATCH
    # =========================================================

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):
        instance = (
            self.get_object()
        )

        return self._update_instance(
            request=request,
            instance=instance,
            partial=True,
        )