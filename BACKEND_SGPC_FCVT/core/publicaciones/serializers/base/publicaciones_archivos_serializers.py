"""
Serializers para gestión de archivos adjuntos de publicaciones.
Permiten listar, crear y cargar múltiples archivos con validación de metadatos.
Aceptan aliases de payload para compatibilidad:
- meta / archivos_meta
- files / archivos
"""

import json
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Publicacion
from core.models.publicaciones.archivos import PublicacionArchivo
# Importamos las utilidades que acabas de crear
from core.publicaciones.utils.publicaciones_archivos_utils import (
    validar_firma_pdf,
    default_nombre_from_file
)


class PublicacionArchivoSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField(read_only=True)
    publicacion_id = serializers.IntegerField(source="publicacion.id", read_only=True)

    class Meta:
        model = PublicacionArchivo
        fields = [
            "id",
            "publicacion_id",
            "nombre",
            "archivo",
            "archivo_url",
            "orden",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "publicacion_id",
            "archivo_url",
            "created_at",
        ]

    def get_archivo_url(self, obj):
        try:
            if not obj.archivo:
                return None
            file_url = obj.archivo.url
        except Exception:
            return None

        request = self.context.get("request")
        if request:
            try:
                return request.build_absolute_uri(file_url)
            except Exception:
                return file_url

        return file_url


class PublicacionArchivoCreateSerializer(serializers.ModelSerializer):
    publicacion = serializers.PrimaryKeyRelatedField(
        queryset=Publicacion.objects.all()
    )
    nombre = serializers.CharField(max_length=150)
    archivo = serializers.FileField()
    orden = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    class Meta:
        model = PublicacionArchivo
        fields = [
            "id",
            "publicacion",
            "nombre",
            "archivo",
            "orden",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_nombre(self, value):
        value = (value or "").strip()
        if not value:
            raise ValidationError("Debe ingresar un nombre para el archivo.")
        return value

    def validate_archivo(self, value):
        # Usamos nuestra nueva utilidad para bloquear falsos PDFs
        return validar_firma_pdf(value)

    def validate(self, attrs):
        if attrs.get("orden") in (None, ""):
            publicacion = attrs.get("publicacion")
            last = (
                PublicacionArchivo.objects
                .filter(publicacion=publicacion)
                .order_by("-orden", "-id")
                .first()
            )
            attrs["orden"] = 1 if not last else int(last.orden or 0) + 1

        return attrs


class PublicacionArchivosBulkUploadSerializer(serializers.Serializer):
    publicacion_id = serializers.IntegerField()
    meta = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        required=False,
    )

    def to_internal_value(self, data):
        source = data.copy() if hasattr(data, "copy") else dict(data)

        meta_value = None
        files_value = []

        if hasattr(data, "getlist"):
            files_value = data.getlist("files") or data.getlist("archivos")
            meta_value = data.get("meta", None)
            if meta_value in (None, ""):
                meta_value = data.get("archivos_meta", None)
        else:
            files_value = source.get("files") or source.get("archivos") or []
            meta_value = source.get("meta", None)
            if meta_value in (None, ""):
                meta_value = source.get("archivos_meta", None)

        if not isinstance(files_value, list):
            files_value = [files_value] if files_value else []

        source["files"] = [f for f in files_value if f]
        source["meta"] = meta_value if meta_value is not None else ""

        return super().to_internal_value(source)

    def validate(self, attrs):
        pub_id = attrs.get("publicacion_id")

        try:
            publicacion = Publicacion.objects.get(id=pub_id)
        except Publicacion.DoesNotExist:
            raise ValidationError({"publicacion_id": ["Publicación no existe."]})

        raw_meta = (attrs.get("meta") or "").strip()
        files = attrs.get("files") or []

        # Usamos nuestra nueva utilidad para bloquear falsos PDFs en la subida masiva
        for index, uploaded_file in enumerate(files, start=1):
            try:
                validar_firma_pdf(uploaded_file)
            except ValidationError as e:
                raise ValidationError({"files": [f"Archivo #{index}: {e.detail[0]}"]})

        try:
            meta_list = json.loads(raw_meta) if raw_meta else []
        except Exception:
            raise ValidationError({"meta": ["Formato inválido. Debe ser JSON válido."]})

        if meta_list and not isinstance(meta_list, list):
            raise ValidationError(
                {"meta": ["Debe enviar una lista JSON con {nombre, orden?}."]}
            )

        if meta_list and len(meta_list) != len(files):
            raise ValidationError(
                {
                    "detail": (
                        "La cantidad de 'meta' debe coincidir con la cantidad de archivos."
                    )
                }
            )

        normalized = []

        if not meta_list:
            for index, uploaded_file in enumerate(files, start=1):
                normalized.append(
                    {
                        "nombre": default_nombre_from_file(uploaded_file),
                        "orden": index,
                    }
                )
        else:
            for index, item in enumerate(meta_list, start=1):
                if not isinstance(item, dict):
                    raise ValidationError(
                        {"meta": ["Cada item de meta debe ser un objeto JSON."]}
                    )

                nombre = (item.get("nombre") or "").strip()
                if not nombre:
                    nombre = default_nombre_from_file(files[index - 1])

                orden = item.get("orden")
                if orden in (None, ""):
                    orden = index

                try:
                    orden = int(orden)
                except Exception:
                    raise ValidationError(
                        {"meta": [f"El 'orden' del archivo #{index} debe ser numérico."]}
                    )

                if orden < 1:
                    raise ValidationError(
                        {"meta": [f"El 'orden' del archivo #{index} debe ser >= 1."]}
                    )

                normalized.append(
                    {
                        "nombre": nombre,
                        "orden": orden,
                    }
                )

        ordenes = [item["orden"] for item in normalized]
        if len(ordenes) != len(set(ordenes)):
            raise ValidationError(
                {"meta": ["No se permite repetir el campo 'orden' en adjuntos."]}
            )

        attrs["publicacion"] = publicacion
        attrs["meta_list"] = sorted(normalized, key=lambda item: item["orden"])
        return attrs

    def create(self, validated_data):
        publicacion = validated_data["publicacion"]
        meta_list = validated_data["meta_list"]
        files = validated_data["files"]

        created = []
        for item, uploaded_file in zip(meta_list, files):
            created.append(
                PublicacionArchivo.objects.create(
                    publicacion=publicacion,
                    nombre=item["nombre"],
                    orden=item["orden"],
                    archivo=uploaded_file,
                )
            )

        return created