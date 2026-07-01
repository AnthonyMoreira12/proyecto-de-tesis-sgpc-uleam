from .scholar_perfiles_views import (
    PerfilScholarDetailAPIView,
    PerfilScholarMeAPIView,
    PerfilesScholarAPIView,
)
from .scholar_publicaciones_views import PublicacionesScholarAPIView
from .scholar_sugerencias_views import ScholarSuggestAPIView
from .scholar_tipos_publicacion_views import TiposPublicacionListAPIView

__all__ = [
    "PerfilScholarDetailAPIView",
    "PerfilScholarMeAPIView",
    "PerfilesScholarAPIView",
    "PublicacionesScholarAPIView",
    "ScholarSuggestAPIView",
    "TiposPublicacionListAPIView",
]