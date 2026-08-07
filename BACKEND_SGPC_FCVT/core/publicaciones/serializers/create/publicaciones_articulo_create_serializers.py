import json
import os

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import (
    Articulo,
    AreaConocimiento,
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

ALLOWED_PDF_EXTENSIONS = {
    ".pdf",
}

ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


def _to_str(value):
    return str(value or "").strip()


def _to_lower(value):
    value = _to_str(value)
    return value.lower() if value else ""


def _none_if_blank(value):
    value = _to_str(value)
    return value or None


def _read_file_header(
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
        or not hasattr(file_obj, "read")
    ):
        return b""

    original_position = 0

    try:
        if hasattr(file_obj, "tell"):
            original_position = file_obj.tell()
    except (OSError, ValueError):
        original_position = 0

    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        content = file_obj.read(max_bytes)

        if isinstance(content, str):
            content = content.encode(
                "utf-8",
                errors="ignore",
            )

        return bytes(content or b"")

    except (
        OSError,
        ValueError,
        TypeError,
    ):
        return b""

    finally:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(original_position)
        except (
            OSError,
            ValueError,
        ):
            pass


def validate_primary_pdf_file(value):
    if not value:
        return value

    file_name = _to_str(
        getattr(value, "name", "")
    )

    extension = os.path.splitext(
        file_name.lower()
    )[1]

    if extension not in ALLOWED_PDF_EXTENSIONS:
        raise ValidationError(
            "Solo se permiten archivos PDF."
        )

    content_type = (
        getattr(value, "content_type", None)
        or getattr(
            getattr(value, "file", None),
            "content_type",
            None,
        )
    )

    if (
        content_type
        and str(content_type).lower()
        not in ALLOWED_PDF_CONTENT_TYPES
    ):
        raise ValidationError(
            "El tipo de contenido no corresponde a un PDF."
        )

    try:
        file_size = int(
            getattr(value, "size", 0)
            or 0
        )
    except (TypeError, ValueError):
        file_size = 0

    if file_size <= 0:
        raise ValidationError(
            "El archivo PDF está vacío."
        )

    if file_size > MAX_PRIMARY_PDF_BYTES:
        raise ValidationError(
            "El PDF principal supera el tamaño máximo de 5 MB."
        )

    header = _read_file_header(value)

    if (
        header
        and not header.startswith(b"%PDF-")
    ):
        raise ValidationError(
            "El archivo no contiene una firma PDF válida."
        )

    return value


def _querydict_to_dict(data):
    if hasattr(data, "lists"):
        output = {}

        for key, values in data.lists():
            if not values:
                output[key] = ""
            elif len(values) == 1:
                output[key] = values[0]
            else:
                output[key] = values

        return output

    return dict(data)


def _parse_autores_payload(raw_value):
    autores = raw_value

    if (
        isinstance(autores, list)
        and len(autores) == 1
        and isinstance(
            autores[0],
            list,
        )
    ):
        autores = autores[0]

    if (
        isinstance(autores, list)
        and len(autores) == 1
        and isinstance(
            autores[0],
            str,
        )
    ):
        autores = autores[0]

    if autores in (
        None,
        "",
        "[]",
        "null",
        "None",
        [],
        {},
    ):
        return []

    if isinstance(autores, str):
        try:
            autores = json.loads(
                autores.strip()
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

    if not isinstance(autores, list):
        raise ValidationError(
            {
                "autores": [
                    "Los autores deben enviarse como una lista."
                ]
            }
        )

    normalized = []

    for index, item in enumerate(
        autores,
        start=1,
    ):
        if not isinstance(item, dict):
            raise ValidationError(
                {
                    "autores": [
                        f"El autor #{index} debe ser un objeto JSON."
                    ]
                }
            )

        item = dict(item)

        orden = item.get("orden")

        if orden in (None, ""):
            raise ValidationError(
                {
                    "autores": [
                        f"El autor #{index} debe incluir el campo 'orden'."
                    ]
                }
            )

        try:
            orden = int(orden)
        except (
            TypeError,
            ValueError,
        ):
            raise ValidationError(
                {
                    "autores": [
                        f"El orden del autor #{index} debe ser numérico."
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

        # Compatibilidad temporal con formularios antiguos.
        # Los roles de autoría ya no forman parte del dominio.
        item.pop("rol_autoria", None)
        item.pop("role", None)

        normalized.append(item)

    return normalized


def _normalize_validated_autores(autores):
    if not autores:
        raise ValidationError(
            {
                "autores": [
                    "Debe registrar al menos un autor."
                ]
            }
        )

    autor_ids = []
    ordenes = []

    for item in autores:
        autor = item.get("autor")

        autor_id = getattr(
            autor,
            "id",
            None,
        )

        if autor_id is None:
            raise ValidationError(
                {
                    "autores": [
                        "Se encontró un autor inválido."
                    ]
                }
            )

        autor_ids.append(autor_id)

        orden = item.get("orden")

        if orden is None:
            raise ValidationError(
                {
                    "autores": [
                        "Cada autor debe tener un orden."
                    ]
                }
            )

        ordenes.append(int(orden))

    if len(autor_ids) != len(set(autor_ids)):
        raise ValidationError(
            {
                "autores": [
                    "No se permite repetir el mismo autor."
                ]
            }
        )

    if len(ordenes) != len(set(ordenes)):
        raise ValidationError(
            {
                "autores": [
                    "No se permite repetir el orden de los autores."
                ]
            }
        )

    expected_orders = list(
        range(1, len(autores) + 1)
    )

    if sorted(ordenes) != expected_orders:
        raise ValidationError(
            {
                "autores": [
                    "Los órdenes de los autores deben ser "
                    f"consecutivos: {expected_orders}."
                ]
            }
        )

    autores = sorted(
        autores,
        key=lambda item: int(
            item["orden"]
        ),
    )


    return autores


class ArticuloRegistroSerializer(
    PublicacionCamposBaseMixin,
    serializers.ModelSerializer,
):
    autores = AutorParticipacionSerializer(
        many=True,
        write_only=True,
        required=True,
    )

    tipo_codigo = serializers.CharField(
        write_only=True,
        required=True,
    )

    # Se recibe para validar la relación,
    # pero NO se almacena en Publicacion.
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
        error_messages={
            "does_not_exist": (
                "El proyecto seleccionado no existe "
                "o no está disponible."
            ),
            "incorrect_type": "Proyecto inválido.",
        },
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


    archivo_pdf = serializers.FileField(
        required=False,
        allow_null=True,
        write_only=True,
    )

    numero_revista = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    factor_impacto = serializers.ChoiceField(
        choices=Articulo.FACTOR_IMPACTO,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    cuartil = serializers.ChoiceField(
        choices=Articulo.CUARTIL,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    base_datos_indexada = serializers.ChoiceField(
        choices=Articulo.BASES_DATOS,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = Articulo

        fields = [
            "id",
            "tipo_codigo",
            "facultad",
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "origen_tipo",
            "origen_grado",
            "anio_publicacion",
            "mes_publicacion",
            "archivo_pdf",
            "tipo_articulo",
            "nombre_articulo",
            "base_datos_indexada",
            "base_datos_otra",
            "codigo_doi",
            "codigo_issn",
            "nombre_revista",
            "numero_revista",
            "link_revista",
            "link_publicacion",
            "factor_impacto",
            "cuartil",
            "sjr",
            "autores",
        ]

        read_only_fields = [
            "id",
        ]

        extra_kwargs = {
            "tipo_articulo": {
                "required": False,
            },
            "base_datos_otra": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "codigo_doi": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "link_revista": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "link_publicacion": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "sjr": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        }

    def to_internal_value(self, data):
        data = _querydict_to_dict(data)

        data["autores"] = (
            _parse_autores_payload(
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

    def validate(self, attrs):
        attrs = self._aplicar_reglas_origen(
            attrs
        )

        tipo_codigo = _to_lower(
            attrs.get("tipo_codigo")
        )

        valid_codes = {
            "articulo_regional",
            "articulo_alto_impacto",
        }

        if tipo_codigo not in valid_codes:
            raise ValidationError(
                {
                    "tipo_codigo": [
                        "Tipo inválido. Use "
                        "'articulo_regional' o "
                        "'articulo_alto_impacto'."
                    ]
                }
            )

        attrs["tipo_codigo"] = (
            tipo_codigo
        )

        attrs["tipo_articulo"] = (
            "regional"
            if tipo_codigo
            == "articulo_regional"
            else "alto_impacto"
        )

        facultad = attrs.get("facultad")
        carrera = attrs.get("carrera")
        proyecto = attrs.get("proyecto")

        if (
            carrera
            and facultad
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
        subarea = attrs.get("subarea")

        if subarea and not area:
            attrs["area"] = subarea.area
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

        autores = (
            _normalize_validated_autores(
                attrs.get("autores") or []
            )
        )

        attrs["autores"] = autores

        for field in (
            "nombre_articulo",
            "codigo_issn",
            "nombre_revista",
            "codigo_doi",
            "base_datos_otra",
            "link_revista",
            "link_publicacion",
            "sjr",
        ):
            if field in attrs:
                attrs[field] = (
                    _none_if_blank(
                        attrs.get(field)
                    )
                )

        for required_field in (
            "nombre_articulo",
            "codigo_issn",
            "nombre_revista",
        ):
            if not _to_str(
                attrs.get(
                    required_field
                )
            ):
                raise ValidationError(
                    {
                        required_field: [
                            "Este campo es obligatorio."
                        ]
                    }
                )

        if (
            attrs["tipo_articulo"]
            == "regional"
        ):
            attrs["factor_impacto"] = None
            attrs["cuartil"] = None
            attrs["sjr"] = None

            base_datos = _to_lower(
                attrs.get(
                    "base_datos_indexada"
                )
            )

            valid_bases = {
                value
                for value, _label
                in Articulo.BASES_DATOS
            }

            if not base_datos:
                raise ValidationError(
                    {
                        "base_datos_indexada": [
                            "Debe seleccionar una base "
                            "de datos o indexación."
                        ]
                    }
                )

            if base_datos not in valid_bases:
                raise ValidationError(
                    {
                        "base_datos_indexada": [
                            "La base de datos seleccionada "
                            "es inválida."
                        ]
                    }
                )

            attrs[
                "base_datos_indexada"
            ] = base_datos

            if base_datos == "otra":
                otra = _none_if_blank(
                    attrs.get(
                        "base_datos_otra"
                    )
                )

                if not otra:
                    raise ValidationError(
                        {
                            "base_datos_otra": [
                                "Debe especificar la base de datos "
                                "cuando seleccione 'Otra'."
                            ]
                        }
                    )

                attrs[
                    "base_datos_otra"
                ] = otra

            else:
                attrs[
                    "base_datos_otra"
                ] = None

        else:
            attrs[
                "base_datos_indexada"
            ] = None

            attrs[
                "base_datos_otra"
            ] = None

            factor = _to_lower(
                attrs.get(
                    "factor_impacto"
                )
            )

            cuartil = _to_lower(
                attrs.get("cuartil")
            )

            sjr = _none_if_blank(
                attrs.get("sjr")
            )

            valid_factors = {
                value
                for value, _label
                in Articulo.FACTOR_IMPACTO
            }

            valid_quartiles = {
                value
                for value, _label
                in Articulo.CUARTIL
            }

            if (
                factor
                and factor
                not in valid_factors
            ):
                raise ValidationError(
                    {
                        "factor_impacto": [
                            "El factor de impacto es inválido."
                        ]
                    }
                )

            if (
                cuartil
                and cuartil
                not in valid_quartiles
            ):
                raise ValidationError(
                    {
                        "cuartil": [
                            "El cuartil es inválido."
                        ]
                    }
                )

            if (
                factor == "sjr"
                and not sjr
            ):
                raise ValidationError(
                    {
                        "sjr": [
                            "Debe ingresar el valor SJR "
                            "cuando el factor es SJR."
                        ]
                    }
                )

            if factor != "sjr":
                sjr = None

            attrs[
                "factor_impacto"
            ] = factor or None

            attrs[
                "cuartil"
            ] = cuartil or None

            attrs["sjr"] = sjr

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

        validated_data.pop(
            "tipo_codigo",
            None,
        )

        tipo_articulo = (
            validated_data.pop(
                "tipo_articulo"
            )
        )

        facultad = (
            validated_data.pop(
                "facultad"
            )
        )

        carrera = (
            validated_data.pop(
                "carrera"
            )
        )

        proyecto = (
            validated_data.pop(
                "proyecto",
                None,
            )
        )

        area = validated_data.pop(
            "area",
            None,
        )

        subarea = validated_data.pop(
            "subarea",
            None,
        )

        origen_tipo = (
            validated_data.pop(
                "origen_tipo",
                "ninguno",
            )
        )

        origen_grado = (
            validated_data.pop(
                "origen_grado",
                None,
            )
        )

        anio_publicacion = validated_data.pop(
            "anio_publicacion"
        )

        mes_publicacion = validated_data.pop(
            "mes_publicacion",
            None,
        )

        archivo_pdf = (
            validated_data.pop(
                "archivo_pdf",
                None,
            )
        )

        if tipo_articulo == "regional":
            tipo = (
                obtener_o_crear_tipo_publicacion(
                    codigo="articulo_regional",
                    nombre="Artículo Regional",
                    categoria="articulo",
                    orden=2,
                )
            )
        else:
            tipo = (
                obtener_o_crear_tipo_publicacion(
                    codigo="articulo_alto_impacto",
                    nombre="Artículo de Alto Impacto",
                    categoria="articulo",
                    orden=2,
                )
            )

        publicacion = crear_publicacion_base(
            proyecto=proyecto,
            tipo=tipo,
            usuario=usuario_creador,

            # Solo se utiliza para comprobar
            # Carrera -> Facultad.
            facultad=facultad,

            carrera=carrera,
            area=area,
            subarea=subarea,
            pais=None,
            ciudad=None,
            origen_tipo=origen_tipo,
            origen_grado=origen_grado,
            anio_publicacion=(
                anio_publicacion
            ),
            mes_publicacion=(
                mes_publicacion
            ),
            archivo_pdf=archivo_pdf,
            registrado_por_admin=(
                registrado_por_admin
            ),
            admin_registrador=(
                admin_registrador
            ),
        )

        articulo = Articulo.objects.create(
            publicacion=publicacion,
            tipo_articulo=tipo_articulo,
            **validated_data,
        )

        registrar_autores_publicacion(
            publicacion=publicacion,
            autores_data=autores_data,
        )

        return articulo