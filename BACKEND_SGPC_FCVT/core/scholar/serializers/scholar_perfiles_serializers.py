"""
Serializer para listar autores visibles en perfiles
públicos o institucionales tipo Scholar.

Expone:
- nombre;
- afiliación;
- avatar;
- total de publicaciones.
"""

from rest_framework import serializers

from core.models import Autor


class PerfilAutorListSerializer(
    serializers.ModelSerializer
):
    name = serializers.SerializerMethodField()
    org = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    publications = serializers.SerializerMethodField()

    class Meta:
        model = Autor

        fields = [
            "id",
            "name",
            "org",
            "avatar",
            "publications",
        ]

        read_only_fields = fields

    def get_name(
        self,
        obj,
    ):
        nombres = str(
            getattr(
                obj,
                "nombres",
                "",
            )
            or ""
        ).strip()

        apellidos = str(
            getattr(
                obj,
                "apellidos",
                "",
            )
            or ""
        ).strip()

        nombre = (
            f"{nombres} {apellidos}"
        ).strip()

        if nombre:
            return nombre

        correo = str(
            getattr(
                obj,
                "correo",
                "",
            )
            or ""
        ).strip()

        return (
            correo
            or "Autor"
        )

    def get_org(
        self,
        obj,
    ):
        user = getattr(
            obj,
            "usuario",
            None,
        )

        institucion = str(
            getattr(
                obj,
                "institucion",
                "",
            )
            or ""
        ).strip()

        # -----------------------------------------------------
        # Autor no vinculado a Usuario
        # -----------------------------------------------------

        if not user:
            if institucion:
                return institucion

            if getattr(
                obj,
                "es_externo",
                False,
            ):
                return "Autor externo"

            return "ULEAM"

        # -----------------------------------------------------
        # Usuario institucional
        # -----------------------------------------------------

        carrera = getattr(
            user,
            "carrera",
            None,
        )

        facultad = (
            getattr(
                carrera,
                "facultad",
                None,
            )
            if carrera
            else None
        )

        parts = []

        if (
            carrera
            and getattr(
                carrera,
                "nombre",
                None,
            )
        ):
            parts.append(
                carrera.nombre
            )

        if (
            facultad
            and getattr(
                facultad,
                "nombre",
                None,
            )
        ):
            parts.append(
                facultad.nombre
            )

        if parts:
            return " • ".join(
                parts
            )

        if institucion:
            return institucion

        if getattr(
            obj,
            "es_externo",
            False,
        ):
            return "Autor externo"

        return "ULEAM"

    def get_avatar(
        self,
        obj,
    ):
        user = getattr(
            obj,
            "usuario",
            None,
        )

        if not user:
            return None

        avatar = getattr(
            user,
            "avatar",
            None,
        )

        if (
            not avatar
            or not getattr(
                avatar,
                "name",
                None,
            )
        ):
            return None

        try:
            url = avatar.url
        except (
            AttributeError,
            ValueError,
        ):
            return None

        request = self.context.get(
            "request"
        )

        if request:
            try:
                return (
                    request.build_absolute_uri(
                        url
                    )
                )
            except Exception:
                pass

        return url

    def get_publications(
        self,
        obj,
    ):
        """
        Normalmente la vista proporciona:

            .annotate(publications=Count(...))

        Se mantiene un fallback seguro para evitar
        errores si el serializer se reutiliza.
        """

        annotated = getattr(
            obj,
            "publications",
            None,
        )

        if annotated is not None:
            try:
                return int(
                    annotated
                )
            except (
                TypeError,
                ValueError,
            ):
                return 0

        try:
            return int(
                obj.publicaciones.count()
            )
        except Exception:
            return 0