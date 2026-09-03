from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.migracion_produccion.services.migracion_produccion_services import (
    comparar_snapshots_produccion,
    diagnostico_actualizacion_produccion,
    normalizar_actualizacion_produccion,
    snapshot_metricas_produccion,
)
from core.permisos.es_admin import EsAdmin


class _AdminBase(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]


class AdminPreparacionProduccionDiagnosticoAPIView(_AdminBase):
    def get(self, request):
        return Response(diagnostico_actualizacion_produccion())


class AdminPreparacionProduccionNormalizarAPIView(_AdminBase):
    def post(self, request):
        dry_run = bool(request.data.get("dry_run", True))
        usar_default = bool(request.data.get("usar_sede_predeterminada", False))
        sede_id = request.data.get("sede_predeterminada_id")
        try:
            sede_id = int(sede_id) if sede_id not in (None, "") else None
        except (TypeError, ValueError):
            return Response({"detail": "La sede predeterminada es inválida."}, status=400)

        if usar_default and not sede_id:
            return Response(
                {"detail": "Seleccione una sede predeterminada antes de usar la asignación masiva."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not dry_run and str(request.data.get("confirmacion", "")) != "NORMALIZAR_PRODUCCION":
            return Response(
                {"detail": "Para aplicar cambios debe enviar confirmacion=NORMALIZAR_PRODUCCION."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            result = normalizar_actualizacion_produccion(
                dry_run=dry_run,
                default_sede_id=sede_id,
                usar_sede_predeterminada=usar_default,
                recalcular_perfiles=True,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        registrar_evento_auditoria(
            actor=request.user,
            accion="diagnosticar" if dry_run else "actualizar",
            modulo="preparacion_produccion",
            entidad_tipo="NormalizacionProduccion",
            descripcion=(
                "Se simuló la normalización de datos históricos para la actualización."
                if dry_run
                else "Se aplicó la normalización segura de datos históricos para la actualización."
            ),
            datos_nuevos={
                "dry_run": dry_run,
                "resumen": result.get("resumen", {}),
                "pendientes": {k: len(v) for k, v in result.get("pendientes", {}).items()},
                "sede_predeterminada_id": sede_id,
            },
            request=request,
        )
        return Response(result)


class AdminPreparacionProduccionVerificarAPIView(_AdminBase):
    def post(self, request):
        before = request.data.get("snapshot_antes") or {}
        if not isinstance(before, dict):
            return Response({"detail": "snapshot_antes debe ser un objeto."}, status=400)
        result = comparar_snapshots_produccion(before, snapshot_metricas_produccion())
        return Response(result)
