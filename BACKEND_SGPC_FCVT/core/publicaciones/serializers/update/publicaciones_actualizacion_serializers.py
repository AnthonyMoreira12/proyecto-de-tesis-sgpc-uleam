"""
Serializer para actualización de publicaciones y sus autores.
Permite modificar datos generales, datos específicos por tipo y sincronizar autorías.
Mantiene coherencia entre carrera/facultad, área/subárea, ubicación y campos obligatorios.
Incluye opción para quitar PDF principal o adjunto asociado.
"""

import json

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


def _to_str(value):
    return "" if value is None else str(value).strip()


def _to_lower(value):
    value = _to_str(value)
    return value.lower() if value else ""


def _none_if_blank(value):
    value = _to_str(value)
    return value or None


def _to_bool(value):
    """
    Normaliza booleanos enviados como JSON, FormData o texto.
    """
    if isinstance(value, bool):
        return value

    if value in (1, "1"):
        return True

    if value in (0, "0"):
        return False

    value = str(value or "").strip().lower()
    return value in ("true", "yes", "y", "on", "si", "sí")


def _delete_file_field(file_field):
    """
    Elimina físicamente el archivo del storage sin guardar aún el modelo.
    """
    try:
        if not file_field:
            return

        if not getattr(file_field, "name", None):
            return

        file_field.delete(save=False)
    except Exception:
        pass


class AutorActualizacionItemSerializer(serializers.Serializer):
    autor_id = serializers.IntegerField()
    orden = serializers.IntegerField(required=False)
    rol_autoria = serializers.ChoiceField(
        choices=["principal", "coautor"],
        required=False,
    )


class PublicacionActualizacionSerializer(serializers.Serializer):
    carrera = serializers.PrimaryKeyRelatedField(
        queryset=Carrera.objects.all(),
        required=False,
    )

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

    fecha_publicacion = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
    )

    origen_tipo = serializers.ChoiceField(
        choices=[c[0] for c in Publicacion._meta.get_field("origen_tipo").choices],
        required=False,
    )

    origen_grado = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    archivo_pdf = serializers.FileField(
        required=False,
        allow_null=True,
    )

    quitar_pdf_actual = serializers.BooleanField(
        required=False,
        default=False,
    )

    quitar_archivo_pdf = serializers.BooleanField(
        required=False,
        default=False,
    )

    quitar_archivo_adjunto_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    autores = AutorActualizacionItemSerializer(
        many=True,
        required=False,
    )

    TIPO_PRESENTACION_CHOICES = [
        ("magistral", "Conferencia magistral"),
        ("oral", "Conferencia oral"),
        ("poster", "Poster"),
        ("otro", "Otro"),
    ]

    tipo_presentacion = serializers.ChoiceField(
        choices=[c[0] for c in TIPO_PRESENTACION_CHOICES],
        required=False,
        allow_null=True,
    )

    tipo_presentacion_otro = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    nombre_evento = serializers.CharField(required=False, allow_blank=True)
    nombre_ponencia = serializers.CharField(required=False, allow_blank=True)
    codigo_issn_isbn = serializers.CharField(required=False, allow_blank=True)
    link_evento = serializers.CharField(required=False, allow_blank=True)

    nombre_articulo = serializers.CharField(required=False, allow_blank=True)

    base_datos_indexada = serializers.ChoiceField(
        choices=[c[0] for c in Articulo.BASES_DATOS],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    base_datos_otra = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    codigo_doi = serializers.CharField(required=False, allow_blank=True)
    codigo_issn = serializers.CharField(required=False, allow_blank=True)
    nombre_revista = serializers.CharField(required=False, allow_blank=True)

    numero_revista = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    link_publicacion = serializers.CharField(required=False, allow_blank=True)
    link_revista = serializers.CharField(required=False, allow_blank=True)

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

    sjr = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    revisor_par_arbitraje = serializers.ChoiceField(
        choices=[c[0] for c in Libro.SI_NO],
        required=False,
    )

    nombre_libro = serializers.CharField(required=False, allow_blank=True)
    codigo_isbn = serializers.CharField(required=False, allow_blank=True)
    editorial_compilador = serializers.CharField(required=False, allow_blank=True)
    link_libro = serializers.CharField(required=False, allow_blank=True)

    nombre_capitulo = serializers.CharField(required=False, allow_blank=True)
    editor_compilador = serializers.CharField(required=False, allow_blank=True)
    link_capitulo = serializers.CharField(required=False, allow_blank=True)

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

    def _instance_tipo_codigo(self):
        instance = self.instance

        if not instance:
            return ""

        return _to_lower(getattr(instance.tipo, "codigo", ""))

    def _articulos_codes(self):
        return {
            "articulo",
            "articulo_regional",
            "articulo_alto_impacto",
        }

    def _capitulos_codes(self):
        return {
            "capitulo_libro",
            "capitulo",
        }

    def _normalize_autores_input(self, data):
        """
        Normaliza autores solo si el campo viene en la petición.

        Importante:
        En PATCH parcial, si no se envía 'autores', no debe tocarse la autoría.
        Esto evita que una acción simple como quitar PDF termine validando autores=[].
        """
        if "autores" not in data:
            return data

        autores = data.get("autores", None)

        if isinstance(autores, list) and len(autores) == 1:
            autores = autores[0]

        if autores in ("", "[]", "null", "None", [], {}):
            data["autores"] = []
            return data

        if autores is None:
            return data

        if isinstance(autores, str):
            raw = autores.strip()

            if raw in ("", "[]", "null", "None"):
                data["autores"] = []
                return data

            try:
                parsed = json.loads(raw)
            except Exception:
                raise ValidationError(
                    {
                        "autores": [
                            "Formato inválido. Debe ser JSON válido (lista)."
                        ]
                    }
                )

            if parsed is None:
                parsed = []

            if not isinstance(parsed, list):
                raise ValidationError(
                    {
                        "autores": [
                            "Formato inválido. Debe ser JSON válido (lista)."
                        ]
                    }
                )

            data["autores"] = parsed

        return data

    def _normalize_string_fields(self, attrs):
        string_fields = [
            "origen_grado",
            "nombre_evento",
            "nombre_ponencia",
            "codigo_issn_isbn",
            "link_evento",
            "tipo_presentacion_otro",
            "nombre_articulo",
            "base_datos_otra",
            "codigo_doi",
            "codigo_issn",
            "nombre_revista",
            "link_publicacion",
            "link_revista",
            "sjr",
            "nombre_libro",
            "codigo_isbn",
            "editorial_compilador",
            "link_libro",
            "nombre_capitulo",
            "editor_compilador",
            "link_capitulo",
        ]

        for field in string_fields:
            if field in attrs and attrs[field] is not None:
                attrs[field] = _to_str(attrs[field])

        return attrs

    def _validate_relaciones_generales(self, attrs):
        instance = self.instance

        final_carrera = attrs.get(
            "carrera",
            getattr(instance, "carrera", None),
        )

        final_proyecto = attrs.get(
            "proyecto",
            getattr(instance, "proyecto", None),
        )

        if final_proyecto and final_carrera:
            if getattr(final_proyecto, "carrera_id", None) != getattr(final_carrera, "id", None):
                raise ValidationError(
                    {
                        "proyecto": [
                            "El proyecto seleccionado no pertenece a la carrera indicada."
                        ]
                    }
                )

        return attrs

    def _validate_pdf_actions(self, attrs):
        quitar_pdf_actual = _to_bool(attrs.get("quitar_pdf_actual", False))
        quitar_archivo_pdf = _to_bool(attrs.get("quitar_archivo_pdf", False))
        quitar_archivo_adjunto_id = attrs.get("quitar_archivo_adjunto_id", None)

        sube_pdf = "archivo_pdf" in attrs and attrs.get("archivo_pdf") is not None

        if sube_pdf and (
            quitar_pdf_actual
            or quitar_archivo_pdf
            or quitar_archivo_adjunto_id
        ):
            raise ValidationError(
                {
                    "archivo_pdf": [
                        "No puedes subir un PDF nuevo y quitar un PDF en la misma solicitud."
                    ]
                }
            )

        attrs["quitar_pdf_actual"] = quitar_pdf_actual
        attrs["quitar_archivo_pdf"] = quitar_archivo_pdf

        return attrs

    def _validate_origen(self, attrs):
        instance = self.instance

        if "origen_tipo" in attrs or "origen_grado" in attrs:
            origen_tipo = attrs.get(
                "origen_tipo",
                getattr(instance, "origen_tipo", "ninguno") if instance else "ninguno",
            )
            origen_tipo = _to_lower(origen_tipo) or "ninguno"

            origen_grado = attrs.get(
                "origen_grado",
                getattr(instance, "origen_grado", None) if instance else None,
            )
            origen_grado = _none_if_blank(origen_grado)

            attrs["origen_tipo"] = origen_tipo

            if origen_tipo == "tic":
                if not origen_grado:
                    raise ValidationError(
                        {
                            "origen_grado": [
                                "Debe especificar el grado cuando el origen es TIC."
                            ]
                        }
                    )

                attrs["origen_grado"] = origen_grado
            else:
                attrs["origen_grado"] = None

        return attrs

    def _validate_area_subarea(self, attrs):
        instance = self.instance

        area = attrs.get("area", None)
        subarea = attrs.get("subarea", None)

        if subarea and not area:
            try:
                attrs["area"] = subarea.area
            except Exception:
                pass

        final_area = attrs.get("area", getattr(instance, "area", None))
        final_subarea = attrs.get("subarea", getattr(instance, "subarea", None))

        if final_subarea and not final_area:
            try:
                attrs["area"] = final_subarea.area
                final_area = final_subarea.area
            except Exception:
                pass

        if final_area and final_subarea:
            if getattr(final_subarea, "area_id", None) != getattr(final_area, "id", None):
                raise ValidationError(
                    {
                        "subarea": [
                            "La subárea seleccionada no pertenece al área indicada."
                        ]
                    }
                )

        return attrs

    def _validate_revisor(self, attrs):
        if "revisor_par_arbitraje" in attrs and attrs["revisor_par_arbitraje"] is not None:
            value = _to_lower(attrs["revisor_par_arbitraje"])

            if value not in ("si", "no"):
                raise ValidationError(
                    {
                        "revisor_par_arbitraje": [
                            "Debe seleccionar Sí o No."
                        ]
                    }
                )

            attrs["revisor_par_arbitraje"] = value

        return attrs

    def _validate_autores(self, attrs):
        if "autores" not in attrs:
            return attrs

        autores = attrs.get("autores") or []

        if not autores:
            raise ValidationError(
                {
                    "autores": [
                        "Debe registrar al menos un autor."
                    ]
                }
            )

        autor_ids = []

        for item in autores:
            autor_id = item.get("autor_id")

            if autor_id is None:
                raise ValidationError(
                    {
                        "autores": [
                            "Cada autor debe incluir 'autor_id'."
                        ]
                    }
                )

            try:
                autor_id = int(autor_id)
            except Exception:
                raise ValidationError(
                    {
                        "autores": [
                            "'autor_id' debe ser numérico."
                        ]
                    }
                )

            if autor_id <= 0:
                raise ValidationError(
                    {
                        "autores": [
                            "'autor_id' inválido."
                        ]
                    }
                )

            autor_ids.append(autor_id)

        if len(autor_ids) != len(set(autor_ids)):
            raise ValidationError(
                {
                    "autores": [
                        "No se permite repetir el mismo autor."
                    ]
                }
            )

        autores_map = Autor.objects.in_bulk(autor_ids)
        faltantes = [
            autor_id for autor_id in autor_ids
            if autor_id not in autores_map
        ]

        if faltantes:
            raise ValidationError(
                {
                    "autores": [
                        f"Autor(es) no existe(n): {', '.join(map(str, faltantes))}."
                    ]
                }
            )

        normalized = []

        for index, item in enumerate(autores, start=1):
            normalized.append(
                {
                    "autor_id": int(item["autor_id"]),
                    "orden": index,
                    "rol_autoria": "principal" if index == 1 else "coautor",
                }
            )

        attrs["autores"] = normalized

        return attrs

    def _validate_required_if_present(self, attrs, field_names):
        for field in field_names:
            if field in attrs:
                value = attrs.get(field)

                if value is None or (isinstance(value, str) and not value.strip()):
                    raise ValidationError(
                        {
                            field: [
                                "Este campo es obligatorio."
                            ]
                        }
                    )

        return attrs

    def _validate_fecha_if_present(self, attrs):
        if "fecha_publicacion" in attrs and not attrs.get("fecha_publicacion"):
            raise ValidationError(
                {
                    "fecha_publicacion": [
                        "Este campo es obligatorio."
                    ]
                }
            )

        return attrs

    def _validate_ponencia(self, attrs):
        instance = self.instance

        final_pais = attrs.get("pais", getattr(instance, "pais", None))
        final_ciudad = attrs.get("ciudad", getattr(instance, "ciudad", None))

        if not final_pais:
            raise ValidationError(
                {
                    "pais": [
                        "Debe seleccionar un país (solo para ponencias)."
                    ]
                }
            )

        if not final_ciudad:
            raise ValidationError(
                {
                    "ciudad": [
                        "Debe seleccionar una ciudad (solo para ponencias)."
                    ]
                }
            )

        if getattr(final_ciudad, "pais_id", None) != getattr(final_pais, "id", None):
            raise ValidationError(
                {
                    "ciudad": [
                        "La ciudad seleccionada no pertenece al país indicado."
                    ]
                }
            )

        attrs = self._validate_required_if_present(
            attrs,
            [
                "nombre_evento",
                "nombre_ponencia",
            ],
        )

        attrs = self._validate_fecha_if_present(attrs)

        return attrs

    def _validate_articulo(self, attrs):
        instance = self.instance
        articulo = getattr(instance, "articulo", None)
        tipo_articulo = _to_lower(getattr(articulo, "tipo_articulo", None))

        attrs = self._validate_required_if_present(
            attrs,
            [
                "nombre_articulo",
                "codigo_issn",
                "nombre_revista",
            ],
        )

        attrs = self._validate_fecha_if_present(attrs)

        final_base = attrs.get(
            "base_datos_indexada",
            getattr(articulo, "base_datos_indexada", None) if articulo else None,
        )

        final_base_otra = attrs.get(
            "base_datos_otra",
            getattr(articulo, "base_datos_otra", None) if articulo else None,
        )

        final_factor = attrs.get(
            "factor_impacto",
            getattr(articulo, "factor_impacto", None) if articulo else None,
        )

        final_cuartil = attrs.get(
            "cuartil",
            getattr(articulo, "cuartil", None) if articulo else None,
        )

        final_sjr = attrs.get(
            "sjr",
            getattr(articulo, "sjr", None) if articulo else None,
        )

        final_base = _to_lower(final_base) or None
        final_base_otra = _none_if_blank(final_base_otra)
        final_factor = _to_lower(final_factor) or None
        final_cuartil = _to_lower(final_cuartil) or None
        final_sjr = _none_if_blank(final_sjr)

        if tipo_articulo == "regional":
            attrs["factor_impacto"] = None
            attrs["cuartil"] = None
            attrs["sjr"] = None

            if not final_base:
                raise ValidationError(
                    {
                        "base_datos_indexada": [
                            "Debe seleccionar una base de datos / indexación."
                        ]
                    }
                )

            valid_bases = {choice[0] for choice in Articulo.BASES_DATOS}

            if final_base not in valid_bases:
                raise ValidationError(
                    {
                        "base_datos_indexada": [
                            "Opción inválida de base de datos / indexación."
                        ]
                    }
                )

            attrs["base_datos_indexada"] = final_base

            if final_base == "otra":
                if not final_base_otra:
                    raise ValidationError(
                        {
                            "base_datos_otra": [
                                "Debe especificar la base de datos cuando seleccione 'Otra'."
                            ]
                        }
                    )

                attrs["base_datos_otra"] = final_base_otra
            else:
                attrs["base_datos_otra"] = None

        else:
            attrs["base_datos_indexada"] = None
            attrs["base_datos_otra"] = None

            valid_factor = {choice[0] for choice in Articulo.FACTOR_IMPACTO}
            valid_cuartil = {choice[0] for choice in Articulo.CUARTIL}

            if final_factor and final_factor not in valid_factor:
                raise ValidationError(
                    {
                        "factor_impacto": [
                            "Factor de impacto inválido."
                        ]
                    }
                )

            if final_cuartil and final_cuartil not in valid_cuartil:
                raise ValidationError(
                    {
                        "cuartil": [
                            "Cuartil inválido."
                        ]
                    }
                )

            attrs["factor_impacto"] = final_factor
            attrs["cuartil"] = final_cuartil
            attrs["sjr"] = final_sjr

            if final_factor == "sjr" and not final_sjr:
                raise ValidationError(
                    {
                        "sjr": [
                            "Debe ingresar el valor SJR cuando el factor de impacto es SJR."
                        ]
                    }
                )

        return attrs

    def _validate_libro(self, attrs):
        attrs = self._validate_required_if_present(
            attrs,
            [
                "nombre_libro",
                "codigo_isbn",
                "editorial_compilador",
                "revisor_par_arbitraje",
                "link_libro",
            ],
        )

        attrs = self._validate_fecha_if_present(attrs)

        return attrs

    def _validate_capitulo(self, attrs):
        attrs = self._validate_required_if_present(
            attrs,
            [
                "nombre_capitulo",
                "nombre_libro",
                "codigo_isbn",
                "editor_compilador",
                "revisor_par_arbitraje",
                "link_capitulo",
            ],
        )

        attrs = self._validate_fecha_if_present(attrs)

        return attrs

    def to_internal_value(self, data):
        data = self._querydict_to_dict(data)
        data = self._normalize_autores_input(data)
        return super().to_internal_value(data)

    def validate(self, attrs):
        attrs = self._normalize_string_fields(attrs)
        attrs = self._validate_pdf_actions(attrs)
        attrs = self._validate_relaciones_generales(attrs)
        attrs = self._validate_origen(attrs)
        attrs = self._validate_area_subarea(attrs)
        attrs = self._validate_revisor(attrs)
        attrs = self._validate_autores(attrs)

        codigo = self._instance_tipo_codigo()
        articulos_codes = self._articulos_codes()
        capitulos_codes = self._capitulos_codes()

        if codigo == "ponencia":
            attrs = self._validate_ponencia(attrs)

        elif codigo in articulos_codes:
            attrs = self._validate_articulo(attrs)

            if "pais" in attrs or "ciudad" in attrs:
                attrs["pais"] = None
                attrs["ciudad"] = None

        elif codigo == "libro":
            attrs = self._validate_libro(attrs)

            if "pais" in attrs or "ciudad" in attrs:
                attrs["pais"] = None
                attrs["ciudad"] = None

        elif codigo in capitulos_codes:
            attrs = self._validate_capitulo(attrs)

            if "pais" in attrs or "ciudad" in attrs:
                attrs["pais"] = None
                attrs["ciudad"] = None

        return attrs

    def _sincronizar_autores(self, *, publicacion: Publicacion, autores_data: list):
        autores_data = autores_data or []
        autor_ids = [int(item["autor_id"]) for item in autores_data]
        autores_map = Autor.objects.in_bulk(autor_ids)

        PublicacionAutor.objects.filter(publicacion=publicacion).delete()

        rels = []

        for item in autores_data:
            autor_id = int(item["autor_id"])
            autor_obj = autores_map.get(autor_id)

            if not autor_obj:
                raise ValidationError(
                    {
                        "autores": [
                            f"Autor no existe: {autor_id}"
                        ]
                    }
                )

            rels.append(
                PublicacionAutor(
                    publicacion=publicacion,
                    autor=autor_obj,
                    rol_autoria=item.get("rol_autoria")
                    or (
                        "principal"
                        if int(item.get("orden") or 0) == 1
                        else "coautor"
                    ),
                    orden=int(item["orden"]),
                )
            )

        if rels:
            PublicacionAutor.objects.bulk_create(rels)

    def _quitar_pdf_actual(self, instance: Publicacion):
        """
        Quita el PDF que actualmente ve el frontend:
        1. Si existe archivo_pdf principal, elimina ese.
        2. Si no existe archivo_pdf principal, elimina el primer adjunto.
        """
        if instance.archivo_pdf:
            _delete_file_field(instance.archivo_pdf)
            instance.archivo_pdf = None
            return

        adjunto_actual = (
            PublicacionArchivo.objects
            .filter(publicacion=instance)
            .order_by("orden", "id")
            .first()
        )

        if adjunto_actual:
            adjunto_actual.delete()

    def _quitar_pdf_principal(self, instance: Publicacion):
        """
        Quita únicamente Publicacion.archivo_pdf.
        No toca adjuntos.
        """
        if instance.archivo_pdf:
            _delete_file_field(instance.archivo_pdf)
            instance.archivo_pdf = None

    def _quitar_adjunto(self, instance: Publicacion, adjunto_id):
        """
        Quita un adjunto específico de PublicacionArchivo.
        """
        if not adjunto_id:
            return

        adjunto = (
            PublicacionArchivo.objects
            .filter(
                id=adjunto_id,
                publicacion=instance,
            )
            .first()
        )

        if not adjunto:
            raise ValidationError(
                {
                    "quitar_archivo_adjunto_id": [
                        "El archivo adjunto indicado no existe para esta publicación."
                    ]
                }
            )

        adjunto.delete()

    @transaction.atomic
    def update(self, instance: Publicacion, validated_data):
        codigo = self._instance_tipo_codigo()
        articulos_codes = self._articulos_codes()
        capitulos_codes = self._capitulos_codes()

        quitar_pdf_actual = _to_bool(
            validated_data.pop("quitar_pdf_actual", False)
        )

        quitar_archivo_pdf = _to_bool(
            validated_data.pop("quitar_archivo_pdf", False)
        )

        quitar_archivo_adjunto_id = validated_data.pop(
            "quitar_archivo_adjunto_id",
            None,
        )

        fecha_changed = False

        for field in [
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "origen_tipo",
            "origen_grado",
            "fecha_publicacion",
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

                if field == "fecha_publicacion":
                    fecha_changed = True

        if codigo == "ponencia":
            if "pais" in validated_data:
                instance.pais = validated_data["pais"]

            if "ciudad" in validated_data:
                instance.ciudad = validated_data["ciudad"]

            if instance.ciudad and not instance.pais:
                raise ValidationError(
                    {
                        "pais": [
                            "Debe seleccionar país si selecciona ciudad."
                        ]
                    }
                )

            if instance.pais and instance.ciudad:
                if getattr(instance.ciudad, "pais_id", None) != getattr(instance.pais, "id", None):
                    raise ValidationError(
                        {
                            "ciudad": [
                                "La ciudad seleccionada no pertenece al país indicado."
                            ]
                        }
                    )
        else:
            instance.pais = None
            instance.ciudad = None

        if instance.subarea and not instance.area:
            try:
                instance.area = instance.subarea.area
            except Exception:
                pass

        if instance.subarea and instance.area:
            if getattr(instance.subarea, "area_id", None) != getattr(instance.area, "id", None):
                raise ValidationError(
                    {
                        "subarea": [
                            "La subárea seleccionada no pertenece al área indicada."
                        ]
                    }
                )

        origen_tipo = _to_lower(instance.origen_tipo) or "ninguno"
        instance.origen_tipo = origen_tipo

        if origen_tipo != "tic":
            instance.origen_grado = None
        else:
            if not _to_str(instance.origen_grado):
                raise ValidationError(
                    {
                        "origen_grado": [
                            "Debe especificar el grado cuando el origen es TIC."
                        ]
                    }
                )

            instance.origen_grado = _to_str(instance.origen_grado)

        if fecha_changed:
            fecha = instance.fecha_publicacion
            instance.anio_publicacion = fecha.year if fecha else None

        if quitar_pdf_actual:
            self._quitar_pdf_actual(instance)

        elif quitar_archivo_pdf:
            self._quitar_pdf_principal(instance)

        if quitar_archivo_adjunto_id:
            self._quitar_adjunto(instance, quitar_archivo_adjunto_id)

        if "archivo_pdf" in validated_data:
            instance.archivo_pdf = validated_data["archivo_pdf"]

        instance.save()

        if "autores" in validated_data:
            self._sincronizar_autores(
                publicacion=instance,
                autores_data=validated_data.get("autores") or [],
            )

        if codigo == "ponencia":
            ponencia, _ = Ponencia.objects.get_or_create(publicacion=instance)

            for field in [
                "nombre_evento",
                "nombre_ponencia",
                "codigo_issn_isbn",
                "tipo_presentacion",
                "tipo_presentacion_otro",
                "link_evento",
            ]:
                if field in validated_data:
                    setattr(ponencia, field, validated_data[field])

            ponencia.save()

        elif codigo in articulos_codes:
            articulo, _ = Articulo.objects.get_or_create(publicacion=instance)

            for field in [
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
            ]:
                if field in validated_data:
                    setattr(articulo, field, validated_data[field])

            tipo_articulo = _to_lower(articulo.tipo_articulo)

            if tipo_articulo == "regional":
                articulo.factor_impacto = None
                articulo.cuartil = None
                articulo.sjr = None

                base_datos = _to_lower(articulo.base_datos_indexada)

                if not base_datos:
                    raise ValidationError(
                        {
                            "base_datos_indexada": [
                                "Debe seleccionar una base de datos / indexación."
                            ]
                        }
                    )

                if base_datos == "otra":
                    if not _to_str(articulo.base_datos_otra):
                        raise ValidationError(
                            {
                                "base_datos_otra": [
                                    "Debe especificar la base de datos cuando seleccione 'Otra'."
                                ]
                            }
                        )

                    articulo.base_datos_otra = _to_str(articulo.base_datos_otra)
                else:
                    articulo.base_datos_otra = None

            else:
                articulo.base_datos_indexada = None
                articulo.base_datos_otra = None

                articulo.factor_impacto = _to_lower(articulo.factor_impacto) or None
                articulo.cuartil = _to_lower(articulo.cuartil) or None
                articulo.sjr = _none_if_blank(articulo.sjr)

                if articulo.factor_impacto == "sjr" and not _to_str(articulo.sjr):
                    raise ValidationError(
                        {
                            "sjr": [
                                "Debe ingresar el valor SJR cuando el factor de impacto es SJR."
                            ]
                        }
                    )

            articulo.save()

        elif codigo == "libro":
            libro, _ = Libro.objects.get_or_create(publicacion=instance)

            for field in [
                "nombre_libro",
                "codigo_isbn",
                "editorial_compilador",
                "revisor_par_arbitraje",
                "link_libro",
            ]:
                if field in validated_data:
                    setattr(libro, field, validated_data[field])

            libro.save()

        elif codigo in capitulos_codes:
            capitulo, _ = CapituloLibro.objects.get_or_create(publicacion=instance)

            for field in [
                "nombre_capitulo",
                "nombre_libro",
                "codigo_isbn",
                "editor_compilador",
                "revisor_par_arbitraje",
                "link_capitulo",
            ]:
                if field in validated_data:
                    setattr(capitulo, field, validated_data[field])

            capitulo.save()

        return instance