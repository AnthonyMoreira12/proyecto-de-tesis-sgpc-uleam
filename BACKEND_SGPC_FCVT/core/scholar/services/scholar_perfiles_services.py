"""
Servicios auxiliares para perfiles tipo Scholar.
"""

from django.db.models import TextField, Value
from django.db.models.functions import Cast, Coalesce, Concat

from core.models import Publicacion, PublicacionAutor
from core.publicaciones.utils.publicaciones_tipo_resolver_utils import (
    annotate_tipo_publicacion_final,
    tipo_publicacion_label,
)


def build_fullname_expression():
    return Cast(
        Concat(
            Coalesce("nombres", Value("")),
            Value(" "),
            Coalesce("apellidos", Value("")),
            output_field=TextField(),
        ),
        TextField(),
    )


def get_user_avatar_absolute_url(request, user):
    if request and user and getattr(user, "avatar", None) and hasattr(user.avatar, "url"):
        try:
            return request.build_absolute_uri(user.avatar.url)
        except Exception:
            return user.avatar.url
    return None


def get_author_org_label(author):
    user = getattr(author, "usuario", None)
    if not user:
        return "Autor externo" if getattr(author, "es_externo", False) else "ULEAM"

    carrera = getattr(user, "carrera", None)
    facultad = getattr(user, "facultad", None)

    parts = []
    if carrera and getattr(carrera, "nombre", None):
        parts.append(carrera.nombre)
    if facultad and getattr(facultad, "nombre", None):
        parts.append(facultad.nombre)

    return " • ".join(parts) if parts else "ULEAM"


def get_publicacion_title_and_venue(publicacion):
    codigo = (getattr(getattr(publicacion, "tipo", None), "codigo", "") or "").lower()

    if codigo in {"articulo", "articulo_regional", "articulo_alto_impacto"} and getattr(publicacion, "articulo", None):
        return (
            (publicacion.articulo.nombre_articulo or "").strip() or "—",
            (publicacion.articulo.nombre_revista or "").strip() or None,
        )

    if codigo == "ponencia" and getattr(publicacion, "ponencia", None):
        return (
            (publicacion.ponencia.nombre_ponencia or "").strip() or "—",
            (publicacion.ponencia.nombre_evento or "").strip() or None,
        )

    if codigo == "libro" and getattr(publicacion, "libro", None):
        return (
            (publicacion.libro.nombre_libro or "").strip() or "—",
            (publicacion.libro.editorial_compilador or "").strip() or None,
        )

    if codigo in {"capitulo", "capitulo_libro"} and getattr(publicacion, "capitulo_libro", None):
        return (
            (publicacion.capitulo_libro.nombre_capitulo or "").strip() or "—",
            (publicacion.capitulo_libro.nombre_libro or "").strip() or None,
        )

    tipo_nombre = getattr(getattr(publicacion, "tipo", None), "nombre", None) or "Publicación"
    numero = getattr(publicacion, "numero", None) or publicacion.id
    return f"{tipo_nombre} #{numero}", None


def get_author_authors_string(publicacion_id: int) -> str:
    rels = (
        PublicacionAutor.objects
        .select_related("autor")
        .filter(publicacion_id=publicacion_id)
        .order_by("orden", "id")
    )

    names = []
    for rel in rels:
        autor = getattr(rel, "autor", None)
        if not autor:
            continue

        label = f"{autor.nombres or ''} {autor.apellidos or ''}".strip()
        if label:
            names.append(label)

    return ", ".join(names) if names else "—"


def build_public_profile_payload(*, request, author, is_me=False):
    user = getattr(author, "usuario", None)

    name = f"{author.nombres or ''} {author.apellidos or ''}".strip() or "—"
    org = get_author_org_label(author)
    avatar = get_user_avatar_absolute_url(request, user)

    publicacion_ids = (
        PublicacionAutor.objects
        .filter(autor_id=author.id)
        .values_list("publicacion_id", flat=True)
        .distinct()
    )

    publicaciones_qs = (
        annotate_tipo_publicacion_final(
            Publicacion.objects
            .select_related("tipo", "articulo", "ponencia", "libro", "capitulo_libro")
            .filter(id__in=publicacion_ids)
        )
        .order_by("-anio_publicacion", "-id")
    )

    publicaciones = []
    for pub in publicaciones_qs:
        title, venue = get_publicacion_title_and_venue(pub)
        tipo_final = getattr(pub, "tipo_publicacion_final", "sin_clasificar")

        publicaciones.append(
            {
                "id": pub.id,
                "title": title,
                "authors": get_author_authors_string(pub.id),
                "venue": venue,
                "citedBy": 0,
                "year": getattr(pub, "anio_publicacion", None),
                "type": {
                    "id": pub.tipo_id,
                    "nombre": pub.tipo.nombre if pub.tipo else None,
                    "codigo": pub.tipo.codigo if pub.tipo else None,
                }
                if pub.tipo
                else None,
                "tipo_publicacion_final": tipo_final,
                "tipo_publicacion_final_label": tipo_publicacion_label(tipo_final),
            }
        )

    payload = {
        "id": author.id,
        "name": name,
        "org": org,
        "avatar": avatar,
        "verified": None,
        "tags": [],
        "sinceYear": 2019,
        "metrics": {
            "citesTotal": 0,
            "citesSince": 0,
            "hTotal": 0,
            "hSince": 0,
            "i10Total": 0,
            "i10Since": 0,
        },
        "publications": publicaciones,
        "coauthors": [],
    }

    if is_me:
        payload["is_me"] = True

    return payload