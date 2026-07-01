"""
Selectors reutilizables para catálogos y selects del sistema.
Centraliza la lógica de consultas ligeras usadas por APIViews y ViewSet.
"""

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q

from core.models import (
    Facultad,
    Carrera,
    Proyecto,
    Pais,
    Ciudad,
    AreaConocimiento,
    Subarea,
    Autor,
)


ESTADOS_PROYECTO_ACTIVOS = {"nuevo", "arrastre"}


def _model_has_field(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


def _existing_value_fields(model, base_fields, optional_fields=None):
    optional_fields = optional_fields or []
    fields = list(base_fields)

    for field_name in optional_fields:
        if _model_has_field(model, field_name):
            fields.append(field_name)

    return fields


def _safe_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _norm_text(value):
    return str(value or "").strip()


def _is_admin_user(user):
    if not user or not getattr(user, "is_authenticated", False):
        return False

    rol = _norm_text(getattr(user, "rol", "")).lower()

    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_staff", False)
        or getattr(user, "es_admin", False)
        or rol in {"admin", "administrador"}
    )


def build_facultades_select_data():
    return list(
        Facultad.objects.values(
            "id",
            "nombre",
        ).order_by("nombre", "id")
    )


def build_carreras_select_data(*, facultad_id=None):
    qs = Carrera.objects.select_related("facultad").all()

    if facultad_id is not None:
        qs = qs.filter(facultad_id=facultad_id)

    data = []

    for carrera in qs.order_by("nombre", "id"):
        facultad = carrera.facultad

        data.append(
            {
                "id": carrera.id,
                "nombre": carrera.nombre,
                "label": carrera.nombre,
                "facultad_id": carrera.facultad_id,
                "facultad": facultad.nombre if facultad else "",
                "facultad_nombre": facultad.nombre if facultad else "",
            }
        )

    return data


def build_proyectos_select_data(
    *,
    carrera_id=None,
    include_id=None,
    q="",
    incluir_cerrados=False,
):
    """
    Devuelve proyectos para el select dependiente de carrera.

    Reglas:
    - Proyecto se filtra por carrera_id.
    - Proyecto.estado NO es booleano.
    - Estados activos: nuevo / arrastre.
    - Si incluir_cerrados=True, también devuelve cierre.
    - include_id permite mantener visible un proyecto ya seleccionado aunque esté cerrado.
    """

    qs = (
        Proyecto.objects
        .select_related("carrera", "carrera__facultad")
        .all()
    )

    if carrera_id is not None:
        qs = qs.filter(carrera_id=carrera_id)

    q = _norm_text(q)

    if q:
        qs = qs.filter(
            Q(nombre__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(carrera__nombre__icontains=q)
            | Q(carrera__facultad__nombre__icontains=q)
        )

    base_qs = qs

    if not incluir_cerrados:
        qs = qs.filter(estado__in=ESTADOS_PROYECTO_ACTIVOS)

    proyectos = list(qs.distinct().order_by("nombre", "id"))

    include_id = _safe_int(include_id)

    if include_id and include_id > 0:
        already_included = any(proyecto.id == include_id for proyecto in proyectos)

        if not already_included:
            extra = (
                base_qs
                .filter(id=include_id)
                .select_related("carrera", "carrera__facultad")
                .first()
            )

            if extra is not None:
                proyectos.append(extra)
                proyectos.sort(
                    key=lambda item: (
                        _norm_text(item.nombre).lower(),
                        item.id or 0,
                    )
                )

    data = []

    for proyecto in proyectos:
        carrera = proyecto.carrera
        facultad = carrera.facultad if carrera else None

        data.append(
            {
                "id": proyecto.id,
                "nombre": proyecto.nombre,
                "label": proyecto.nombre,
                "descripcion": proyecto.descripcion or "",
                "estado": proyecto.estado,
                "estado_label": proyecto.get_estado_display(),
                "es_activo": proyecto.estado in ESTADOS_PROYECTO_ACTIVOS,
                "carrera_id": proyecto.carrera_id,
                "carrera": carrera.nombre if carrera else "",
                "carrera_nombre": carrera.nombre if carrera else "",
                "facultad_id": facultad.id if facultad else None,
                "facultad": facultad.nombre if facultad else "",
                "facultad_nombre": facultad.nombre if facultad else "",
                "anio_inicio": proyecto.anio_inicio,
                "anio_fin": proyecto.anio_fin,
                "fecha_inicio": proyecto.fecha_inicio,
                "fecha_fin_planificada": proyecto.fecha_fin_planificada,
                "fecha_fin_prorrogada": proyecto.fecha_fin_prorrogada,
                "fecha_cierre": proyecto.fecha_cierre,
            }
        )

    return data


def build_paises_select_data():
    fields = _existing_value_fields(
        Pais,
        base_fields=["id", "nombre"],
        optional_fields=["iso2", "iso3"],
    )

    return list(
        Pais.objects.values(*fields).order_by("nombre", "id")
    )


def build_ciudades_select_data(*, pais_id=None):
    qs = Ciudad.objects.all()

    if pais_id is not None:
        qs = qs.filter(pais_id=pais_id)

    fields = _existing_value_fields(
        Ciudad,
        base_fields=["id", "nombre", "pais_id"],
        optional_fields=["admin1", "geoname_id"],
    )

    return list(
        qs.values(*fields).order_by("nombre", "id")
    )


def build_areas_select_data():
    return list(
        AreaConocimiento.objects.values(
            "id",
            "nombre",
        ).order_by("nombre", "id")
    )


def build_subareas_select_data(*, area_id=None):
    qs = Subarea.objects.all()

    if area_id is not None:
        qs = qs.filter(area_id=area_id)

    return list(
        qs.values(
            "id",
            "nombre",
        ).order_by("nombre", "id")
    )


def build_autores_select_data(*, q=""):
    autores = (
        Autor.objects
        .select_related("usuario")
        .all()
        .order_by("apellidos", "nombres", "id")
    )

    q = _norm_text(q)

    if q:
        autores = autores.filter(
            Q(nombres__icontains=q)
            | Q(apellidos__icontains=q)
            | Q(identificacion__icontains=q)
            | Q(correo__icontains=q)
            | Q(institucion__icontains=q)
            | Q(usuario__email__icontains=q)
        ).distinct()

    data = []

    for autor in autores[:100]:
        correo = autor.correo

        if autor.usuario and autor.usuario.email:
            correo = correo or autor.usuario.email

        nombres = _norm_text(autor.nombres)
        apellidos = _norm_text(autor.apellidos)
        nombre_completo = f"{nombres} {apellidos}".strip()

        data.append(
            {
                "id": autor.id,
                "nombres": nombres,
                "apellidos": apellidos,
                "identificacion": autor.identificacion,
                "correo": correo,
                "institucion": autor.institucion,
                "es_externo": autor.es_externo,
                "usuario_id": autor.usuario.id if autor.usuario else None,
                "nombre": nombre_completo,
                "nombre_completo": nombre_completo,
                "label": nombre_completo,
                "es_admin": (
                    bool(
                        getattr(autor.usuario, "is_staff", False)
                        or getattr(autor.usuario, "is_superuser", False)
                    )
                    if autor.usuario
                    else False
                ),
            }
        )

    return data