from django.db import transaction
from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Autor
from core.autores.serializers.autores_autor_serializers import AutorSerializer
from core.autores.services.autores_usuario_sync_services import (
    AutorUsuarioSyncError,
    asegurar_usuario_pendiente_para_autor,
    buscar_autor_existente,
    serializar_autor_match,
)


class AutoresViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AutorSerializer
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = (
            Autor.objects
            .select_related("usuario")
            .all()
            .order_by("apellidos", "nombres", "id")
        )

        q = (
            self.request.query_params.get("q")
            or self.request.query_params.get("search")
            or ""
        ).strip()

        if q:
            qs = qs.filter(
                Q(nombres__icontains=q)
                | Q(apellidos__icontains=q)
                | Q(identificacion__icontains=q)
                | Q(correo__icontains=q)
                | Q(institucion__icontains=q)
                | Q(usuario__email__icontains=q)
            )

        return qs.order_by("apellidos", "nombres", "id")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        autor = serializer.save(es_externo=True, usuario=None)

        try:
            asegurar_usuario_pendiente_para_autor(autor)
        except AutorUsuarioSyncError as exc:
            raise ValidationError(exc.detail)

        autor.refresh_from_db()
        response_serializer = self.get_serializer(autor)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        autor = serializer.save()

        if bool(getattr(autor, "es_externo", False)):
            try:
                asegurar_usuario_pendiente_para_autor(autor)
            except AutorUsuarioSyncError as exc:
                raise ValidationError(exc.detail)

        autor.refresh_from_db()
        response_serializer = self.get_serializer(autor)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="validar-existencia")
    def validar_existencia(self, request):
        identificacion = request.query_params.get("identificacion")
        correo = request.query_params.get("correo")
        nombres = request.query_params.get("nombres")
        apellidos = request.query_params.get("apellidos")

        found = buscar_autor_existente(
            identificacion=identificacion,
            correo=correo,
            nombres=nombres,
            apellidos=apellidos,
        )

        return Response(
            serializar_autor_match(found["autor"], found["match_type"]),
            status=status.HTTP_200_OK,
        )