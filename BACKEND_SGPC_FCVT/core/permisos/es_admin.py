"""Permiso administrativo del SGPC ULEAM."""

from rest_framework.permissions import BasePermission


class EsAdmin(BasePermission):
    message = (
        "No tiene permisos administrativos para realizar "
        "esta operación."
    )
    code = "admin_permission_required"

    @staticmethod
    def _es_administrador_activo(user):
        if user is None:
            return False

        authenticated = getattr(user, "is_authenticated", False)

        if callable(authenticated):
            authenticated = authenticated()

        return bool(
            authenticated
            and getattr(user, "is_active", False)
            and (
                getattr(user, "is_staff", False)
                or getattr(user, "is_superuser", False)
            )
        )

    def has_permission(self, request, view):
        return self._es_administrador_activo(request.user)

    def has_object_permission(self, request, view, obj):
        return self._es_administrador_activo(request.user)
