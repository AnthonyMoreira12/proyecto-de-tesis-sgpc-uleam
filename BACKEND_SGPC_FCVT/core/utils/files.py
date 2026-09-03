"""Utilidades compartidas para textos y archivos."""

import hashlib
import os

from django.utils.text import get_valid_filename
from rest_framework import serializers


PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}

PDF_SIGNATURE = b"%PDF-"
PDF_SIGNATURE_SCAN_BYTES = 1024
PDF_TRAILER = b"%%EOF"
PDF_TRAILER_SCAN_BYTES = 4096
PDF_HASH_CHUNK_BYTES = 64 * 1024


def normalize_text(value):
    return str(value or "").strip()


def normalize_optional_text(value):
    value = normalize_text(value)
    return value or None


def sanitize_pdf_filename(
    filename,
    *,
    fallback="documento.pdf",
    max_length=180,
):
    """Devuelve un nombre base seguro y con extensión .pdf."""

    raw = os.path.basename(
        normalize_text(filename)
        or fallback
    )

    base, _extension = os.path.splitext(raw)
    safe_base = get_valid_filename(
        base
        or os.path.splitext(fallback)[0]
        or "documento"
    )

    safe_base = normalize_text(
        safe_base
    ) or "documento"

    # Reserva cuatro caracteres para '.pdf'.
    safe_base = safe_base[: max(1, int(max_length) - 4)]

    return f"{safe_base}.pdf"


def _file_object(uploaded_file):
    if uploaded_file in (None, ""):
        return None

    try:
        return getattr(
            uploaded_file,
            "file",
            uploaded_file,
        )
    except Exception:
        return uploaded_file


def _remember_position(file_obj):
    try:
        if hasattr(file_obj, "tell"):
            return file_obj.tell()
    except (OSError, ValueError):
        pass

    return 0


def _restore_position(file_obj, position):
    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(position)
    except (OSError, ValueError):
        try:
            file_obj.seek(0)
        except Exception:
            pass


def read_file_prefix(
    uploaded_file,
    *,
    max_bytes=PDF_SIGNATURE_SCAN_BYTES,
):
    file_obj = _file_object(
        uploaded_file
    )

    if (
        file_obj is None
        or not hasattr(file_obj, "read")
    ):
        return b""

    position = _remember_position(
        file_obj
    )

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        content = file_obj.read(
            int(max_bytes)
        )

        if isinstance(content, str):
            content = content.encode(
                "utf-8",
                errors="ignore",
            )

        return bytes(content or b"")

    except (OSError, ValueError, TypeError):
        return b""

    finally:
        _restore_position(
            file_obj,
            position,
        )


def read_file_tail(
    uploaded_file,
    *,
    max_bytes=PDF_TRAILER_SCAN_BYTES,
):
    file_obj = _file_object(
        uploaded_file
    )

    if (
        file_obj is None
        or not hasattr(file_obj, "read")
        or not hasattr(file_obj, "seek")
    ):
        return b""

    position = _remember_position(
        file_obj
    )

    try:
        file_obj.seek(
            0,
            os.SEEK_END,
        )

        total = file_obj.tell()
        start = max(
            0,
            int(total) - int(max_bytes),
        )

        file_obj.seek(start)
        content = file_obj.read()

        if isinstance(content, str):
            content = content.encode(
                "utf-8",
                errors="ignore",
            )

        return bytes(content or b"")

    except (OSError, ValueError, TypeError):
        return b""

    finally:
        _restore_position(
            file_obj,
            position,
        )


def compute_file_sha256(
    uploaded_file,
):
    """Calcula SHA-256 sin alterar la posición útil del archivo."""

    file_obj = _file_object(
        uploaded_file
    )

    if (
        file_obj is None
        or not hasattr(file_obj, "read")
    ):
        return None

    position = _remember_position(
        file_obj
    )

    digest = hashlib.sha256()

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        while True:
            chunk = file_obj.read(
                PDF_HASH_CHUNK_BYTES
            )

            if not chunk:
                break

            if isinstance(chunk, str):
                chunk = chunk.encode(
                    "utf-8",
                    errors="ignore",
                )

            digest.update(
                bytes(chunk)
            )

        return digest.hexdigest()

    except (OSError, ValueError, TypeError):
        return None

    finally:
        _restore_position(
            file_obj,
            position,
        )


def _detected_mime_from_content(
    prefix,
):
    """
    Usa python-magic/libmagic cuando está disponible.

    Si la dependencia nativa no está disponible, la validación continúa
    mediante firma binaria y estructura PDF, evitando convertir libmagic
    en un requisito obligatorio para arrancar Django.
    """

    if not prefix:
        return None

    try:
        import magic
    except Exception:
        return None

    try:
        detected = magic.from_buffer(
            prefix,
            mime=True,
        )
    except Exception:
        return None

    detected = normalize_text(
        detected
    ).lower()

    return detected or None


def validate_pdf_file(
    uploaded_file,
    *,
    max_bytes,
    field_name="archivo_pdf",
    label="El archivo PDF",
):
    """
    Valida un PDF por múltiples capas:

    - extensión;
    - MIME declarado;
    - tamaño;
    - firma binaria %PDF-;
    - MIME detectado por contenido cuando libmagic está disponible;
    - marcador estructural %%EOF;
    - cálculo SHA-256 para comprobar que el contenido es legible.

    La posición del cursor se restaura al finalizar.
    """

    if uploaded_file in (None, ""):
        return uploaded_file

    filename = normalize_text(
        getattr(
            uploaded_file,
            "name",
            "",
        )
    )

    if not filename:
        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} no posee un nombre de archivo válido."
                )
            }
        )

    if os.path.splitext(
        filename.lower()
    )[1] != ".pdf":
        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} debe tener extensión .pdf."
                )
            }
        )

    content_type = normalize_text(
        getattr(
            uploaded_file,
            "content_type",
            "",
        )
        or getattr(
            getattr(
                uploaded_file,
                "file",
                None,
            ),
            "content_type",
            "",
        )
    ).lower()

    if (
        content_type
        and content_type not in PDF_CONTENT_TYPES
    ):
        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} debe declarar un tipo de contenido PDF válido."
                )
            }
        )

    try:
        size = int(
            getattr(
                uploaded_file,
                "size",
                0,
            )
            or 0
        )
    except (TypeError, ValueError):
        size = 0

    if size <= 0:
        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} está vacío."
                )
            }
        )

    if size > int(max_bytes):
        max_mb = int(max_bytes) / (1024 * 1024)

        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} supera el tamaño máximo "
                    f"de {max_mb:g} MB."
                )
            }
        )

    prefix = read_file_prefix(
        uploaded_file,
        max_bytes=PDF_SIGNATURE_SCAN_BYTES,
    )

    if (
        not prefix
        or PDF_SIGNATURE not in prefix
    ):
        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} no contiene una firma PDF válida."
                )
            }
        )

    detected_mime = (
        _detected_mime_from_content(
            prefix
        )
    )

    if (
        detected_mime
        and detected_mime not in PDF_CONTENT_TYPES
    ):
        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} no corresponde realmente a un documento PDF."
                )
            }
        )

    tail = read_file_tail(
        uploaded_file,
        max_bytes=PDF_TRAILER_SCAN_BYTES,
    )

    if (
        not tail
        or PDF_TRAILER not in tail
    ):
        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} no contiene una estructura PDF completa "
                    "(marcador %%EOF ausente)."
                )
            }
        )

    digest = compute_file_sha256(
        uploaded_file
    )

    if not digest:
        raise serializers.ValidationError(
            {
                field_name: (
                    f"{label} no pudo leerse completamente para "
                    "verificar su integridad."
                )
            }
        )

    return uploaded_file


def delete_storage_file(field_file):
    if not field_file:
        return

    name = getattr(
        field_file,
        "name",
        None,
    )

    storage = getattr(
        field_file,
        "storage",
        None,
    )

    if not name or storage is None:
        return

    try:
        if storage.exists(name):
            storage.delete(name)
    except (OSError, ValueError):
        return