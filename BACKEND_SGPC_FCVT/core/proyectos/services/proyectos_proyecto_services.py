"""
Servicios del módulo de proyectos.

Este módulo centraliza:

- Validación de permisos administrativos.
- Lectura y normalización del equipo investigador.
- Sincronización transaccional de autores.
- Validación de roles y órdenes.
- Comprobación del investigador principal.
- Normalización y resolución de estados del proyecto.
"""

import json
import unicodedata
from collections.abc import Mapping

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction

from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from core.models import (
    Autor,
    Proyecto,
    ProyectoAutor,
)


# ============================================================
# CONFIGURACIÓN DE AUTORES
# ============================================================

PROYECTO_AUTOR_ROLES = frozenset(
    value
    for value, _label in ProyectoAutor.ROLES
)

PROYECTO_AUTOR_ROLE_ALIASES = {
    "principal": "principal",
    "investigador_principal": "principal",
    "investigadorprincipal": "principal",

    "coinvestigador": "coinvestigador",
    "co_investigador": "coinvestigador",
    "co-investigador": "coinvestigador",

    "colaborador": "colaborador",
}

MAX_AUTORES_POR_PROYECTO = 100
MAX_AUTORES_JSON_LENGTH = 100_000


# ============================================================
# CONFIGURACIÓN DE ESTADOS
# ============================================================

PROYECTO_ESTADOS = frozenset(
    value
    for value, _label in Proyecto.ESTADOS
)

ESTADO_TRANSITIONS = {
    "nuevo": "arrastre",
    "arrastre": "cierre",
    "cierre": "arrastre",
}

LEGACY_ESTADO_MAP = {
    # Valores activos
    "true": "arrastre",
    "1": "arrastre",
    "si": "arrastre",
    "sí": "arrastre",
    "vigente": "arrastre",
    "activo": "arrastre",
    "activa": "arrastre",
    "active": "arrastre",
    "abierto": "arrastre",
    "abierta": "arrastre",

    # Valores cerrados
    "false": "cierre",
    "0": "cierre",
    "no": "cierre",
    "finalizado": "cierre",
    "finalizada": "cierre",
    "cerrado": "cierre",
    "cerrada": "cierre",
    "closed": "cierre",
    "close": "cierre",

    # Valores iniciales
    "none": "nuevo",
    "null": "nuevo",
}


# ============================================================
# UTILIDADES GENERALES
# ============================================================

def _normalize_text(value):
    """
    Normaliza Unicode y elimina espacios repetidos.
    """
    normalized = unicodedata.normalize(
        "NFKC",
        str(value or ""),
    )

    return " ".join(
        normalized.split()
    )


def _normalize_token(value):
    """
    Normaliza un valor utilizado como código o alias.
    """
    normalized = _normalize_text(
        value
    ).casefold()

    normalized = (
        normalized
        .replace(" ", "_")
        .replace("-", "_")
    )

    while "__" in normalized:
        normalized = normalized.replace(
            "__",
            "_",
        )

    return normalized.strip("_")


def _parse_positive_integer(
    value,
    *,
    field_label,
):
    """
    Convierte un valor en entero positivo.

    Los booleanos no se aceptan porque en Python son subclases
    de int y podrían convertirse accidentalmente en 0 o 1.
    """
    if isinstance(
        value,
        bool,
    ):
        raise ValidationError(
            f"{field_label} debe ser un número entero válido."
        )

    try:
        normalized_value = int(
            str(value).strip()
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise ValidationError(
            f"{field_label} debe ser un número entero válido."
        ) from exc

    if normalized_value < 1:
        raise ValidationError(
            f"{field_label} debe ser mayor o igual a 1."
        )

    return normalized_value


def _django_validation_detail(exc):
    """
    Convierte ValidationError de Django en una estructura
    compatible con Django REST Framework.
    """
    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
        return list(
            exc.messages
        )

    return str(exc)


# ============================================================
# PERMISOS ADMINISTRATIVOS
# ============================================================

def user_is_project_admin(user):
    """
    Determina si el usuario puede administrar proyectos.

    Se utilizan is_staff e is_superuser porque el modelo
    Proyecto también exige estos privilegios para creado_por.
    """
    if (
        user is None
        or not getattr(
            user,
            "is_authenticated",
            False,
        )
    ):
        return False

    return bool(
        getattr(
            user,
            "is_staff",
            False,
        )
        or getattr(
            user,
            "is_superuser",
            False,
        )
    )


def require_project_admin(user):
    """
    Exige autenticación y privilegios administrativos.
    """
    if (
        user is None
        or not getattr(
            user,
            "is_authenticated",
            False,
        )
    ):
        raise PermissionDenied(
            "Debes iniciar sesión para gestionar proyectos."
        )

    if not user_is_project_admin(
        user
    ):
        raise PermissionDenied(
            (
                "No tienes permisos administrativos "
                "para gestionar proyectos."
            )
        )


# ============================================================
# ENTRADA DE AUTORES
# ============================================================

def parse_autores_data_input(raw_items):
    """
    Convierte la entrada de autores en una lista.

    Formatos admitidos:

    - Lista de objetos.
    - Tupla de objetos.
    - Un único objeto.
    - JSON enviado mediante multipart/form-data.
    - Cadena vacía para representar una lista vacía.

    None significa que el campo no fue enviado.
    """
    if raw_items is None:
        return None

    if isinstance(
        raw_items,
        bytes,
    ):
        try:
            raw_items = raw_items.decode(
                "utf-8"
            )

        except UnicodeDecodeError as exc:
            raise ValidationError(
                (
                    "La lista de autores contiene una "
                    "codificación inválida."
                )
            ) from exc

    if isinstance(
        raw_items,
        str,
    ):
        serialized_items = raw_items.strip()

        if not serialized_items:
            return []

        if (
            len(serialized_items)
            > MAX_AUTORES_JSON_LENGTH
        ):
            raise ValidationError(
                (
                    "La lista de autores supera el tamaño "
                    "máximo permitido."
                )
            )

        try:
            raw_items = json.loads(
                serialized_items
            )

        except json.JSONDecodeError as exc:
            raise ValidationError(
                (
                    "La lista de autores del proyecto "
                    "no contiene un JSON válido."
                )
            ) from exc

        if raw_items is None:
            return []

    if isinstance(
        raw_items,
        Mapping,
    ):
        raw_items = [
            dict(raw_items)
        ]

    elif isinstance(
        raw_items,
        tuple,
    ):
        raw_items = list(
            raw_items
        )

    if not isinstance(
        raw_items,
        list,
    ):
        raise ValidationError(
            (
                "La lista de autores del proyecto "
                "debe ser un arreglo de objetos."
            )
        )

    if (
        len(raw_items)
        > MAX_AUTORES_POR_PROYECTO
    ):
        raise ValidationError(
            (
                "Un proyecto no puede contener más de "
                f"{MAX_AUTORES_POR_PROYECTO} autores."
            )
        )

    return raw_items


def _extract_author_id(
    item,
    *,
    position,
):
    """
    Obtiene el identificador desde los alias admitidos.

    Alias:

    - autor_id
    - autor
    - id
    """
    raw_author = None

    for field_name in (
        "autor_id",
        "autor",
        "id",
    ):
        if (
            field_name in item
            and item.get(field_name)
            not in (
                None,
                "",
            )
        ):
            raw_author = item.get(
                field_name
            )
            break

    if isinstance(
        raw_author,
        Mapping,
    ):
        raw_author = (
            raw_author.get("id")
            or raw_author.get("pk")
            or raw_author.get("autor_id")
        )

    elif hasattr(
        raw_author,
        "pk",
    ):
        raw_author = getattr(
            raw_author,
            "pk",
            None,
        )

    if raw_author in (
        None,
        "",
    ):
        raise ValidationError(
            (
                f"El registro de autor #{position} "
                "debe incluir un autor."
            )
        )

    return _parse_positive_integer(
        raw_author,
        field_label=(
            f"El identificador del autor #{position}"
        ),
    )


def _normalize_author_role(
    value,
    *,
    position,
):
    """
    Normaliza y valida el rol del autor.
    """
    if value in (
        None,
        "",
    ):
        normalized_role = "principal"

    else:
        role_token = _normalize_token(
            value
        )

        normalized_role = (
            PROYECTO_AUTOR_ROLE_ALIASES.get(
                role_token,
                role_token,
            )
        )

    if (
        normalized_role
        not in PROYECTO_AUTOR_ROLES
    ):
        valid_roles = ", ".join(
            sorted(
                PROYECTO_AUTOR_ROLES
            )
        )

        raise ValidationError(
            (
                f"El rol del autor #{position} no es válido. "
                f"Valores permitidos: {valid_roles}."
            )
        )

    return normalized_role


def normalize_proyecto_autores_payload(
    raw_items,
):
    """
    Normaliza y valida el equipo investigador.

    Cada elemento resultante contiene:

        {
            "autor_id": 12,
            "rol": "principal",
            "orden": 1,
        }

    No exige un investigador principal en todos los estados.
    Esa regla se aplica cuando el proyecto se cierra.
    """
    parsed_items = parse_autores_data_input(
        raw_items
    )

    if parsed_items is None:
        return None

    if not parsed_items:
        return []

    normalized_items = []

    seen_author_ids = set()
    seen_orders = set()

    for position, item in enumerate(
        parsed_items,
        start=1,
    ):
        if not isinstance(
            item,
            Mapping,
        ):
            raise ValidationError(
                (
                    f"El registro de autor #{position} "
                    "debe ser un objeto válido."
                )
            )

        author_id = _extract_author_id(
            item,
            position=position,
        )

        role = _normalize_author_role(
            item.get("rol"),
            position=position,
        )

        raw_order = item.get(
            "orden",
            position,
        )

        if raw_order in (
            None,
            "",
        ):
            raw_order = position

        order = _parse_positive_integer(
            raw_order,
            field_label=(
                f"El orden del autor #{position}"
            ),
        )

        if author_id in seen_author_ids:
            raise ValidationError(
                (
                    "No puede repetir el mismo autor "
                    "dentro del proyecto."
                )
            )

        if order in seen_orders:
            raise ValidationError(
                (
                    "No puede repetir el mismo orden "
                    "dentro del proyecto."
                )
            )

        seen_author_ids.add(
            author_id
        )

        seen_orders.add(
            order
        )

        normalized_items.append(
            {
                "autor_id": author_id,
                "rol": role,
                "orden": order,
            }
        )

    existing_author_ids = set(
        Autor.objects
        .filter(
            pk__in=seen_author_ids
        )
        .values_list(
            "pk",
            flat=True,
        )
    )

    missing_author_ids = sorted(
        seen_author_ids
        - existing_author_ids
    )

    if missing_author_ids:
        missing_text = ", ".join(
            str(author_id)
            for author_id
            in missing_author_ids
        )

        raise ValidationError(
            (
                "No existen los siguientes autores "
                f"seleccionados: {missing_text}."
            )
        )

    normalized_items.sort(
        key=lambda item: (
            item["orden"],
            item["autor_id"],
        )
    )

    return normalized_items


# ============================================================
# INVESTIGADOR PRINCIPAL
# ============================================================

def autores_payload_tiene_principal(
    autores_data,
):
    """
    Indica si el payload contiene al menos un investigador
    principal.
    """
    parsed_items = parse_autores_data_input(
        autores_data
    )

    if not parsed_items:
        return False

    for position, item in enumerate(
        parsed_items,
        start=1,
    ):
        if not isinstance(
            item,
            Mapping,
        ):
            continue

        role = _normalize_author_role(
            item.get("rol"),
            position=position,
        )

        if role == "principal":
            return True

    return False


def proyecto_tiene_investigador_principal(
    proyecto,
):
    """
    Comprueba el equipo almacenado del proyecto.
    """
    project_id = getattr(
        proyecto,
        "pk",
        None,
    )

    if not project_id:
        return False

    return (
        ProyectoAutor.objects
        .filter(
            proyecto_id=project_id,
            rol="principal",
        )
        .exists()
    )


# ============================================================
# SINCRONIZACIÓN DEL EQUIPO
# ============================================================

@transaction.atomic
def sync_proyecto_autores(
    proyecto,
    autores_data,
):
    """
    Reemplaza transaccionalmente el equipo investigador.

    La operación bloquea:

    - El proyecto.
    - Los autores involucrados.
    - Las participaciones actuales.

    Si alguna validación o inserción falla, la transacción
    restaura automáticamente el equipo anterior.
    """
    project_id = getattr(
        proyecto,
        "pk",
        None,
    )

    if not project_id:
        raise ValidationError(
            (
                "El proyecto debe estar guardado antes "
                "de asignar autores."
            )
        )

    normalized_items = (
        normalize_proyecto_autores_payload(
            autores_data
        )
    )

    if normalized_items is None:
        return []

    try:
        locked_project = (
            Proyecto.objects
            .select_for_update()
            .get(
                pk=project_id
            )
        )

    except Proyecto.DoesNotExist as exc:
        raise ValidationError(
            "El proyecto indicado no existe."
        ) from exc

    author_ids = {
        item["autor_id"]
        for item in normalized_items
    }

    if author_ids:
        locked_author_ids = set(
            Autor.objects
            .select_for_update()
            .filter(
                pk__in=author_ids
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        missing_author_ids = sorted(
            author_ids
            - locked_author_ids
        )

        if missing_author_ids:
            missing_text = ", ".join(
                str(author_id)
                for author_id
                in missing_author_ids
            )

            raise ValidationError(
                (
                    "Uno o más autores dejaron de estar "
                    "disponibles durante la operación: "
                    f"{missing_text}."
                )
            )

    # Bloquea las participaciones existentes antes de eliminarlas.
    list(
        ProyectoAutor.objects
        .select_for_update()
        .filter(
            proyecto_id=locked_project.pk
        )
        .values_list(
            "pk",
            flat=True,
        )
    )

    ProyectoAutor.objects.filter(
        proyecto_id=locked_project.pk
    ).delete()

    if not normalized_items:
        return []

    participations = [
        ProyectoAutor(
            proyecto=locked_project,
            autor_id=item["autor_id"],
            rol=item["rol"],
            orden=item["orden"],
        )
        for item in normalized_items
    ]

    try:
        for participation in participations:
            participation.clean()

        ProyectoAutor.objects.bulk_create(
            participations
        )

    except DjangoValidationError as exc:
        raise ValidationError(
            _django_validation_detail(
                exc
            )
        ) from exc

    except IntegrityError as exc:
        raise ValidationError(
            (
                "No fue posible guardar el equipo investigador. "
                "Verifique que no existan autores u órdenes "
                "repetidos."
            )
        ) from exc

    return list(
        ProyectoAutor.objects
        .select_related(
            "autor",
            "autor__usuario",
        )
        .filter(
            proyecto_id=locked_project.pk
        )
        .order_by(
            "orden",
            "pk",
        )
    )


# ============================================================
# ESTADOS
# ============================================================

def _estados_validos(proyecto=None):
    """
    Obtiene los estados definidos por el modelo.
    """
    choices = getattr(
        proyecto,
        "ESTADOS",
        Proyecto.ESTADOS,
    )

    return {
        value
        for value, _label in choices
    }


def normalizar_estado(
    estado,
    default="nuevo",
):
    """
    Normaliza estados actuales y valores heredados.

    Cuando el valor no es reconocido, devuelve default.
    Utilizar default=None permite detectar valores inválidos.
    """
    raw_state = _normalize_text(
        estado
    ).casefold()

    if not raw_state:
        return default

    if raw_state in PROYECTO_ESTADOS:
        return raw_state

    if raw_state in LEGACY_ESTADO_MAP:
        return LEGACY_ESTADO_MAP[
            raw_state
        ]

    return default


def resolver_estado_destino(
    proyecto,
    estado_solicitado="",
):
    """
    Resuelve el siguiente estado del proyecto.

    Cuando se envía un estado:

    - Se normaliza.
    - Se valida contra Proyecto.ESTADOS.
    - Se utiliza directamente.

    Cuando no se envía estado, se aplica la transición automática:

        nuevo -> arrastre
        arrastre -> cierre
        cierre -> arrastre
    """
    if proyecto is None:
        raise ValidationError(
            {
                "estado": (
                    "No fue posible determinar el proyecto "
                    "que se desea actualizar."
                )
            }
        )

    valid_states = _estados_validos(
        proyecto
    )

    current_state = normalizar_estado(
        getattr(
            proyecto,
            "estado",
            None,
        ),
        default="nuevo",
    )

    raw_requested_state = _normalize_text(
        estado_solicitado
    )

    if raw_requested_state:
        destination_state = normalizar_estado(
            raw_requested_state,
            default=None,
        )

        if destination_state is None:
            raise ValidationError(
                {
                    "estado": (
                        "El estado solicitado "
                        f"'{raw_requested_state}' es inválido."
                    )
                }
            )

    else:
        destination_state = (
            ESTADO_TRANSITIONS.get(
                current_state
            )
        )

        if destination_state is None:
            raise ValidationError(
                {
                    "estado": (
                        "No existe una transición automática "
                        f"desde el estado '{current_state}'."
                    )
                }
            )

    if destination_state not in valid_states:
        raise ValidationError(
            {
                "estado": (
                    "El estado de destino calculado "
                    "no está definido en el modelo."
                )
            }
        )

    return destination_state


__all__ = [
    "PROYECTO_AUTOR_ROLES",
    "MAX_AUTORES_POR_PROYECTO",
    "ESTADO_TRANSITIONS",
    "LEGACY_ESTADO_MAP",
    "user_is_project_admin",
    "require_project_admin",
    "parse_autores_data_input",
    "normalize_proyecto_autores_payload",
    "autores_payload_tiene_principal",
    "proyecto_tiene_investigador_principal",
    "sync_proyecto_autores",
    "normalizar_estado",
    "resolver_estado_destino",
]