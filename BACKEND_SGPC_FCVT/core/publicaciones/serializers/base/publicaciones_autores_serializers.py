"""
Serializers base para la participación de autores
en publicaciones.

Reglas principales:

- todos los participantes se consideran autores;
- no existe clasificación entre autor principal y coautor;
- acepta autor_id como campo oficial;
- mantiene compatibilidad temporal con el alias autor;
- mantiene compatibilidad temporal ignorando rol_autoria si
  un frontend antiguo todavía lo envía;
- cada autor debe tener un orden mayor o igual a 1;
- el orden representa únicamente la posición bibliográfica
  del autor dentro de la publicación.
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

    Payload oficial:

        {
            "autor_id": 10,
            "orden": 1
        }

    También admite temporalmente el alias histórico:

        {
            "autor": 10,
            "orden": 1
        }

    IMPORTANTE:

    El valor de ``orden`` NO representa una jerarquía de
    autoría. Únicamente conserva la posición en la que los
    autores deben mostrarse en:

    - detalles;
    - listados;
    - perfiles académicos;
    - reportes;
    - exportaciones;
    - referencias bibliográficas.
    """

    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(),
        source="autor",
        write_only=True,
    )

    orden = serializers.IntegerField(
        min_value=1,
    )

    # =========================================================
    # INPUT
    # =========================================================

    def to_internal_value(
        self,
        data,
    ):
        """
        Normaliza aliases históricos del frontend.

        Contrato nuevo:

            autor_id
            orden

        Compatibilidad temporal:

            autor -> autor_id

        ``rol_autoria`` se descarta si todavía es enviado por
        una versión anterior del frontend. No se valida, no se
        almacena y no forma parte del contrato actual.
        """

        if hasattr(
            data,
            "copy",
        ):
            source = data.copy()
        else:
            source = dict(data)

        # -----------------------------------------------------
        # Alias histórico:
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

        # Evitamos que el alias llegue como campo desconocido.
        source.pop(
            "autor",
            None,
        )

        # -----------------------------------------------------
        # Compatibilidad temporal con el contrato antiguo.
        #
        # Los roles de autoría fueron eliminados.
        # -----------------------------------------------------

        source.pop(
            "rol_autoria",
            None,
        )

        source.pop(
            "role",
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
        """
        Valida exclusivamente:

        - existencia del autor;
        - orden bibliográfico >= 1.

        La unicidad y consecutividad del conjunto completo
        de autores se comprueba posteriormente en el servicio
        de registro.
        """

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

        attrs["orden"] = orden

        return attrs


class PublicacionAutorSerializer(
    serializers.ModelSerializer
):
    """
    Serializer de lectura de PublicacionAutor.

    Todos los participantes se exponen simplemente como
    autores.

    Se mantienen los aliases históricos de nombre porque
    distintas interfaces del frontend utilizan:

    - autor_nombre;
    - nombre;
    - nombre_completo.

    No se expone ``rol_autoria`` porque esa clasificación
    dejó de formar parte del dominio de publicaciones.
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
            "orden",
        )

        read_only_fields = fields

    def _build_nombre(
        self,
        obj,
    ):
        """
        Construye una representación legible del autor.

        Prioridad:

        1. nombres + apellidos;
        2. correo;
        3. identificación;
        4. etiqueta genérica.
        """

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