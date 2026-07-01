"""
Serializers para gestionar la participación de autores en publicaciones.
Normalizan autor, orden y rol de autoría para registro y lectura de relaciones.
"""

from rest_framework import serializers

from core.models import Autor, PublicacionAutor


class AutorParticipacionSerializer(serializers.Serializer):
    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(),
        source="autor",
        write_only=True,
        required=False,
        allow_null=True,
    )

    autor = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    orden = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )

    rol_autoria = serializers.ChoiceField(
        choices=PublicacionAutor.ROL_AUTORIA,
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        autor_obj = attrs.get("autor")
        if autor_obj is None:
            raise serializers.ValidationError(
                {"autor_id": ["Debe enviar un autor válido en 'autor_id'."]}
            )

        orden = attrs.get("orden")
        if orden is None:
            raise serializers.ValidationError(
                {"orden": ["Debe especificar el orden del autor."]}
            )

        try:
            orden = int(orden)
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                {"orden": ["Debe ser un número entero válido."]}
            )

        if orden < 1:
            raise serializers.ValidationError(
                {"orden": ["Debe ser mayor o igual a 1."]}
            )

        rol = attrs.get("rol_autoria")
        if rol not in dict(PublicacionAutor.ROL_AUTORIA):
            raise serializers.ValidationError(
                {"rol_autoria": ["Debe especificar un rol de autoría válido."]}
            )

        attrs["orden"] = orden
        attrs["rol_autoria"] = rol
        return attrs


class PublicacionAutorSerializer(serializers.ModelSerializer):
    autor_id = serializers.IntegerField(source="autor.id", read_only=True)
    autor_nombre = serializers.SerializerMethodField(read_only=True)
    nombre = serializers.SerializerMethodField(read_only=True)
    nombre_completo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PublicacionAutor
        fields = [
            "id",
            "autor_id",
            "autor_nombre",
            "nombre",
            "nombre_completo",
            "rol_autoria",
            "orden",
        ]
        read_only_fields = fields

    def _build_nombre(self, obj):
        autor = getattr(obj, "autor", None)
        if not autor:
            return "Autor"

        nombres = str(getattr(autor, "nombres", "") or "").strip()
        apellidos = str(getattr(autor, "apellidos", "") or "").strip()
        full = f"{nombres} {apellidos}".strip()

        return full or "Autor"

    def get_autor_nombre(self, obj):
        return self._build_nombre(obj)

    def get_nombre(self, obj):
        return self._build_nombre(obj)

    def get_nombre_completo(self, obj):
        return self._build_nombre(obj)