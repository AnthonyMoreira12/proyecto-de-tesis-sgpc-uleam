from django.contrib.auth import get_user_model
from django.db import transaction

from core.models import Autor

User = get_user_model()


def _norm_text(value):
    return str(value or "").strip()


def _norm_optional_text(value):
    value = _norm_text(value)
    return value or None


def _norm_email(value):
    value = _norm_text(value).lower()
    return value or None


class AutorUsuarioSyncError(Exception):
    def __init__(self, detail):
        self.detail = detail
        super().__init__(str(detail))


def buscar_autor_existente(
    *,
    identificacion=None,
    correo=None,
    nombres="",
    apellidos="",
    exclude_autor_id=None,
):
    identificacion = _norm_optional_text(identificacion)
    correo = _norm_email(correo)
    nombres = _norm_text(nombres)
    apellidos = _norm_text(apellidos)

    qs = Autor.objects.select_related("usuario").all()

    if exclude_autor_id:
        qs = qs.exclude(pk=exclude_autor_id)

    if identificacion:
        autor = qs.filter(identificacion=identificacion).first()
        if autor:
            return {
                "exists": True,
                "match_type": "identificacion",
                "autor": autor,
            }

    if correo:
        autor = qs.filter(correo__iexact=correo).first()
        if autor:
            return {
                "exists": True,
                "match_type": "correo",
                "autor": autor,
            }

    if nombres and apellidos:
        autor = qs.filter(
            nombres__iexact=nombres,
            apellidos__iexact=apellidos,
        ).first()

        if autor:
            return {
                "exists": True,
                "match_type": "nombre_apellido",
                "autor": autor,
            }

    return {
        "exists": False,
        "match_type": None,
        "autor": None,
    }


def serializar_autor_match(autor, match_type=None):
    if not autor:
        return {
            "exists": False,
            "match_type": match_type,
            "autor": None,
        }

    correo_resuelto = None

    if getattr(autor, "usuario", None) and getattr(autor.usuario, "email", None):
        correo_resuelto = autor.usuario.email
    else:
        correo_resuelto = autor.correo

    return {
        "exists": True,
        "match_type": match_type,
        "autor": {
            "id": autor.id,
            "nombre_completo": f"{autor.nombres or ''} {autor.apellidos or ''}".strip(),
            "identificacion": autor.identificacion,
            "correo_resuelto": correo_resuelto,
            "institucion": autor.institucion,
            "usuario_id": getattr(autor.usuario, "id", None),
            "es_externo": bool(getattr(autor, "es_externo", False)),
        },
    }


def asegurar_autor_para_usuario(user):
    if not user:
        return None

    auth_source = _norm_text(getattr(user, "auth_source", "")).lower()
    rol = _norm_text(getattr(user, "rol", "")).lower()

    es_microsoft = auth_source == "microsoft" and rol == "autor"
    es_autor_local = auth_source == "local" and rol == "autor"
    es_autor_externo = auth_source == "local" and rol == "autor_externo"

    if not (es_microsoft or es_autor_local or es_autor_externo):
        return None

    email = _norm_email(getattr(user, "email", None))
    identificacion = _norm_optional_text(getattr(user, "identificacion", None))
    nombres = _norm_text(getattr(user, "nombres", "")) or "Usuario"
    apellidos = _norm_text(getattr(user, "apellidos", "")) or ""
    externo_flag = bool(es_autor_externo)

    institucion_inicial = _norm_optional_text(
        getattr(user, "ms_department", None)
        or getattr(user, "ms_office_location", None)
    )

    with transaction.atomic():
        autor = (
            Autor.objects.select_for_update()
            .filter(usuario=user)
            .first()
        )

        if autor is None:
            candidatos = Autor.objects.select_for_update().filter(usuario__isnull=True)

            if identificacion:
                autor = candidatos.filter(identificacion=identificacion).first()

            if autor is None and email:
                autor = candidatos.filter(correo__iexact=email).first()

        if autor is None:
            autor = Autor(
                usuario=user,
                identificacion=identificacion,
                nombres=nombres,
                apellidos=apellidos,
                correo=email,
                institucion=institucion_inicial,
                es_externo=externo_flag,
            )
            autor.save()
            return autor

        changed = False

        if autor.usuario_id != user.id:
            autor.usuario = user
            changed = True

        if identificacion and autor.identificacion != identificacion:
            autor.identificacion = identificacion
            changed = True

        if nombres and autor.nombres != nombres:
            autor.nombres = nombres
            changed = True

        if apellidos and autor.apellidos != apellidos:
            autor.apellidos = apellidos
            changed = True

        correo_actual = _norm_email(getattr(autor, "correo", None))
        if email and correo_actual != email:
            autor.correo = email
            changed = True

        if institucion_inicial and not getattr(autor, "institucion", None):
            autor.institucion = institucion_inicial
            changed = True

        if autor.es_externo != externo_flag:
            autor.es_externo = externo_flag
            changed = True

        if changed:
            autor.save()

        return autor


def asegurar_usuario_pendiente_para_autor(autor):
    if not autor:
        return None

    identificacion = _norm_optional_text(getattr(autor, "identificacion", None))
    correo = _norm_email(getattr(autor, "correo", None))
    nombres = _norm_text(getattr(autor, "nombres", "")) or "Autor"
    apellidos = _norm_text(getattr(autor, "apellidos", "")) or ""

    if not identificacion:
        raise AutorUsuarioSyncError(
            {
                "identificacion": (
                    "Para registrar el pendiente, la identificación es obligatoria."
                )
            }
        )

    if not correo:
        raise AutorUsuarioSyncError(
            {
                "correo": (
                    "Para registrar el pendiente, el correo es obligatorio."
                )
            }
        )

    with transaction.atomic():
        by_ident = (
            User.objects.select_for_update()
            .filter(identificacion=identificacion)
            .first()
        )

        by_email = (
            User.objects.select_for_update()
            .filter(email__iexact=correo)
            .first()
        )

        if by_ident and by_email and by_ident.pk != by_email.pk:
            raise AutorUsuarioSyncError(
                {
                    "detail": (
                        "La identificación y el correo corresponden a usuarios distintos. "
                        "Revise los datos antes de guardar."
                    )
                }
            )

        user = by_ident or by_email or getattr(autor, "usuario", None)

        if user:
            auth_source = _norm_text(getattr(user, "auth_source", "")).lower()
            rol = _norm_text(getattr(user, "rol", "")).lower()

            if auth_source == "microsoft":
                raise AutorUsuarioSyncError(
                    {
                        "correo": (
                            "Ya existe un usuario institucional con este correo. "
                            "No puede registrarse como autor externo pendiente."
                        )
                    }
                )

            if rol not in {"autor_externo"}:
                raise AutorUsuarioSyncError(
                    {
                        "detail": (
                            "Ya existe un usuario con esos datos, pero no corresponde "
                            "a un usuario externo pendiente."
                        )
                    }
                )

            linked_autor = getattr(user, "autor", None)

            if linked_autor and linked_autor.pk != autor.pk:
                raise AutorUsuarioSyncError(
                    {
                        "detail": (
                            "Ese usuario ya está vinculado a otro autor. "
                            "No se puede duplicar el registro."
                        )
                    }
                )

            changed_fields = []

            if user.email != correo:
                user.email = correo
                changed_fields.append("email")

            if (user.identificacion or None) != identificacion:
                user.identificacion = identificacion
                changed_fields.append("identificacion")

            if user.nombres != nombres:
                user.nombres = nombres
                changed_fields.append("nombres")

            if user.apellidos != apellidos:
                user.apellidos = apellidos
                changed_fields.append("apellidos")

            if user.rol != "autor_externo":
                user.rol = "autor_externo"
                changed_fields.append("rol")

            if user.auth_source != "local":
                user.auth_source = "local"
                changed_fields.append("auth_source")

            if not getattr(user, "creado_desde_selector", False):
                user.creado_desde_selector = True
                changed_fields.append("creado_desde_selector")

            if changed_fields:
                user.save(update_fields=changed_fields)

        else:
            user = User.objects.create_user(
                email=correo,
                nombres=nombres,
                apellidos=apellidos,
                password=None,
                identificacion=identificacion,
                rol="autor_externo",
                auth_source="local",
                is_active=False,
                is_staff=False,
                perfil_completo=False,
                creado_desde_selector=True,
            )

        autor_changed_fields = []

        if autor.usuario_id != user.id:
            autor.usuario = user
            autor_changed_fields.append("usuario")

        if autor.correo != correo:
            autor.correo = correo
            autor_changed_fields.append("correo")

        if autor.identificacion != identificacion:
            autor.identificacion = identificacion
            autor_changed_fields.append("identificacion")

        if not autor.es_externo:
            autor.es_externo = True
            autor_changed_fields.append("es_externo")

        if autor_changed_fields:
            autor.save(update_fields=autor_changed_fields)

        return user