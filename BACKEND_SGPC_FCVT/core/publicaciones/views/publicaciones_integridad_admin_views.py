from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.permisos.es_admin import EsAdmin
from core.publicaciones.services.publicaciones_integridad_backfill_services import (
    backfill_integridad_documental,
    diagnostico_integridad_documental,
)


class AdminIntegridadDocumentalDiagnosticoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]

    def get(self, request):
        return Response(diagnostico_integridad_documental())


class AdminIntegridadDocumentalBackfillAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]

    def post(self, request):
        dry_run = bool(request.data.get("dry_run", False))
        limit = request.data.get("limit")
        publication_id = request.data.get("publication_id")
        try:
            limit = int(limit) if limit not in (None, "") else None
            publication_id = int(publication_id) if publication_id not in (None, "") else None
        except (TypeError, ValueError):
            return Response({"detail": "Los parámetros numéricos son inválidos."}, status=400)
        if limit is not None and limit < 1:
            return Response({"detail": "limit debe ser mayor que cero."}, status=400)

        result = backfill_integridad_documental(
            dry_run=dry_run,
            limit=limit,
            publication_id=publication_id,
        )
        registrar_evento_auditoria(
            actor=request.user,
            accion="actualizar" if not dry_run else "diagnosticar",
            modulo="integridad_documental",
            entidad_tipo="PDFHistorico",
            descripcion=(
                "Se ejecutó el backfill de metadatos PDF históricos."
                if not dry_run
                else "Se simuló el backfill de metadatos PDF históricos."
            ),
            datos_nuevos=result,
            request=request,
        )
        return Response(result, status=status.HTTP_200_OK)
