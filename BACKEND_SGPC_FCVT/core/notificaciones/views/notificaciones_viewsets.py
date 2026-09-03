"""
Endpoints de notificaciones del usuario autenticado.

No se permite crear notificaciones desde el cliente. Son generadas
exclusivamente por eventos del backend.
"""

from django.db import transaction
from django.utils import timezone

from rest_framework import (
    mixins,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.models import Notificacion
from core.notificaciones.serializers.notificaciones_serializers import (
    NotificacionSerializer,
)


def _truthy(
    value,
):
    return str(
        value
        or ""
    ).strip().lower() in {
        "1",
        "true",
        "si",
        "sí",
        "yes",
    }


class NotificacionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = (
        NotificacionSerializer
    )

    http_method_names = [
        "get",
        "post",
        "head",
        "options",
    ]

    def get_queryset(
        self,
    ):
        queryset = (
            Notificacion.objects
            .select_related(
                "publicacion"
            )
            .filter(
                destinatario=(
                    self.request.user
                ),
                visible_en_bandeja=True,
            )
            .order_by(
                "-created_at",
                "-id",
            )
        )

        if _truthy(
            self.request.query_params.get(
                "solo_no_leidas"
            )
        ):
            queryset = (
                queryset.filter(
                    leida=False
                )
            )

        tipo = str(
            self.request.query_params.get(
                "tipo",
                "",
            )
            or ""
        ).strip().lower()

        if tipo:
            queryset = queryset.filter(
                tipo=tipo
            )

        return queryset

    @action(
        detail=False,
        methods=[
            "get",
        ],
        url_path="resumen",
    )
    def resumen(
        self,
        request,
    ):
        base = (
            Notificacion.objects
            .filter(
                destinatario=request.user,
                visible_en_bandeja=True,
            )
        )

        return Response(
            {
                "total": (
                    base.count()
                ),
                "no_leidas": (
                    base.filter(
                        leida=False
                    ).count()
                ),
            },
            status=(
                status.HTTP_200_OK
            ),
        )

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="leer",
    )
    def leer(
        self,
        request,
        pk=None,
    ):
        notification = (
            self.get_object()
        )

        if not notification.leida:
            notification.leida = True
            notification.leida_at = (
                timezone.now()
            )

            notification.save(
                update_fields=[
                    "leida",
                    "leida_at",
                ]
            )

        return Response(
            self.get_serializer(
                notification
            ).data,
            status=(
                status.HTTP_200_OK
            ),
        )

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="marcar-todas-leidas",
    )
    def marcar_todas_leidas(
        self,
        request,
    ):
        now = timezone.now()

        with transaction.atomic():
            updated = (
                Notificacion.objects
                .filter(
                    destinatario=(
                        request.user
                    ),
                    visible_en_bandeja=True,
                    leida=False,
                )
                .update(
                    leida=True,
                    leida_at=now,
                )
            )

        return Response(
            {
                "ok": True,
                "actualizadas": (
                    updated
                ),
                "no_leidas": 0,
            },
            status=(
                status.HTTP_200_OK
            ),
        )