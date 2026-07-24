"""
Serializer para resultados rápidos de búsqueda de autores.

Expone:

- Datos básicos del autor.
- Nombre completo normalizado.
- Correo efectivo.
- Identificación e institución.
- Estado de autor externo.
- Usuario relacionado, cuando existe.

El correo del Usuario vinculado tiene prioridad sobre el correo
almacenado directamente en Autor.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import Autor


User = get_user_model()


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza un texto eliminando espacios repetidos.
    """
    return " ".join(
        str(value or "").split()
    )


def _normalize_email(value):
    """
    Normaliza un correo mediante el manager de Usuario.
    """
    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        return None

    return (
        User.objects
        .normalize_email(normalized)
        .strip()
        .lower()
        or None
    )


def _build_full_name(author):
    """
    Construye el nombre completo del autor.
    """
    return " ".join(
        part
        for part in [
            _normalize_text(
                getattr(
                    author,
                    "nombres",
                    "",
                )
            ),
            _normalize_text(
                getattr(
                    author,
                    "apellidos",
                    "",
                )
            ),
        ]
        if part
    )


# ============================================================
# SERIALIZER
# ============================================================

class AutorBusquedaSerializer(
    serializers.ModelSerializer
):
    """
    Representación resumida de un autor para búsquedas y
    autocompletados.
    """

    nombre_completo = serializers.SerializerMethodField(
        read_only=True,
    )

    correo_resuelto = serializers.SerializerMethodField(
        read_only=True,
    )

    usuario_id = serializers.IntegerField(
        read_only=True,
    )

    usuario_activo = serializers.SerializerMethodField(
        read_only=True,
    )

    es_admin = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Autor

        fields = [
            "id",
            "nombres",
            "apellidos",
            "nombre_completo",
            "identificacion",
            "correo",
            "correo_resuelto",
            "institucion",
            "es_externo",
            "usuario_id",
            "usuario_activo",
            "es_admin",
        ]

        read_only_fields = fields

    # ========================================================
    # NOMBRE
    # ========================================================

    def get_nombre_completo(
        self,
        obj,
    ):
        """
        Devuelve nombres y apellidos normalizados.
        """
        model_full_name = getattr(
            obj,
            "nombre_completo",
            None,
        )

        if callable(model_full_name):
            resolved_name = _normalize_text(
                model_full_name()
            )

            if resolved_name:
                return resolved_name

        if isinstance(
            model_full_name,
            str,
        ):
            resolved_name = _normalize_text(
                model_full_name
            )

            if resolved_name:
                return resolved_name

        return _build_full_name(
            obj
        )

    # ========================================================
    # CORREO
    # ========================================================

    def get_correo_resuelto(
        self,
        obj,
    ):
        """
        Prioriza el correo del Usuario vinculado.

        Cuando no existe Usuario o no tiene correo, devuelve el
        correo almacenado directamente en Autor.
        """
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if user is not None:
            user_email = _normalize_email(
                getattr(
                    user,
                    "email",
                    None,
                )
            )

            if user_email:
                return user_email

        return _normalize_email(
            getattr(
                obj,
                "correo",
                None,
            )
        )

    # ========================================================
    # USUARIO
    # ========================================================

    def get_usuario_activo(
        self,
        obj,
    ):
        """
        Indica si el autor está vinculado a una cuenta activa.
        """
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if user is None:
            return False

        return bool(
            getattr(
                user,
                "is_active",
                False,
            )
        )

    def get_es_admin(
        self,
        obj,
    ):
        """
        Indica si el Usuario vinculado posee permisos
        administrativos.
        """
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if user is None:
            return False

        return bool(
            getattr(
                user,
                "is_staff",
                False,
            )
            or getattr(
                user,
                "is_superuser",
                False,
            )
        )