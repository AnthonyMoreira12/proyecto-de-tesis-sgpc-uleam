"""Actualización administrativa de publicaciones."""

import json

from django.db import transaction
from rest_framework import serializers

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
    PublicacionAutor,
    Subarea,
)
from core.utils.files import normalize_optional_text, validate_pdf_file


MAX_PRIMARY_PDF_BYTES = 5 * 1024 * 1024


class AutorActualizacionItemSerializer(serializers.Serializer):
    autor_id = serializers.IntegerField(min_value=1)
    orden = serializers.IntegerField(required=False, min_value=1)
    rol_autoria = serializers.ChoiceField(
        choices=["principal", "coautor"],
        required=False,
    )


class PublicacionActualizacionSerializer(serializers.Serializer):
    # Compatibilidad con el frontend. No se guarda en Publicacion.
    facultad = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True,
    )

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
        choices=[
            choice[0]
            for choice in Publicacion._meta.get_field(
                "origen_tipo"
            ).choices
        ],
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
    autores = AutorActualizacionItemSerializer(
        many=True,
        required=False,
    )

    # Ponencia
    tipo_presentacion = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    tipo_presentacion_otro = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    nombre_evento = serializers.CharField(required=False)
    nombre_ponencia = serializers.CharField(required=False)
    codigo_issn_isbn = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    link_evento = serializers.URLField(
        required=False,
        allow_blank=True,
    )

    # Artículo
    nombre_articulo = serializers.CharField(required=False)
    base_datos_indexada = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    base_datos_otra = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    codigo_doi = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    codigo_issn = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    nombre_revista = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    numero_revista = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    link_publicacion = serializers.URLField(
        required=False,
        allow_blank=True,
    )
    link_revista = serializers.URLField(
        required=False,
        allow_blank=True,
    )
    factor_impacto = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    cuartil = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    sjr = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    # Libro y capítulo
    revisor_par_arbitraje = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    nombre_libro = serializers.CharField(required=False)
    codigo_isbn = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    editorial_compilador = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    link_libro = serializers.URLField(
        required=False,
        allow_blank=True,
    )
    nombre_capitulo = serializers.CharField(required=False)
    editor_compilador = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    link_capitulo = serializers.URLField(
        required=False,
        allow_blank=True,
    )

    GENERAL_FIELDS = {
        "carrera",
        "proyecto",
        "area",
        "subarea",
        "pais",
        "ciudad",
        "fecha_publicacion",
        "origen_tipo",
        "origen_grado",
        "archivo_pdf",
    }

    TYPE_FIELDS = {
        "ponencia": {
            "tipo_presentacion",
            "tipo_presentacion_otro",
            "nombre_evento",
            "nombre_ponencia",
            "codigo_issn_isbn",
            "link_evento",
            "revisor_par_arbitraje",
        },
        "articulo": {
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
        },
        "libro": {
            "nombre_libro",
            "codigo_isbn",
            "editorial_compilador",
            "revisor_par_arbitraje",
            "link_libro",
        },
        "capitulo": {
            "nombre_capitulo",
            "nombre_libro",
            "codigo_isbn",
            "editor_compilador",
            "revisor_par_arbitraje",
            "link_capitulo",
        },
    }

    def to_internal_value(self, data):
        if hasattr(data, "lists"):
            plain = {}
            for key, values in data.lists():
                plain[key] = (
                    values[0]
                    if len(values) == 1
                    else list(values)
                )
        else:
            plain = dict(data)

        if "autores" in plain and isinstance(
            plain["autores"],
            str,
        ):
            try:
                plain["autores"] = json.loads(plain["autores"])
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError(
                    {
                        "autores": (
                            "El campo autores debe ser una "
                            "lista JSON válida."
                        )
                    }
                ) from exc

        return super().to_internal_value(plain)

    def _category(self):
        publication_type = getattr(self.instance, "tipo", None)
        code = str(
            getattr(publication_type, "codigo", "") or ""
        ).lower()
        category = str(
            getattr(publication_type, "categoria", "") or ""
        ).lower()

        if category:
            return category

        if "ponencia" in code:
            return "ponencia"

        if "capitulo" in code:
            return "capitulo"

        if "libro" in code:
            return "libro"

        return "articulo"

    def validate(self, attrs):
        instance = self.instance
        faculty_id = attrs.pop("facultad", None)

        career = attrs.get(
            "carrera",
            getattr(instance, "carrera", None),
        )
        project = attrs.get(
            "proyecto",
            getattr(instance, "proyecto", None),
        )

        if faculty_id is not None and career is not None:
            try:
                faculty_id = int(faculty_id)
            except (TypeError, ValueError, OverflowError) as exc:
                raise serializers.ValidationError(
                    {"facultad": "La facultad no es válida."}
                ) from exc

            if career.facultad_id != faculty_id:
                raise serializers.ValidationError(
                    {
                        "carrera": (
                            "La carrera no pertenece a la "
                            "facultad indicada."
                        )
                    }
                )

        if (
            project is not None
            and career is not None
            and project.carrera_id != career.pk
        ):
            raise serializers.ValidationError(
                {
                    "proyecto": (
                        "El proyecto no pertenece a la "
                        "carrera indicada."
                    )
                }
            )

        area = attrs.get("area", getattr(instance, "area", None))
        subarea = attrs.get(
            "subarea",
            getattr(instance, "subarea", None),
        )

        if subarea and not area:
            attrs["area"] = subarea.area
            area = subarea.area

        if area and subarea and subarea.area_id != area.pk:
            raise serializers.ValidationError(
                {
                    "subarea": (
                        "La subárea no pertenece al área "
                        "seleccionada."
                    )
                }
            )

        country = attrs.get("pais", getattr(instance, "pais", None))
        city = attrs.get("ciudad", getattr(instance, "ciudad", None))

        if city and country and city.pais_id != country.pk:
            raise serializers.ValidationError(
                {
                    "ciudad": (
                        "La ciudad no pertenece al país "
                        "seleccionado."
                    )
                }
            )

        if "archivo_pdf" in attrs and attrs["archivo_pdf"]:
            validate_pdf_file(
                attrs["archivo_pdf"],
                max_bytes=MAX_PRIMARY_PDF_BYTES,
            )

        if "origen_tipo" in attrs or "origen_grado" in attrs:
            origin = str(
                attrs.get(
                    "origen_tipo",
                    getattr(instance, "origen_tipo", "ninguno"),
                )
                or "ninguno"
            ).strip().lower()
            degree = normalize_optional_text(
                attrs.get(
                    "origen_grado",
                    getattr(instance, "origen_grado", None),
                )
            )

            if origin == "tic" and not degree:
                raise serializers.ValidationError(
                    {
                        "origen_grado": (
                            "Debe especificar el grado cuando "
                            "el origen es TIC."
                        )
                    }
                )

            attrs["origen_tipo"] = origin
            attrs["origen_grado"] = (
                degree if origin == "tic" else None
            )

        if "autores" in attrs:
            authors = attrs["autores"] or []

            if not authors:
                raise serializers.ValidationError(
                    {"autores": "Debe registrar al menos un autor."}
                )

            ids = [item["autor_id"] for item in authors]

            if len(ids) != len(set(ids)):
                raise serializers.ValidationError(
                    {"autores": "No puede repetir autores."}
                )

            existing = Autor.objects.in_bulk(ids)
            missing = [
                author_id
                for author_id in ids
                if author_id not in existing
            ]

            if missing:
                raise serializers.ValidationError(
                    {
                        "autores": (
                            "No existen los autores: "
                            + ", ".join(map(str, missing))
                        )
                    }
                )

            attrs["autores"] = [
                {
                    "autor_id": item["autor_id"],
                    "orden": index,
                    "rol_autoria": (
                        "principal" if index == 1 else "coautor"
                    ),
                }
                for index, item in enumerate(authors, start=1)
            ]

        return attrs

    def _update_related(self, instance, category, data):
        model_map = {
            "ponencia": (Ponencia, "ponencia"),
            "articulo": (Articulo, "articulo"),
            "libro": (Libro, "libro"),
            "capitulo": (CapituloLibro, "capitulo_libro"),
        }
        model, relation_name = model_map[category]
        values = {
            key: data[key]
            for key in self.TYPE_FIELDS[category]
            if key in data
        }

        if not values:
            return

        related = getattr(instance, relation_name, None)

        if related is None:
            model.objects.create(publicacion=instance, **values)
            return

        for key, value in values.items():
            setattr(related, key, value)

        related.save()

    def _sync_authors(self, instance, authors):
        PublicacionAutor.objects.filter(
            publicacion=instance
        ).delete()

        for item in authors:
            relation = PublicacionAutor(
                publicacion=instance,
                autor_id=item["autor_id"],
                orden=item["orden"],
                rol_autoria=item["rol_autoria"],
            )
            relation.full_clean()
            relation.save()

    @transaction.atomic
    def update(self, instance, validated_data):
        locked = (
            Publicacion.objects
            .select_for_update()
            .get(pk=instance.pk)
        )

        authors = validated_data.pop("autores", None)
        category = self._category()

        for field in self.GENERAL_FIELDS:
            if field in validated_data:
                setattr(locked, field, validated_data[field])

        locked.save()
        self._update_related(locked, category, validated_data)

        if authors is not None:
            self._sync_authors(locked, authors)

        return locked
