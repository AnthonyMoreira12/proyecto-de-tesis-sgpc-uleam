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
    Sede,
    PublicacionAutor,
    Subarea,
)
from core.publicaciones.services.publicaciones_duplicados_services import (
    validar_duplicados_fuerte_publicacion,
)
from core.publicaciones.services.publicaciones_historial_services import (
    registrar_edicion_publicacion,
)
from core.publicaciones.services.publicaciones_integridad_services import (
    validar_integridad_publicacion,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    get_publicacion_edit_block_reason,
    is_publicacion_content_editable,
)
from core.utils.files import normalize_optional_text, validate_pdf_file


MAX_PRIMARY_PDF_BYTES = 5 * 1024 * 1024


class AutorActualizacionItemSerializer(serializers.Serializer):
    autor_id = serializers.IntegerField(min_value=1)
    orden = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text=(
            "Se acepta por compatibilidad. El orden final se normaliza "
            "según la posición del autor en la lista recibida."
        ),
    )


class PublicacionActualizacionSerializer(serializers.Serializer):
    # Compatibilidad con el frontend. No se guarda en Publicacion.
    facultad = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True,
    )

    sede = serializers.PrimaryKeyRelatedField(
        queryset=Sede.objects.filter(activa=True),
        required=False,
        allow_null=True,
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

    anio_publicacion = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=2100,
    )
    mes_publicacion = serializers.ChoiceField(
        choices=[(month, month) for month in range(1, 13)],
        required=False,
        allow_null=True,
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
        "sede",
        "carrera",
        "proyecto",
        "area",
        "subarea",
        "pais",
        "ciudad",
        "anio_publicacion",
        "mes_publicacion",
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

        if (
            instance is not None
            and not is_publicacion_content_editable(
                instance
            )
        ):
            raise serializers.ValidationError(
                {
                    "estado": [
                        (
                            get_publicacion_edit_block_reason(
                                instance
                            )
                            or (
                                "El estado actual de la publicación "
                                "no permite modificar su contenido."
                            )
                        )
                    ]
                }
            )

        faculty_id = attrs.pop("facultad", None)

        site = attrs.get(
            "sede",
            getattr(instance, "sede", None),
        )
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

        if site is not None and career is not None:
            if not career.sedes_carrera.filter(
                sede_id=site.pk, activa=True
            ).exists():
                raise serializers.ValidationError({
                    "carrera": "La carrera seleccionada no está habilitada en la sede indicada."
                })

        if (
            project is not None
            and site is not None
            and getattr(project, "sede_id", None)
            and project.sede_id != site.pk
        ):
            raise serializers.ValidationError({
                "proyecto": "El proyecto seleccionado pertenece a una sede diferente."
            })

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

            # La posición en la lista recibida define únicamente el
            # orden bibliográfico. No existe jerarquía entre autores.
            attrs["autores"] = [
                {
                    "autor_id": item["autor_id"],
                    "orden": index,
                }
                for index, item in enumerate(authors, start=1)
            ]

        integrity = validar_integridad_publicacion(
            usuario=getattr(
                instance,
                "usuario_creador",
                None,
            ),
            sede=site,
            carrera=career,
            proyecto=project,
            area=attrs.get(
                "area",
                getattr(instance, "area", None),
            ),
            subarea=attrs.get(
                "subarea",
                getattr(instance, "subarea", None),
            ),
            pais=attrs.get(
                "pais",
                getattr(instance, "pais", None),
            ),
            ciudad=attrs.get(
                "ciudad",
                getattr(instance, "ciudad", None),
            ),
            anio_publicacion=attrs.get(
                "anio_publicacion",
                getattr(instance, "anio_publicacion", None),
            ),
            mes_publicacion=attrs.get(
                "mes_publicacion",
                getattr(instance, "mes_publicacion", None),
            ),
            registrado_por_admin=True,
            require_sede=False,
            require_carrera=True,
            require_periodo=True,
        )

        if (
            attrs.get("subarea")
            and not attrs.get("area")
            and integrity["area"] is not None
        ):
            attrs["area"] = integrity["area"]

        attrs["anio_publicacion"] = (
            integrity["anio_publicacion"]
        )
        attrs["mes_publicacion"] = (
            integrity["mes_publicacion"]
        )

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
            )
            relation.full_clean()
            relation.save()


    def _normalizar_valor_auditoria(
        self,
        value,
    ):
        if hasattr(
            value,
            "pk",
        ):
            return value.pk

        if isinstance(
            value,
            (list, tuple),
        ):
            return tuple(
                self._normalizar_valor_auditoria(
                    item
                )
                for item in value
            )

        return value

    def _autores_actuales_auditoria(
        self,
        instance,
    ):
        return tuple(
            PublicacionAutor.objects
            .filter(
                publicacion=instance
            )
            .order_by(
                "orden",
                "id",
            )
            .values_list(
                "autor_id",
                "orden",
            )
        )

    def _autores_nuevos_auditoria(
        self,
        autores,
    ):
        return tuple(
            (
                int(
                    item["autor_id"]
                ),
                int(
                    item.get(
                        "orden",
                        index,
                    )
                ),
            )
            for index, item in enumerate(
                autores or [],
                start=1,
            )
        )

    def _categoria_auditoria(
        self,
    ):
        if hasattr(
            self,
            "_category",
        ):
            return self._category()

        codigo = (
            self._instance_tipo_codigo()
            if hasattr(
                self,
                "_instance_tipo_codigo",
            )
            else ""
        )

        if codigo in {
            "articulo",
            "articulo_regional",
            "articulo_alto_impacto",
        }:
            return "articulo"

        if codigo == "ponencia":
            return "ponencia"

        if codigo == "libro":
            return "libro"

        if codigo in {
            "capitulo",
            "capitulo_libro",
        }:
            return "capitulo"

        return ""

    def _valor_actual_auditoria(
        self,
        instance,
        field,
    ):
        fk_fields = {
            "sede",
            "carrera",
            "proyecto",
            "area",
            "subarea",
            "pais",
            "ciudad",
        }

        if field in fk_fields:
            return getattr(
                instance,
                f"{field}_id",
                None,
            )

        base_fields = {
            "anio_publicacion",
            "mes_publicacion",
            "origen_tipo",
            "origen_grado",
        }

        if field in base_fields:
            return getattr(
                instance,
                field,
                None,
            )

        if field == "archivo_pdf":
            archivo = getattr(
                instance,
                "archivo_pdf",
                None,
            )
            return (
                getattr(
                    archivo,
                    "name",
                    None,
                )
                or None
            )

        if field == "autores":
            return (
                self._autores_actuales_auditoria(
                    instance
                )
            )

        relation_name = {
            "ponencia": "ponencia",
            "articulo": "articulo",
            "libro": "libro",
            "capitulo": "capitulo_libro",
        }.get(
            self._categoria_auditoria()
        )

        related = (
            getattr(
                instance,
                relation_name,
                None,
            )
            if relation_name
            else None
        )

        if (
            related is not None
            and hasattr(
                related,
                field,
            )
        ):
            return getattr(
                related,
                field,
                None,
            )

        return getattr(
            instance,
            field,
            None,
        )

    def _campos_realmente_modificados(
        self,
        instance,
        validated_data,
    ):
        """
        Calcula los campos cuyo valor realmente cambia.

        ``validate()`` puede insertar valores actuales para validar
        integridad. Esos valores no deben aparecer en auditoría si
        permanecen iguales.
        """

        modified = []

        for field, new_value in (
            validated_data.items()
        ):
            if field == "facultad":
                continue

            if field == "autores":
                old_value = (
                    self._autores_actuales_auditoria(
                        instance
                    )
                )
                new_value = (
                    self._autores_nuevos_auditoria(
                        new_value
                    )
                )

            elif field == "archivo_pdf":
                old_value = (
                    self._valor_actual_auditoria(
                        instance,
                        field,
                    )
                )
                new_value = (
                    getattr(
                        new_value,
                        "name",
                        None,
                    )
                    if new_value
                    else None
                )

            else:
                old_value = (
                    self._normalizar_valor_auditoria(
                        self._valor_actual_auditoria(
                            instance,
                            field,
                        )
                    )
                )
                new_value = (
                    self._normalizar_valor_auditoria(
                        new_value
                    )
                )

            if old_value != new_value:
                modified.append(
                    field
                )

        return sorted(
            set(
                modified
            )
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        campos_modificados = (
            self._campos_realmente_modificados(
                instance,
                validated_data,
            )
        )

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

        validar_duplicados_fuerte_publicacion(
            locked,
            campos_modificados=(
                campos_modificados
            ),
        )

        if authors is not None:
            self._sync_authors(locked, authors)

        request = self.context.get(
            "request"
        )

        actor = getattr(
            request,
            "user",
            None,
        )

        registrar_edicion_publicacion(
            publicacion=locked,
            actor=actor,
            campos_modificados=(
                campos_modificados
            ),
            origen="administracion",
        )

        return locked