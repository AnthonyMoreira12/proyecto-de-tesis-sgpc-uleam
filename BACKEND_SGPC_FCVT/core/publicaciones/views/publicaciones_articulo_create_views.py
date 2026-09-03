from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models.publicaciones.archivos import PublicacionArchivo
from core.publicaciones.mixins.publicaciones_auth_mixins import (
    PublicacionesJWTAuthAPIViewMixin,
)
from core.publicaciones.mixins.publicaciones_multipart_mixins import (
    PublicacionesMultiPartMixin,
)
from core.publicaciones.serializers.create.publicaciones_articulo_create_serializers import (
    ArticuloRegistroSerializer,
)
from core.publicaciones.services.publicaciones_archivos_services import (
    procesar_adjuntos_payload,
)


class ArticuloCreateAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    PublicacionesMultiPartMixin,
    APIView,
):
    """
    Registra artículos regionales y de alto impacto.

    Toda la operación se ejecuta de forma atómica:

    - Publicacion
    - Articulo
    - Autores
    - Adjuntos

    Si una parte falla, no queda información incompleta
    almacenada en la base de datos.
    """

    ATTACHMENT_INPUT_FIELDS = {
        "files",
        "archivos",
        "meta",
        "archivos_meta",
    }

    def _build_plain_data(self, request):
        source = request.data
        data = {}

        if hasattr(source, "lists"):
            for key, values in source.lists():
                if not values:
                    data[key] = ""

                elif len(values) == 1:
                    data[key] = values[0]

                else:
                    data[key] = values

        else:
            data = dict(source)

        if "archivo_pdf" in request.FILES:
            data["archivo_pdf"] = request.FILES[
                "archivo_pdf"
            ]

        return data

    def _build_serializer_data(self, plain_data):
        """
        Elimina únicamente los campos pertenecientes
        al sistema de adjuntos.

        Esos campos no forman parte de
        ArticuloRegistroSerializer.
        """

        return {
            key: value
            for key, value in plain_data.items()
            if key not in self.ATTACHMENT_INPUT_FIELDS
        }

    def _django_validation_to_drf(self, exc):
        if hasattr(exc, "message_dict"):
            return ValidationError(
                exc.message_dict
            )

        if hasattr(exc, "messages"):
            return ValidationError(
                {
                    "adjuntos": list(
                        exc.messages
                    )
                }
            )

        return ValidationError(
            {
                "adjuntos": [
                    str(exc)
                ]
            }
        )

    @transaction.atomic
    def post(self, request):
        plain_data = self._build_plain_data(
            request
        )

        # -----------------------------------------------------
        # 1. Validar adjuntos
        # -----------------------------------------------------

        try:
            adjuntos = procesar_adjuntos_payload(
                request,
                plain_data,
            )

        except ValidationError as exc:
            return Response(
                {
                    "detail": (
                        "No se pudieron validar "
                        "los adjuntos del artículo."
                    ),
                    "errors": getattr(
                        exc,
                        "detail",
                        {
                            "adjuntos": [
                                "Error de validación."
                            ]
                        },
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # 2. Validar datos del artículo
        # -----------------------------------------------------

        serializer_data = (
            self._build_serializer_data(
                plain_data
            )
        )

        serializer = ArticuloRegistroSerializer(
            data=serializer_data,
            context={
                "request": request,
            },
        )

        if not serializer.is_valid():
            return Response(
                {
                    "detail": (
                        "No se pudo registrar el artículo. "
                        "Revise los campos indicados."
                    ),
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------------------
        # 3. Crear Publicacion + Articulo + Autores
        # -----------------------------------------------------

        articulo = serializer.save()

        publicacion = articulo.publicacion

        # -----------------------------------------------------
        # 4. Crear adjuntos
        # -----------------------------------------------------

        created_adjuntos = []

        try:
            for item in adjuntos:
                adjunto = (
                    PublicacionArchivo.objects.create(
                        publicacion=publicacion,
                        nombre=item["nombre"],
                        orden=item["orden"],
                        archivo=item["file"],
                    )
                )

                created_adjuntos.append(
                    adjunto
                )

        except DjangoValidationError as exc:
            # Debe propagarse como excepción para que
            # transaction.atomic haga rollback de todo.
            raise self._django_validation_to_drf(
                exc
            )

        # -----------------------------------------------------
        # 5. Respuesta
        # -----------------------------------------------------

        return Response(
            {
                "message": (
                    "La publicación se guardó correctamente y quedó "
                    "en estado Borrador."
                ),
                "estado": publicacion.estado,
                "estado_label": publicacion.get_estado_display(),
                "articulo": {
                    "id": articulo.id,
                    "nombre_articulo": (
                        articulo.nombre_articulo
                    ),
                    "tipo_articulo": (
                        articulo.tipo_articulo
                    ),
                    "publicacion_id": (
                        publicacion.id
                    ),
                    "numero_publicacion": (
                        publicacion.numero
                    ),
                    "anio_publicacion": (
                        publicacion.anio_publicacion
                    ),
                },
                "adjuntos": {
                    "total": len(
                        created_adjuntos
                    ),
                    "ids": [
                        adjunto.id
                        for adjunto
                        in created_adjuntos
                    ],
                },
            },
            status=status.HTTP_201_CREATED,
        )