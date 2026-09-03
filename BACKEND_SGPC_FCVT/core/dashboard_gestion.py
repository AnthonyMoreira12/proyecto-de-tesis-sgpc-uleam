"""Dashboard administrativo de gestión científica del SGPC ULEAM."""

import logging

from django.db import DatabaseError
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Proyecto, Publicacion, PublicacionHistorial
from core.proyectos.services.proyectos_proyecto_services import user_is_project_admin

logger = logging.getLogger(__name__)

PUBLICATION_STATES = {value for value, _label in Publicacion.ESTADOS}
PROJECT_STATES = {value for value, _label in Proyecto.ESTADOS}
DEFAULT_TOP = 10
MAX_TOP = 100


class IsManagementDashboardAdministrator(BasePermission):
    message = "No tienes permisos administrativos para consultar el dashboard de gestión."

    def has_permission(self, request, view):
        return user_is_project_admin(request.user)


def _positive_int(value, field):
    if value in (None, ""):
        return None
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError({field: ["Debe indicar un identificador numérico válido."]}) from exc
    if parsed < 1:
        raise ValidationError({field: ["El identificador debe ser mayor o igual a 1."]})
    return parsed


def _year(value, field):
    if value in (None, ""):
        return None
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError({field: ["El año debe ser numérico."]}) from exc
    if not 1900 <= parsed <= 2100:
        raise ValidationError({field: ["El año debe estar entre 1900 y 2100."]})
    return parsed


def _state(value, allowed, field):
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    if normalized not in allowed:
        raise ValidationError({field: ["El estado indicado no es válido."]})
    return normalized


def _top(value):
    if value in (None, ""):
        return DEFAULT_TOP
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError({"top": ["El límite debe ser numérico."]}) from exc
    if parsed < 1:
        raise ValidationError({"top": ["El límite debe ser mayor o igual a 1."]})
    return min(parsed, MAX_TOP)


def _parse_filters(params):
    exact_year = _year(params.get("anio") or params.get("year"), "anio")
    year_from = _year(params.get("anio_desde"), "anio_desde")
    year_to = _year(params.get("anio_hasta"), "anio_hasta")
    if exact_year is not None:
        year_from = exact_year
        year_to = exact_year
    if year_from is not None and year_to is not None and year_from > year_to:
        year_from, year_to = year_to, year_from

    return {
        "sede_id": _positive_int(params.get("sede") or params.get("sede_id"), "sede"),
        "facultad_id": _positive_int(params.get("facultad") or params.get("facultad_id"), "facultad"),
        "carrera_id": _positive_int(params.get("carrera") or params.get("carrera_id"), "carrera"),
        "proyecto_id": _positive_int(params.get("proyecto") or params.get("proyecto_id"), "proyecto"),
        "tipo_id": _positive_int(params.get("tipo") or params.get("tipo_id"), "tipo"),
        "estado": _state(
            params.get("estado") or params.get("estado_publicacion") or params.get("publication_status"),
            PUBLICATION_STATES,
            "estado",
        ),
        "estado_proyecto": _state(
            params.get("estado_proyecto") or params.get("project_status"),
            PROJECT_STATES,
            "estado_proyecto",
        ),
        "anio": exact_year,
        "anio_desde": year_from,
        "anio_hasta": year_to,
        "top": _top(params.get("top") or params.get("limite") or params.get("limit")),
    }


def _publications(filters):
    qs = Publicacion.objects.select_related(
        "tipo", "sede", "carrera", "carrera__facultad", "proyecto", "usuario_creador"
    )
    if filters["sede_id"]:
        qs = qs.filter(sede_id=filters["sede_id"])
    if filters["facultad_id"]:
        qs = qs.filter(carrera__facultad_id=filters["facultad_id"])
    if filters["carrera_id"]:
        qs = qs.filter(carrera_id=filters["carrera_id"])
    if filters["proyecto_id"]:
        qs = qs.filter(proyecto_id=filters["proyecto_id"])
    if filters["tipo_id"]:
        qs = qs.filter(tipo_id=filters["tipo_id"])
    if filters["estado"]:
        qs = qs.filter(estado=filters["estado"])
    if filters["anio_desde"]:
        qs = qs.filter(anio_publicacion__gte=filters["anio_desde"])
    if filters["anio_hasta"]:
        qs = qs.filter(anio_publicacion__lte=filters["anio_hasta"])
    if filters["estado_proyecto"]:
        qs = qs.filter(proyecto__estado=filters["estado_proyecto"])
    return qs


def _summary(qs):
    values = qs.aggregate(
        total=Count("id"),
        borrador=Count("id", filter=Q(estado=Publicacion.ESTADO_BORRADOR)),
        en_revision=Count("id", filter=Q(estado=Publicacion.ESTADO_EN_REVISION)),
        observada=Count("id", filter=Q(estado=Publicacion.ESTADO_OBSERVADA)),
        aprobada=Count("id", filter=Q(estado=Publicacion.ESTADO_APROBADA)),
        rechazada=Count("id", filter=Q(estado=Publicacion.ESTADO_RECHAZADA)),
        con_pdf=Count("id", filter=Q(archivo_pdf__isnull=False) & ~Q(archivo_pdf="")),
        con_proyecto=Count("id", filter=Q(proyecto__isnull=False)),
    )
    total = int(values["total"] or 0)
    approved = int(values["aprobada"] or 0)
    rejected = int(values["rechazada"] or 0)
    in_review = int(values["en_revision"] or 0)
    observed = int(values["observada"] or 0)
    with_pdf = int(values["con_pdf"] or 0)
    with_project = int(values["con_proyecto"] or 0)
    resolved = approved + rejected
    return {
        "total_publicaciones": total,
        "borrador": int(values["borrador"] or 0),
        "en_revision": in_review,
        "observada": observed,
        "aprobada": approved,
        "rechazada": rejected,
        "pendientes_gestion": in_review + observed,
        "resueltas": resolved,
        "con_pdf": with_pdf,
        "sin_pdf": max(total - with_pdf, 0),
        "con_proyecto": with_project,
        "sin_proyecto": max(total - with_project, 0),
        "tasa_aprobacion_total": round(approved / total * 100, 2) if total else 0.0,
        "tasa_aprobacion_resueltas": round(approved / resolved * 100, 2) if resolved else 0.0,
        "tasa_rechazo_resueltas": round(rejected / resolved * 100, 2) if resolved else 0.0,
        "cobertura_pdf": round(with_pdf / total * 100, 2) if total else 0.0,
        "vinculacion_proyectos": round(with_project / total * 100, 2) if total else 0.0,
    }


def _by_year(qs):
    rows = qs.exclude(anio_publicacion__isnull=True).values("anio_publicacion").annotate(
        total=Count("id"),
        aprobadas=Count("id", filter=Q(estado=Publicacion.ESTADO_APROBADA)),
        observadas=Count("id", filter=Q(estado=Publicacion.ESTADO_OBSERVADA)),
        rechazadas=Count("id", filter=Q(estado=Publicacion.ESTADO_RECHAZADA)),
    ).order_by("anio_publicacion")
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


def _by_type(qs):
    rows = qs.values("tipo_id", "tipo__codigo", "tipo__nombre", "tipo__categoria").annotate(
        total=Count("id"),
        aprobadas=Count("id", filter=Q(estado=Publicacion.ESTADO_APROBADA)),
    ).order_by("-total", "tipo__nombre", "tipo_id")
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


def _group(qs, id_field, name_field, id_key, name_key, limit):
    rows = qs.values(id_field, name_field).annotate(
        total=Count("id"),
        aprobadas=Count("id", filter=Q(estado=Publicacion.ESTADO_APROBADA)),
        en_revision=Count("id", filter=Q(estado=Publicacion.ESTADO_EN_REVISION)),
        observadas=Count("id", filter=Q(estado=Publicacion.ESTADO_OBSERVADA)),
    ).order_by("-total", name_field)[:limit]
    return [
        {
            id_key: row[id_field],
            name_key: row[name_field] or "Sin clasificar",
            "total": int(row["total"] or 0),
            "aprobadas": int(row["aprobadas"] or 0),
            "en_revision": int(row["en_revision"] or 0),
            "observadas": int(row["observadas"] or 0),
        }
        for row in rows
    ]


def _relation_filter(filters):
    q = Q()
    if filters["tipo_id"]:
        q &= Q(publicaciones__tipo_id=filters["tipo_id"])
    if filters["estado"]:
        q &= Q(publicaciones__estado=filters["estado"])
    if filters["anio_desde"]:
        q &= Q(publicaciones__anio_publicacion__gte=filters["anio_desde"])
    if filters["anio_hasta"]:
        q &= Q(publicaciones__anio_publicacion__lte=filters["anio_hasta"])
    return q


def _project_metrics(filters):
    relation_q = _relation_filter(filters)
    qs = Proyecto.objects.select_related("sede", "carrera", "carrera__facultad")
    if filters["sede_id"]:
        qs = qs.filter(sede_id=filters["sede_id"])
    if filters["facultad_id"]:
        qs = qs.filter(carrera__facultad_id=filters["facultad_id"])
    if filters["carrera_id"]:
        qs = qs.filter(carrera_id=filters["carrera_id"])
    if filters["proyecto_id"]:
        qs = qs.filter(pk=filters["proyecto_id"])
    if filters["estado_proyecto"]:
        qs = qs.filter(estado=filters["estado_proyecto"])

    qs = qs.annotate(
        total_publicaciones=Count("publicaciones", filter=relation_q, distinct=True),
        aprobadas=Count(
            "publicaciones",
            filter=relation_q & Q(publicaciones__estado=Publicacion.ESTADO_APROBADA),
            distinct=True,
        ),
        en_revision=Count(
            "publicaciones",
            filter=relation_q & Q(publicaciones__estado=Publicacion.ESTADO_EN_REVISION),
            distinct=True,
        ),
        observadas=Count(
            "publicaciones",
            filter=relation_q & Q(publicaciones__estado=Publicacion.ESTADO_OBSERVADA),
            distinct=True,
        ),
    ).order_by("-total_publicaciones", "-aprobadas", "nombre", "id")

    rows = []
    for project in qs:
        total = int(project.total_publicaciones or 0)
        approved = int(project.aprobadas or 0)
        rows.append(
            {
                "proyecto_id": project.pk,
                "nombre": project.nombre,
                "estado": project.estado,
                "estado_label": project.get_estado_display(),
                "sede": project.sede.nombre if project.sede_id else None,
                "carrera": project.carrera.nombre if project.carrera_id else None,
                "facultad": project.carrera.facultad.nombre if project.carrera_id else None,
                "total_publicaciones": total,
                "aprobadas": approved,
                "en_revision": int(project.en_revision or 0),
                "observadas": int(project.observadas or 0),
                "tasa_aprobacion": round(approved / total * 100, 2) if total else 0.0,
            }
        )

    with_production = [row for row in rows if row["total_publicaciones"] > 0]
    without_production = [row for row in rows if row["total_publicaciones"] == 0]
    total_projects = len(rows)
    return {
        "resumen": {
            "total_proyectos": total_projects,
            "proyectos_con_produccion": len(with_production),
            "proyectos_sin_produccion": len(without_production),
            "tasa_proyectos_con_produccion": (
                round(len(with_production) / total_projects * 100, 2)
                if total_projects else 0.0
            ),
        },
        "ranking_productividad": with_production[:filters["top"]],
        "proyectos_sin_produccion": without_production[:filters["top"]],
    }


def _review_queue(qs, limit):
    rows = qs.filter(estado=Publicacion.ESTADO_EN_REVISION).select_related(
        "tipo", "usuario_creador", "sede", "carrera"
    ).order_by("updated_at", "id")[:limit]
    return [
        {
            "publicacion_id": item.pk,
            "numero": item.numero,
            "tipo": item.tipo.nombre if item.tipo_id else None,
            "tipo_codigo": item.tipo.codigo if item.tipo_id else None,
            "anio_publicacion": item.anio_publicacion,
            "sede": item.sede.nombre if item.sede_id else None,
            "carrera": item.carrera.nombre if item.carrera_id else None,
            "usuario_creador_id": item.usuario_creador_id,
            "usuario_creador_email": getattr(item.usuario_creador, "email", None),
            "estado": item.estado,
            "estado_label": item.get_estado_display(),
            "updated_at": item.updated_at,
        }
        for item in rows
    ]


def _recent_activity(qs, limit):
    rows = PublicacionHistorial.objects.filter(publicacion__in=qs).order_by(
        "-created_at", "-id"
    )[:limit]
    return [
        {
            "id": item.pk,
            "publicacion_id": item.publicacion_id,
            "evento": item.evento,
            "evento_label": item.get_evento_display(),
            "actor_id": item.actor_id,
            "actor_nombre": item.actor_nombre,
            "actor_email": item.actor_email,
            "estado_anterior": item.estado_anterior,
            "estado_resultante": item.estado_resultante,
            "created_at": item.created_at,
        }
        for item in rows
    ]


def _filter_metadata():
    years = list(
        Publicacion.objects.exclude(anio_publicacion__isnull=True)
        .values_list("anio_publicacion", flat=True)
        .distinct()
        .order_by("-anio_publicacion")
    )
    return {
        "estados_publicacion": [
            {"value": value, "label": label}
            for value, label in Publicacion.ESTADOS
        ],
        "estados_proyecto": [
            {"value": value, "label": label}
            for value, label in Proyecto.ESTADOS
        ],
        "anios": years,
    }


def build_management_dashboard_payload(params):
    filters = _parse_filters(params)
    qs = _publications(filters)
    indicators = _summary(qs)
    projects = _project_metrics(filters)
    return {
        "ok": True,
        "filtros_aplicados": filters,
        "filtros_disponibles": _filter_metadata(),
        "indicadores": indicators,
        "alertas": {
            "publicaciones_en_revision": indicators["en_revision"],
            "publicaciones_observadas": indicators["observada"],
            "publicaciones_sin_pdf": indicators["sin_pdf"],
            "publicaciones_sin_proyecto": indicators["sin_proyecto"],
            "proyectos_sin_produccion": projects["resumen"]["proyectos_sin_produccion"],
        },
        "distribuciones": {
            "por_anio": _by_year(qs),
            "por_tipo": _by_type(qs),
            "por_sede": _group(qs, "sede_id", "sede__nombre", "sede_id", "sede", filters["top"]),
            "por_facultad": _group(
                qs,
                "carrera__facultad_id",
                "carrera__facultad__nombre",
                "facultad_id",
                "facultad",
                filters["top"],
            ),
            "por_carrera": _group(qs, "carrera_id", "carrera__nombre", "carrera_id", "carrera", filters["top"]),
            "por_proyecto": _group(qs, "proyecto_id", "proyecto__nombre", "proyecto_id", "proyecto", filters["top"]),
        },
        "proyectos": projects,
        "cola_revision": _review_queue(qs, filters["top"]),
        "actividad_reciente": _recent_activity(qs, filters["top"]),
    }


class DashboardGestionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsManagementDashboardAdministrator]

    def get(self, request, *args, **kwargs):
        try:
            payload = build_management_dashboard_payload(request.query_params)
        except DatabaseError:
            logger.exception("Error de base de datos al construir el dashboard de gestión.")
            return Response(
                {
                    "ok": False,
                    "detail": (
                        "No fue posible cargar el dashboard de gestión debido "
                        "a un error temporal de la base de datos."
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(payload, status=status.HTTP_200_OK)