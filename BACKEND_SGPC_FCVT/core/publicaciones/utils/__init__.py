"""
Utilidades compartidas del módulo de publicaciones.
"""

from .publicaciones_archivos_utils import (
    default_nombre_from_file,
    validar_firma_pdf,
)
from .publicaciones_creation_context_utils import (
    resolve_publicacion_creation_context,
)
from .publicaciones_permissions_utils import (
    can_edit_publicacion,
    is_admin_user,
    resolve_user_autor_id,
)
from .publicaciones_tipo_resolver_utils import (
    TIPOS_PUBLICACION_FINALES,
    annotate_tipo_publicacion_final,
    normalize_tipo_publicacion_final,
    tipo_publicacion_es_valido,
    tipo_publicacion_label,
)


__all__ = (
    "default_nombre_from_file",
    "validar_firma_pdf",
    "resolve_publicacion_creation_context",
    "can_edit_publicacion",
    "is_admin_user",
    "resolve_user_autor_id",
    "TIPOS_PUBLICACION_FINALES",
    "annotate_tipo_publicacion_final",
    "normalize_tipo_publicacion_final",
    "tipo_publicacion_es_valido",
    "tipo_publicacion_label",
)