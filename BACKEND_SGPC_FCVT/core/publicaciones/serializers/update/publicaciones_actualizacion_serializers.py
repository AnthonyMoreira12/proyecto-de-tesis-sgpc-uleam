import json
import os

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import (
    AreaConocimiento,
    Articulo,
    Autor,
    CapituloLibro,
    Carrera,
    Ciudad,
    Libro,
    Pais,
    Ponencia,
    Proyecto,
    Publicacion,
    PublicacionArchivo,
    PublicacionAutor,
    Subarea,
)


MAX_PRIMARY_PDF_BYTES = (
    5 * 1024 * 1024
)

ALLOWED_PDF_EXTENSIONS = {
    ".pdf",
}

ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}


def _to_str(value):
    return (
        ""
        if value is None
        else str(value).strip()
    )


def _to_lower(value):
    value = _to_str(value)

    return (
        value.lower()
        if value
        else ""
    )


def _none_if_blank(value):
    value = _to_str(value)

    return (
        value
        or None
    )


def _to_bool(value):
    if isinstance(
        value,
        bool,
    ):
        return value

    if value in (
        1,
        "1",
    ):
        return True

    if value in (
        0,
        "0",
    ):
        return False

    value = _to_lower(value)

    return value in {
        "true",
        "yes",
        "y",
        "on",
        "si",
        "sí",
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

    original_position = 0

    try:
        if hasattr(
            file_obj,
            "tell",
        ):
            original_position = (
                file_obj.tell()
            )
    except (
        OSError,
        ValueError,
    ):
        original_position = 0

    try:
        if hasattr(
            file_obj,
            "seek",
        ):
            file_obj.seek(0)

        content = file_obj.read(
            max_bytes
        )

        if isinstance(
            content,
            str,
        ):
            content = (
                content.encode(
                    "utf-8",
                    errors="ignore",
                )
            )

        return bytes(
            content
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
                    original_position
                )
        except (
            OSError,
            ValueError,
        ):
            pass


def validate_primary_pdf_file(value):
    if not value:
        return value

    file_name = _to_str(
        getattr(
            value,
            "name",
            "",
        )
    )

    extension = os.path.splitext(
        file_name.lower()
    )[1]

    if (
        extension
        not in ALLOWED_PDF_EXTENSIONS
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
            "El PDF principal supera "
            "el tamaño máximo de 5 MB."
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
            "El archivo no contiene "
            "una firma PDF válida."
        )

    return value


def _django_validation_to_drf(exc):
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


class AutorActualizacionItemSerializer(
    serializers.Serializer
):
    """
    Autor incluido durante la actualización de una publicación.

    Todos los participantes se consideran autores. ``orden`` representa
    únicamente la posición bibliográfica y no una jerarquía de autoría.
    """

    autor_id = serializers.IntegerField(
        min_value=1,
    )

    orden = serializers.IntegerField(
        min_value=1,
    )


class PublicacionActualizacionSerializer(
    serializers.Serializer
):
    # ---------------------------------------------------------
    # Publicación base
    # ---------------------------------------------------------

    carrera = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                Carrera.objects
                .select_related(
                    "facultad"
                )
                .all()
            ),
            required=False,
        )
    )

    proyecto = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                Proyecto.objects
                .select_related(
                    "carrera"
                )
                .all()
            ),
            required=False,
            allow_null=True,
        )
    )

    area = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                AreaConocimiento.objects
                .all()
            ),
            required=False,
            allow_null=True,
        )
    )

    subarea = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                Subarea.objects
                .select_related(
                    "area"
                )
                .all()
            ),
            required=False,
            allow_null=True,
        )
    )

    pais = (
        serializers.PrimaryKeyRelatedField(
            queryset=Pais.objects.all(),
            required=False,
            allow_null=True,
        )
    )

    ciudad = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                Ciudad.objects
                .select_related(
                    "pais"
                )
                .all()
            ),
            required=False,
            allow_null=True,
        )
    )

    anio_publicacion = serializers.IntegerField(
        required=False,
        min_value=1900,
    )

    mes_publicacion = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=12,
    )

    origen_tipo = (
        serializers.ChoiceField(
            choices=Publicacion.ORIGEN_TIPO,
            required=False,
        )
    )

    origen_grado = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            allow_null=True,
            max_length=120,
            trim_whitespace=True,
        )
    )

    archivo_pdf = (
        serializers.FileField(
            required=False,
            allow_null=True,
        )
    )

    # ---------------------------------------------------------
    # Acciones PDF
    # ---------------------------------------------------------

    quitar_pdf_actual = (
        serializers.BooleanField(
            required=False,
            default=False,
        )
    )

    quitar_archivo_pdf = (
        serializers.BooleanField(
            required=False,
            default=False,
        )
    )

    quitar_archivo_adjunto_id = (
        serializers.IntegerField(
            required=False,
            allow_null=True,
            min_value=1,
        )
    )

    # ---------------------------------------------------------
    # Autores
    # ---------------------------------------------------------

    autores = (
        AutorActualizacionItemSerializer(
            many=True,
            required=False,
        )
    )

    # ---------------------------------------------------------
    # Ponencia
    # ---------------------------------------------------------

    tipo_presentacion = (
        serializers.ChoiceField(
            choices=Ponencia.TIPO_PRESENTACION,
            required=False,
            allow_null=True,
            allow_blank=True,
        )
    )

    tipo_presentacion_otro = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            allow_null=True,
            max_length=150,
        )
    )

    nombre_evento = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=255,
        )
    )

    nombre_ponencia = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=255,
        )
    )

    codigo_issn_isbn = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            allow_null=True,
            max_length=100,
        )
    )

    link_evento = (
        serializers.URLField(
            required=False,
            allow_blank=True,
            allow_null=True,
            max_length=500,
        )
    )

    # ---------------------------------------------------------
    # Artículo
    # ---------------------------------------------------------

    nombre_articulo = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=255,
        )
    )

    base_datos_indexada = (
        serializers.ChoiceField(
            choices=Articulo.BASES_DATOS,
            required=False,
            allow_null=True,
            allow_blank=True,
        )
    )

    base_datos_otra = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            allow_null=True,
            max_length=150,
        )
    )

    codigo_doi = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            allow_null=True,
            max_length=150,
        )
    )

    codigo_issn = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=100,
        )
    )

    nombre_revista = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=255,
        )
    )

    numero_revista = (
        serializers.IntegerField(
            required=False,
            allow_null=True,
            min_value=1,
        )
    )

    link_publicacion = (
        serializers.URLField(
            required=False,
            allow_blank=True,
            allow_null=True,
            max_length=500,
        )
    )

    link_revista = (
        serializers.URLField(
            required=False,
            allow_blank=True,
            allow_null=True,
            max_length=500,
        )
    )

    factor_impacto = (
        serializers.ChoiceField(
            choices=Articulo.FACTOR_IMPACTO,
            required=False,
            allow_null=True,
            allow_blank=True,
        )
    )

    cuartil = (
        serializers.ChoiceField(
            choices=Articulo.CUARTIL,
            required=False,
            allow_null=True,
            allow_blank=True,
        )
    )

    sjr = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )

    jcr = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=100,
    )

    # ---------------------------------------------------------
    # Ponencia / Libro / Capítulo
    # ---------------------------------------------------------

    revisor_par_arbitraje = (
        serializers.ChoiceField(
            choices=[
                ("si", "Sí"),
                ("no", "No"),
            ],
            required=False,
            allow_null=True,
            allow_blank=True,
        )
    )

    # ---------------------------------------------------------
    # Libro
    # ---------------------------------------------------------

    nombre_libro = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=255,
        )
    )

    codigo_isbn = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=100,
        )
    )

    editorial_compilador = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=255,
        )
    )

    link_libro = (
        serializers.URLField(
            required=False,
            allow_blank=True,
            max_length=500,
        )
    )

    # ---------------------------------------------------------
    # Capítulo
    # ---------------------------------------------------------

    nombre_capitulo = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=255,
        )
    )

    editor_compilador = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=255,
        )
    )

    link_capitulo = (
        serializers.URLField(
            required=False,
            allow_blank=True,
            max_length=500,
        )
    )

    # =========================================================
    # INPUT
    # =========================================================

    def _querydict_to_dict(
        self,
        data,
    ):
        if hasattr(
            data,
            "lists",
        ):
            output = {}

            for key, values in data.lists():
                if not values:
                    output[key] = ""

                elif len(values) == 1:
                    output[key] = (
                        values[0]
                    )

                else:
                    output[key] = (
                        values
                    )

            return output

        return dict(data)

    def _normalize_autores_input(
        self,
        data,
    ):
        if "autores" not in data:
            return data

        autores = data.get(
            "autores"
        )

        if (
            isinstance(
                autores,
                list,
            )
            and len(autores) == 1
        ):
            autores = autores[0]

        if autores in (
            None,
            "",
            "null",
            "None",
        ):
            data["autores"] = []
            return data

        if isinstance(
            autores,
            str,
        ):
            raw = autores.strip()

            if raw in {
                "",
                "[]",
                "null",
                "None",
            }:
                data["autores"] = []
                return data

            try:
                autores = json.loads(
                    raw
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
            autores,
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
            autores,
            start=1,
        ):
            if not isinstance(
                item,
                dict,
            ):
                raise ValidationError(
                    {
                        "autores": [
                            f"El autor #{index} "
                            "debe ser un objeto."
                        ]
                    }
                )

            item = dict(item)

            if (
                "autor_id" not in item
                and "autor" in item
            ):
                item["autor_id"] = (
                    item["autor"]
                )

            # Compatibilidad temporal con payloads antiguos.
            # Los roles de autoría ya no forman parte del dominio.
            item.pop("rol_autoria", None)
            item.pop("role", None)

            normalized.append(
                item
            )

        data["autores"] = (
            normalized
        )

        return data

    def to_internal_value(
        self,
        data,
    ):
        data = (
            self._querydict_to_dict(
                data
            )
        )

        data = (
            self._normalize_autores_input(
                data
            )
        )

        return super().to_internal_value(
            data
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def _instance_tipo_codigo(
        self,
    ):
        instance = self.instance

        if instance is None:
            return ""

        tipo = getattr(
            instance,
            "tipo",
            None,
        )

        codigo = _to_lower(
            getattr(
                tipo,
                "codigo",
                None,
            )
        )

        categoria = _to_lower(
            getattr(
                tipo,
                "categoria",
                None,
            )
        )

        articulo = getattr(
            instance,
            "articulo",
            None,
        )

        if (
            categoria == "articulo"
            or codigo
            in {
                "articulo",
                "articulo_regional",
                "articulo_alto_impacto",
            }
        ):
            tipo_articulo = _to_lower(
                getattr(
                    articulo,
                    "tipo_articulo",
                    None,
                )
            )

            if (
                tipo_articulo
                == "regional"
            ):
                return (
                    "articulo_regional"
                )

            if (
                tipo_articulo
                == "alto_impacto"
            ):
                return (
                    "articulo_alto_impacto"
                )

        if (
            categoria == "ponencia"
            or codigo == "ponencia"
        ):
            return "ponencia"

        if (
            categoria == "libro"
            or codigo == "libro"
        ):
            return "libro"

        if (
            categoria == "capitulo"
            or codigo
            in {
                "capitulo",
                "capitulo_libro",
            }
        ):
            return "capitulo_libro"

        return codigo

    def _articulo_instance(
        self,
    ):
        return getattr(
            self.instance,
            "articulo",
            None,
        )

    def _ponencia_instance(
        self,
    ):
        return getattr(
            self.instance,
            "ponencia",
            None,
        )

    def _libro_instance(
        self,
    ):
        return getattr(
            self.instance,
            "libro",
            None,
        )

    def _capitulo_instance(
        self,
    ):
        return getattr(
            self.instance,
            "capitulo_libro",
            None,
        )

    def _final_value(
        self,
        attrs,
        field,
        current_value,
    ):
        if field in attrs:
            return attrs[field]

        return current_value

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def validate_archivo_pdf(
        self,
        value,
    ):
        return (
            validate_primary_pdf_file(
                value
            )
        )

    def _validate_pdf_actions(
        self,
        attrs,
    ):
        quitar_actual = _to_bool(
            attrs.get(
                "quitar_pdf_actual",
                False,
            )
        )

        quitar_principal = _to_bool(
            attrs.get(
                "quitar_archivo_pdf",
                False,
            )
        )

        nuevo_pdf = attrs.get(
            "archivo_pdf"
        )

        if (
            nuevo_pdf
            and (
                quitar_actual
                or quitar_principal
            )
        ):
            raise ValidationError(
                {
                    "archivo_pdf": [
                        "No puede cargar un PDF nuevo "
                        "y eliminar el PDF actual "
                        "en la misma operación."
                    ]
                }
            )

        return attrs

    def _validate_relaciones_generales(
        self,
        attrs,
    ):
        instance = self.instance

        carrera = self._final_value(
            attrs,
            "carrera",
            getattr(
                instance,
                "carrera",
                None,
            ),
        )

        proyecto = self._final_value(
            attrs,
            "proyecto",
            getattr(
                instance,
                "proyecto",
                None,
            ),
        )

        if carrera is None:
            raise ValidationError(
                {
                    "carrera": [
                        "La carrera es obligatoria."
                    ]
                }
            )

        if (
            proyecto
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

        return attrs

    def _validate_area_subarea(
        self,
        attrs,
    ):
        instance = self.instance

        area = self._final_value(
            attrs,
            "area",
            getattr(
                instance,
                "area",
                None,
            ),
        )

        subarea = self._final_value(
            attrs,
            "subarea",
            getattr(
                instance,
                "subarea",
                None,
            ),
        )

        if (
            subarea
            and not area
        ):
            area = subarea.area
            attrs["area"] = area

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

        return attrs

    def _validate_periodo_publicacion(
        self,
        attrs,
    ):
        """
        Garantiza que la publicación mantenga un año válido y que
        el mes, cuando exista, esté entre 1 y 12.
        """

        instance = self.instance

        anio = self._final_value(
            attrs,
            "anio_publicacion",
            getattr(instance, "anio_publicacion", None),
        )

        if anio in (None, ""):
            raise ValidationError(
                {
                    "anio_publicacion": [
                        "El año de publicación es obligatorio."
                    ]
                }
            )

        try:
            anio = int(anio)
        except (TypeError, ValueError):
            raise ValidationError(
                {
                    "anio_publicacion": [
                        "El año de publicación debe ser numérico."
                    ]
                }
            )

        if anio < 1900:
            raise ValidationError(
                {
                    "anio_publicacion": [
                        "El año de publicación debe ser mayor "
                        "o igual a 1900."
                    ]
                }
            )

        mes = self._final_value(
            attrs,
            "mes_publicacion",
            getattr(instance, "mes_publicacion", None),
        )

        if mes in ("", None):
            mes = None
        else:
            try:
                mes = int(mes)
            except (TypeError, ValueError):
                raise ValidationError(
                    {
                        "mes_publicacion": [
                            "El mes de publicación debe ser numérico."
                        ]
                    }
                )

            if not 1 <= mes <= 12:
                raise ValidationError(
                    {
                        "mes_publicacion": [
                            "El mes de publicación debe estar "
                            "entre 1 y 12."
                        ]
                    }
                )

        attrs["anio_publicacion"] = anio
        attrs["mes_publicacion"] = mes

        return attrs

    def _validate_origen(
        self,
        attrs,
    ):
        instance = self.instance

        origen_tipo = _to_lower(
            self._final_value(
                attrs,
                "origen_tipo",
                getattr(
                    instance,
                    "origen_tipo",
                    "ninguno",
                ),
            )
        ) or "ninguno"

        origen_grado = _none_if_blank(
            self._final_value(
                attrs,
                "origen_grado",
                getattr(
                    instance,
                    "origen_grado",
                    None,
                ),
            )
        )

        valid_origins = {
            value
            for value, _label
            in Publicacion.ORIGEN_TIPO
        }

        if (
            origen_tipo
            not in valid_origins
        ):
            raise ValidationError(
                {
                    "origen_tipo": [
                        "El origen de la publicación es inválido."
                    ]
                }
            )

        if origen_tipo == "tic":
            if not origen_grado:
                raise ValidationError(
                    {
                        "origen_grado": [
                            "Debe especificar el grado "
                            "o programa cuando el origen "
                            "es un Trabajo de Integración "
                            "Curricular."
                        ]
                    }
                )

        elif origen_tipo == "otro":
            if not origen_grado:
                raise ValidationError(
                    {
                        "origen_grado": [
                            "Debe escribir el origen "
                            "de la publicación."
                        ]
                    }
                )

        else:
            origen_grado = None

        attrs["origen_tipo"] = (
            origen_tipo
        )

        attrs["origen_grado"] = (
            origen_grado
        )

        return attrs

    def _validate_autores(
        self,
        attrs,
    ):
        """
        Valida la lista completa de autores.

        Reglas:
        - al menos un autor;
        - autores no repetidos;
        - orden no repetido;
        - órdenes consecutivos 1..N;
        - el orden se conserva exactamente y no genera roles.
        """

        if "autores" not in attrs:
            return attrs

        autores = attrs.get(
            "autores"
        ) or []

        if not autores:
            raise ValidationError(
                {
                    "autores": [
                        "La publicación debe tener "
                        "al menos un autor."
                    ]
                }
            )

        normalized = []
        autor_ids = []
        ordenes = []

        for index, item in enumerate(
            autores,
            start=1,
        ):
            try:
                autor_id = int(
                    item["autor_id"]
                )
            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                raise ValidationError(
                    {
                        "autores": [
                            f"El autor #{index} debe incluir "
                            "un autor_id válido."
                        ]
                    }
                )

            orden = item.get("orden")

            if orden in (None, ""):
                raise ValidationError(
                    {
                        "autores": [
                            f"El autor #{index} debe incluir "
                            "su orden bibliográfico."
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
                            f"El orden del autor #{index} "
                            "debe ser numérico."
                        ]
                    }
                )

            if orden < 1:
                raise ValidationError(
                    {
                        "autores": [
                            "El orden de los autores debe ser "
                            "mayor o igual a 1."
                        ]
                    }
                )

            autor_ids.append(autor_id)
            ordenes.append(orden)
            normalized.append(
                {
                    "autor_id": autor_id,
                    "orden": orden,
                }
            )

        if len(autor_ids) != len(set(autor_ids)):
            raise ValidationError(
                {
                    "autores": [
                        "No se permite repetir "
                        "el mismo autor."
                    ]
                }
            )

        if len(ordenes) != len(set(ordenes)):
            raise ValidationError(
                {
                    "autores": [
                        "No se permite repetir "
                        "el orden de los autores."
                    ]
                }
            )

        expected_orders = list(
            range(1, len(normalized) + 1)
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

        existing_ids = set(
            Autor.objects
            .filter(id__in=autor_ids)
            .values_list("id", flat=True)
        )

        missing_ids = set(autor_ids) - existing_ids

        if missing_ids:
            raise ValidationError(
                {
                    "autores": [
                        "Uno o más autores "
                        "seleccionados no existen."
                    ]
                }
            )

        normalized.sort(
            key=lambda item: item["orden"]
        )

        attrs["autores"] = normalized

        return attrs

    def _validate_ponencia(
        self,
        attrs,
    ):
        current = (
            self._ponencia_instance()
        )

        nombre_evento = _to_str(
            self._final_value(
                attrs,
                "nombre_evento",
                getattr(
                    current,
                    "nombre_evento",
                    None,
                ),
            )
        )

        nombre_ponencia = _to_str(
            self._final_value(
                attrs,
                "nombre_ponencia",
                getattr(
                    current,
                    "nombre_ponencia",
                    None,
                ),
            )
        )

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

        attrs["nombre_evento"] = (
            nombre_evento
        )

        attrs["nombre_ponencia"] = (
            nombre_ponencia
        )

        tipo_presentacion = _none_if_blank(
            self._final_value(
                attrs,
                "tipo_presentacion",
                getattr(
                    current,
                    "tipo_presentacion",
                    None,
                ),
            )
        )

        if tipo_presentacion:
            tipo_presentacion = (
                tipo_presentacion.lower()
            )

        tipo_otro = _none_if_blank(
            self._final_value(
                attrs,
                "tipo_presentacion_otro",
                getattr(
                    current,
                    "tipo_presentacion_otro",
                    None,
                ),
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
                            "Debe escribir el tipo "
                            "de presentación cuando "
                            "seleccione 'Otro'."
                        ]
                    }
                )
        else:
            tipo_otro = None

        attrs["tipo_presentacion"] = (
            tipo_presentacion
        )

        attrs[
            "tipo_presentacion_otro"
        ] = tipo_otro

        instance = self.instance

        pais = self._final_value(
            attrs,
            "pais",
            getattr(
                instance,
                "pais",
                None,
            ),
        )

        ciudad = self._final_value(
            attrs,
            "ciudad",
            getattr(
                instance,
                "ciudad",
                None,
            ),
        )

        if not pais:
            raise ValidationError(
                {
                    "pais": [
                        "Debe seleccionar un país."
                    ]
                }
            )

        if not ciudad:
            raise ValidationError(
                {
                    "ciudad": [
                        "Debe seleccionar una ciudad."
                    ]
                }
            )

        if (
            ciudad.pais_id
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

        return attrs

    def _validate_articulo(
        self,
        attrs,
    ):
        articulo = (
            self._articulo_instance()
        )

        if articulo is None:
            raise ValidationError(
                {
                    "detail": [
                        "No existe el detalle "
                        "del artículo asociado."
                    ]
                }
            )

        nombre_articulo = _to_str(
            self._final_value(
                attrs,
                "nombre_articulo",
                articulo.nombre_articulo,
            )
        )

        codigo_issn = _to_str(
            self._final_value(
                attrs,
                "codigo_issn",
                articulo.codigo_issn,
            )
        )

        nombre_revista = _to_str(
            self._final_value(
                attrs,
                "nombre_revista",
                articulo.nombre_revista,
            )
        )

        if not nombre_articulo:
            raise ValidationError(
                {
                    "nombre_articulo": [
                        "El nombre del artículo es obligatorio."
                    ]
                }
            )

        if not codigo_issn:
            raise ValidationError(
                {
                    "codigo_issn": [
                        "El código ISSN es obligatorio."
                    ]
                }
            )

        if not nombre_revista:
            raise ValidationError(
                {
                    "nombre_revista": [
                        "El nombre de la revista es obligatorio."
                    ]
                }
            )

        attrs["nombre_articulo"] = (
            nombre_articulo
        )

        attrs["codigo_issn"] = (
            codigo_issn
        )

        attrs["nombre_revista"] = (
            nombre_revista
        )

        tipo_articulo = _to_lower(
            articulo.tipo_articulo
        )

        if tipo_articulo == "regional":
            base_datos = _to_lower(
                self._final_value(
                    attrs,
                    "base_datos_indexada",
                    articulo.base_datos_indexada,
                )
            )

            base_otra = _none_if_blank(
                self._final_value(
                    attrs,
                    "base_datos_otra",
                    articulo.base_datos_otra,
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
                            "Debe seleccionar una "
                            "base de datos o indexación."
                        ]
                    }
                )

            if (
                base_datos
                not in valid_bases
            ):
                raise ValidationError(
                    {
                        "base_datos_indexada": [
                            "La base de datos seleccionada "
                            "es inválida."
                        ]
                    }
                )

            if (
                base_datos == "otra"
                and not base_otra
            ):
                raise ValidationError(
                    {
                        "base_datos_otra": [
                            "Debe especificar la base "
                            "de datos cuando seleccione 'Otra'."
                        ]
                    }
                )

            attrs[
                "base_datos_indexada"
            ] = base_datos

            attrs[
                "base_datos_otra"
            ] = (
                base_otra
                if base_datos == "otra"
                else None
            )

            attrs["factor_impacto"] = (
                None
            )

            attrs["cuartil"] = None

            attrs["sjr"] = None
            attrs["jcr"] = None

        else:
            factor = _to_lower(
                self._final_value(
                    attrs,
                    "factor_impacto",
                    articulo.factor_impacto,
                )
            ) or None

            cuartil = _to_lower(
                self._final_value(
                    attrs,
                    "cuartil",
                    articulo.cuartil,
                )
            ) or None

            sjr = _none_if_blank(
                self._final_value(
                    attrs,
                    "sjr",
                    articulo.sjr,
                )
            )

            jcr = _none_if_blank(
                self._final_value(
                    attrs,
                    "jcr",
                    articulo.jcr,
                )
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

            if factor == "sjr":
                if not sjr:
                    raise ValidationError(
                        {
                            "sjr": [
                                "Debe ingresar el valor SJR "
                                "cuando el factor es SJR."
                            ]
                        }
                    )
                jcr = None

            elif factor == "jcr":
                if not jcr:
                    raise ValidationError(
                        {
                            "jcr": [
                                "Debe ingresar el valor JCR "
                                "cuando el factor es JCR."
                            ]
                        }
                    )
                sjr = None

            else:
                sjr = None
                jcr = None

            attrs[
                "base_datos_indexada"
            ] = None

            attrs[
                "base_datos_otra"
            ] = None

            attrs["factor_impacto"] = (
                factor
            )

            attrs["cuartil"] = (
                cuartil
            )

            attrs["sjr"] = sjr
            attrs["jcr"] = jcr

        return attrs

    def _validate_libro(
        self,
        attrs,
    ):
        libro = self._libro_instance()

        if libro is None:
            raise ValidationError(
                {
                    "detail": [
                        "No existe el detalle "
                        "del libro asociado."
                    ]
                }
            )

        required_fields = {
            "nombre_libro": (
                libro.nombre_libro
            ),
            "codigo_isbn": (
                libro.codigo_isbn
            ),
            "editorial_compilador": (
                libro.editorial_compilador
            ),
            "revisor_par_arbitraje": (
                libro.revisor_par_arbitraje
            ),
            "link_libro": (
                libro.link_libro
            ),
        }

        for field, current in (
            required_fields.items()
        ):
            value = _to_str(
                self._final_value(
                    attrs,
                    field,
                    current,
                )
            )

            if not value:
                raise ValidationError(
                    {
                        field: [
                            "Este campo es obligatorio."
                        ]
                    }
                )

            attrs[field] = value

        return attrs

    def _validate_capitulo(
        self,
        attrs,
    ):
        capitulo = (
            self._capitulo_instance()
        )

        if capitulo is None:
            raise ValidationError(
                {
                    "detail": [
                        "No existe el detalle "
                        "del capítulo asociado."
                    ]
                }
            )

        required_fields = {
            "nombre_capitulo": (
                capitulo.nombre_capitulo
            ),
            "nombre_libro": (
                capitulo.nombre_libro
            ),
            "codigo_isbn": (
                capitulo.codigo_isbn
            ),
            "editor_compilador": (
                capitulo.editor_compilador
            ),
            "revisor_par_arbitraje": (
                capitulo.revisor_par_arbitraje
            ),
            "link_capitulo": (
                capitulo.link_capitulo
            ),
        }

        for field, current in (
            required_fields.items()
        ):
            value = _to_str(
                self._final_value(
                    attrs,
                    field,
                    current,
                )
            )

            if not value:
                raise ValidationError(
                    {
                        field: [
                            "Este campo es obligatorio."
                        ]
                    }
                )

            attrs[field] = value

        return attrs

    def validate(
        self,
        attrs,
    ):
        attrs = self._validate_pdf_actions(
            attrs
        )

        attrs = (
            self._validate_relaciones_generales(
                attrs
            )
        )

        attrs = (
            self._validate_area_subarea(
                attrs
            )
        )

        attrs = self._validate_periodo_publicacion(
            attrs
        )

        attrs = self._validate_origen(
            attrs
        )

        attrs = self._validate_autores(
            attrs
        )

        codigo = (
            self._instance_tipo_codigo()
        )

        if codigo == "ponencia":
            attrs = self._validate_ponencia(
                attrs
            )

        elif codigo in {
            "articulo_regional",
            "articulo_alto_impacto",
        }:
            attrs = self._validate_articulo(
                attrs
            )

            attrs["pais"] = None
            attrs["ciudad"] = None

        elif codigo == "libro":
            attrs = self._validate_libro(
                attrs
            )

            attrs["pais"] = None
            attrs["ciudad"] = None

        elif codigo == "capitulo_libro":
            attrs = self._validate_capitulo(
                attrs
            )

            attrs["pais"] = None
            attrs["ciudad"] = None

        else:
            raise ValidationError(
                {
                    "detail": [
                        "El tipo de publicación "
                        "no es compatible con la actualización."
                    ]
                }
            )

        return attrs

    # =========================================================
    # AUTORÍAS
    # =========================================================

    def _sincronizar_autores(
        self,
        *,
        publicacion,
        autores_data,
    ):
        """
        Sustituye las relaciones de autoría conservando únicamente
        el autor y su orden bibliográfico.
        """

        autores_data = autores_data or []

        if not autores_data:
            raise ValidationError(
                {
                    "autores": [
                        "La publicación debe mantener "
                        "al menos un autor."
                    ]
                }
            )

        autor_ids = [
            int(item["autor_id"])
            for item in autores_data
        ]

        autores_map = Autor.objects.in_bulk(
            autor_ids
        )

        if len(autores_map) != len(set(autor_ids)):
            raise ValidationError(
                {
                    "autores": [
                        "Uno o más autores "
                        "seleccionados no existen."
                    ]
                }
            )

        PublicacionAutor.objects.filter(
            publicacion=publicacion
        ).delete()

        for item in autores_data:
            autor_id = int(
                item["autor_id"]
            )

            PublicacionAutor.objects.create(
                publicacion=publicacion,
                autor=autores_map[autor_id],
                orden=int(item["orden"]),
            )

    # =========================================================
    # PDF
    # =========================================================

    def _quitar_pdf_actual(
        self,
        instance,
    ):
        """
        Elimina el PDF que actualmente utiliza
        la interfaz.

        1. PDF principal.
        2. Primer adjunto, si no existe principal.
        """

        if (
            instance.archivo_pdf
            and getattr(
                instance.archivo_pdf,
                "name",
                None,
            )
        ):
            # El propio save() del modelo se encargará
            # de eliminar físicamente el archivo antiguo.
            instance.archivo_pdf = None
            return

        adjunto = (
            PublicacionArchivo.objects
            .filter(
                publicacion=instance
            )
            .order_by(
                "orden",
                "id",
            )
            .first()
        )

        if adjunto:
            adjunto.delete()

    def _quitar_pdf_principal(
        self,
        instance,
    ):
        if (
            instance.archivo_pdf
            and getattr(
                instance.archivo_pdf,
                "name",
                None,
            )
        ):
            instance.archivo_pdf = None

    def _quitar_adjunto(
        self,
        instance,
        adjunto_id,
    ):
        if not adjunto_id:
            return

        try:
            adjunto = (
                PublicacionArchivo.objects
                .get(
                    id=adjunto_id,
                    publicacion=instance,
                )
            )

        except PublicacionArchivo.DoesNotExist:
            raise ValidationError(
                {
                    "quitar_archivo_adjunto_id": [
                        "El archivo adjunto indicado "
                        "no pertenece a esta publicación."
                    ]
                }
            )

        adjunto.delete()

    # =========================================================
    # UPDATE
    # =========================================================

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        codigo = (
            self._instance_tipo_codigo()
        )

        quitar_pdf_actual = _to_bool(
            validated_data.pop(
                "quitar_pdf_actual",
                False,
            )
        )

        quitar_archivo_pdf = _to_bool(
            validated_data.pop(
                "quitar_archivo_pdf",
                False,
            )
        )

        quitar_adjunto_id = (
            validated_data.pop(
                "quitar_archivo_adjunto_id",
                None,
            )
        )

        autores_data = (
            validated_data.pop(
                "autores",
                None,
            )
        )

        nuevo_pdf_presente = (
            "archivo_pdf"
            in validated_data
        )

        nuevo_pdf = (
            validated_data.pop(
                "archivo_pdf",
                None,
            )
            if nuevo_pdf_presente
            else None
        )

        # -----------------------------------------------------
        # Publicacion
        # -----------------------------------------------------

        base_fields = [
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "pais",
            "ciudad",
            "origen_tipo",
            "origen_grado",
            "anio_publicacion",
            "mes_publicacion",
        ]

        for field in base_fields:
            if field in validated_data:
                setattr(
                    instance,
                    field,
                    validated_data.pop(
                        field
                    ),
                )

        if codigo != "ponencia":
            instance.pais = None
            instance.ciudad = None

        if (
            instance.subarea
            and not instance.area
        ):
            instance.area = (
                instance.subarea.area
            )


        if quitar_pdf_actual:
            self._quitar_pdf_actual(
                instance
            )

        elif quitar_archivo_pdf:
            self._quitar_pdf_principal(
                instance
            )

        if quitar_adjunto_id:
            self._quitar_adjunto(
                instance,
                quitar_adjunto_id,
            )

        if nuevo_pdf_presente:
            instance.archivo_pdf = (
                nuevo_pdf
            )

        try:
            instance.save()

        except DjangoValidationError as exc:
            raise (
                _django_validation_to_drf(
                    exc
                )
            )

        # -----------------------------------------------------
        # Autores
        # -----------------------------------------------------

        if autores_data is not None:
            self._sincronizar_autores(
                publicacion=instance,
                autores_data=autores_data,
            )

        # -----------------------------------------------------
        # Ponencia
        # -----------------------------------------------------

        if codigo == "ponencia":
            try:
                ponencia = (
                    instance.ponencia
                )

            except Ponencia.DoesNotExist:
                raise ValidationError(
                    {
                        "detail": [
                            "No existe el detalle "
                            "de la ponencia asociada."
                        ]
                    }
                )

            fields = [
                "nombre_evento",
                "nombre_ponencia",
                "codigo_issn_isbn",
                "tipo_presentacion",
                "tipo_presentacion_otro",
                "link_evento",
                "revisor_par_arbitraje",
            ]

            for field in fields:
                if field in validated_data:
                    setattr(
                        ponencia,
                        field,
                        validated_data.pop(
                            field
                        ),
                    )

            try:
                ponencia.save()

            except DjangoValidationError as exc:
                raise (
                    _django_validation_to_drf(
                        exc
                    )
                )

        # -----------------------------------------------------
        # Artículo
        # -----------------------------------------------------

        elif codigo in {
            "articulo_regional",
            "articulo_alto_impacto",
        }:
            try:
                articulo = (
                    instance.articulo
                )

            except Articulo.DoesNotExist:
                raise ValidationError(
                    {
                        "detail": [
                            "No existe el detalle "
                            "del artículo asociado."
                        ]
                    }
                )

            fields = [
                "nombre_articulo",
                "base_datos_indexada",
                "base_datos_otra",
                "codigo_doi",
                "codigo_issn",
                "nombre_revista",
                "numero_revista",
                "link_publicacion",
                "link_revista",
                "factor_impacto",
                "cuartil",
                "sjr",
                "jcr",
            ]

            for field in fields:
                if field in validated_data:
                    setattr(
                        articulo,
                        field,
                        validated_data.pop(
                            field
                        ),
                    )

            try:
                articulo.save()

            except DjangoValidationError as exc:
                raise (
                    _django_validation_to_drf(
                        exc
                    )
                )

        # -----------------------------------------------------
        # Libro
        # -----------------------------------------------------

        elif codigo == "libro":
            try:
                libro = instance.libro

            except Libro.DoesNotExist:
                raise ValidationError(
                    {
                        "detail": [
                            "No existe el detalle "
                            "del libro asociado."
                        ]
                    }
                )

            fields = [
                "nombre_libro",
                "codigo_isbn",
                "editorial_compilador",
                "revisor_par_arbitraje",
                "link_libro",
            ]

            for field in fields:
                if field in validated_data:
                    setattr(
                        libro,
                        field,
                        validated_data.pop(
                            field
                        ),
                    )

            try:
                libro.save()

            except DjangoValidationError as exc:
                raise (
                    _django_validation_to_drf(
                        exc
                    )
                )

        # -----------------------------------------------------
        # Capítulo
        # -----------------------------------------------------

        elif codigo == "capitulo_libro":
            try:
                capitulo = (
                    instance.capitulo_libro
                )

            except CapituloLibro.DoesNotExist:
                raise ValidationError(
                    {
                        "detail": [
                            "No existe el detalle "
                            "del capítulo asociado."
                        ]
                    }
                )

            fields = [
                "nombre_capitulo",
                "nombre_libro",
                "codigo_isbn",
                "editor_compilador",
                "revisor_par_arbitraje",
                "link_capitulo",
            ]

            for field in fields:
                if field in validated_data:
                    setattr(
                        capitulo,
                        field,
                        validated_data.pop(
                            field
                        ),
                    )

            try:
                capitulo.save()

            except DjangoValidationError as exc:
                raise (
                    _django_validation_to_drf(
                        exc
                    )
                )

        return instance