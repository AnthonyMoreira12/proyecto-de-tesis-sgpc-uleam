"""
View para registrar artículos científicos.
Soporta creación del artículo y, opcionalmente, adjuntos múltiples
en la misma operación multipart.
Lógica de procesamiento delegada a servicios para cumplir con patrón CQRS.
"""

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

# IMPORTANTE: Importamos el servicio que acabamos de crear
from core.publicaciones.services.publicaciones_archivos_services import (
    procesar_adjuntos_payload
)

class ArticuloCreateAPIView(
    PublicacionesJWTAuthAPIViewMixin,
    PublicacionesMultiPartMixin,
    APIView,
):
    def _build_plain_data(self, request):
        source = request.data
        data = {}

        if hasattr(source, "lists"):
            for key, values in source.lists():
                if len(values) == 0:
                    data[key] = ""
                elif len(values) == 1:
                    data[key] = values[0]
                else:
                    data[key] = values
        else:
            data = dict(source)

        if "archivo_pdf" in request.FILES:
            data["archivo_pdf"] = request.FILES["archivo_pdf"]

        return data

    @transaction.atomic
    def post(self, request):
        data = self._build_plain_data(request)

        # 1. Delegamos el procesamiento de adjuntos al servicio
        try:
            adjuntos = procesar_adjuntos_payload(request, data)
        except ValidationError as exc:
            return Response(
                {
                    "detail": "No se pudieron validar los adjuntos del artículo.",
                    "errors": getattr(exc, "detail", {"adjuntos": ["Error de validación."]}),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Validamos y guardamos los datos principales del artículo a través del serializer
        serializer = ArticuloRegistroSerializer(
            data=data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {
                    "detail": "No se pudo registrar el artículo. Revise los campos.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        articulo = serializer.save()
        publicacion = articulo.publicacion

        # 3. Guardamos los adjuntos procesados por el servicio
        created_adjuntos = []
        for item in adjuntos:
            created_adjuntos.append(
                PublicacionArchivo.objects.create(
                    publicacion=publicacion,
                    nombre=item["nombre"],
                    orden=item["orden"],
                    archivo=item["file"],
                )
            )

        # 4. Devolvemos la respuesta
        return Response(
            {
                "message": "Artículo registrado correctamente",
                "articulo": {
                    "id": articulo.id,
                    "nombre_articulo": articulo.nombre_articulo,
                    "publicacion_id": publicacion.id,
                    "numero_publicacion": publicacion.numero,
                    "anio_publicacion": publicacion.anio_publicacion,
                },
                "adjuntos": {
                    "total": len(created_adjuntos),
                },
            },
            status=status.HTTP_201_CREATED,
        )