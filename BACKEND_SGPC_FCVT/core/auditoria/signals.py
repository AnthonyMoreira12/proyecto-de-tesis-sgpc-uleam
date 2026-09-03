"""Auditoría transversal de modelos de negocio del SGPC.

La lista es deliberadamente explícita. No se auditan tokens, contraseñas,
notificaciones ni el propio log para evitar fuga de secretos, recursión y
ruido operativo.
"""

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from core.auditoria.context import get_current_request
from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.models import (
    AreaConocimiento,
    Articulo,
    Autor,
    Banner,
    BannerConfiguracion,
    CapituloLibro,
    Carrera,
    CarreraSede,
    Ciudad,
    Facultad,
    Libro,
    Pais,
    Ponencia,
    Proyecto,
    ProyectoAutor,
    PublicacionArchivo,
    PublicacionAutor,
    PublicacionHistorial,
    PublicacionRevision,
    Sede,
    Subarea,
    TipoPublicacion,
    Usuario,
)


AUDIT_MODEL_CONFIG = {
    Usuario: "usuarios",
    Sede: "estructura_academica",
    Facultad: "estructura_academica",
    Carrera: "estructura_academica",
    CarreraSede: "estructura_academica",
    Proyecto: "proyectos",
    ProyectoAutor: "proyectos",
    Banner: "avisos",
    BannerConfiguracion: "avisos",
    AreaConocimiento: "catalogos",
    Subarea: "catalogos",
    Pais: "catalogos",
    Ciudad: "catalogos",
    TipoPublicacion: "publicaciones",
    Ponencia: "publicaciones",
    Articulo: "publicaciones",
    Libro: "publicaciones",
    CapituloLibro: "publicaciones",
    Autor: "autores",
    PublicacionAutor: "publicaciones",
    PublicacionArchivo: "publicaciones",
    PublicacionRevision: "publicaciones",
    PublicacionHistorial: "publicaciones",
}

# Nunca deben copiarse al log aunque en el futuro se agreguen a un modelo
# auditable. Los nombres se comparan por field.name y field.attname.
SENSITIVE_FIELDS = {
    "password",
    "token",
    "refresh_token",
    "access_token",
    "secret",
    "client_secret",
}

IGNORED_FIELDS = {
    "updated_at",
    "last_login",
}


def _actor_from_request(request):
    user = getattr(request, "user", None) if request is not None else None
    if getattr(user, "is_authenticated", False) and getattr(user, "pk", None):
        return user
    return None


def _safe_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "name") and not hasattr(value, "pk"):
        return str(getattr(value, "name", "") or "")
    if hasattr(value, "pk"):
        return getattr(value, "pk", None)
    if isinstance(value, (list, tuple, set)):
        return [_safe_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _safe_value(v) for k, v in value.items()}
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except (TypeError, ValueError):
            pass
    return str(value)


def _snapshot(instance):
    data = {}
    for field in instance._meta.concrete_fields:
        if getattr(field, "primary_key", False):
            continue
        name = str(field.name)
        attname = str(getattr(field, "attname", name))
        lowered = {name.lower(), attname.lower()}
        if lowered & SENSITIVE_FIELDS or lowered & IGNORED_FIELDS:
            continue
        try:
            value = getattr(instance, attname)
        except Exception:
            continue
        data[name] = _safe_value(value)
    return data


def _diff(before, after):
    keys = set(before) | set(after)
    old = {}
    new = {}
    for key in sorted(keys):
        if before.get(key) != after.get(key):
            old[key] = before.get(key)
            new[key] = after.get(key)
    return old, new


def _event_action(instance, *, created=False, deleted=False):
    if deleted:
        return "eliminar"
    if isinstance(instance, PublicacionRevision) and created:
        return str(getattr(instance, "decision", "") or "actualizar")
    if isinstance(instance, PublicacionHistorial) and created:
        mapping = {
            "creada": "crear",
            "editada": "actualizar",
            "enviada_revision": "enviar",
            "reenviada_revision": "enviar",
            "observada": "observar",
            "aprobada": "aprobar",
            "rechazada": "rechazar",
        }
        return mapping.get(str(getattr(instance, "evento", "") or ""), "actualizar")
    return "crear" if created else "actualizar"


def _description(instance, action):
    label = str(instance._meta.verbose_name or instance.__class__.__name__).strip()
    return f"{action.capitalize()} automático de {label}."


@receiver(pre_save, dispatch_uid="sgpc_audit_pre_save_business_models")
def audit_pre_save(sender, instance, **kwargs):
    if sender not in AUDIT_MODEL_CONFIG or not getattr(instance, "pk", None):
        return
    try:
        previous = sender._default_manager.get(pk=instance.pk)
        instance._sgpc_audit_before = _snapshot(previous)
    except sender.DoesNotExist:
        instance._sgpc_audit_before = {}
    except Exception:
        instance._sgpc_audit_before = {}


@receiver(post_save, dispatch_uid="sgpc_audit_post_save_business_models")
def audit_post_save(sender, instance, created, **kwargs):
    modulo = AUDIT_MODEL_CONFIG.get(sender)
    if not modulo:
        return

    request = get_current_request()
    actor = _actor_from_request(request)

    # Los modelos de historial/revisión ya contienen el actor formal; úselo
    # cuando la operación provenga de un servicio o proceso sin request.
    if actor is None:
        actor = getattr(instance, "actor", None) or getattr(instance, "revisor", None)

    after = _snapshot(instance)
    before = {} if created else getattr(instance, "_sgpc_audit_before", {}) or {}
    if created:
        old, new = {}, after
    else:
        old, new = _diff(before, after)
        if not old and not new:
            return

    action = _event_action(instance, created=created)
    registrar_evento_auditoria(
        actor=actor,
        accion=action,
        modulo=modulo,
        entidad=instance,
        descripcion=_description(instance, action),
        datos_anteriores=old,
        datos_nuevos=new,
        contexto={"origen": "auditoria_transversal"},
        request=request,
    )


@receiver(post_delete, dispatch_uid="sgpc_audit_post_delete_business_models")
def audit_post_delete(sender, instance, **kwargs):
    modulo = AUDIT_MODEL_CONFIG.get(sender)
    if not modulo:
        return
    request = get_current_request()
    actor = _actor_from_request(request)
    registrar_evento_auditoria(
        actor=actor,
        accion="eliminar",
        modulo=modulo,
        entidad_tipo=instance.__class__.__name__,
        entidad_id=getattr(instance, "pk", ""),
        descripcion=_description(instance, "eliminar"),
        datos_anteriores=_snapshot(instance),
        datos_nuevos={},
        contexto={"origen": "auditoria_transversal"},
        request=request,
    )
