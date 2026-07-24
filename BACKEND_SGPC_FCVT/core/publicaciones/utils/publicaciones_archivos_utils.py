import os

from rest_framework.exceptions import ValidationError


PDF_SIGNATURE = b"%PDF-"
PDF_SIGNATURE_SCAN_BYTES = 1024
MAX_ATTACHMENT_NAME_LENGTH = 150


def _read_prefix(
    uploaded_file,
    max_bytes=PDF_SIGNATURE_SCAN_BYTES,
):
    if not uploaded_file:
        return b""

    file_obj = getattr(
        uploaded_file,
        "file",
        uploaded_file,
    )

    if (
        file_obj is None
        or not hasattr(file_obj, "read")
    ):
        return b""

    original_position = 0

    try:
        if hasattr(file_obj, "tell"):
            original_position = file_obj.tell()
    except (OSError, ValueError):
        original_position = 0

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        content = file_obj.read(max_bytes)

        if isinstance(content, str):
            content = content.encode(
                "utf-8",
                errors="ignore",
            )

        return bytes(content or b"")

    except (OSError, ValueError, TypeError):
        return b""

    finally:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(original_position)
        except (OSError, ValueError):
            pass


def validar_firma_pdf(uploaded_file):
    """
    Comprueba que la firma real de PDF (%PDF-) aparezca
    dentro de los primeros 1024 bytes.

    Esto mantiene la comprobación de contenido sin exigir
    que la cabecera se encuentre exactamente en el byte 0.
    """

    if not uploaded_file:
        raise ValidationError(
            "No se proporcionó ningún archivo."
        )

    prefix = _read_prefix(
        uploaded_file,
        max_bytes=PDF_SIGNATURE_SCAN_BYTES,
    )

    if not prefix or PDF_SIGNATURE not in prefix:
        raise ValidationError(
            "El archivo adjunto no contiene "
            "una firma PDF válida."
        )

    return uploaded_file


def default_nombre_from_file(uploaded_file):
    """
    Genera un nombre válido para PublicacionArchivo.nombre
    a partir del nombre original del archivo.
    """

    raw_name = str(
        getattr(uploaded_file, "name", "")
        or ""
    ).strip()

    if not raw_name:
        return "Archivo PDF"

    raw_name = os.path.basename(raw_name)
    base, _ext = os.path.splitext(raw_name)
    resolved = str(base or raw_name or "Archivo PDF").strip()

    return resolved[:MAX_ATTACHMENT_NAME_LENGTH]
