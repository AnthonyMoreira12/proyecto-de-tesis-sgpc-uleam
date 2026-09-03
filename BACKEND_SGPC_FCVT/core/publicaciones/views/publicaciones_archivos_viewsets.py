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
    get_publicacion_edit_block_reason,
)
from core.publicaciones.utils.publicaciones_visibilidad_utils import (
    apply_user_visible_publicaciones_scope,
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

    block_reason = (
        get_publicacion_edit_block_reason(
            publicacion
        )
    )

    if block_reason:
        raise PermissionDenied(
            block_reason
        )

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

    def get_permissions(self):
        """
        Permite lectura anónima solo sobre archivos de
        publicaciones Aprobadas. La restricción se aplica en
        get_queryset mediante la política central de visibilidad.

        Crear, eliminar y cargar archivos continúa requiriendo
        autenticación y los permisos de edición existentes.
        """

        if self.request.method in permissions.SAFE_METHODS:
            permission_classes = [
                permissions.AllowAny
            ]
        else:
            permission_classes = [
                permissions.IsAuthenticated
            ]

        return [
            permission()
            for permission in permission_classes
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
                "publicacion__sede",
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

        return (
            apply_user_visible_publicaciones_scope(
                queryset,
                user=self.request.user,
                prefix="publicacion__",
            )
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