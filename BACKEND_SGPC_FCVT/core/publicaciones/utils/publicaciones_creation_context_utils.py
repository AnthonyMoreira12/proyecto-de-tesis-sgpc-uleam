from rest_framework.exceptions import ValidationError


def resolve_publicacion_creation_context(serializer):
    context = getattr(serializer, "context", {}) or {}

    request = context.get("request")
    request_user = getattr(request, "user", None)

    usuario_creador = context.get("usuario_creador_override") or request_user
    if not usuario_creador or not getattr(usuario_creador, "is_authenticated", False):
        raise ValidationError(
            {"detail": ["No se pudo resolver el usuario creador de la publicación."]}
        )

    admin_registrador = context.get("admin_registrador")
    registrado_por_admin = bool(context.get("registrado_por_admin"))

    if admin_registrador is None and registrado_por_admin:
        admin_registrador = request_user

    if admin_registrador is not None:
        if not getattr(admin_registrador, "is_staff", False) and not getattr(
            admin_registrador,
            "is_superuser",
            False,
        ):
            raise ValidationError(
                {"detail": ["El administrador registrador no es válido."]}
            )
        registrado_por_admin = True

    return usuario_creador, admin_registrador, registrado_por_admin