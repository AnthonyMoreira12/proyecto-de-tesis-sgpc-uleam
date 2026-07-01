"""
Servicio para construir el detalle completo de una publicación según su tipo.
"""

from core.models import (
    Articulo,
    CapituloLibro,
    Libro,
    Ponencia,
    Publicacion,
    PublicacionAutor,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
    tipo_publicacion_label,
)


def _fecha_a_str(value):
    if not value:
        return None

    try:
        return value.isoformat()
    except Exception:
        return str(value)


def _safe_related(obj, rel_name):
    try:
        return getattr(obj, rel_name)
    except Exception:
        return None


def _safe_file_url(file_field):
    try:
        if not file_field:
            return None
        return file_field.url
    except Exception:
        return None


def _to_str(value):
    return "" if value is None else str(value).strip()


def _to_lower(value):
    value = _to_str(value)
    return value.lower() if value else ""


def _get_articulo_payload(articulo):
    if not articulo:
        return {}

    tipo_articulo = _to_lower(getattr(articulo, "tipo_articulo", None))

    base_datos_indexada = getattr(articulo, "base_datos_indexada", None)
    base_datos_otra = getattr(articulo, "base_datos_otra", None)

    factor_impacto = getattr(articulo, "factor_impacto", None)
    cuartil = getattr(articulo, "cuartil", None)
    sjr = getattr(articulo, "sjr", None)

    if tipo_articulo == "regional":
        factor_impacto = None
        cuartil = None
        sjr = None

        base_norm = _to_lower(base_datos_indexada)
        if not base_norm:
            base_datos_indexada = None

        if base_norm != "otra":
            base_datos_otra = None

    elif tipo_articulo == "alto_impacto":
        base_datos_indexada = None
        base_datos_otra = None

        factor_impacto = _to_lower(factor_impacto) or None
        cuartil = _to_lower(cuartil) or None
        sjr = _to_str(sjr) or None

    return {
        "tipo_articulo": tipo_articulo,
        "nombre_articulo": articulo.nombre_articulo,
        "nombre_revista": articulo.nombre_revista,
        "base_datos_indexada": base_datos_indexada,
        "base_datos_otra": base_datos_otra,
        "codigo_issn": articulo.codigo_issn,
        "codigo_doi": articulo.codigo_doi,
        "factor_impacto": factor_impacto,
        "cuartil": cuartil,
        "sjr": sjr,
        "link_publicacion": articulo.link_publicacion,
        "link_revista": articulo.link_revista,
        "numero_revista": getattr(articulo, "numero_revista", None),
    }


def construir_detalle_publicacion(*, publicacion_id: int):
    pub = (
        annotate_tipo_publicacion_final(
            Publicacion.objects.select_related(
                "usuario_creador",
                "facultad",
                "carrera",
                "proyecto",
                "area",
                "subarea",
                "pais",
                "ciudad",
                "tipo",
                "articulo",
                "ponencia",
                "libro",
                "capitulo_libro",
            )
        )
        .get(id=publicacion_id)
    )

    autores_rel = (
        PublicacionAutor.objects.select_related("autor")
        .filter(publicacion=pub)
        .order_by("orden", "id")
    )

    autores = []
    for pa in autores_rel:
        autores.append(
            {
                "autor_id": pa.autor.id,
                "id": pa.autor.id,
                "nombre": str(pa.autor),
                "nombre_completo": str(pa.autor),
                "rol_autoria": pa.rol_autoria,
                "orden": pa.orden,
            }
        )

    tipo = getattr(pub, "tipo", None)
    codigo = ((getattr(tipo, "codigo", "") or "").strip().lower())
    tipo_final = getattr(pub, "tipo_publicacion_final", "sin_clasificar")

    ARTICULOS = {"articulo", "articulo_regional", "articulo_alto_impacto"}
    CAPITULOS = {"capitulo_libro", "capitulo"}

    origen_tipo = str(pub.origen_tipo or "ninguno").strip().lower()
    origen_grado = pub.origen_grado if origen_tipo == "tic" else None

    data = {
        "id": pub.id,
        "tipo": getattr(tipo, "nombre", None),
        "tipo_codigo": getattr(tipo, "codigo", None),
        "tipo_publicacion_final": tipo_final,
        "tipo_publicacion_final_label": tipo_publicacion_label(tipo_final),
        "proyecto": pub.proyecto.nombre if pub.proyecto else None,
        "facultad": pub.facultad.nombre if pub.facultad else None,
        "carrera": pub.carrera.nombre if pub.carrera else None,
        "area": pub.area.nombre if pub.area else None,
        "subarea": pub.subarea.nombre if pub.subarea else None,
        "pais": pub.pais.nombre if (codigo == "ponencia" and pub.pais) else None,
        "ciudad": pub.ciudad.nombre if (codigo == "ponencia" and pub.ciudad) else None,
        "proyecto_id": pub.proyecto_id,
        "facultad_id": pub.facultad_id,
        "carrera_id": pub.carrera_id,
        "area_id": pub.area_id,
        "subarea_id": pub.subarea_id,
        "pais_id": pub.pais_id if codigo == "ponencia" else None,
        "ciudad_id": pub.ciudad_id if codigo == "ponencia" else None,
        "fecha_publicacion": _fecha_a_str(pub.fecha_publicacion),
        "anio_publicacion": pub.anio_publicacion,
        "origen_tipo": origen_tipo,
        "origen_grado": origen_grado,
        "archivo_pdf": _safe_file_url(pub.archivo_pdf),
        "autores": autores,
    }

    if codigo == "ponencia":
        pon = _safe_related(pub, "ponencia") or Ponencia.objects.filter(publicacion=pub).first()
        if pon:
            data.update(
                {
                    "nombre_evento": pon.nombre_evento,
                    "nombre_ponencia": pon.nombre_ponencia,
                    "codigo_issn_isbn": pon.codigo_issn_isbn,
                    "tipo_presentacion": pon.tipo_presentacion,
                    "link_evento": pon.link_evento,
                }
            )

    elif codigo in ARTICULOS:
        art = _safe_related(pub, "articulo") or Articulo.objects.filter(publicacion=pub).first()
        if art:
            data.update(_get_articulo_payload(art))

    elif codigo == "libro":
        lib = _safe_related(pub, "libro") or Libro.objects.filter(publicacion=pub).first()
        if lib:
            data.update(
                {
                    "nombre_libro": lib.nombre_libro,
                    "codigo_isbn": lib.codigo_isbn,
                    "editorial_compilador": lib.editorial_compilador,
                    "revisor_par_arbitraje": lib.revisor_par_arbitraje,
                    "link_libro": lib.link_libro,
                }
            )

    elif codigo in CAPITULOS:
        cap = _safe_related(pub, "capitulo_libro") or CapituloLibro.objects.filter(publicacion=pub).first()
        if cap:
            data.update(
                {
                    "nombre_capitulo": cap.nombre_capitulo,
                    "nombre_libro": cap.nombre_libro,
                    "codigo_isbn": cap.codigo_isbn,
                    "editor_compilador": cap.editor_compilador,
                    "revisor_par_arbitraje": cap.revisor_par_arbitraje,
                    "link_capitulo": cap.link_capitulo,
                }
            )

    return data