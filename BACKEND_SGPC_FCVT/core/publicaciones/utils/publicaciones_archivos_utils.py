import magic
import os
import json
from rest_framework.exceptions import ValidationError

def validar_firma_pdf(uploaded_file):
    """
    Lee los bytes reales del archivo para asegurar que sea un PDF legítimo,
    evitando ataques de spoofing MIME/extensión (Requisito de Auditoría).
    """
    if not uploaded_file:
        raise ValidationError("No se proporcionó ningún archivo.")

    try:
        # Leer los primeros 2048 bytes para determinar la firma real (Magic Bytes)
        file_mime = magic.from_buffer(uploaded_file.read(2048), mime=True)
        if file_mime != "application/pdf":
            raise ValidationError("El archivo adjunto no es un PDF válido (Firma MIME incorrecta).")
        
        # Devolver el puntero al inicio para que Django/Storage pueda guardarlo luego
        uploaded_file.seek(0)
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error al validar los bytes del archivo: {str(e)}")
    
    return uploaded_file


def default_nombre_from_file(uploaded_file):
    """Genera un nombre por defecto basado en el nombre del archivo original."""
    raw_name = str(getattr(uploaded_file, "name", "") or "").strip()
    if not raw_name:
        return "Archivo PDF"

    base, _ext = os.path.splitext(raw_name)
    base = str(base or "").strip()
    return base or raw_name or "Archivo PDF"