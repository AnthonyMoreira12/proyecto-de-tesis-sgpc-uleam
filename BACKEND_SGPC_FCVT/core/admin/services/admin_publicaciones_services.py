# Servicio administrativo para publicaciones delegadas:
# resuelve el usuario y autor objetivo, valida coherencia entre ambos y prepara el payload
# para crear publicaciones en nombre de otro usuario desde el módulo administrativo.

import json

from django.contrib.auth import get_user_model
from rest_framework import status

from core.autores.services.autores_usuario_sync_services import asegurar_autor_para_usuario
from core.models import Autor

User = get_user_model()


class AdminPublicacionesServiceError(Exception):
    def __init__(self, detail, status_code=status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def _safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def _safe_get_autor_for_user(usuario):
    if not usuario:
        return None

    try:
        return usuario.autor
    except Exception:
        return None


def _get_usuario_by_id(usuario_id):
    usuario_id = _safe_int(usuario_id)
    if not usuario_id:
        return None

    usuario = (
        User.objects.select_related("facultad", "carrera")
        .filter(pk=usuario_id)
        .first()
    )

    if not usuario:
        raise AdminPublicacionesServiceError(
            {"usuario_objetivo_id": "El usuario objetivo no existe."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return usuario


def _get_autor_by_id(autor_id):
    autor_id = _safe_int(autor_id)
    if not autor_id:
        return None

    autor = (
        Autor.objects.select_related("usuario")
        .filter(pk=autor_id)
        .first()
    )

    if not autor:
        raise AdminPublicacionesServiceError(
            {"autor_objetivo_id": "El autor objetivo no existe."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return autor


def _validate_usuario_objetivo(usuario):
    if not usuario:
        raise AdminPublicacionesServiceError(
            {"detail": "No se pudo resolver el usuario objetivo."}
        )

    if not getattr(usuario, "is_active", False):
        raise AdminPublicacionesServiceError(
            {"detail": "El usuario objetivo está inactivo."}
        )

    rol = str(getattr(usuario, "rol", "") or "").strip().lower()
    if rol not in {"autor", "autor_externo"}:
        raise AdminPublicacionesServiceError(
            {"detail": "El usuario objetivo no es válido para publicaciones."}
        )

    return usuario


def resolve_usuario_objetivo(*, usuario_id=None, autor_id=None):
    usuario = _get_usuario_by_id(usuario_id)
    autor = _get_autor_by_id(autor_id)

    if usuario is None and autor is None:
        raise AdminPublicacionesServiceError(
            {
                "detail": (
                    "Debe enviar 'usuario_objetivo_id' o 'autor_objetivo_id' "
                    "para crear publicaciones en modo delegado."
                )
            }
        )

    if usuario is not None and autor is not None:
        autor_usuario = getattr(autor, "usuario", None)

        if autor_usuario is None:
            raise AdminPublicacionesServiceError(
                {
                    "autor_objetivo_id": (
                        "El autor objetivo no está vinculado a un usuario del sistema."
                    )
                }
            )

        if getattr(autor_usuario, "id", None) != getattr(usuario, "id", None):
            raise AdminPublicacionesServiceError(
                {
                    "detail": (
                        "El usuario objetivo y el autor objetivo no son coherentes "
                        "entre sí."
                    )
                }
            )

        return _validate_usuario_objetivo(usuario)

    if usuario is not None:
        return _validate_usuario_objetivo(usuario)

    autor_usuario = getattr(autor, "usuario", None)

    if autor_usuario is None:
        raise AdminPublicacionesServiceError(
            {
                "autor_objetivo_id": (
                    "El autor objetivo no está vinculado a un usuario del sistema."
                )
            }
        )

    return _validate_usuario_objetivo(autor_usuario)


def ensure_autor_objetivo(usuario, *, autor_id=None):
    explicit_autor = _get_autor_by_id(autor_id)

    if explicit_autor is not None:
        explicit_usuario = getattr(explicit_autor, "usuario", None)

        if explicit_usuario is None:
            raise AdminPublicacionesServiceError(
                {
                    "autor_objetivo_id": (
                        "El autor objetivo no está vinculado a un usuario del sistema."
                    )
                }
            )

        if getattr(explicit_usuario, "id", None) != getattr(usuario, "id", None):
            raise AdminPublicacionesServiceError(
                {
                    "detail": (
                        "El autor objetivo no pertenece al usuario objetivo indicado."
                    )
                }
            )

        return explicit_autor

    autor = _safe_get_autor_for_user(usuario)

    if autor is None:
        try:
            posible_autor = asegurar_autor_para_usuario(usuario)
            if posible_autor is not None:
                autor = posible_autor
        except Exception:
            autor = None

    if autor is None:
        try:
            usuario.refresh_from_db()
        except Exception:
            pass

        autor = _safe_get_autor_for_user(usuario)

    if autor is None:
        raise AdminPublicacionesServiceError(
            {
                "detail": (
                    "No se pudo resolver o crear el autor asociado al usuario objetivo."
                )
            }
        )

    return autor


def _decode_autores_payload(raw_autores):
    if raw_autores in (None, "", "[]", "null", "None", [], {}):
        return []

    if isinstance(raw_autores, list):
        if len(raw_autores) == 1 and isinstance(raw_autores[0], str):
            raw_autores = raw_autores[0]
        elif len(raw_autores) == 1 and isinstance(raw_autores[0], list):
            return raw_autores[0]
        else:
            return raw_autores

    if isinstance(raw_autores, str):
        raw = raw_autores.strip()

        if raw in ("", "[]", "null", "None"):
            return []

        try:
            parsed = json.loads(raw)
        except Exception:
            raise AdminPublicacionesServiceError(
                {"autores": ["Formato inválido. Debe ser JSON válido."]}
            )

        if parsed is None:
            return []

        if not isinstance(parsed, list):
            raise AdminPublicacionesServiceError(
                {"autores": ["El campo 'autores' debe ser una lista."]}
            )

        return parsed

    raise AdminPublicacionesServiceError(
        {"autores": ["Formato inválido para el campo 'autores'."]}
    )


def _normalize_autores_for_admin(*, autores_payload, autor_objetivo):
    autores_list = _decode_autores_payload(autores_payload)

    seen = set()
    ordered_ids = []

    autor_objetivo_id = int(autor_objetivo.id)
    ordered_ids.append(autor_objetivo_id)
    seen.add(autor_objetivo_id)

    for item in autores_list:
        if not isinstance(item, dict):
            raise AdminPublicacionesServiceError(
                {"autores": ["Cada autor debe ser un objeto JSON."]}
            )

        autor_id = item.get("autor_id", item.get("autor"))
        autor_id = _safe_int(autor_id)

        if not autor_id:
            raise AdminPublicacionesServiceError(
                {"autores": ["Cada autor debe incluir 'autor_id' o 'autor'."]}
            )

        if autor_id in seen:
            continue

        ordered_ids.append(autor_id)
        seen.add(autor_id)

    autores_existentes = set(
        Autor.objects.filter(id__in=ordered_ids).values_list("id", flat=True)
    )
    faltantes = [autor_id for autor_id in ordered_ids if autor_id not in autores_existentes]

    if faltantes:
        raise AdminPublicacionesServiceError(
            {
                "autores": [
                    f"Autor(es) no existe(n): {', '.join(map(str, faltantes))}."
                ]
            }
        )

    normalized = []

    for index, autor_id in enumerate(ordered_ids, start=1):
        normalized.append(
            {
                "autor_id": autor_id,
                "orden": index,
                "rol_autoria": "principal" if index == 1 else "coautor",
            }
        )

    return normalized


def prepare_admin_publicacion_payload(*, raw_data):
    data = raw_data.copy() if hasattr(raw_data, "copy") else dict(raw_data)

    usuario_objetivo_id = (
        data.pop("usuario_objetivo_id", None)
        or data.pop("usuario_id", None)
    )

    autor_objetivo_id = (
        data.pop("autor_objetivo_id", None)
        or data.pop("autor_id_objetivo", None)
        or data.pop("autor_id", None)
    )

    usuario_objetivo = resolve_usuario_objetivo(
        usuario_id=usuario_objetivo_id,
        autor_id=autor_objetivo_id,
    )

    autor_objetivo = ensure_autor_objetivo(
        usuario_objetivo,
        autor_id=autor_objetivo_id,
    )

    data["autores"] = _normalize_autores_for_admin(
        autores_payload=data.get("autores"),
        autor_objetivo=autor_objetivo,
    )

    return data, usuario_objetivo, autor_objetivo