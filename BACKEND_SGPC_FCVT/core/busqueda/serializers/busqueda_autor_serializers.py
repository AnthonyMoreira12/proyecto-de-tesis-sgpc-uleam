"""
Serializer público para resultados rápidos de búsqueda de autores.

Este serializer expone únicamente información académica necesaria para
mostrar investigadores en resultados públicos y autocompletados.

Reglas principales:

- Autor.id es el identificador canónico del perfil científico.
- Los autores externos pendientes pueden aparecer en resultados porque
  pueden tener participaciones registradas.
- No se exponen cédulas, correos, identificadores internos del Usuario,
  origen de autenticación ni privilegios administrativos.
- La afiliación institucional se deriva del Autor y, cuando corresponde,
  de la sede, carrera y facultad del Usuario vinculado.
- El estado distingue cuentas pendientes, activas e inactivas sin exponer
  credenciales.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from core.models import Autor, Publicacion


User = get_user_model()


# ============================================================
# CONSTANTES
# ============================================================

ROLE_EXTERNAL_AUTHOR = getattr(
    getattr(User, "Rol", None),
    "AUTOR_EXTERNO",
    "autor_externo",
)

AUTH_SOURCE_LOCAL = getattr(
    getattr(User, "AuthSource", None),
    "LOCAL",
    "local",
)


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


def _normalize_account_value(value):
    """Normaliza valores internos como rol y fuente de acceso."""
    return str(value or "").strip().lower()


def _safe_user(author):
    """Obtiene de manera segura el Usuario vinculado."""
    if author is None or not getattr(author, "usuario_id", None):
        return None

    try:
        return author.usuario
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


def _build_full_name(author):
    """Construye el nombre completo del Autor."""
    if author is None:
        return None

    model_full_name = getattr(author, "nombre_completo", None)

    if callable(model_full_name):
        resolved = _optional_text(model_full_name())
        if resolved:
            return resolved

    if isinstance(model_full_name, str):
        resolved = _optional_text(model_full_name)
        if resolved:
            return resolved

    full_name = " ".join(
        value
        for value in (
            _optional_text(getattr(author, "nombres", None)),
            _optional_text(getattr(author, "apellidos", None)),
        )
        if value
    )

    return full_name or None


def _site(user):
    """Obtiene la sede del Usuario institucional vinculado."""
    return getattr(user, "sede", None) if user is not None else None


def _career(user):
    """Obtiene la carrera del Usuario vinculado."""
    return getattr(user, "carrera", None) if user is not None else None


def _faculty(user):
    """Obtiene la facultad mediante ``usuario.carrera.facultad``."""
    career = _career(user)
    return getattr(career, "facultad", None) if career is not None else None


def _has_usable_password(user):
    """Comprueba de forma segura si la cuenta recibió contraseña."""
    if user is None:
        return False

    try:
        return bool(user.has_usable_password())
    except (AttributeError, TypeError, ValueError):
        return False


def _is_pending_external_user(user):
    """
    Identifica una cuenta externa local que todavía no recibió acceso.

    Una cuenta pendiente está inactiva y no posee contraseña utilizable.
    """
    if user is None:
        return False

    role = _normalize_account_value(getattr(user, "rol", ""))
    auth_source = _normalize_account_value(
        getattr(user, "auth_source", "")
    )

    return bool(
        role == _normalize_account_value(ROLE_EXTERNAL_AUTHOR)
        and auth_source == _normalize_account_value(AUTH_SOURCE_LOCAL)
        and not bool(getattr(user, "is_active", False))
        and not _has_usable_password(user)
    )


def _resolve_user_state(user):
    """Devuelve ``sin_usuario``, ``pendiente``, ``activo`` o ``inactivo``."""
    if user is None:
        return "sin_usuario"

    if _is_pending_external_user(user):
        return "pendiente"

    if bool(getattr(user, "is_active", False)):
        return "activo"

    return "inactivo"


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

    prefetched = getattr(author, "_busqueda_participaciones", None)
    if prefetched is not None:
        publicacion_ids = {
            getattr(participation, "publicacion_id", None)
            for participation in prefetched
            if getattr(participation, "publicacion_id", None)
        }

        if not publicacion_ids:
            return 0

        try:
            return (
                Publicacion.objects
                .filter(
                    pk__in=publicacion_ids,
                    estado=(
                        Publicacion.ESTADO_APROBADA
                    ),
                )
                .count()
            )
        except (AttributeError, TypeError, ValueError):
            return 0

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


# ============================================================
# SERIALIZER
# ============================================================

class AutorBusquedaSerializer(serializers.ModelSerializer):
    """
    Representación pública y canónica de un investigador.

    El campo ``id`` siempre corresponde a ``Autor.id``. Esto conserva el
    vínculo correcto con perfiles y participaciones científicas.
    """

    autor_id = serializers.IntegerField(source="pk", read_only=True)

    nombre_completo = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    institucion = serializers.SerializerMethodField(read_only=True)
    org = serializers.SerializerMethodField(read_only=True)

    sede_id = serializers.SerializerMethodField(read_only=True)
    sede = serializers.SerializerMethodField(read_only=True)
    carrera_id = serializers.SerializerMethodField(read_only=True)
    carrera = serializers.SerializerMethodField(read_only=True)
    facultad_id = serializers.SerializerMethodField(read_only=True)
    facultad = serializers.SerializerMethodField(read_only=True)

    avatar_url = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    publicaciones_count = serializers.SerializerMethodField(read_only=True)
    publications = serializers.SerializerMethodField(read_only=True)

    tags = serializers.SerializerMethodField(read_only=True)
    verified = serializers.SerializerMethodField(read_only=True)

    usuario_activo = serializers.SerializerMethodField(read_only=True)
    usuario_pendiente = serializers.SerializerMethodField(read_only=True)
    usuario_estado = serializers.SerializerMethodField(read_only=True)
    perfil_disponible = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Autor

        fields = [
            "id",
            "autor_id",
            "nombres",
            "apellidos",
            "nombre_completo",
            "name",
            "institucion",
            "org",
            "sede_id",
            "sede",
            "carrera_id",
            "carrera",
            "facultad_id",
            "facultad",
            "avatar_url",
            "avatar",
            "publicaciones_count",
            "publications",
            "tags",
            "verified",
            "es_externo",
            "usuario_activo",
            "usuario_pendiente",
            "usuario_estado",
            "perfil_disponible",
        ]

        read_only_fields = fields

    # ========================================================
    # IDENTIDAD PÚBLICA
    # ========================================================

    def get_nombre_completo(self, obj):
        return _build_full_name(obj) or f"Autor #{obj.pk}"

    def get_name(self, obj):
        return self.get_nombre_completo(obj)

    # ========================================================
    # AFILIACIÓN
    # ========================================================

    def get_institucion(self, obj):
        return _optional_text(getattr(obj, "institucion", None))

    def get_org(self, obj):
        institution = self.get_institucion(obj)
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

    def get_sede_id(self, obj):
        user = _safe_user(obj)
        site = _site(user)
        return getattr(site, "pk", None) if site is not None else None

    def get_sede(self, obj):
        user = _safe_user(obj)
        site = _site(user)
        return _optional_text(getattr(site, "nombre", None))

    def get_carrera_id(self, obj):
        user = _safe_user(obj)
        career = _career(user)
        return getattr(career, "pk", None) if career is not None else None

    def get_carrera(self, obj):
        user = _safe_user(obj)
        career = _career(user)
        return _optional_text(getattr(career, "nombre", None))

    def get_facultad_id(self, obj):
        user = _safe_user(obj)
        faculty = _faculty(user)
        return getattr(faculty, "pk", None) if faculty is not None else None

    def get_facultad(self, obj):
        user = _safe_user(obj)
        faculty = _faculty(user)
        return _optional_text(getattr(faculty, "nombre", None))

    # ========================================================
    # AVATAR
    # ========================================================

    def get_avatar_url(self, obj):
        user = _safe_user(obj)
        return _safe_file_url(
            getattr(user, "avatar", None),
            request=self.context.get("request"),
        )

    def get_avatar(self, obj):
        return self.get_avatar_url(obj)

    # ========================================================
    # PRODUCCIÓN CIENTÍFICA
    # ========================================================

    def get_publicaciones_count(self, obj):
        return _publications_count(obj)

    def get_publications(self, obj):
        return self.get_publicaciones_count(obj)

    def get_tags(self, obj):
        return _unique_text_list(
            [
                self.get_sede(obj),
                self.get_facultad(obj),
                self.get_carrera(obj),
            ]
        )

    # ========================================================
    # ESTADO DEL PERFIL
    # ========================================================

    def get_verified(self, obj):
        user = _safe_user(obj)
        return bool(
            user is not None
            and getattr(user, "is_active", False)
            and getattr(user, "perfil_completo", False)
        )

    def get_usuario_activo(self, obj):
        user = _safe_user(obj)
        return bool(user is not None and getattr(user, "is_active", False))

    def get_usuario_pendiente(self, obj):
        return _is_pending_external_user(_safe_user(obj))

    def get_usuario_estado(self, obj):
        return _resolve_user_state(_safe_user(obj))

    def get_perfil_disponible(self, obj):
        # El perfil científico se construye desde Autor y sus
        # participaciones, incluso cuando la cuenta sigue pendiente.
        return bool(getattr(obj, "pk", None))