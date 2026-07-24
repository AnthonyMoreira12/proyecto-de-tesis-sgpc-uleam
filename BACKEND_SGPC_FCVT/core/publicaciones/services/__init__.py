"""
Servicios del dominio de publicaciones.

La lógica de negocio se mantiene separada de serializers
y views para facilitar mantenimiento, pruebas y reutilización.
"""

from .publicaciones_archivos_services import (
    procesar_adjuntos_payload,
)
from .publicaciones_autores_services import (
    registrar_autores_publicacion,
)
from .publicaciones_detalle_services import (
    construir_detalle_publicacion,
)
from .publicaciones_excel_services import (
    build_publicaciones_excel,
    workbook_to_bytes,
)
from .publicaciones_factory_services import (
    crear_publicacion_base,
    obtener_o_crear_tipo_publicacion,
)


__all__ = (
    "procesar_adjuntos_payload",
    "registrar_autores_publicacion",
    "construir_detalle_publicacion",
    "build_publicaciones_excel",
    "workbook_to_bytes",
    "crear_publicacion_base",
    "obtener_o_crear_tipo_publicacion",
)