"""ViewSet administrativo de usuarios."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.admin.selectors.admin_usuarios_selectors import (
    admin_users_detail_queryset,
    admin_users_list_queryset,
    filter_admin_users_queryset,
)
from core.admin.serializers.admin_usuarios_serializers import (
    AdminUsuarioSerializer,
)
from core.admin.services.admin_usuarios_services import (
    AdminUsuariosServiceError,
    activate_external_user,
    block_profile_edit,
    enable_profile_edit,
    extend_profile_edit,
    parse_bool,
    validate_admin_guard,
)
from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario,
)
from core.models import Autor
from core.permisos.es_admin import EsAdmin


User = get_user_model()


class AdminUsuariosViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    serializer_class = AdminUsuarioSerializer
    queryset = admin_users_detail_queryset()

    def get_queryset(self):
        if self.action == "list":
            base = admin_users_list_queryset()
            params = self.request.query_params

            return filter_admin_users_queryset(
                base,
                q=params.get("q", ""),
                scope=params.get("scope", ""),
                incompletos=params.get("incompletos"),
            )

        return admin_users_detail_queryset()

    def _service_error_response(self, exc):
        return Response(exc.detail, status=exc.status_code)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        password = data.pop("password", None)

        data["rol"] = "autor_externo"
        data["auth_source"] = "local"
        data["carrera"] = None
        data.setdefault("is_active", True)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated = dict(serializer.validated_data)

        if not password:
            raise ValidationError(
                {"password": "La contraseña es obligatoria."}
            )

        provisional = User(**validated)

        try:
            validate_password(str(password), user=provisional)
        except DjangoValidationError as exc:
            raise ValidationError(
                {"password": list(exc.messages)}
            ) from exc

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    password=str(password),
                    **validated,
                )
                asegurar_autor_para_usuario(user)
        except IntegrityError as exc:
            raise ValidationError(
                {
                    "detail": (
                        "No se pudo crear el usuario por "
                        "un conflicto de unicidad."
                    )
                }
            ) from exc

        return Response(
            self.get_serializer(user).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        current = self.get_object()
        data = request.data.copy()

        for key in (
            "is_superuser",
            "rol",
            "auth_source",
            "facultad",
        ):
            data.pop(key, None)

        try:
            with transaction.atomic():
                locked = (
                    User.objects
                    .select_for_update()
                    .get(pk=current.pk)
                )

                if "is_active" in data:
                    new_active = parse_bool(data["is_active"])
                    validate_admin_guard(
                        locked,
                        request.user,
                        new_is_active=new_active,
                    )
                    data["is_active"] = new_active

                if "is_staff" in data:
                    new_staff = parse_bool(data["is_staff"])
                    validate_admin_guard(
                        locked,
                        request.user,
                        new_is_staff=new_staff,
                    )
                    data["is_staff"] = new_staff

                serializer = self.get_serializer(
                    locked,
                    data=data,
                    partial=kwargs.pop("partial", False),
                )
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                asegurar_autor_para_usuario(user)

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        return Response(self.get_serializer(user).data)

    def destroy(self, request, *args, **kwargs):
        current = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(pk=current.pk)
                )

                validate_admin_guard(
                    user,
                    request.user,
                    new_is_active=False,
                    new_is_staff=False,
                )

                author = (
                    Autor.objects
                    .select_for_update()
                    .filter(usuario=user)
                    .first()
                )

                if author and author.participaciones.exists():
                    author.usuario = None
                    author.save(update_fields=["usuario"])

                user.delete()

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)
        except (ProtectedError, IntegrityError):
            return Response(
                {
                    "detail": (
                        "No se puede eliminar el usuario "
                        "porque mantiene registros relacionados."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="activar")
    def activar(self, request, pk=None):
        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(pk=self.get_object().pk)
                )
                fields = activate_external_user(
                    user,
                    email=request.data.get("email"),
                    password=request.data.get("password"),
                )
                user.save(update_fields=fields)
                asegurar_autor_para_usuario(user)

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        return Response(self.get_serializer(user).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="habilitar-edicion-perfil",
    )
    def habilitar_edicion_perfil(self, request, pk=None):
        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(pk=self.get_object().pk)
                )
                fields = enable_profile_edit(
                    user,
                    hours=request.data.get("horas", 48),
                    attempts=request.data.get("intentos", 3),
                )
                user.save(update_fields=fields)

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        return Response(self.get_serializer(user).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="extender-edicion-perfil",
    )
    def extender_edicion_perfil(self, request, pk=None):
        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(pk=self.get_object().pk)
                )
                fields = extend_profile_edit(
                    user,
                    hours=request.data.get("horas", 24),
                )
                user.save(update_fields=fields)

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        return Response(self.get_serializer(user).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="bloquear-edicion-perfil",
    )
    def bloquear_edicion_perfil(self, request, pk=None):
        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(pk=self.get_object().pk)
                )
                fields = block_profile_edit(
                    user,
                    reason=request.data.get("reason"),
                )
                user.save(update_fields=fields)

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=["post"], url_path="toggle-activo")
    def toggle_activo(self, request, pk=None):
        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(pk=self.get_object().pk)
                )
                new_state = not user.is_active

                validate_admin_guard(
                    user,
                    request.user,
                    new_is_active=new_state,
                )

                user.is_active = new_state
                user.save(update_fields=["is_active"])

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=["post"], url_path="promover-admin")
    def promover_admin(self, request, pk=None):
        with transaction.atomic():
            user = (
                User.objects
                .select_for_update()
                .get(pk=self.get_object().pk)
            )

            if user.is_superuser:
                raise ValidationError(
                    {"detail": "El usuario ya es superusuario."}
                )

            user.is_staff = True
            user.save(update_fields=["is_staff"])

        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=["post"], url_path="revocar-admin")
    def revocar_admin(self, request, pk=None):
        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(pk=self.get_object().pk)
                )

                validate_admin_guard(
                    user,
                    request.user,
                    new_is_staff=False,
                )

                user.is_staff = False
                user.save(update_fields=["is_staff"])

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        return Response(self.get_serializer(user).data)

    @action(
        detail=False,
        methods=["get"],
        url_path="buscar-microsoft",
    )
    def buscar_microsoft(self, request):
        query = str(request.query_params.get("q", "")).strip()
        queryset = admin_users_list_queryset().filter(
            auth_source="microsoft"
        )

        if query:
            queryset = filter_admin_users_queryset(
                queryset,
                q=query,
            )

        return Response(
            self.get_serializer(queryset[:25], many=True).data
        )


# Compatibilidad con imports previos en singular.
AdminUsuarioViewSet = AdminUsuariosViewSet
