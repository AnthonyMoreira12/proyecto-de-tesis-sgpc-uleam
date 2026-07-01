# Serializer administrativo de usuarios:
# expone información del usuario, su carrera, estado de cuenta, vínculo con autor,
# publicaciones relacionadas y validaciones para roles, autenticación e identificación.

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AdminUsuarioSerializer(serializers.ModelSerializer):
    es_admin = serializers.SerializerMethodField(read_only=True)

    # Ahora lee la facultad a través de la carrera
    facultad_nombre = serializers.CharField(source="carrera.facultad.nombre", read_only=True)
    carrera_nombre = serializers.CharField(source="carrera.nombre", read_only=True)

    es_institucional = serializers.SerializerMethodField(read_only=True)
    es_externo = serializers.SerializerMethodField(read_only=True)
    es_pendiente = serializers.SerializerMethodField(read_only=True)

    autor_id = serializers.SerializerMethodField(read_only=True)
    tiene_autor = serializers.SerializerMethodField(read_only=True)
    autor_nombre = serializers.SerializerMethodField(read_only=True)
    total_publicaciones = serializers.SerializerMethodField(read_only=True)
    publicaciones_relacionadas = serializers.SerializerMethodField(read_only=True)

    profile_edit_until = serializers.DateTimeField(read_only=True, allow_null=True)
    profile_edit_attempts_left = serializers.IntegerField(read_only=True)
    profile_edit_locked = serializers.BooleanField(read_only=True)
    profile_edit_lock_reason = serializers.CharField(read_only=True, allow_null=True)

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
            "carrera",
            "facultad_nombre",
            "carrera_nombre",
            "perfil_completo",
            "creado_desde_selector",
            "profile_edit_until",
            "profile_edit_attempts_left",
            "profile_edit_locked",
            "profile_edit_lock_reason",
            "is_active",
            "is_staff",
            "is_superuser",
            "es_admin",
            "es_institucional",
            "es_externo",
            "es_pendiente",
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
            "carrera": {"required": False, "allow_null": True},
            "identificacion": {"required": False, "allow_null": True},
        }

    def _get_autor(self, obj):
        try:
            return obj.autor
        except Exception:
            return None

    def get_es_admin(self, obj):
        return bool(obj.is_superuser or obj.is_staff)

    def get_es_institucional(self, obj):
        return str(obj.auth_source).lower() == "microsoft"

    def get_es_externo(self, obj):
        return str(obj.rol).lower() == "autor_externo"

    def get_es_pendiente(self, obj):
        return (
            str(obj.rol).lower() == "autor_externo"
            and str(obj.auth_source).lower() == "local"
            and not bool(obj.is_active)
        )

    def get_autor_id(self, obj):
        autor = self._get_autor(obj)
        return getattr(autor, "id", None)

    def get_tiene_autor(self, obj):
        return self._get_autor(obj) is not None

    def get_autor_nombre(self, obj):
        autor = self._get_autor(obj)
        if not autor:
            return None
        return f"{autor.nombres or ''} {autor.apellidos or ''}".strip()

    def get_total_publicaciones(self, obj):
        autor = self._get_autor(obj)
        if not autor:
            return 0
        try:
            return len(list(autor.participaciones.all()))
        except Exception:
            return 0

    def get_publicaciones_relacionadas(self, obj):
        autor = self._get_autor(obj)
        if not autor:
            return []

        try:
            participaciones = list(autor.participaciones.all())
        except Exception:
            return []

        data = []

        for rel in participaciones:
            publicacion = getattr(rel, "publicacion", None)
            if not publicacion:
                continue

            tipo = getattr(getattr(publicacion, "tipo", None), "nombre", "Publicación")
            numero = publicacion.numero if publicacion.numero is not None else "s/n"
            anio = getattr(publicacion, "anio_publicacion", None)
            rol = getattr(rel, "rol_autoria", None)
            orden = getattr(rel, "orden", None)

            if rol == "principal":
                rol_label = "Principal"
            else:
                rol_label = f"Coautor #{orden}" if orden else "Coautor"

            data.append(
                {
                    "publicacion_id": publicacion.id,
                    "tipo": tipo,
                    "numero": numero,
                    "anio_publicacion": anio,
                    "rol_autoria": rol,
                    "rol_label": rol_label,
                    "orden": orden,
                    "label": f"{tipo} #{numero}",
                }
            )

        return data

    def validate_email(self, value):
        return (value or "").strip().lower()

    def validate_identificacion(self, value):
        if value in (None, ""):
            return None

        v = str(value).strip()
        if not v.isdigit() or len(v) != 10:
            raise serializers.ValidationError(
                "La identificación debe tener 10 dígitos numéricos."
            )
        return v

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        rol = str(
            attrs.get("rol", getattr(instance, "rol", "") if instance else "") or ""
        ).strip().lower()

        auth_source = str(
            attrs.get(
                "auth_source",
                getattr(instance, "auth_source", "") if instance else "",
            )
            or ""
        ).strip().lower()

        carrera = attrs.get(
            "carrera",
            getattr(instance, "carrera", None) if instance else None,
        )

        if rol and rol not in ("autor", "autor_externo"):
            raise serializers.ValidationError(
                {"rol": "Rol inválido. Use 'autor' o 'autor_externo'."}
            )

        if auth_source and auth_source not in ("local", "microsoft"):
            raise serializers.ValidationError(
                {
                    "auth_source": (
                        "Origen de autenticación inválido. "
                        "Use 'local' o 'microsoft'."
                    )
                }
            )

        if auth_source == "microsoft" and rol and rol != "autor":
            raise serializers.ValidationError(
                {"rol": "Un usuario Microsoft debe ser 'autor'."}
            )

        if rol == "autor_externo" and auth_source and auth_source != "local":
            raise serializers.ValidationError(
                {"auth_source": "Un autor externo debe ser 'local'."}
            )

        if rol == "autor_externo":
            if carrera is not None:
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Un usuario externo no debe tener carrera asignada."
                        )
                    }
                )
            return attrs

        return attrs