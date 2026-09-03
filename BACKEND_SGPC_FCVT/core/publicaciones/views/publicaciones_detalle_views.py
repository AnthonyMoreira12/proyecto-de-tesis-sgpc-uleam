"""
Vista para consultar y actualizar el detalle de una publicación.

Admite:
- GET
- PUT
- PATCH
- application/json
- multipart/form-data
- application/x-www-form-urlencoded

La modificación de una publicación está limitada a:
- administradores;
- usuario creador de la publicación.
"""

from django.db.models import Prefetch
from rest_framework import (
    permissions,
    status,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from core.actualizaciones.services.actualizaciones_services import (
    actualizar_progreso_participantes_campania,
    autorizacion_edicion_registro_por_campania,
)
from core.auditoria.services.auditoria_services import (
    registrar_evento_auditoria,
)
from core.models import (
    CampaniaActualizacion,
    Publicacion,
    PublicacionAutor,
)
from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.mixins.publicaciones_multipart_mixins import (
    PublicacionesMultiPartMixin,
)
from core.publicaciones.serializers.update.publicaciones_actualizacion_serializers import (
    PublicacionActualizacionSerializer,
)
from core.publicaciones.services.publicaciones_detalle_services import (
    construir_detalle_publicacion,
)
from core.publicaciones.services.publicaciones_estado_services import (
    can_enviar_a_revision,
    can_reenviar_a_revision,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    can_edit_publicacion,
    get_publicacion_edit_block_reason,
    is_publicacion_content_editable,
)
from core.publicaciones.utils.publicaciones_visibilidad_utils import (
    apply_user_visible_publicaciones_scope,
)


class PublicacionDetailAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    PublicacionesMultiPartMixin,
    APIView,
):
    parser_classes = [
        JSONParser,
        FormParser,
        MultiPartParser,
    ]

    def get_permissions(self):
        """
        La lectura es pública solo para publicaciones visibles.

        GET/HEAD/OPTIONS permiten usuario anónimo; el queryset
        aplica después la política central de visibilidad y,
        para un anónimo, limita el resultado a Aprobada.

        Las operaciones de escritura mantienen IsAuthenticated
        heredado de PublicacionesJWTAuthAPIViewMixin.
        """

        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]

        return [
            permission()
            for permission in self.permission_classes
        ]

    # =========================================================
    # QUERY
    # =========================================================

    def _get_publicacion(
        self,
        publicacion_id,
        *,
        user,
    ):
        autores_prefetch = Prefetch(
            "participaciones",
            queryset=(
                PublicacionAutor.objects
                .select_related("autor")
                .order_by(
                    "orden",
                    "id",
                )
            ),
            to_attr="participaciones_ordenadas",
        )

        queryset = (
            Publicacion.objects
            .select_related(
                "tipo",
                "proyecto",
                "proyecto__sede",
                "sede",
                "usuario_creador",
                "admin_registrador",
                "carrera",
                "carrera__facultad",
                "area",
                "subarea",
                "pais",
                "ciudad",
                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
            .prefetch_related(
                autores_prefetch,
                "archivos",
            )
        )

        queryset = (
            apply_user_visible_publicaciones_scope(
                queryset,
                user=user,
            )
        )

        return queryset.get(
            pk=publicacion_id
        )

    # =========================================================
    # PERMISOS
    # =========================================================

    def _check_can_edit(
        self,
        request,
        publicacion,
        *,
        requested_fields=None,
    ):
        """Resuelve la vía de edición aplicable a la publicación.

        Una campaña vigente tiene prioridad cuando los campos solicitados
        están expresamente habilitados por ella. Esto es especialmente
        importante para usuarios que además poseen permisos administrativos:
        de lo contrario, ``can_edit_publicacion`` los resolvería primero como
        edición ordinaria y el serializer bloquearía después una publicación
        aprobada como "edición directa".

        Si existe una campaña pero los campos solicitados no están habilitados,
        un usuario con permiso ordinario conserva su flujo normal; para el resto
        se rechaza la operación indicando los campos no autorizados.
        """

        campaign_permission = (
            autorizacion_edicion_registro_por_campania(
                request.user,
                tipo=CampaniaActualizacion.TIPO_PUBLICACION,
                registro=publicacion,
                requested_fields=requested_fields,
            )
        )

        # La actualización controlada debe prevalecer siempre que la campaña
        # cubra exactamente los campos solicitados, incluso si el usuario es
        # administrador. Así el serializer recibe permitir_edicion_campania=True
        # y mantiene el whitelist de campos de la campaña.
        if (
            campaign_permission is not None
            and campaign_permission.get("authorized")
        ):
            return {
                "via_campaign": True,
                **campaign_permission,
            }

        # Fuera de una actualización válida por campaña se conserva la política
        # ordinaria existente (por ejemplo, edición administrativa).
        if can_edit_publicacion(
            request.user,
            publicacion,
        ):
            return {
                "via_campaign": False,
                "campaign_ids": [],
                "participant_ids": [],
                "allowed_fields": [],
                "requested_fields": [],
            }

        if campaign_permission is not None:
            raise PermissionDenied(
                {
                    "detail": (
                        "La campaña global no habilita uno o más de "
                        "los campos que intenta modificar."
                    ),
                    "campos_no_habilitados": campaign_permission.get(
                        "unauthorized_fields",
                        [],
                    ),
                    "campos_habilitados": campaign_permission.get(
                        "allowed_fields",
                        [],
                    ),
                    "campanias": campaign_permission.get(
                        "campaign_ids",
                        [],
                    ),
                }
            )

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
            "No tiene permisos para editar "
            "esta publicación."
        )

    def _campaign_audit_snapshot(
        self,
        publicacion,
        fields,
    ):
        snapshot = {}
        fk_fields = {
            "sede",
            "carrera",
            "area",
            "subarea",
            "pais",
            "ciudad",
            "proyecto",
        }
        for field in fields or []:
            if field in fk_fields:
                snapshot[field] = getattr(
                    publicacion,
                    f"{field}_id",
                    None,
                )
        return snapshot

    def _attach_edit_metadata(
        self,
        *,
        request,
        publicacion,
        data,
    ):
        """
        Añade al detalle los metadatos necesarios para que el
        frontend use la misma regla de autorización del backend.
        """

        payload = dict(
            data or {}
        )

        payload["usuario_creador_id"] = (
            publicacion.usuario_creador_id
        )

        puede_editar_normal = bool(
            can_edit_publicacion(
                request.user,
                publicacion,
            )
        )

        campaign_permission = (
            autorizacion_edicion_registro_por_campania(
                request.user,
                tipo=CampaniaActualizacion.TIPO_PUBLICACION,
                registro=publicacion,
                requested_fields=None,
            )
        )

        puede_editar_campania = bool(
            campaign_permission
            and campaign_permission.get("authorized")
        )

        puede_editar = bool(
            puede_editar_normal
            or puede_editar_campania
        )

        estado_editable = bool(
            is_publicacion_content_editable(
                publicacion
            )
        )

        payload["puede_editar"] = (
            puede_editar
        )

        payload["estado_editable"] = (
            estado_editable
        )

        payload["edicion_por_campania"] = (
            puede_editar_campania
        )
        payload["campos_editables_campania"] = (
            campaign_permission.get("allowed_fields", [])
            if campaign_permission
            else []
        )
        payload["campos_pendientes_campania"] = (
            campaign_permission.get("pending_fields", [])
            if campaign_permission
            else []
        )
        payload["campanias_actualizacion_ids"] = (
            campaign_permission.get("campaign_ids", [])
            if campaign_permission
            else []
        )

        payload[
            "puede_enviar_revision"
        ] = bool(
            can_enviar_a_revision(
                request.user,
                publicacion,
            )
        )

        payload[
            "puede_reenviar_revision"
        ] = bool(
            can_reenviar_a_revision(
                request.user,
                publicacion,
            )
        )

        if puede_editar:
            payload[
                "motivo_bloqueo_edicion"
            ] = None

        else:
            payload[
                "motivo_bloqueo_edicion"
            ] = (
                get_publicacion_edit_block_reason(
                    publicacion
                )
                or (
                    "No tiene permisos para editar "
                    "esta publicación."
                )
            )

        return payload

    # =========================================================
    # REQUEST DATA
    # =========================================================

    def _build_plain_data(
        self,
        request,
    ):
        """
        Convierte QueryDict/FormData en un diccionario
        manejable por el serializer sin perder archivos
        ni listas.
        """

        source = request.data
        data = {}

        if hasattr(
            source,
            "lists",
        ):
            for key, values in source.lists():
                if not values:
                    data[key] = ""

                elif len(values) == 1:
                    data[key] = values[0]

                else:
                    data[key] = values

        else:
            data = dict(source)

        if (
            hasattr(request, "FILES")
            and "archivo_pdf"
            in request.FILES
        ):
            data["archivo_pdf"] = (
                request.FILES[
                    "archivo_pdf"
                ]
            )

        return data

    # =========================================================
    # GET
    # =========================================================

    def get(
        self,
        request,
        id,
    ):
        try:
            publicacion = (
                self._get_publicacion(
                    id,
                    user=request.user,
                )
            )

            data = (
                construir_detalle_publicacion(
                    publicacion_id=id
                )
            )

        except Publicacion.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Publicación no encontrada."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        data = self._attach_edit_metadata(
            request=request,
            publicacion=publicacion,
            data=data,
        )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # PUT
    # =========================================================

    def put(
        self,
        request,
        id,
    ):
        return self._update(
            request=request,
            publicacion_id=id,
            partial=False,
        )

    # =========================================================
    # PATCH
    # =========================================================

    def patch(
        self,
        request,
        id,
    ):
        return self._update(
            request=request,
            publicacion_id=id,
            partial=True,
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def _update(
        self,
        *,
        request,
        publicacion_id,
        partial,
    ):
        try:
            publicacion = (
                self._get_publicacion(
                    publicacion_id,
                    user=request.user,
                )
            )

        except Publicacion.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Publicación no encontrada."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        plain_data = (
            self._build_plain_data(
                request
            )
        )

        edit_permission = self._check_can_edit(
            request,
            publicacion,
            requested_fields=plain_data.keys(),
        )

        via_campaign = bool(
            edit_permission.get("via_campaign")
        )
        campaign_fields = (
            edit_permission.get("requested_fields", [])
            if via_campaign
            else []
        )
        before_campaign = (
            self._campaign_audit_snapshot(
                publicacion,
                campaign_fields,
            )
            if via_campaign
            else {}
        )

        serializer = (
            PublicacionActualizacionSerializer(
                instance=publicacion,
                data=plain_data,
                partial=partial,
                context={
                    "request": request,
                    "permitir_edicion_campania": via_campaign,
                    "origen_edicion": (
                        "actualizacion_global"
                        if via_campaign
                        else "publicaciones"
                    ),
                },
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        publicacion = serializer.save()

        if via_campaign:
            publicacion.refresh_from_db()
            after_campaign = (
                self._campaign_audit_snapshot(
                    publicacion,
                    campaign_fields,
                )
            )
            changed_before = {}
            changed_after = {}
            for field, old_value in before_campaign.items():
                new_value = after_campaign.get(field)
                if old_value != new_value:
                    changed_before[field] = old_value
                    changed_after[field] = new_value

            actualizar_progreso_participantes_campania(
                request.user,
                edit_permission.get("participant_ids", []),
            )

            if changed_after:
                registrar_evento_auditoria(
                    actor=request.user,
                    accion="actualizar",
                    modulo="publicaciones",
                    entidad=publicacion,
                    descripcion=(
                        "El usuario actualizó información de una publicación "
                        "mediante una campaña global."
                    ),
                    datos_anteriores=changed_before,
                    datos_nuevos=changed_after,
                    contexto={
                        "origen": "actualizacion_global",
                        "campanias": edit_permission.get(
                            "campaign_ids",
                            [],
                        ),
                    },
                    request=request,
                )

        try:
            data = (
                construir_detalle_publicacion(
                    publicacion_id=(
                        publicacion.pk
                    )
                )
            )

        except Publicacion.DoesNotExist:
            return Response(
                {
                    "error": (
                        "La publicación fue actualizada, "
                        "pero no pudo recuperarse su detalle."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        data = self._attach_edit_metadata(
            request=request,
            publicacion=publicacion,
            data=data,
        )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )