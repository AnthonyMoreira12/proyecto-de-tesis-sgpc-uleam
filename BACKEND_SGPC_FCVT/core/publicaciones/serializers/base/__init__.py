"""
Serializers base reutilizables del módulo de publicaciones.
"""

from .publicaciones_archivos_serializers import (
    PublicacionArchivoCreateSerializer,
    PublicacionArchivoSerializer,
    PublicacionArchivosBulkUploadSerializer,
)
from .publicaciones_autores_serializers import (
    AutorParticipacionSerializer,
    PublicacionAutorSerializer,
)
from .publicaciones_campos_base_serializers import (
    PublicacionCamposBaseMixin,
)


__all__ = (
    "PublicacionArchivoSerializer",
    "PublicacionArchivoCreateSerializer",
    "PublicacionArchivosBulkUploadSerializer",
    "AutorParticipacionSerializer",
    "PublicacionAutorSerializer",
    "PublicacionCamposBaseMixin",
)