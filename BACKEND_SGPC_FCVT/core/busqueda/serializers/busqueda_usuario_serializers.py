"""
Serializer público para resultados rápidos de usuarios académicos.

La búsqueda pública utiliza ``Autor.id`` como identificador canónico del
perfil científico. El Usuario solo aporta datos académicos y visuales.

Por seguridad no se exponen:

- Correo electrónico.
- Número de cédula.
- Fuente de autenticación.
- Identificador interno del Usuario.
- Privilegios administrativos.
- Datos de credenciales.
"""

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from core.models import Publicacion, Usuario


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """Normaliza un texto eliminando espacios repetidos."""
    return " ".join(str(value or "").split())


def _optional_text(value):
    """Devuelve texto normalizado o ``None``."""
    normalized = _normalize_text(value)
    return normalized or None


def _safe_author(user):
    """Obtiene de forma segura el Autor vinculado al Usuario."""
    if user is None:
        return None

    try:
        return user.autor
    except (ObjectDoesNotExist, AttributeError):
        return None


def _safe_file_url(file_field, *, request=None):
    """Obtiene una URL segura y, cuando es posible, absoluta."""
    if not file_field or not getattr(file_field, "name", None):
        return None

    try:
        file_url = file_field.url
    except (ValueError, OSError, NotImplementedError):
        return None

    if request is None:
        return file_url

    try:
        return request.build_absolute_uri(file_url)
    except (ValueError, TypeError):
        return file_url


def _build_full_name(user):
    """Construye el nombre completo del Usuario."""
    if user is None:
        return None

    get_full_name = getattr(user, "get_full_name", None)
    if callable(get_full_name):
        full_name = _optional_text(get_full_name())
        if full_name:
            return full_name

    full_name = " ".join(
        value
        for value in (
            _optional_text(getattr(user, "nombres", None)),
            _optional_text(getattr(user, "apellidos", None)),
        )
        if value
    )

    return full_name or None


def _site(user):
    """Obtiene la sede institucional del Usuario."""
    return getattr(user, "sede", None) if user is not None else None


def _career(user):
    """Obtiene la carrera del Usuario."""
    return getattr(user, "carrera", None) if user is not None else None


def _faculty(user):
    """Obtiene la facultad mediante ``usuario.carrera.facultad``."""
    career = _career(user)
    return getattr(career, "facultad", None) if career is not None else None


def _unique_text_list(values):
    """Construye una lista de etiquetas sin duplicados."""
    seen = set()
    result = []

    for value in values:
        normalized = _optional_text(value)
        if not normalized:
            continue

        key = normalized.casefold()
        if key in seen:
            continue

        seen.add(key)
        result.append(normalized)

    return result


def _publications_count(author):
    """Obtiene el total de publicaciones distintas del Autor."""
    if author is None:
        return 0

    for attribute_name in (
        "publicaciones_count",
        "total_publicaciones",
        "_publications_count",
    ):
        annotated_value = getattr(author, attribute_name, None)

        if annotated_value is None:
            continue

        try:
            return max(0, int(annotated_value))
        except (TypeError, ValueError, OverflowError):
            continue

    relation_manager = getattr(author, "participaciones", None)
    if relation_manager is None:
        return 0

    try:
        return (
            relation_manager
            .filter(
                publicacion__estado=(
                    Publicacion.ESTADO_APROBADA
                )
            )
            .values("publicacion_id")
            .distinct()
            .count()
        )
    except (AttributeError, TypeError, ValueError):
        return 0


# ============================================================
# SERIALIZER
# ============================================================

class UsuarioBusquedaSerializer(serializers.ModelSerializer):
    """
    Representación pública de una cuenta académica activa.

    ``id`` y ``autor_id`` corresponden a ``Autor.id``. Si la cuenta todavía
    no tiene Autor vinculado, ambos valores son ``None`` y
    ``perfil_disponible`` es falso.
    """

    id = serializers.SerializerMethodField(read_only=True)
    autor_id = serializers.SerializerMethodField(read_only=True)

    nombre_completo = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    rol_label = serializers.SerializerMethodField(read_only=True)
    es_externo = serializers.SerializerMethodField(read_only=True)

    sede_id = serializers.SerializerMethodField(read_only=True)
    sede = serializers.SerializerMethodField(read_only=True)
    carrera_id = serializers.SerializerMethodField(read_only=True)
    carrera = serializers.SerializerMethodField(read_only=True)
    facultad_id = serializers.SerializerMethodField(read_only=True)
    facultad = serializers.SerializerMethodField(read_only=True)

    org = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)

    avatar_url = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    publicaciones_count = serializers.SerializerMethodField(read_only=True)
    publications = serializers.SerializerMethodField(read_only=True)

    verified = serializers.SerializerMethodField(read_only=True)
    usuario_activo = serializers.SerializerMethodField(read_only=True)
    usuario_pendiente = serializers.SerializerMethodField(read_only=True)
    usuario_estado = serializers.SerializerMethodField(read_only=True)
    perfil_disponible = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Usuario

        fields = [
            "id",
            "autor_id",
            "nombres",
            "apellidos",
            "nombre_completo",
            "name",
            "rol_label",
            "es_externo",
            "sede_id",
            "sede",
            "carrera_id",
            "carrera",
            "facultad_id",
            "facultad",
            "org",
            "tags",
            "avatar_url",
            "avatar",
            "publicaciones_count",
            "publications",
            "verified",
            "usuario_activo",
            "usuario_pendiente",
            "usuario_estado",
            "perfil_disponible",
        ]

        read_only_fields = fields

    # ========================================================
    # IDENTIFICADOR CANÓNICO
    # ========================================================

    def get_id(self, obj):
        author = _safe_author(obj)
        return getattr(author, "pk", None) if author is not None else None

    def get_autor_id(self, obj):
        return self.get_id(obj)

    # ========================================================
    # NOMBRE Y ROL
    # ========================================================

    def get_nombre_completo(self, obj):
        return _build_full_name(obj) or "Investigador"

    def get_name(self, obj):
        return self.get_nombre_completo(obj)

    def get_rol_label(self, obj):
        get_role_display = getattr(obj, "get_rol_display", None)

        if callable(get_role_display):
            role_label = _optional_text(get_role_display())
            if role_label:
                return role_label

        return _optional_text(getattr(obj, "rol", None))

    def get_es_externo(self, obj):
        role = str(getattr(obj, "rol", "") or "").strip().lower()
        external_role = str(
            getattr(getattr(Usuario, "Rol", None), "AUTOR_EXTERNO", "autor_externo")
        ).strip().lower()

        author = _safe_author(obj)

        return bool(
            role == external_role
            or (
                author is not None
                and getattr(author, "es_externo", False)
            )
        )

    # ========================================================
    # SEDE, CARRERA Y FACULTAD
    # ========================================================

    def get_sede_id(self, obj):
        site = _site(obj)
        return getattr(site, "pk", None) if site is not None else None

    def get_sede(self, obj):
        site = _site(obj)
        return _optional_text(getattr(site, "nombre", None))

    def get_carrera_id(self, obj):
        career = _career(obj)
        return getattr(career, "pk", None) if career is not None else None

    def get_carrera(self, obj):
        career = _career(obj)
        return _optional_text(getattr(career, "nombre", None))

    def get_facultad_id(self, obj):
        faculty = _faculty(obj)
        return getattr(faculty, "pk", None) if faculty is not None else None

    def get_facultad(self, obj):
        faculty = _faculty(obj)
        return _optional_text(getattr(faculty, "nombre", None))

    def get_org(self, obj):
        author = _safe_author(obj)
        institution = _optional_text(getattr(author, "institucion", None))

        if institution:
            return institution

        values = _unique_text_list(
            [
                self.get_sede(obj),
                self.get_facultad(obj),
                self.get_carrera(obj),
            ]
        )

        return " · ".join(values) if values else None

    def get_tags(self, obj):
        return _unique_text_list(
            [
                self.get_sede(obj),
                self.get_facultad(obj),
                self.get_carrera(obj),
            ]
        )

    # ========================================================
    # AVATAR
    # ========================================================

    def get_avatar_url(self, obj):
        return _safe_file_url(
            getattr(obj, "avatar", None),
            request=self.context.get("request"),
        )

    def get_avatar(self, obj):
        return self.get_avatar_url(obj)

    # ========================================================
    # PRODUCCIÓN CIENTÍFICA
    # ========================================================

    def get_publicaciones_count(self, obj):
        return _publications_count(_safe_author(obj))

    def get_publications(self, obj):
        return self.get_publicaciones_count(obj)

    # ========================================================
    # ESTADO PÚBLICO DEL PERFIL
    # ========================================================

    def get_verified(self, obj):
        return bool(
            getattr(obj, "is_active", False)
            and getattr(obj, "perfil_completo", False)
        )

    def get_usuario_activo(self, obj):
        return bool(getattr(obj, "is_active", False))

    def get_usuario_pendiente(self, obj):
        # Este serializer se utiliza con buscar_usuarios(), que devuelve
        # únicamente cuentas activas. Se conserva el campo para mantener un
        # contrato estable con los resultados de AutorBusquedaSerializer.
        return False

    def get_usuario_estado(self, obj):
        return "activo" if getattr(obj, "is_active", False) else "inactivo"

    def get_perfil_disponible(self, obj):
        return _safe_author(obj) is not None