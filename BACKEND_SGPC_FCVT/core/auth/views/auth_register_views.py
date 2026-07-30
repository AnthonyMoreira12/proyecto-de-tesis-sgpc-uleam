"""
View para el registro público de usuarios externos.

La operación garantiza que:

- El usuario se cree como autor externo local.
- La cédula tenga exactamente 10 dígitos.
- La cuenta no reciba Carrera.
- La cuenta no reciba permisos administrativos.
- El registro Autor asociado se cree o sincronice.
- Usuario y Autor se guarden dentro de una misma transacción.
- Los tokens JWT se generen después de confirmar el registro.
- No se devuelvan tokens cuando el proceso quede incompleto.
"""

import re

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction

from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from core.auth.serializers.auth_register_serializers import (
    RegisterSerializer,
)
from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario,
)
from core.auth.views.auth_login_views import (
    build_local_auth_user_payload,
)


User = get_user_model()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLE_EXTERNAL = "autor_externo"
AUTH_SOURCE_LOCAL = "local"

CEDULA_PATTERN = re.compile(
    r"^\d{10}$"
)


# ============================================================
# UTILIDADES
# ============================================================

def _normalize_text(value):
    """
    Normaliza un valor textual.
    """
    return str(
        value or ""
    ).strip()


def _normalized_role(user):
    """
    Obtiene el rol normalizado del usuario.
    """
    return _normalize_text(
        getattr(
            user,
            "rol",
            "",
        )
    ).lower()


def _normalized_auth_source(user):
    """
    Obtiene el origen de autenticación normalizado.
    """
    return _normalize_text(
        getattr(
            user,
            "auth_source",
            "",
        )
    ).lower()


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
        "detail": str(
            exc
        ),
    }


def _get_registered_user(user_id):
    """
    Recupera al usuario registrado con las relaciones necesarias
    para construir la respuesta completa.
    """
    if not user_id:
        return None

    return (
        User.objects
        .select_related(
            "carrera",
            "carrera__facultad",
            "autor",
        )
        .filter(
            pk=user_id
        )
        .first()
    )


def _build_tokens(user):
    """
    Genera los tokens JWT del usuario registrado.
    """
    refresh = RefreshToken.for_user(
        user
    )

    return {
        "access": str(
            refresh.access_token
        ),
        "refresh": str(
            refresh
        ),
    }


def _validate_registered_user(user):
    """
    Comprueba las condiciones de seguridad del usuario creado.

    Esta validación se ejecuta antes de confirmar la transacción.
    Cualquier inconsistencia provoca la reversión completa del
    registro.
    """
    if user is None or not getattr(
        user,
        "pk",
        None,
    ):
        raise ValidationError(
            {
                "detail": (
                    "No fue posible crear la cuenta "
                    "del usuario externo."
                )
            }
        )

    if (
        _normalized_role(user)
        != ROLE_EXTERNAL
    ):
        raise ValidationError(
            {
                "rol": (
                    "El registro público solo puede crear "
                    "autores externos."
                )
            }
        )

    if (
        _normalized_auth_source(user)
        != AUTH_SOURCE_LOCAL
    ):
        raise ValidationError(
            {
                "auth_source": (
                    "El registro público solo puede crear "
                    "cuentas con autenticación local."
                )
            }
        )

    if getattr(
        user,
        "carrera_id",
        None,
    ) is not None:
        raise ValidationError(
            {
                "carrera": (
                    "Los usuarios externos no pueden tener "
                    "una Carrera asignada."
                )
            }
        )

    if bool(
        getattr(
            user,
            "is_staff",
            False,
        )
    ):
        raise ValidationError(
            {
                "is_staff": (
                    "El registro público no puede conceder "
                    "permisos administrativos."
                )
            }
        )

    if bool(
        getattr(
            user,
            "is_superuser",
            False,
        )
    ):
        raise ValidationError(
            {
                "is_superuser": (
                    "El registro público no puede crear "
                    "superusuarios."
                )
            }
        )

    if not bool(
        getattr(
            user,
            "is_active",
            False,
        )
    ):
        raise ValidationError(
            {
                "is_active": (
                    "La cuenta creada mediante el registro "
                    "público debe quedar activa."
                )
            }
        )

    identificacion = _normalize_text(
        getattr(
            user,
            "identificacion",
            "",
        )
    )

    if not CEDULA_PATTERN.fullmatch(
        identificacion
    ):
        raise ValidationError(
            {
                "identificacion": (
                    "La cédula debe contener exactamente "
                    "10 dígitos numéricos."
                )
            }
        )

    if not user.has_usable_password():
        raise ValidationError(
            {
                "password": (
                    "La cuenta registrada debe tener "
                    "una contraseña utilizable."
                )
            }
        )


def _validate_linked_author(
    user,
    author,
):
    """
    Comprueba que el registro Autor exista y esté vinculado con
    el Usuario recién creado.
    """
    if author is None:
        raise ValidationError(
            {
                "detail": (
                    "No fue posible crear el registro "
                    "académico del autor."
                )
            }
        )

    author_user_id = getattr(
        author,
        "usuario_id",
        None,
    )

    if author_user_id != user.pk:
        raise ValidationError(
            {
                "detail": (
                    "El registro Autor fue creado, pero no "
                    "quedó correctamente vinculado con "
                    "la cuenta del usuario."
                )
            }
        )


# ============================================================
# REGISTRO
# ============================================================

class RegisterView(APIView):
    """
    Registra un autor externo y devuelve una sesión JWT.

    Este endpoint es público y no utiliza una autenticación
    previamente establecida.
    """

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(
        self,
        request,
    ):
        serializer = RegisterSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:
            with transaction.atomic():
                # ============================================
                # CREACIÓN DEL USUARIO
                # ============================================

                user = serializer.save()

                _validate_registered_user(
                    user
                )

                # ============================================
                # SINCRONIZACIÓN OBLIGATORIA DEL AUTOR
                # ============================================

                author = (
                    asegurar_autor_para_usuario(
                        user
                    )
                )

                _validate_linked_author(
                    user,
                    author,
                )

                user_id = user.pk

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
                        "No se pudo completar el registro "
                        "porque el correo o la cédula ya "
                        "pertenecen a otra cuenta."
                    )
                }
            ) from exc

        # ====================================================
        # CONSULTA POSTERIOR A LA TRANSACCIÓN
        # ====================================================

        registered_user = (
            _get_registered_user(
                user_id
            )
        )

        if registered_user is None:
            return Response(
                {
                    "detail": (
                        "El usuario fue registrado, pero no "
                        "pudo recuperarse después de guardar "
                        "la información."
                    )
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        # Se comprueba nuevamente el estado persistido antes de
        # generar credenciales de acceso.
        try:
            _validate_registered_user(
                registered_user
            )

            registered_author = getattr(
                registered_user,
                "autor",
                None,
            )

            _validate_linked_author(
                registered_user,
                registered_author,
            )

        except ValidationError:
            return Response(
                {
                    "detail": (
                        "La cuenta se registró, pero presenta "
                        "una inconsistencia interna. Solicite "
                        "una revisión al administrador."
                    )
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        # ====================================================
        # TOKENS
        # ====================================================

        tokens = _build_tokens(
            registered_user
        )

        response = Response(
            {
                "message": (
                    "Usuario registrado correctamente."
                ),

                "tokens": tokens,

                "user": (
                    build_local_auth_user_payload(
                        registered_user,
                        request=request,
                    )
                ),
            },
            status=status.HTTP_201_CREATED,
        )

        # Impide que el navegador o un proxy almacenen los
        # tokens y los datos de la sesión.
        response[
            "Cache-Control"
        ] = (
            "no-store, no-cache, "
            "must-revalidate, max-age=0"
        )

        response[
            "Pragma"
        ] = "no-cache"

        response[
            "Expires"
        ] = "0"

        return response