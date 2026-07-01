"""
ViewSet para gestión de proyectos del sistema.

Qué hace:
- Lista proyectos con paginación.
- Usa selectors centralizados para visibilidad, búsqueda y filtros.
- Permite filtrar por: q, anio, estado.
- Expone endpoint de años disponibles desde base de datos.
- Permite a administradores crear, editar, eliminar y cambiar estado.
- Permite extender la fecha final del proyecto mediante endpoint dedicado.
- Permite gestionar autores después de crear el proyecto.
- Para usuarios no administradores solo expone proyectos visibles.
- Devuelve serializer liviano en listados y serializer completo en detalle.
- Soporta multipart/form-data para carga del PDF del proyecto.
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.proyectos.serializers.proyectos_proyecto_serializers import (
    ProyectoAutorReadSerializer,
    ProyectoListSerializer,
    ProyectoSerializer,
)
from core.proyectos.selectors.proyectos_proyecto_selectors import (
    get_filtered_proyectos_queryset_for_user,
    get_proyectos_available_years_for_user,
)

# IMPORTANTE: Aquí importamos el resolver_estado_destino
from core.proyectos.services.proyectos_proyecto_services import (
    autores_payload_tiene_principal,
    normalize_proyecto_autores_payload,
    require_project_admin,
    sync_proyecto_autores,
    resolver_estado_destino,
)

class ProyectoPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ProyectoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = ProyectoPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "list":
            return ProyectoListSerializer
        return ProyectoSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q", "")
        anio = self.request.query_params.get("anio", "")
        estado = self.request.query_params.get("estado", "")

        return get_filtered_proyectos_queryset_for_user(
            self.request.user,
            q=q,
            anio=anio,
            estado=estado,
        )

    def perform_create(self, serializer):
        require_project_admin(self.request.user)
        serializer.save(creado_por=self.request.user)

    def perform_update(self, serializer):
        require_project_admin(self.request.user)
        serializer.save()

    def perform_destroy(self, instance):
        require_project_admin(self.request.user)
        instance.delete()

    def _limpiar_prefetch_cache(self, instance):
        if hasattr(instance, "_prefetched_objects_cache"):
            instance._prefetched_objects_cache = {}

    def _extraer_autores_payload(self, request):
        data = request.data

        if isinstance(data, list):
            return data

        autores_data = None

        if hasattr(data, "get"):
            autores_data = data.get("autores_data", None)

            if autores_data is None:
                autores_data = data.get("autores", None)

        if autores_data is None:
            raise ValidationError(
                {
                    "autores_data": (
                        "Debe enviar la lista de autores del proyecto."
                    )
                }
            )

        return autores_data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
                context={"request": request},
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            context={"request": request},
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="anios")
    def anios(self, request, *args, **kwargs):
        q = request.query_params.get("q", "")
        estado = request.query_params.get("estado", "")

        anios = get_proyectos_available_years_for_user(
            request.user,
            q=q,
            estado=estado,
        )

        return Response(anios, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "put", "patch"], url_path="autores")
    def autores(self, request, pk=None):
        proyecto = self.get_object()

        if request.method.lower() == "get":
            serializer = ProyectoAutorReadSerializer(
                proyecto.participaciones.all(),
                many=True,
                context={"request": request},
            )

            return Response(
                {
                    "autores": serializer.data,
                    "autores_total": proyecto.participaciones.count(),
                    "tiene_investigador_principal": proyecto.participaciones.filter(
                        rol="principal"
                    ).exists(),
                    "equipo_pendiente": not proyecto.participaciones.exists(),
                },
                status=status.HTTP_200_OK,
            )

        require_project_admin(request.user)

        raw_autores = self._extraer_autores_payload(request)
        autores_data = normalize_proyecto_autores_payload(raw_autores)

        if proyecto.estado == "cierre" and not autores_payload_tiene_principal(autores_data):
            raise ValidationError(
                {
                    "autores_data": (
                        "Un proyecto cerrado debe conservar al menos un investigador principal."
                    )
                }
            )

        sync_proyecto_autores(proyecto, autores_data)
        self._limpiar_prefetch_cache(proyecto)

        serializer = ProyectoSerializer(
            proyecto,
            context={"request": request},
        )

        return Response(
            {"proyecto": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="cambiar_estado")
    def cambiar_estado(self, request, pk=None):
        require_project_admin(request.user)

        proyecto = self.get_object()

        estado_solicitado = request.data.get("estado", "")
        
        # Lógica de transición delegada al servicio externo
        estado_destino = resolver_estado_destino(
            proyecto,
            estado_solicitado,
        )

        payload = {
            "estado": estado_destino,
        }

        if estado_destino == "cierre":
            payload["fecha_cierre"] = proyecto.fecha_cierre or timezone.now().date()
        else:
            payload["fecha_cierre"] = None

        serializer = ProyectoSerializer(
            proyecto,
            data=payload,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"proyecto": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="extender_fecha")
    def extender_fecha(self, request, pk=None):
        require_project_admin(request.user)

        proyecto = self.get_object()

        nueva_fecha = (
            request.data.get("fecha_fin_prorrogada")
            or request.data.get("fecha_fin")
            or request.data.get("nueva_fecha_fin")
        )

        if not nueva_fecha:
            raise ValidationError(
                {
                    "fecha_fin_prorrogada": (
                        "Debe indicar la nueva fecha de finalización."
                    )
                }
            )

        payload = {
            "fecha_fin_prorrogada": nueva_fecha,
            "estado": "arrastre",
            "fecha_cierre": None,
        }

        serializer = ProyectoSerializer(
            proyecto,
            data=payload,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"proyecto": serializer.data},
            status=status.HTTP_200_OK,
        )