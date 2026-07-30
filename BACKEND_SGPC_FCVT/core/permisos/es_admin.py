"""Permiso administrativo del SGPC ULEAM."""

from rest_framework.permissions import BasePermission


class EsAdmin(BasePermission):
    """
    Permite el acceso únicamente a administradores activos.

    Un usuario es administrador cuando:

    - Está autenticado.
    - Su cuenta está activa.
    - Tiene is_staff=True o is_superuser=True.

    El rol académico y el origen de autenticación no determinan
    los permisos administrativos.
    """

    message = (
        "No tiene permisos administrativos para realizar "
        "esta operación."
    )

    code = "admin_permission_required"

    @staticmethod
    def _es_administrador_activo(user):
        """
        Comprueba de forma segura que el usuario autenticado tenga
        permisos administrativos y una cuenta activa.
        """
        if user is None:
            return False

        is_authenticated = getattr(
            user,
            "is_authenticated",
            False,
        )

        # Compatibilidad con implementaciones antiguas donde
        # is_authenticated podía ser un método.
        if callable(is_authenticated):
            is_authenticated = (
                is_authenticated()
            )

        if not bool(is_authenticated):
            return False

        if not bool(
            getattr(
                user,
                "is_active",
                False,
            )
        ):
            return False

        is_staff = bool(
            getattr(
                user,
                "is_staff",
                False,
            )
        )

        is_superuser = bool(
            getattr(
                user,
                "is_superuser",
                False,
            )
        )

        return bool(
            is_staff
            or is_superuser
        )

    def has_permission(
        self,
        request,
        view,
    ):
        """
        Validación general de acceso al endpoint.
        """
        return self._es_administrador_activo(
            getattr(
                request,
                "user",
                None,
            )
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        """
        Validación para operaciones sobre objetos individuales.
        """
        return self._es_administrador_activo(
            getattr(
                request,
                "user",
                None,
            )
        )