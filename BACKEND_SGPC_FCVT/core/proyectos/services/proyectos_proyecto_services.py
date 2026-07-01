import json

from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.models import Autor, ProyectoAutor

PROYECTO_AUTOR_ROLES = {"principal", "coinvestigador", "colaborador"}

def user_is_project_admin(user):
    if not user or not getattr(user, "is_authenticated", False):
        return False

    return bool(
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
    )

def require_project_admin(user):
    if not user or not getattr(user, "is_authenticated", False):
        raise PermissionDenied("Debes iniciar sesión.")

    if not user_is_project_admin(user):
        raise PermissionDenied("No autorizado.")

def parse_autores_data_input(raw_items):
    if raw_items is None:
        return None

    if isinstance(raw_items, str):
        raw_items = raw_items.strip()

        if not raw_items:
            return []

        try:
            raw_items = json.loads(raw_items)
        except json.JSONDecodeError:
            raise ValidationError(
                "La lista de autores del proyecto no tiene un JSON válido."
            )

    if isinstance(raw_items, dict):
        raw_items = [raw_items]

    if not isinstance(raw_items, list):
        raise ValidationError("La lista de autores del proyecto es inválida.")

    return raw_items

def normalize_proyecto_autores_payload(raw_items):
    raw_items = parse_autores_data_input(raw_items)

    if raw_items is None:
        return None

    if not raw_items:
        return []

    normalized = []

    for index, item in enumerate(raw_items, start=1):
        if not isinstance(item, dict):
            raise ValidationError(
                "Cada autor del proyecto debe ser un objeto válido."
            )

        autor_id = item.get("autor") or item.get("autor_id") or item.get("id")
        rol = str(item.get("rol") or "principal").strip().lower()
        orden = item.get("orden", index)

        if not autor_id:
            raise ValidationError("Cada registro debe incluir un autor.")

        try:
            autor_id = int(autor_id)
        except (TypeError, ValueError):
            raise ValidationError("El identificador del autor es inválido.")

        try:
            orden = int(orden)
        except (TypeError, ValueError):
            raise ValidationError(
                "El orden de los autores del proyecto es inválido."
            )

        if rol not in PROYECTO_AUTOR_ROLES:
            raise ValidationError(
                "El rol de uno o más autores del proyecto es inválido."
            )

        if orden < 1:
            raise ValidationError(
                "El orden de los autores del proyecto debe ser mayor o igual a 1."
            )

        normalized.append(
            {
                "autor_id": autor_id,
                "rol": rol,
                "orden": orden,
            }
        )

    seen_autores = set()
    seen_ordenes = set()

    for item in normalized:
        autor_id = item["autor_id"]
        orden = item["orden"]

        if autor_id in seen_autores:
            raise ValidationError(
                "No puede repetir el mismo autor dentro del proyecto."
            )

        if orden in seen_ordenes:
            raise ValidationError(
                "No puede repetir el mismo orden dentro del proyecto."
            )

        seen_autores.add(autor_id)
        seen_ordenes.add(orden)

    autores_existentes = set(
        Autor.objects.filter(id__in=seen_autores).values_list("id", flat=True)
    )

    if autores_existentes != seen_autores:
        raise ValidationError("Uno o más autores seleccionados no existen.")

    normalized.sort(key=lambda item: item["orden"])

    return normalized

def autores_payload_tiene_principal(autores_data):
    if not autores_data:
        return False

    return any(
        str(item.get("rol") or "").strip().lower() == "principal"
        for item in autores_data
    )

def proyecto_tiene_investigador_principal(proyecto):
    if not proyecto or not getattr(proyecto, "pk", None):
        return False

    return proyecto.participaciones.filter(rol="principal").exists()

@transaction.atomic
def sync_proyecto_autores(proyecto, autores_data):
    autores_data = normalize_proyecto_autores_payload(autores_data)

    if autores_data is None:
        return []

    ProyectoAutor.objects.filter(proyecto=proyecto).delete()

    if not autores_data:
        return []

    participaciones = [
        ProyectoAutor(
            proyecto=proyecto,
            autor_id=item["autor_id"],
            rol=item["rol"],
            orden=item["orden"],
        )
        for item in autores_data
    ]

    ProyectoAutor.objects.bulk_create(participaciones)

    return participaciones

# ============================================================
# LÓGICA DE ESTADOS DEL PROYECTO (MÁQUINA DE ESTADOS REFACTORIZADA)
# ============================================================

ESTADO_TRANSITIONS = {
    "nuevo": "arrastre",
    "arrastre": "cierre",
    "cierre": "arrastre",
}

LEGACY_ESTADO_MAP = {
    "true": "arrastre", "1": "arrastre", "si": "arrastre", "sí": "arrastre",
    "vigente": "arrastre", "activo": "arrastre", "activa": "arrastre",
    "active": "arrastre", "abierto": "arrastre", "abierta": "arrastre",
    "false": "cierre", "0": "cierre", "no": "cierre",
    "finalizado": "cierre", "finalizada": "cierre", "cerrado": "cierre",
    "cerrada": "cierre", "closed": "cierre", "close": "cierre",
    "none": "nuevo", "null": "nuevo",
}

def _estados_validos(proyecto):
    return {value for value, _ in proyecto.ESTADOS}

def normalizar_estado(estado, default="nuevo"):
    raw = str(estado if estado is not None else "").strip().lower()

    if not raw:
        return default

    if raw in {"nuevo", "arrastre", "cierre"}:
        return raw

    if raw in LEGACY_ESTADO_MAP:
        return LEGACY_ESTADO_MAP[raw]

    return default

def resolver_estado_destino(proyecto, estado_solicitado=""):
    estados_validos = _estados_validos(proyecto)
    
    estado_actual = normalizar_estado(
        proyecto.estado,
        default="arrastre",
    )

    raw_solicitado = str(
        estado_solicitado if estado_solicitado is not None else ""
    ).strip()

    if raw_solicitado:
        estado_destino = normalizar_estado(raw_solicitado, default="")
        # Si el usuario envió algo, pero al normalizarlo no es un estado válido, bloqueamos.
        if not estado_destino:
            raise ValidationError(
                {"estado": f"El estado solicitado '{raw_solicitado}' es inválido."}
            )
    else:
        # Si no envió nada, aplicamos la transición automática de la máquina de estados.
        estado_destino = ESTADO_TRANSITIONS.get(
            estado_actual,
            "arrastre",
        )

    if estado_destino not in estados_validos:
        raise ValidationError(
            {"estado": "El estado de destino calculado es inválido."}
        )

    return estado_destino