"""
Selectores para la búsqueda académica general.

Este módulo centraliza las consultas de:

- Investigadores y usuarios académicos.
- Autores.
- Proyectos.
- Publicaciones.

Los selectores:

- Normalizan los términos de búsqueda.
- Limitan defensivamente la cantidad de resultados.
- Priorizan coincidencias exactas y por prefijo.
- Evitan exponer usuarios inactivos.
- Derivan la facultad desde carrera.facultad.
- Excluyen publicaciones sin clasificación válida.
"""

import unicodedata

from django.db.models import (
    Case,
    F,
    IntegerField,
    Q,
    Value,
    When,
)

from core.models import (
    Autor,
    Proyecto,
    Publicacion,
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
    query = _normalize_query(
        q
    )

    normalized_limit = _normalize_limit(
        limit
    )

    if not query:
        return Usuario.objects.none()

    academic_roles = [
        Usuario.Rol.AUTOR,
        Usuario.Rol.AUTOR_EXTERNO,
    ]

    queryset = (
        Usuario.objects
        .select_related(
            "carrera",
            "carrera__facultad",
        )
        .filter(
            is_active=True,
            rol__in=academic_roles,
        )
        .filter(
            Q(
                nombres__icontains=query
            )
            | Q(
                apellidos__icontains=query
            )
            | Q(
                email__icontains=query
            )
            | Q(
                identificacion__icontains=query
            )
            | Q(
                carrera__nombre__icontains=query
            )
            | Q(
                carrera__facultad__nombre__icontains=query
            )
        )
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

    return queryset[
        :normalized_limit
    ]


# ============================================================
# PROYECTOS
# ============================================================

def buscar_proyectos(
    q,
    *,
    limit=SEARCH_LIMIT,
):
    """
    Busca proyectos por nombre, descripción, carrera o facultad.
    """
    query = _normalize_query(
        q
    )

    normalized_limit = _normalize_limit(
        limit
    )

    if not query:
        return Proyecto.objects.none()

    queryset = (
        Proyecto.objects
        .select_related(
            "carrera",
            "carrera__facultad",
            "creado_por",
        )
        .filter(
            Q(
                nombre__icontains=query
            )
            | Q(
                descripcion__icontains=query
            )
            | Q(
                carrera__nombre__icontains=query
            )
            | Q(
                carrera__facultad__nombre__icontains=query
            )
        )
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

    return queryset[
        :normalized_limit
    ]


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

    Permite restringir los resultados a publicaciones que
    contengan un PDF principal.
    """
    query = _normalize_query(
        q
    )

    normalized_limit = _normalize_limit(
        limit
    )

    if not query:
        return Publicacion.objects.none()

    queryset = (
        Publicacion.objects
        .select_related(
            "tipo",
            "usuario_creador",
            "proyecto",
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
            Q(
                titulo__icontains=query
            )
            | Q(
                tipo__nombre__icontains=query
            )
            | Q(
                tipo__codigo__icontains=query
            )
            | Q(
                proyecto__nombre__icontains=query
            )
            | Q(
                usuario_creador__nombres__icontains=query
            )
            | Q(
                usuario_creador__apellidos__icontains=query
            )
            | Q(
                usuario_creador__email__icontains=query
            )
            | Q(
                carrera__facultad__nombre__icontains=query
            )
            | Q(
                carrera__nombre__icontains=query
            )
            | Q(
                area__nombre__icontains=query
            )
            | Q(
                subarea__nombre__icontains=query
            )
        )
        .distinct()
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
        .annotate(
            _search_priority=Case(
                When(
                    titulo__iexact=query,
                    then=Value(0),
                ),
                When(
                    titulo__istartswith=query,
                    then=Value(1),
                ),
                When(
                    tipo__codigo__iexact=query,
                    then=Value(2),
                ),
                When(
                    tipo__nombre__iexact=query,
                    then=Value(2),
                ),
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

    queryset = queryset.order_by(
        "_search_priority",
        F(
            "fecha_publicacion"
        ).desc(
            nulls_last=True
        ),
        "-pk",
    )

    return queryset[
        :normalized_limit
    ]


# ============================================================
# AUTORES
# ============================================================

def buscar_autores(
    q,
    *,
    limit=SEARCH_LIMIT,
):
    """
    Busca autores por datos propios o por el usuario vinculado.

    Incluye autores externos pendientes porque pueden estar
    registrados como coautores aunque todavía no tengan una
    cuenta activa.
    """
    query = _normalize_query(
        q
    )

    normalized_limit = _normalize_limit(
        limit
    )

    if not query:
        return Autor.objects.none()

    queryset = (
        Autor.objects
        .select_related(
            "usuario",
        )
        .filter(
            Q(
                nombres__icontains=query
            )
            | Q(
                apellidos__icontains=query
            )
            | Q(
                correo__icontains=query
            )
            | Q(
                identificacion__icontains=query
            )
            | Q(
                institucion__icontains=query
            )
            | Q(
                usuario__nombres__icontains=query
            )
            | Q(
                usuario__apellidos__icontains=query
            )
            | Q(
                usuario__email__icontains=query
            )
            | Q(
                usuario__identificacion__icontains=query
            )
        )
        .annotate(
            _search_priority=Case(
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
                    nombres__iexact=query,
                    then=Value(1),
                ),
                When(
                    apellidos__iexact=query,
                    then=Value(1),
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

    return queryset[
        :normalized_limit
    ]