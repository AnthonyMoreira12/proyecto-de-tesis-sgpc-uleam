import os

from rest_framework.exceptions import ValidationError

from core.models.publicaciones.archivos import (
    MAX_ADJUNTO_PDF_BYTES,
)
from core.utils.files import validate_pdf_file


MAX_ATTACHMENT_NAME_LENGTH = 150


def validar_firma_pdf(uploaded_file):
    """
    Mantiene el nombre histórico de la utilidad, pero aplica la
    validación PDF reforzada y compartida por todo el backend.
    """

    try:
        return validate_pdf_file(
            uploaded_file,
            max_bytes=MAX_ADJUNTO_PDF_BYTES,
            field_name="archivo",
            label="El archivo adjunto",
        )

    except ValidationError as exc:
        detail = exc.detail

        if isinstance(detail, dict):
            detail = detail.get(
                "archivo",
                detail,
            )

        if isinstance(detail, (list, tuple)):
            detail = detail[0] if detail else (
                "El archivo adjunto no es un PDF válido."
            )

        raise ValidationError(
            str(detail)
        ) from exc


def default_nombre_from_file(uploaded_file):
    """Genera el nombre visible del adjunto desde el archivo original."""

    raw_name = str(
        getattr(
            uploaded_file,
            "name",
            "",
        )
        or ""
    ).strip()

    if not raw_name:
        return "Archivo PDF"

    raw_name = os.path.basename(
        raw_name
    )

    base, _extension = os.path.splitext(
        raw_name
    )

    resolved = str(
        base
        or raw_name
        or "Archivo PDF"
    ).strip()

    return resolved[:MAX_ATTACHMENT_NAME_LENGTH]
