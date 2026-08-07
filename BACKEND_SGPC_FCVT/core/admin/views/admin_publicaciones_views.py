"""ViewSet administrativo de publicaciones."""

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.admin.selectors.admin_publicaciones_selectors import (
    admin_publicaciones_detail_queryset,
    admin_publicaciones_list_queryset,
    filter_admin_publicaciones_queryset,
)
from core.admin.serializers.admin_publicaciones_serializers import (
    AdminPublicacionDetalleSerializer,
    AdminPublicacionListadoSerializer,
)
from core.admin.serializers.update.publicaciones_actualizacion_serializers import (
    PublicacionActualizacionSerializer,
)
from core.admin.services.admin_publicaciones_services import (
    AdminPublicacionesServiceError,
    prepare_admin_publicacion_payload,
)
from core.models import (
    Publicacion,
    PublicacionArchivo,
)
from core.permisos.es_admin import EsAdmin
from core.publicaciones.serializers.create.publicaciones_articulo_create_serializers import (
    ArticuloRegistroSerializer,
)
from core.publicaciones.serializers.create.publicaciones_capitulo_libro_create_serializers import (
    CapituloLibroRegistroSerializer,
)
from core.publicaciones.serializers.create.publicaciones_libro_create_serializers import (
    LibroRegistroSerializer,
)
from core.publicaciones.serializers.create.publicaciones_ponencia_create_serializers import (
    PonenciaRegistroSerializer,
)


def _django_validation_payload(
    exc,
):
    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
        return {
            "detail": list(
                exc.messages
            )
        }

    return {
        "detail": [
            str(exc)
        ]
    }


class AdminPublicacionViewSet(
    viewsets.ModelViewSet
):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        permissions.IsAuthenticated,
        EsAdmin,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    queryset = (
        admin_publicaciones_detail_queryset()
    )

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self):
        if self.action == "retrieve":
            return (
                admin_publicaciones_detail_queryset()
            )

        base = (
            admin_publicaciones_list_queryset()
        )

        params = self.request.query_params

        return filter_admin_publicaciones_queryset(
            base,
            q=params.get(
                "q",
                "",
            ),
            tipo=(
                params.get(
                    "tipo"
                )
                or params.get(
                    "tipo_publicacion_final",
                    "",
                )
            ),
            usuario_objetivo_id=(
                params.get(
                    "usuario_objetivo_id"
                )
                or params.get(
                    "usuario_id"
                )
            ),
            autor_objetivo_id=(
                params.get(
                    "autor_objetivo_id"
                )
                or params.get(
                    "autor_id"
                )
            ),
            admin_registrador_id=(
                params.get(
                    "admin_registrador_id"
                )
            ),
            facultad_id=params.get(
                "facultad_id"
            ),
            carrera_id=params.get(
                "carrera_id"
            ),
            anio=params.get(
                "anio"
            ),
            mes=params.get(
                "mes"
            ),
            solo_delegadas=params.get(
                "solo_delegadas"
            ),
            solo_con_pdf=params.get(
                "solo_con_pdf"
            ),
            solo_con_adjuntos=params.get(
                "solo_con_adjuntos"
            ),
            ordering=params.get(
                "ordering",
                "",
            ),
        )

    # ========================================================
    # SERIALIZERS
    # ========================================================

    def get_serializer_class(self):
        if self.action in {
            "update",
            "partial_update",
        }:
            return (
                PublicacionActualizacionSerializer
            )

        if self.action == "retrieve":
            return (
                AdminPublicacionDetalleSerializer
            )

        return (
            AdminPublicacionListadoSerializer
        )

    def _serialize_detail(
        self,
        publication,
    ):
        """
        Recupera nuevamente la publicación con todas sus
        relaciones y adjuntos para construir la respuesta.
        """
        refreshed = (
            admin_publicaciones_detail_queryset()
            .get(
                pk=publication.pk
            )
        )

        return (
            AdminPublicacionDetalleSerializer(
                refreshed,
                context=(
                    self.get_serializer_context()
                ),
            )
            .data
        )

    # ========================================================
    # CREACIÓN GENÉRICA BLOQUEADA
    # ========================================================

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        return Response(
            {
                "detail": (
                    "Utilice el endpoint de creación "
                    "correspondiente al tipo de publicación."
                )
            },
            status=(
                status.HTTP_405_METHOD_NOT_ALLOWED
            ),
        )

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        current = self.get_object()

        with transaction.atomic():
            locked = (
                Publicacion.objects
                .select_for_update()
                .get(
                    pk=current.pk
                )
            )

            serializer = (
                PublicacionActualizacionSerializer(
                    locked,
                    data=request.data,
                    partial=kwargs.pop(
                        "partial",
                        False,
                    ),
                    context=(
                        self.get_serializer_context()
                    ),
                )
            )

            serializer.is_valid(
                raise_exception=True
            )

            publication = serializer.save()

        return Response(
            self._serialize_detail(
                publication
            )
        )

    # ========================================================
    # CREACIÓN ADMINISTRATIVA DELEGADA
    # ========================================================

    def _create_delegated(
        self,
        request,
        *,
        serializer_class,
        label,
        allow_attachments=False,
        preserve_facultad=False,
    ):
        """
        Registra una publicación en nombre de un usuario.

        El servicio prepara:

        - Usuario objetivo.
        - Autor objetivo.
        - Datos normalizados.
        - Archivos adjuntos validados.
        """
        try:
            prepared = (
                prepare_admin_publicacion_payload(
                    request=request,
                    preserve_facultad=(
                        preserve_facultad
                    ),
                )
            )

        except AdminPublicacionesServiceError as exc:
            return Response(
                exc.detail,
                status=exc.status_code,
            )

        try:
            with transaction.atomic():
                serializer = serializer_class(
                    data=prepared[
                        "data"
                    ],
                    context={
                        "request": request,
                        "usuario_creador_override": (
                            prepared[
                                "usuario_objetivo"
                            ]
                        ),
                        "autor_objetivo": (
                            prepared[
                                "autor_objetivo"
                            ]
                        ),
                        "admin_registrador": (
                            request.user
                        ),
                        "registrado_por_admin": True,
                        "permitir_usuario_inactivo_delegado": (
                            prepared[
                                "permitir_usuario_inactivo_delegado"
                            ]
                        ),
                    },
                )

                serializer.is_valid(
                    raise_exception=True
                )

                saved = serializer.save()

                publication = getattr(
                    saved,
                    "publicacion",
                    saved,
                )

                created_files = []

                if allow_attachments:
                    for item in prepared[
                        "adjuntos"
                    ]:
                        created_files.append(
                            PublicacionArchivo.objects.create(
                                publicacion=publication,
                                nombre=item[
                                    "nombre"
                                ],
                                orden=item[
                                    "orden"
                                ],
                                archivo=item[
                                    "file"
                                ],
                            )
                        )

        except DjangoValidationError as exc:
            return Response(
                _django_validation_payload(
                    exc
                ),
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        except serializers.ValidationError:
            raise

        except IntegrityError:
            return Response(
                {
                    "detail": (
                        "No se pudo registrar la publicación "
                        "por un conflicto de integridad."
                    )
                },
                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        target_user = prepared[
            "usuario_objetivo"
        ]

        target_author = prepared[
            "autor_objetivo"
        ]

        payload = {
            "message": label,

            "usuario_objetivo": {
                "id": target_user.pk,
                "nombre": (
                    target_user.get_full_name()
                ),
                "email": target_user.email,
            },

            "autor_objetivo": {
                "id": target_author.pk,
                "nombre": (
                    f"{target_author.nombres} "
                    f"{target_author.apellidos}"
                ).strip(),
            },

            "publicacion": (
                self._serialize_detail(
                    publication
                )
            ),
        }

        if allow_attachments:
            payload["adjuntos"] = {
                "total": len(
                    created_files
                ),
            }

        return Response(
            payload,
            status=(
                status.HTTP_201_CREATED
            ),
        )

    # ========================================================
    # ARTÍCULOS
    # ========================================================

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="articulos/crear",
    )
    def crear_articulo(
        self,
        request,
    ):
        return self._create_delegated(
            request,
            serializer_class=(
                ArticuloRegistroSerializer
            ),
            label=(
                "Artículo delegado registrado "
                "correctamente."
            ),
            allow_attachments=True,
            preserve_facultad=True,
        )

    # ========================================================
    # LIBROS
    # ========================================================

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="libros/crear",
    )
    def crear_libro(
        self,
        request,
    ):
        return self._create_delegated(
            request,
            serializer_class=(
                LibroRegistroSerializer
            ),
            label=(
                "Libro delegado registrado "
                "correctamente."
            ),
            allow_attachments=True,
            preserve_facultad=True,
        )

    # ========================================================
    # CAPÍTULOS DE LIBRO
    # ========================================================

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="capitulos/crear",
    )
    def crear_capitulo(
        self,
        request,
    ):
        return self._create_delegated(
            request,
            serializer_class=(
                CapituloLibroRegistroSerializer
            ),
            label=(
                "Capítulo delegado registrado "
                "correctamente."
            ),
            allow_attachments=True,
            preserve_facultad=True,
        )

    # ========================================================
    # PONENCIAS
    # ========================================================

    @action(
        detail=False,
        methods=[
            "post",
        ],
        url_path="ponencias/crear",
    )
    def crear_ponencia(
        self,
        request,
    ):
        return self._create_delegated(
            request,
            serializer_class=(
                PonenciaRegistroSerializer
            ),
            label=(
                "Ponencia delegada registrada "
                "correctamente."
            ),
            allow_attachments=True,
            preserve_facultad=False,
        )
