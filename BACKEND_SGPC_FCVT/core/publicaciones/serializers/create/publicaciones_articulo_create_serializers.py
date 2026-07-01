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
ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_PDF_CONTENT_TYPES = {"application/pdf"}


def _to_str(value):
    return "" if value is None else str(value).strip()


def _to_lower(value):
    value = _to_str(value)
    return value.lower() if value else ""


def _none_if_blank(value):
    value = _to_str(value)
    return value or None


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


class ArticuloRegistroSerializer(PublicacionCamposBaseMixin, serializers.ModelSerializer):
    autores = AutorParticipacionSerializer(many=True, write_only=True, required=True)
    tipo_codigo = serializers.CharField(write_only=True, required=True)

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

    fecha_publicacion = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
    )

    numero_revista = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    factor_impacto = serializers.ChoiceField(
        choices=[c[0] for c in Articulo.FACTOR_IMPACTO],
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    cuartil = serializers.ChoiceField(
        choices=[c[0] for c in Articulo.CUARTIL],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    base_datos_indexada = serializers.ChoiceField(
        choices=[c[0] for c in Articulo.BASES_DATOS],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = Articulo
        fields = [
            "tipo_codigo",
            "facultad",
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "origen_tipo",
            "origen_grado",
            "fecha_publicacion",
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
        extra_kwargs = {
            "tipo_articulo": {"required": False},
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
        data = data.copy() if hasattr(data, "copy") else dict(data)
        autores = data.get("autores", None)

        if isinstance(autores, list) and len(autores) == 1 and isinstance(autores[0], list):
            autores = autores[0]

        if isinstance(autores, list) and len(autores) == 1 and isinstance(autores[0], str):
            autores = autores[0]

        if autores in (None, "", "[]", "null", "None", []):
            data["autores"] = []
            return super().to_internal_value(data)

        if isinstance(autores, str):
            raw = autores.strip()

            if raw in ("", "[]", "null", "None"):
                data["autores"] = []
                return super().to_internal_value(data)

            try:
                data["autores"] = json.loads(raw)
            except Exception:
                raise ValidationError(
                    {"autores": ["Formato inválido. Debe ser JSON válido."]}
                )

            return super().to_internal_value(data)

        data["autores"] = autores
        return super().to_internal_value(data)

    def validate_archivo_pdf(self, value):
        return validate_primary_pdf_file(value)

    def _validate_autores(self, attrs):
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

    def _normalize_text_fields(self, attrs):
        for field in (
            "codigo_doi",
            "codigo_issn",
            "nombre_revista",
            "nombre_articulo",
            "base_datos_otra",
            "link_revista",
            "link_publicacion",
            "sjr",
        ):
            if field in attrs:
                attrs[field] = _none_if_blank(attrs.get(field))

        return attrs

    def _validate_required_article_fields(self, attrs):
        for field in ("codigo_issn", "nombre_revista", "nombre_articulo"):
            if not _to_str(attrs.get(field)):
                raise ValidationError({field: ["Este campo es obligatorio."]})
        return attrs

    def _validate_regional(self, attrs):
        base_datos = _to_lower(attrs.get("base_datos_indexada"))

        attrs["factor_impacto"] = None
        attrs["cuartil"] = None
        attrs["sjr"] = None

        if not base_datos:
            raise ValidationError(
                {
                    "base_datos_indexada": [
                        "Debe seleccionar una base de datos / indexación."
                    ]
                }
            )

        valid_bases = {choice[0] for choice in Articulo.BASES_DATOS}
        if base_datos not in valid_bases:
            raise ValidationError(
                {"base_datos_indexada": ["Opción inválida de base de datos / indexación."]}
            )

        attrs["base_datos_indexada"] = base_datos

        if base_datos == "otra":
            texto = _to_str(attrs.get("base_datos_otra"))
            if not texto:
                raise ValidationError(
                    {
                        "base_datos_otra": [
                            "Debe especificar la base de datos cuando seleccione 'Otra'."
                        ]
                    }
                )
            attrs["base_datos_otra"] = texto
        else:
            attrs["base_datos_otra"] = None

        return attrs

    def _validate_alto_impacto(self, attrs):
        factor = _to_lower(attrs.get("factor_impacto"))
        cuartil = _to_lower(attrs.get("cuartil"))
        sjr = _none_if_blank(attrs.get("sjr"))

        attrs["base_datos_indexada"] = None
        attrs["base_datos_otra"] = None

        attrs["factor_impacto"] = factor or None
        attrs["cuartil"] = cuartil or None
        attrs["sjr"] = sjr

        valid_factor = {choice[0] for choice in Articulo.FACTOR_IMPACTO}
        valid_cuartil = {choice[0] for choice in Articulo.CUARTIL}

        if factor and factor not in valid_factor:
            raise ValidationError({"factor_impacto": ["Factor de impacto inválido."]})

        if cuartil and cuartil not in valid_cuartil:
            raise ValidationError({"cuartil": ["Cuartil inválido."]})

        if factor == "sjr" and not sjr:
            raise ValidationError(
                {"sjr": ["Debe ingresar el valor SJR cuando el factor de impacto es SJR."]}
            )

        return attrs

    def validate(self, attrs):
        tipo_codigo = _to_lower(attrs.get("tipo_codigo"))

        if tipo_codigo not in ("articulo_regional", "articulo_alto_impacto"):
            raise ValidationError(
                {
                    "tipo_codigo": [
                        "Tipo inválido. Use 'articulo_regional' o 'articulo_alto_impacto'."
                    ]
                }
            )

        attrs["tipo_codigo"] = tipo_codigo
        attrs["tipo_articulo"] = (
            "regional" if tipo_codigo == "articulo_regional" else "alto_impacto"
        )

        if "pais" in self.initial_data or "ciudad" in self.initial_data:
            raise ValidationError(
                {"detail": "País/Ciudad no aplican a Artículos. Solo a Ponencias."}
            )

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

        attrs = self._validate_autores(attrs)
        attrs = self._normalize_text_fields(attrs)
        attrs = self._validate_required_article_fields(attrs)

        if attrs["tipo_articulo"] == "regional":
            attrs = self._validate_regional(attrs)
        else:
            attrs = self._validate_alto_impacto(attrs)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        autores_data = validated_data.pop("autores", [])
        usuario_creador, admin_registrador, registrado_por_admin = (
            resolve_publicacion_creation_context(self)
        )

        validated_data.pop("tipo_codigo", None)
        tipo_articulo = validated_data.pop("tipo_articulo")

        facultad = validated_data.pop("facultad")
        carrera = validated_data.pop("carrera")
        proyecto = validated_data.pop("proyecto", None)

        area = validated_data.pop("area", None)
        subarea = validated_data.pop("subarea", None)

        origen_tipo = validated_data.pop("origen_tipo", "ninguno")
        origen_grado = validated_data.pop("origen_grado", None)
        fecha_publicacion = validated_data.pop("fecha_publicacion", None)
        archivo_pdf = validated_data.pop("archivo_pdf", None)

        if tipo_articulo == "regional":
            tipo = obtener_o_crear_tipo_publicacion(
                codigo="articulo_regional",
                nombre="Artículo Regional",
                categoria="articulo",
                orden=2,
            )
        else:
            tipo = obtener_o_crear_tipo_publicacion(
                codigo="articulo_alto_impacto",
                nombre="Artículo de Alto Impacto",
                categoria="articulo",
                orden=2,
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