"""
Serializers para archivos adjuntos de publicaciones.

Gestiona:
- lectura;
- creación individual;
- subida múltiple;
- validación de PDF;
- límite máximo de adjuntos;
- asignación segura del orden.
"""

import json

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Publicacion
from core.models.publicaciones.archivos import (
    MAX_ADJUNTOS_POR_PUBLICACION,
    PublicacionArchivo,
)
from core.publicaciones.utils.publicaciones_archivos_utils import (
    default_nombre_from_file,
    validar_firma_pdf,
)


def _django_validation_to_drf(
    exc,
):
    if hasattr(
        exc,
        "message_dict",
    ):
        return ValidationError(
            exc.message_dict
        )

    if hasattr(
        exc,
        "messages",
    ):
        return ValidationError(
            {
                "detail": list(
                    exc.messages
                )
            }
        )

    return ValidationError(
        {
            "detail": [
                str(exc)
            ]
        }
    )


def _next_free_order(
    used_orders,
):
    order = 1

    while order in used_orders:
        order += 1

    return order


class PublicacionArchivoSerializer(
    serializers.ModelSerializer
):
    publicacion_id = serializers.IntegerField(
        source="publicacion.id",
        read_only=True,
    )

    archivo_url = (
        serializers.SerializerMethodField(
            read_only=True
        )
    )

    class Meta:
        model = PublicacionArchivo

        fields = [
            "id",
            "publicacion_id",
            "nombre",
            "archivo",
            "archivo_url",
            "nombre_original",
            "tamano_bytes",
            "sha256",
            "orden",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "publicacion_id",
            "archivo_url",
            "nombre_original",
            "tamano_bytes",
            "sha256",
            "created_at",
        ]

    def get_archivo_url(
        self,
        obj,
    ):
        try:
            archivo = getattr(
                obj,
                "archivo",
                None,
            )

            if (
                not archivo
                or not getattr(
                    archivo,
                    "name",
                    None,
                )
            ):
                return None

            file_url = archivo.url

        except (
            ValueError,
            AttributeError,
        ):
            return None

        request = self.context.get(
            "request"
        )

        if request is None:
            return file_url

        try:
            return (
                request.build_absolute_uri(
                    file_url
                )
            )
        except Exception:
            return file_url


class PublicacionArchivoCreateSerializer(
    serializers.ModelSerializer
):
    publicacion = (
        serializers.PrimaryKeyRelatedField(
            queryset=Publicacion.objects.all(),
        )
    )

    nombre = serializers.CharField(
        max_length=150,
    )

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
            "nombre_original",
            "tamano_bytes",
            "sha256",
            "orden",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "nombre_original",
            "tamano_bytes",
            "sha256",
            "created_at",
        ]

    def validate_nombre(
        self,
        value,
    ):
        value = str(
            value or ""
        ).strip()

        if not value:
            raise ValidationError(
                "Debe ingresar un nombre "
                "para el archivo."
            )

        return value

    def validate_archivo(
        self,
        value,
    ):
        return validar_firma_pdf(
            value
        )

    @transaction.atomic
    def create(
        self,
        validated_data,
    ):
        publicacion = (
            validated_data[
                "publicacion"
            ]
        )

        publicacion = (
            Publicacion.objects
            .select_for_update()
            .get(
                pk=publicacion.pk
            )
        )

        existing = list(
            PublicacionArchivo.objects
            .filter(
                publicacion=publicacion
            )
            .values_list(
                "orden",
                flat=True,
            )
        )

        if (
            len(existing)
            >= MAX_ADJUNTOS_POR_PUBLICACION
        ):
            raise ValidationError(
                {
                    "archivo": [
                        "Solo se permiten hasta "
                        f"{MAX_ADJUNTOS_POR_PUBLICACION} "
                        "archivos adjuntos por publicación."
                    ]
                }
            )

        requested_order = (
            validated_data.get(
                "orden"
            )
        )

        used_orders = set(
            existing
        )

        if requested_order is None:
            requested_order = (
                _next_free_order(
                    used_orders
                )
            )

        if requested_order in used_orders:
            raise ValidationError(
                {
                    "orden": [
                        "Ya existe un archivo "
                        "con este orden."
                    ]
                }
            )

        try:
            return (
                PublicacionArchivo.objects
                .create(
                    publicacion=publicacion,
                    nombre=validated_data[
                        "nombre"
                    ],
                    archivo=validated_data[
                        "archivo"
                    ],
                    orden=requested_order,
                )
            )

        except DjangoValidationError as exc:
            raise _django_validation_to_drf(
                exc
            )


class PublicacionArchivosBulkUploadSerializer(
    serializers.Serializer
):
    publicacion_id = serializers.IntegerField(
        min_value=1,
    )

    meta = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=False,
    )

    def to_internal_value(
        self,
        data,
    ):
        source = {}

        if hasattr(
            data,
            "getlist",
        ):
            files_value = (
                data.getlist(
                    "files"
                )
                or data.getlist(
                    "archivos"
                )
            )

            meta_value = data.get(
                "meta",
                None,
            )

            if meta_value in (
                None,
                "",
            ):
                meta_value = data.get(
                    "archivos_meta",
                    None,
                )

            publicacion_id = data.get(
                "publicacion_id",
                None,
            )

        else:
            raw = dict(
                data
            )

            files_value = (
                raw.get(
                    "files"
                )
                or raw.get(
                    "archivos"
                )
                or []
            )

            meta_value = raw.get(
                "meta",
                None,
            )

            if meta_value in (
                None,
                "",
            ):
                meta_value = raw.get(
                    "archivos_meta",
                    None,
                )

            publicacion_id = raw.get(
                "publicacion_id",
                None,
            )

        if not isinstance(
            files_value,
            list,
        ):
            files_value = (
                [files_value]
                if files_value
                else []
            )

        source[
            "publicacion_id"
        ] = publicacion_id

        source["files"] = [
            file
            for file in files_value
            if file
        ]

        source["meta"] = (
            meta_value
            if meta_value is not None
            else ""
        )

        return super().to_internal_value(
            source
        )

    def validate(
        self,
        attrs,
    ):
        publicacion_id = attrs.get(
            "publicacion_id"
        )

        try:
            publicacion = (
                Publicacion.objects
                .get(
                    pk=publicacion_id
                )
            )
        except Publicacion.DoesNotExist:
            raise ValidationError(
                {
                    "publicacion_id": [
                        "La publicación no existe."
                    ]
                }
            )

        files = attrs.get(
            "files"
        ) or []

        if not files:
            raise ValidationError(
                {
                    "files": [
                        "Debe adjuntar al menos "
                        "un archivo PDF."
                    ]
                }
            )

        if (
            len(files)
            > MAX_ADJUNTOS_POR_PUBLICACION
        ):
            raise ValidationError(
                {
                    "files": [
                        "Solo se permiten hasta "
                        f"{MAX_ADJUNTOS_POR_PUBLICACION} "
                        "archivos adjuntos por publicación."
                    ]
                }
            )

        for index, uploaded_file in enumerate(
            files,
            start=1,
        ):
            try:
                validar_firma_pdf(
                    uploaded_file
                )
            except ValidationError as exc:
                detail = exc.detail

                if isinstance(
                    detail,
                    list,
                ):
                    message = str(
                        detail[0]
                    )
                else:
                    message = str(
                        detail
                    )

                raise ValidationError(
                    {
                        "files": [
                            f"Archivo #{index}: "
                            f"{message}"
                        ]
                    }
                )

        raw_meta = str(
            attrs.get(
                "meta"
            )
            or ""
        ).strip()

        try:
            meta_list = (
                json.loads(
                    raw_meta
                )
                if raw_meta
                else []
            )
        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            raise ValidationError(
                {
                    "meta": [
                        "Formato inválido. "
                        "Debe ser JSON válido."
                    ]
                }
            )

        if (
            meta_list
            and not isinstance(
                meta_list,
                list,
            )
        ):
            raise ValidationError(
                {
                    "meta": [
                        "Debe enviar una lista JSON "
                        "con los metadatos de los archivos."
                    ]
                }
            )

        if (
            meta_list
            and len(meta_list)
            != len(files)
        ):
            raise ValidationError(
                {
                    "meta": [
                        "La cantidad de metadatos "
                        "debe coincidir con la cantidad "
                        "de archivos."
                    ]
                }
            )

        normalized = []

        for index, uploaded_file in enumerate(
            files,
            start=1,
        ):
            item = (
                meta_list[index - 1]
                if meta_list
                else {}
            )

            if not isinstance(
                item,
                dict,
            ):
                raise ValidationError(
                    {
                        "meta": [
                            f"El elemento #{index} "
                            "debe ser un objeto JSON."
                        ]
                    }
                )

            nombre = str(
                item.get(
                    "nombre"
                )
                or ""
            ).strip()

            if not nombre:
                nombre = (
                    default_nombre_from_file(
                        uploaded_file
                    )
                )

            if len(nombre) > 150:
                raise ValidationError(
                    {
                        "meta": [
                            f"El nombre del archivo "
                            f"#{index} supera "
                            "150 caracteres."
                        ]
                    }
                )

            orden = item.get(
                "orden",
                None,
            )

            if orden not in (
                None,
                "",
            ):
                try:
                    orden = int(
                        orden
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    raise ValidationError(
                        {
                            "meta": [
                                f"El orden del archivo "
                                f"#{index} debe ser numérico."
                            ]
                        }
                    )

                if orden < 1:
                    raise ValidationError(
                        {
                            "meta": [
                                f"El orden del archivo "
                                f"#{index} debe ser mayor "
                                "o igual a 1."
                            ]
                        }
                    )
            else:
                orden = None

            normalized.append(
                {
                    "nombre": nombre,
                    "orden": orden,
                }
            )

        explicit_orders = [
            item["orden"]
            for item in normalized
            if item["orden"] is not None
        ]

        if (
            len(explicit_orders)
            != len(
                set(explicit_orders)
            )
        ):
            raise ValidationError(
                {
                    "meta": [
                        "No se permite repetir "
                        "el orden de los adjuntos."
                    ]
                }
            )

        attrs["publicacion"] = (
            publicacion
        )

        attrs["meta_list"] = (
            normalized
        )

        return attrs

    @transaction.atomic
    def create(
        self,
        validated_data,
    ):
        publicacion = (
            validated_data[
                "publicacion"
            ]
        )

        files = validated_data[
            "files"
        ]

        meta_list = validated_data[
            "meta_list"
        ]

        publicacion = (
            Publicacion.objects
            .select_for_update()
            .get(
                pk=publicacion.pk
            )
        )

        existing = list(
            PublicacionArchivo.objects
            .filter(
                publicacion=publicacion
            )
            .values_list(
                "orden",
                flat=True,
            )
        )

        if (
            len(existing)
            + len(files)
            > MAX_ADJUNTOS_POR_PUBLICACION
        ):
            disponibles = max(
                MAX_ADJUNTOS_POR_PUBLICACION
                - len(existing),
                0,
            )

            raise ValidationError(
                {
                    "files": [
                        "La publicación solo admite "
                        f"{MAX_ADJUNTOS_POR_PUBLICACION} "
                        "adjuntos. "
                        f"Puede agregar {disponibles} "
                        "archivo(s) adicional(es)."
                    ]
                }
            )

        used_orders = set(
            existing
        )

        assigned = []

        for item in meta_list:
            order = item[
                "orden"
            ]

            if order is not None:
                if order in used_orders:
                    raise ValidationError(
                        {
                            "meta": [
                                f"Ya existe un archivo "
                                f"con orden {order}."
                            ]
                        }
                    )
            else:
                order = _next_free_order(
                    used_orders
                )

            used_orders.add(
                order
            )

            assigned.append(
                {
                    "nombre": item[
                        "nombre"
                    ],
                    "orden": order,
                }
            )

        created = []

        try:
            for metadata, uploaded_file in zip(
                assigned,
                files,
            ):
                obj = (
                    PublicacionArchivo.objects
                    .create(
                        publicacion=publicacion,
                        nombre=metadata[
                            "nombre"
                        ],
                        orden=metadata[
                            "orden"
                        ],
                        archivo=uploaded_file,
                    )
                )

                created.append(
                    obj
                )

        except DjangoValidationError as exc:
            raise _django_validation_to_drf(
                exc
            )

        return created