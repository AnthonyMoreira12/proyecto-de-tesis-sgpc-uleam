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
    Subarea,
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
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_PDF_CONTENT_TYPES = {"application/pdf"}


def validate_primary_pdf_file(value):
    if not value:
        return value

    file_name = str(getattr(value, "name", "") or "").lower()
    ext = os.path.splitext(file_name)[1]

    if ext not in ALLOWED_PDF_EXTENSIONS:
        raise ValidationError(
            {"archivo_pdf": ["Solo se permiten archivos PDF."]}
        )

    content_type = (
        getattr(value, "content_type", None)
        or getattr(getattr(value, "file", None), "content_type", None)
    )

    if content_type and content_type not in ALLOWED_PDF_CONTENT_TYPES:
        raise ValidationError(
            {"archivo_pdf": ["Solo se permiten archivos PDF."]}
        )

    file_size = int(getattr(value, "size", 0) or 0)

    if file_size > MAX_PRIMARY_PDF_BYTES:
        raise ValidationError(
            {"archivo_pdf": ["El PDF principal supera el tamaño máximo de 5 MB."]}
        )

    return value


class PonenciaRegistroSerializer(PublicacionCamposBaseMixin, serializers.ModelSerializer):
    TIPO_PRESENTACION_CHOICES = [
        ("magistral", "Conferencia magistral"),
        ("oral", "Conferencia oral"),
        ("poster", "Poster"),
        ("otro", "Otro"),
    ]

    autores = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
    )

    carrera = serializers.PrimaryKeyRelatedField(queryset=Carrera.objects.all())

    proyecto = serializers.PrimaryKeyRelatedField(
        queryset=Proyecto.objects.all(),
        required=False,
        allow_null=True,
    )

    area = serializers.PrimaryKeyRelatedField(
        queryset=AreaConocimiento.objects.all(),
        required=False,
        allow_null=True,
    )

    subarea = serializers.PrimaryKeyRelatedField(
        queryset=Subarea.objects.all(),
        required=False,
        allow_null=True,
    )

    pais = serializers.PrimaryKeyRelatedField(
        queryset=Pais.objects.all(),
        required=False,
        allow_null=True,
    )

    ciudad = serializers.PrimaryKeyRelatedField(
        queryset=Ciudad.objects.all(),
        required=False,
        allow_null=True,
    )

    tipo_presentacion = serializers.ChoiceField(
        choices=[choice[0] for choice in TIPO_PRESENTACION_CHOICES],
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

    class Meta:
        model = Ponencia
        fields = [
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "pais",
            "ciudad",
            "origen_tipo",
            "origen_grado",
            "fecha_publicacion",
            "archivo_pdf",
            "nombre_evento",
            "nombre_ponencia",
            "codigo_issn_isbn",
            "tipo_presentacion",
            "tipo_presentacion_otro",
            "link_evento",
            "autores",
        ]

    def to_internal_value(self, data):
        if hasattr(data, "dict"):
            base = data.dict()
            base["autores"] = data.get("autores", None)
            data = base
        else:
            data = dict(data)

        autores = data.get("autores", None)

        if isinstance(autores, list):
            if len(autores) == 1 and isinstance(autores[0], str):
                raw = (autores[0] or "").strip()

                if raw in ("", "[]", "null", "None"):
                    data["autores"] = []
                else:
                    try:
                        data["autores"] = json.loads(raw)
                    except Exception:
                        raise ValidationError(
                            {"autores": ["Formato inválido. Debe ser JSON válido (lista)."]}
                        )

            elif len(autores) == 1 and isinstance(autores[0], list):
                data["autores"] = autores[0]
            else:
                data["autores"] = autores

        elif isinstance(autores, str):
            raw = autores.strip()

            if raw in ("", "[]", "null", "None"):
                data["autores"] = []
            else:
                try:
                    data["autores"] = json.loads(raw)
                except Exception:
                    raise ValidationError(
                        {"autores": ["Formato inválido. Debe ser JSON válido (lista)."]}
                    )

        elif autores is None:
            data["autores"] = []
        else:
            data["autores"] = autores

        if (
            isinstance(data.get("autores"), list)
            and len(data["autores"]) == 1
            and isinstance(data["autores"][0], list)
        ):
            data["autores"] = data["autores"][0]

        return super().to_internal_value(data)

    def validate_archivo_pdf(self, value):
        return validate_primary_pdf_file(value)

    def validate(self, attrs):
        carrera = attrs.get("carrera")
        proyecto = attrs.get("proyecto")

        if proyecto and carrera and getattr(proyecto, "carrera_id", None) != getattr(carrera, "id", None):
            raise ValidationError(
                {"proyecto": ["El proyecto seleccionado no pertenece a la carrera indicada."]}
            )

        pais = attrs.get("pais")
        ciudad = attrs.get("ciudad")

        if not pais:
            raise ValidationError(
                {"pais": ["Debe seleccionar un país (solo para ponencias)."]}
            )

        if not ciudad:
            raise ValidationError(
                {"ciudad": ["Debe seleccionar una ciudad (solo para ponencias)."]}
            )

        if getattr(ciudad, "pais_id", None) != getattr(pais, "id", None):
            raise ValidationError(
                {"ciudad": ["La ciudad seleccionada no pertenece al país indicado."]}
            )

        tipo_presentacion = attrs.get("tipo_presentacion")
        tipo_presentacion_otro = attrs.get("tipo_presentacion_otro")

        if isinstance(tipo_presentacion, str):
            tipo_presentacion = tipo_presentacion.strip().lower() or None

        if tipo_presentacion_otro is not None:
            tipo_presentacion_otro = str(tipo_presentacion_otro).strip() or None

        attrs["tipo_presentacion"] = tipo_presentacion
        attrs["tipo_presentacion_otro"] = tipo_presentacion_otro

        if tipo_presentacion == "otro":
            if not tipo_presentacion_otro:
                raise ValidationError(
                    {
                        "tipo_presentacion_otro": [
                            "Debe escribir el tipo de presentación cuando seleccione 'Otro'."
                        ]
                    }
                )
        else:
            attrs["tipo_presentacion_otro"] = None

        attrs = self._aplicar_reglas_origen(attrs)

        area = attrs.get("area")
        subarea = attrs.get("subarea")

        if subarea and not area:
            try:
                attrs["area"] = subarea.area
            except Exception:
                pass

        if attrs.get("area") and attrs.get("subarea"):
            if getattr(attrs["subarea"], "area_id", None) != getattr(attrs["area"], "id", None):
                raise ValidationError(
                    {"subarea": ["La subárea seleccionada no pertenece al área indicada."]}
                )

        autores = attrs.get("autores") or []

        if not autores:
            raise ValidationError({"autores": ["Debe registrar al menos un autor."]})

        autor_ids = []
        ordenes = []

        for item in autores:
            if not isinstance(item, dict):
                raise ValidationError(
                    {"autores": ["Cada autor debe ser un objeto JSON."]}
                )

            autor_id = item.get("autor_id") or item.get("autor")

            if autor_id is None:
                raise ValidationError(
                    {"autores": ["Cada autor debe incluir 'autor_id'."]}
                )

            try:
                autor_id = int(autor_id)
            except Exception:
                raise ValidationError({"autores": ["'autor_id' debe ser numérico."]})

            autor_ids.append(autor_id)

            orden = item.get("orden")

            if orden is None:
                raise ValidationError({"autores": ["Cada autor debe tener un 'orden'."]})

            try:
                orden = int(orden)
            except Exception:
                raise ValidationError({"autores": ["El 'orden' debe ser un número entero."]})

            ordenes.append(orden)

        if len(autor_ids) != len(set(autor_ids)):
            raise ValidationError({"autores": ["No se permite repetir el mismo autor."]})

        if len(ordenes) != len(set(ordenes)):
            raise ValidationError({"autores": ["No se permite repetir el campo 'orden'."]})

        if 1 not in ordenes:
            raise ValidationError(
                {"autores": ["Debe existir un autor con orden = 1 (Autor Principal)."]}
            )

        autores_sorted = sorted(
            autores,
            key=lambda item: int(item.get("orden", 999999) or 999999),
        )

        normalized = []

        for index, item in enumerate(autores_sorted, start=1):
            autor_id = int(item.get("autor_id") or item.get("autor"))

            normalized.append(
                {
                    "autor_id": autor_id,
                    "orden": index,
                    "rol_autoria": "principal" if index == 1 else "coautor",
                }
            )

        attrs["autores"] = normalized

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        autores_data = validated_data.pop("autores", [])

        usuario_creador, admin_registrador, registrado_por_admin = (
            resolve_publicacion_creation_context(self)
        )

        carrera = validated_data.pop("carrera")
        proyecto = validated_data.pop("proyecto", None)

        area = validated_data.pop("area", None)
        subarea = validated_data.pop("subarea", None)
        pais = validated_data.pop("pais", None)
        ciudad = validated_data.pop("ciudad", None)

        origen_tipo = validated_data.pop("origen_tipo", "ninguno")
        origen_grado = validated_data.pop("origen_grado", None)
        fecha_publicacion = validated_data.pop("fecha_publicacion", None)
        archivo_pdf = validated_data.pop("archivo_pdf", None)

        facultad = carrera.facultad

        tipo = obtener_o_crear_tipo_publicacion(
            codigo="ponencia",
            nombre="Ponencia",
            categoria="ponencia",
            orden=1,
        )

        publicacion = crear_publicacion_base(
            proyecto=proyecto,
            tipo=tipo,
            usuario=usuario_creador,
            facultad=facultad,
            carrera=carrera,
            area=area,
            subarea=subarea,
            pais=pais,
            ciudad=ciudad,
            origen_tipo=origen_tipo,
            origen_grado=origen_grado,
            fecha_publicacion=fecha_publicacion,
            archivo_pdf=archivo_pdf,
            registrado_por_admin=registrado_por_admin,
            admin_registrador=admin_registrador,
        )

        ponencia = Ponencia.objects.create(
            publicacion=publicacion,
            nombre_evento=validated_data["nombre_evento"],
            nombre_ponencia=validated_data["nombre_ponencia"],
            codigo_issn_isbn=validated_data.get("codigo_issn_isbn"),
            tipo_presentacion=validated_data.get("tipo_presentacion"),
            tipo_presentacion_otro=validated_data.get("tipo_presentacion_otro"),
            link_evento=validated_data.get("link_evento"),
        )

        registrar_autores_publicacion(
            publicacion=publicacion,
            autores_data=autores_data,
        )

        return ponencia