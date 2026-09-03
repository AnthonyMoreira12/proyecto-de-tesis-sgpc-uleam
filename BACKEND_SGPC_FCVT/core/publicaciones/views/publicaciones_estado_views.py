"""
Endpoints de acciones del flujo de estado para publicaciones.

El campo ``estado`` no se modifica mediante PATCH/PUT.
Cada cambio se ejecuta como una acción explícita del dominio.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.services.publicaciones_estado_services import (
    PublicacionEstadoServiceError,
    build_transition_payload,
    enviar_a_revision,
    reenviar_a_revision,
)


class PublicacionEnviarRevisionAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    POST /publicaciones/<id>/enviar-revision/

    Transición:
        borrador -> en_revision
    """

    def post(
        self,
        request,
        id,
    ):
        try:
            result = enviar_a_revision(
                publicacion_id=id,
                actor=request.user,
            )

        except PublicacionEstadoServiceError as exc:
            detail = exc.detail

            if isinstance(
                detail,
                dict,
            ):
                payload = dict(
                    detail
                )
                payload[
                    "codigo"
                ] = exc.code
            else:
                payload = {
                    "detail": detail,
                    "codigo": exc.code,
                }

            return Response(
                payload,
                status=exc.status_code,
            )

        return Response(
            build_transition_payload(
                result,
                message=(
                    "La publicación fue enviada "
                    "a revisión correctamente."
                ),
            ),
            status=(
                status.HTTP_200_OK
            ),
        )



class PublicacionReenviarRevisionAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    POST /publicaciones/<id>/reenviar-revision/

    Transición:
        observada -> en_revision

    El contenido debe corregirse previamente mediante los endpoints
    ordinarios de edición. Este endpoint únicamente confirma que la
    versión corregida vuelve al proceso formal de revisión.
    """

    def post(
        self,
        request,
        id,
    ):
        try:
            result = reenviar_a_revision(
                publicacion_id=id,
                actor=request.user,
            )

        except PublicacionEstadoServiceError as exc:
            detail = exc.detail

            if isinstance(
                detail,
                dict,
            ):
                payload = dict(
                    detail
                )
                payload[
                    "codigo"
                ] = exc.code
            else:
                payload = {
                    "detail": detail,
                    "codigo": exc.code,
                }

            return Response(
                payload,
                status=exc.status_code,
            )

        return Response(
            build_transition_payload(
                result,
                message=(
                    "La publicación corregida fue "
                    "reenviada a revisión correctamente."
                ),
            ),
            status=(
                status.HTTP_200_OK
            ),
        )