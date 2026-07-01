from django.db.models import Prefetch, Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models.publicaciones import Publicacion, PublicacionAutor
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
    is_admin_user,
    resolve_user_autor_id,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
)


class PublicacionViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "put", "patch", "head", "options"]

    def get_queryset(self):
        autores_prefetch = Prefetch(
            "participaciones",
            queryset=(
                PublicacionAutor.objects.select_related("autor").order_by("orden", "id")
            ),
            to_attr="participaciones_ordenadas",
        )

        qs = (
            Publicacion.objects.select_related(
                "tipo",
                "facultad",
                "carrera",
                "proyecto",
                "area",
                "subarea",
                "pais",
                "ciudad",
                "ponencia",
                "articulo",
                "libro",
                "capitulo_libro",
                "usuario_creador",
            )
            .prefetch_related(autores_prefetch)
            .order_by("-updated_at", "-id")
        )

        return annotate_tipo_publicacion_final(qs)

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return PublicacionActualizacionSerializer

        if self.action == "retrieve":
            return PublicacionDetalleSerializer

        if self.action in ("list", "mias"):
            return PublicacionListadoSerializer

        return PublicacionDetalleSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def _check_can_edit(self, instance):
        user = self.request.user

        if is_admin_user(user):
            return

        if getattr(instance, "usuario_creador_id", None) == getattr(user, "id", None):
            return

        if can_edit_publicacion(user, instance):
            return

        raise PermissionDenied("No tiene permisos para editar esta publicación.")

    @action(detail=False, methods=["get"], url_path="mias")
    def mias(self, request):
        autor_id = resolve_user_autor_id(request.user)

        filtros = Q(usuario_creador=request.user)
        if autor_id:
            filtros |= Q(participaciones__autor_id=autor_id)

        queryset = self.get_queryset().filter(filtros).distinct()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PublicacionDetalleSerializer(
            instance,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self._check_can_edit(instance)

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=False,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        instance = self.get_queryset().get(pk=instance.pk)

        read_serializer = PublicacionDetalleSerializer(
            instance,
            context=self.get_serializer_context(),
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self._check_can_edit(instance)

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        instance = self.get_queryset().get(pk=instance.pk)

        read_serializer = PublicacionDetalleSerializer(
            instance,
            context=self.get_serializer_context(),
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)