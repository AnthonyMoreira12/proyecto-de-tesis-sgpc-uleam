"""
Serializers base para la participación de autores
en publicaciones.

Reglas principales:

- acepta autor_id como campo oficial;
- mantiene compatibilidad con el alias autor;
- orden >= 1;
- orden 1 = autor principal;
- orden > 1 = coautor;
- evita inconsistencias entre orden y rol.
"""

from rest_framework import serializers

from core.models import (
    Autor,
    PublicacionAutor,
)


class AutorParticipacionSerializer(
    serializers.Serializer
):
    """
    Serializer de entrada utilizado durante el registro
    de una publicación.

    Payload recomendado:

        {
            "autor_id": 10,
            "orden": 1
        }

    También admite por compatibilidad:

        {
            "autor": 10,
            "orden": 1
        }

    El rol se determina automáticamente a partir
    del orden.
    """

    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(),
        source="autor",
        write_only=True,
    )

    orden = serializers.IntegerField(
        min_value=1,
    )

    rol_autoria = serializers.ChoiceField(
        choices=PublicacionAutor.ROL_AUTORIA,
        required=False,
        allow_null=True,
    )

    # =========================================================
    # INPUT
    # =========================================================

    def to_internal_value(
        self,
        data,
    ):
        if hasattr(
            data,
            "copy",
        ):
            source = data.copy()
        else:
            source = dict(data)

        # -----------------------------------------------------
        # Compatibilidad:
        #
        #     autor
        #
        # pasa a:
        #
        #     autor_id
        # -----------------------------------------------------

        autor_id = source.get(
            "autor_id",
            None,
        )

        autor_alias = source.get(
            "autor",
            None,
        )

        if autor_id in (
            None,
            "",
        ):
            if autor_alias not in (
                None,
                "",
            ):
                source["autor_id"] = (
                    autor_alias
                )

        # Evitamos que el alias llegue como un campo
        # desconocido al Serializer.
        source.pop(
            "autor",
            None,
        )

        return super().to_internal_value(
            source
        )

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def validate(
        self,
        attrs,
    ):
        autor = attrs.get(
            "autor"
        )

        if autor is None:
            raise serializers.ValidationError(
                {
                    "autor_id": [
                        "Debe seleccionar "
                        "un autor válido."
                    ]
                }
            )

        orden = attrs.get(
            "orden"
        )

        if orden is None:
            raise serializers.ValidationError(
                {
                    "orden": [
                        "Debe especificar "
                        "el orden del autor."
                    ]
                }
            )

        try:
            orden = int(
                orden
            )

        except (
            TypeError,
            ValueError,
        ):
            raise serializers.ValidationError(
                {
                    "orden": [
                        "El orden debe ser "
                        "un número entero válido."
                    ]
                }
            )

        if orden < 1:
            raise serializers.ValidationError(
                {
                    "orden": [
                        "El orden debe ser mayor "
                        "o igual a 1."
                    ]
                }
            )

        # -----------------------------------------------------
        # El rol real se deriva del orden.
        # -----------------------------------------------------

        expected_role = (
            "principal"
            if orden == 1
            else "coautor"
        )

        received_role = attrs.get(
            "rol_autoria"
        )

        # Si el frontend envía rol, comprobamos que
        # sea coherente.
        if (
            received_role
            and received_role
            != expected_role
        ):
            if orden == 1:
                raise serializers.ValidationError(
                    {
                        "rol_autoria": [
                            "El autor ubicado en "
                            "el orden 1 debe ser principal."
                        ]
                    }
                )

            raise serializers.ValidationError(
                {
                    "rol_autoria": [
                        "Los autores con orden superior "
                        "a 1 deben ser coautores."
                    ]
                }
            )

        attrs["orden"] = orden

        attrs[
            "rol_autoria"
        ] = expected_role

        return attrs


class PublicacionAutorSerializer(
    serializers.ModelSerializer
):
    """
    Serializer de lectura de PublicacionAutor.

    Mantiene los alias históricos utilizados por
    distintas interfaces del frontend:

    - autor_nombre
    - nombre
    - nombre_completo
    """

    autor_id = serializers.IntegerField(
        source="autor.id",
        read_only=True,
    )

    autor_nombre = (
        serializers.SerializerMethodField(
            read_only=True
        )
    )

    nombre = (
        serializers.SerializerMethodField(
            read_only=True
        )
    )

    nombre_completo = (
        serializers.SerializerMethodField(
            read_only=True
        )
    )

    class Meta:
        model = PublicacionAutor

        fields = (
            "id",
            "autor_id",
            "autor_nombre",
            "nombre",
            "nombre_completo",
            "rol_autoria",
            "orden",
        )

        read_only_fields = fields

    def _build_nombre(
        self,
        obj,
    ):
        autor = getattr(
            obj,
            "autor",
            None,
        )

        if autor is None:
            return "Autor"

        nombres = str(
            getattr(
                autor,
                "nombres",
                "",
            )
            or ""
        ).strip()

        apellidos = str(
            getattr(
                autor,
                "apellidos",
                "",
            )
            or ""
        ).strip()

        nombre_completo = (
            f"{nombres} {apellidos}"
        ).strip()

        if nombre_completo:
            return nombre_completo

        correo = str(
            getattr(
                autor,
                "correo",
                "",
            )
            or ""
        ).strip()

        if correo:
            return correo

        identificacion = str(
            getattr(
                autor,
                "identificacion",
                "",
            )
            or ""
        ).strip()

        return (
            identificacion
            or "Autor"
        )

    def get_autor_nombre(
        self,
        obj,
    ):
        return self._build_nombre(
            obj
        )

    def get_nombre(
        self,
        obj,
    ):
        return self._build_nombre(
            obj
        )

    def get_nombre_completo(
        self,
        obj,
    ):
        return self._build_nombre(
            obj
        )