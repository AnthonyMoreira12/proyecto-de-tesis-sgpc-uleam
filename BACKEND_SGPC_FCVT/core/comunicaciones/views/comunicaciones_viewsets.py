"""Endpoints de comunicaciones globales del SGPC."""

from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.comunicaciones.serializers.comunicaciones_serializers import (
    ComunicacionGlobalSerializer,
)
from core.models import ComunicacionGlobal
from core.permisos.es_admin import EsAdmin


class ComunicacionGlobalViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComunicacionGlobalSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            classes = [permissions.IsAuthenticated, EsAdmin]
        else:
            classes = [permissions.IsAuthenticated]
        return [cls() for cls in classes]

    def get_queryset(self):
        qs = ComunicacionGlobal.objects.select_related(
            "creado_por", "campania"
        ).all()

        user = self.request.user
        if EsAdmin._es_administrador_activo(user):
            state = str(self.request.query_params.get("estado", "") or "").strip().lower()
            if state == "activas":
                qs = qs.filter(activa=True)
            elif state == "inactivas":
                qs = qs.filter(activa=False)
            return qs

        now = timezone.now()
        qs = qs.filter(activa=True).filter(
            Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=now)
        ).filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=now))

        return qs.filter(
            Q(campania__isnull=True)
            | Q(campania__participantes__usuario=user)
        ).distinct()

    def perform_create(self, serializer):
        communication = serializer.save(creado_por=self.request.user)
        registrar_evento_auditoria(
            actor=self.request.user,
            accion="crear",
            modulo="comunicaciones",
            entidad=communication,
            descripcion="Se creó una comunicación global.",
            datos_nuevos={
                "titulo": communication.titulo,
                "tipo": communication.tipo,
                "activa": communication.activa,
            },
            request=self.request,
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        before = {
            "titulo": instance.titulo,
            "mensaje": instance.mensaje,
            "tipo": instance.tipo,
            "activa": instance.activa,
            "fecha_inicio": instance.fecha_inicio,
            "fecha_fin": instance.fecha_fin,
        }
        communication = serializer.save()
        after = {
            "titulo": communication.titulo,
            "mensaje": communication.mensaje,
            "tipo": communication.tipo,
            "activa": communication.activa,
            "fecha_inicio": communication.fecha_inicio,
            "fecha_fin": communication.fecha_fin,
        }
        registrar_evento_auditoria(
            actor=self.request.user,
            accion="actualizar",
            modulo="comunicaciones",
            entidad=communication,
            descripcion="Se modificó una comunicación global.",
            datos_anteriores=before,
            datos_nuevos=after,
            request=self.request,
        )

    def perform_destroy(self, instance):
        registrar_evento_auditoria(
            actor=self.request.user,
            accion="eliminar",
            modulo="comunicaciones",
            entidad=instance,
            descripcion="Se eliminó una comunicación global.",
            datos_anteriores={"titulo": instance.titulo, "tipo": instance.tipo},
            request=self.request,
        )
        instance.delete()
