# core/admin/serializers/admin_usuarios_serializers.py
# ============================================================
# SGPC ULEAM — Serializer administrativo de usuarios
# ============================================================
#
# Expone información general del usuario, relación académica,
# avatar, estado de cuenta, vínculo con autor, publicaciones
# relacionadas y restricciones de edición del perfil.
# ============================================================

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AdminUsuarioSerializer(serializers.ModelSerializer):
    # ========================================================
    # DATOS CALCULADOS
    # ========================================================

    es_admin = serializers.SerializerMethodField(
        read_only=True,
    )

    avatar_url = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad_nombre = serializers.CharField(
        source="carrera.facultad.nombre",
        read_only=True,
        allow_null=True,
        default=None,
    )

    carrera_nombre = serializers.CharField(
        source="carrera.nombre",
        read_only=True,
        allow_null=True,
        default=None,
    )

    es_institucional = serializers.SerializerMethodField(
        read_only=True,
    )

    es_externo = serializers.SerializerMethodField(
        read_only=True,
    )

    es_pendiente = serializers.SerializerMethodField(
        read_only=True,
    )

    autor_id = serializers.SerializerMethodField(
        read_only=True,
    )

    tiene_autor = serializers.SerializerMethodField(
        read_only=True,
    )

    autor_nombre = serializers.SerializerMethodField(
        read_only=True,
    )

    total_publicaciones = serializers.SerializerMethodField(
        read_only=True,
    )

    publicaciones_relacionadas = serializers.SerializerMethodField(
        read_only=True,
    )

    profile_edit_until = serializers.DateTimeField(
        read_only=True,
        allow_null=True,
    )

    profile_edit_attempts_left = serializers.IntegerField(
        read_only=True,
    )

    profile_edit_locked = serializers.BooleanField(
        read_only=True,
    )

    profile_edit_lock_reason = serializers.CharField(
        read_only=True,
        allow_null=True,
    )

    # ========================================================
    # META
    # ========================================================

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

            # Fotografía del usuario
            "avatar_url",

            # Relación académica
            "carrera",
            "facultad_nombre",
            "carrera_nombre",

            # Estado de perfil
            "perfil_completo",
            "creado_desde_selector",
            "profile_edit_until",
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",

            # Estado de acceso
            "is_active",
            "is_staff",
            "is_superuser",
            "es_admin",

            # Clasificación
            "es_institucional",
            "es_externo",
            "es_pendiente",

            # Relación con autor y publicaciones
            "autor_id",
            "tiene_autor",
            "autor_nombre",
            "total_publicaciones",
            "publicaciones_relacionadas",
        ]

        read_only_fields = [
            "id",
            "is_superuser",
            "es_admin",
            "avatar_url",
            "facultad_nombre",
            "carrera_nombre",
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
            "carrera": {
                "required": False,
                "allow_null": True,
            },
            "identificacion": {
                "required": False,
                "allow_null": True,
            },
        }

    # ========================================================
    # HELPERS
    # ========================================================

    def _get_autor(self, obj):
        try:
            return obj.autor
        except Exception:
            return None

    # ========================================================
    # AVATAR
    # ========================================================

    def get_avatar_url(self, obj):
        """
        Devuelve la URL absoluta del avatar.

        Ejemplo:
        http://127.0.0.1:8000/media/avatars/foto.jpg

        Si el usuario no tiene avatar, devuelve None para que
        el frontend muestre las iniciales.
        """

        avatar = getattr(
            obj,
            "avatar",
            None,
        )

        if not avatar:
            return None

        avatar_name = getattr(
            avatar,
            "name",
            None,
        )

        avatar_url = getattr(
            avatar,
            "url",
            None,
        )

        if not avatar_name or not avatar_url:
            return None

        request = self.context.get(
            "request",
        )

        if request:
            try:
                return request.build_absolute_uri(
                    avatar_url
                )
            except Exception:
                pass

        return avatar_url

    # ========================================================
    # CLASIFICACIÓN DEL USUARIO
    # ========================================================

    def get_es_admin(self, obj):
        return bool(
            obj.is_superuser
            or obj.is_staff
        )

    def get_es_institucional(self, obj):
        return (
            str(
                obj.auth_source
                or ""
            ).lower()
            == "microsoft"
        )

    def get_es_externo(self, obj):
        return (
            str(
                obj.rol
                or ""
            ).lower()
            == "autor_externo"
        )

    def get_es_pendiente(self, obj):
        return (
            str(
                obj.rol
                or ""
            ).lower()
            == "autor_externo"
            and str(
                obj.auth_source
                or ""
            ).lower()
            == "local"
            and not bool(
                obj.is_active
            )
        )

    # ========================================================
    # AUTOR VINCULADO
    # ========================================================

    def get_autor_id(self, obj):
        autor = self._get_autor(
            obj
        )

        return getattr(
            autor,
            "id",
            None,
        )

    def get_tiene_autor(self, obj):
        return (
            self._get_autor(obj)
            is not None
        )

    def get_autor_nombre(self, obj):
        autor = self._get_autor(
            obj
        )

        if not autor:
            return None

        nombre = (
            f"{autor.nombres or ''} "
            f"{autor.apellidos or ''}"
        ).strip()

        return nombre or None

    # ========================================================
    # PUBLICACIONES
    # ========================================================

    def get_total_publicaciones(self, obj):
        autor = self._get_autor(
            obj
        )

        if not autor:
            return 0

        try:
            return len(
                list(
                    autor.participaciones.all()
                )
            )
        except Exception:
            return 0

    def get_publicaciones_relacionadas(self, obj):
        autor = self._get_autor(
            obj
        )

        if not autor:
            return []

        try:
            participaciones = list(
                autor.participaciones.all()
            )
        except Exception:
            return []

        data = []

        for relacion in participaciones:
            publicacion = getattr(
                relacion,
                "publicacion",
                None,
            )

            if not publicacion:
                continue

            tipo_obj = getattr(
                publicacion,
                "tipo",
                None,
            )

            tipo = getattr(
                tipo_obj,
                "nombre",
                "Publicación",
            )

            numero = (
                publicacion.numero
                if publicacion.numero is not None
                else "s/n"
            )

            anio = getattr(
                publicacion,
                "anio_publicacion",
                None,
            )

            rol = getattr(
                relacion,
                "rol_autoria",
                None,
            )

            orden = getattr(
                relacion,
                "orden",
                None,
            )

            if rol == "principal":
                rol_label = "Principal"
            else:
                rol_label = (
                    f"Coautor #{orden}"
                    if orden
                    else "Coautor"
                )

            data.append(
                {
                    "publicacion_id": (
                        publicacion.id
                    ),
                    "tipo": tipo,
                    "numero": numero,
                    "anio_publicacion": anio,
                    "rol_autoria": rol,
                    "rol_label": rol_label,
                    "orden": orden,
                    "label": (
                        f"{tipo} #{numero}"
                    ),
                }
            )

        return data

    # ========================================================
    # VALIDACIONES DE CAMPOS
    # ========================================================

    def validate_email(self, value):
        return (
            value
            or ""
        ).strip().lower()

    def validate_identificacion(self, value):
        if value in (
            None,
            "",
        ):
            return None

        identificacion = str(
            value
        ).strip()

        if (
            not identificacion.isdigit()
            or len(identificacion) != 10
        ):
            raise serializers.ValidationError(
                (
                    "La identificación debe tener "
                    "10 dígitos numéricos."
                )
            )

        return identificacion

    # ========================================================
    # VALIDACIÓN GENERAL
    # ========================================================

    def validate(self, attrs):
        instance = getattr(
            self,
            "instance",
            None,
        )

        rol = str(
            attrs.get(
                "rol",
                getattr(
                    instance,
                    "rol",
                    "",
                )
                if instance
                else "",
            )
            or ""
        ).strip().lower()

        auth_source = str(
            attrs.get(
                "auth_source",
                getattr(
                    instance,
                    "auth_source",
                    "",
                )
                if instance
                else "",
            )
            or ""
        ).strip().lower()

        carrera = attrs.get(
            "carrera",
            getattr(
                instance,
                "carrera",
                None,
            )
            if instance
            else None,
        )

        if rol and rol not in (
            "autor",
            "autor_externo",
        ):
            raise serializers.ValidationError(
                {
                    "rol": (
                        "Rol inválido. Use 'autor' "
                        "o 'autor_externo'."
                    )
                }
            )

        if auth_source and auth_source not in (
            "local",
            "microsoft",
        ):
            raise serializers.ValidationError(
                {
                    "auth_source": (
                        "Origen de autenticación inválido. "
                        "Use 'local' o 'microsoft'."
                    )
                }
            )

        if (
            auth_source == "microsoft"
            and rol
            and rol != "autor"
        ):
            raise serializers.ValidationError(
                {
                    "rol": (
                        "Un usuario Microsoft debe "
                        "ser 'autor'."
                    )
                }
            )

        if (
            rol == "autor_externo"
            and auth_source
            and auth_source != "local"
        ):
            raise serializers.ValidationError(
                {
                    "auth_source": (
                        "Un autor externo debe ser "
                        "'local'."
                    )
                }
            )

        if rol == "autor_externo":
            if carrera is not None:
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Un usuario externo no debe "
                            "tener carrera asignada."
                        )
                    }
                )

            return attrs

        return attrs