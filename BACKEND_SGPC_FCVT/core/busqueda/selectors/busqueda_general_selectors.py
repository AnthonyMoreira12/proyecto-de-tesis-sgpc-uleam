"""
Selectores para la búsqueda académica general.

Este módulo centraliza las consultas de:

- Investigadores y usuarios académicos.
- Autores.
- Proyectos.
- Publicaciones.

Los selectores:

- Normalizan los términos de búsqueda.
- Permiten consultas compuestas por varias palabras.
- Limitan defensivamente la cantidad de resultados.
- Priorizan coincidencias exactas y por prefijo.
- Evitan exponer usuarios inactivos en la búsqueda de cuentas.
- Incluyen autores externos pendientes en la búsqueda científica.
- Derivan la facultad desde carrera.facultad.
- Incorporan la sede institucional cuando corresponde.
- Buscan publicaciones por sus autores científicos reales.
- Buscan en los campos específicos de artículos, ponencias,
  libros y capítulos de libro.
- Excluyen publicaciones sin clasificación válida.
"""

import unicodedata

from django.db.models import (
    Case,
    CharField,
    F,
    IntegerField,
    Prefetch,
    Q,
    Value,
    When,
)
from django.db.models.functions import Concat

from core.models import (
    Autor,
    Proyecto,
    Publicacion,
    PublicacionAutor,
    Usuario,
)
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

SEARCH_LIMIT = 8
MAX_SEARCH_LIMIT = 20
MAX_SEARCH_QUERY_LENGTH = 200


# ============================================================
# NORMALIZACIÓN
# ============================================================

def _normalize_query(value):
    """
    Normaliza un término de búsqueda.

    - Aplica normalización Unicode.
    - Elimina espacios repetidos.
    - Limita defensivamente su longitud.
    """
    normalized = unicodedata.normalize(
        "NFKC",
        str(value or ""),
    )

    normalized = " ".join(
        normalized.split()
    )

    return normalized[
        :MAX_SEARCH_QUERY_LENGTH
    ]


def _normalize_limit(
    value,
    *,
    default=SEARCH_LIMIT,
):
    """
    Convierte el límite en un entero dentro del rango permitido.
    """
    if isinstance(value, bool):
        return int(default)

    try:
        normalized_limit = int(value)

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        normalized_limit = int(default)

    return max(
        1,
        min(
            normalized_limit,
            MAX_SEARCH_LIMIT,
        ),
    )


def _query_terms(query):
    """
    Divide la consulta en términos únicos.

    Cada término deberá coincidir con al menos uno de los campos
    buscables de la entidad. Esto permite encontrar nombres
    completos aunque nombres y apellidos estén almacenados en
    columnas diferentes.
    """
    seen = set()
    terms = []

    for raw_term in _normalize_query(query).split():
        key = raw_term.casefold()

        if not key or key in seen:
            continue

        seen.add(key)
        terms.append(raw_term)

    return terms


def _positive_integer(value):
    """
    Convierte una cadena en entero positivo cuando es posible.
    """
    if isinstance(value, bool):
        return None

    try:
        parsed = int(str(value).strip())

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None

    return parsed if parsed > 0 else None


def _apply_terms(queryset, terms, query_builder):
    """
    Aplica una condición de búsqueda por cada término.

    La consulta conserva una semántica AND entre palabras y OR
    entre los campos disponibles para cada palabra.
    """
    for term in terms:
        queryset = queryset.filter(
            query_builder(term)
        )

    return queryset


# ============================================================
# CONSULTAS REUTILIZABLES
# ============================================================

def _user_term_query(term):
    return (
        Q(_search_full_name__icontains=term)
        | Q(nombres__icontains=term)
        | Q(apellidos__icontains=term)
        | Q(email__icontains=term)
        | Q(identificacion__icontains=term)
        | Q(sede__nombre__icontains=term)
        | Q(sede__codigo__icontains=term)
        | Q(sede__ciudad__icontains=term)
        | Q(carrera__nombre__icontains=term)
        | Q(carrera__facultad__nombre__icontains=term)
    )


def _project_term_query(term):
    return (
        Q(nombre__icontains=term)
        | Q(descripcion__icontains=term)
        | Q(sede__nombre__icontains=term)
        | Q(sede__codigo__icontains=term)
        | Q(sede__ciudad__icontains=term)
        | Q(carrera__nombre__icontains=term)
        | Q(carrera__facultad__nombre__icontains=term)
        | Q(creado_por__nombres__icontains=term)
        | Q(creado_por__apellidos__icontains=term)
    )


def _publication_term_query(term):
    """
    Construye la búsqueda completa de publicaciones.

    Incluye campos generales, campos específicos de cada subtipo
    y autores científicos asociados mediante PublicacionAutor.
    """
    return (
        # Datos generales
        Q(tipo__nombre__icontains=term)
        | Q(tipo__codigo__icontains=term)
        | Q(tipo__categoria__icontains=term)
        | Q(proyecto__nombre__icontains=term)
        | Q(sede__nombre__icontains=term)
        | Q(sede__codigo__icontains=term)
        | Q(sede__ciudad__icontains=term)
        | Q(carrera__facultad__nombre__icontains=term)
        | Q(carrera__nombre__icontains=term)
        | Q(area__nombre__icontains=term)
        | Q(subarea__nombre__icontains=term)
        | Q(usuario_creador__nombres__icontains=term)
        | Q(usuario_creador__apellidos__icontains=term)

        # Autores científicos reales
        | Q(participaciones__autor__nombres__icontains=term)
        | Q(participaciones__autor__apellidos__icontains=term)
        | Q(participaciones__autor__institucion__icontains=term)
        | Q(participaciones__autor__orcid__icontains=term)
        | Q(participaciones__autor__registro_senescyt__icontains=term)
        | Q(participaciones__autor__google_scholar__icontains=term)
        | Q(participaciones__autor__scopus_id__icontains=term)
        | Q(participaciones__autor__usuario__nombres__icontains=term)
        | Q(participaciones__autor__usuario__apellidos__icontains=term)

        # Artículos
        | Q(articulo__nombre_articulo__icontains=term)
        | Q(articulo__codigo_doi__icontains=term)
        | Q(articulo__codigo_issn__icontains=term)
        | Q(articulo__nombre_revista__icontains=term)
        | Q(articulo__base_datos_indexada__icontains=term)
        | Q(articulo__base_datos_otra__icontains=term)

        # Ponencias
        | Q(ponencia__nombre_ponencia__icontains=term)
        | Q(ponencia__nombre_evento__icontains=term)
        | Q(ponencia__codigo_issn_isbn__icontains=term)
        | Q(ponencia__tipo_presentacion__icontains=term)
        | Q(ponencia__tipo_presentacion_otro__icontains=term)

        # Libros
        | Q(libro__nombre_libro__icontains=term)
        | Q(libro__codigo_isbn__icontains=term)
        | Q(libro__editorial_compilador__icontains=term)

        # Capítulos de libro
        | Q(capitulo_libro__nombre_capitulo__icontains=term)
        | Q(capitulo_libro__nombre_libro__icontains=term)
        | Q(capitulo_libro__codigo_isbn__icontains=term)
        | Q(capitulo_libro__editor_compilador__icontains=term)
    )


def _author_term_query(term):
    return (
        Q(_search_full_name__icontains=term)
        | Q(_linked_full_name__icontains=term)
        | Q(nombres__icontains=term)
        | Q(apellidos__icontains=term)
        | Q(correo__icontains=term)
        | Q(identificacion__icontains=term)
        | Q(institucion__icontains=term)
        | Q(orcid__icontains=term)
        | Q(registro_senescyt__icontains=term)
        | Q(google_scholar__icontains=term)
        | Q(scopus_id__icontains=term)
        | Q(usuario__nombres__icontains=term)
        | Q(usuario__apellidos__icontains=term)
        | Q(usuario__email__icontains=term)
        | Q(usuario__identificacion__icontains=term)
        | Q(usuario__sede__nombre__icontains=term)
        | Q(usuario__sede__codigo__icontains=term)
        | Q(usuario__sede__ciudad__icontains=term)
        | (
            Q(
                participaciones__publicacion__estado=(
                    Publicacion.ESTADO_APROBADA
                )
            )
            & (
                Q(
                    participaciones__publicacion__articulo__nombre_articulo__icontains=(
                        term
                    )
                )
                | Q(
                    participaciones__publicacion__ponencia__nombre_ponencia__icontains=(
                        term
                    )
                )
                | Q(
                    participaciones__publicacion__libro__nombre_libro__icontains=(
                        term
                    )
                )
                | Q(
                    participaciones__publicacion__capitulo_libro__nombre_capitulo__icontains=(
                        term
                    )
                )
            )
        )
    )


def _publication_participations_queryset():
    """
    Carga las autorías científicas en el orden registrado.
    """
    return (
        PublicacionAutor.objects
        .select_related(
            "autor",
            "autor__usuario",
            "autor__usuario__sede",
        )
        .order_by(
            "orden",
            "pk",
        )
    )


# ============================================================
# USUARIOS ACADÉMICOS
# ============================================================

def buscar_usuarios(
    q,
    *,
    limit=SEARCH_LIMIT,
):
    """
    Busca usuarios académicos activos.

    No devuelve administradores que no tengan rol académico ni
    cuentas inactivas creadas como registros pendientes.
    """
    query = _normalize_query(q)
    normalized_limit = _normalize_limit(limit)

    if not query:
        return Usuario.objects.none()

    academic_roles = [
        Usuario.Rol.AUTOR,
        Usuario.Rol.AUTOR_EXTERNO,
    ]

    queryset = (
        Usuario.objects
        .select_related(
            "sede",
            "carrera",
            "carrera__facultad",
        )
        .filter(
            is_active=True,
            rol__in=academic_roles,
        )
        .annotate(
            _search_full_name=Concat(
                "nombres",
                Value(" "),
                "apellidos",
                output_field=CharField(),
            )
        )
    )

    numeric_value = _positive_integer(query)

    if numeric_value is not None:
        queryset = queryset.filter(
            Q(pk=numeric_value)
            | _user_term_query(query)
        )
    else:
        queryset = _apply_terms(
            queryset,
            _query_terms(query),
            _user_term_query,
        )

    queryset = (
        queryset
        .annotate(
            _search_priority=Case(
                When(
                    email__iexact=query,
                    then=Value(0),
                ),
                When(
                    identificacion__iexact=query,
                    then=Value(0),
                ),
                When(
                    _search_full_name__iexact=query,
                    then=Value(1),
                ),
                When(
                    nombres__iexact=query,
                    then=Value(1),
                ),
                When(
                    apellidos__iexact=query,
                    then=Value(1),
                ),
                When(
                    email__istartswith=query,
                    then=Value(2),
                ),
                When(
                    identificacion__istartswith=query,
                    then=Value(2),
                ),
                When(
                    _search_full_name__istartswith=query,
                    then=Value(3),
                ),
                When(
                    nombres__istartswith=query,
                    then=Value(3),
                ),
                When(
                    apellidos__istartswith=query,
                    then=Value(3),
                ),
                default=Value(4),
                output_field=IntegerField(),
            )
        )
        .distinct()
        .order_by(
            "_search_priority",
            "apellidos",
            "nombres",
            "pk",
        )
    )

    return queryset[:normalized_limit]


# ============================================================
# PROYECTOS
# ============================================================

def buscar_proyectos(
    q,
    *,
    limit=SEARCH_LIMIT,
):
    """
    Busca proyectos por nombre, descripción, sede, carrera, facultad
    o responsable de creación.
    """
    query = _normalize_query(q)
    normalized_limit = _normalize_limit(limit)

    if not query:
        return Proyecto.objects.none()

    queryset = (
        Proyecto.objects
        .select_related(
            "sede",
            "carrera",
            "carrera__facultad",
            "creado_por",
        )
    )

    numeric_value = _positive_integer(query)

    if numeric_value is not None:
        queryset = queryset.filter(
            Q(pk=numeric_value)
            | _project_term_query(query)
        )
    else:
        queryset = _apply_terms(
            queryset,
            _query_terms(query),
            _project_term_query,
        )

    queryset = (
        queryset
        .annotate(
            _search_priority=Case(
                When(
                    nombre__iexact=query,
                    then=Value(0),
                ),
                When(
                    nombre__istartswith=query,
                    then=Value(1),
                ),
                When(
                    carrera__nombre__iexact=query,
                    then=Value(2),
                ),
                When(
                    carrera__facultad__nombre__iexact=query,
                    then=Value(2),
                ),
                default=Value(3),
                output_field=IntegerField(),
            )
        )
        .distinct()
        .order_by(
            "_search_priority",
            "nombre",
            "pk",
        )
    )

    return queryset[:normalized_limit]


# ============================================================
# PUBLICACIONES
# ============================================================

def buscar_publicaciones(
    q,
    *,
    limit=SEARCH_LIMIT,
    solo_con_pdf=False,
):
    """
    Busca publicaciones clasificadas.

    La búsqueda incluye:

    - Título general y título específico del subtipo.
    - DOI, ISSN e ISBN.
    - Revista, evento, editorial y libro contenedor.
    - Sede, proyecto, carrera, facultad, área y subárea.
    - Autores científicos vinculados mediante PublicacionAutor.

    Permite restringir los resultados a publicaciones que
    contengan un PDF principal.
    """
    query = _normalize_query(q)
    normalized_limit = _normalize_limit(limit)

    if not query:
        return Publicacion.objects.none()

    queryset = (
        Publicacion.objects
        .select_related(
            "tipo",
            "usuario_creador",
            "sede",
            "proyecto",
            "proyecto__sede",
            "carrera",
            "carrera__facultad",
            "area",
            "subarea",
            "articulo",
            "ponencia",
            "libro",
            "capitulo_libro",
        )
        .filter(
            estado=Publicacion.ESTADO_APROBADA
        )
        .prefetch_related(
            Prefetch(
                "participaciones",
                queryset=(
                    _publication_participations_queryset()
                ),
                to_attr=(
                    "_busqueda_participaciones"
                ),
            )
        )
    )

    numeric_value = _positive_integer(query)

    if numeric_value is not None:
        queryset = queryset.filter(
            Q(pk=numeric_value)
            | Q(numero=numeric_value)
            | Q(anio_publicacion=numeric_value)
            | _publication_term_query(query)
        )
    else:
        queryset = _apply_terms(
            queryset,
            _query_terms(query),
            _publication_term_query,
        )

    queryset = (
        annotate_tipo_publicacion_final(queryset)
        .exclude(
            tipo_publicacion_final=(
                "sin_clasificar"
            )
        )
        .annotate(
            _search_priority=Case(
                # Coincidencias exactas de identidad académica
                When(
                    articulo__codigo_doi__iexact=query,
                    then=Value(0),
                ),
                When(
                    articulo__nombre_articulo__iexact=query,
                    then=Value(0),
                ),
                When(
                    ponencia__nombre_ponencia__iexact=query,
                    then=Value(0),
                ),
                When(
                    libro__nombre_libro__iexact=query,
                    then=Value(0),
                ),
                When(
                    capitulo_libro__nombre_capitulo__iexact=query,
                    then=Value(0),
                ),

                # Coincidencias por prefijo de título
                When(
                    articulo__nombre_articulo__istartswith=query,
                    then=Value(1),
                ),
                When(
                    ponencia__nombre_ponencia__istartswith=query,
                    then=Value(1),
                ),
                When(
                    libro__nombre_libro__istartswith=query,
                    then=Value(1),
                ),
                When(
                    capitulo_libro__nombre_capitulo__istartswith=query,
                    then=Value(1),
                ),

                # Tipo y medio de publicación
                When(
                    tipo__codigo__iexact=query,
                    then=Value(2),
                ),
                When(
                    tipo__nombre__iexact=query,
                    then=Value(2),
                ),
                When(
                    articulo__nombre_revista__iexact=query,
                    then=Value(2),
                ),
                When(
                    ponencia__nombre_evento__iexact=query,
                    then=Value(2),
                ),

                # Proyecto y demás coincidencias
                When(
                    proyecto__nombre__iexact=query,
                    then=Value(3),
                ),
                default=Value(4),
                output_field=IntegerField(),
            )
        )
    )

    if solo_con_pdf:
        queryset = (
            queryset
            .exclude(
                archivo_pdf__isnull=True
            )
            .exclude(
                archivo_pdf=""
            )
        )

    queryset = (
        queryset
        .distinct()
        .order_by(
            "_search_priority",
            F("anio_publicacion").desc(
                nulls_last=True
            ),
            F("mes_publicacion").desc(
                nulls_last=True
            ),
            "-pk",
        )
    )

    return queryset[:normalized_limit]


# ============================================================
# AUTORES
# ============================================================

def buscar_autores(
    q,
    *,
    limit=SEARCH_LIMIT,
):
    """
    Busca autores por datos propios, Usuario vinculado o
    publicaciones relacionadas.

    Incluye autores externos pendientes porque pueden estar
    registrados como autores de publicaciones aunque todavía no
    tengan una cuenta activa.
    """
    query = _normalize_query(q)
    normalized_limit = _normalize_limit(limit)

    if not query:
        return Autor.objects.none()

    queryset = (
        Autor.objects
        .select_related(
            "usuario",
            "usuario__sede",
            "usuario__carrera",
            "usuario__carrera__facultad",
        )
        .annotate(
            _search_full_name=Concat(
                "nombres",
                Value(" "),
                "apellidos",
                output_field=CharField(),
            ),
            _linked_full_name=Concat(
                "usuario__nombres",
                Value(" "),
                "usuario__apellidos",
                output_field=CharField(),
            ),
        )
    )

    numeric_value = _positive_integer(query)

    if numeric_value is not None:
        queryset = queryset.filter(
            Q(pk=numeric_value)
            | Q(usuario_id=numeric_value)
            | _author_term_query(query)
        )
    else:
        queryset = _apply_terms(
            queryset,
            _query_terms(query),
            _author_term_query,
        )

    queryset = (
        queryset
        .annotate(
            _search_priority=Case(
                When(
                    orcid__iexact=query,
                    then=Value(0),
                ),
                When(
                    registro_senescyt__iexact=query,
                    then=Value(0),
                ),
                When(
                    scopus_id__iexact=query,
                    then=Value(0),
                ),
                When(
                    identificacion__iexact=query,
                    then=Value(0),
                ),
                When(
                    correo__iexact=query,
                    then=Value(0),
                ),
                When(
                    usuario__identificacion__iexact=query,
                    then=Value(0),
                ),
                When(
                    usuario__email__iexact=query,
                    then=Value(0),
                ),
                When(
                    _search_full_name__iexact=query,
                    then=Value(1),
                ),
                When(
                    _linked_full_name__iexact=query,
                    then=Value(1),
                ),
                When(
                    nombres__iexact=query,
                    then=Value(1),
                ),
                When(
                    apellidos__iexact=query,
                    then=Value(1),
                ),
                When(
                    _search_full_name__istartswith=query,
                    then=Value(2),
                ),
                When(
                    nombres__istartswith=query,
                    then=Value(2),
                ),
                When(
                    apellidos__istartswith=query,
                    then=Value(2),
                ),
                default=Value(3),
                output_field=IntegerField(),
            )
        )
        .distinct()
        .order_by(
            "_search_priority",
            "apellidos",
            "nombres",
            "pk",
        )
    )

    return queryset[:normalized_limit]