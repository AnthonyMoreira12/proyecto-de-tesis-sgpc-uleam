from django.db.models import Q
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import (
    Publicacion,
    PublicacionArchivo,
)
from core.publicaciones.mixins.publicaciones_multipart_mixins import (
    PublicacionesMultiPartMixin,
)
from core.publicaciones.serializers.base.publicaciones_archivos_serializers import (
    PublicacionArchivoCreateSerializer,
    PublicacionArchivoSerializer,
    PublicacionArchivosBulkUploadSerializer,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    can_edit_publicacion,
    is_admin_user,
    resolve_user_autor_id,
)


def _assert_user_can_access_publicacion(
    *,
    user,
    publicacion,
):
    if publicacion is None:
        raise ValidationError(
            {
                "publicacion": [
                    "La publicación es obligatoria."
                ]
            }
        )

    if can_edit_publicacion(
        user,
        publicacion,
    ):
        return

    raise PermissionDenied(
        "No tiene permisos para gestionar "
        "los archivos de esta publicación."
    )


class PublicacionArchivoViewSet(
    PublicacionesMultiPartMixin,
    viewsets.ModelViewSet,
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated
    ]

    http_method_names = [
        "get",
        "post",
        "delete",
        "head",
        "options",
    ]

    # =========================================================
    # QUERYSET
    # =========================================================

    def get_queryset(self):
        queryset = (
            PublicacionArchivo.objects
            .select_related(
                "publicacion",
                "publicacion__tipo",
                "publicacion__usuario_creador",
                "publicacion__carrera",
                "publicacion__carrera__facultad",
            )
            .order_by(
                "orden",
                "id",
            )
        )

        publicacion_id = (
            self.request.query_params.get(
                "publicacion_id"
            )
        )

        if publicacion_id:
            try:
                publicacion_id = int(
                    publicacion_id
                )

            except (
                TypeError,
                ValueError,
            ):
                raise ValidationError(
                    {
                        "publicacion_id": [
                            "Debe ser un número "
                            "entero válido."
                        ]
                    }
                )

            if publicacion_id < 1:
                raise ValidationError(
                    {
                        "publicacion_id": [
                            "Debe ser mayor "
                            "o igual a 1."
                        ]
                    }
                )

            queryset = (
                queryset.filter(
                    publicacion_id=(
                        publicacion_id
                    )
                )
            )

        user = self.request.user

        if is_admin_user(
            user
        ):
            return queryset

        autor_id = (
            resolve_user_autor_id(
                user
            )
        )

        filters = Q(
            publicacion__usuario_creador=user
        )

        if autor_id:
            filters |= Q(
                publicacion__participaciones__autor_id=(
                    autor_id
                )
            )

        return (
            queryset
            .filter(filters)
            .distinct()
        )

    # =========================================================
    # SERIALIZER
    # =========================================================

    def get_serializer_class(
        self,
    ):
        if self.action == "create":
            return (
                PublicacionArchivoCreateSerializer
            )

        return (
            PublicacionArchivoSerializer
        )

    def get_serializer_context(
        self,
    ):
        context = (
            super()
            .get_serializer_context()
        )

        context["request"] = (
            self.request
        )

        return context

    # =========================================================
    # CREATE
    # =========================================================

    def perform_create(
        self,
        serializer,
    ):
        publicacion = (
            serializer.validated_data.get(
                "publicacion"
            )
        )

        _assert_user_can_access_publicacion(
            user=self.request.user,
            publicacion=publicacion,
        )

        serializer.save()

    # =========================================================
    # DELETE
    # =========================================================

    def perform_destroy(
        self,
        instance,
    ):
        _assert_user_can_access_publicacion(
            user=self.request.user,
            publicacion=(
                instance.publicacion
            ),
        )

        # PublicacionArchivo.delete()
        # elimina el archivo físico.
        instance.delete()

    # =========================================================
    # BULK UPLOAD
    # =========================================================

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-upload",
    )
    def bulk_upload(
        self,
        request,
    ):
        serializer = (
            PublicacionArchivosBulkUploadSerializer(
                data=request.data,
                context={
                    "request": request,
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        publicacion = (
            serializer.validated_data[
                "publicacion"
            ]
        )

        _assert_user_can_access_publicacion(
            user=request.user,
            publicacion=publicacion,
        )

        created = serializer.save()

        output = (
            PublicacionArchivoSerializer(
                created,
                many=True,
                context={
                    "request": request,
                },
            ).data
        )

        return Response(
            output,
            status=(
                status.HTTP_201_CREATED
            ),
        )