"""
Serializer para resultados rápidos de búsqueda de usuarios
académicos.

Expone:

- Información básica del usuario.
- Nombre completo.
- Rol y etiqueta legible.
- Carrera y facultad relacionadas.
- Estado de completitud del perfil.
- URL absoluta del avatar.

La facultad se deriva exclusivamente desde:

    usuario.carrera.facultad
"""

from rest_framework import serializers

from core.models import Usuario


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


def _optional_text(value):
    """
    Devuelve un texto normalizado o None.
    """
    normalized = _normalize_text(
        value
    )

    return normalized or None


def _safe_file_url(
    file_field,
    *,
    request=None,
):
    """
    Obtiene de forma segura la URL de un archivo almacenado.

    Cuando existe una petición HTTP, devuelve una URL absoluta.
    """
    if not file_field:
        return None

    file_name = getattr(
        file_field,
        "name",
        None,
    )

    if not file_name:
        return None

    try:
        file_url = file_field.url

    except (
        ValueError,
        OSError,
        NotImplementedError,
    ):
        return None

    if request is None:
        return file_url

    try:
        return request.build_absolute_uri(
            file_url
        )

    except (
        ValueError,
        TypeError,
    ):
        return file_url


def _build_full_name(user):
    """
    Construye el nombre completo del usuario.
    """
    if user is None:
        return None

    get_full_name = getattr(
        user,
        "get_full_name",
        None,
    )

    if callable(get_full_name):
        full_name = _optional_text(
            get_full_name()
        )

        if full_name:
            return full_name

    names = _optional_text(
        getattr(
            user,
            "nombres",
            None,
        )
    )

    surnames = _optional_text(
        getattr(
            user,
            "apellidos",
            None,
        )
    )

    resolved_name = " ".join(
        value
        for value in [
            names,
            surnames,
        ]
        if value
    )

    return resolved_name or None


# ============================================================
# SERIALIZER
# ============================================================

class UsuarioBusquedaSerializer(
    serializers.ModelSerializer
):
    """
    Representación resumida de un usuario académico para
    resultados de búsqueda y autocompletado.

    El selector correspondiente debe limitar los resultados a
    usuarios académicos activos.
    """

    nombre_completo = serializers.SerializerMethodField(
        read_only=True,
    )

    rol_label = serializers.SerializerMethodField(
        read_only=True,
    )

    carrera_id = serializers.IntegerField(
        read_only=True,
    )

    carrera = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad_id = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad = serializers.SerializerMethodField(
        read_only=True,
    )

    avatar_url = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Usuario

        fields = [
            "id",
            "nombres",
            "apellidos",
            "nombre_completo",
            "email",
            "rol",
            "rol_label",
            "auth_source",
            "carrera_id",
            "carrera",
            "facultad_id",
            "facultad",
            "perfil_completo",
            "avatar_url",
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
        Devuelve el nombre completo normalizado.
        """
        return _build_full_name(
            obj
        )

    # ========================================================
    # ROL
    # ========================================================

    def get_rol_label(
        self,
        obj,
    ):
        """
        Devuelve la etiqueta legible del rol.

        Ejemplos:

        - Autor
        - Autor externo
        """
        get_role_display = getattr(
            obj,
            "get_rol_display",
            None,
        )

        if callable(get_role_display):
            role_label = _optional_text(
                get_role_display()
            )

            if role_label:
                return role_label

        return _optional_text(
            getattr(
                obj,
                "rol",
                None,
            )
        )

    # ========================================================
    # CARRERA
    # ========================================================

    def get_carrera(
        self,
        obj,
    ):
        """
        Devuelve el nombre de la carrera relacionada.
        """
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        return _optional_text(
            getattr(
                career,
                "nombre",
                None,
            )
        )

    # ========================================================
    # FACULTAD
    # ========================================================

    def get_facultad_id(
        self,
        obj,
    ):
        """
        Obtiene el identificador de la facultad desde la carrera.
        """
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        return getattr(
            career,
            "facultad_id",
            None,
        )

    def get_facultad(
        self,
        obj,
    ):
        """
        Obtiene el nombre de la facultad desde:

            usuario.carrera.facultad
        """
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        faculty = getattr(
            career,
            "facultad",
            None,
        )

        if faculty is None:
            return None

        return _optional_text(
            getattr(
                faculty,
                "nombre",
                None,
            )
        )

    # ========================================================
    # AVATAR
    # ========================================================

    def get_avatar_url(
        self,
        obj,
    ):
        """
        Devuelve la URL absoluta del avatar cuando existe.
        """
        return _safe_file_url(
            getattr(
                obj,
                "avatar",
                None,
            ),
            request=self.context.get(
                "request"
            ),
        )