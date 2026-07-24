"""Serializer administrativo de usuarios."""

import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


User = get_user_model()


def _text(value):
    return str(value or "").strip()


class AdminUsuarioSerializer(serializers.ModelSerializer):
    es_admin = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
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
    es_institucional = serializers.SerializerMethodField()
    es_externo = serializers.SerializerMethodField()
    es_pendiente = serializers.SerializerMethodField()
    autor_id = serializers.SerializerMethodField()
    tiene_autor = serializers.SerializerMethodField()
    autor_nombre = serializers.SerializerMethodField()
    total_publicaciones = serializers.SerializerMethodField()
    publicaciones_relacionadas = serializers.SerializerMethodField()

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
            "identificacion": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "carrera": {
                "required": False,
                "allow_null": True,
            },
        }

    def _author(self, obj):
        prefetched = getattr(obj, "autor_admin", None)
        if prefetched is not None:
            return prefetched

        try:
            return obj.autor
        except (ObjectDoesNotExist, AttributeError):
            return None

    def _participations(self, author):
        if author is None:
            return []

        prefetched = getattr(author, "participaciones_admin", None)
        if prefetched is not None:
            return list(prefetched)

        cache = getattr(author, "_prefetched_objects_cache", {})
        if "participaciones" in cache:
            return list(cache["participaciones"])

        return list(
            author.participaciones
            .select_related("publicacion", "publicacion__tipo")
            .order_by("orden", "id")
        )

    def get_es_admin(self, obj):
        return bool(obj.is_staff or obj.is_superuser)

    def get_avatar_url(self, obj):
        avatar = getattr(obj, "avatar", None)

        if not avatar or not getattr(avatar, "name", None):
            return None

        try:
            url = avatar.url
        except (ValueError, OSError):
            return None

        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_es_institucional(self, obj):
        return _text(obj.auth_source).lower() == "microsoft"

    def get_es_externo(self, obj):
        return _text(obj.rol).lower() == "autor_externo"

    def get_es_pendiente(self, obj):
        return bool(
            self.get_es_externo(obj)
            and _text(obj.auth_source).lower() == "local"
            and not obj.is_active
        )

    def get_autor_id(self, obj):
        return getattr(self._author(obj), "pk", None)

    def get_tiene_autor(self, obj):
        return self._author(obj) is not None

    def get_autor_nombre(self, obj):
        author = self._author(obj)

        if author is None:
            return None

        name = " ".join(
            part
            for part in [
                _text(author.nombres),
                _text(author.apellidos),
            ]
            if part
        )
        return name or _text(author.correo) or None

    def get_total_publicaciones(self, obj):
        annotated = getattr(obj, "total_publicaciones", None)

        if annotated is not None:
            return int(annotated)

        return len(self._participations(self._author(obj)))

    def get_publicaciones_relacionadas(self, obj):
        output = []

        for relation in self._participations(self._author(obj)):
            publication = getattr(relation, "publicacion", None)

            if publication is None:
                continue

            publication_type = getattr(publication, "tipo", None)
            type_name = _text(
                getattr(publication_type, "nombre", "")
            ) or "Publicación"
            order = getattr(relation, "orden", None)
            role = _text(
                getattr(relation, "rol_autoria", "")
            ).lower()
            principal = role == "principal" or order == 1

            output.append(
                {
                    "publicacion_id": publication.pk,
                    "tipo": type_name,
                    "tipo_codigo": _text(
                        getattr(publication_type, "codigo", "")
                    ) or None,
                    "numero": getattr(publication, "numero", None),
                    "anio_publicacion": getattr(
                        publication,
                        "anio_publicacion",
                        None,
                    ),
                    "rol_autoria": (
                        "principal" if principal else "coautor"
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

    def validate_email(self, value):
        email = User.objects.normalize_email(value).strip().lower()

        duplicates = User.objects.filter(email__iexact=email)

        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este correo."
            )

        return email

    def validate_identificacion(self, value):
        value = _text(value)

        if not value:
            return None

        if not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._/-]{2,19}",
            value,
        ):
            raise serializers.ValidationError(
                "La identificación debe contener entre 3 y "
                "20 caracteres alfanuméricos."
            )

        duplicates = User.objects.filter(
            identificacion__iexact=value
        )

        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con esta identificación."
            )

        return value

    def validate(self, attrs):
        instance = self.instance
        role = _text(
            attrs.get(
                "rol",
                getattr(instance, "rol", "autor"),
            )
        ).lower()
        source = _text(
            attrs.get(
                "auth_source",
                getattr(instance, "auth_source", "local"),
            )
        ).lower()
        career = attrs.get(
            "carrera",
            getattr(instance, "carrera", None),
        )

        if source == "microsoft" and role != "autor":
            raise serializers.ValidationError(
                {
                    "rol": (
                        "Un usuario Microsoft debe tener "
                        "el rol de autor."
                    )
                }
            )

        if role == "autor_externo" and source != "local":
            raise serializers.ValidationError(
                {
                    "auth_source": (
                        "Un autor externo debe utilizar "
                        "autenticación local."
                    )
                }
            )

        if role == "autor_externo" and career is not None:
            raise serializers.ValidationError(
                {
                    "carrera": (
                        "Un autor externo no debe tener "
                        "carrera institucional."
                    )
                }
            )

        attrs["rol"] = role
        attrs["auth_source"] = source
        return attrs
