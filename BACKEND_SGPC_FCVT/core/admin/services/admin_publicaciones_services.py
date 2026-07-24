"""Servicios para publicaciones administrativas delegadas."""

import json

from django.contrib.auth import get_user_model
from django.db import transaction

from core.models import Autor
from core.utils.files import normalize_optional_text, validate_pdf_file


User = get_user_model()
MAX_ATTACHMENT_BYTES = 3 * 1024 * 1024


class AdminPublicacionesServiceError(Exception):
    def __init__(self, detail, *, status_code=400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(str(detail))


def _positive_int(value, *, field):
    if isinstance(value, bool):
        raise AdminPublicacionesServiceError(
            {field: "El identificador debe ser un entero positivo."}
        )

    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise AdminPublicacionesServiceError(
            {field: "El identificador debe ser un entero positivo."}
        ) from exc

    if parsed <= 0:
        raise AdminPublicacionesServiceError(
            {field: "El identificador debe ser mayor que cero."}
        )

    return parsed


def _plain_data(source):
    output = {}

    if hasattr(source, "lists"):
        for key, values in source.lists():
            output[key] = (
                values[0]
                if len(values) == 1
                else list(values)
            )
    else:
        output.update(dict(source))

    return output


def _parse_authors(value):
    if value in (None, "", "[]", [], "null", "None"):
        return []

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise AdminPublicacionesServiceError(
                {"autores": "El campo autores debe ser JSON válido."}
            ) from exc

    if not isinstance(value, list):
        raise AdminPublicacionesServiceError(
            {"autores": "El campo autores debe ser una lista."}
        )

    return value


def _target_user(data):
    raw_id = (
        data.get("usuario_objetivo_id")
        or data.get("usuario_id")
    )

    if raw_id in (None, ""):
        raise AdminPublicacionesServiceError(
            {
                "usuario_objetivo_id": (
                    "Debe seleccionar el usuario para quien "
                    "se registrará la publicación."
                )
            }
        )

    user_id = _positive_int(
        raw_id,
        field="usuario_objetivo_id",
    )

    try:
        return (
            User.objects
            .select_related("carrera__facultad", "autor")
            .get(pk=user_id)
        )
    except User.DoesNotExist as exc:
        raise AdminPublicacionesServiceError(
            {"usuario_objetivo_id": "El usuario no existe."},
            status_code=404,
        ) from exc


def _target_author(data, user):
    raw_id = (
        data.get("autor_objetivo_id")
        or data.get("autor_id")
        or getattr(getattr(user, "autor", None), "pk", None)
    )

    if raw_id in (None, ""):
        raise AdminPublicacionesServiceError(
            {
                "autor_objetivo_id": (
                    "El usuario seleccionado no tiene un "
                    "autor vinculado."
                )
            }
        )

    author_id = _positive_int(
        raw_id,
        field="autor_objetivo_id",
    )

    try:
        author = Autor.objects.select_related("usuario").get(
            pk=author_id
        )
    except Autor.DoesNotExist as exc:
        raise AdminPublicacionesServiceError(
            {"autor_objetivo_id": "El autor no existe."},
            status_code=404,
        ) from exc

    if author.usuario_id not in (None, user.pk):
        raise AdminPublicacionesServiceError(
            {
                "autor_objetivo_id": (
                    "El autor seleccionado pertenece a "
                    "otro usuario."
                )
            }
        )

    return author


def _attachments(request):
    files = []

    for key in (
        "adjuntos",
        "adjuntos[]",
        "archivos",
        "archivos[]",
    ):
        if hasattr(request.FILES, "getlist"):
            files.extend(request.FILES.getlist(key))

    unique_files = []
    seen = set()

    for uploaded in files:
        identity = id(uploaded)

        if identity in seen:
            continue

        seen.add(identity)
        unique_files.append(uploaded)

    names = request.data.get("nombres_adjuntos")

    if isinstance(names, str):
        try:
            names = json.loads(names)
        except json.JSONDecodeError:
            names = []

    names = names if isinstance(names, list) else []
    output = []

    for index, uploaded in enumerate(unique_files, start=1):
        validate_pdf_file(
            uploaded,
            max_bytes=MAX_ATTACHMENT_BYTES,
            field_name="adjuntos",
            label=f"El adjunto #{index}",
        )

        name = (
            normalize_optional_text(
                names[index - 1]
                if index - 1 < len(names)
                else None
            )
            or normalize_optional_text(
                getattr(uploaded, "name", None)
            )
            or f"Adjunto {index}"
        )

        output.append(
            {
                "file": uploaded,
                "nombre": name,
                "orden": index,
            }
        )

    return output


@transaction.atomic
def prepare_admin_publicacion_payload(*, request):
    data = _plain_data(request.data)
    user = _target_user(data)
    author = _target_author(data, user)

    if not user.is_active:
        raise AdminPublicacionesServiceError(
            {
                "usuario_objetivo_id": (
                    "El usuario seleccionado está inactivo."
                )
            }
        )

    if not data.get("carrera") and user.carrera_id:
        data["carrera"] = user.carrera_id

    for key in (
        "facultad",
        "usuario_objetivo_id",
        "usuario_id",
        "autor_objetivo_id",
        "autor_id",
    ):
        data.pop(key, None)

    authors = _parse_authors(data.get("autores"))
    normalized = [
        {
            "autor_id": author.pk,
            "orden": 1,
            "rol_autoria": "principal",
        }
    ]
    seen_ids = {author.pk}

    for item in authors:
        try:
            item_id = int(item.get("autor_id"))
        except (TypeError, ValueError, AttributeError):
            continue

        if item_id in seen_ids:
            continue

        seen_ids.add(item_id)
        normalized.append(
            {
                "autor_id": item_id,
                "orden": len(normalized) + 1,
                "rol_autoria": "coautor",
            }
        )

    data["autores"] = json.dumps(normalized)

    return {
        "data": data,
        "usuario_objetivo": user,
        "autor_objetivo": author,
        "adjuntos": _attachments(request),
    }
