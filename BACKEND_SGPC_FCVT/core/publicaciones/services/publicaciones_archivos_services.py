import json

from rest_framework.exceptions import ValidationError

from core.models.publicaciones.archivos import (
    MAX_ADJUNTOS_POR_PUBLICACION,
)
from core.publicaciones.utils.publicaciones_archivos_utils import (
    default_nombre_from_file,
    validar_firma_pdf,
)


def extraer_archivos_request(
    request,
):
    """
    Extrae los adjuntos PDF desde multipart/form-data.

    Soporta los nombres:
    - files
    - archivos
    """

    request_files = getattr(
        request,
        "FILES",
        None,
    )

    if request_files is None:
        return []

    if hasattr(
        request_files,
        "getlist",
    ):
        files = (
            request_files.getlist(
                "files"
            )
            or request_files.getlist(
                "archivos"
            )
        )
    else:
        files = []

    return [
        file
        for file in files
        if file
    ]


def parse_meta_json(
    raw_meta,
):
    raw = str(
        raw_meta or ""
    ).strip()

    if not raw:
        return []

    try:
        parsed = json.loads(
            raw
        )
    except (
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        raise ValidationError(
            {
                "meta": [
                    "Formato inválido. "
                    "Debe ser JSON válido."
                ]
            }
        )

    if parsed is None:
        return []

    if not isinstance(
        parsed,
        list,
    ):
        raise ValidationError(
            {
                "meta": [
                    "Debe enviar una lista "
                    "JSON de adjuntos."
                ]
            }
        )

    return parsed


def _normalizar_nombre(
    value,
    uploaded_file,
):
    nombre = str(
        value or ""
    ).strip()

    if not nombre:
        nombre = (
            default_nombre_from_file(
                uploaded_file
            )
        )

    if len(nombre) > 150:
        raise ValidationError(
            {
                "meta": [
                    "El nombre de un adjunto "
                    "no puede superar 150 caracteres."
                ]
            }
        )

    return nombre


def procesar_adjuntos_payload(
    request,
    plain_data,
):
    """
    Prepara los adjuntos enviados junto con la creación
    de una publicación.

    Esta función no guarda archivos. Solo:

    - extrae;
    - valida;
    - normaliza;
    - empareja archivo/metadatos.
    """

    files = extraer_archivos_request(
        request
    )

    if not files:
        return []

    if (
        len(files)
        > MAX_ADJUNTOS_POR_PUBLICACION
    ):
        raise ValidationError(
            {
                "files": [
                    "Solo se permiten hasta "
                    f"{MAX_ADJUNTOS_POR_PUBLICACION} "
                    "archivos adjuntos por publicación."
                ]
            }
        )

    for index, uploaded_file in enumerate(
        files,
        start=1,
    ):
        try:
            validar_firma_pdf(
                uploaded_file
            )
        except ValidationError as exc:
            detail = exc.detail

            if isinstance(
                detail,
                list,
            ):
                message = str(
                    detail[0]
                )
            else:
                message = str(
                    detail
                )

            raise ValidationError(
                {
                    "files": [
                        f"Archivo #{index}: "
                        f"{message}"
                    ]
                }
            )

    raw_meta = (
        plain_data.get(
            "meta"
        )
        or plain_data.get(
            "archivos_meta"
        )
        or ""
    )

    meta_list = parse_meta_json(
        raw_meta
    )

    if (
        meta_list
        and len(meta_list)
        != len(files)
    ):
        raise ValidationError(
            {
                "meta": [
                    "La cantidad de metadatos "
                    "debe coincidir con la cantidad "
                    "de archivos adjuntos."
                ]
            }
        )

    normalized = []

    for index, uploaded_file in enumerate(
        files,
        start=1,
    ):
        item = (
            meta_list[index - 1]
            if meta_list
            else {}
        )

        if not isinstance(
            item,
            dict,
        ):
            raise ValidationError(
                {
                    "meta": [
                        f"El adjunto #{index} "
                        "debe ser un objeto JSON."
                    ]
                }
            )

        nombre = _normalizar_nombre(
            item.get(
                "nombre"
            ),
            uploaded_file,
        )

        orden = item.get(
            "orden"
        )

        if orden in (
            None,
            "",
            0,
            "0",
        ):
            orden = index

        try:
            orden = int(
                orden
            )
        except (
            TypeError,
            ValueError,
        ):
            raise ValidationError(
                {
                    "meta": [
                        f"El orden del adjunto "
                        f"#{index} debe ser numérico."
                    ]
                }
            )

        if orden < 1:
            raise ValidationError(
                {
                    "meta": [
                        f"El orden del adjunto "
                        f"#{index} debe ser mayor "
                        "o igual a 1."
                    ]
                }
            )

        normalized.append(
            {
                "file": uploaded_file,
                "nombre": nombre,
                "orden": orden,
            }
        )

    ordenes = [
        item["orden"]
        for item in normalized
    ]

    if (
        len(ordenes)
        != len(set(ordenes))
    ):
        raise ValidationError(
            {
                "meta": [
                    "No se permite repetir "
                    "el orden de los adjuntos."
                ]
            }
        )

    # Se conserva la asociación original entre
    # cada archivo y sus metadatos.
    return normalized