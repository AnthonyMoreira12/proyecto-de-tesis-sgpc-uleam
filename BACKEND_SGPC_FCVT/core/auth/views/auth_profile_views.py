"""
Views del perfil del usuario autenticado.
"""

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DatabaseError, IntegrityError
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.auth.serializers.auth_profile_extension_serializers import (
    ProfileEditExtensionRequestSerializer,
)
from core.auth.serializers.auth_profile_read_serializers import ProfileSerializer
from core.auth.serializers.auth_profile_update_serializers import ProfileUpdateSerializer
from core.auth.services.auth_author_sync_services import asegurar_autor_para_usuario
from core.auth.services.auth_profile_extension_services import (
    ProfileExtensionRequestError,
    create_profile_edit_extension_request,
    get_current_profile_extension_request,
    get_profile_extension_request_for_admin,
    list_profile_extension_requests,
    resolve_profile_edit_extension_request,
    serialize_profile_extension_request,
)
from core.actualizaciones.services.actualizaciones_services import (
    recalcular_participante,
)
from core.auditoria.services.auditoria_services import (
    registrar_evento_auditoria,
)
from core.models import CampaniaActualizacionUsuario
from core.permisos.es_admin import EsAdmin

logger = logging.getLogger(__name__)


from core.auth.services.auth_profile_services import (
    ProfileEditServiceError,
    ensure_profile_edit_allowed,
    finalize_profile_update,
    register_failed_profile_attempt,
)


def _profile_extension_database_response(exc, operation):
    """Registra el fallo de BD y evita exponer un 500 sin contexto.

    Un error de esquema (por ejemplo, una migración pendiente) o una
    indisponibilidad temporal de PostgreSQL no debe convertirse en una
    respuesta HTML 500 para el frontend. El traceback completo queda en
    el log del backend y la API devuelve un 503 estable.
    """
    logger.exception(
        "Error de base de datos en solicitudes de extensión (%s): %s",
        operation,
        exc,
    )

    return Response(
        {
            "detail": (
                "El servicio de solicitudes de extensión no está "
                "disponible temporalmente. Intente nuevamente en unos "
                "momentos."
            )
        },
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


def _django_validation_to_payload(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict

    if hasattr(exc, "messages"):
        return {"detail": exc.messages}

    return {"detail": str(exc)}


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(
            request.user,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user

        try:
            edit_permission = ensure_profile_edit_allowed(
                user,
                requested_fields=request.data.keys(),
            )
        except ProfileEditServiceError as exc:
            return Response(exc.detail, status=exc.status_code)

        via_campaign = bool(edit_permission.get("via_campaign"))
        participant_ids = edit_permission.get("campaign_participant_ids", [])
        campaign_ids = edit_permission.get("campaign_ids", [])

        before = {
            "nombres": getattr(user, "nombres", None),
            "apellidos": getattr(user, "apellidos", None),
            "identificacion": getattr(user, "identificacion", None),
            "sede_id": getattr(user, "sede_id", None),
            "carrera_id": getattr(user, "carrera_id", None),
            "perfil_completo": getattr(user, "perfil_completo", False),
        }

        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            # Una campaña global no consume los intentos de la ventana
            # individual; ambos mecanismos permanecen independientes.
            if not via_campaign:
                register_failed_profile_attempt(user)

            return Response(
                {
                    **serializer.errors,
                    "profile_edit_locked": getattr(
                        user,
                        "profile_edit_locked",
                        False,
                    ),
                    "attempts_left": getattr(
                        user,
                        "profile_edit_attempts_left",
                        0,
                    ),
                    "profile_edit_until": getattr(
                        user,
                        "profile_edit_until",
                        None,
                    ),
                    "via_campaign": via_campaign,
                    "campaign_ids": campaign_ids,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer.save()
            finalize_profile_update(user)
            asegurar_autor_para_usuario(user)
        except DjangoValidationError as exc:
            if not via_campaign:
                register_failed_profile_attempt(user)

            return Response(
                {
                    **_django_validation_to_payload(exc),
                    "profile_edit_locked": getattr(
                        user,
                        "profile_edit_locked",
                        False,
                    ),
                    "attempts_left": getattr(
                        user,
                        "profile_edit_attempts_left",
                        0,
                    ),
                    "profile_edit_until": getattr(
                        user,
                        "profile_edit_until",
                        None,
                    ),
                    "via_campaign": via_campaign,
                    "campaign_ids": campaign_ids,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError:
            if not via_campaign:
                register_failed_profile_attempt(user)

            return Response(
                {
                    "detail": (
                        "No se pudo actualizar el perfil por conflicto "
                        "de unicidad."
                    ),
                    "profile_edit_locked": getattr(
                        user,
                        "profile_edit_locked",
                        False,
                    ),
                    "attempts_left": getattr(
                        user,
                        "profile_edit_attempts_left",
                        0,
                    ),
                    "profile_edit_until": getattr(
                        user,
                        "profile_edit_until",
                        None,
                    ),
                    "via_campaign": via_campaign,
                    "campaign_ids": campaign_ids,
                },
                status=status.HTTP_409_CONFLICT,
            )

        user.refresh_from_db()

        after = {
            "nombres": getattr(user, "nombres", None),
            "apellidos": getattr(user, "apellidos", None),
            "identificacion": getattr(user, "identificacion", None),
            "sede_id": getattr(user, "sede_id", None),
            "carrera_id": getattr(user, "carrera_id", None),
            "perfil_completo": getattr(user, "perfil_completo", False),
        }
        changed_before = {}
        changed_after = {}
        for field, old_value in before.items():
            new_value = after.get(field)
            if old_value != new_value:
                changed_before[field] = old_value
                changed_after[field] = new_value

        if via_campaign and participant_ids:
            participants = (
                CampaniaActualizacionUsuario.objects
                .filter(
                    pk__in=participant_ids,
                    usuario=user,
                )
                .select_related("campania", "usuario")
            )
            for participant in participants:
                if participant.iniciada_at is None:
                    participant.iniciada_at = timezone.now()
                    participant.estado = (
                        CampaniaActualizacionUsuario.ESTADO_EN_PROGRESO
                    )
                    participant.save(
                        update_fields=[
                            "iniciada_at",
                            "estado",
                            "updated_at",
                        ]
                    )
                recalcular_participante(participant)

        if changed_after:
            registrar_evento_auditoria(
                actor=user,
                accion="actualizar",
                modulo="perfil",
                entidad=user,
                descripcion=(
                    "El usuario actualizó su perfil mediante una campaña global."
                    if via_campaign
                    else "El usuario actualizó su perfil."
                ),
                datos_anteriores=changed_before,
                datos_nuevos=changed_after,
                contexto={
                    "origen": (
                        "actualizacion_global"
                        if via_campaign
                        else "edicion_individual"
                    ),
                    "campanias": campaign_ids,
                },
                request=request,
            )

        response_serializer = ProfileSerializer(
            user,
            context={"request": request},
        )
        payload = dict(response_serializer.data)
        payload["via_campaign"] = via_campaign
        payload["campaign_ids"] = campaign_ids
        return Response(payload, status=status.HTTP_200_OK)


class ProfileEditExtensionRequestView(APIView):
    """Consulta o crea la solicitud de extensión del usuario autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            solicitud = get_current_profile_extension_request(
                request.user
            )
        except DatabaseError as exc:
            return _profile_extension_database_response(
                exc,
                "consulta del usuario",
            )

        return Response(
            {
                "solicitud": (
                    serialize_profile_extension_request(solicitud)
                    if solicitud is not None
                    else None
                )
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ProfileEditExtensionRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        try:
            solicitud = create_profile_edit_extension_request(
                user=request.user,
                motivo=serializer.validated_data["motivo"],
                horas_solicitadas=serializer.validated_data[
                    "horas_solicitadas"
                ],
                request=request,
            )
        except ProfileExtensionRequestError as exc:
            return Response(exc.detail, status=exc.status_code)
        except DatabaseError as exc:
            return _profile_extension_database_response(
                exc,
                "creación de solicitud",
            )

        return Response(
            {
                "detail": (
                    "La solicitud fue registrada. Administración recibió "
                    "una notificación dentro del SGPC."
                ),
                "solicitud": serialize_profile_extension_request(
                    solicitud
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class AdminProfileEditExtensionRequestsView(APIView):
    """Listado administrativo de solicitudes de extensión."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, EsAdmin]

    def get(self, request):
        try:
            payload = list_profile_extension_requests(
                estado=request.query_params.get("estado", "pendiente"),
                limit=request.query_params.get("limit", 20),
                usuario_id=request.query_params.get("usuario_id"),
            )
        except ProfileExtensionRequestError as exc:
            return Response(exc.detail, status=exc.status_code)
        except DatabaseError as exc:
            return _profile_extension_database_response(
                exc,
                "listado administrativo",
            )

        return Response(payload, status=status.HTTP_200_OK)


class AdminProfileEditExtensionRequestDetailView(APIView):
    """Detalle y resolución de una solicitud de extensión."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, EsAdmin]

    def get(self, request, pk):
        try:
            solicitud = get_profile_extension_request_for_admin(pk)
        except ProfileExtensionRequestError as exc:
            return Response(exc.detail, status=exc.status_code)
        except DatabaseError as exc:
            return _profile_extension_database_response(
                exc,
                "detalle administrativo",
            )

        return Response(
            serialize_profile_extension_request(solicitud),
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        try:
            solicitud = resolve_profile_edit_extension_request(
                solicitud_id=pk,
                admin_user=request.user,
                decision=request.data.get("decision"),
                motivo_resolucion=request.data.get(
                    "motivo_resolucion", ""
                ),
                horas_aprobadas=request.data.get(
                    "horas_aprobadas"
                ),
            )
        except ProfileExtensionRequestError as exc:
            return Response(exc.detail, status=exc.status_code)
        except DatabaseError as exc:
            return _profile_extension_database_response(
                exc,
                "resolución administrativa",
            )

        return Response(
            {
                "detail": (
                    "La solicitud fue resuelta correctamente."
                ),
                "solicitud": serialize_profile_extension_request(
                    solicitud
                ),
            },
            status=status.HTTP_200_OK,
        )
