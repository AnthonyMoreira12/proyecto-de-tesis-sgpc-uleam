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

MAX_PRIMARY_PDF_BYTES = 5 * 1024 * 1024  # 5 MB
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


class CapituloLibroRegistroSerializer(PublicacionCamposBaseMixin, serializers.ModelSerializer):
    facultad = serializers.PrimaryKeyRelatedField(queryset=Facultad.objects.all())
    carrera = serializers.PrimaryKeyRelatedField(queryset=Carrera.objects.all())

    proyecto = serializers.PrimaryKeyRelatedField(
        queryset=Proyecto.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            "does_not_exist": "El proyecto seleccionado no existe o no está disponible.",
            "incorrect_type": "Proyecto inválido.",
        },
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

    autores = AutorParticipacionSerializer(many=True, write_only=True, required=True)

    revisor_par_arbitraje = serializers.ChoiceField(
        choices=[c[0] for c in CapituloLibro.SI_NO],
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

    def _querydict_to_dict(self, data):
        if hasattr(data, "lists"):
            output = {}
            for key, values in data.lists():
                if len(values) == 0:
                    output[key] = ""
                elif len(values) == 1:
                    output[key] = values[0]
                else:
                    output[key] = values
            return output
        return dict(data)

    def to_internal_value(self, data):
        data = self._querydict_to_dict(data)

        autores = data.get("autores", None)

        if isinstance(autores, list) and len(autores) == 1:
            autores = autores[0]

        if autores in (None, "", "[]", "null", "None", [], {}):
            raise ValidationError({"autores": ["Debe registrar al menos un autor."]})

        if isinstance(autores, str):
            raw = autores.strip()

            if raw in ("", "[]", "null", "None"):
                raise ValidationError({"autores": ["Debe registrar al menos un autor."]})

            try:
                parsed = json.loads(raw)
            except Exception:
                raise ValidationError(
                    {"autores": ["Formato inválido. Debe ser JSON válido (lista)."]}
                )

            if parsed is None:
                parsed = []

            if not isinstance(parsed, list):
                raise ValidationError(
                    {"autores": ["Formato inválido. Debe ser una lista JSON."]}
                )

            data["autores"] = parsed

        return super().to_internal_value(data)

    def validate_archivo_pdf(self, value):
        return validate_primary_pdf_file(value)

    def validate(self, attrs):
        attrs = self._aplicar_reglas_origen(attrs)

        facultad = attrs.get("facultad")
        carrera = attrs.get("carrera")
        proyecto = attrs.get("proyecto")

        if carrera and facultad and getattr(carrera, "facultad_id", None) != getattr(facultad, "id", None):
            raise ValidationError(
                {"carrera": ["La carrera seleccionada no pertenece a la facultad indicada."]}
            )

        if proyecto and carrera and getattr(proyecto, "carrera_id", None) != getattr(carrera, "id", None):
            raise ValidationError(
                {"proyecto": ["El proyecto seleccionado no pertenece a la carrera indicada."]}
            )

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

        if "pais" in self.initial_data or "ciudad" in self.initial_data:
            raise ValidationError(
                {"detail": "País/Ciudad no aplican a Capítulos de Libro. Solo a Ponencias."}
            )

        required_fields = [
            "nombre_capitulo",
            "nombre_libro",
            "codigo_isbn",
            "editor_compilador",
            "revisor_par_arbitraje",
            "link_capitulo",
        ]

        for field in required_fields:
            value = attrs.get(field, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValidationError({field: ["Este campo es obligatorio."]})
            if isinstance(value, str):
                attrs[field] = value.strip()

        autores = attrs.get("autores") or []
        if not autores:
            raise ValidationError({"autores": ["Debe registrar al menos un autor."]})

        def _autor_id(item):
            value = item.get("autor")
            if value is None:
                return None
            return getattr(value, "id", value)

        autor_ids = [_autor_id(item) for item in autores if _autor_id(item) is not None]
        if len(autor_ids) != len(set(autor_ids)):
            raise ValidationError({"autores": ["No se permite repetir el mismo autor."]})

        ordenes = []
        for item in autores:
            orden = item.get("orden")
            if orden is None:
                raise ValidationError({"autores": ["Cada autor debe tener un 'orden'."]})

            try:
                ordenes.append(int(orden))
            except Exception:
                raise ValidationError({"autores": ["El 'orden' debe ser un número entero."]})

        if len(ordenes) != len(set(ordenes)):
            raise ValidationError({"autores": ["No se permite repetir el campo 'orden'."]})

        if 1 not in ordenes:
            raise ValidationError(
                {"autores": ["Debe existir un autor con orden = 1 (Autor Principal)."]}
            )

        autores_sorted = sorted(autores, key=lambda item: int(item["orden"]))
        for index, item in enumerate(autores_sorted, start=1):
            item["orden"] = index
            item["rol_autoria"] = "principal" if index == 1 else "coautor"

        attrs["autores"] = autores_sorted
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        autores_data = validated_data.pop("autores", [])

        usuario_creador, admin_registrador, registrado_por_admin = (
            resolve_publicacion_creation_context(self)
        )

        facultad = validated_data.pop("facultad")
        carrera = validated_data.pop("carrera")
        proyecto = validated_data.pop("proyecto", None)

        area = validated_data.pop("area", None)
        subarea = validated_data.pop("subarea", None)

        origen_tipo = validated_data.pop("origen_tipo", "ninguno")
        origen_grado = validated_data.pop("origen_grado", None)
        fecha_publicacion = validated_data.pop("fecha_publicacion", None)
        archivo_pdf = validated_data.pop("archivo_pdf", None)

        tipo = obtener_o_crear_tipo_publicacion(
            codigo="capitulo_libro",
            nombre="Capítulo de Libro",
            categoria="capitulo",
            orden=4,
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
            fecha_publicacion=fecha_publicacion,
            archivo_pdf=archivo_pdf,
            registrado_por_admin=registrado_por_admin,
            admin_registrador=admin_registrador,
        )

        capitulo = CapituloLibro.objects.create(
            publicacion=publicacion,
            nombre_capitulo=validated_data["nombre_capitulo"],
            nombre_libro=validated_data["nombre_libro"],
            codigo_isbn=validated_data["codigo_isbn"],
            editor_compilador=validated_data["editor_compilador"],
            revisor_par_arbitraje=validated_data["revisor_par_arbitraje"],
            link_capitulo=validated_data["link_capitulo"],
        )

        registrar_autores_publicacion(
            publicacion=publicacion,
            autores_data=autores_data,
        )
        return capitulo