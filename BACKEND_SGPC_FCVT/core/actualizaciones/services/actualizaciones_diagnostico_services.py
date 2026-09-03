"""Diagnóstico de información pendiente para campañas de actualización."""

import re

from django.core.exceptions import ObjectDoesNotExist

from core.models import Proyecto, Publicacion


CEDULA_PATTERN = re.compile(r"^\d{10}$")


def publicacion_es_elegible_para_actualizacion(publicacion):
    """Indica si una publicación puede entrar en una campaña de actualización.

    Las campañas de actualización de publicaciones se reservan para registros
    ya aprobados. Borradores, publicaciones en revisión, observadas o rechazadas
    deben corregirse mediante su flujo normal en ``Mis publicaciones``.
    """
    return bool(
        publicacion
        and getattr(publicacion, "estado", None) == Publicacion.ESTADO_APROBADA
    )


def _is_institutional_user(user):
    return bool(
        user
        and str(getattr(user, "rol", "") or "").strip().lower() == "autor"
        and str(getattr(user, "auth_source", "") or "").strip().lower()
        == "microsoft"
    )


def _field_is_empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def diagnosticar_perfil(usuario, campos_habilitados=None):
    """Devuelve los campos de perfil que requieren intervención del usuario."""
    enabled = set(campos_habilitados or {"identificacion", "sede", "carrera"})

    # Las cuentas externas no requieren clasificación académica ULEAM.
    if not _is_institutional_user(usuario):
        return {
            "campos_pendientes": [],
            "resumen": {
                "tipo_cuenta": "externa_o_no_institucional",
                "completo": True,
            },
        }

    pending = []

    if "identificacion" in enabled:
        identification = str(getattr(usuario, "identificacion", "") or "").strip()
        if not CEDULA_PATTERN.fullmatch(identification):
            pending.append("identificacion")

    if "sede" in enabled and not getattr(usuario, "sede_id", None):
        pending.append("sede")

    if "carrera" in enabled and not getattr(usuario, "carrera_id", None):
        pending.append("carrera")

    if getattr(usuario, "sede_id", None) and getattr(usuario, "carrera_id", None):
        relation_exists = (
            usuario.carrera.sedes_carrera.filter(
                sede_id=usuario.sede_id,
                activa=True,
            ).exists()
        )
        if not relation_exists:
            # La carrera es el dato que debe volver a confirmarse según la sede.
            if "carrera" in enabled and "carrera" not in pending:
                pending.append("carrera")
            elif "sede" in enabled and "sede" not in pending:
                pending.append("sede")

    return {
        "campos_pendientes": pending,
        "resumen": {
            "tipo_cuenta": "institucional",
            "completo": not pending,
        },
    }


def _publicacion_tipo_codigo(publicacion):
    tipo = getattr(publicacion, "tipo", None)
    return str(getattr(tipo, "codigo", "") or "").strip().lower()


def _safe_related(instance, relation_name):
    try:
        return getattr(instance, relation_name, None)
    except (AttributeError, ObjectDoesNotExist):
        return None


def _publicacion_titulo(publicacion):
    """Devuelve un título humano para identificar la publicación."""
    candidates = (
        (_safe_related(publicacion, "articulo"), "nombre_articulo"),
        (_safe_related(publicacion, "ponencia"), "nombre_ponencia"),
        (_safe_related(publicacion, "libro"), "nombre_libro"),
        (_safe_related(publicacion, "capitulo_libro"), "nombre_capitulo"),
    )

    for related, attr_name in candidates:
        value = str(getattr(related, attr_name, "") or "").strip()
        if value:
            return value

    return "Publicación sin título"


def _publicacion_record_summary(publicacion, pending):
    tipo = getattr(publicacion, "tipo", None)

    return {
        "id": publicacion.pk,
        "titulo": _publicacion_titulo(publicacion),
        "tipo": str(getattr(tipo, "nombre", "") or "").strip(),
        "anio": getattr(publicacion, "anio_publicacion", None),
        "estado": getattr(publicacion, "estado", None),
        "campos": pending,
    }


def _publicacion_missing_fields(publicacion, enabled):
    pending = []

    simple_fields = {
        "sede": "sede_id",
        "carrera": "carrera_id",
        "area": "area_id",
        "subarea": "subarea_id",
        "proyecto": "proyecto_id",
    }

    # País y ciudad se usan en la actualización de Ponencia. Para el resto de
    # tipos el serializer histórico los limpia, por lo que no deben marcarse
    # como faltantes imposibles de completar.
    if _publicacion_tipo_codigo(publicacion) == "ponencia":
        simple_fields.update(
            {
                "pais": "pais_id",
                "ciudad": "ciudad_id",
            }
        )

    for logical_name, attr_name in simple_fields.items():
        if logical_name in enabled and _field_is_empty(
            getattr(publicacion, attr_name, None)
        ):
            pending.append(logical_name)

    if getattr(publicacion, "sede_id", None) and getattr(publicacion, "carrera_id", None):
        relation_exists = (
            publicacion.carrera.sedes_carrera.filter(
                sede_id=publicacion.sede_id,
                activa=True,
            ).exists()
        )
        if not relation_exists:
            if "carrera" in enabled and "carrera" not in pending:
                pending.append("carrera")
            elif "sede" in enabled and "sede" not in pending:
                pending.append("sede")

    if (
        getattr(publicacion, "subarea_id", None)
        and getattr(publicacion, "area_id", None)
        and getattr(publicacion.subarea, "area_id", None) != publicacion.area_id
    ):
        if "subarea" in enabled and "subarea" not in pending:
            pending.append("subarea")

    if (
        _publicacion_tipo_codigo(publicacion) == "ponencia"
        and getattr(publicacion, "ciudad_id", None)
        and getattr(publicacion, "pais_id", None)
        and getattr(publicacion.ciudad, "pais_id", None) != publicacion.pais_id
    ):
        if "ciudad" in enabled and "ciudad" not in pending:
            pending.append("ciudad")

    return pending


def diagnosticar_publicacion(publicacion, campos_habilitados=None):
    """Diagnóstico de una publicación aprobada dentro de una campaña."""
    eligible = publicacion_es_elegible_para_actualizacion(publicacion)
    if not eligible:
        return {
            "campos_pendientes": [],
            "resumen": {
                "id": getattr(publicacion, "pk", None),
                "estado": getattr(publicacion, "estado", None),
                "elegible": False,
                "completo": True,
            },
        }

    enabled = set(campos_habilitados or [])
    pending = _publicacion_missing_fields(publicacion, enabled)
    return {
        "campos_pendientes": pending,
        "resumen": {
            "id": getattr(publicacion, "pk", None),
            "estado": getattr(publicacion, "estado", None),
            "elegible": True,
            "completo": not pending,
        },
    }


def diagnosticar_publicaciones(usuario, campos_habilitados=None):
    enabled = set(campos_habilitados or [])
    # Regla de negocio: Información pendiente solo trabaja con producción
    # científica ya aprobada. Los demás estados pertenecen al flujo normal de
    # revisión/corrección de publicaciones.
    queryset = (
        Publicacion.objects.filter(
            usuario_creador=usuario,
            estado=Publicacion.ESTADO_APROBADA,
        )
        .select_related(
            "tipo",
            "sede",
            "carrera",
            "area",
            "subarea",
            "pais",
            "ciudad",
            "proyecto",
            "articulo",
            "ponencia",
            "libro",
            "capitulo_libro",
        )
        .order_by("id")
    )

    records = []
    union_fields = []

    for publication in queryset.iterator():
        pending = _publicacion_missing_fields(publication, enabled)
        if not pending:
            continue
        records.append(
            _publicacion_record_summary(
                publication,
                pending,
            )
        )
        for field in pending:
            if field not in union_fields:
                union_fields.append(field)

    return {
        "campos_pendientes": union_fields,
        "resumen": {
            "total": queryset.count(),
            "total_aprobadas": queryset.count(),
            "total_incompletas": len(records),
            "solo_publicaciones_aprobadas": True,
            "estado_incluido": Publicacion.ESTADO_APROBADA,
            "registros": records,
        },
    }


def _proyecto_missing_fields(project, enabled):
    pending = []
    attr_map = {
        "sede": "sede_id",
        "carrera": "carrera_id",
        "descripcion": "descripcion",
        "fecha_inicio": "fecha_inicio",
        "fecha_fin_planificada": "fecha_fin_planificada",
        "fecha_fin_prorrogada": "fecha_fin_prorrogada",
    }

    for logical_name, attr_name in attr_map.items():
        if logical_name in enabled and _field_is_empty(getattr(project, attr_name, None)):
            pending.append(logical_name)

    if getattr(project, "sede_id", None) and getattr(project, "carrera_id", None):
        relation_exists = (
            project.carrera.sedes_carrera.filter(
                sede_id=project.sede_id,
                activa=True,
            ).exists()
        )
        if not relation_exists:
            if "carrera" in enabled and "carrera" not in pending:
                pending.append("carrera")
            elif "sede" in enabled and "sede" not in pending:
                pending.append("sede")

    return pending


def diagnosticar_proyecto(proyecto, campos_habilitados=None):
    """Diagnóstico de un registro concreto de proyecto."""
    enabled = set(campos_habilitados or [])
    pending = _proyecto_missing_fields(proyecto, enabled)
    return {
        "campos_pendientes": pending,
        "resumen": {
            "id": getattr(proyecto, "pk", None),
            "completo": not pending,
        },
    }


def diagnosticar_proyectos(usuario, campos_habilitados=None):
    enabled = set(campos_habilitados or [])
    queryset = (
        Proyecto.objects.filter(participaciones__autor__usuario=usuario)
        .select_related("sede", "carrera")
        .distinct()
        .order_by("id")
    )

    records = []
    union_fields = []

    for project in queryset.iterator():
        pending = _proyecto_missing_fields(project, enabled)
        if not pending:
            continue
        records.append({"id": project.pk, "campos": pending})
        for field in pending:
            if field not in union_fields:
                union_fields.append(field)

    return {
        "campos_pendientes": union_fields,
        "resumen": {
            "total": queryset.count(),
            "total_incompletos": len(records),
            "registros": records,
        },
    }


def diagnosticar_usuario_para_campania(usuario, campania):
    if campania.tipo == campania.TIPO_PERFIL:
        return diagnosticar_perfil(usuario, campania.campos_habilitados)
    if campania.tipo == campania.TIPO_PUBLICACION:
        return diagnosticar_publicaciones(usuario, campania.campos_habilitados)
    if campania.tipo == campania.TIPO_PROYECTO:
        return diagnosticar_proyectos(usuario, campania.campos_habilitados)
    return {"campos_pendientes": [], "resumen": {}}
