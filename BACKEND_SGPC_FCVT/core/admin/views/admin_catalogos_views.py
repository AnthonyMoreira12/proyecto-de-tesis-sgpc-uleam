"""
Views administrativas para catálogos académicos.

Responsabilidad:
- Gestionar facultades y carreras desde administración.
- Exponer operaciones CRUD protegidas para catálogos académicos.
- Centralizar los endpoints administrativos que permiten crear, consultar,
  actualizar y eliminar facultades/carreras usando permisos de administrador.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Facultad, Carrera
from core.permisos.es_admin import EsAdmin
from core.admin.serializers.admin_catalogos_serializers import (
    AdminFacultadSerializer,
    AdminCarreraSerializer,
)


class AdminFacultadViewSet(viewsets.ModelViewSet):
    queryset = Facultad.objects.all().order_by("nombre")
    serializer_class = AdminFacultadSerializer
    permission_classes = [IsAuthenticated, EsAdmin]


class AdminCarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.select_related("facultad").all().order_by("nombre")
    serializer_class = AdminCarreraSerializer
    permission_classes = [IsAuthenticated, EsAdmin]