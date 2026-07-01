# ViewSet administrativo de usuarios:
# permite crear, listar, actualizar, activar, eliminar y administrar usuarios del sistema,
# incluyendo control de acceso admin, usuarios externos, edición de perfil y sincronización con autores.

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permisos.es_admin import EsAdmin
from core.admin.serializers.admin_usuarios_serializers import AdminUsuarioSerializer
from core.admin.selectors.admin_usuarios_selectors import (
    admin_users_base_queryset,
    active_admins_qs,
    filter_admin_users_queryset,
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
from core.autores.services.autores_usuario_sync_services import asegurar_autor_para_usuario
# Importación necesaria para la corrección
from core.auth.services.auth_microsoft_services import obtener_usuario_microsoft_por_id

User = get_user_model()


class AdminUsuariosViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUsuarioSerializer
    permission_classes = [IsAuthenticated, EsAdmin]
    queryset = admin_users_base_queryset()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def _service_error_response(self, exc):
        return Response(exc.detail, status=exc.status_code)

    def _safe_get_autor(self, usuario):
        try:
            return usuario.autor
        except Exception:
            return None

    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        incompletos = (
            (self.request.query_params.get("incompletos") or "").strip().lower()
            in ("1", "true", "yes")
        )
        scope = (self.request.query_params.get("scope") or "").strip().lower()

        return filter_admin_users_queryset(
            admin_users_base_queryset(),
            q=q,
            scope=scope,
            incompletos=incompletos,
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        email = (str(data.get("email") or "")).strip().lower()
        data["email"] = email

        if (str(data.get("auth_source") or "")).strip().lower() == "microsoft":
            return Response(
                {
                    "detail": (
                        "Los usuarios institucionales se registran "
                        "automáticamente al iniciar sesión con Microsoft."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data["rol"] = "autor_externo"
        data["auth_source"] = "local"
        data["is_active"] = False
        data["is_staff"] = False
        data["perfil_completo"] = False
        data["creado_desde_selector"] = False

        data.pop("facultad", None)
        data.pop("carrera", None)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"email": "Ya existe un usuario con este correo."},
                status=status.HTTP_409_CONFLICT,
            )

        ident = serializer.validated_data.get("identificacion")
        if ident and User.objects.filter(identificacion=ident).exists():
            return Response(
                {"identificacion": "Esta identificación ya está registrada."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            user = User.objects.create_user(password=None, **serializer.validated_data)
            asegurar_autor_para_usuario(user)
        except IntegrityError:
            return Response(
                {"detail": "No se pudo crear el usuario por conflicto de unicidad."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            self.get_serializer(user).data,
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        try:
            if "is_staff_set" in data or "is_staff" in data:
                raw = data.get("is_staff_set", data.get("is_staff"))
                parsed = parse_bool(raw)

                if parsed is None:
                    return Response(
                        {"is_staff": "Valor inválido. Use true/false."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                validate_admin_guard(instance, request.user, new_is_staff=parsed)
                data["is_staff"] = parsed
                data.pop("is_staff_set", None)

            if "is_active_set" in data or "is_active" in data:
                raw = data.get("is_active_set", data.get("is_active"))
                parsed = parse_bool(raw)

                if parsed is None:
                    return Response(
                        {"is_active": "Valor inválido. Use true/false."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                validate_admin_guard(instance, request.user, new_is_active=parsed)
                data["is_active"] = parsed
                data.pop("is_active_set", None)

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        if "email" in data:
            data["email"] = (str(data.get("email") or "")).strip().lower()

        if "identificacion" in data:
            raw_ident = data.get("identificacion")

            if raw_ident in (None, "", "null"):
                data["identificacion"] = None
            else:
                data["identificacion"] = str(raw_ident).strip()

        is_externo = (
            str(getattr(instance, "rol", "")).lower() == "autor_externo"
            and str(getattr(instance, "auth_source", "")).lower() == "local"
        )

        if is_externo:
            data.pop("facultad", None)
            data.pop("carrera", None)

        data.pop("auth_source", None)
        data.pop("rol", None)
        data.pop("is_superuser", None)
        data.pop("creado_desde_selector", None)

        new_email = data.get("email", None)
        if new_email and User.objects.filter(email__iexact=new_email).exclude(pk=instance.pk).exists():
            return Response(
                {"email": "Ya existe un usuario con este correo."},
                status=status.HTTP_409_CONFLICT,
            )

        new_ident = data.get("identificacion", None)
        if new_ident and User.objects.filter(identificacion=new_ident).exclude(pk=instance.pk).exists():
            return Response(
                {"identificacion": "Esta identificación ya está registrada."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_update(serializer)
            asegurar_autor_para_usuario(serializer.instance)
        except IntegrityError:
            return Response(
                {"detail": "No se pudo actualizar el usuario por conflicto de unicidad."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()

        if usuario.pk == getattr(request.user, "pk", None):
            return Response(
                {"detail": "No puedes eliminar tu propio usuario desde este módulo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if getattr(usuario, "is_superuser", False):
            return Response(
                {"detail": "No se puede eliminar un superusuario desde este módulo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if bool(usuario.is_staff) and bool(usuario.is_active):
            if not active_admins_qs().exclude(pk=usuario.pk).exists():
                return Response(
                    {"detail": "No se puede eliminar al último administrador activo del sistema."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        autor_vinculado = self._safe_get_autor(usuario)

        try:
            usuario.delete()

            if autor_vinculado:
                tiene_publicaciones = autor_vinculado.participaciones.exists()

                if not tiene_publicaciones:
                    autor_vinculado.delete()
                else:
                    if autor_vinculado.usuario_id is not None:
                        autor_vinculado.usuario = None
                        autor_vinculado.save(update_fields=["usuario"])

        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "No se puede eliminar este usuario porque tiene registros "
                        "asociados en el sistema."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )
        except IntegrityError:
            return Response(
                {"detail": "No se pudo eliminar el usuario por restricciones de integridad."},
                status=status.HTTP_409_CONFLICT,
            )
        except Exception as exc:
            return Response(
                {
                    "detail": (
                        "Ocurrió un error inesperado al eliminar el usuario: "
                        f"{str(exc)}"
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="activar")
    @transaction.atomic
    def activar(self, request, pk=None):
        user = self.get_object()

        email = request.data.get("email", None)
        raw_password = request.data.get("password", "")

        try:
            update_fields = activate_external_user(
                user,
                email=email,
                password=raw_password,
            )
        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        if email is not None:
            normalized_email = str(email).strip().lower()
            if User.objects.filter(email__iexact=normalized_email).exclude(pk=user.pk).exists():
                return Response(
                    {"email": "Ya existe un usuario con este correo."},
                    status=status.HTTP_409_CONFLICT,
                )

        try:
            user.save(update_fields=update_fields)
            asegurar_autor_para_usuario(user)
        except IntegrityError:
            return Response(
                {"detail": "No se pudo activar el usuario por conflicto de unicidad."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            self.get_serializer(user).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="habilitar-edicion-perfil")
    @transaction.atomic
    def habilitar_edicion_perfil(self, request, pk=None):
        usuario = self.get_object()

        try:
            update_fields = enable_profile_edit(usuario, hours=48, attempts=3)
        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        usuario.save(update_fields=update_fields)
        return Response(self.get_serializer(usuario).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="extender-edicion-perfil")
    @transaction.atomic
    def extender_edicion_perfil(self, request, pk=None):
        usuario = self.get_object()
        horas = request.data.get("horas", 24)

        try:
            update_fields = extend_profile_edit(usuario, hours=horas)
        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        usuario.save(update_fields=update_fields)
        return Response(self.get_serializer(usuario).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="bloquear-edicion-perfil")
    @transaction.atomic
    def bloquear_edicion_perfil(self, request, pk=None):
        usuario = self.get_object()
        reason = request.data.get("reason", None)

        try:
            update_fields = block_profile_edit(usuario, reason=reason)
        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        usuario.save(update_fields=update_fields)
        return Response(self.get_serializer(usuario).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="toggle-activo")
    @transaction.atomic
    def toggle_activo(self, request, pk=None):
        usuario = self.get_object()
        nuevo_estado = not usuario.is_active

        try:
            validate_admin_guard(usuario, request.user, new_is_active=nuevo_estado)
        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        usuario.is_active = nuevo_estado
        usuario.save(update_fields=["is_active"])
        asegurar_autor_para_usuario(usuario)

        return Response(self.get_serializer(usuario).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="promover-admin")
    @transaction.atomic
    def promover_admin(self, request, pk=None):
        usuario = self.get_object()

        if getattr(usuario, "is_superuser", False):
            return Response(
                {"detail": "El usuario ya es superusuario."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if usuario.pk == getattr(request.user, "pk", None):
            return Response(
                {"detail": "No puedes modificar tu propio acceso administrativo desde este endpoint."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.is_staff = True
        usuario.save(update_fields=["is_staff"])

        return Response(self.get_serializer(usuario).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="revocar-admin")
    @transaction.atomic
    def revocar_admin(self, request, pk=None):
        usuario = self.get_object()

        if getattr(usuario, "is_superuser", False):
            return Response(
                {"detail": "No se puede revocar permisos a un superusuario."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_admin_guard(usuario, request.user, new_is_staff=False)
        except AdminUsuariosServiceError as exc:
            return self._service_error_response(exc)

        usuario.is_staff = False
        usuario.save(update_fields=["is_staff"])

        return Response(self.get_serializer(usuario).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="buscar-microsoft")
    def buscar_microsoft(self, request):
        """
        Busca un usuario directamente en Microsoft Entra ID usando su Object ID.
        """
        ms_id = request.query_params.get("ms_id")
        
        if not ms_id:
            return Response(
                {"detail": "Debe enviar el parámetro 'ms_id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = obtener_usuario_microsoft_por_id(ms_id)

        if not data or data.get("_error"):
            return Response(
                {
                    "detail": "No se pudo encontrar el usuario en Microsoft.",
                    "meta": data
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(data, status=status.HTTP_200_OK)