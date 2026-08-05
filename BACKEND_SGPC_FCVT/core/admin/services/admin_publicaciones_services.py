"""Servicios para publicaciones administrativas delegadas."""

import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from core.utils.files import (
    normalize_optional_text,
    validate_pdf_file,
)


User = get_user_model()


MAX_ATTACHMENT_BYTES = 3 * 1024 * 1024
MAX_ATTACHMENTS_PER_PUBLICATION = 2


ATTACHMENT_FILE_KEYS = (
    "files",
    "files[]",
    "adjuntos",
    "adjuntos[]",
    "archivos",
    "archivos[]",
)


ATTACHMENT_META_KEYS = (
    "meta",
    "archivos_meta",
    "nombres_adjuntos",
)


class AdminPublicacionesServiceError(
    Exception
):
    def __init__(
        self,
        detail,
        *,
        status_code=400,
    ):
        self.detail = detail
        self.status_code = status_code

        super().__init__(
            str(detail)
        )


def _positive_int(
    value,
    *,
    field,
):
    if isinstance(
        value,
        bool,
    ):
        raise AdminPublicacionesServiceError(
            {
                field: (
                    "El identificador debe ser "
                    "un entero positivo."
                )
            }
        )

    try:
        parsed = int(
            value
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise AdminPublicacionesServiceError(
            {
                field: (
                    "El identificador debe ser "
                    "un entero positivo."
                )
            }
        ) from exc

    if parsed <= 0:
        raise AdminPublicacionesServiceError(
            {
                field: (
                    "El identificador debe ser "
                    "mayor que cero."
                )
            }
        )

    return parsed


def _plain_data(
    source,
):
    """
    Convierte QueryDict o diccionarios similares en un
    diccionario convencional sin perder valores múltiples.
    """
    output = {}

    if hasattr(
        source,
        "lists",
    ):
        for key, values in source.lists():
            output[key] = (
                values[0]
                if len(values) == 1
                else list(values)
            )

    else:
        output.update(
            dict(source)
        )

    return output


def _parse_json_list(
    value,
    *,
    field,
):
    """
    Convierte una cadena JSON o una lista en una lista Python.
    """
    if value in (
        None,
        "",
        "[]",
        [],
        "null",
        "None",
    ):
        return []

    if isinstance(
        value,
        str,
    ):
        try:
            value = json.loads(
                value
            )

        except json.JSONDecodeError as exc:
            raise AdminPublicacionesServiceError(
                {
                    field: (
                        f"El campo {field} "
                        "debe ser JSON válido."
                    )
                }
            ) from exc

    if not isinstance(
        value,
        list,
    ):
        raise AdminPublicacionesServiceError(
            {
                field: (
                    f"El campo {field} "
                    "debe ser una lista."
                )
            }
        )

    return value


def _parse_authors(
    value,
):
    return _parse_json_list(
        value,
        field="autores",
    )


def _target_user(
    data,
):
    """
    Obtiene el usuario para quien el administrador registrará
    la publicación.
    """
    raw_id = (
        data.get(
            "usuario_objetivo_id"
        )
        or data.get(
            "usuario_id"
        )
    )

    if raw_id in (
        None,
        "",
    ):
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
            .select_related(
                "carrera__facultad",
                "autor",
            )
            .get(
                pk=user_id
            )
        )

    except User.DoesNotExist as exc:
        raise AdminPublicacionesServiceError(
            {
                "usuario_objetivo_id": (
                    "El usuario no existe."
                )
            },
            status_code=404,
        ) from exc


def _target_author(
    data,
    user,
):
    """
    Obtiene el Autor vinculado al usuario objetivo.

    El autor recibido desde el frontend debe corresponder
    exactamente al Autor asociado al Usuario.
    """
    try:
        linked_author = user.autor

    except ObjectDoesNotExist:
        linked_author = None

    if linked_author is None:
        raise AdminPublicacionesServiceError(
            {
                "autor_objetivo_id": (
                    "El usuario seleccionado no tiene un "
                    "autor vinculado."
                )
            }
        )

    raw_id = (
        data.get(
            "autor_objetivo_id"
        )
        or data.get(
            "autor_id"
        )
        or linked_author.pk
    )

    author_id = _positive_int(
        raw_id,
        field="autor_objetivo_id",
    )

    if author_id != linked_author.pk:
        raise AdminPublicacionesServiceError(
            {
                "autor_objetivo_id": (
                    "El autor seleccionado no corresponde "
                    "al usuario objetivo."
                )
            }
        )

    return linked_author


def _collect_uploaded_files(
    request,
):
    """
    Recupera adjuntos enviados con cualquiera de los nombres
    aceptados por el frontend y elimina referencias repetidas.
    """
    files = []

    if not hasattr(
        request.FILES,
        "getlist",
    ):
        return files

    for key in ATTACHMENT_FILE_KEYS:
        files.extend(
            request.FILES.getlist(
                key
            )
        )

    unique_files = []
    seen = set()

    for uploaded in files:
        identity = id(
            uploaded
        )

        if identity in seen:
            continue

        seen.add(
            identity
        )

        unique_files.append(
            uploaded
        )

    return unique_files


def _attachment_metadata(
    request,
):
    """
    Normaliza los metadatos asociados a los adjuntos.

    Formatos permitidos:

    - Lista de textos.
    - Lista de objetos con nombre y orden.
    """
    raw_value = None
    source_key = "meta"

    for key in ATTACHMENT_META_KEYS:
        candidate = request.data.get(
            key
        )

        if candidate not in (
            None,
            "",
            [],
            "null",
            "None",
        ):
            raw_value = candidate
            source_key = key
            break

    metadata = _parse_json_list(
        raw_value,
        field=source_key,
    )

    normalized = []

    for index, item in enumerate(
        metadata,
        start=1,
    ):
        if isinstance(
            item,
            str,
        ):
            normalized.append(
                {
                    "nombre": (
                        normalize_optional_text(
                            item
                        )
                    ),
                    "orden": index,
                }
            )

            continue

        if not isinstance(
            item,
            dict,
        ):
            raise AdminPublicacionesServiceError(
                {
                    source_key: (
                        f"El elemento #{index} de los "
                        "metadatos debe ser un objeto "
                        "o un texto."
                    )
                }
            )

        order_value = item.get(
            "orden",
            index,
        )

        order = _positive_int(
            order_value,
            field=(
                f"{source_key}"
                f"[{index}].orden"
            ),
        )

        normalized.append(
            {
                "nombre": (
                    normalize_optional_text(
                        item.get(
                            "nombre"
                        )
                        or item.get(
                            "name"
                        )
                    )
                ),
                "orden": order,
            }
        )

    return normalized


def _attachments(
    request,
):
    """
    Valida y prepara los archivos adjuntos.

    Reglas:

    - Máximo dos archivos.
    - Solo PDF.
    - Máximo 3 MB por archivo.
    - El número de metadatos debe coincidir con el número de
      archivos.
    - El orden no puede repetirse.
    """
    uploaded_files = (
        _collect_uploaded_files(
            request
        )
    )

    if (
        len(uploaded_files)
        > MAX_ATTACHMENTS_PER_PUBLICATION
    ):
        raise AdminPublicacionesServiceError(
            {
                "adjuntos": (
                    "Solo se permiten hasta "
                    f"{MAX_ATTACHMENTS_PER_PUBLICATION} "
                    "archivos adjuntos por publicación."
                )
            }
        )

    metadata = _attachment_metadata(
        request
    )

    if (
        metadata
        and len(metadata)
        != len(uploaded_files)
    ):
        raise AdminPublicacionesServiceError(
            {
                "meta": (
                    "La cantidad de metadatos debe coincidir "
                    "con la cantidad de archivos adjuntos."
                )
            }
        )

    output = []
    used_orders = set()

    for index, uploaded in enumerate(
        uploaded_files,
        start=1,
    ):
        validate_pdf_file(
            uploaded,
            max_bytes=(
                MAX_ATTACHMENT_BYTES
            ),
            field_name="adjuntos",
            label=(
                f"El adjunto #{index}"
            ),
        )

        item_meta = (
            metadata[index - 1]
            if (
                index - 1
                < len(metadata)
            )
            else {}
        )

        order = item_meta.get(
            "orden",
            index,
        )

        if order in used_orders:
            raise AdminPublicacionesServiceError(
                {
                    "meta": (
                        "El orden de los archivos adjuntos "
                        "no puede repetirse."
                    )
                }
            )

        used_orders.add(
            order
        )

        name = (
            normalize_optional_text(
                item_meta.get(
                    "nombre"
                )
            )
            or normalize_optional_text(
                getattr(
                    uploaded,
                    "name",
                    None,
                )
            )
            or f"Adjunto {index}"
        )

        output.append(
            {
                "file": uploaded,
                "nombre": name,
                "orden": order,
            }
        )

    return sorted(
        output,
        key=lambda item: item[
            "orden"
        ],
    )


def _remove_control_fields(
    data,
):
    """
    Elimina campos administrativos y auxiliares que no forman
    parte de los serializers normales de publicaciones.
    """
    for key in (
        "facultad",
        "usuario_objetivo_id",
        "usuario_id",
        "autor_objetivo_id",
        "autor_id",
        *ATTACHMENT_FILE_KEYS,
        *ATTACHMENT_META_KEYS,
    ):
        data.pop(
            key,
            None,
        )


def _normalize_authors(
    raw_authors,
    target_author,
):
    """
    Garantiza que el Autor vinculado al usuario objetivo sea el
    autor principal y ocupe el orden uno.
    """
    normalized = [
        {
            "autor_id": (
                target_author.pk
            ),
            "orden": 1,
            "rol_autoria": (
                "principal"
            ),
        }
    ]

    seen_ids = {
        target_author.pk
    }

    for index, item in enumerate(
        raw_authors,
        start=1,
    ):
        if not isinstance(
            item,
            dict,
        ):
            raise AdminPublicacionesServiceError(
                {
                    "autores": (
                        f"El autor #{index} debe enviarse "
                        "como un objeto."
                    )
                }
            )

        raw_id = (
            item.get(
                "autor_id"
            )
            or item.get(
                "autor"
            )
            or item.get(
                "id"
            )
        )

        item_id = _positive_int(
            raw_id,
            field=(
                f"autores[{index}]"
                ".autor_id"
            ),
        )

        if item_id in seen_ids:
            continue

        seen_ids.add(
            item_id
        )

        normalized.append(
            {
                "autor_id": item_id,
                "orden": (
                    len(normalized)
                    + 1
                ),
                "rol_autoria": (
                    "coautor"
                ),
            }
        )

    return normalized


@transaction.atomic
def prepare_admin_publicacion_payload(
    *,
    request,
):
    """
    Prepara el contenido necesario para registrar una
    publicación administrativa delegada.

    Retorna:

    - Datos limpios para el serializer.
    - Usuario objetivo.
    - Autor objetivo.
    - Adjuntos validados.
    """
    data = _plain_data(
        request.data
    )

    user = _target_user(
        data
    )

    author = _target_author(
        data,
        user,
    )

    if not user.is_active:
        raise AdminPublicacionesServiceError(
            {
                "usuario_objetivo_id": (
                    "El usuario seleccionado está inactivo."
                )
            }
        )

    if (
        not data.get(
            "carrera"
        )
        and user.carrera_id
    ):
        data["carrera"] = (
            user.carrera_id
        )

    raw_authors = _parse_authors(
        data.get(
            "autores"
        )
    )

    attachments = _attachments(
        request
    )

    _remove_control_fields(
        data
    )

    data["autores"] = json.dumps(
        _normalize_authors(
            raw_authors,
            author,
        )
    )

    return {
        "data": data,
        "usuario_objetivo": user,
        "autor_objetivo": author,
        "adjuntos": attachments,
    }

"""Servicios para publicaciones administrativas delegadas."""

import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from core.utils.files import (
    normalize_optional_text,
    validate_pdf_file,
)


User = get_user_model()


MAX_ATTACHMENT_BYTES = 3 * 1024 * 1024
MAX_ATTACHMENTS_PER_PUBLICATION = 2
MAX_ATTACHMENT_NAME_LENGTH = 150


ATTACHMENT_FILE_KEYS = (
    "files",
    "files[]",
    "adjuntos",
    "adjuntos[]",
    "archivos",
    "archivos[]",
)


ATTACHMENT_META_KEYS = (
    "meta",
    "archivos_meta",
    "nombres_adjuntos",
)


class AdminPublicacionesServiceError(
    Exception
):
    def __init__(
        self,
        detail,
        *,
        status_code=400,
    ):
        self.detail = detail
        self.status_code = status_code

        super().__init__(
            str(detail)
        )


def _positive_int(
    value,
    *,
    field,
):
    if isinstance(
        value,
        bool,
    ):
        raise AdminPublicacionesServiceError(
            {
                field: (
                    "El identificador debe ser "
                    "un entero positivo."
                )
            }
        )

    try:
        parsed = int(
            value
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise AdminPublicacionesServiceError(
            {
                field: (
                    "El identificador debe ser "
                    "un entero positivo."
                )
            }
        ) from exc

    if parsed <= 0:
        raise AdminPublicacionesServiceError(
            {
                field: (
                    "El identificador debe ser "
                    "mayor que cero."
                )
            }
        )

    return parsed


def _plain_data(
    source,
):
    """
    Convierte QueryDict o diccionarios similares en un
    diccionario convencional sin perder valores múltiples.
    """
    output = {}

    if hasattr(
        source,
        "lists",
    ):
        for key, values in source.lists():
            output[key] = (
                values[0]
                if len(values) == 1
                else list(values)
            )

    else:
        output.update(
            dict(source)
        )

    return output


def _parse_json_list(
    value,
    *,
    field,
):
    """
    Convierte una cadena JSON o una lista en una lista Python.
    """
    if value in (
        None,
        "",
        "[]",
        [],
        "null",
        "None",
    ):
        return []

    if isinstance(
        value,
        str,
    ):
        try:
            value = json.loads(
                value
            )

        except json.JSONDecodeError as exc:
            raise AdminPublicacionesServiceError(
                {
                    field: (
                        f"El campo {field} "
                        "debe ser JSON válido."
                    )
                }
            ) from exc

    if not isinstance(
        value,
        list,
    ):
        raise AdminPublicacionesServiceError(
            {
                field: (
                    f"El campo {field} "
                    "debe ser una lista."
                )
            }
        )

    return value


def _parse_authors(
    value,
):
    return _parse_json_list(
        value,
        field="autores",
    )


def _is_pending_external_user(
    user,
):
    """
    Determina si el usuario corresponde a una cuenta externa
    local pendiente de activación.

    Una cuenta desactivada que ya tiene contraseña utilizable
    no se considera pendiente y no puede utilizarse como
    usuario objetivo de una creación delegada.
    """
    if user is None:
        return False

    role = str(
        getattr(
            user,
            "rol",
            "",
        )
        or ""
    ).strip().lower()

    auth_source = str(
        getattr(
            user,
            "auth_source",
            "",
        )
        or ""
    ).strip().lower()

    if (
        role != "autor_externo"
        or auth_source != "local"
        or bool(
            getattr(
                user,
                "is_active",
                False,
            )
        )
    ):
        return False

    try:
        return not user.has_usable_password()

    except (
        AttributeError,
        TypeError,
        ValueError,
    ):
        return False


def _target_user(
    data,
):
    """
    Obtiene el usuario para quien el administrador registrará
    la publicación.
    """
    raw_id = (
        data.get(
            "usuario_objetivo_id"
        )
        or data.get(
            "usuario_id"
        )
    )

    if raw_id in (
        None,
        "",
    ):
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
            .select_related(
                "carrera__facultad",
                "autor",
            )
            .get(
                pk=user_id
            )
        )

    except User.DoesNotExist as exc:
        raise AdminPublicacionesServiceError(
            {
                "usuario_objetivo_id": (
                    "El usuario no existe."
                )
            },
            status_code=404,
        ) from exc


def _target_author(
    data,
    user,
):
    """
    Obtiene el Autor vinculado al usuario objetivo.

    El autor recibido desde el frontend debe corresponder
    exactamente al Autor asociado al Usuario.
    """
    try:
        linked_author = user.autor

    except ObjectDoesNotExist:
        linked_author = None

    if linked_author is None:
        raise AdminPublicacionesServiceError(
            {
                "autor_objetivo_id": (
                    "El usuario seleccionado no tiene un "
                    "autor vinculado."
                )
            }
        )

    raw_id = (
        data.get(
            "autor_objetivo_id"
        )
        or data.get(
            "autor_id"
        )
        or linked_author.pk
    )

    author_id = _positive_int(
        raw_id,
        field="autor_objetivo_id",
    )

    if author_id != linked_author.pk:
        raise AdminPublicacionesServiceError(
            {
                "autor_objetivo_id": (
                    "El autor seleccionado no corresponde "
                    "al usuario objetivo."
                )
            }
        )

    return linked_author


def _collect_uploaded_files(
    request,
):
    """
    Recupera adjuntos enviados con cualquiera de los nombres
    aceptados por el frontend y elimina referencias repetidas.
    """
    files = []

    if not hasattr(
        request.FILES,
        "getlist",
    ):
        return files

    for key in ATTACHMENT_FILE_KEYS:
        files.extend(
            request.FILES.getlist(
                key
            )
        )

    unique_files = []
    seen = set()

    for uploaded in files:
        identity = id(
            uploaded
        )

        if identity in seen:
            continue

        seen.add(
            identity
        )

        unique_files.append(
            uploaded
        )

    return unique_files


def _attachment_metadata(
    request,
):
    """
    Normaliza los metadatos asociados a los adjuntos.

    Formatos permitidos:

    - Lista de textos.
    - Lista de objetos con nombre y orden.
    """
    raw_value = None
    source_key = "meta"

    for key in ATTACHMENT_META_KEYS:
        candidate = request.data.get(
            key
        )

        if candidate not in (
            None,
            "",
            [],
            "null",
            "None",
        ):
            raw_value = candidate
            source_key = key
            break

    metadata = _parse_json_list(
        raw_value,
        field=source_key,
    )

    normalized = []

    for index, item in enumerate(
        metadata,
        start=1,
    ):
        if isinstance(
            item,
            str,
        ):
            normalized.append(
                {
                    "nombre": (
                        normalize_optional_text(
                            item
                        )
                    ),
                    "orden": index,
                }
            )

            continue

        if not isinstance(
            item,
            dict,
        ):
            raise AdminPublicacionesServiceError(
                {
                    source_key: (
                        f"El elemento #{index} de los "
                        "metadatos debe ser un objeto "
                        "o un texto."
                    )
                }
            )

        order_value = item.get(
            "orden",
            index,
        )

        order = _positive_int(
            order_value,
            field=(
                f"{source_key}"
                f"[{index}].orden"
            ),
        )

        normalized.append(
            {
                "nombre": (
                    normalize_optional_text(
                        item.get(
                            "nombre"
                        )
                        or item.get(
                            "name"
                        )
                    )
                ),
                "orden": order,
            }
        )

    return normalized


def _attachments(
    request,
):
    """
    Valida y prepara los archivos adjuntos.

    Reglas:

    - Máximo dos archivos.
    - Solo PDF.
    - Máximo 3 MB por archivo.
    - El número de metadatos debe coincidir con el número de
      archivos.
    - El orden no puede repetirse.
    """
    uploaded_files = (
        _collect_uploaded_files(
            request
        )
    )

    if (
        len(uploaded_files)
        > MAX_ATTACHMENTS_PER_PUBLICATION
    ):
        raise AdminPublicacionesServiceError(
            {
                "adjuntos": (
                    "Solo se permiten hasta "
                    f"{MAX_ATTACHMENTS_PER_PUBLICATION} "
                    "archivos adjuntos por publicación."
                )
            }
        )

    metadata = _attachment_metadata(
        request
    )

    if (
        metadata
        and len(metadata)
        != len(uploaded_files)
    ):
        raise AdminPublicacionesServiceError(
            {
                "meta": (
                    "La cantidad de metadatos debe coincidir "
                    "con la cantidad de archivos adjuntos."
                )
            }
        )

    output = []
    used_orders = set()

    for index, uploaded in enumerate(
        uploaded_files,
        start=1,
    ):
        validate_pdf_file(
            uploaded,
            max_bytes=(
                MAX_ATTACHMENT_BYTES
            ),
            field_name="adjuntos",
            label=(
                f"El adjunto #{index}"
            ),
        )

        item_meta = (
            metadata[index - 1]
            if (
                index - 1
                < len(metadata)
            )
            else {}
        )

        order = item_meta.get(
            "orden",
            index,
        )

        if order in used_orders:
            raise AdminPublicacionesServiceError(
                {
                    "meta": (
                        "El orden de los archivos adjuntos "
                        "no puede repetirse."
                    )
                }
            )

        used_orders.add(
            order
        )

        name = (
            normalize_optional_text(
                item_meta.get(
                    "nombre"
                )
            )
            or normalize_optional_text(
                getattr(
                    uploaded,
                    "name",
                    None,
                )
            )
            or f"Adjunto {index}"
        )

        if (
            len(name)
            > MAX_ATTACHMENT_NAME_LENGTH
        ):
            raise AdminPublicacionesServiceError(
                {
                    "meta": (
                        f"El nombre del adjunto #{index} "
                        "no puede superar "
                        f"{MAX_ATTACHMENT_NAME_LENGTH} "
                        "caracteres."
                    )
                }
            )

        output.append(
            {
                "file": uploaded,
                "nombre": name,
                "orden": order,
            }
        )

    return sorted(
        output,
        key=lambda item: item[
            "orden"
        ],
    )


def _remove_control_fields(
    data,
    *,
    preserve_facultad=False,
):
    """
    Elimina campos administrativos y auxiliares que no forman
    parte de los serializers normales de publicaciones.

    Artículo, Libro y Capítulo de Libro reciben ``facultad``
    para validar la relación Facultad -> Carrera. Ponencia la
    deriva directamente desde Carrera y no declara ese campo.
    """
    control_fields = [
        "usuario_objetivo_id",
        "usuario_id",
        "autor_objetivo_id",
        "autor_id",
        *ATTACHMENT_FILE_KEYS,
        *ATTACHMENT_META_KEYS,
    ]

    if not preserve_facultad:
        control_fields.append(
            "facultad"
        )

    for key in control_fields:
        data.pop(
            key,
            None,
        )


def _normalize_authors(
    raw_authors,
    target_author,
):
    """
    Garantiza que el Autor vinculado al usuario objetivo sea el
    autor principal y ocupe el orden uno.
    """
    normalized = [
        {
            "autor_id": (
                target_author.pk
            ),
            "orden": 1,
            "rol_autoria": (
                "principal"
            ),
        }
    ]

    seen_ids = {
        target_author.pk
    }

    for index, item in enumerate(
        raw_authors,
        start=1,
    ):
        if not isinstance(
            item,
            dict,
        ):
            raise AdminPublicacionesServiceError(
                {
                    "autores": (
                        f"El autor #{index} debe enviarse "
                        "como un objeto."
                    )
                }
            )

        raw_id = (
            item.get(
                "autor_id"
            )
            or item.get(
                "autor"
            )
            or item.get(
                "id"
            )
        )

        item_id = _positive_int(
            raw_id,
            field=(
                f"autores[{index}]"
                ".autor_id"
            ),
        )

        if item_id in seen_ids:
            continue

        seen_ids.add(
            item_id
        )

        normalized.append(
            {
                "autor_id": item_id,
                "orden": (
                    len(normalized)
                    + 1
                ),
                "rol_autoria": (
                    "coautor"
                ),
            }
        )

    return normalized


@transaction.atomic
def prepare_admin_publicacion_payload(
    *,
    request,
    preserve_facultad=False,
):
    """
    Prepara el contenido necesario para registrar una
    publicación administrativa delegada.

    Retorna:

    - Datos limpios para el serializer.
    - Usuario objetivo.
    - Autor objetivo.
    - Adjuntos validados.
    """
    data = _plain_data(
        request.data
    )

    user = _target_user(
        data
    )

    author = _target_author(
        data,
        user,
    )

    pending_external = (
        _is_pending_external_user(
            user
        )
    )

    if (
        not user.is_active
        and not pending_external
    ):
        raise AdminPublicacionesServiceError(
            {
                "usuario_objetivo_id": (
                    "El usuario seleccionado está inactivo "
                    "y no corresponde a una cuenta externa "
                    "pendiente de activación."
                )
            }
        )

    if (
        not data.get(
            "carrera"
        )
        and user.carrera_id
    ):
        data["carrera"] = (
            user.carrera_id
        )

    raw_authors = _parse_authors(
        data.get(
            "autores"
        )
    )

    attachments = _attachments(
        request
    )

    _remove_control_fields(
        data,
        preserve_facultad=(
            preserve_facultad
        ),
    )

    data["autores"] = json.dumps(
        _normalize_authors(
            raw_authors,
            author,
        )
    )

    return {
        "data": data,
        "usuario_objetivo": user,
        "autor_objetivo": author,
        "adjuntos": attachments,
        "permitir_usuario_inactivo_delegado": (
            pending_external
        ),
    }