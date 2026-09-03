from .base import TipoPublicacion, Publicacion
from .autoria import Autor, PublicacionAutor
from .archivos import PublicacionArchivo
from .revision import PublicacionRevision
from .historial import PublicacionHistorial
from .tipos import Ponencia, Articulo, Libro, CapituloLibro

__all__ = [
    "TipoPublicacion",
    "Publicacion",
    "Autor",
    "PublicacionAutor",
    "PublicacionArchivo",
    "PublicacionRevision",
    "PublicacionHistorial",
    "Ponencia",
    "Articulo",
    "Libro",
    "CapituloLibro",
]