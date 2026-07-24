"""
Mixin para vistas que reciben formularios y archivos.

Permite procesar:

- multipart/form-data
- application/x-www-form-urlencoded

Es utilizado principalmente por los formularios de
registro y gestión de publicaciones con archivos PDF.
"""

from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)


class PublicacionesMultiPartMixin:
    """
    Habilita recepción de formularios tradicionales
    y multipart/form-data.
    """

    parser_classes = (
        MultiPartParser,
        FormParser,
    )