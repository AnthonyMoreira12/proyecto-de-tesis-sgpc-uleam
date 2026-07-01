import json
import os
from rest_framework.exceptions import ValidationError

def extraer_archivos_request(request):
    """Extrae los archivos de la solicitud multipart."""
    files = []
    if hasattr(request.FILES, "getlist"):
        files = request.FILES.getlist("files") or request.FILES.getlist("archivos")
    return [f for f in files if f]

def default_nombre_from_file(uploaded_file):
    """Genera un nombre por defecto basado en el nombre del archivo original."""
    raw_name = str(getattr(uploaded_file, "name", "") or "").strip()
    if not raw_name:
        return "Archivo PDF"

    base, _ext = os.path.splitext(raw_name)
    base = str(base or "").strip()
    return base or raw_name or "Archivo PDF"

def parse_meta_json(raw_meta):
    """Convierte el string de metadatos a una lista JSON."""
    raw = str(raw_meta or "").strip()
    if not raw:
        return []

    try:
        parsed = json.loads(raw)
    except Exception:
        raise ValidationError(
            {"meta": ["Formato inválido. Debe ser JSON válido."]}
        )

    if parsed is None:
        return []

    if not isinstance(parsed, list):
        raise ValidationError(
            {"meta": ["Debe enviar una lista JSON de adjuntos."]}
        )

    return parsed

def procesar_adjuntos_payload(request, plain_data):
    """
    Valida y empareja los archivos subidos con sus respectivos metadatos (orden, nombre).
    Devuelve una lista de diccionarios listos para guardar.
    """
    files = extraer_archivos_request(request)
    if not files:
        return []

    raw_meta = plain_data.get("meta") or plain_data.get("archivos_meta") or ""
    meta_list = parse_meta_json(raw_meta)

    if meta_list and len(meta_list) != len(files):
        raise ValidationError(
            {
                "detail": (
                    "La cantidad de metadatos debe coincidir con la cantidad de archivos adjuntos."
                )
            }
        )

    normalized = []
    
    if not meta_list:
        for index, uploaded_file in enumerate(files, start=1):
            normalized.append(
                {
                    "file": uploaded_file,
                    "nombre": default_nombre_from_file(uploaded_file),
                    "orden": index,
                }
            )
        return normalized

    for index, uploaded_file in enumerate(files, start=1):
        item = meta_list[index - 1]

        if not isinstance(item, dict):
            raise ValidationError(
                {"meta": [f"El adjunto #{index} debe ser un objeto JSON."]}
            )

        nombre = str(item.get("nombre") or "").strip()
        if not nombre:
            nombre = default_nombre_from_file(uploaded_file)

        orden = item.get("orden")
        if orden in (None, "", 0):
            orden = index

        try:
            orden = int(orden)
        except Exception:
            raise ValidationError(
                {"meta": [f"El 'orden' del adjunto #{index} debe ser numérico."]}
            )

        if orden < 1:
            raise ValidationError(
                {"meta": [f"El 'orden' del adjunto #{index} debe ser >= 1."]}
            )

        normalized.append(
            {
                "file": uploaded_file,
                "nombre": nombre,
                "orden": orden,
            }
        )

    ordenes = [item["orden"] for item in normalized]
    if len(ordenes) != len(set(ordenes)):
        raise ValidationError(
            {"meta": ["No se permite repetir el campo 'orden' en adjuntos."]}
        )

    return sorted(normalized, key=lambda item: item["orden"])