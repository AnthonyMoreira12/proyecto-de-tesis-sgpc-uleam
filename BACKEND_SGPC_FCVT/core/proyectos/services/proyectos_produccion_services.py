"""Analítica de producción científica asociada a proyectos."""

from django.db.models import Count, Q
from rest_framework.exceptions import ValidationError

from core.models import Proyecto, Publicacion, PublicacionAutor


ESTADOS_PUBLICACION = {value for value, _label in Publicacion.ESTADOS}


def _positive_int(value, *, field_name):
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        raise ValidationError({field_name: ["Debe indicar un identificador numérico válido."]})
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError({field_name: ["Debe indicar un identificador numérico válido."]}) from exc
    if parsed < 1:
        raise ValidationError({field_name: ["El identificador debe ser mayor o igual a 1."]})
    return parsed


def _year(value):
    if value in (None, ""):
        return None
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError({"anio": ["El año debe ser numérico."]}) from exc
    if not 1900 <= parsed <= 2100:
        raise ValidationError({"anio": ["El año debe estar entre 1900 y 2100."]})
    return parsed


def _state(value):
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    if normalized not in ESTADOS_PUBLICACION:
        raise ValidationError({"estado": ["El estado de publicación indicado no es válido."]})
    return normalized


def _apply_filters(queryset, *, estado=None, anio=None, tipo_id=None):
    normalized_state = _state(estado)
    normalized_year = _year(anio)
    normalized_type_id = _positive_int(tipo_id, field_name="tipo")

    if normalized_state:
        queryset = queryset.filter(estado=normalized_state)
    if normalized_year is not None:
        queryset = queryset.filter(anio_publicacion=normalized_year)
    if normalized_type_id is not None:
        queryset = queryset.filter(tipo_id=normalized_type_id)

    return queryset, {
        "estado": normalized_state,
        "anio": normalized_year,
        "tipo": normalized_type_id,
    }


def _project_payload(proyecto):
    career = getattr(proyecto, "carrera", None)
    faculty = getattr(career, "facultad", None)
    site = getattr(proyecto, "sede", None)
    return {
        "id": proyecto.pk,
        "nombre": proyecto.nombre,
        "estado": proyecto.estado,
        "estado_label": proyecto.get_estado_display(),
        "sede": {"id": site.pk, "nombre": site.nombre} if site is not None else None,
        "carrera": {"id": career.pk, "nombre": career.nombre} if career is not None else None,
        "facultad": {"id": faculty.pk, "nombre": faculty.nombre} if faculty is not None else None,
        "anio_inicio": proyecto.anio_inicio,
        "anio_fin": proyecto.anio_fin,
    }


def _summary_payload(queryset):
    totals = queryset.aggregate(
        total=Count("id"),
        borrador=Count("id", filter=Q(estado=Publicacion.ESTADO_BORRADOR)),
        en_revision=Count("id", filter=Q(estado=Publicacion.ESTADO_EN_REVISION)),
        observada=Count("id", filter=Q(estado=Publicacion.ESTADO_OBSERVADA)),
        aprobada=Count("id", filter=Q(estado=Publicacion.ESTADO_APROBADA)),
        rechazada=Count("id", filter=Q(estado=Publicacion.ESTADO_RECHAZADA)),
        con_pdf=Count("id", filter=Q(archivo_pdf__isnull=False) & ~Q(archivo_pdf="")),
    )
    total = int(totals.get("total") or 0)
    approved = int(totals.get("aprobada") or 0)
    with_pdf = int(totals.get("con_pdf") or 0)
    pending_review = int(totals.get("en_revision") or 0) + int(totals.get("observada") or 0)
    return {
        "total_publicaciones": total,
        "borrador": int(totals.get("borrador") or 0),
        "en_revision": int(totals.get("en_revision") or 0),
        "observada": int(totals.get("observada") or 0),
        "aprobada": approved,
        "rechazada": int(totals.get("rechazada") or 0),
        "pendientes_revision": pending_review,
        "con_pdf": with_pdf,
        "sin_pdf": max(total - with_pdf, 0),
        "tasa_aprobacion": round((approved / total) * 100, 2) if total else 0.0,
        "cobertura_pdf": round((with_pdf / total) * 100, 2) if total else 0.0,
    }


def _types_payload(queryset):
    rows = (
        queryset.values("tipo_id", "tipo__codigo", "tipo__nombre", "tipo__categoria")
        .annotate(
            total=Count("id"),
            aprobadas=Count("id", filter=Q(estado=Publicacion.ESTADO_APROBADA)),
        )
        .order_by("-total", "tipo__nombre", "tipo_id")
    )
    return [
        {
            "tipo_id": row["tipo_id"],
            "codigo": row["tipo__codigo"],
            "nombre": row["tipo__nombre"],
            "categoria": row["tipo__categoria"],
            "total": int(row["total"] or 0),
            "aprobadas": int(row["aprobadas"] or 0),
        }
        for row in rows
    ]


def _years_payload(queryset):
    rows = (
        queryset.exclude(anio_publicacion__isnull=True)
        .values("anio_publicacion")
        .annotate(
            total=Count("id"),
            aprobadas=Count("id", filter=Q(estado=Publicacion.ESTADO_APROBADA)),
            observadas=Count("id", filter=Q(estado=Publicacion.ESTADO_OBSERVADA)),
            rechazadas=Count("id", filter=Q(estado=Publicacion.ESTADO_RECHAZADA)),
        )
        .order_by("anio_publicacion")
    )
    return [
        {
            "anio": row["anio_publicacion"],
            "total": int(row["total"] or 0),
            "aprobadas": int(row["aprobadas"] or 0),
            "observadas": int(row["observadas"] or 0),
            "rechazadas": int(row["rechazadas"] or 0),
        }
        for row in rows
    ]


def _authors_payload(proyecto, *, estado=None, anio=None, tipo_id=None):
    queryset = PublicacionAutor.objects.filter(publicacion__proyecto_id=proyecto.pk)
    normalized_state = _state(estado)
    normalized_year = _year(anio)
    normalized_type_id = _positive_int(tipo_id, field_name="tipo")
    if normalized_state:
        queryset = queryset.filter(publicacion__estado=normalized_state)
    if normalized_year is not None:
        queryset = queryset.filter(publicacion__anio_publicacion=normalized_year)
    if normalized_type_id is not None:
        queryset = queryset.filter(publicacion__tipo_id=normalized_type_id)
    rows = (
        queryset.values(
            "autor_id",
            "autor__nombres",
            "autor__apellidos",
            "autor__correo",
            "autor__institucion",
            "autor__es_externo",
        )
        .annotate(
            total_publicaciones=Count("publicacion_id", distinct=True),
            aprobadas=Count(
                "publicacion_id",
                filter=Q(publicacion__estado=Publicacion.ESTADO_APROBADA),
                distinct=True,
            ),
        )
        .order_by("-total_publicaciones", "autor__apellidos", "autor__nombres", "autor_id")
    )
    return [
        {
            "autor_id": row["autor_id"],
            "nombres": row["autor__nombres"],
            "apellidos": row["autor__apellidos"],
            "nombre_completo": " ".join(
                part for part in (
                    str(row["autor__nombres"] or "").strip(),
                    str(row["autor__apellidos"] or "").strip(),
                ) if part
            ),
            "correo": row["autor__correo"],
            "institucion": row["autor__institucion"],
            "es_externo": bool(row["autor__es_externo"]),
            "total_publicaciones": int(row["total_publicaciones"] or 0),
            "aprobadas": int(row["aprobadas"] or 0),
        }
        for row in rows
    ]


def obtener_produccion_cientifica_proyecto(*, proyecto, estado=None, anio=None, tipo_id=None):
    queryset = (
        Publicacion.objects.select_related("tipo", "sede", "carrera", "carrera__facultad")
        .filter(proyecto_id=proyecto.pk)
    )
    queryset, filters = _apply_filters(
        queryset,
        estado=estado,
        anio=anio,
        tipo_id=tipo_id,
    )
    years = _years_payload(queryset)
    return {
        "proyecto": _project_payload(proyecto),
        "filtros": filters,
        "resumen": _summary_payload(queryset),
        "por_tipo": _types_payload(queryset),
        "por_anio": years,
        "autores_produccion": _authors_payload(
            proyecto,
            estado=estado,
            anio=anio,
            tipo_id=tipo_id,
        ),
        "periodo_produccion": {
            "primer_anio": years[0]["anio"] if years else None,
            "ultimo_anio": years[-1]["anio"] if years else None,
            "anios_con_produccion": len(years),
        },
    }

# ============================================================
# COMPARATIVA INSTITUCIONAL DE PROYECTOS
# ============================================================

ESTADOS_PROYECTO = {
    value
    for value, _label
    in Proyecto.ESTADOS
}

DEFAULT_RANKING_LIMIT = 10
MAX_RANKING_LIMIT = 100


def _project_state(value):
    normalized = str(value or "").strip().lower()

    if not normalized:
        return None

    if normalized not in ESTADOS_PROYECTO:
        raise ValidationError(
            {
                "estado_proyecto": [
                    "El estado de proyecto indicado no es válido."
                ]
            }
        )

    return normalized


def _ranking_limit(value):
    if value in (None, ""):
        return DEFAULT_RANKING_LIMIT

    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError(
            {
                "limite": [
                    "El límite del ranking debe ser numérico."
                ]
            }
        ) from exc

    if parsed < 1:
        raise ValidationError(
            {
                "limite": [
                    "El límite del ranking debe ser mayor o igual a 1."
                ]
            }
        )

    return min(parsed, MAX_RANKING_LIMIT)


def _publication_relation_filter(
    *,
    estado_publicacion=None,
    anio=None,
    tipo_id=None,
):
    publication_state = _state(estado_publicacion)
    publication_year = _year(anio)
    publication_type_id = _positive_int(
        tipo_id,
        field_name="tipo",
    )

    relation_filter = Q()

    if publication_state:
        relation_filter &= Q(
            publicaciones__estado=publication_state
        )

    if publication_year is not None:
        relation_filter &= Q(
            publicaciones__anio_publicacion=publication_year
        )

    if publication_type_id is not None:
        relation_filter &= Q(
            publicaciones__tipo_id=publication_type_id
        )

    return relation_filter, {
        "estado_publicacion": publication_state,
        "anio": publication_year,
        "tipo": publication_type_id,
    }


def _comparative_project_queryset(
    *,
    sede_id=None,
    carrera_id=None,
    facultad_id=None,
    estado_proyecto=None,
    estado_publicacion=None,
    anio=None,
    tipo_id=None,
):
    site_id = _positive_int(
        sede_id,
        field_name="sede",
    )
    career_id = _positive_int(
        carrera_id,
        field_name="carrera",
    )
    faculty_id = _positive_int(
        facultad_id,
        field_name="facultad",
    )
    project_state = _project_state(estado_proyecto)

    publication_filter, publication_filters = (
        _publication_relation_filter(
            estado_publicacion=estado_publicacion,
            anio=anio,
            tipo_id=tipo_id,
        )
    )

    queryset = (
        Proyecto.objects
        .select_related(
            "sede",
            "carrera",
            "carrera__facultad",
        )
        .all()
    )

    if site_id is not None:
        queryset = queryset.filter(sede_id=site_id)

    if career_id is not None:
        queryset = queryset.filter(carrera_id=career_id)

    if faculty_id is not None:
        queryset = queryset.filter(
            carrera__facultad_id=faculty_id
        )

    if project_state:
        queryset = queryset.filter(estado=project_state)

    queryset = queryset.annotate(
        total_publicaciones=Count(
            "publicaciones",
            filter=publication_filter,
            distinct=True,
        ),
        publicaciones_aprobadas=Count(
            "publicaciones",
            filter=(
                publication_filter
                & Q(
                    publicaciones__estado=(
                        Publicacion.ESTADO_APROBADA
                    )
                )
            ),
            distinct=True,
        ),
        publicaciones_en_revision=Count(
            "publicaciones",
            filter=(
                publication_filter
                & Q(
                    publicaciones__estado=(
                        Publicacion.ESTADO_EN_REVISION
                    )
                )
            ),
            distinct=True,
        ),
        publicaciones_observadas=Count(
            "publicaciones",
            filter=(
                publication_filter
                & Q(
                    publicaciones__estado=(
                        Publicacion.ESTADO_OBSERVADA
                    )
                )
            ),
            distinct=True,
        ),
        publicaciones_rechazadas=Count(
            "publicaciones",
            filter=(
                publication_filter
                & Q(
                    publicaciones__estado=(
                        Publicacion.ESTADO_RECHAZADA
                    )
                )
            ),
            distinct=True,
        ),
        publicaciones_borrador=Count(
            "publicaciones",
            filter=(
                publication_filter
                & Q(
                    publicaciones__estado=(
                        Publicacion.ESTADO_BORRADOR
                    )
                )
            ),
            distinct=True,
        ),
        publicaciones_con_pdf=Count(
            "publicaciones",
            filter=(
                publication_filter
                & Q(
                    publicaciones__archivo_pdf__isnull=False
                )
                & ~Q(
                    publicaciones__archivo_pdf=""
                )
            ),
            distinct=True,
        ),
    )

    return queryset, {
        "sede": site_id,
        "carrera": career_id,
        "facultad": faculty_id,
        "estado_proyecto": project_state,
        **publication_filters,
    }


def _comparative_project_row(project):
    total = int(
        getattr(project, "total_publicaciones", 0)
        or 0
    )
    approved = int(
        getattr(project, "publicaciones_aprobadas", 0)
        or 0
    )
    with_pdf = int(
        getattr(project, "publicaciones_con_pdf", 0)
        or 0
    )

    site = getattr(project, "sede", None)
    career = getattr(project, "carrera", None)
    faculty = getattr(career, "facultad", None)

    return {
        "proyecto_id": project.pk,
        "nombre": project.nombre,
        "estado": project.estado,
        "estado_label": project.get_estado_display(),
        "sede": (
            {"id": site.pk, "nombre": site.nombre}
            if site is not None
            else None
        ),
        "carrera": (
            {"id": career.pk, "nombre": career.nombre}
            if career is not None
            else None
        ),
        "facultad": (
            {"id": faculty.pk, "nombre": faculty.nombre}
            if faculty is not None
            else None
        ),
        "anio_inicio": project.anio_inicio,
        "anio_fin": project.anio_fin,
        "total_publicaciones": total,
        "aprobadas": approved,
        "en_revision": int(
            getattr(project, "publicaciones_en_revision", 0)
            or 0
        ),
        "observadas": int(
            getattr(project, "publicaciones_observadas", 0)
            or 0
        ),
        "rechazadas": int(
            getattr(project, "publicaciones_rechazadas", 0)
            or 0
        ),
        "borradores": int(
            getattr(project, "publicaciones_borrador", 0)
            or 0
        ),
        "con_pdf": with_pdf,
        "tasa_aprobacion": (
            round((approved / total) * 100, 2)
            if total
            else 0.0
        ),
        "cobertura_pdf": (
            round((with_pdf / total) * 100, 2)
            if total
            else 0.0
        ),
    }


def _group_comparative_rows(rows, *, key_name):
    grouped = {}

    for row in rows:
        entity = row.get(key_name)
        entity_id = (
            entity.get("id")
            if isinstance(entity, dict)
            else None
        )
        entity_name = (
            entity.get("nombre")
            if isinstance(entity, dict)
            else "Sin clasificar"
        )

        key = (entity_id, entity_name)
        group = grouped.setdefault(
            key,
            {
                "id": entity_id,
                "nombre": entity_name or "Sin clasificar",
                "proyectos": 0,
                "proyectos_con_produccion": 0,
                "proyectos_sin_produccion": 0,
                "publicaciones": 0,
                "aprobadas": 0,
            },
        )

        total = int(row.get("total_publicaciones") or 0)
        approved = int(row.get("aprobadas") or 0)

        group["proyectos"] += 1
        group["publicaciones"] += total
        group["aprobadas"] += approved

        if total > 0:
            group["proyectos_con_produccion"] += 1
        else:
            group["proyectos_sin_produccion"] += 1

    result = []

    for group in grouped.values():
        publications = int(group["publicaciones"] or 0)
        approved = int(group["aprobadas"] or 0)
        group["tasa_aprobacion"] = (
            round((approved / publications) * 100, 2)
            if publications
            else 0.0
        )
        result.append(group)

    return sorted(
        result,
        key=lambda item: (
            -int(item["publicaciones"] or 0),
            str(item["nombre"] or "").lower(),
        ),
    )


def _group_project_state_rows(rows):
    labels = dict(Proyecto.ESTADOS)
    grouped = {
        state: {
            "estado": state,
            "estado_label": label,
            "proyectos": 0,
            "publicaciones": 0,
            "aprobadas": 0,
        }
        for state, label in Proyecto.ESTADOS
    }

    for row in rows:
        state = row.get("estado")
        group = grouped.setdefault(
            state,
            {
                "estado": state,
                "estado_label": labels.get(state, state),
                "proyectos": 0,
                "publicaciones": 0,
                "aprobadas": 0,
            },
        )
        group["proyectos"] += 1
        group["publicaciones"] += int(
            row.get("total_publicaciones") or 0
        )
        group["aprobadas"] += int(
            row.get("aprobadas") or 0
        )

    return [
        grouped[state]
        for state, _label in Proyecto.ESTADOS
        if grouped[state]["proyectos"] > 0
    ]


def obtener_comparativa_produccion_proyectos(
    *,
    sede_id=None,
    carrera_id=None,
    facultad_id=None,
    estado_proyecto=None,
    estado_publicacion=None,
    anio=None,
    tipo_id=None,
    limite=None,
):
    """
    Devuelve una visión comparativa institucional de proyectos.
    """

    ranking_limit = _ranking_limit(limite)

    queryset, filters = _comparative_project_queryset(
        sede_id=sede_id,
        carrera_id=carrera_id,
        facultad_id=facultad_id,
        estado_proyecto=estado_proyecto,
        estado_publicacion=estado_publicacion,
        anio=anio,
        tipo_id=tipo_id,
    )

    projects = list(
        queryset.order_by("nombre", "id")
    )

    rows = [
        _comparative_project_row(project)
        for project in projects
    ]

    ranked = sorted(
        rows,
        key=lambda row: (
            -int(row["total_publicaciones"] or 0),
            -int(row["aprobadas"] or 0),
            str(row["nombre"] or "").lower(),
            int(row["proyecto_id"] or 0),
        ),
    )

    with_production = [
        row
        for row in ranked
        if int(row["total_publicaciones"] or 0) > 0
    ]
    without_production = [
        row
        for row in ranked
        if int(row["total_publicaciones"] or 0) == 0
    ]

    project_count = len(rows)
    project_with_count = len(with_production)
    project_without_count = len(without_production)

    publication_total = sum(
        int(row["total_publicaciones"] or 0)
        for row in rows
    )
    approved_total = sum(
        int(row["aprobadas"] or 0)
        for row in rows
    )
    in_review_total = sum(
        int(row["en_revision"] or 0)
        for row in rows
    )
    observed_total = sum(
        int(row["observadas"] or 0)
        for row in rows
    )
    rejected_total = sum(
        int(row["rechazadas"] or 0)
        for row in rows
    )
    draft_total = sum(
        int(row["borradores"] or 0)
        for row in rows
    )

    return {
        "filtros": {
            **filters,
            "limite": ranking_limit,
        },
        "resumen": {
            "total_proyectos": project_count,
            "proyectos_con_produccion": project_with_count,
            "proyectos_sin_produccion": project_without_count,
            "publicaciones_total": publication_total,
            "aprobadas_total": approved_total,
            "en_revision_total": in_review_total,
            "observadas_total": observed_total,
            "rechazadas_total": rejected_total,
            "borradores_total": draft_total,
            "promedio_publicaciones_por_proyecto": (
                round(publication_total / project_count, 2)
                if project_count
                else 0.0
            ),
            "tasa_proyectos_con_produccion": (
                round(
                    (project_with_count / project_count) * 100,
                    2,
                )
                if project_count
                else 0.0
            ),
            "tasa_aprobacion_global": (
                round(
                    (approved_total / publication_total) * 100,
                    2,
                )
                if publication_total
                else 0.0
            ),
        },
        "ranking_productividad": with_production[:ranking_limit],
        "proyectos_sin_produccion": without_production[:ranking_limit],
        "por_sede": _group_comparative_rows(
            rows,
            key_name="sede",
        ),
        "por_facultad": _group_comparative_rows(
            rows,
            key_name="facultad",
        ),
        "por_carrera": _group_comparative_rows(
            rows,
            key_name="carrera",
        ),
        "por_estado_proyecto": _group_project_state_rows(rows),
    }
