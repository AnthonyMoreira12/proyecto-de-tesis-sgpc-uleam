"""Consulta administrativa del registro de auditoría."""

from datetime import timedelta

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import (
    permissions,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.auditoria.serializers.auditoria_serializers import (
    AuditoriaSistemaSerializer,
)
from core.auditoria.services.auditoria_excel_services import (
    EXCEL_CONTENT_TYPE,
    auditoria_excel_filename,
    build_auditoria_excel,
)
from core.models import AuditoriaSistema
from core.permisos.es_admin import EsAdmin


class AdminAuditoriaSistemaViewSet(
    viewsets.ReadOnlyModelViewSet
):
    authentication_classes = [
        JWTAuthentication
    ]

    permission_classes = [
        permissions.IsAuthenticated,
        EsAdmin,
    ]

    serializer_class = (
        AuditoriaSistemaSerializer
    )

    def get_queryset(self):
        qs = (
            AuditoriaSistema.objects
            .select_related("actor")
            .all()
        )

        params = (
            self.request.query_params
        )

        if params.get("actor_id"):
            qs = qs.filter(
                actor_id=params[
                    "actor_id"
                ]
            )

        if params.get("modulo"):
            qs = qs.filter(
                modulo=params[
                    "modulo"
                ]
            )

        if params.get("accion"):
            qs = qs.filter(
                accion=params[
                    "accion"
                ]
            )

        if params.get(
            "entidad_tipo"
        ):
            qs = qs.filter(
                entidad_tipo=params[
                    "entidad_tipo"
                ]
            )

        if params.get(
            "entidad_id"
        ):
            qs = qs.filter(
                entidad_id=str(
                    params[
                        "entidad_id"
                    ]
                )
            )

        if params.get(
            "fecha_desde"
        ):
            qs = qs.filter(
                created_at__date__gte=
                params[
                    "fecha_desde"
                ]
            )

        if params.get(
            "fecha_hasta"
        ):
            qs = qs.filter(
                created_at__date__lte=
                params[
                    "fecha_hasta"
                ]
            )

        q = str(
            params.get(
                "q",
                "",
            )
            or ""
        ).strip()

        if q:
            qs = qs.filter(
                Q(
                    descripcion__icontains=q
                )
                | Q(
                    actor__nombres__icontains=q
                )
                | Q(
                    actor__apellidos__icontains=q
                )
                | Q(
                    actor__email__icontains=q
                )
                | Q(
                    entidad_tipo__icontains=q
                )
                | Q(
                    entidad_id__icontains=q
                )
            )

        return qs

    @action(
        detail=False,
        methods=["get"],
        url_path="resumen",
    )
    def resumen(
        self,
        request,
    ):
        desde = (
            timezone.now()
            - timedelta(
                hours=24
            )
        )

        qs = (
            AuditoriaSistema.objects
            .filter(
                created_at__gte=desde
            )
        )

        return Response(
            {
                "ultimas_24_horas":
                    qs.count(),

                "usuarios_activos_24h":
                    (
                        qs
                        .exclude(
                            actor_id__isnull=True
                        )
                        .values(
                            "actor_id"
                        )
                        .distinct()
                        .count()
                    ),

                "publicaciones_24h":
                    qs.filter(
                        modulo="publicaciones"
                    ).count(),

                "administrativas_24h":
                    qs.filter(
                        modulo__in=[
                            "actualizaciones",
                            "comunicaciones",
                            "usuarios",
                            "estructura_academica",
                        ]
                    ).count(),
            }
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="exportar",
    )
    def exportar(
        self,
        request,
    ):
        """
        Exporta los registros de auditoría
        respetando los filtros actuales.

        El archivo incluye:
        - Resumen.
        - Eventos de auditoría.
        - Cambios realizados.
        - Datos técnicos.
        """

        queryset = (
            self.get_queryset()
        )

        file_bytes = (
            build_auditoria_excel(
                queryset=queryset,
                params=(
                    request.query_params
                ),
            )
        )

        filename = (
            auditoria_excel_filename()
        )

        response = HttpResponse(
            file_bytes,
            content_type=(
                EXCEL_CONTENT_TYPE
            ),
        )

        response[
            "Content-Disposition"
        ] = (
            f'attachment; '
            f'filename="{filename}"'
        )

        response[
            "Content-Length"
        ] = str(
            len(file_bytes)
        )

        response[
            "Cache-Control"
        ] = (
            "private, no-store, "
            "no-cache, must-revalidate"
        )

        response[
            "Pragma"
        ] = "no-cache"

        response[
            "Expires"
        ] = "0"

        response[
            "X-Content-Type-Options"
        ] = "nosniff"

        return response