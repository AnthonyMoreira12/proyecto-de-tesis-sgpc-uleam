"""Serializers administrativos para catálogos académicos."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.models import Carrera, CarreraSede, Facultad, Sede
from core.utils.files import normalize_optional_text, normalize_text


def _django_payload(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"detail": list(exc.messages)}
    return {"detail": str(exc)}


class _ModelValidationMixin:
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_payload(exc)
            ) from exc

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_payload(exc)
            ) from exc


class AdminFacultadSerializer(
    _ModelValidationMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = Facultad
        fields = ["id", "nombre", "siglas", "descripcion"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "nombre": {
                "required": True,
                "allow_blank": False,
                "trim_whitespace": True,
            },
            "siglas": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
                "trim_whitespace": True,
            },
            "descripcion": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
                "trim_whitespace": True,
            },
        }

    def validate_nombre(self, value):
        value = normalize_text(value)

        if not value:
            raise serializers.ValidationError(
                "El nombre de la facultad es obligatorio."
            )

        duplicates = Facultad.objects.filter(nombre__iexact=value)
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                "Ya existe una facultad con este nombre."
            )

        return value

    def validate_siglas(self, value):
        value = normalize_optional_text(value)

        if value is None:
            return None

        value = value.upper()
        duplicates = Facultad.objects.filter(siglas__iexact=value)

        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                "Ya existe una facultad con estas siglas."
            )

        return value

    def validate_descripcion(self, value):
        return normalize_optional_text(value)


class AdminCarreraSerializer(
    _ModelValidationMixin,
    serializers.ModelSerializer,
):
    facultad_nombre = serializers.CharField(
        source="facultad.nombre",
        read_only=True,
    )
    facultad_siglas = serializers.CharField(
        source="facultad.siglas",
        read_only=True,
        allow_null=True,
        default=None,
    )

    class Meta:
        model = Carrera
        fields = [
            "id",
            "nombre",
            "facultad",
            "facultad_nombre",
            "facultad_siglas",
        ]
        read_only_fields = [
            "id",
            "facultad_nombre",
            "facultad_siglas",
        ]

    def validate_nombre(self, value):
        value = normalize_text(value)
        if not value:
            raise serializers.ValidationError(
                "El nombre de la carrera es obligatorio."
            )
        return value

    def validate(self, attrs):
        instance = self.instance
        name = normalize_text(
            attrs.get(
                "nombre",
                getattr(instance, "nombre", ""),
            )
        )
        faculty = attrs.get(
            "facultad",
            getattr(instance, "facultad", None),
        )

        if faculty is None:
            raise serializers.ValidationError(
                {"facultad": "La facultad es obligatoria."}
            )

        duplicates = Carrera.objects.filter(
            nombre__iexact=name,
            facultad_id=faculty.pk,
        )

        if instance is not None:
            duplicates = duplicates.exclude(pk=instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                {
                    "nombre": (
                        "Ya existe una carrera con este nombre "
                        "dentro de la facultad seleccionada."
                    )
                }
            )

        attrs["nombre"] = name
        return attrs


class AdminSedeSerializer(
    _ModelValidationMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = Sede
        fields = [
            "id", "nombre", "codigo", "ciudad", "descripcion", "activa",
        ]
        read_only_fields = ["id"]

    def validate_nombre(self, value):
        value = normalize_text(value)
        if not value:
            raise serializers.ValidationError("El nombre de la sede es obligatorio.")
        qs = Sede.objects.filter(nombre__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una sede con este nombre.")
        return value

    def validate_codigo(self, value):
        value = normalize_text(value).lower()
        if not value:
            raise serializers.ValidationError("El código de la sede es obligatorio.")
        qs = Sede.objects.filter(codigo__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una sede con este código.")
        return value


class AdminCarreraSedeSerializer(
    _ModelValidationMixin,
    serializers.ModelSerializer,
):
    sede_nombre = serializers.CharField(source="sede.nombre", read_only=True)
    carrera_nombre = serializers.CharField(source="carrera.nombre", read_only=True)
    facultad_nombre = serializers.CharField(source="carrera.facultad.nombre", read_only=True)

    class Meta:
        model = CarreraSede
        fields = [
            "id", "sede", "sede_nombre", "carrera", "carrera_nombre",
            "facultad_nombre", "activa",
        ]
        read_only_fields = ["id", "sede_nombre", "carrera_nombre", "facultad_nombre"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance
        sede = attrs.get("sede", getattr(instance, "sede", None))
        carrera = attrs.get("carrera", getattr(instance, "carrera", None))
        if sede is None:
            raise serializers.ValidationError({"sede": "La sede es obligatoria."})
        if carrera is None:
            raise serializers.ValidationError({"carrera": "La carrera es obligatoria."})
        qs = CarreraSede.objects.filter(sede=sede, carrera=carrera)
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                "carrera": "Esta carrera ya está relacionada con la sede seleccionada."
            })
        return attrs
