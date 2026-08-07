"""Servicio centralizado para consultar publicaciones.

Este módulo funciona como única fuente de verdad para:

- listado institucional;
- Mis publicaciones;
- búsqueda textual;
- filtros académicos;
- filtros temporales;
- filtros por tipo y origen;
- ordenamiento;
- futuras consultas de exportación Excel.

Las vistas no deben reconstruir estas reglas por separado.
"""

from django.db.models import (
    Case,
    CharField,
    F,
    Prefetch,
    Q,
    Value,
    When,
)
from django.db.models.functions import (
    Lower,
)
from rest_framework.exceptions import (
    ValidationError,
)

from core.models import (
    Publicacion,
    PublicacionAutor,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    resolve_user_autor_id,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
    normalize_tipo_publicacion_final,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

ORIGENES_VALIDOS = {
    "ninguno",
    "tic",
    "maestria",
    "doctoral",
    "otro",
}

ORDENES_VALIDOS = {
    "recientes",
    "antiguas",
    "titulo_asc",
    "titulo_desc",
    "tipo",
}

TRUE_VALUES = {
    "1",
    "true",
    "si",
    "sí",
    "yes",
    "on",
}

FALSE_VALUES = {
    "0",
    "false",
    "no",
    "off",
    "",
}


# ============================================================
# NORMALIZACIÓN GENERAL
# ============================================================

def _to_text(
    value,
):
    return str(
        value or ""
    ).strip()


def _to_lower(
    value,
):
    return _to_text(
        value
    ).lower()


def _first_value(
    source,
    *keys,
):
    """
    Obtiene el primer parámetro no vacío entre varios aliases.

    Permite mantener compatibilidad con diferentes nombres
    utilizados históricamente por frontend y backend.
    """

    for key in keys:
        value = source.get(
            key
        )

        if value not in (
            None,
            "",
        ):
            return value

    return None


def _parse_positive_int(
    value,
    *,
    field_name,
    required=False,
):
    """
    Convierte un parámetro en entero positivo.

    Devuelve None cuando el campo no fue enviado.
    """

    if value in (
        None,
        "",
    ):
        if required:
            raise ValidationError(
                {
                    field_name: [
                        "Este campo es obligatorio."
                    ]
                }
            )

        return None

    try:
        parsed = int(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        raise ValidationError(
            {
                field_name: [
                    "Debe ser un número entero válido."
                ]
            }
        )

    if parsed < 1:
        raise ValidationError(
            {
                field_name: [
                    "Debe ser mayor o igual a 1."
                ]
            }
        )

    return parsed


def _parse_boolean(
    value,
    *,
    field_name,
):
    """
    Normaliza valores booleanos enviados mediante query params.
    """

    if value in (
        None,
        "",
    ):
        return False

    normalized = _to_lower(
        value
    )

    if normalized in TRUE_VALUES:
        return True

    if normalized in FALSE_VALUES:
        return False

    raise ValidationError(
        {
            field_name: [
                "Debe enviar un valor booleano válido."
            ]
        }
    )


# ============================================================
# EXTRACCIÓN Y VALIDACIÓN DE FILTROS
# ============================================================

def extract_publicaciones_filters(
    query_params,
):
    """
    Convierte request.query_params en un diccionario validado.

    Parámetros reconocidos
    ----------------------
    tipo
    tipo_publicacion_final

    origen
    origen_tipo

    anio
    mes
    anio_desde
    anio_hasta

    texto
    q
    search

    facultad
    carrera
    proyecto

    orden
    ordering

    solo_con_pdf
    """

    query_params = (
        query_params
        or {}
    )

    raw_tipo = _first_value(
        query_params,
        "tipo",
        "tipo_publicacion_final",
    )

    tipo = None

    if raw_tipo:
        tipo = (
            normalize_tipo_publicacion_final(
                raw_tipo
            )
        )

        if not tipo:
            raise ValidationError(
                {
                    "tipo": [
                        "El tipo de publicación "
                        "seleccionado no es válido."
                    ]
                }
            )

    raw_origen = _first_value(
        query_params,
        "origen_tipo",
        "origen",
    )

    origen_tipo = None

    if raw_origen:
        origen_tipo = _to_lower(
            raw_origen
        )

        if (
            origen_tipo
            not in ORIGENES_VALIDOS
        ):
            raise ValidationError(
                {
                    "origen_tipo": [
                        "El origen de la publicación "
                        "seleccionado no es válido."
                    ]
                }
            )

    anio = _parse_positive_int(
        _first_value(
            query_params,
            "anio",
        ),
        field_name="anio",
    )

    mes = _parse_positive_int(
        _first_value(
            query_params,
            "mes",
            "mes_publicacion",
        ),
        field_name="mes",
    )

    if mes is not None and mes > 12:
        raise ValidationError(
            {
                "mes": [
                    "El mes debe estar entre 1 y 12."
                ]
            }
        )

    anio_desde = _parse_positive_int(
        _first_value(
            query_params,
            "anio_desde",
            "desde",
        ),
        field_name="anio_desde",
    )

    anio_hasta = _parse_positive_int(
        _first_value(
            query_params,
            "anio_hasta",
            "hasta",
        ),
        field_name="anio_hasta",
    )

    if anio:
        anio_desde = None
        anio_hasta = None

    elif (
        anio_desde
        and anio_hasta
        and anio_desde > anio_hasta
    ):
        anio_desde, anio_hasta = (
            anio_hasta,
            anio_desde,
        )

    facultad_id = _parse_positive_int(
        _first_value(
            query_params,
            "facultad",
            "facultad_id",
        ),
        field_name="facultad",
    )

    carrera_id = _parse_positive_int(
        _first_value(
            query_params,
            "carrera",
            "carrera_id",
        ),
        field_name="carrera",
    )

    proyecto_id = _parse_positive_int(
        _first_value(
            query_params,
            "proyecto",
            "proyecto_id",
        ),
        field_name="proyecto",
    )

    texto = _to_text(
        _first_value(
            query_params,
            "texto",
            "q",
            "search",
        )
    )

    orden = _to_lower(
        _first_value(
            query_params,
            "orden",
            "ordering",
        )
        or "recientes"
    )

    if orden not in ORDENES_VALIDOS:
        raise ValidationError(
            {
                "orden": [
                    "El criterio de ordenamiento "
                    "seleccionado no es válido."
                ]
            }
        )

    solo_con_pdf = _parse_boolean(
        _first_value(
            query_params,
            "solo_con_pdf",
            "con_pdf",
        ),
        field_name="solo_con_pdf",
    )

    return {
        "tipo": tipo,
        "origen_tipo": origen_tipo,
        "anio": anio,
        "mes": mes,
        "anio_desde": anio_desde,
        "anio_hasta": anio_hasta,
        "texto": texto,
        "facultad_id": facultad_id,
        "carrera_id": carrera_id,
        "proyecto_id": proyecto_id,
        "orden": orden,
        "solo_con_pdf": solo_con_pdf,
    }


# ============================================================
# QUERYSET BASE
# ============================================================

def build_publicaciones_base_queryset():
    """
    Construye el queryset optimizado común.

    Incluye las relaciones que utiliza el serializer de listado
    y evita consultas repetitivas por cada publicación.
    """

    autores_prefetch = Prefetch(
        "participaciones",
        queryset=(
            PublicacionAutor.objects
            .select_related(
                "autor",
                "autor__usuario",
            )
            .order_by(
                "orden",
                "id",
            )
        ),
        to_attr=(
            "participaciones_ordenadas"
        ),
    )

    queryset = (
        Publicacion.objects
        .select_related(
            "tipo",
            "proyecto",
            "proyecto__carrera",
            "proyecto__carrera__facultad",

            "usuario_creador",
            "admin_registrador",

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

    queryset = (
        annotate_tipo_publicacion_final(
            queryset
        )
        .exclude(
            tipo_publicacion_final=(
                "sin_clasificar"
            )
        )
    )

    return queryset


# ============================================================
# MIS PUBLICACIONES
# ============================================================

def apply_user_publicaciones_scope(
    queryset,
    *,
    user,
):
    """
    Limita el queryset a las publicaciones relacionadas con
    el usuario autenticado.

    Incluye:

    - publicaciones creadas por el usuario;
    - publicaciones donde participa como Autor;
    - compatibilidad con registros antiguos resueltos mediante
      resolve_user_autor_id.
    """

    if (
        user is None
        or not getattr(
            user,
            "is_authenticated",
            False,
        )
    ):
        return queryset.none()

    user_filter = Q(
        usuario_creador=user
    )

    # Relación moderna:
    #
    # Usuario -> Autor -> PublicacionAutor -> Publicacion

    user_filter |= Q(
        participaciones__autor__usuario=user
    )

    # Compatibilidad con autores históricos que pudieran estar
    # vinculados mediante la utilidad existente.

    autor_id = resolve_user_autor_id(
        user
    )

    if autor_id:
        user_filter |= Q(
            participaciones__autor_id=(
                autor_id
            )
        )

    return (
        queryset
        .filter(
            user_filter
        )
        .distinct()
    )


# ============================================================
# FILTROS
# ============================================================

def apply_publicaciones_filters(
    queryset,
    filters,
):
    """
    Aplica todos los filtros oficiales sobre el queryset.
    """

    filters = dict(
        filters or {}
    )

    tipo = filters.get(
        "tipo"
    )

    if tipo:
        queryset = queryset.filter(
            tipo_publicacion_final=tipo
        )

    origen_tipo = filters.get(
        "origen_tipo"
    )

    if origen_tipo:
        queryset = queryset.filter(
            origen_tipo=origen_tipo
        )

    anio = filters.get(
        "anio"
    )

    anio_desde = filters.get(
        "anio_desde"
    )

    anio_hasta = filters.get(
        "anio_hasta"
    )

    if anio:
        queryset = queryset.filter(
            anio_publicacion=anio
        )

    else:
        if anio_desde:
            queryset = queryset.filter(
                anio_publicacion__gte=(
                    anio_desde
                )
            )

        if anio_hasta:
            queryset = queryset.filter(
                anio_publicacion__lte=(
                    anio_hasta
                )
            )

    mes = filters.get(
        "mes"
    )

    if mes:
        queryset = queryset.filter(
            mes_publicacion=mes
        )

    facultad_id = filters.get(
        "facultad_id"
    )

    if facultad_id:
        queryset = queryset.filter(
            carrera__facultad_id=(
                facultad_id
            )
        )

    carrera_id = filters.get(
        "carrera_id"
    )

    if carrera_id:
        queryset = queryset.filter(
            carrera_id=carrera_id
        )

    proyecto_id = filters.get(
        "proyecto_id"
    )

    if proyecto_id:
        queryset = queryset.filter(
            proyecto_id=proyecto_id
        )

    texto = _to_text(
        filters.get(
            "texto"
        )
    )

    if texto:
        queryset = queryset.filter(
            _build_text_search_query(
                texto
            )
        )

    if filters.get(
        "solo_con_pdf"
    ):
        queryset = queryset.filter(
            (
                Q(
                    archivo_pdf__isnull=False
                )
                & ~Q(
                    archivo_pdf=""
                )
            )
            |
            (
                Q(
                    archivos__archivo__isnull=False
                )
                & ~Q(
                    archivos__archivo=""
                )
            )
        )

    return queryset.distinct()


def _build_text_search_query(
    texto,
):
    """
    Construye la búsqueda global utilizando campos comunes y
    campos específicos de cada subtipo de publicación.
    """

    return (
        # -----------------------------------------------------
        # Tipo de publicación
        # -----------------------------------------------------

        Q(
            tipo__nombre__icontains=texto
        )
        |
        Q(
            tipo__codigo__icontains=texto
        )

        # -----------------------------------------------------
        # Ubicación académica y proyecto
        # -----------------------------------------------------

        |
        Q(
            carrera__nombre__icontains=texto
        )
        |
        Q(
            carrera__facultad__nombre__icontains=texto
        )
        |
        Q(
            carrera__facultad__siglas__icontains=texto
        )
        |
        Q(
            proyecto__nombre__icontains=texto
        )
        |
        Q(
            proyecto__descripcion__icontains=texto
        )

        # -----------------------------------------------------
        # Autores
        # -----------------------------------------------------

        |
        Q(
            participaciones__autor__nombres__icontains=texto
        )
        |
        Q(
            participaciones__autor__apellidos__icontains=texto
        )
        |
        Q(
            participaciones__autor__correo__icontains=texto
        )
        |
        Q(
            participaciones__autor__institucion__icontains=texto
        )

        # -----------------------------------------------------
        # Clasificación académica
        # -----------------------------------------------------

        |
        Q(
            area__nombre__icontains=texto
        )
        |
        Q(
            subarea__nombre__icontains=texto
        )
        |
        Q(
            origen_grado__icontains=texto
        )
        |
        Q(
            pais__nombre__icontains=texto
        )
        |
        Q(
            ciudad__nombre__icontains=texto
        )

        # -----------------------------------------------------
        # Artículo
        # -----------------------------------------------------

        |
        Q(
            articulo__nombre_articulo__icontains=texto
        )
        |
        Q(
            articulo__codigo_doi__icontains=texto
        )
        |
        Q(
            articulo__codigo_issn__icontains=texto
        )
        |
        Q(
            articulo__nombre_revista__icontains=texto
        )
        |
        Q(
            articulo__base_datos_indexada__icontains=texto
        )
        |
        Q(
            articulo__base_datos_otra__icontains=texto
        )
        |
        Q(
            articulo__factor_impacto__icontains=texto
        )
        |
        Q(
            articulo__cuartil__icontains=texto
        )

        # -----------------------------------------------------
        # Ponencia
        # -----------------------------------------------------

        |
        Q(
            ponencia__nombre_ponencia__icontains=texto
        )
        |
        Q(
            ponencia__nombre_evento__icontains=texto
        )
        |
        Q(
            ponencia__codigo_issn_isbn__icontains=texto
        )
        |
        Q(
            ponencia__tipo_presentacion__icontains=texto
        )
        |
        Q(
            ponencia__tipo_presentacion_otro__icontains=texto
        )

        # -----------------------------------------------------
        # Libro
        # -----------------------------------------------------

        |
        Q(
            libro__nombre_libro__icontains=texto
        )
        |
        Q(
            libro__codigo_isbn__icontains=texto
        )
        |
        Q(
            libro__editorial_compilador__icontains=texto
        )

        # -----------------------------------------------------
        # Capítulo de libro
        # -----------------------------------------------------

        |
        Q(
            capitulo_libro__nombre_capitulo__icontains=texto
        )
        |
        Q(
            capitulo_libro__nombre_libro__icontains=texto
        )
        |
        Q(
            capitulo_libro__codigo_isbn__icontains=texto
        )
        |
        Q(
            capitulo_libro__editor_compilador__icontains=texto
        )
    )


# ============================================================
# TÍTULO NORMALIZADO PARA ORDENAMIENTO
# ============================================================

def annotate_publicaciones_list_title(
    queryset,
):
    """
    Añade titulo_listado para ordenar publicaciones que tienen
    el título almacenado en tablas de subtipo diferentes.
    """

    return queryset.annotate(
        titulo_listado=Case(
            When(
                articulo__isnull=False,
                then=F(
                    "articulo__nombre_articulo"
                ),
            ),
            When(
                ponencia__isnull=False,
                then=F(
                    "ponencia__nombre_ponencia"
                ),
            ),
            When(
                libro__isnull=False,
                then=F(
                    "libro__nombre_libro"
                ),
            ),
            When(
                capitulo_libro__isnull=False,
                then=F(
                    "capitulo_libro__nombre_capitulo"
                ),
            ),
            When(
                proyecto__isnull=False,
                then=F(
                    "proyecto__nombre"
                ),
            ),
            default=Value(
                ""
            ),
            output_field=CharField(),
        )
    )


# ============================================================
# ORDENAMIENTO
# ============================================================

def apply_publicaciones_ordering(
    queryset,
    orden,
):
    """
    Aplica uno de los ordenamientos admitidos por el frontend.
    """

    orden = _to_lower(
        orden
        or "recientes"
    )

    if orden not in ORDENES_VALIDOS:
        orden = "recientes"

    if orden == "antiguas":
        return queryset.order_by(
            F(
                "anio_publicacion"
            ).asc(
                nulls_last=True
            ),
            F(
                "mes_publicacion"
            ).asc(
                nulls_last=True
            ),
            "id",
        )

    if orden in {
        "titulo_asc",
        "titulo_desc",
        "tipo",
    }:
        queryset = (
            annotate_publicaciones_list_title(
                queryset
            )
            .annotate(
                titulo_listado_normalizado=Lower(
                    "titulo_listado"
                )
            )
        )

    if orden == "titulo_asc":
        return queryset.order_by(
            "titulo_listado_normalizado",
            "id",
        )

    if orden == "titulo_desc":
        return queryset.order_by(
            "-titulo_listado_normalizado",
            "-id",
        )

    if orden == "tipo":
        return queryset.order_by(
            "tipo_publicacion_final",
            "titulo_listado_normalizado",
            "id",
        )

    return queryset.order_by(
        F(
            "anio_publicacion"
        ).desc(
            nulls_last=True
        ),
        F(
            "mes_publicacion"
        ).desc(
            nulls_last=True
        ),
        "-id",
    )




# ============================================================
# AÑOS DISPONIBLES
# ============================================================

def get_publicaciones_available_years(
    *,
    filters=None,
    user=None,
    solo_mias=False,
):
    """
    Devuelve los años realmente existentes en la base de datos.

    La consulta reutiliza el mismo alcance y los mismos filtros del
    listado principal. Los filtros temporales se eliminan de forma
    deliberada para que el catálogo no quede restringido por el año
    seleccionado actualmente.

    Parameters
    ----------
    filters:
        Diccionario normalizado mediante extract_publicaciones_filters.

    user:
        Usuario autenticado. Es obligatorio cuando solo_mias=True.

    solo_mias:
        Cuando es True, limita los años a publicaciones creadas por
        el usuario o donde participa como autor.
    """

    filters = dict(
        filters or {}
    )

    # El catálogo de años debe conservar filtros como tipo, origen,
    # facultad, carrera, proyecto, texto o PDF, pero no debe filtrarse
    # a sí mismo por un año o rango ya seleccionado.
    filters["anio"] = None
    filters["mes"] = None
    filters["anio_desde"] = None
    filters["anio_hasta"] = None

    queryset = (
        build_publicaciones_base_queryset()
    )

    if solo_mias:
        queryset = (
            apply_user_publicaciones_scope(
                queryset,
                user=user,
            )
        )

    queryset = apply_publicaciones_filters(
        queryset,
        filters,
    )

    # Se elimina cualquier ordenamiento previo antes del DISTINCT.
    # PostgreSQL recibe una consulta equivalente a:
    #
    # SELECT DISTINCT anio_publicacion
    # FROM publicaciones
    # WHERE anio_publicacion IS NOT NULL
    # ORDER BY anio_publicacion DESC;
    years_queryset = (
        queryset
        .filter(
            anio_publicacion__isnull=False,
            anio_publicacion__gt=0,
        )
        .order_by()
        .values_list(
            "anio_publicacion",
            flat=True,
        )
        .distinct()
        .order_by(
            "-anio_publicacion"
        )
    )

    return list(
        years_queryset
    )


# ============================================================
# SERVICIO PRINCIPAL
# ============================================================

def build_publicaciones_queryset(
    *,
    filters=None,
    user=None,
    solo_mias=False,
):
    """
    Construye el queryset final reutilizable.

    Parameters
    ----------
    filters:
        Diccionario previamente normalizado mediante
        extract_publicaciones_filters.

    user:
        Usuario autenticado. Solo es obligatorio cuando
        solo_mias=True.

    solo_mias:
        Limita el resultado a publicaciones vinculadas con
        el usuario.
    """

    filters = dict(
        filters or {}
    )

    queryset = (
        build_publicaciones_base_queryset()
    )

    if solo_mias:
        queryset = (
            apply_user_publicaciones_scope(
                queryset,
                user=user,
            )
        )

    queryset = apply_publicaciones_filters(
        queryset,
        filters,
    )

    queryset = apply_publicaciones_ordering(
        queryset,
        filters.get(
            "orden",
            "recientes",
        ),
    )

    return queryset