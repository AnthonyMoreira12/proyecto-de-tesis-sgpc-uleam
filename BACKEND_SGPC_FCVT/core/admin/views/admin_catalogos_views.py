"""Views administrativas para catálogos académicos."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.admin.serializers.admin_catalogos_serializers import (
    AdminCarreraSerializer,
    AdminFacultadSerializer,
)
from core.models import Carrera, Facultad
from core.permisos.es_admin import EsAdmin


class _SafeCatalogMixin:
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, EsAdmin]

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().create(request, *args, **kwargs)
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(
                    exc,
                    "message_dict",
                    {"detail": exc.messages},
                )
            ) from exc
        except IntegrityError:
            return Response(
                {
                    "detail": (
                        "El registro entra en conflicto "
                        "con otro existente."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().update(request, *args, **kwargs)
        except DjangoValidationError as exc:
            raise ValidationError(
                getattr(
                    exc,
                    "message_dict",
                    {"detail": exc.messages},
                )
            ) from exc
        except IntegrityError:
            return Response(
                {
                    "detail": (
                        "El registro entra en conflicto "
                        "con otro existente."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return super().destroy(request, *args, **kwargs)
        except (ProtectedError, IntegrityError):
            return Response(
                {
                    "detail": (
                        "No se puede eliminar porque mantiene "
                        "información relacionada."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )


class AdminFacultadViewSet(
    _SafeCatalogMixin,
    viewsets.ModelViewSet,
):
    serializer_class = AdminFacultadSerializer
    queryset = Facultad.objects.all().order_by("nombre", "id")

    def get_queryset(self):
        queryset = Facultad.objects.all()

        if self.action != "list":
            return queryset

        query = str(
            self.request.query_params.get("q", "")
        ).strip()

        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query)
                | Q(siglas__icontains=query)
            )

        return queryset.order_by("nombre", "id")


class AdminCarreraViewSet(
    _SafeCatalogMixin,
    viewsets.ModelViewSet,
):
    serializer_class = AdminCarreraSerializer
    queryset = (
        Carrera.objects
        .select_related("facultad")
        .order_by("nombre", "id")
    )

    def get_queryset(self):
        queryset = Carrera.objects.select_related("facultad")

        if self.action != "list":
            return queryset

        params = self.request.query_params
        query = str(params.get("q", "")).strip()
        faculty_id = (
            params.get("facultad_id")
            or params.get("facultad")
        )

        if faculty_id not in (None, ""):
            try:
                faculty_id = int(faculty_id)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValidationError(
                    {"facultad_id": "Debe ser un entero positivo."}
                ) from exc

            if faculty_id <= 0:
                raise ValidationError(
                    {"facultad_id": "Debe ser un entero positivo."}
                )

            queryset = queryset.filter(facultad_id=faculty_id)

        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query)
                | Q(facultad__nombre__icontains=query)
                | Q(facultad__siglas__icontains=query)
            )

        return queryset.order_by("nombre", "id")
