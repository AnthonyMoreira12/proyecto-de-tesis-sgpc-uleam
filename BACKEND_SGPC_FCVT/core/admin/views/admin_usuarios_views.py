"""ViewSet administrativo de usuarios."""

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

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
from core.models import Autor, Sede
from core.permisos.es_admin import EsAdmin


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLE_INSTITUTIONAL = "autor"
ROLE_EXTERNAL = "autor_externo"

AUTH_SOURCE_LOCAL = "local"
AUTH_SOURCE_MICROSOFT = "microsoft"

DEFAULT_PROFILE_EDIT_HOURS = 48
DEFAULT_PROFILE_EDIT_ATTEMPTS = 3


# ============================================================
# UTILIDADES
# ============================================================

def _text(value):
    """
    Normaliza un valor textual.
    """
    return str(value or "").strip()


def _normalized_role(user):
    """
    Retorna el rol normalizado de un usuario.
    """
    return _text(
        getattr(
            user,
            "rol",
            "",
        )
    ).lower()


def _normalized_auth_source(user):
    """
    Retorna el origen de autenticación normalizado.
    """
    return _text(
        getattr(
            user,
            "auth_source",
            "",
        )
    ).lower()


def _is_external_user(user):
    """
    Comprueba que la cuenta sea realmente externa local.
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user) == ROLE_EXTERNAL
        and _normalized_auth_source(user)
        == AUTH_SOURCE_LOCAL
    )


def _is_institutional_user(user):
    """
    Comprueba que la cuenta sea realmente institucional
    Microsoft.
    """
    if user is None:
        return False

    return bool(
        _normalized_role(user)
        == ROLE_INSTITUTIONAL
        and _normalized_auth_source(user)
        == AUTH_SOURCE_MICROSOFT
    )


def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura
    compatible con Django REST Framework.
    """
    if hasattr(exc, "message_dict"):
        return exc.message_dict

    if hasattr(exc, "messages"):
        return {
            "detail": list(exc.messages),
        }

    return {
        "detail": str(exc),
    }


def _unique_fields(fields):
    """
    Elimina duplicados conservando el orden.
    """
    return list(
        dict.fromkeys(
            field
            for field in fields
            if field
        )
    )


def _positive_optional_id(
    value,
    *,
    field_name,
):
    """
    Convierte un valor opcional en identificador entero positivo.
    """
    if value in (
        None,
        "",
        "null",
        "None",
    ):
        return None

    if isinstance(value, bool):
        raise ValidationError(
            {
                field_name: (
                    "El identificador seleccionado "
                    "no es válido."
                )
            }
        )

    try:
        parsed = int(value)

    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise ValidationError(
            {
                field_name: (
                    "El identificador seleccionado "
                    "debe ser numérico."
                )
            }
        ) from exc

    if parsed <= 0:
        raise ValidationError(
            {
                field_name: (
                    "El identificador seleccionado "
                    "no es válido."
                )
            }
        )

    return parsed


def _request_field(
    request,
    field_name,
    default=None,
):
    """
    Obtiene un campo del request de manera compatible con
    diccionarios y QueryDict.
    """
    if field_name not in request.data:
        return default

    return request.data.get(
        field_name,
        default,
    )


# ============================================================
# VIEWSET
# ============================================================

class AdminUsuariosViewSet(
    viewsets.ModelViewSet
):
    """
    Administración de usuarios del SGPC ULEAM.

    La creación administrativa registra exclusivamente usuarios
    externos locales pendientes.

    Los usuarios institucionales se originan mediante Microsoft
    365 y únicamente pueden recibir una asignación académica
    interna desde este panel.
    """

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        permissions.IsAuthenticated,
        EsAdmin,
    ]

    serializer_class = (
        AdminUsuarioSerializer
    )

    queryset = (
        admin_users_detail_queryset()
    )

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self):
        if self.action == "list":
            base_queryset = (
                admin_users_list_queryset()
            )

            params = self.request.query_params

            return filter_admin_users_queryset(
                base_queryset,
                q=params.get(
                    "q",
                    "",
                ),
                scope=params.get(
                    "scope",
                    "",
                ),
                incompletos=params.get(
                    "incompletos"
                ),
            )

        return admin_users_detail_queryset()

    # ========================================================
    # RESPUESTAS
    # ========================================================

    def _service_error_response(
        self,
        exc,
    ):
        return Response(
            exc.detail,
            status=exc.status_code,
        )

    def _get_refreshed_user(
        self,
        user_id,
    ):
        """
        Recupera nuevamente el usuario con todas las relaciones
        requeridas por el serializer administrativo.
        """
        return (
            admin_users_detail_queryset()
            .filter(
                pk=user_id
            )
            .first()
        )

    def _user_response(
        self,
        user,
        *,
        response_status=status.HTTP_200_OK,
    ):
        """
        Construye una respuesta utilizando información actualizada
        desde la base de datos.
        """
        refreshed_user = (
            self._get_refreshed_user(
                user.pk
            )
            or user
        )

        return Response(
            self.get_serializer(
                refreshed_user
            ).data,
            status=response_status,
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
        Registra una cuenta externa pendiente.

        La cuenta:

        - Se crea inactiva.
        - Se crea sin contraseña utilizable.
        - No recibe Carrera.
        - No recibe permisos administrativos.
        - Debe activarse posteriormente desde la acción activar.
        """
        data = {
            "email": _request_field(
                request,
                "email",
                "",
            ),
            "nombres": _request_field(
                request,
                "nombres",
                "",
            ),
            "apellidos": _request_field(
                request,
                "apellidos",
                "",
            ),
            "identificacion": (
                _request_field(
                    request,
                    "identificacion",
                    None,
                )
            ),

            # Valores controlados exclusivamente por backend.
            "rol": ROLE_EXTERNAL,
            "auth_source": AUTH_SOURCE_LOCAL,
            "sede": None,
            "carrera": None,
            "is_active": False,
            "is_staff": False,
        }

        serializer = self.get_serializer(
            data=data
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = dict(
            serializer.validated_data
        )

        # Se vuelven a forzar los valores sensibles después de
        # la validación para impedir modificaciones del cliente.
        validated_data["rol"] = (
            ROLE_EXTERNAL
        )

        validated_data["auth_source"] = (
            AUTH_SOURCE_LOCAL
        )

        validated_data["sede"] = None
        validated_data["carrera"] = None
        validated_data["is_active"] = False
        validated_data["is_staff"] = False
        validated_data["is_superuser"] = False

        validated_data[
            "creado_desde_selector"
        ] = False

        validated_data["perfil_completo"] = True

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    password=None,
                    **validated_data,
                )

                author = (
                    asegurar_autor_para_usuario(
                        user
                    )
                )

                if author is None:
                    raise ValidationError(
                        {
                            "detail": (
                                "El usuario fue creado, pero "
                                "no fue posible generar su "
                                "registro de autor."
                            )
                        }
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
                        "No se pudo crear el usuario "
                        "porque existe información duplicada."
                    )
                }
            ) from exc

        return self._user_response(
            user,
            response_status=(
                status.HTTP_201_CREATED
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
        """
        Actualiza campos administrativos permitidos.

        No permite modificar:

        - rol
        - auth_source
        - is_superuser
        - perfil_completo
        - clasificación externa o institucional
        """
        current_user = self.get_object()

        partial = kwargs.pop(
            "partial",
            False,
        )

        allowed_fields = {
            "nombres",
            "apellidos",
            "email",
            "identificacion",
            "sede",
            "carrera",
            "facultad",
            "is_active",
            "is_staff",
        }

        data = {
            field_name: request.data.get(
                field_name
            )
            for field_name in allowed_fields
            if field_name in request.data
        }

        # Compatibilidad temporal con versiones anteriores del
        # frontend que enviaban is_staff_set.
        if (
            "is_staff" not in data
            and "is_staff_set"
            in request.data
        ):
            data["is_staff"] = (
                request.data.get(
                    "is_staff_set"
                )
            )

        faculty_was_sent = (
            "facultad"
            in data
        )

        selected_faculty_value = data.pop(
            "facultad",
            None,
        )

        try:
            with transaction.atomic():
                locked_user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
                )

                # El correo institucional proviene de Microsoft
                # y no puede alterarse desde este endpoint.
                if _is_institutional_user(
                    locked_user
                ):
                    data.pop(
                        "email",
                        None,
                    )

                if "is_active" in data:
                    new_is_active = parse_bool(
                        data[
                            "is_active"
                        ]
                    )

                    validate_admin_guard(
                        locked_user,
                        request.user,
                        new_is_active=(
                            new_is_active
                        ),
                    )

                    data["is_active"] = (
                        new_is_active
                    )

                if "is_staff" in data:
                    new_is_staff = parse_bool(
                        data[
                            "is_staff"
                        ]
                    )

                    validate_admin_guard(
                        locked_user,
                        request.user,
                        new_is_staff=(
                            new_is_staff
                        ),
                    )

                    data["is_staff"] = (
                        new_is_staff
                    )

                serializer = self.get_serializer(
                    locked_user,
                    data=data,
                    partial=partial,
                )

                serializer.is_valid(
                    raise_exception=True
                )

                validated_site = serializer.validated_data.get(
                    "sede", getattr(locked_user, "sede", None)
                )
                validated_career = serializer.validated_data.get(
                    "carrera", getattr(locked_user, "carrera", None)
                )

                if _is_institutional_user(locked_user):
                    if validated_site is not None and not validated_site.activa:
                        raise ValidationError({"sede": "La sede seleccionada está inactiva."})
                    if validated_site is not None and validated_career is not None:
                        if not validated_career.sedes_carrera.filter(
                            sede_id=validated_site.pk, activa=True
                        ).exists():
                            raise ValidationError({
                                "carrera": "La carrera seleccionada no está habilitada en la sede indicada."
                            })
                else:
                    serializer.validated_data["sede"] = None
                    serializer.validated_data["carrera"] = None

                if faculty_was_sent:
                    selected_faculty_id = (
                        _positive_optional_id(
                            selected_faculty_value,
                            field_name="facultad",
                        )
                    )

                    validated_career = (
                        serializer.validated_data.get(
                            "carrera",
                            getattr(
                                locked_user,
                                "carrera",
                                None,
                            ),
                        )
                    )

                    if (
                        selected_faculty_id
                        is not None
                        and validated_career
                        is None
                    ):
                        raise ValidationError(
                            {
                                "carrera": (
                                    "Seleccione una carrera "
                                    "perteneciente a la Facultad "
                                    "indicada."
                                )
                            }
                        )

                    if (
                        validated_career
                        is not None
                        and selected_faculty_id
                        is not None
                        and validated_career.facultad_id
                        != selected_faculty_id
                    ):
                        raise ValidationError(
                            {
                                "carrera": (
                                    "La carrera seleccionada "
                                    "no pertenece a la Facultad "
                                    "indicada."
                                )
                            }
                        )

                user = serializer.save()

                author = (
                    asegurar_autor_para_usuario(
                        user
                    )
                )

                if author is None:
                    raise ValidationError(
                        {
                            "detail": (
                                "Los datos fueron procesados, "
                                "pero no fue posible sincronizar "
                                "el registro del autor."
                            )
                        }
                    )

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(
                exc
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
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
                        "No se pudo actualizar el usuario "
                        "porque los datos entran en conflicto "
                        "con otro registro."
                    )
                }
            ) from exc

        return self._user_response(
            user
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
        current_user = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
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
                    .filter(
                        usuario=user
                    )
                    .first()
                )

                if author is not None:
                    has_related_records = bool(
                        author.participaciones.exists()
                        or author.proyectos_participaciones.exists()
                    )

                    # Se conserva el Autor cuando participa en
                    # publicaciones o proyectos. Si no mantiene
                    # registros científicos, se elimina para no
                    # dejar un Autor huérfano con correo o cédula
                    # reservados por sus restricciones únicas.
                    if has_related_records:
                        author.usuario = None
                        author.save(
                            update_fields=[
                                "usuario",
                            ]
                        )
                    else:
                        author.delete()

                user.delete()

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(
                exc
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        except (
            ProtectedError,
            IntegrityError,
        ):
            return Response(
                {
                    "detail": (
                        "No se puede eliminar el usuario "
                        "porque mantiene registros relacionados."
                    )
                },
                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    # ========================================================
    # ACTIVAR CUENTA EXTERNA
    # ========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="activar",
    )
    def activar(
        self,
        request,
        pk=None,
    ):
        """
        Activa una cuenta externa pendiente.

        La contraseña y el correo son obligatorios. Además, el
        periodo de edición comienza nuevamente desde la fecha
        de activación.
        """
        current_user = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
                )

                update_fields = (
                    activate_external_user(
                        user,
                        email=request.data.get(
                            "email"
                        ),
                        password=request.data.get(
                            "password"
                        ),
                    )
                )

                profile_fields = (
                    enable_profile_edit(
                        user,
                        hours=(
                            DEFAULT_PROFILE_EDIT_HOURS
                        ),
                        attempts=(
                            DEFAULT_PROFILE_EDIT_ATTEMPTS
                        ),
                    )
                )

                update_fields.extend(
                    profile_fields
                )

                user.save(
                    update_fields=(
                        _unique_fields(
                            update_fields
                        )
                    )
                )

                author = (
                    asegurar_autor_para_usuario(
                        user
                    )
                )

                if author is None:
                    raise ValidationError(
                        {
                            "detail": (
                                "La cuenta fue activada, pero "
                                "no fue posible sincronizar "
                                "el registro del autor."
                            )
                        }
                    )

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(
                exc
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
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
                        "No se pudo activar la cuenta "
                        "porque el correo o la cédula "
                        "ya pertenecen a otro usuario."
                    )
                }
            ) from exc

        return self._user_response(
            user
        )

    # ========================================================
    # HABILITAR EDICIÓN DEL PERFIL
    # ========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="habilitar-edicion-perfil",
    )
    def habilitar_edicion_perfil(
        self,
        request,
        pk=None,
    ):
        current_user = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
                )

                update_fields = enable_profile_edit(
                    user,
                    hours=request.data.get(
                        "horas",
                        DEFAULT_PROFILE_EDIT_HOURS,
                    ),
                    attempts=request.data.get(
                        "intentos",
                        DEFAULT_PROFILE_EDIT_ATTEMPTS,
                    ),
                )

                user.save(
                    update_fields=(
                        _unique_fields(
                            update_fields
                        )
                    )
                )

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(
                exc
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return self._user_response(
            user
        )

    # ========================================================
    # EXTENDER EDICIÓN DEL PERFIL
    # ========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="extender-edicion-perfil",
    )
    def extender_edicion_perfil(
        self,
        request,
        pk=None,
    ):
        current_user = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
                )

                update_fields = extend_profile_edit(
                    user,
                    hours=request.data.get(
                        "horas",
                        24,
                    ),
                )

                user.save(
                    update_fields=(
                        _unique_fields(
                            update_fields
                        )
                    )
                )

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(
                exc
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return self._user_response(
            user
        )

    # ========================================================
    # BLOQUEAR EDICIÓN DEL PERFIL
    # ========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="bloquear-edicion-perfil",
    )
    def bloquear_edicion_perfil(
        self,
        request,
        pk=None,
    ):
        current_user = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
                )

                update_fields = block_profile_edit(
                    user,
                    reason=request.data.get(
                        "reason"
                    ),
                )

                user.save(
                    update_fields=(
                        _unique_fields(
                            update_fields
                        )
                    )
                )

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(
                exc
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return self._user_response(
            user
        )

    # ========================================================
    # CAMBIAR ESTADO ACTIVO
    # ========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="toggle-activo",
    )
    def toggle_activo(
        self,
        request,
        pk=None,
    ):
        current_user = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
                )

                new_state = not bool(
                    user.is_active
                )

                # Una cuenta externa pendiente sin contraseña no
                # puede activarse saltándose el flujo seguro.
                if (
                    new_state
                    and _is_external_user(
                        user
                    )
                    and not user.has_usable_password()
                ):
                    raise AdminUsuariosServiceError(
                        {
                            "detail": (
                                "La cuenta externa todavía no "
                                "tiene una contraseña. Utilice "
                                "la acción «Activar cuenta»."
                            )
                        },
                        status_code=409,
                    )

                validate_admin_guard(
                    user,
                    request.user,
                    new_is_active=new_state,
                )

                user.is_active = new_state

                user.save(
                    update_fields=[
                        "is_active",
                    ]
                )

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(
                exc
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return self._user_response(
            user
        )

    # ========================================================
    # PROMOVER ADMINISTRADOR
    # ========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="promover-admin",
    )
    def promover_admin(
        self,
        request,
        pk=None,
    ):
        current_user = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
                )

                if user.is_superuser:
                    raise ValidationError(
                        {
                            "detail": (
                                "El usuario ya es "
                                "superusuario."
                            )
                        }
                    )

                if not user.is_staff:
                    user.is_staff = True

                    user.save(
                        update_fields=[
                            "is_staff",
                        ]
                    )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return self._user_response(
            user
        )

    # ========================================================
    # REVOCAR ADMINISTRADOR
    # ========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="revocar-admin",
    )
    def revocar_admin(
        self,
        request,
        pk=None,
    ):
        current_user = self.get_object()

        try:
            with transaction.atomic():
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        pk=current_user.pk
                    )
                )

                validate_admin_guard(
                    user,
                    request.user,
                    new_is_staff=False,
                )

                if user.is_staff:
                    user.is_staff = False

                    user.save(
                        update_fields=[
                            "is_staff",
                        ]
                    )

        except AdminUsuariosServiceError as exc:
            return self._service_error_response(
                exc
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": (
                        "El usuario seleccionado "
                        "ya no existe."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return self._user_response(
            user
        )

    # ========================================================
    # BÚSQUEDA MICROSOFT
    # ========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="buscar-microsoft",
    )
    def buscar_microsoft(
        self,
        request,
    ):
        query = _text(
            request.query_params.get(
                "q",
                "",
            )
        )

        queryset = (
            admin_users_list_queryset()
            .filter(
                auth_source=(
                    AUTH_SOURCE_MICROSOFT
                ),
                rol=ROLE_INSTITUTIONAL,
            )
        )

        if query:
            queryset = (
                filter_admin_users_queryset(
                    queryset,
                    q=query,
                )
            )

        return Response(
            self.get_serializer(
                queryset[:25],
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )


# Compatibilidad con imports previos en singular.
AdminUsuarioViewSet = AdminUsuariosViewSet
