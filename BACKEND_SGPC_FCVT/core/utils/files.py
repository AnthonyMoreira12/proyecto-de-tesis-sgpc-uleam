"""Utilidades compartidas para textos y archivos."""

import os

from rest_framework import serializers


PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


def normalize_text(value):
    return str(value or "").strip()


def normalize_optional_text(value):
    value = normalize_text(value)
    return value or None


def validate_pdf_file(
    uploaded_file,
    *,
    max_bytes,
    field_name="archivo_pdf",
    label="El archivo PDF",
):
    if uploaded_file in (None, ""):
        return uploaded_file

    filename = normalize_text(
        getattr(uploaded_file, "name", "")
    ).lower()

    if os.path.splitext(filename)[1] != ".pdf":
        raise serializers.ValidationError(
            {field_name: f"{label} debe tener extensión .pdf."}
        )

    content_type = normalize_text(
        getattr(uploaded_file, "content_type", "")
    ).lower()

    if content_type and content_type not in PDF_CONTENT_TYPES:
        raise serializers.ValidationError(
            {field_name: f"{label} debe ser un PDF válido."}
        )

    size = int(getattr(uploaded_file, "size", 0) or 0)

    if size <= 0:
        raise serializers.ValidationError(
            {field_name: f"{label} está vacío."}
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

    return uploaded_file


def delete_storage_file(field_file):
    if not field_file:
        return

    name = getattr(field_file, "name", None)
    storage = getattr(field_file, "storage", None)

    if not name or storage is None:
        return

    try:
        if storage.exists(name):
            storage.delete(name)
    except (OSError, ValueError):
        return
