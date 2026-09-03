"""Diagnóstico y backfill seguro de metadatos técnicos de PDF históricos.

Se usan ``QuerySet.update`` deliberadamente para no ejecutar ``full_clean``
sobre publicaciones históricas que todavía puedan tener sede u otros campos
nuevos pendientes. Solo se completan metadatos derivados del archivo físico.
"""

import hashlib
import os

from django.db.models import Q

from core.models import Publicacion, PublicacionArchivo

CHUNK_SIZE = 64 * 1024


def _metadata_from_field(field_file):
    if not field_file or not getattr(field_file, "name", None):
        return None, "sin_archivo"

    name = str(field_file.name)
    storage = field_file.storage
    try:
        if not storage.exists(name):
            return None, "archivo_no_encontrado"
        size = int(storage.size(name))
        digest = hashlib.sha256()
        with storage.open(name, "rb") as fh:
            while True:
                chunk = fh.read(CHUNK_SIZE)
                if not chunk:
                    break
                digest.update(chunk)
        return {
            "nombre_original": os.path.basename(name)[:255] or None,
            "tamano_bytes": size,
            "sha256": digest.hexdigest(),
        }, None
    except Exception as exc:
        return None, str(exc)[:500]


def diagnostico_integridad_documental():
    pubs_with_pdf = Publicacion.objects.exclude(archivo_pdf="").exclude(archivo_pdf__isnull=True)
    files = PublicacionArchivo.objects.exclude(archivo="").exclude(archivo__isnull=True)
    return {
        "publicaciones_con_pdf": pubs_with_pdf.count(),
        "publicaciones_metadata_incompleta": pubs_with_pdf.filter(
            Q(archivo_pdf_nombre_original__isnull=True)
            | Q(archivo_pdf_nombre_original="")
            | Q(archivo_pdf_tamano_bytes__isnull=True)
            | Q(archivo_pdf_sha256__isnull=True)
            | Q(archivo_pdf_sha256="")
        ).count(),
        "adjuntos_pdf": files.count(),
        "adjuntos_metadata_incompleta": files.filter(
            Q(nombre_original__isnull=True)
            | Q(nombre_original="")
            | Q(tamano_bytes__isnull=True)
            | Q(sha256__isnull=True)
            | Q(sha256="")
        ).count(),
    }


def backfill_integridad_documental(*, dry_run=False, limit=None, publication_id=None):
    result = {
        "dry_run": bool(dry_run),
        "publicaciones_revisadas": 0,
        "publicaciones_actualizadas": 0,
        "adjuntos_revisados": 0,
        "adjuntos_actualizados": 0,
        "errores": [],
    }

    pub_qs = Publicacion.objects.exclude(archivo_pdf="").exclude(archivo_pdf__isnull=True).order_by("id")
    if publication_id:
        pub_qs = pub_qs.filter(pk=publication_id)
    if limit:
        pub_qs = pub_qs[: int(limit)]

    pub_ids = []
    for pub in pub_qs.iterator(chunk_size=100):
        pub_ids.append(pub.pk)
        result["publicaciones_revisadas"] += 1
        metadata, error = _metadata_from_field(pub.archivo_pdf)
        if error:
            result["errores"].append({"tipo": "publicacion", "id": pub.pk, "error": error})
            continue
        values = {}
        if not pub.archivo_pdf_nombre_original:
            values["archivo_pdf_nombre_original"] = metadata["nombre_original"]
        if pub.archivo_pdf_tamano_bytes is None:
            values["archivo_pdf_tamano_bytes"] = metadata["tamano_bytes"]
        if not pub.archivo_pdf_sha256:
            values["archivo_pdf_sha256"] = metadata["sha256"]
        if values:
            result["publicaciones_actualizadas"] += 1
            if not dry_run:
                Publicacion.objects.filter(pk=pub.pk).update(**values)

    file_qs = PublicacionArchivo.objects.exclude(archivo="").exclude(archivo__isnull=True).order_by("id")
    if publication_id:
        file_qs = file_qs.filter(publicacion_id=publication_id)
    elif limit and pub_ids:
        file_qs = file_qs.filter(publicacion_id__in=pub_ids)

    for item in file_qs.iterator(chunk_size=100):
        result["adjuntos_revisados"] += 1
        metadata, error = _metadata_from_field(item.archivo)
        if error:
            result["errores"].append({"tipo": "adjunto", "id": item.pk, "error": error})
            continue
        values = {}
        if not item.nombre_original:
            values["nombre_original"] = metadata["nombre_original"]
        if item.tamano_bytes is None:
            values["tamano_bytes"] = metadata["tamano_bytes"]
        if not item.sha256:
            values["sha256"] = metadata["sha256"]
        if values:
            result["adjuntos_actualizados"] += 1
            if not dry_run:
                PublicacionArchivo.objects.filter(pk=item.pk).update(**values)

    result["errores_total"] = len(result["errores"])
    return result
