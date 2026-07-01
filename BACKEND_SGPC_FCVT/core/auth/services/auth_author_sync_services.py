"""
Servicio para garantizar que cada usuario autor tenga su registro Autor asociado.
Crea, vincula o sincroniza el autor según rol, origen de autenticación y datos del usuario.
"""

from django.db import transaction

from core.models import Autor


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_email(value):
    value = _norm_text(value).lower()
    return value or None


def asegurar_autor_para_usuario(user):
    if not user:
        return None

    auth_source = _norm_text(getattr(user, "auth_source", "")).lower()
    rol = _norm_text(getattr(user, "rol", "")).lower()

    es_microsoft = auth_source == "microsoft"
    es_autor = rol == "autor"
    es_autor_externo = rol == "autor_externo"

    if not (es_microsoft or es_autor or es_autor_externo):
        return None

    email = _norm_email(getattr(user, "email", None))
    ident = _norm_optional_text(getattr(user, "identificacion", None))

    nombres = _norm_text(getattr(user, "nombres", ""))
    apellidos = _norm_text(getattr(user, "apellidos", ""))

    with transaction.atomic():
        autor = Autor.objects.select_for_update().filter(usuario=user).first()

        if autor is None and es_autor_externo:
            pendientes_qs = Autor.objects.select_for_update().filter(
                usuario__isnull=True,
                es_externo=True,
            )

            if ident:
                autor = pendientes_qs.filter(identificacion=ident).first()

            if autor is None and email:
                autor = pendientes_qs.filter(correo__iexact=email).first()

            if autor is not None:
                autor.usuario = user
                autor.save(update_fields=["usuario"])

        if autor is None:
            autor = Autor.objects.create(
                usuario=user,
                identificacion=ident,
                nombres=nombres,
                apellidos=apellidos,
                correo=email,
                es_externo=es_autor_externo,
            )
            return autor

        changed = False

        if autor.nombres != nombres:
            autor.nombres = nombres
            changed = True

        if autor.apellidos != apellidos:
            autor.apellidos = apellidos
            changed = True

        if email and (autor.correo or "").strip().lower() != email:
            autor.correo = email
            changed = True

        if ident and autor.identificacion != ident:
            autor.identificacion = ident
            changed = True

        new_ext = False if es_microsoft else es_autor_externo
        if autor.es_externo != new_ext:
            autor.es_externo = new_ext
            changed = True

        if changed:
            autor.save()

        return autor