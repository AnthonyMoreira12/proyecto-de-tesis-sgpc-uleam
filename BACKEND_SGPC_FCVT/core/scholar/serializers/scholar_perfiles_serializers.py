"""
Serializer para listar autores visibles en perfiles
públicos o institucionales tipo Scholar.

Expone:
- nombre;
- afiliación;
- avatar;
- total de publicaciones.
"""

import re

from rest_framework import serializers

from core.models import Autor, Publicacion


class PerfilAutorListSerializer(
    serializers.ModelSerializer
):
    name = serializers.SerializerMethodField()
    org = serializers.SerializerMethodField()
    sede_id = serializers.SerializerMethodField()
    sede = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    publications = serializers.SerializerMethodField()

    class Meta:
        model = Autor

        fields = [
            "id",
            "name",
            "org",
            "sede_id",
            "sede",
            "avatar",
            "publications",
        ]

        read_only_fields = fields

    def get_name(
        self,
        obj,
    ):
        nombres = str(
            getattr(
                obj,
                "nombres",
                "",
            )
            or ""
        ).strip()

        apellidos = str(
            getattr(
                obj,
                "apellidos",
                "",
            )
            or ""
        ).strip()

        nombre = (
            f"{nombres} {apellidos}"
        ).strip()

        if nombre:
            return nombre

        correo = str(
            getattr(
                obj,
                "correo",
                "",
            )
            or ""
        ).strip()

        return (
            correo
            or "Autor"
        )

    def get_org(
        self,
        obj,
    ):
        user = getattr(
            obj,
            "usuario",
            None,
        )

        institucion = str(
            getattr(
                obj,
                "institucion",
                "",
            )
            or ""
        ).strip()

        # -----------------------------------------------------
        # Autor no vinculado a Usuario
        # -----------------------------------------------------

        if not user:
            if institucion:
                return institucion

            if getattr(
                obj,
                "es_externo",
                False,
            ):
                return "Autor externo"

            return "ULEAM"

        # -----------------------------------------------------
        # Usuario institucional
        # -----------------------------------------------------

        carrera = getattr(
            user,
            "carrera",
            None,
        )

        facultad = (
            getattr(
                carrera,
                "facultad",
                None,
            )
            if carrera
            else None
        )

        parts = []

        if (
            carrera
            and getattr(
                carrera,
                "nombre",
                None,
            )
        ):
            parts.append(
                carrera.nombre
            )

        if (
            facultad
            and getattr(
                facultad,
                "nombre",
                None,
            )
        ):
            parts.append(
                facultad.nombre
            )

        if parts:
            return " • ".join(
                parts
            )

        if institucion:
            return institucion

        if getattr(
            obj,
            "es_externo",
            False,
        ):
            return "Autor externo"

        return "ULEAM"

    def get_sede_id(
        self,
        obj,
    ):
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if not bool(
            getattr(
                user,
                "es_institucional",
                False,
            )
        ):
            return None

        sede = getattr(
            user,
            "sede",
            None,
        )

        return getattr(
            sede,
            "pk",
            None,
        )

    def get_sede(
        self,
        obj,
    ):
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if not bool(
            getattr(
                user,
                "es_institucional",
                False,
            )
        ):
            return None

        sede = getattr(
            user,
            "sede",
            None,
        )

        nombre = str(
            getattr(
                sede,
                "nombre",
                "",
            )
            or ""
        ).strip()

        return nombre or None

    def get_avatar(
        self,
        obj,
    ):
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if not user:
            return None

        avatar = getattr(
            user,
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
            AttributeError,
            ValueError,
        ):
            return None

        request = self.context.get(
            "request"
        )

        if request:
            try:
                return (
                    request.build_absolute_uri(
                        url
                    )
                )
            except Exception:
                pass

        return url

    def get_publications(
        self,
        obj,
    ):
        """
        Normalmente la vista proporciona:

            .annotate(publications=Count(...))

        Se mantiene un fallback seguro para evitar
        errores si el serializer se reutiliza.
        """

        annotated = getattr(
            obj,
            "publications",
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
            ):
                return 0

        try:
            return int(
                obj.publicaciones.filter(
                    estado=(
                        Publicacion.ESTADO_APROBADA
                    )
                ).count()
            )
        except Exception:
            return 0

# =============================================================
# IDENTIFICADORES ACADÉMICOS
# =============================================================

ORCID_PATTERN = re.compile(
    r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$"
)


def _normalize_optional_text(value):
    if value is None:
        return None

    value = str(value).strip()
    return value or None


def _normalize_orcid(value):
    value = _normalize_optional_text(value)

    if not value:
        return None

    value = value.upper()

    for prefix in (
        "https://orcid.org/",
        "http://orcid.org/",
        "orcid.org/",
    ):
        if value.lower().startswith(prefix):
            value = value[len(prefix):]
            break

    return value.strip().upper() or None


def _is_valid_orcid_checksum(orcid):
    """
    Valida el dígito de control ORCID mediante
    ISO 7064 MOD 11-2.
    """

    compact = orcid.replace("-", "")

    if len(compact) != 16:
        return False

    total = 0

    for char in compact[:15]:
        if not char.isdigit():
            return False

        total = (total + int(char)) * 2

    remainder = total % 11
    result = (12 - remainder) % 11

    expected = (
        "X"
        if result == 10
        else str(result)
    )

    return compact[-1] == expected


class PerfilAcademicoAutorSerializer(
    serializers.ModelSerializer
):
    """
    Serializer de los identificadores académicos del Autor.

    Todos los campos son opcionales y pertenecen a Autor.
    No intervienen en autenticación, permisos ni completitud
    del perfil de Usuario.
    """

    orcid = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=50,
    )

    registro_senescyt = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=100,
    )

    google_scholar = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=500,
    )

    scopus_id = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=100,
    )

    class Meta:
        model = Autor
        fields = [
            "orcid",
            "registro_senescyt",
            "google_scholar",
            "scopus_id",
        ]

    def validate_orcid(self, value):
        value = _normalize_orcid(value)

        if not value:
            return None

        if not ORCID_PATTERN.fullmatch(value):
            raise serializers.ValidationError(
                "El ORCID debe tener el formato "
                "0000-0000-0000-0000."
            )

        if not _is_valid_orcid_checksum(value):
            raise serializers.ValidationError(
                "El ORCID indicado no posee "
                "un dígito de control válido."
            )

        queryset = Autor.objects.filter(orcid=value)

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "Este ORCID ya está asociado "
                "a otro autor."
            )

        return value

    def validate_registro_senescyt(self, value):
        return _normalize_optional_text(value)

    def validate_google_scholar(self, value):
        return _normalize_optional_text(value)

    def validate_scopus_id(self, value):
        return _normalize_optional_text(value)

    def update(self, instance, validated_data):
        for field in (
            "orcid",
            "registro_senescyt",
            "google_scholar",
            "scopus_id",
        ):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance