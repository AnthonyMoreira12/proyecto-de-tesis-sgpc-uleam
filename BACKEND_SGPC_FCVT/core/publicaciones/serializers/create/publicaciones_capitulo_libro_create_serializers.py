import json
import os

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import (
    AreaConocimiento,
    CapituloLibro,
    Carrera,
    Facultad,
    Proyecto,
    Subarea,
)
from core.publicaciones.serializers.base.publicaciones_autores_serializers import (
    AutorParticipacionSerializer,
)
from core.publicaciones.serializers.base.publicaciones_campos_base_serializers import (
    PublicacionCamposBaseMixin,
)
from core.publicaciones.services.publicaciones_autores_services import (
    registrar_autores_publicacion,
)
from core.publicaciones.services.publicaciones_factory_services import (
    crear_publicacion_base,
    obtener_o_crear_tipo_publicacion,
)
from core.publicaciones.utils.publicaciones_creation_context_utils import (
    resolve_publicacion_creation_context,
)


MAX_PRIMARY_PDF_BYTES = 5 * 1024 * 1024

ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


def _read_header(
    uploaded_file,
    max_bytes=1024,
):
    file_obj = getattr(
        uploaded_file,
        "file",
        uploaded_file,
    )

    if (
        file_obj is None
        or not hasattr(
            file_obj,
            "read",
        )
    ):
        return b""

    position = 0

    try:
        if hasattr(
            file_obj,
            "tell",
        ):
            position = (
                file_obj.tell()
            )
    except (
        OSError,
        ValueError,
    ):
        position = 0

    try:
        if hasattr(
            file_obj,
            "seek",
        ):
            file_obj.seek(0)

        return bytes(
            file_obj.read(
                max_bytes
            )
            or b""
        )

    except (
        OSError,
        ValueError,
        TypeError,
    ):
        return b""

    finally:
        try:
            if hasattr(
                file_obj,
                "seek",
            ):
                file_obj.seek(
                    position
                )
        except (
            OSError,
            ValueError,
        ):
            pass


def validate_primary_pdf_file(value):
    if not value:
        return value

    file_name = str(
        getattr(
            value,
            "name",
            "",
        )
        or ""
    ).strip()

    extension = os.path.splitext(
        file_name.lower()
    )[1]

    if extension != ".pdf":
        raise ValidationError(
            "Solo se permiten archivos PDF."
        )

    content_type = (
        getattr(
            value,
            "content_type",
            None,
        )
        or getattr(
            getattr(
                value,
                "file",
                None,
            ),
            "content_type",
            None,
        )
    )

    if (
        content_type
        and str(
            content_type
        ).lower()
        not in ALLOWED_PDF_CONTENT_TYPES
    ):
        raise ValidationError(
            "El tipo de contenido no corresponde a un PDF."
        )

    try:
        file_size = int(
            getattr(
                value,
                "size",
                0,
            )
            or 0
        )
    except (
        TypeError,
        ValueError,
    ):
        file_size = 0

    if file_size <= 0:
        raise ValidationError(
            "El archivo PDF está vacío."
        )

    if (
        file_size
        > MAX_PRIMARY_PDF_BYTES
    ):
        raise ValidationError(
            "El PDF principal supera el tamaño máximo de 5 MB."
        )

    header = _read_header(
        value
    )

    if (
        header
        and not header.startswith(
            b"%PDF-"
        )
    ):
        raise ValidationError(
            "El archivo no contiene una firma PDF válida."
        )

    return value


def _plain_data(data):
    if hasattr(data, "lists"):
        result = {}

        for key, values in data.lists():
            if not values:
                result[key] = ""
            elif len(values) == 1:
                result[key] = values[0]
            else:
                result[key] = values

        return result

    return dict(data)


def _parse_autores(value):
    if (
        isinstance(value, list)
        and len(value) == 1
    ):
        value = value[0]

    if value in (
        None,
        "",
        "[]",
        "null",
        "None",
        [],
        {},
    ):
        return []

    if isinstance(value, str):
        try:
            value = json.loads(
                value.strip()
            )
        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            raise ValidationError(
                {
                    "autores": [
                        "Formato inválido. "
                        "Debe enviar una lista JSON válida."
                    ]
                }
            )

    if not isinstance(
        value,
        list,
    ):
        raise ValidationError(
            {
                "autores": [
                    "Los autores deben enviarse como una lista."
                ]
            }
        )

    normalized = []

    for index, item in enumerate(
        value,
        start=1,
    ):
        if not isinstance(
            item,
            dict,
        ):
            raise ValidationError(
                {
                    "autores": [
                        f"El autor #{index} debe ser un objeto."
                    ]
                }
            )

        item = dict(item)

        try:
            orden = int(
                item.get("orden")
            )
        except (
            TypeError,
            ValueError,
        ):
            raise ValidationError(
                {
                    "autores": [
                        f"El autor #{index} debe tener un orden válido."
                    ]
                }
            )

        if orden < 1:
            raise ValidationError(
                {
                    "autores": [
                        "El orden debe ser mayor o igual a 1."
                    ]
                }
            )

        item["orden"] = orden

        item["rol_autoria"] = (
            "principal"
            if orden == 1
            else "coautor"
        )

        normalized.append(
            item
        )

    return normalized


def _normalize_autores(autores):
    if not autores:
        raise ValidationError(
            {
                "autores": [
                    "Debe registrar al menos un autor."
                ]
            }
        )

    autor_ids = [
        item["autor"].id
        for item in autores
    ]

    ordenes = [
        int(item["orden"])
        for item in autores
    ]

    if (
        len(autor_ids)
        != len(set(autor_ids))
    ):
        raise ValidationError(
            {
                "autores": [
                    "No se permite repetir el mismo autor."
                ]
            }
        )

    if (
        len(ordenes)
        != len(set(ordenes))
    ):
        raise ValidationError(
            {
                "autores": [
                    "No se permite repetir el orden."
                ]
            }
        )

    if 1 not in ordenes:
        raise ValidationError(
            {
                "autores": [
                    "Debe existir un autor principal con orden 1."
                ]
            }
        )

    autores = sorted(
        autores,
        key=lambda item: int(
            item["orden"]
        ),
    )

    for index, item in enumerate(
        autores,
        start=1,
    ):
        item["orden"] = index

        item["rol_autoria"] = (
            "principal"
            if index == 1
            else "coautor"
        )

    return autores


class CapituloLibroRegistroSerializer(
    PublicacionCamposBaseMixin,
    serializers.ModelSerializer,
):
    facultad = serializers.PrimaryKeyRelatedField(
        queryset=Facultad.objects.all(),
        write_only=True,
    )

    carrera = serializers.PrimaryKeyRelatedField(
        queryset=Carrera.objects.select_related(
            "facultad"
        ).all(),
        write_only=True,
    )

    proyecto = serializers.PrimaryKeyRelatedField(
        queryset=Proyecto.objects.select_related(
            "carrera"
        ).all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    area = serializers.PrimaryKeyRelatedField(
        queryset=AreaConocimiento.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    subarea = serializers.PrimaryKeyRelatedField(
        queryset=Subarea.objects.select_related(
            "area"
        ).all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    fecha_publicacion = serializers.DateField(
        required=False,
        allow_null=True,
        write_only=True,
        input_formats=[
            "%Y-%m-%d",
            "%d/%m/%Y",
        ],
    )

    archivo_pdf = serializers.FileField(
        required=False,
        allow_null=True,
        write_only=True,
    )

    autores = AutorParticipacionSerializer(
        many=True,
        write_only=True,
        required=True,
    )

    revisor_par_arbitraje = serializers.ChoiceField(
        choices=CapituloLibro.SI_NO,
        required=True,
    )

    class Meta:
        model = CapituloLibro

        fields = [
            "id",
            "facultad",
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "origen_tipo",
            "origen_grado",
            "fecha_publicacion",
            "archivo_pdf",
            "nombre_capitulo",
            "nombre_libro",
            "codigo_isbn",
            "editor_compilador",
            "revisor_par_arbitraje",
            "link_capitulo",
            "autores",
        ]

        read_only_fields = [
            "id",
        ]

    def to_internal_value(
        self,
        data,
    ):
        data = _plain_data(data)

        data["autores"] = (
            _parse_autores(
                data.get("autores")
            )
        )

        return super().to_internal_value(
            data
        )

    def validate_archivo_pdf(
        self,
        value,
    ):
        return validate_primary_pdf_file(
            value
        )

    def validate(
        self,
        attrs,
    ):
        attrs = self._aplicar_reglas_origen(
            attrs
        )

        facultad = attrs.get(
            "facultad"
        )

        carrera = attrs.get(
            "carrera"
        )

        proyecto = attrs.get(
            "proyecto"
        )

        if (
            facultad
            and carrera
            and carrera.facultad_id
            != facultad.id
        ):
            raise ValidationError(
                {
                    "carrera": [
                        "La carrera seleccionada no pertenece "
                        "a la facultad indicada."
                    ]
                }
            )

        if (
            proyecto
            and carrera
            and proyecto.carrera_id
            != carrera.id
        ):
            raise ValidationError(
                {
                    "proyecto": [
                        "El proyecto seleccionado no pertenece "
                        "a la carrera indicada."
                    ]
                }
            )

        area = attrs.get("area")
        subarea = attrs.get(
            "subarea"
        )

        if subarea and not area:
            attrs["area"] = (
                subarea.area
            )

            area = subarea.area

        if (
            area
            and subarea
            and subarea.area_id
            != area.id
        ):
            raise ValidationError(
                {
                    "subarea": [
                        "La subárea seleccionada no pertenece "
                        "al área indicada."
                    ]
                }
            )

        for field in (
            "nombre_capitulo",
            "nombre_libro",
            "codigo_isbn",
            "editor_compilador",
            "link_capitulo",
        ):
            value = str(
                attrs.get(field)
                or ""
            ).strip()

            if not value:
                raise ValidationError(
                    {
                        field: [
                            "Este campo es obligatorio."
                        ]
                    }
                )

            attrs[field] = value

        attrs["autores"] = (
            _normalize_autores(
                attrs.get("autores")
                or []
            )
        )

        return attrs

    @transaction.atomic
    def create(
        self,
        validated_data,
    ):
        autores_data = (
            validated_data.pop(
                "autores",
                [],
            )
        )

        (
            usuario_creador,
            admin_registrador,
            registrado_por_admin,
        ) = resolve_publicacion_creation_context(
            self
        )

        facultad = validated_data.pop(
            "facultad"
        )

        carrera = validated_data.pop(
            "carrera"
        )

        proyecto = validated_data.pop(
            "proyecto",
            None,
        )

        area = validated_data.pop(
            "area",
            None,
        )

        subarea = validated_data.pop(
            "subarea",
            None,
        )

        origen_tipo = validated_data.pop(
            "origen_tipo",
            "ninguno",
        )

        origen_grado = validated_data.pop(
            "origen_grado",
            None,
        )

        fecha_publicacion = (
            validated_data.pop(
                "fecha_publicacion",
                None,
            )
        )

        archivo_pdf = (
            validated_data.pop(
                "archivo_pdf",
                None,
            )
        )

        tipo = (
            obtener_o_crear_tipo_publicacion(
                codigo="capitulo_libro",
                nombre="Capítulo de Libro",
                categoria="capitulo",
                orden=4,
            )
        )

        publicacion = crear_publicacion_base(
            proyecto=proyecto,
            tipo=tipo,
            usuario=usuario_creador,
            facultad=facultad,
            carrera=carrera,
            area=area,
            subarea=subarea,
            pais=None,
            ciudad=None,
            origen_tipo=origen_tipo,
            origen_grado=origen_grado,
            fecha_publicacion=(
                fecha_publicacion
            ),
            archivo_pdf=archivo_pdf,
            registrado_por_admin=(
                registrado_por_admin
            ),
            admin_registrador=(
                admin_registrador
            ),
        )

        capitulo = (
            CapituloLibro.objects.create(
                publicacion=publicacion,
                **validated_data,
            )
        )

        registrar_autores_publicacion(
            publicacion=publicacion,
            autores_data=autores_data,
        )

        return capitulo