from django.db.models import Q
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Publicacion, SolicitudModificacionPublicacion
from core.permisos.es_admin import EsAdmin
from core.publicaciones.solicitudes.solicitudes_modificacion_serializers import (
    ResolverSolicitudModificacionSerializer,
    SolicitudModificacionPublicacionCreateSerializer,
    SolicitudModificacionPublicacionSerializer,
)
from core.publicaciones.solicitudes.solicitudes_modificacion_services import (
    SolicitudModificacionError,
    cancelar_solicitud,
    campos_sensibles_permitidos,
    resolver_solicitud,
    snapshot_campos,
)


class SolicitudModificacionPublicacionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            SolicitudModificacionPublicacion.objects
            .select_related(
                "publicacion",
                "publicacion__tipo",
                "publicacion__ponencia",
                "publicacion__articulo",
                "publicacion__libro",
                "publicacion__capitulo_libro",
                "solicitante",
                "revisor",
            )
            .filter(solicitante=self.request.user)
        )

    def get_serializer_class(self):
        if self.action == "create":
            return SolicitudModificacionPublicacionCreateSerializer
        return SolicitudModificacionPublicacionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.save()
        except SolicitudModificacionError as exc:
            return Response(exc.detail, status=exc.status_code)
        return Response(
            SolicitudModificacionPublicacionSerializer(instance, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


    @action(detail=False, methods=["get"], url_path="configuracion")
    def configuracion(self, request):
        publicacion_id = request.query_params.get("publicacion_id")
        if not publicacion_id:
            return Response({"detail": "publicacion_id es obligatorio."}, status=400)
        publicacion = (
            Publicacion.objects
            .select_related("tipo", "ponencia", "articulo", "libro", "capitulo_libro")
            .prefetch_related("participaciones")
            .filter(pk=publicacion_id, usuario_creador=request.user)
            .first()
        )
        if publicacion is None:
            return Response({"detail": "Publicación no encontrada."}, status=404)
        if publicacion.estado != Publicacion.ESTADO_APROBADA:
            return Response(
                {"detail": "Solo las publicaciones aprobadas usan este flujo."},
                status=409,
            )
        fields = campos_sensibles_permitidos(publicacion)
        return Response({
            "publicacion_id": publicacion.pk,
            "campos_permitidos": fields,
            "valores_actuales": snapshot_campos(publicacion, fields),
        })

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        try:
            instance = cancelar_solicitud(self.get_object(), usuario=request.user, request=request)
        except SolicitudModificacionError as exc:
            return Response(exc.detail, status=exc.status_code)
        return Response(SolicitudModificacionPublicacionSerializer(instance).data)


class AdminSolicitudModificacionPublicacionViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    serializer_class = SolicitudModificacionPublicacionSerializer

    def get_queryset(self):
        qs = (
            SolicitudModificacionPublicacion.objects
            .select_related(
                "publicacion",
                "publicacion__tipo",
                "publicacion__ponencia",
                "publicacion__articulo",
                "publicacion__libro",
                "publicacion__capitulo_libro",
                "solicitante",
                "revisor",
            )
            .all()
        )
        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        q = str(self.request.query_params.get("q", "") or "").strip()
        if q:
            query = (
                Q(solicitante__nombres__icontains=q)
                | Q(solicitante__apellidos__icontains=q)
                | Q(solicitante__email__icontains=q)
                | Q(motivo__icontains=q)
            )
            if q.isdigit():
                query |= Q(publicacion_id=int(q))
            qs = qs.filter(query)
        return qs

    def _resolve(self, request, *, approve):
        serializer = ResolverSolicitudModificacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = resolver_solicitud(
                self.get_object(),
                admin_user=request.user,
                aprobar=approve,
                comentario=serializer.validated_data.get("comentario", ""),
                request=request,
            )
        except SolicitudModificacionError as exc:
            return Response(exc.detail, status=exc.status_code)
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        return self._resolve(request, approve=True)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        return self._resolve(request, approve=False)
