"""Servicios de escritura del registro inmutable de auditoría."""

from datetime import date, datetime
from decimal import Decimal

from core.auditoria.context import get_current_request
from core.models import AuditoriaSistema


def _json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "pk"):
        return getattr(value, "pk", None)
    return str(value)


def request_metadata(request):
    request = request or get_current_request()
    if request is None:
        return {"ip": None, "user_agent": "", "ruta": "", "metodo_http": ""}

    forwarded = str(request.META.get("HTTP_X_FORWARDED_FOR", "") or "").strip()
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")

    return {
        "ip": ip or None,
        "user_agent": str(request.META.get("HTTP_USER_AGENT", "") or "")[:500],
        "ruta": str(getattr(request, "path", "") or "")[:500],
        "metodo_http": str(getattr(request, "method", "") or "")[:12].upper(),
    }


def registrar_evento_auditoria(
    *,
    actor=None,
    accion,
    modulo,
    entidad=None,
    entidad_tipo=None,
    entidad_id=None,
    descripcion="",
    datos_anteriores=None,
    datos_nuevos=None,
    contexto=None,
    request=None,
):
    """Crea un evento de auditoría. Los eventos no se actualizan ni eliminan."""
    if entidad is not None:
        entidad_tipo = entidad_tipo or entidad.__class__.__name__
        entidad_id = entidad_id if entidad_id is not None else getattr(entidad, "pk", "")

    request = request or get_current_request()
    if actor is None and request is not None:
        request_user = getattr(request, "user", None)
        if getattr(request_user, "is_authenticated", False):
            actor = request_user

    meta = request_metadata(request)

    return AuditoriaSistema.objects.create(
        actor=actor if getattr(actor, "pk", None) else None,
        accion=str(accion or "").strip().lower()[:60],
        modulo=str(modulo or "").strip().lower()[:80],
        entidad_tipo=str(entidad_tipo or "").strip()[:100],
        entidad_id=str(entidad_id or "").strip()[:80],
        descripcion=str(descripcion or "").strip(),
        datos_anteriores=_json_safe(datos_anteriores or {}),
        datos_nuevos=_json_safe(datos_nuevos or {}),
        contexto=_json_safe(contexto or {}),
        **meta,
    )
