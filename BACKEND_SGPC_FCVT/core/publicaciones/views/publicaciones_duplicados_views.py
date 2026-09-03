"""Endpoint de prevalidación de publicaciones duplicadas."""

from rest_framework import status
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.services.publicaciones_duplicados_services import (
    analizar_duplicados_candidato,
)
from core.publicaciones.utils.publicaciones_validation_response_utils import (
    construir_respuesta_validacion,
    problemas_desde_duplicados,
)


class PublicacionValidarDuplicadosAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    APIView,
):
    """
    POST /publicaciones/validar-duplicados/

    Permite al frontend consultar coincidencias antes de guardar.
    Las advertencias no crean ni modifican registros.
    """

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    def post(
        self,
        request,
    ):
        uploaded_file = (
            request.FILES.get(
                "archivo_pdf"
            )
            if hasattr(
                request,
                "FILES",
            )
            else None
        )

        result = (
            analizar_duplicados_candidato(
                request.data,
                uploaded_file=uploaded_file,
                exclude_publication_id=(
                    request.data.get(
                        "excluir_publicacion_id"
                    )
                    if hasattr(
                        request.data,
                        "get",
                    )
                    else None
                ),
            )
        )

        blocking, warnings = (
            problemas_desde_duplicados(
                result
            )
        )

        normalized = (
            construir_respuesta_validacion(
                bloqueantes=blocking,
                advertencias=warnings,
                validaciones={
                    "duplicados": {
                        "ejecutada": True,
                        "valida": not bool(
                            blocking
                        ),
                        "criterios": (
                            result.get(
                                "criterios",
                                {},
                            )
                        ),
                    }
                },
            )
        )

        # Compatibilidad con el contrato del PASO 2: se conservan
        # las claves originales y se añade la representación común.
        payload = dict(result)
        payload["ok"] = True
        payload["valido"] = normalized[
            "valido"
        ]
        payload["puede_continuar"] = (
            normalized[
                "puede_continuar"
            ]
        )
        payload["resumen"] = normalized[
            "resumen"
        ]
        payload["respuesta_validacion"] = (
            normalized
        )

        return Response(
            payload,
            status=(
                status.HTTP_200_OK
            ),
        )