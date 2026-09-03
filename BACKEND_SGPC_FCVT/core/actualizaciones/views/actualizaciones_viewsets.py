"""Endpoints administrativos y personales de campañas de actualización."""

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.actualizaciones.serializers.actualizaciones_serializers import (
    CampaniaActualizacionSerializer,
    CampaniaActualizacionUsuarioSerializer,
    MiCampaniaActualizacionSerializer,
)
from core.actualizaciones.services.actualizaciones_recordatorios_services import (
    sincronizar_avisos_actualizacion_usuario,
)
from core.actualizaciones.services.actualizaciones_services import (
    ActualizacionServiceError,
    activar_campania,
    campanias_activas_para_usuario,
    diagnostico_campania,
    finalizar_campania,
    progreso_campania,
    recalcular_participante,
    sincronizar_participantes_campania,
)
from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.comunicaciones.services.comunicaciones_services import notificar_campania
from core.models import CampaniaActualizacion, CampaniaActualizacionUsuario
from core.permisos.es_admin import EsAdmin


class AdminCampaniaActualizacionViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    serializer_class = CampaniaActualizacionSerializer

    def get_queryset(self):
        qs = CampaniaActualizacion.objects.select_related("creado_por").all()
        params = self.request.query_params
        if params.get("estado"):
            qs = qs.filter(estado=params["estado"])
        if params.get("tipo"):
            qs = qs.filter(tipo=params["tipo"])
        q = str(params.get("q", "") or "").strip()
        if q:
            qs = qs.filter(Q(titulo__icontains=q) | Q(descripcion__icontains=q))
        return qs

    def perform_create(self, serializer):
        campaign = serializer.save(creado_por=self.request.user)
        registrar_evento_auditoria(
            actor=self.request.user,
            accion="crear",
            modulo="actualizaciones",
            entidad=campaign,
            descripcion="Se creó una campaña global de actualización.",
            datos_nuevos={
                "titulo": campaign.titulo,
                "tipo": campaign.tipo,
                "alcance": campaign.alcance,
                "campos_habilitados": campaign.campos_habilitados,
            },
            request=self.request,
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        before = {
            "titulo": instance.titulo,
            "descripcion": instance.descripcion,
            "tipo": instance.tipo,
            "alcance": instance.alcance,
            "fecha_inicio": instance.fecha_inicio,
            "fecha_fin": instance.fecha_fin,
            "solo_incompletos": instance.solo_incompletos,
            "campos_habilitados": instance.campos_habilitados,
            "filtros_destinatarios": instance.filtros_destinatarios,
        }
        campaign = serializer.save()
        after = {
            "titulo": campaign.titulo,
            "descripcion": campaign.descripcion,
            "tipo": campaign.tipo,
            "alcance": campaign.alcance,
            "fecha_inicio": campaign.fecha_inicio,
            "fecha_fin": campaign.fecha_fin,
            "solo_incompletos": campaign.solo_incompletos,
            "campos_habilitados": campaign.campos_habilitados,
            "filtros_destinatarios": campaign.filtros_destinatarios,
        }
        registrar_evento_auditoria(
            actor=self.request.user,
            accion="actualizar",
            modulo="actualizaciones",
            entidad=campaign,
            descripcion="Se modificó una campaña de actualización en borrador.",
            datos_anteriores=before,
            datos_nuevos=after,
            request=self.request,
        )

    def destroy(self, request, *args, **kwargs):
        campaign = self.get_object()
        if campaign.estado != CampaniaActualizacion.ESTADO_BORRADOR:
            return Response(
                {"detail": "Solo se pueden eliminar campañas en borrador."},
                status=status.HTTP_409_CONFLICT,
            )
        registrar_evento_auditoria(
            actor=request.user,
            accion="eliminar",
            modulo="actualizaciones",
            entidad=campaign,
            descripcion="Se eliminó una campaña que aún estaba en borrador.",
            datos_anteriores={"titulo": campaign.titulo, "tipo": campaign.tipo},
            request=request,
        )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        try:
            campaign = activar_campania(self.get_object(), admin_user=request.user, request=request)
        except ActualizacionServiceError as exc:
            return Response(exc.detail, status=exc.status_code)
        return Response(self.get_serializer(campaign).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def finalizar(self, request, pk=None):
        try:
            campaign = finalizar_campania(
                self.get_object(), admin_user=request.user, request=request, cancelar=False
            )
        except ActualizacionServiceError as exc:
            return Response(exc.detail, status=exc.status_code)
        return Response(self.get_serializer(campaign).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        try:
            campaign = finalizar_campania(
                self.get_object(), admin_user=request.user, request=request, cancelar=True
            )
        except ActualizacionServiceError as exc:
            return Response(exc.detail, status=exc.status_code)
        return Response(self.get_serializer(campaign).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="recordatorio")
    def recordatorio(self, request, pk=None):
        campaign = self.get_object()
        if not campaign.esta_vigente:
            return Response(
                {"detail": "Solo se pueden enviar recordatorios de campañas activas y vigentes."},
                status=status.HTTP_409_CONFLICT,
            )
        result = notificar_campania(
            campaign,
            actor=request.user,
            request=request,
            recordatorio=True,
            solo_pendientes=True,
        )
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def progreso(self, request, pk=None):
        return Response(progreso_campania(self.get_object()), status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def participantes(self, request, pk=None):
        campaign = self.get_object()
        qs = campaign.participantes.select_related("usuario", "campania").all()
        state = request.query_params.get("estado")
        if state:
            qs = qs.filter(estado=state)
        q = str(request.query_params.get("q", "") or "").strip()
        if q:
            qs = qs.filter(
                Q(usuario__nombres__icontains=q)
                | Q(usuario__apellidos__icontains=q)
                | Q(usuario__email__icontains=q)
            )
        serializer = CampaniaActualizacionUsuarioSerializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})

    @action(detail=True, methods=["get"])
    def diagnostico(self, request, pk=None):
        return Response(
            diagnostico_campania(self.get_object()),
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def recalcular(self, request, pk=None):
        campaign = self.get_object()

        with transaction.atomic():
            sync_result = sincronizar_participantes_campania(campaign)

        registrar_evento_auditoria(
            actor=request.user,
            accion="actualizar",
            modulo="actualizaciones",
            entidad=campaign,
            descripcion=(
                "Se recalcularon los pendientes y se sincronizaron los "
                "participantes de la campaña."
            ),
            contexto={
                "creados": sync_result["creados"],
                "actualizados": sync_result["actualizados"],
                "pendientes": sync_result["pendientes"],
                "completados": sync_result["completados"],
            },
            request=request,
        )

        return Response(
            {
                **progreso_campania(campaign),
                "sincronizacion": sync_result,
            },
            status=status.HTTP_200_OK,
        )


class MisActualizacionesViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MiCampaniaActualizacionSerializer

    def get_queryset(self):
        return campanias_activas_para_usuario(self.request.user)

    @action(detail=False, methods=["post"], url_path="estado-aviso")
    def estado_aviso(self, request):
        """Sincroniza pendientes, notificaciones y recordatorios del usuario."""
        payload = sincronizar_avisos_actualizacion_usuario(request.user)
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def iniciar(self, request, pk=None):
        participant = self.get_object()
        if participant.estado == CampaniaActualizacionUsuario.ESTADO_PENDIENTE:
            participant.estado = CampaniaActualizacionUsuario.ESTADO_EN_PROGRESO
            participant.iniciada_at = participant.iniciada_at or timezone.now()
            participant.save(update_fields=["estado", "iniciada_at", "updated_at"])
        return Response(self.get_serializer(participant).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def recalcular(self, request, pk=None):
        participant = recalcular_participante(self.get_object())
        return Response(self.get_serializer(participant).data, status=status.HTTP_200_OK)
