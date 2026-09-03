import json
import os

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import (
    AreaConocimiento,
    Carrera,
    Ciudad,
    Pais,
    Ponencia,
    Proyecto,
    Sede,
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
from core.publicaciones.services.publicaciones_duplicados_services import (
    validar_duplicados_fuerte_publicacion,
)
from core.publicaciones.utils.publicaciones_creation_context_utils import (
    resolve_publicacion_creation_context,
)


MAX_PRIMARY_PDF_BYTES = 5 * 1024 * 1024

ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


def _none_if_blank(value):
    value = str(
        value or ""
    ).strip()

    return value or None


def _normalize_city_name(value):
    return " ".join(
        str(
            value or ""
        ).split()
    )


def _resolve_city_for_create(
    *,
    pais,
    ciudad=None,
    ciudad_manual=None,
):
    """
    Devuelve una ciudad existente o crea la escrita manualmente.

    El bloqueo del país serializa las altas manuales del mismo
    catálogo y evita duplicados cuando dos solicitudes intentan
    crear simultáneamente la misma ciudad.
    """
    if ciudad is not None:
        return ciudad

    nombre = _normalize_city_name(
        ciudad_manual
    )

    if not nombre:
        raise ValidationError(
            {
                "ciudad": [
                    "Debe seleccionar o escribir una ciudad."
                ]
            }
        )

    pais_locked = (
        Pais.objects
        .select_for_update()
        .get(
            pk=pais.pk
        )
    )

    existente = (
        Ciudad.objects
        .filter(
            pais=pais_locked,
            nombre__iexact=nombre,
        )
        .order_by(
            "id"
        )
        .first()
    )

    if existente is not None:
        return existente

    return Ciudad.objects.create(
        pais=pais_locked,
        nombre=nombre,
    )


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

    if (
        os.path.splitext(
            file_name.lower()
        )[1]
        != ".pdf"
    ):
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
        size = int(
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
        size = 0

    if size <= 0:
        raise ValidationError(
            "El archivo PDF está vacío."
        )

    if size > MAX_PRIMARY_PDF_BYTES:
        raise ValidationError(
            "El PDF principal supera el tamaño máximo de 5 MB."
        )

    header = _read_header(value)

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

        # Compatibilidad temporal con formularios antiguos.
        # Los roles de autoría ya no forman parte del dominio.
        item.pop("rol_autoria", None)
        item.pop("role", None)

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

    ids = [
        item["autor"].id
        for item in autores
    ]

    orders = [
        int(item["orden"])
        for item in autores
    ]

    if len(ids) != len(set(ids)):
        raise ValidationError(
            {
                "autores": [
                    "No se permite repetir el mismo autor."
                ]
            }
        )

    if (
        len(orders)
        != len(set(orders))
    ):
        raise ValidationError(
            {
                "autores": [
                    "No se permite repetir el orden."
                ]
            }
        )

    expected_orders = list(
        range(1, len(autores) + 1)
    )

    if sorted(orders) != expected_orders:
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


class PonenciaRegistroSerializer(
    PublicacionCamposBaseMixin,
    serializers.ModelSerializer,
):
    autores = AutorParticipacionSerializer(
        many=True,
        write_only=True,
        required=True,
    )

    sede = serializers.PrimaryKeyRelatedField(
        queryset=Sede.objects.filter(
            activa=True
        ).order_by(
            "nombre",
            "id",
        ),
        required=False,
        allow_null=True,
        write_only=True,
        error_messages={
            "does_not_exist": (
                "La sede seleccionada no existe "
                "o no está activa."
            ),
            "incorrect_type": (
                "Sede inválida."
            ),
        },
    )

    carrera = serializers.PrimaryKeyRelatedField(
        queryset=Carrera.objects.select_related(
            "facultad"
        ).all(),
        write_only=True,
    )

    proyecto = serializers.PrimaryKeyRelatedField(
        queryset=Proyecto.objects.select_related(
            "sede",
            "carrera",
            "carrera__facultad",
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

    pais = serializers.PrimaryKeyRelatedField(
        queryset=Pais.objects.all(),
        required=True,
        write_only=True,
    )

    ciudad = serializers.PrimaryKeyRelatedField(
        queryset=Ciudad.objects.select_related(
            "pais"
        ).all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    ciudad_manual = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
        write_only=True,
    )


    archivo_pdf = serializers.FileField(
        required=False,
        allow_null=True,
        write_only=True,
    )

    tipo_presentacion = serializers.ChoiceField(
        choices=Ponencia.TIPO_PRESENTACION,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    tipo_presentacion_otro = serializers.CharField(
        max_length=150,
        required=False,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
    )

    revisor_par_arbitraje = serializers.ChoiceField(
        choices=[
            ("si", "Sí"),
            ("no", "No"),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = Ponencia

        fields = [
            "id",
            "sede",
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "pais",
            "ciudad",
            "ciudad_manual",
            "origen_tipo",
            "origen_grado",
            "anio_publicacion",
            "mes_publicacion",
            "archivo_pdf",
            "nombre_evento",
            "nombre_ponencia",
            "codigo_issn_isbn",
            "tipo_presentacion",
            "tipo_presentacion_otro",
            "link_evento",
            "revisor_par_arbitraje",
            "autores",
        ]

        read_only_fields = [
            "id",
        ]

        extra_kwargs = {
            "codigo_issn_isbn": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "link_evento": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        }

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

        sede = attrs.get(
            "sede"
        )

        carrera = attrs.get(
            "carrera"
        )

        proyecto = attrs.get(
            "proyecto"
        )

        if (
            sede
            and carrera
            and not carrera.sedes_carrera.filter(
                sede_id=sede.id,
                activa=True,
            ).exists()
        ):
            raise ValidationError(
                {
                    "carrera": [
                        "La carrera seleccionada no está "
                        "habilitada en la sede indicada."
                    ]
                }
            )

        if (
            proyecto
            and sede
            and getattr(
                proyecto,
                "sede_id",
                None,
            )
            and proyecto.sede_id != sede.id
        ):
            raise ValidationError(
                {
                    "proyecto": [
                        "El proyecto seleccionado pertenece "
                        "a una sede diferente."
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

        pais = attrs.get(
            "pais"
        )

        ciudad = attrs.get(
            "ciudad"
        )

        ciudad_manual = (
            _normalize_city_name(
                attrs.get(
                    "ciudad_manual"
                )
            )
        )

        if not pais:
            raise ValidationError(
                {
                    "pais": [
                        "Debe seleccionar un país."
                    ]
                }
            )

        if (
            not ciudad
            and not ciudad_manual
        ):
            raise ValidationError(
                {
                    "ciudad": [
                        "Debe seleccionar o escribir una ciudad."
                    ]
                }
            )

        if (
            ciudad is not None
            and ciudad.pais_id
            != pais.id
        ):
            raise ValidationError(
                {
                    "ciudad": [
                        "La ciudad seleccionada no pertenece "
                        "al país indicado."
                    ]
                }
            )

        if ciudad is not None:
            ciudad_manual = ""

        attrs[
            "ciudad_manual"
        ] = ciudad_manual

        area = attrs.get(
            "area"
        )

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

        nombre_evento = str(
            attrs.get(
                "nombre_evento"
            )
            or ""
        ).strip()

        nombre_ponencia = str(
            attrs.get(
                "nombre_ponencia"
            )
            or ""
        ).strip()

        if not nombre_evento:
            raise ValidationError(
                {
                    "nombre_evento": [
                        "El nombre del evento es obligatorio."
                    ]
                }
            )

        if not nombre_ponencia:
            raise ValidationError(
                {
                    "nombre_ponencia": [
                        "El nombre de la ponencia es obligatorio."
                    ]
                }
            )

        attrs[
            "nombre_evento"
        ] = nombre_evento

        attrs[
            "nombre_ponencia"
        ] = nombre_ponencia

        attrs[
            "codigo_issn_isbn"
        ] = _none_if_blank(
            attrs.get(
                "codigo_issn_isbn"
            )
        )

        attrs[
            "link_evento"
        ] = _none_if_blank(
            attrs.get(
                "link_evento"
            )
        )

        tipo_presentacion = (
            _none_if_blank(
                attrs.get(
                    "tipo_presentacion"
                )
            )
        )

        if tipo_presentacion:
            tipo_presentacion = (
                tipo_presentacion.lower()
            )

        tipo_otro = (
            _none_if_blank(
                attrs.get(
                    "tipo_presentacion_otro"
                )
            )
        )

        if (
            tipo_presentacion
            == "otro"
        ):
            if not tipo_otro:
                raise ValidationError(
                    {
                        "tipo_presentacion_otro": [
                            "Debe escribir el tipo de presentación "
                            "cuando seleccione 'Otro'."
                        ]
                    }
                )
        else:
            tipo_otro = None

        attrs[
            "tipo_presentacion"
        ] = tipo_presentacion

        attrs[
            "tipo_presentacion_otro"
        ] = tipo_otro

        revisor = _none_if_blank(
            attrs.get(
                "revisor_par_arbitraje"
            )
        )

        if revisor:
            revisor = revisor.lower()

        if (
            revisor
            and revisor
            not in {
                "si",
                "no",
            }
        ):
            raise ValidationError(
                {
                    "revisor_par_arbitraje": [
                        "El valor debe ser 'si' o 'no'."
                    ]
                }
            )

        attrs[
            "revisor_par_arbitraje"
        ] = revisor

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

        sede = (
            validated_data.pop(
                "sede",
                None,
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

        pais = validated_data.pop(
            "pais"
        )

        ciudad = validated_data.pop(
            "ciudad",
            None,
        )

        ciudad_manual = (
            validated_data.pop(
                "ciudad_manual",
                None,
            )
        )

        ciudad = _resolve_city_for_create(
            pais=pais,
            ciudad=ciudad,
            ciudad_manual=ciudad_manual,
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

        tipo = (
            obtener_o_crear_tipo_publicacion(
                codigo="ponencia",
                nombre="Ponencia",
                categoria="ponencia",
                orden=1,
            )
        )

        # Facultad siempre se deriva de Carrera.
        facultad = carrera.facultad

        publicacion = crear_publicacion_base(
            proyecto=proyecto,
            tipo=tipo,
            usuario=usuario_creador,
            facultad=facultad,
            sede=sede,
            carrera=carrera,
            area=area,
            subarea=subarea,
            pais=pais,
            ciudad=ciudad,
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

        ponencia = Ponencia.objects.create(
            publicacion=publicacion,
            **validated_data,
        )

        validar_duplicados_fuerte_publicacion(
            publicacion
        )

        registrar_autores_publicacion(
            publicacion=publicacion,
            autores_data=autores_data,
        )

        return ponencia
