"""Serializer administrativo de usuarios."""

import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

CEDULA_PATTERN = re.compile(r"^\d{10}$")

ROLE_INSTITUTIONAL = "autor"
ROLE_EXTERNAL = "autor_externo"

AUTH_SOURCE_LOCAL = "local"
AUTH_SOURCE_MICROSOFT = "microsoft"


# ============================================================
# UTILIDADES
# ============================================================

def _text(value):
    """
    Normaliza un valor textual.
    """
    return str(value or "").strip()


def _normalized_role(user):
    """
    Retorna el rol normalizado del usuario.
    """
    return _text(
        getattr(
            user,
            "rol",
            "",
        )
    ).lower()


def _normalized_auth_source(user):
    """
    Retorna el origen de autenticación normalizado.
    """
    return _text(
        getattr(
            user,
            "auth_source",
            "",
        )
    ).lower()


def _is_institutional_user(user):
    """
    Determina si la cuenta es institucional.

    Una cuenta es institucional únicamente cuando:

    - rol = autor
    - auth_source = microsoft

    El permiso administrativo no modifica esta clasificación.
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user)
        == ROLE_INSTITUTIONAL
        and _normalized_auth_source(user)
        == AUTH_SOURCE_MICROSOFT
    )


def _is_external_user(user):
    """
    Determina si la cuenta es externa.

    Una cuenta es externa únicamente cuando:

    - rol = autor_externo
    - auth_source = local

    El permiso administrativo no modifica esta clasificación.
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user)
        == ROLE_EXTERNAL
        and _normalized_auth_source(user)
        == AUTH_SOURCE_LOCAL
    )


def _is_pending_external_user(user):
    """
    Determina si una cuenta externa todavía está pendiente de
    activación. Una cuenta externa desactivada que ya posee una
    contraseña utilizable no debe volver a clasificarse como
    pendiente.
    """
    if (
        not _is_external_user(user)
        or getattr(user, "is_active", False)
    ):
        return False

    try:
        return not user.has_usable_password()
    except (AttributeError, TypeError, ValueError):
        return False


def _publication_title(publication):
    """
    Resuelve el título real según el subtipo de publicación.

    Publicacion no almacena un campo ``titulo`` propio; el valor
    se encuentra en Articulo, Ponencia, Libro o CapituloLibro.
    """
    if publication is None:
        return None

    candidates = (
        ("articulo", "nombre_articulo"),
        ("ponencia", "nombre_ponencia"),
        ("libro", "nombre_libro"),
        ("capitulo_libro", "nombre_capitulo"),
    )

    for relation_name, field_name in candidates:
        try:
            related = getattr(
                publication,
                relation_name,
                None,
            )
        except ObjectDoesNotExist:
            related = None

        title = _text(
            getattr(
                related,
                field_name,
                "",
            )
        )

        if title:
            return title

    try:
        project = getattr(
            publication,
            "proyecto",
            None,
        )
    except ObjectDoesNotExist:
        project = None

    return (
        _text(
            getattr(
                project,
                "nombre",
                "",
            )
        )
        or None
    )


def _has_valid_cedula(user):
    """
    Comprueba que el usuario tenga una cédula válida en cuanto
    a formato: exactamente 10 dígitos numéricos.
    """
    cedula = _text(
        getattr(
            user,
            "identificacion",
            "",
        )
    )

    return bool(
        CEDULA_PATTERN.fullmatch(
            cedula
        )
    )


def _calculate_profile_complete(user):
    """
    Calcula la completitud efectiva del perfil.

    Externo:
        Requiere cédula.

    Institucional:
        Requiere cédula y Carrera.

    Otras combinaciones:
        No se consideran perfiles completos.
    """
    if user is None:
        return False

    cedula_complete = _has_valid_cedula(
        user
    )

    if _is_external_user(user):
        return cedula_complete

    if _is_institutional_user(user):
        return bool(
            cedula_complete
            and getattr(
                user,
                "carrera_id",
                None,
            )
        )

    return False


# ============================================================
# SERIALIZER
# ============================================================

class AdminUsuarioSerializer(
    serializers.ModelSerializer
):
    """
    Serializer utilizado por la administración de usuarios.

    Reglas principales:

    - Solo se admiten cédulas de 10 dígitos.
    - Solo los usuarios institucionales pueden tener Carrera.
    - La Facultad se deriva desde Carrera.
    - Los permisos administrativos son independientes del tipo
      de cuenta.
    """

    # ========================================================
    # CLASIFICACIÓN Y PERMISOS
    # ========================================================

    es_admin = serializers.SerializerMethodField(
        read_only=True,
    )

    es_institucional = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    es_externo = serializers.SerializerMethodField(
        read_only=True,
    )

    es_pendiente = serializers.SerializerMethodField(
        read_only=True,
    )

    perfil_completo = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    # ========================================================
    # AVATAR
    # ========================================================

    avatar_url = serializers.SerializerMethodField(
        read_only=True,
    )

    # ========================================================
    # RELACIÓN ACADÉMICA
    # ========================================================

    facultad_id = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad_nombre = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    carrera_nombre = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    # ========================================================
    # AUTOR Y PUBLICACIONES
    # ========================================================

    autor_id = serializers.SerializerMethodField(
        read_only=True,
    )

    tiene_autor = serializers.SerializerMethodField(
        read_only=True,
    )

    autor_nombre = serializers.SerializerMethodField(
        read_only=True,
    )

    total_publicaciones = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    publicaciones_relacionadas = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "nombres",
            "apellidos",
            "identificacion",
            "rol",
            "auth_source",
            "avatar_url",

            # Relación académica
            "facultad_id",
            "facultad_nombre",
            "carrera",
            "carrera_nombre",

            # Perfil
            "perfil_completo",
            "creado_desde_selector",

            # Control de edición
            "profile_edit_until",
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",

            # Estado y permisos
            "is_active",
            "is_staff",
            "is_superuser",
            "es_admin",

            # Clasificación
            "es_institucional",
            "es_externo",
            "es_pendiente",

            # Autor
            "autor_id",
            "tiene_autor",
            "autor_nombre",

            # Publicaciones
            "total_publicaciones",
            "publicaciones_relacionadas",
        ]

        read_only_fields = [
            "id",
            "is_superuser",
            "es_admin",
            "avatar_url",

            "facultad_id",
            "facultad_nombre",
            "carrera_nombre",

            "perfil_completo",
            "es_institucional",
            "es_externo",
            "es_pendiente",

            "creado_desde_selector",

            "profile_edit_until",
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",

            "autor_id",
            "tiene_autor",
            "autor_nombre",

            "total_publicaciones",
            "publicaciones_relacionadas",
        ]

        extra_kwargs = {
            "email": {
                "required": True,
                "allow_blank": False,
                "trim_whitespace": True,
            },

            "nombres": {
                "required": True,
                "allow_blank": False,
                "trim_whitespace": True,
            },

            "apellidos": {
                "required": True,
                "allow_blank": False,
                "trim_whitespace": True,
            },

            "identificacion": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
                "trim_whitespace": True,
            },

            "carrera": {
                "required": False,
                "allow_null": True,
            },

            "rol": {
                "required": False,
            },

            "auth_source": {
                "required": False,
            },

            "is_active": {
                "required": False,
            },

            "is_staff": {
                "required": False,
            },
        }

    # ========================================================
    # AUTOR
    # ========================================================

    def _author(
        self,
        obj,
    ):
        """
        Obtiene el Autor vinculado al Usuario.
        """
        prefetched = getattr(
            obj,
            "autor_admin",
            None,
        )

        if prefetched is not None:
            return prefetched

        try:
            return obj.autor

        except (
            ObjectDoesNotExist,
            AttributeError,
        ):
            return None

    def _participations(
        self,
        author,
    ):
        """
        Obtiene las participaciones del Autor.
        """
        if author is None:
            return []

        prefetched = getattr(
            author,
            "participaciones_admin",
            None,
        )

        if prefetched is not None:
            return list(
                prefetched
            )

        cache = getattr(
            author,
            "_prefetched_objects_cache",
            {},
        )

        if "participaciones" in cache:
            return list(
                cache[
                    "participaciones"
                ]
            )

        return list(
            author.participaciones
            .select_related(
                "publicacion",
                "publicacion__tipo",
            )
            .order_by(
                "orden",
                "id",
            )
        )

    # ========================================================
    # CLASIFICACIÓN
    # ========================================================

    def get_es_admin(
        self,
        obj,
    ):
        return bool(
            getattr(
                obj,
                "is_staff",
                False,
            )
            or getattr(
                obj,
                "is_superuser",
                False,
            )
        )

    def get_es_institucional(
        self,
        obj,
    ):
        return _is_institutional_user(
            obj
        )

    def get_es_externo(
        self,
        obj,
    ):
        return _is_external_user(
            obj
        )

    def get_es_pendiente(
        self,
        obj,
    ):
        return _is_pending_external_user(
            obj
        )

    def get_perfil_completo(
        self,
        obj,
    ):
        return _calculate_profile_complete(
            obj
        )

    # ========================================================
    # AVATAR
    # ========================================================

    def get_avatar_url(
        self,
        obj,
    ):
        avatar = getattr(
            obj,
            "avatar",
            None,
        )

        if (
            not avatar
            or not getattr(
                avatar,
                "name",
                None,
            )
        ):
            return None

        try:
            url = avatar.url

        except (
            ValueError,
            OSError,
        ):
            return None

        request = self.context.get(
            "request"
        )

        if request is None:
            return url

        try:
            return request.build_absolute_uri(
                url
            )

        except (
            ValueError,
            TypeError,
        ):
            return url

    # ========================================================
    # RELACIÓN ACADÉMICA
    # ========================================================

    def get_facultad_id(
        self,
        obj,
    ):
        if not _is_institutional_user(
            obj
        ):
            return None

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

    def get_facultad_nombre(
        self,
        obj,
    ):
        if not _is_institutional_user(
            obj
        ):
            return None

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

        return (
            _text(
                getattr(
                    faculty,
                    "nombre",
                    "",
                )
            )
            or None
        )

    def get_carrera_nombre(
        self,
        obj,
    ):
        if not _is_institutional_user(
            obj
        ):
            return None

        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        return (
            _text(
                getattr(
                    career,
                    "nombre",
                    "",
                )
            )
            or None
        )

    # ========================================================
    # AUTOR
    # ========================================================

    def get_autor_id(
        self,
        obj,
    ):
        return getattr(
            self._author(
                obj
            ),
            "pk",
            None,
        )

    def get_tiene_autor(
        self,
        obj,
    ):
        return self._author(
            obj
        ) is not None

    def get_autor_nombre(
        self,
        obj,
    ):
        author = self._author(
            obj
        )

        if author is None:
            return None

        name = " ".join(
            part
            for part in [
                _text(
                    getattr(
                        author,
                        "nombres",
                        "",
                    )
                ),
                _text(
                    getattr(
                        author,
                        "apellidos",
                        "",
                    )
                ),
            ]
            if part
        )

        return (
            name
            or _text(
                getattr(
                    author,
                    "correo",
                    "",
                )
            )
            or None
        )

    # ========================================================
    # PUBLICACIONES
    # ========================================================

    def get_total_publicaciones(
        self,
        obj,
    ):
        annotated = getattr(
            obj,
            "total_publicaciones",
            None,
        )

        if annotated is not None:
            try:
                return int(
                    annotated
                )

            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                pass

        return len(
            self._participations(
                self._author(
                    obj
                )
            )
        )

    def get_publicaciones_relacionadas(
        self,
        obj,
    ):
        output = []

        author = self._author(
            obj
        )

        for relation in self._participations(
            author
        ):
            publication = getattr(
                relation,
                "publicacion",
                None,
            )

            if publication is None:
                continue

            publication_type = getattr(
                publication,
                "tipo",
                None,
            )

            type_name = (
                _text(
                    getattr(
                        publication_type,
                        "nombre",
                        "",
                    )
                )
                or "Publicación"
            )

            type_code = (
                _text(
                    getattr(
                        publication_type,
                        "codigo",
                        "",
                    )
                )
                or None
            )

            title = _publication_title(
                publication
            )

            publication_number = getattr(
                publication,
                "numero",
                None,
            )

            if title:
                label = title

            elif publication_number:
                label = (
                    f"{type_name} "
                    f"N.º {publication_number}"
                )

            else:
                label = type_name

            order = getattr(
                relation,
                "orden",
                None,
            )

            role = _text(
                getattr(
                    relation,
                    "rol_autoria",
                    "",
                )
            ).lower()

            principal = bool(
                role == "principal"
                or order == 1
            )

            output.append(
                {
                    "publicacion_id": (
                        publication.pk
                    ),

                    "titulo": title,

                    "label": label,

                    "tipo": type_name,

                    "tipo_codigo": type_code,

                    "numero": (
                        publication_number
                    ),

                    "anio_publicacion": (
                        getattr(
                            publication,
                            "anio_publicacion",
                            None,
                        )
                    ),

                    "rol_autoria": (
                        "principal"
                        if principal
                        else "coautor"
                    ),

                    "rol_label": (
                        "Principal"
                        if principal
                        else (
                            f"Coautor #{order}"
                            if order
                            else "Coautor"
                        )
                    ),

                    "orden": order,
                }
            )

        return output

    # ========================================================
    # VALIDACIÓN DE CORREO
    # ========================================================

    def validate_email(
        self,
        value,
    ):
        email = (
            User.objects.normalize_email(
                str(
                    value or ""
                )
            )
            .strip()
            .lower()
        )

        if not email:
            raise serializers.ValidationError(
                (
                    "El correo electrónico "
                    "es obligatorio."
                )
            )

        duplicates = User.objects.filter(
            email__iexact=email
        )

        if self.instance is not None:
            duplicates = duplicates.exclude(
                pk=self.instance.pk
            )

        if duplicates.exists():
            raise serializers.ValidationError(
                (
                    "Ya existe un usuario con "
                    "este correo electrónico."
                )
            )

        return email

    # ========================================================
    # VALIDACIÓN DE NOMBRES
    # ========================================================

    def validate_nombres(
        self,
        value,
    ):
        normalized = " ".join(
            str(
                value or ""
            ).split()
        )

        if not normalized:
            raise serializers.ValidationError(
                "Los nombres son obligatorios."
            )

        if len(normalized) > 100:
            raise serializers.ValidationError(
                (
                    "Los nombres no pueden superar "
                    "los 100 caracteres."
                )
            )

        return normalized

    def validate_apellidos(
        self,
        value,
    ):
        normalized = " ".join(
            str(
                value or ""
            ).split()
        )

        if not normalized:
            raise serializers.ValidationError(
                "Los apellidos son obligatorios."
            )

        if len(normalized) > 100:
            raise serializers.ValidationError(
                (
                    "Los apellidos no pueden superar "
                    "los 100 caracteres."
                )
            )

        return normalized

    # ========================================================
    # VALIDACIÓN DE CÉDULA
    # ========================================================

    def validate_identificacion(
        self,
        value,
    ):
        cedula = _text(
            value
        )

        # La creación administrativa actual registra
        # exclusivamente usuarios externos y requiere cédula.
        if not cedula:
            if self.instance is None:
                raise serializers.ValidationError(
                    (
                        "El número de cédula "
                        "es obligatorio."
                    )
                )

            return None

        if not CEDULA_PATTERN.fullmatch(
            cedula
        ):
            raise serializers.ValidationError(
                (
                    "La cédula debe contener exactamente "
                    "10 dígitos numéricos."
                )
            )

        duplicates = User.objects.filter(
            identificacion=cedula
        )

        if self.instance is not None:
            duplicates = duplicates.exclude(
                pk=self.instance.pk
            )

        if duplicates.exists():
            raise serializers.ValidationError(
                (
                    "Ya existe un usuario registrado "
                    "con esta cédula."
                )
            )

        return cedula

    # ========================================================
    # VALIDACIÓN GENERAL
    # ========================================================

    def validate(
        self,
        attrs,
    ):
        """
        Valida la combinación entre rol, autenticación y Carrera.

        Solamente los usuarios institucionales pueden tener una
        Carrera asignada.
        """
        instance = self.instance

        role = _text(
            attrs.get(
                "rol",
                getattr(
                    instance,
                    "rol",
                    ROLE_INSTITUTIONAL,
                ),
            )
        ).lower()

        source = _text(
            attrs.get(
                "auth_source",
                getattr(
                    instance,
                    "auth_source",
                    AUTH_SOURCE_LOCAL,
                ),
            )
        ).lower()

        career_was_sent = (
            "carrera"
            in attrs
        )

        career = attrs.get(
            "carrera",
            getattr(
                instance,
                "carrera",
                None,
            ),
        )

        is_institutional = bool(
            role == ROLE_INSTITUTIONAL
            and source
            == AUTH_SOURCE_MICROSOFT
        )

        is_external = bool(
            role == ROLE_EXTERNAL
            and source
            == AUTH_SOURCE_LOCAL
        )

        if (
            source
            == AUTH_SOURCE_MICROSOFT
            and role
            != ROLE_INSTITUTIONAL
        ):
            raise serializers.ValidationError(
                {
                    "rol": (
                        "Un usuario Microsoft debe tener "
                        "el rol de autor institucional."
                    )
                }
            )

        if (
            role == ROLE_EXTERNAL
            and source
            != AUTH_SOURCE_LOCAL
        ):
            raise serializers.ValidationError(
                {
                    "auth_source": (
                        "Un autor externo debe utilizar "
                        "autenticación local."
                    )
                }
            )

        if (
            career is not None
            and not is_institutional
        ):
            message = (
                "Solo los usuarios institucionales "
                "autenticados mediante Microsoft pueden "
                "tener una carrera asignada."
            )

            raise serializers.ValidationError(
                {
                    "carrera": message,
                }
            )

        # Si existen datos antiguos inconsistentes y se edita
        # una cuenta no institucional sin enviar Carrera, se
        # elimina automáticamente la relación residual.
        if (
            not is_institutional
            and not career_was_sent
            and instance is not None
            and getattr(
                instance,
                "carrera_id",
                None,
            )
        ):
            attrs["carrera"] = None

        # Para cuentas externas se asegura que nunca quede una
        # Carrera asignada.
        if is_external:
            attrs["carrera"] = None

        attrs["rol"] = role
        attrs["auth_source"] = source

        return attrs

    # ========================================================
    # REPRESENTACIÓN
    # ========================================================

    def to_representation(
        self,
        instance,
    ):
        """
        Evita exponer relaciones académicas residuales de
        usuarios externos o no institucionales.
        """
        data = super().to_representation(
            instance
        )

        if not _is_institutional_user(
            instance
        ):
            data["facultad_id"] = None
            data["facultad_nombre"] = None
            data["carrera"] = None
            data["carrera_nombre"] = None

        return data

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def update(
        self,
        instance,
        validated_data,
    ):
        """
        Actualiza el usuario y recalcula la completitud efectiva
        del perfil.
        """
        updated_user = super().update(
            instance,
            validated_data,
        )

        profile_complete = (
            _calculate_profile_complete(
                updated_user
            )
        )

        if (
            updated_user.perfil_completo
            != profile_complete
        ):
            updated_user.perfil_completo = (
                profile_complete
            )

            updated_user.save(
                update_fields=[
                    "perfil_completo",
                ]
            )

        return updated_user