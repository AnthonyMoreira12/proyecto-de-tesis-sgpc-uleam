"""
Serializers de creación de publicaciones.

Expone únicamente los serializers públicos utilizados
para registrar los diferentes tipos de producción científica.
"""

from .publicaciones_articulo_create_serializers import (
    ArticuloRegistroSerializer,
)
from .publicaciones_capitulo_libro_create_serializers import (
    CapituloLibroRegistroSerializer,
)
from .publicaciones_libro_create_serializers import (
    LibroRegistroSerializer,
)
from .publicaciones_ponencia_create_serializers import (
    PonenciaRegistroSerializer,
)


__all__ = (
    "ArticuloRegistroSerializer",
    "CapituloLibroRegistroSerializer",
    "LibroRegistroSerializer",
    "PonenciaRegistroSerializer",
)