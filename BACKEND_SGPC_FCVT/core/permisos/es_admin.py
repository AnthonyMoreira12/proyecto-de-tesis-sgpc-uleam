from rest_framework.permissions import BasePermission


class EsAdmin(BasePermission):
    """
    Permite acceso solo a usuarios administradores del sistema.
    """

    def has_permission(self, request, view):
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            return False

        return bool(
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
        )