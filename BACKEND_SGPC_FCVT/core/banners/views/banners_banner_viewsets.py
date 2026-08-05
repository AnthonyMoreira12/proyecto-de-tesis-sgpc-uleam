"""
ViewSet para gestionar los banners institucionales y su
configuración visual global.

Permisos:

- Usuarios autenticados:
    - Listar banners.
    - Consultar banners.
    - Consultar estado.
    - Consultar configuración.

- Administradores:
    - Crear banners.
    - Modificar banners.
    - Eliminar banners.
    - Modificar la configuración global.

El módulo mantiene respuestas controladas cuando las tablas
todavía no existen, para evitar que el frontend falle durante
despliegues o migraciones pendientes.
"""

import hashlib
import json
import logging

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import (
    DatabaseError,
    IntegrityError,
    transaction,
)
from django.db.models.deletion import ProtectedError
from django.db.utils import (
    OperationalError,
    ProgrammingError,
)
from django.shortcuts import get_object_or_404

from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from core.banners.serializers.banners_banner_serializers import (
    BannerConfiguracionSerializer,
    BannerSerializer,
)
from core.models.banners import (
    DEFAULT_BANNER_EYEBROW,
    DEFAULT_BANNER_RECENT_LABEL,
    DEFAULT_BANNER_TEXT,
    DEFAULT_BANNER_TITLE,
    DISPLAY_MODE_DEFAULT,
    MEDIA_PANE_WIDTH_DEFAULT,
    STAGE_HEIGHT_DEFAULT,
    STAGE_WIDTH_DEFAULT,
    Banner,
    BannerConfiguracion,
)
from core.permisos.es_admin import EsAdmin


logger = logging.getLogger(__name__)


# ============================================================
# UTILIDADES
# ============================================================

def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura
    compatible con Django REST Framework.
    """
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
        "detail": str(exc),
    }


def _datetime_to_iso(value):
    """
    Convierte una fecha en una cadena estable para versiones.
    """
    if value is None:
        return ""

    isoformat = getattr(
        value,
        "isoformat",
        None,
    )

    if callable(isoformat):
        return isoformat()

    return str(value)


def _hash_version_payload(payload):
    """
    Construye una versión determinista sin exponer el contenido.
    """
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def _empty_status_payload():
    """
    Respuesta estable cuando no existen banners disponibles.
    """
    return {
        "has_items": False,
        "total": 0,
        "version": "",
        "notify_version": "",
    }


# ============================================================
# VIEWSET
# ============================================================

class BannerViewSet(viewsets.ModelViewSet):
    """
    Gestiona banners y la configuración global de presentación.
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    parser_classes = [
        JSONParser,
        FormParser,
        MultiPartParser,
    ]

    serializer_class = BannerSerializer

    queryset = (
        Banner.objects
        .all()
        .order_by(
            "-created_at",
            "-pk",
        )
    )

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    ]

    lookup_field = "pk"

    lookup_value_regex = r"\d+"

    # ========================================================
    # ENCABEZADOS
    # ========================================================

    def finalize_response(
        self,
        request,
        response,
        *args,
        **kwargs,
    ):
        """
        Impide almacenar banners y configuraciones en caché.

        El frontend ya utiliza el endpoint status para detectar
        cambios, por lo que las respuestas deben representar
        siempre el estado actual.
        """
        response = super().finalize_response(
            request,
            response,
            *args,
            **kwargs,
        )

        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, "
            "max-age=0, private"
        )

        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response

    # ========================================================
    # PERMISOS
    # ========================================================

    def get_permissions(self):
        """
        Las operaciones de escritura requieren privilegios
        administrativos.
        """
        action_name = getattr(
            self,
            "action",
            None,
        )

        write_actions = {
            "create",
            "update",
            "partial_update",
            "destroy",
        }

        config_write = bool(
            action_name == "config"
            and self.request.method.upper()
            in {
                "PATCH",
                "PUT",
            }
        )

        if (
            action_name in write_actions
            or config_write
        ):
            permission_classes = [
                permissions.IsAuthenticated,
                EsAdmin,
            ]

        else:
            permission_classes = [
                permissions.IsAuthenticated,
            ]

        return [
            permission_class()
            for permission_class
            in permission_classes
        ]

    # ========================================================
    # CONTEXTO DEL SERIALIZER
    # ========================================================

    def get_serializer_context(self):
        """
        Incluye la petición para construir URLs absolutas.
        """
        context = super().get_serializer_context()

        context["request"] = self.request

        return context

    # ========================================================
    # DISPONIBILIDAD DE TABLAS
    # ========================================================

    def _banner_table_ready(self):
        """
        Comprueba que la tabla de banners exista.

        La consulta funciona aunque la tabla esté vacía.
        """
        try:
            list(
                Banner.objects
                .values_list(
                    "pk",
                    flat=True,
                )[:1]
            )

            return True

        except (
            ProgrammingError,
            OperationalError,
        ):
            return False

    def _config_table_ready(self):
        """
        Comprueba que la tabla de configuración exista sin crear
        automáticamente un registro.
        """
        try:
            list(
                BannerConfiguracion.objects
                .values_list(
                    "pk",
                    flat=True,
                )[:1]
            )

            return True

        except (
            ProgrammingError,
            OperationalError,
        ):
            return False

    def _tables_unavailable_response(
        self,
        detail=(
            "Las tablas de banners todavía no han "
            "sido migradas."
        ),
    ):
        """
        Respuesta controlada cuando una tabla no existe.
        """
        return Response(
            {
                "detail": detail,
            },
            status=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

    # ========================================================
    # CONFIGURACIÓN PREDETERMINADA
    # ========================================================

    def _default_config_payload(self):
        """
        Devuelve la configuración visual predeterminada.
        """
        return {
            "eyebrow": (
                DEFAULT_BANNER_EYEBROW
            ),
            "title": (
                DEFAULT_BANNER_TITLE
            ),
            "text": (
                DEFAULT_BANNER_TEXT
            ),
            "recentLabel": (
                DEFAULT_BANNER_RECENT_LABEL
            ),
            "stageWidth": (
                STAGE_WIDTH_DEFAULT
            ),
            "stageHeight": (
                STAGE_HEIGHT_DEFAULT
            ),
            "mediaPaneWidth": (
                MEDIA_PANE_WIDTH_DEFAULT
            ),
            "displayMode": (
                DISPLAY_MODE_DEFAULT
            ),
            "created_at": None,
            "updated_at": None,
        }

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self):
        """
        Retorna un queryset vacío cuando la tabla aún no existe.

        Esto permite que el listado inicial del frontend no falle
        durante una instalación nueva.
        """
        if not self._banner_table_ready():
            return Banner.objects.none()

        return (
            Banner.objects
            .all()
            .order_by(
                "-created_at",
                "-pk",
            )
        )

    # ========================================================
    # RECUPERACIÓN BLOQUEADA
    # ========================================================

    def _get_locked_banner(self):
        """
        Recupera y bloquea un banner durante una modificación o
        eliminación.
        """
        lookup_url_kwarg = (
            self.lookup_url_kwarg
            or self.lookup_field
        )

        lookup_value = self.kwargs.get(
            lookup_url_kwarg
        )

        queryset = (
            Banner.objects
            .select_for_update()
            .all()
        )

        banner = get_object_or_404(
            queryset,
            **{
                self.lookup_field: (
                    lookup_value
                )
            },
        )

        self.check_object_permissions(
            self.request,
            banner,
        )

        return banner

    # ========================================================
    # LISTADO Y DETALLE
    # ========================================================

    def list(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Devuelve una lista vacía cuando todavía no se ha creado
        la tabla.
        """
        if not self._banner_table_ready():
            return Response(
                [],
                status=status.HTTP_200_OK,
            )

        return super().list(
            request,
            *args,
            **kwargs,
        )

    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        return super().retrieve(
            request,
            *args,
            **kwargs,
        )

    # ========================================================
    # CREACIÓN
    # ========================================================

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Crea un banner dentro de una transacción.
        """
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        try:
            serializer = self.get_serializer(
                data=request.data
            )

            serializer.is_valid(
                raise_exception=True
            )

            with transaction.atomic():
                banner = serializer.save()

                created_banner = (
                    Banner.objects
                    .get(
                        pk=banner.pk
                    )
                )

        except DjangoValidationError as exc:
            raise ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No fue posible crear el banner "
                        "debido a un conflicto con los "
                        "datos almacenados."
                    )
                }
            ) from exc

        except OSError:
            logger.exception(
                "No se pudo almacenar la imagen del banner."
            )

            return Response(
                {
                    "detail": (
                        "No fue posible almacenar la imagen "
                        "del banner. Revise el almacenamiento "
                        "de archivos."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        except DatabaseError:
            logger.exception(
                "Error de base de datos al crear un banner."
            )

            return Response(
                {
                    "detail": (
                        "No fue posible crear el banner "
                        "debido a un error temporal de la "
                        "base de datos."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        response_serializer = self.get_serializer(
            created_banner
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(
                response_serializer.data
            ),
        )

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def _update_banner(
        self,
        request,
        *,
        partial,
    ):
        """
        Implementación compartida por PUT y PATCH.
        """
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        try:
            with transaction.atomic():
                banner = self._get_locked_banner()

                serializer = self.get_serializer(
                    banner,
                    data=request.data,
                    partial=partial,
                )

                serializer.is_valid(
                    raise_exception=True
                )

                updated_banner = serializer.save()

                updated_banner = (
                    Banner.objects
                    .get(
                        pk=updated_banner.pk
                    )
                )

        except DjangoValidationError as exc:
            raise ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No fue posible actualizar el banner "
                        "debido a un conflicto con los "
                        "datos almacenados."
                    )
                }
            ) from exc

        except OSError:
            logger.exception(
                (
                    "No se pudo reemplazar la imagen "
                    "del banner."
                )
            )

            return Response(
                {
                    "detail": (
                        "No fue posible almacenar la nueva "
                        "imagen del banner."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        except DatabaseError:
            logger.exception(
                "Error de base de datos al actualizar un banner."
            )

            return Response(
                {
                    "detail": (
                        "No fue posible actualizar el banner "
                        "debido a un error temporal de la "
                        "base de datos."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        response_serializer = self.get_serializer(
            updated_banner
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        return self._update_banner(
            request,
            partial=False,
        )

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):
        return self._update_banner(
            request,
            partial=True,
        )

    # ========================================================
    # ELIMINACIÓN
    # ========================================================

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Elimina un banner protegiendo la operación frente a
        actualizaciones concurrentes.
        """
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        try:
            with transaction.atomic():
                banner = self._get_locked_banner()

                self.perform_destroy(
                    banner
                )

        except ProtectedError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No se puede eliminar el banner "
                        "porque está relacionado con otros "
                        "registros del sistema."
                    )
                }
            ) from exc

        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No se puede eliminar el banner "
                        "porque mantiene relaciones activas."
                    )
                }
            ) from exc

        except OSError:
            logger.exception(
                (
                    "No se pudo eliminar el archivo físico "
                    "del banner."
                )
            )

            return Response(
                {
                    "detail": (
                        "El banner no pudo eliminarse por un "
                        "problema con el almacenamiento."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al eliminar "
                    "un banner."
                )
            )

            return Response(
                {
                    "detail": (
                        "No fue posible eliminar el banner "
                        "debido a un error temporal de la "
                        "base de datos."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    # ========================================================
    # ESTADO
    # ========================================================

    @action(
        detail=False,
        methods=[
            "get",
        ],
        url_path="status",
        url_name="status",
    )
    def status(
        self,
        request,
    ):
        """
        Devuelve dos versiones independientes:

        - version:
          Cambia por contenido, imágenes o diseño.

        - notify_version:
          Cambia únicamente cuando se modifica información que
          debe volver a mostrarse como aviso a los usuarios.

        De este modo, cambiar solo el tamaño o la distribución
        no reabre el overlay institucional para todos.
        """
        if not self._banner_table_ready():
            return Response(
                _empty_status_payload(),
                status=status.HTTP_200_OK,
            )

        try:
            queryset = (
                Banner.objects
                .all()
                .order_by("pk")
            )

            banner_rows = list(
                queryset.values(
                    "pk",
                    "title",
                    "eyebrow",
                    "text",
                    "recent_label",
                    "image",
                    "created_at",
                    "updated_at",
                )
            )

            total = len(banner_rows)

            normalized_banners = []

            for row in banner_rows:
                normalized_banners.append(
                    {
                        "id": row.get("pk"),
                        "title": str(
                            row.get("title") or ""
                        ),
                        "eyebrow": str(
                            row.get("eyebrow") or ""
                        ),
                        "text": str(
                            row.get("text") or ""
                        ),
                        "recent_label": str(
                            row.get("recent_label") or ""
                        ),
                        "image": str(
                            row.get("image") or ""
                        ),
                        "created_at": _datetime_to_iso(
                            row.get("created_at")
                        ),
                        "updated_at": _datetime_to_iso(
                            row.get("updated_at")
                        ),
                    }
                )

            configuration = None

            if self._config_table_ready():
                configuration = (
                    BannerConfiguracion.objects
                    .order_by("pk")
                    .first()
                )

            global_content = {
                "eyebrow": str(
                    getattr(
                        configuration,
                        "eyebrow",
                        DEFAULT_BANNER_EYEBROW,
                    )
                    or ""
                ),
                "title": str(
                    getattr(
                        configuration,
                        "title",
                        DEFAULT_BANNER_TITLE,
                    )
                    or ""
                ),
                "text": str(
                    getattr(
                        configuration,
                        "text",
                        DEFAULT_BANNER_TEXT,
                    )
                    or ""
                ),
                "recent_label": str(
                    getattr(
                        configuration,
                        "recent_label",
                        DEFAULT_BANNER_RECENT_LABEL,
                    )
                    or ""
                ),
            }

            layout = {
                "stage_width": int(
                    getattr(
                        configuration,
                        "stage_width",
                        STAGE_WIDTH_DEFAULT,
                    )
                ),
                "stage_height": int(
                    getattr(
                        configuration,
                        "stage_height",
                        STAGE_HEIGHT_DEFAULT,
                    )
                ),
                "media_pane_width": int(
                    getattr(
                        configuration,
                        "media_pane_width",
                        MEDIA_PANE_WIDTH_DEFAULT,
                    )
                ),
                "display_mode": str(
                    getattr(
                        configuration,
                        "display_mode",
                        DISPLAY_MODE_DEFAULT,
                    )
                    or DISPLAY_MODE_DEFAULT
                ),
            }

            notify_version = _hash_version_payload(
                {
                    "banners": normalized_banners,
                    "global_content": global_content,
                }
            )

            general_version = _hash_version_payload(
                {
                    "notify_version": notify_version,
                    "layout": layout,
                    "configuration_updated_at": (
                        _datetime_to_iso(
                            getattr(
                                configuration,
                                "updated_at",
                                None,
                            )
                        )
                    ),
                }
            )

            return Response(
                {
                    "has_items": total > 0,
                    "total": total,
                    "version": general_version,
                    "notify_version": notify_version,
                },
                status=status.HTTP_200_OK,
            )

        except (
            ProgrammingError,
            OperationalError,
        ):
            return Response(
                _empty_status_payload(),
                status=status.HTTP_200_OK,
            )

        except DatabaseError:
            logger.exception(
                (
                    "No se pudo calcular el estado "
                    "de los banners."
                )
            )

            return Response(
                _empty_status_payload(),
                status=status.HTTP_200_OK,
            )

    # ========================================================
    # CONFIGURACIÓN GLOBAL
    # ========================================================

    @action(
        detail=False,
        methods=[
            "get",
            "patch",
        ],
        url_path="config",
        url_name="config",
    )
    def config(
        self,
        request,
    ):
        """
        Consulta o modifica la configuración singleton.

        GET no crea registros automáticamente. Cuando todavía no
        existe una configuración, devuelve los valores
        predeterminados.

        PATCH crea o actualiza el singleton.
        """
        if not self._config_table_ready():
            if request.method.upper() == "GET":
                return Response(
                    self._default_config_payload(),
                    status=status.HTTP_200_OK,
                )

            return self._tables_unavailable_response()

        if request.method.upper() == "GET":
            try:
                configuration = (
                    BannerConfiguracion.objects
                    .order_by("pk")
                    .first()
                )

            except DatabaseError:
                logger.exception(
                    (
                        "No se pudo consultar la configuración "
                        "de banners."
                    )
                )

                return Response(
                    {
                        "detail": (
                            "No fue posible consultar la "
                            "configuración de banners."
                        )
                    },
                    status=(
                        status.HTTP_503_SERVICE_UNAVAILABLE
                    ),
                )

            if configuration is None:
                return Response(
                    self._default_config_payload(),
                    status=status.HTTP_200_OK,
                )

            serializer = (
                BannerConfiguracionSerializer(
                    configuration,
                    context=(
                        self.get_serializer_context()
                    ),
                )
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        try:
            with transaction.atomic():
                configuration = (
                    BannerConfiguracion.objects
                    .select_for_update()
                    .order_by("pk")
                    .first()
                )

                if configuration is None:
                    serializer = (
                        BannerConfiguracionSerializer(
                            data=request.data,
                            partial=True,
                            context=(
                                self.get_serializer_context()
                            ),
                        )
                    )

                else:
                    serializer = (
                        BannerConfiguracionSerializer(
                            configuration,
                            data=request.data,
                            partial=True,
                            context=(
                                self.get_serializer_context()
                            ),
                        )
                    )

                serializer.is_valid(
                    raise_exception=True
                )

                saved_configuration = (
                    serializer.save()
                )

                saved_configuration = (
                    BannerConfiguracion.objects
                    .get(
                        pk=saved_configuration.pk
                    )
                )

        except DjangoValidationError as exc:
            raise ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            logger.exception(
                (
                    "Conflicto de integridad al guardar "
                    "la configuración de banners."
                )
            )

            raise ValidationError(
                {
                    "detail": (
                        "No fue posible guardar la "
                        "configuración de banners debido "
                        "a un conflicto de integridad."
                    )
                }
            ) from exc

        except DatabaseError:
            logger.exception(
                (
                    "Error de base de datos al actualizar "
                    "la configuración de banners."
                )
            )

            return Response(
                {
                    "detail": (
                        "No fue posible actualizar la "
                        "configuración debido a un error "
                        "temporal de la base de datos."
                    )
                },
                status=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        response_serializer = (
            BannerConfiguracionSerializer(
                saved_configuration,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )