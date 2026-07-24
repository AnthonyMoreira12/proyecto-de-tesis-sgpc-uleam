"""
Servicio para construir el detalle completo de una publicación.

La respuesta mantiene compatibilidad con las interfaces
actuales del SGPC y respeta la estructura normalizada:

    Publicacion -> Carrera -> Facultad

Incluye:
- datos generales;
- tipo final;
- autores;
- PDF principal;
- adjuntos;
- datos específicos de artículo;
- ponencia;
- libro;
- capítulo de libro.
"""

import os

from django.db.models import Prefetch

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


ARTICULO_CODES = {
    "articulo",
    "articulo_regional",
    "articulo_alto_impacto",
}

CAPITULO_CODES = {
    "capitulo",
    "capitulo_libro",
}


def _to_str(value):
    return (
        ""
        if value is None
        else str(value).strip()
    )


def _to_lower(value):
    value = _to_str(value)

    return (
        value.lower()
        if value
        else ""
    )


def _fecha_a_str(value):
    if not value:
        return None

    try:
        return value.isoformat()
    except (
        AttributeError,
        ValueError,
    ):
        return str(value)


def _safe_related(
    obj,
    relation_name,
):
    if obj is None:
        return None

    try:
        return getattr(
            obj,
            relation_name,
        )
    except (
        AttributeError,
        ObjectDoesNotExist,
    ):
        return None
    except Exception:
        return None


# Evita importar ObjectDoesNotExist arriba únicamente
# para una función pequeña sin perder compatibilidad.
try:
    from django.core.exceptions import (
        ObjectDoesNotExist,
    )
except ImportError:
    ObjectDoesNotExist = Exception


def _safe_file_url(
    file_field,
):
    try:
        if (
            not file_field
            or not getattr(
                file_field,
                "name",
                None,
            )
        ):
            return None

        return file_field.url

    except (
        AttributeError,
        ValueError,
    ):
        return None


def _safe_file_name(
    file_field,
):
    name = _to_str(
        getattr(
            file_field,
            "name",
            None,
        )
    )

    if not name:
        return None

    return (
        os.path.basename(name)
        or None
    )


def _get_facultad_desde_publicacion(
    publicacion,
):
    """
    Facultad NO es una FK de Publicacion.

    Publicacion
        -> Carrera
            -> Facultad
    """

    carrera = _safe_related(
        publicacion,
        "carrera",
    )

    if carrera is None:
        return None

    return _safe_related(
        carrera,
        "facultad",
    )


def _get_autores_payload(
    publicacion,
):
    participaciones = getattr(
        publicacion,
        "participaciones_ordenadas",
        None,
    )

    if participaciones is None:
        participaciones = (
            PublicacionAutor.objects
            .select_related(
                "autor"
            )
            .filter(
                publicacion=publicacion
            )
            .order_by(
                "orden",
                "id",
            )
        )

    result = []

    for participacion in participaciones:
        autor = getattr(
            participacion,
            "autor",
            None,
        )

        if autor is None:
            continue

        nombres = _to_str(
            getattr(
                autor,
                "nombres",
                None,
            )
        )

        apellidos = _to_str(
            getattr(
                autor,
                "apellidos",
                None,
            )
        )

        nombre_completo = (
            f"{nombres} {apellidos}"
        ).strip()

        if not nombre_completo:
            nombre_completo = (
                _to_str(
                    getattr(
                        autor,
                        "correo",
                        None,
                    )
                )
                or _to_str(
                    getattr(
                        autor,
                        "identificacion",
                        None,
                    )
                )
                or "Autor"
            )

        result.append(
            {
                "id": autor.id,
                "autor_id": autor.id,
                "nombre": nombre_completo,
                "autor_nombre": nombre_completo,
                "nombre_completo": nombre_completo,
                "rol_autoria": (
                    participacion.rol_autoria
                ),
                "orden": (
                    participacion.orden
                ),
            }
        )

    return result


def _build_archivos_payload(
    publicacion,
):
    archivos = []

    # ---------------------------------------------------------
    # PDF principal
    # ---------------------------------------------------------

    principal_url = (
        _safe_file_url(
            publicacion.archivo_pdf
        )
    )

    if principal_url:
        archivos.append(
            {
                "id": None,
                "tipo": "principal",
                "nombre": (
                    _safe_file_name(
                        publicacion.archivo_pdf
                    )
                    or "PDF principal"
                ),
                "archivo": principal_url,
                "url": principal_url,
                "orden": 0,
                "es_principal": True,
            }
        )

    # ---------------------------------------------------------
    # Adjuntos
    # ---------------------------------------------------------

    prefetched = getattr(
        publicacion,
        "_prefetched_objects_cache",
        {},
    )

    if "archivos" in prefetched:
        adjuntos = sorted(
            prefetched["archivos"],
            key=lambda item: (
                getattr(
                    item,
                    "orden",
                    0,
                ),
                getattr(
                    item,
                    "id",
                    0,
                ),
            ),
        )

    else:
        adjuntos = (
            publicacion.archivos
            .all()
            .order_by(
                "orden",
                "id",
            )
        )

    for adjunto in adjuntos:
        url = _safe_file_url(
            adjunto.archivo
        )

        if not url:
            continue

        archivos.append(
            {
                "id": adjunto.id,
                "tipo": "adjunto",
                "nombre": (
                    _to_str(
                        adjunto.nombre
                    )
                    or _safe_file_name(
                        adjunto.archivo
                    )
                    or "Adjunto"
                ),
                "archivo": url,
                "url": url,
                "orden": adjunto.orden,
                "es_principal": False,
            }
        )

    return archivos


def _get_pdf_principal_o_adjunto(
    publicacion,
    archivos,
):
    principal_url = (
        _safe_file_url(
            publicacion.archivo_pdf
        )
    )

    if principal_url:
        return principal_url

    for archivo in archivos:
        if archivo.get(
            "es_principal"
        ):
            continue

        url = (
            archivo.get("url")
            or archivo.get("archivo")
        )

        if url:
            return url

    return None


def _get_articulo_payload(
    articulo,
):
    if articulo is None:
        return {}

    tipo_articulo = _to_lower(
        articulo.tipo_articulo
    )

    base_datos = (
        articulo.base_datos_indexada
    )

    base_datos_otra = (
        articulo.base_datos_otra
    )

    factor_impacto = (
        articulo.factor_impacto
    )

    cuartil = articulo.cuartil
    sjr = articulo.sjr

    # ---------------------------------------------------------
    # Regional
    # ---------------------------------------------------------

    if tipo_articulo == "regional":
        factor_impacto = None
        cuartil = None
        sjr = None

        if (
            _to_lower(base_datos)
            != "otra"
        ):
            base_datos_otra = None

    # ---------------------------------------------------------
    # Alto impacto
    # ---------------------------------------------------------

    elif tipo_articulo == "alto_impacto":
        base_datos = None
        base_datos_otra = None

        factor_impacto = (
            _to_lower(
                factor_impacto
            )
            or None
        )

        cuartil = (
            _to_lower(
                cuartil
            )
            or None
        )

        sjr = (
            _to_str(sjr)
            or None
        )

        if factor_impacto != "sjr":
            sjr = None

    return {
        "tipo_articulo": tipo_articulo,
        "nombre_articulo": (
            articulo.nombre_articulo
        ),
        "base_datos_indexada": (
            base_datos
        ),
        "base_datos_otra": (
            base_datos_otra
        ),
        "codigo_doi": (
            articulo.codigo_doi
        ),
        "codigo_issn": (
            articulo.codigo_issn
        ),
        "nombre_revista": (
            articulo.nombre_revista
        ),
        "numero_revista": (
            articulo.numero_revista
        ),
        "link_revista": (
            articulo.link_revista
        ),
        "link_publicacion": (
            articulo.link_publicacion
        ),
        "factor_impacto": (
            factor_impacto
        ),
        "cuartil": cuartil,
        "sjr": sjr,
    }


def construir_detalle_publicacion(
    *,
    publicacion_id,
):
    autores_prefetch = Prefetch(
        "participaciones",
        queryset=(
            PublicacionAutor.objects
            .select_related(
                "autor"
            )
            .order_by(
                "orden",
                "id",
            )
        ),
        to_attr="participaciones_ordenadas",
    )

    queryset = (
        Publicacion.objects
        .select_related(
            "usuario_creador",
            "admin_registrador",

            "tipo",
            "proyecto",

            "carrera",
            "carrera__facultad",

            "area",
            "subarea",

            "pais",
            "ciudad",

            "articulo",
            "ponencia",
            "libro",
            "capitulo_libro",
        )
        .prefetch_related(
            autores_prefetch,
            "archivos",
        )
    )

    publicacion = (
        annotate_tipo_publicacion_final(
            queryset
        )
        .get(
            pk=publicacion_id
        )
    )

    tipo = publicacion.tipo

    tipo_codigo = _to_lower(
        getattr(
            tipo,
            "codigo",
            None,
        )
    )

    tipo_categoria = _to_lower(
        getattr(
            tipo,
            "categoria",
            None,
        )
    )

    tipo_final = _to_lower(
        getattr(
            publicacion,
            "tipo_publicacion_final",
            None,
        )
    ) or "sin_clasificar"

    facultad = (
        _get_facultad_desde_publicacion(
            publicacion
        )
    )

    archivos = (
        _build_archivos_payload(
            publicacion
        )
    )

    archivo_pdf_url = (
        _get_pdf_principal_o_adjunto(
            publicacion,
            archivos,
        )
    )

    autores = (
        _get_autores_payload(
            publicacion
        )
    )

    origen_tipo = (
        _to_lower(
            publicacion.origen_tipo
        )
        or "ninguno"
    )

    origen_grado = (
        publicacion.origen_grado
        if origen_tipo == "tic"
        else None
    )

    data = {
        # -----------------------------------------------------
        # Identidad
        # -----------------------------------------------------

        "id": publicacion.id,
        "numero": publicacion.numero,

        "tipo": getattr(
            tipo,
            "nombre",
            None,
        ),
        "tipo_codigo": tipo_codigo,

        "tipo_publicacion_final": (
            tipo_final
        ),
        "tipo_publicacion_final_label": (
            tipo_publicacion_label(
                tipo_final
            )
        ),

        # -----------------------------------------------------
        # Relaciones institucionales
        # -----------------------------------------------------

        "proyecto_id": (
            publicacion.proyecto_id
        ),
        "proyecto": (
            publicacion.proyecto.nombre
            if publicacion.proyecto
            else None
        ),

        "facultad_id": (
            facultad.id
            if facultad
            else None
        ),
        "facultad": (
            facultad.nombre
            if facultad
            else None
        ),

        "carrera_id": (
            publicacion.carrera_id
        ),
        "carrera": (
            publicacion.carrera.nombre
            if publicacion.carrera
            else None
        ),

        "area_id": (
            publicacion.area_id
        ),
        "area": (
            publicacion.area.nombre
            if publicacion.area
            else None
        ),

        "subarea_id": (
            publicacion.subarea_id
        ),
        "subarea": (
            publicacion.subarea.nombre
            if publicacion.subarea
            else None
        ),

        # -----------------------------------------------------
        # Localización
        #
        # Únicamente aplica a Ponencia.
        # -----------------------------------------------------

        "pais_id": (
            publicacion.pais_id
            if tipo_final == "ponencia"
            else None
        ),
        "pais": (
            publicacion.pais.nombre
            if (
                tipo_final == "ponencia"
                and publicacion.pais
            )
            else None
        ),

        "ciudad_id": (
            publicacion.ciudad_id
            if tipo_final == "ponencia"
            else None
        ),
        "ciudad": (
            publicacion.ciudad.nombre
            if (
                tipo_final == "ponencia"
                and publicacion.ciudad
            )
            else None
        ),

        # -----------------------------------------------------
        # Origen
        # -----------------------------------------------------

        "origen_tipo": origen_tipo,
        "origen_grado": origen_grado,

        # -----------------------------------------------------
        # Fecha
        # -----------------------------------------------------

        "fecha_publicacion": (
            _fecha_a_str(
                publicacion.fecha_publicacion
            )
        ),
        "anio_publicacion": (
            publicacion.anio_publicacion
        ),

        # -----------------------------------------------------
        # Archivos
        # -----------------------------------------------------

        "archivo_pdf": (
            archivo_pdf_url
        ),
        "archivo_pdf_url": (
            archivo_pdf_url
        ),
        "pdf_url": (
            archivo_pdf_url
        ),

        "tiene_pdf": bool(
            archivo_pdf_url
        ),
        "has_pdf": bool(
            archivo_pdf_url
        ),
        "hasPdf": bool(
            archivo_pdf_url
        ),

        "archivos": archivos,

        # -----------------------------------------------------
        # Autores
        # -----------------------------------------------------

        "autores": autores,

        # -----------------------------------------------------
        # Registro
        # -----------------------------------------------------

        "registrado_por_admin": (
            publicacion.registrado_por_admin
        ),
        "admin_registrador_id": (
            publicacion.admin_registrador_id
        ),
        "usuario_creador_id": (
            publicacion.usuario_creador_id
        ),
    }

    # =========================================================
    # PONENCIA
    # =========================================================

    if tipo_final == "ponencia":
        ponencia = _safe_related(
            publicacion,
            "ponencia",
        )

        if ponencia is None:
            ponencia = (
                Ponencia.objects
                .filter(
                    publicacion=publicacion
                )
                .first()
            )

        if ponencia:
            data.update(
                {
                    "nombre_evento": (
                        ponencia.nombre_evento
                    ),
                    "nombre_ponencia": (
                        ponencia.nombre_ponencia
                    ),
                    "codigo_issn_isbn": (
                        ponencia.codigo_issn_isbn
                    ),
                    "tipo_presentacion": (
                        ponencia.tipo_presentacion
                    ),
                    "tipo_presentacion_otro": (
                        ponencia
                        .tipo_presentacion_otro
                    ),
                    "link_evento": (
                        ponencia.link_evento
                    ),
                    "revisor_par_arbitraje": (
                        ponencia
                        .revisor_par_arbitraje
                    ),
                }
            )

    # =========================================================
    # ARTÍCULO
    # =========================================================

    elif (
        tipo_final
        in {
            "articulo_regional",
            "articulo_alto_impacto",
        }
        or tipo_categoria == "articulo"
        or tipo_codigo in ARTICULO_CODES
    ):
        articulo = _safe_related(
            publicacion,
            "articulo",
        )

        if articulo is None:
            articulo = (
                Articulo.objects
                .filter(
                    publicacion=publicacion
                )
                .first()
            )

        if articulo:
            data.update(
                _get_articulo_payload(
                    articulo
                )
            )

    # =========================================================
    # LIBRO
    # =========================================================

    elif tipo_final == "libro":
        libro = _safe_related(
            publicacion,
            "libro",
        )

        if libro is None:
            libro = (
                Libro.objects
                .filter(
                    publicacion=publicacion
                )
                .first()
            )

        if libro:
            data.update(
                {
                    "nombre_libro": (
                        libro.nombre_libro
                    ),
                    "codigo_isbn": (
                        libro.codigo_isbn
                    ),
                    "editorial_compilador": (
                        libro
                        .editorial_compilador
                    ),
                    "revisor_par_arbitraje": (
                        libro
                        .revisor_par_arbitraje
                    ),
                    "link_libro": (
                        libro.link_libro
                    ),
                }
            )

    # =========================================================
    # CAPÍTULO
    # =========================================================

    elif (
        tipo_final
        == "capitulo_libro"
        or tipo_codigo
        in CAPITULO_CODES
    ):
        capitulo = _safe_related(
            publicacion,
            "capitulo_libro",
        )

        if capitulo is None:
            capitulo = (
                CapituloLibro.objects
                .filter(
                    publicacion=publicacion
                )
                .first()
            )

        if capitulo:
            data.update(
                {
                    "nombre_capitulo": (
                        capitulo.nombre_capitulo
                    ),
                    "nombre_libro": (
                        capitulo.nombre_libro
                    ),
                    "codigo_isbn": (
                        capitulo.codigo_isbn
                    ),
                    "editor_compilador": (
                        capitulo
                        .editor_compilador
                    ),
                    "revisor_par_arbitraje": (
                        capitulo
                        .revisor_par_arbitraje
                    ),
                    "link_capitulo": (
                        capitulo.link_capitulo
                    ),
                }
            )

    return data