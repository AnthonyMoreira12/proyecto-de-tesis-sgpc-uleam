"""
Servicios para autenticación y sincronización con Microsoft 365.

Este módulo gestiona:

- Construcción de la URL de autorización.
- Intercambio del código OAuth.
- Consulta de Microsoft Graph.
- Resolución de la identidad institucional.
- Validación de dominios y correos permitidos.
- Creación o actualización segura del usuario.
- Sincronización del registro Autor.
- Generación del payload JWT para el frontend.

La facultad del usuario se deriva exclusivamente desde
usuario.carrera.facultad.
"""

import logging
import re
from urllib.parse import quote

import msal
import requests

from django.conf import settings
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction
from django.utils import timezone

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario,
)
from core.auth.services.auth_profile_services import (
    get_profile_edit_status,
)


logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURACIÓN PREDETERMINADA
# ============================================================

DEFAULT_MICROSOFT_ALLOWED_DOMAINS = (
    "uleam.edu.ec",
)

DEFAULT_MICROSOFT_ALLOWED_EMAILS = (
    "e1316718111@live.uleam.edu.ec",
)

DEFAULT_MICROSOFT_ADMIN_EMAILS = (
    "e1316718111@live.uleam.edu.ec",
)

DEFAULT_MICROSOFT_SCOPES = (
    "User.Read",
)

DEFAULT_MICROSOFT_APP_SCOPES = (
    "https://graph.microsoft.com/.default",
)

DEFAULT_GRAPH_TIMEOUT_SECONDS = 15

MICROSOFT_AUTH_SOURCE = "microsoft"
LOCAL_AUTH_SOURCE = "local"

INSTITUTIONAL_AUTHOR_ROLE = "autor"
EXTERNAL_AUTHOR_ROLE = "autor_externo"


# ============================================================
# EXCEPCIÓN DEL SERVICIO
# ============================================================

class MicrosoftAuthServiceError(Exception):
    """
    Error controlado producido durante la autenticación o
    sincronización con Microsoft.
    """

    def __init__(
        self,
        detail,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        self.detail = detail
        self.status_code = status_code

        super().__init__(
            str(detail)
        )


# ============================================================
# NORMALIZACIÓN
# ============================================================

def _normalize_text(value):
    """
    Normaliza un valor textual.
    """
    return str(
        value or ""
    ).strip()


PERSON_NAME_LOWERCASE_PARTICLES = {
    "da",
    "das",
    "de",
    "del",
    "do",
    "dos",
    "e",
    "la",
    "las",
    "los",
    "van",
    "von",
    "y",
}


def _capitalize_name_fragment(fragment):
    if not fragment:
        return fragment

    return (
        fragment[:1].upper()
        + fragment[1:].lower()
    )


def _normalize_name_token(token):
    normalized_token = token.lower()

    if normalized_token in PERSON_NAME_LOWERCASE_PARTICLES:
        return normalized_token

    fragments = re.split(
        r"([-’'])",
        normalized_token,
    )

    return "".join(
        fragment
        if fragment in {
            "-",
            "'",
            "’",
        }
        else _capitalize_name_fragment(
            fragment
        )
        for fragment in fragments
    )


def _normalize_person_name(value):
    """
    Convierte nombres provenientes de Microsoft a una
    capitalización uniforme y legible.
    """
    normalized = re.sub(
        r"\s+",
        " ",
        _normalize_text(
            value
        ),
    )

    if not normalized:
        return ""

    return " ".join(
        _normalize_name_token(
            token
        )
        for token in normalized.split(" ")
        if token
    )


def _normalize_optional_text(value):
    """
    Normaliza un texto opcional.
    """
    normalized = _normalize_text(
        value
    )

    return normalized or None


def _normalize_email(value):
    """
    Normaliza un correo electrónico.
    """
    normalized = _normalize_optional_text(
        value
    )

    if normalized is None:
        return None

    return normalized.lower()


def _normalize_string_list(
    value,
    *,
    lowercase=False,
):
    """
    Convierte una configuración textual o iterable en una lista
    normalizada y sin duplicados.

    Admite:

    - Lista.
    - Tupla.
    - Conjunto.
    - Cadena separada por comas o punto y coma.
    """
    if value in (
        None,
        "",
    ):
        return []

    if isinstance(
        value,
        str,
    ):
        candidates = (
            value
            .replace(";", ",")
            .split(",")
        )

    else:
        try:
            candidates = list(
                value
            )

        except TypeError:
            candidates = [
                value,
            ]

    normalized_values = []

    for candidate in candidates:
        normalized = _normalize_text(
            candidate
        )

        if not normalized:
            continue

        if lowercase:
            normalized = normalized.lower()

        if normalized not in normalized_values:
            normalized_values.append(
                normalized
            )

    return normalized_values


def _normalize_phone_list(value):
    """
    Normaliza los teléfonos entregados por Microsoft Graph.
    """
    if value in (
        None,
        "",
    ):
        return []

    if isinstance(
        value,
        (list, tuple, set),
    ):
        candidates = value

    else:
        candidates = [
            value,
        ]

    phones = []

    for candidate in candidates:
        phone = _normalize_text(
            candidate
        )

        if phone and phone not in phones:
            phones.append(
                phone
            )

    return phones


# ============================================================
# CONFIGURACIÓN DE MICROSOFT
# ============================================================

def _get_required_setting(
    setting_name,
):
    """
    Obtiene una configuración obligatoria.
    """
    value = _normalize_optional_text(
        getattr(
            settings,
            setting_name,
            None,
        )
    )

    if value is None:
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    f"No se encuentra configurado "
                    f"{setting_name}."
                )
            },
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

    return value


def _get_allowed_domains():
    """
    Obtiene los dominios institucionales admitidos.
    """
    configured = getattr(
        settings,
        "MICROSOFT_ALLOWED_DOMAINS",
        DEFAULT_MICROSOFT_ALLOWED_DOMAINS,
    )

    return _normalize_string_list(
        configured,
        lowercase=True,
    )


def _get_allowed_emails():
    """
    Obtiene correos específicos permitidos fuera del dominio
    principal.
    """
    configured = getattr(
        settings,
        "MICROSOFT_ALLOWED_EMAILS",
        DEFAULT_MICROSOFT_ALLOWED_EMAILS,
    )

    return _normalize_string_list(
        configured,
        lowercase=True,
    )


def _get_admin_emails():
    """
    Obtiene los correos Microsoft que deben recibir privilegios
    administrativos.

    El servicio únicamente promueve cuentas configuradas. Nunca
    elimina automáticamente permisos existentes.
    """
    configured = getattr(
        settings,
        "MICROSOFT_ADMIN_EMAILS",
        DEFAULT_MICROSOFT_ADMIN_EMAILS,
    )

    return _normalize_string_list(
        configured,
        lowercase=True,
    )


def _microsoft_scopes():
    """
    Obtiene los permisos delegados del inicio de sesión.
    """
    configured = getattr(
        settings,
        "MICROSOFT_SCOPES",
        DEFAULT_MICROSOFT_SCOPES,
    )

    scopes = _normalize_string_list(
        configured,
    )

    return scopes or list(
        DEFAULT_MICROSOFT_SCOPES
    )


def _microsoft_app_scopes():
    """
    Obtiene los permisos de aplicación utilizados para consultar
    usuarios mediante credenciales del servidor.
    """
    configured = getattr(
        settings,
        "MICROSOFT_APP_SCOPES",
        DEFAULT_MICROSOFT_APP_SCOPES,
    )

    scopes = _normalize_string_list(
        configured,
    )

    return scopes or list(
        DEFAULT_MICROSOFT_APP_SCOPES
    )


def _get_graph_timeout():
    """
    Obtiene el tiempo máximo de espera para Microsoft Graph.
    """
    configured = getattr(
        settings,
        "MICROSOFT_GRAPH_TIMEOUT_SECONDS",
        DEFAULT_GRAPH_TIMEOUT_SECONDS,
    )

    try:
        timeout = int(
            configured
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        timeout = DEFAULT_GRAPH_TIMEOUT_SECONDS

    return max(
        1,
        min(
            timeout,
            60,
        ),
    )


# ============================================================
# VALIDACIÓN INSTITUCIONAL
# ============================================================

def is_allowed_institutional_email(email_norm):
    """
    Comprueba que el correo pertenezca a la institución o esté
    incluido expresamente en MICROSOFT_ALLOWED_EMAILS.

    Los subdominios también son admitidos. Por ejemplo:

    live.uleam.edu.ec
    estudiantes.uleam.edu.ec
    """
    normalized_email = _normalize_email(
        email_norm
    )

    if normalized_email is None:
        return False

    if normalized_email in _get_allowed_emails():
        return True

    if "@" not in normalized_email:
        return False

    local_part, domain = normalized_email.rsplit(
        "@",
        1,
    )

    if not local_part or not domain:
        return False

    for allowed_domain in _get_allowed_domains():
        if (
            domain == allowed_domain
            or domain.endswith(
                f".{allowed_domain}"
            )
        ):
            return True

    return False


def _is_admin_email(email):
    """
    Determina si el correo debe recibir privilegios
    administrativos.
    """
    normalized_email = _normalize_email(
        email
    )

    if normalized_email is None:
        return False

    return normalized_email in _get_admin_emails()


# ============================================================
# CLIENTE MSAL
# ============================================================

def _build_msal_app():
    """
    Construye la aplicación confidencial MSAL.
    """
    client_id = _get_required_setting(
        "MICROSOFT_CLIENT_ID"
    )

    client_secret = _get_required_setting(
        "MICROSOFT_CLIENT_SECRET"
    )

    authority = _get_required_setting(
        "MICROSOFT_AUTHORITY"
    )

    return msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority,
    )


# ============================================================
# AUTORIZACIÓN OAUTH
# ============================================================

def build_microsoft_authorization_url(
    *,
    state,
):
    """
    Construye la URL de autorización de Microsoft.
    """
    normalized_state = _normalize_optional_text(
        state
    )

    if normalized_state is None:
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "No fue posible generar el estado "
                    "de autenticación."
                )
            }
        )

    redirect_uri = _get_required_setting(
        "MICROSOFT_REDIRECT_URI"
    )

    return (
        _build_msal_app()
        .get_authorization_request_url(
            scopes=_microsoft_scopes(),
            redirect_uri=redirect_uri,
            state=normalized_state,
            prompt="select_account",
            response_mode="query",
        )
    )


def exchange_microsoft_authorization_code(
    *,
    code,
):
    """
    Intercambia el código temporal por tokens de Microsoft.
    """
    normalized_code = _normalize_optional_text(
        code
    )

    if normalized_code is None:
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "El código de autorización "
                    "es obligatorio."
                )
            }
        )

    redirect_uri = _get_required_setting(
        "MICROSOFT_REDIRECT_URI"
    )

    result = (
        _build_msal_app()
        .acquire_token_by_authorization_code(
            code=normalized_code,
            scopes=_microsoft_scopes(),
            redirect_uri=redirect_uri,
        )
    )

    if not isinstance(
        result,
        dict,
    ):
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "Microsoft no devolvió una respuesta "
                    "válida durante la autenticación."
                )
            },
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
        )

    return result


# ============================================================
# MICROSOFT GRAPH
# ============================================================

def _graph_headers(access_token):
    """
    Construye los encabezados para Microsoft Graph.
    """
    return {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Accept": "application/json",
    }


def _graph_profile_select():
    """
    Campos solicitados a Microsoft Graph.
    """
    return (
        "id,"
        "displayName,"
        "givenName,"
        "surname,"
        "mail,"
        "userPrincipalName,"
        "jobTitle,"
        "department,"
        "officeLocation,"
        "businessPhones,"
        "mobilePhone"
    )


def fetch_graph_profile(access_token):
    """
    Obtiene el perfil del usuario autenticado desde Microsoft
    Graph.

    Los errores se devuelven como una estructura controlada para
    permitir continuar con los claims del ID token.
    """
    normalized_token = _normalize_optional_text(
        access_token
    )

    if normalized_token is None:
        return {
            "_error": "missing_access_token",
        }

    graph_url = (
        "https://graph.microsoft.com/v1.0/me"
        f"?$select={_graph_profile_select()}"
    )

    try:
        response = requests.get(
            graph_url,
            headers=_graph_headers(
                normalized_token
            ),
            timeout=_get_graph_timeout(),
        )

    except requests.Timeout:
        logger.warning(
            (
                "Microsoft Graph excedió el tiempo de espera "
                "al consultar el perfil."
            )
        )

        return {
            "_error": "graph_timeout",
        }

    except requests.RequestException:
        logger.exception(
            (
                "Error de conexión al consultar el perfil "
                "de Microsoft Graph."
            )
        )

        return {
            "_error": "graph_request_failed",
        }

    if not response.ok:
        logger.warning(
            (
                "Microsoft Graph devolvió HTTP %s al consultar "
                "el perfil."
            ),
            response.status_code,
        )

        return {
            "_error": "graph_failed",
            "_status": response.status_code,
        }

    try:
        payload = response.json()

    except ValueError:
        logger.warning(
            (
                "Microsoft Graph devolvió una respuesta "
                "que no contiene JSON válido."
            )
        )

        return {
            "_error": "graph_invalid_json",
        }

    if not isinstance(
        payload,
        dict,
    ):
        return {
            "_error": "graph_invalid_payload",
        }

    return payload


def _acquire_application_access_token():
    """
    Obtiene un token de aplicación para consultas administrativas
    a Microsoft Graph.
    """
    result = (
        _build_msal_app()
        .acquire_token_for_client(
            scopes=_microsoft_app_scopes()
        )
    )

    if not isinstance(
        result,
        dict,
    ):
        return None

    return _normalize_optional_text(
        result.get(
            "access_token"
        )
    )


def obtener_usuario_microsoft_por_id(
    user_id,
):
    """
    Consulta un usuario de Microsoft Graph mediante su ID o UPN.

    Esta función se conserva por compatibilidad con otros módulos.
    """
    normalized_user_id = _normalize_optional_text(
        user_id
    )

    if normalized_user_id is None:
        return {
            "_error": "missing_user_id",
        }

    access_token = (
        _acquire_application_access_token()
    )

    if access_token is None:
        return {
            "_error": "msal_token_failed",
        }

    encoded_user_id = quote(
        normalized_user_id,
        safe="",
    )

    endpoint = (
        "https://graph.microsoft.com/v1.0/users/"
        f"{encoded_user_id}"
        f"?$select={_graph_profile_select()}"
    )

    try:
        response = requests.get(
            endpoint,
            headers=_graph_headers(
                access_token
            ),
            timeout=_get_graph_timeout(),
        )

    except requests.Timeout:
        return {
            "_error": "graph_timeout",
        }

    except requests.RequestException:
        logger.exception(
            (
                "No se pudo consultar el usuario %s "
                "en Microsoft Graph."
            ),
            normalized_user_id,
        )

        return {
            "_error": "graph_request_failed",
        }

    if not response.ok:
        return {
            "_error": "graph_failed",
            "_status": response.status_code,
        }

    try:
        payload = response.json()

    except ValueError:
        return {
            "_error": "graph_invalid_json",
        }

    if not isinstance(
        payload,
        dict,
    ):
        return {
            "_error": "graph_invalid_payload",
        }

    return payload


# ============================================================
# RESOLUCIÓN DE IDENTIDAD
# ============================================================

def resolve_microsoft_identity(
    *,
    claims,
    graph,
):
    """
    Construye una identidad normalizada utilizando los claims
    del ID token y el perfil de Microsoft Graph.
    """
    claims = (
        claims
        if isinstance(
            claims,
            dict,
        )
        else {}
    )

    graph = (
        graph
        if isinstance(
            graph,
            dict,
        )
        and not graph.get("_error")
        else {}
    )

    oid = _normalize_optional_text(
        claims.get("oid")
        or graph.get("id")
        or claims.get("sub")
    )

    email = _normalize_email(
        claims.get(
            "preferred_username"
        )
        or claims.get(
            "email"
        )
        or claims.get(
            "upn"
        )
        or graph.get(
            "mail"
        )
        or graph.get(
            "userPrincipalName"
        )
    )

    display_name = (
        _normalize_person_name(
            claims.get("name")
            or graph.get("displayName")
        )
        or None
    )

    given_name = (
        _normalize_person_name(
            claims.get("given_name")
            or graph.get("givenName")
        )
        or None
    )

    surname = (
        _normalize_person_name(
            claims.get("family_name")
            or graph.get("surname")
        )
        or None
    )

    if (
        not given_name
        and not surname
        and display_name
    ):
        name_parts = display_name.split()

        if name_parts:
            given_name = name_parts[0]

        if len(name_parts) > 1:
            surname = " ".join(
                name_parts[1:]
            )

    if not given_name:
        given_name = "Usuario"

    # El modelo Usuario exige apellidos no vacíos.
    if not surname:
        surname = "Institucional"

    if not display_name:
        display_name = (
            f"{given_name} {surname}"
        ).strip()

    if oid is None or email is None:
        return None

    return {
        "oid": oid,
        "email": email,
        "display_name": display_name,
        "given": given_name,
        "family": surname,
        "tenant_id": _normalize_optional_text(
            claims.get("tid")
        ),
    }


# ============================================================
# CAMPOS MICROSOFT
# ============================================================

def _assign_if_changed(
    user,
    field_name,
    value,
    updated_fields,
):
    """
    Asigna un valor únicamente cuando el modelo contiene el
    campo y su contenido ha cambiado.
    """
    if not hasattr(
        user,
        field_name,
    ):
        return

    current_value = getattr(
        user,
        field_name,
        None,
    )

    if current_value == value:
        return

    setattr(
        user,
        field_name,
        value,
    )

    updated_fields.append(
        field_name
    )


def _apply_claim_fields(
    user,
    claims,
    updated_fields,
):
    """
    Sincroniza los claims recibidos desde Microsoft.
    """
    store_raw_claims = bool(
        getattr(
            settings,
            "MICROSOFT_STORE_RAW_CLAIMS",
            True,
        )
    )

    if (
        store_raw_claims
        and hasattr(
            user,
            "ms_raw_claims",
        )
    ):
        _assign_if_changed(
            user,
            "ms_raw_claims",
            claims,
            updated_fields,
        )


def _apply_graph_fields(
    user,
    graph,
    updated_fields,
):
    """
    Sincroniza los datos obtenidos desde Microsoft Graph.
    """
    if (
        not isinstance(
            graph,
            dict,
        )
        or graph.get("_error")
    ):
        return

    graph_mapping = {
        "ms_graph_id": (
            _normalize_optional_text(
                graph.get("id")
            )
        ),

        "ms_display_name": (
            _normalize_person_name(
                graph.get("displayName")
            )
            or None
        ),

        "ms_given_name": (
            _normalize_person_name(
                graph.get("givenName")
            )
            or None
        ),

        "ms_surname": (
            _normalize_person_name(
                graph.get("surname")
            )
            or None
        ),

        "ms_mail": (
            _normalize_email(
                graph.get("mail")
            )
        ),

        "ms_user_principal_name": (
            _normalize_email(
                graph.get(
                    "userPrincipalName"
                )
            )
        ),

        "ms_job_title": (
            _normalize_optional_text(
                graph.get("jobTitle")
            )
        ),

        "ms_department": (
            _normalize_optional_text(
                graph.get("department")
            )
        ),

        "ms_office_location": (
            _normalize_optional_text(
                graph.get("officeLocation")
            )
        ),

        "ms_business_phones": (
            _normalize_phone_list(
                graph.get(
                    "businessPhones"
                )
            )
        ),

        "ms_mobile_phone": (
            _normalize_optional_text(
                graph.get("mobilePhone")
            )
        ),
    }

    for field_name, value in graph_mapping.items():
        _assign_if_changed(
            user,
            field_name,
            value,
            updated_fields,
        )

    store_raw_graph = bool(
        getattr(
            settings,
            "MICROSOFT_STORE_RAW_GRAPH",
            True,
        )
    )

    if (
        store_raw_graph
        and hasattr(
            user,
            "ms_raw_graph",
        )
    ):
        _assign_if_changed(
            user,
            "ms_raw_graph",
            graph,
            updated_fields,
        )

    if hasattr(
        user,
        "ms_last_sync",
    ):
        user.ms_last_sync = timezone.now()

        updated_fields.append(
            "ms_last_sync"
        )


# ============================================================
# BÚSQUEDA Y CONFLICTOS
# ============================================================

def _find_locked_user_by_microsoft_id(
    user_model,
    microsoft_id,
):
    """
    Busca y bloquea el usuario vinculado al identificador
    Microsoft.
    """
    if not microsoft_id:
        return None

    users = list(
        user_model.objects
        .select_for_update()
        .filter(
            microsoft_id=microsoft_id
        )[:2]
    )

    if len(users) > 1:
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "Existen varias cuentas vinculadas al "
                    "mismo identificador Microsoft."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    return users[0] if users else None


def _find_locked_user_by_graph_id(
    user_model,
    graph_id,
):
    """
    Busca y bloquea el usuario vinculado al identificador de
    Microsoft Graph.
    """
    if not graph_id:
        return None

    users = list(
        user_model.objects
        .select_for_update()
        .filter(
            ms_graph_id=graph_id
        )[:2]
    )

    if len(users) > 1:
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "Existen varias cuentas vinculadas al "
                    "mismo identificador de Microsoft Graph."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    return users[0] if users else None


def _find_locked_user_by_email(
    user_model,
    email,
):
    """
    Busca y bloquea el usuario mediante el correo.
    """
    if not email:
        return None

    return (
        user_model.objects
        .select_for_update()
        .filter(
            email__iexact=email
        )
        .first()
    )


def _resolve_existing_microsoft_user(
    user_model,
    *,
    identity,
    graph,
):
    """
    Resuelve la cuenta existente y detecta conflictos entre:

    - microsoft_id
    - ms_graph_id
    - correo
    """
    oid = identity["oid"]
    email = identity["email"]

    graph_id = _normalize_optional_text(
        graph.get("id")
        if isinstance(
            graph,
            dict,
        )
        and not graph.get("_error")
        else None
    )

    user_by_microsoft_id = (
        _find_locked_user_by_microsoft_id(
            user_model,
            oid,
        )
    )

    user_by_graph_id = (
        _find_locked_user_by_graph_id(
            user_model,
            graph_id,
        )
    )

    user_by_email = (
        _find_locked_user_by_email(
            user_model,
            email,
        )
    )

    candidates = {
        user.pk: user
        for user in (
            user_by_microsoft_id,
            user_by_graph_id,
            user_by_email,
        )
        if user is not None
    }

    if len(candidates) > 1:
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "El correo y el identificador Microsoft "
                    "se encuentran asociados a cuentas "
                    "diferentes. Solicite una revisión al "
                    "administrador."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    if not candidates:
        return None

    return next(
        iter(
            candidates.values()
        )
    )


def _validate_existing_account_link(
    user,
    *,
    identity,
):
    """
    Valida que una cuenta existente pueda vincularse con la
    identidad Microsoft recibida.
    """
    current_source = _normalize_text(
        getattr(
            user,
            "auth_source",
            "",
        )
    ).lower()

    current_microsoft_id = (
        _normalize_optional_text(
            getattr(
                user,
                "microsoft_id",
                None,
            )
        )
    )

    if (
        current_microsoft_id
        and current_microsoft_id
        != identity["oid"]
    ):
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "La cuenta ya está vinculada a una "
                    "identidad Microsoft diferente."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    if current_source == MICROSOFT_AUTH_SOURCE:
        return

    allow_local_linking = bool(
        getattr(
            settings,
            "MICROSOFT_ALLOW_LOCAL_ACCOUNT_LINKING",
            True,
        )
    )

    if not allow_local_linking:
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "Ya existe una cuenta local con este "
                    "correo. El administrador debe autorizar "
                    "su vinculación con Microsoft."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        )


# ============================================================
# SINCRONIZACIÓN DEL USUARIO
# ============================================================

def sync_microsoft_user(
    user_model,
    *,
    identity,
    claims,
    graph,
):
    """
    Crea o actualiza el usuario institucional.

    La operación se ejecuta dentro de una transacción y bloquea
    cualquier cuenta coincidente antes de modificarla.
    """
    if not isinstance(
        identity,
        dict,
    ):
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "La identidad Microsoft recibida "
                    "no es válida."
                )
            }
        )

    email = _normalize_email(
        identity.get("email")
    )

    oid = _normalize_optional_text(
        identity.get("oid")
    )

    given_name = (
        _normalize_person_name(
            identity.get("given")
        )
        or "Usuario"
    )

    surname = (
        _normalize_person_name(
            identity.get("family")
        )
        or "Institucional"
    )

    if not email or not oid:
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "Microsoft no proporcionó un correo "
                    "o identificador válido."
                )
            }
        )

    if not is_allowed_institutional_email(
        email
    ):
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "El correo Microsoft no pertenece a "
                    "un dominio institucional autorizado."
                )
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    claims = (
        claims
        if isinstance(
            claims,
            dict,
        )
        else {}
    )

    graph = (
        graph
        if isinstance(
            graph,
            dict,
        )
        else {}
    )

    try:
        with transaction.atomic():
            user = (
                _resolve_existing_microsoft_user(
                    user_model,
                    identity={
                        **identity,
                        "email": email,
                        "oid": oid,
                    },
                    graph=graph,
                )
            )

            if user is None:
                user = user_model(
                    email=email,
                    nombres=given_name,
                    apellidos=surname,
                    rol=INSTITUTIONAL_AUTHOR_ROLE,
                    microsoft_id=oid,
                    auth_source=MICROSOFT_AUTH_SOURCE,
                    is_active=True,
                    is_staff=_is_admin_email(
                        email
                    ),
                    is_superuser=False,
                )

                user.set_unusable_password()

                updated_fields = []

                _apply_claim_fields(
                    user,
                    claims,
                    updated_fields,
                )

                _apply_graph_fields(
                    user,
                    graph,
                    updated_fields,
                )

                user.save()

            else:
                _validate_existing_account_link(
                    user,
                    identity={
                        **identity,
                        "email": email,
                        "oid": oid,
                    },
                )

                updated_fields = []

                _assign_if_changed(
                    user,
                    "email",
                    email,
                    updated_fields,
                )

                _assign_if_changed(
                    user,
                    "microsoft_id",
                    oid,
                    updated_fields,
                )

                _assign_if_changed(
                    user,
                    "auth_source",
                    MICROSOFT_AUTH_SOURCE,
                    updated_fields,
                )

                _assign_if_changed(
                    user,
                    "rol",
                    INSTITUTIONAL_AUTHOR_ROLE,
                    updated_fields,
                )

                _assign_if_changed(
                    user,
                    "is_active",
                    True,
                    updated_fields,
                )

                sync_names = bool(
                    getattr(
                        settings,
                        "MICROSOFT_SYNC_NAMES",
                        True,
                    )
                )

                if sync_names:
                    _assign_if_changed(
                        user,
                        "nombres",
                        given_name,
                        updated_fields,
                    )

                    _assign_if_changed(
                        user,
                        "apellidos",
                        surname,
                        updated_fields,
                    )

                if (
                    _is_admin_email(email)
                    and not bool(
                        getattr(
                            user,
                            "is_staff",
                            False,
                        )
                    )
                ):
                    user.is_staff = True

                    updated_fields.append(
                        "is_staff"
                    )

                _apply_claim_fields(
                    user,
                    claims,
                    updated_fields,
                )

                _apply_graph_fields(
                    user,
                    graph,
                    updated_fields,
                )

                if updated_fields:
                    user.save(
                        update_fields=list(
                            dict.fromkeys(
                                updated_fields
                            )
                        )
                    )

            author = asegurar_autor_para_usuario(
                user
            )

            if author is None:
                raise MicrosoftAuthServiceError(
                    {
                        "detail": (
                            "No fue posible crear o actualizar "
                            "el registro de autor institucional."
                        )
                    },
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                )

            return user

    except MicrosoftAuthServiceError:
        raise

    except DjangoValidationError as exc:
        if hasattr(
            exc,
            "message_dict",
        ):
            detail = exc.message_dict

        elif hasattr(
            exc,
            "messages",
        ):
            detail = {
                "detail": list(
                    exc.messages
                )
            }

        else:
            detail = {
                "detail": str(
                    exc
                )
            }

        raise MicrosoftAuthServiceError(
            detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from exc

    except IntegrityError as exc:
        logger.exception(
            (
                "Conflicto de integridad al sincronizar "
                "la cuenta Microsoft %s."
            ),
            email,
        )

        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "No fue posible sincronizar la cuenta "
                    "Microsoft debido a un conflicto con "
                    "información existente."
                )
            },
            status_code=status.HTTP_409_CONFLICT,
        ) from exc


# ============================================================
# AVATAR
# ============================================================

def _avatar_url(
    user,
    request=None,
):
    """
    Obtiene la URL del avatar.
    """
    avatar = getattr(
        user,
        "avatar",
        None,
    )

    if not avatar:
        return None

    avatar_name = getattr(
        avatar,
        "name",
        None,
    )

    if not avatar_name:
        return None

    try:
        avatar_url = avatar.url

    except (
        ValueError,
        OSError,
        NotImplementedError,
    ):
        return None

    if request is None:
        return avatar_url

    try:
        return request.build_absolute_uri(
            avatar_url
        )

    except (
        ValueError,
        TypeError,
    ):
        return avatar_url


# ============================================================
# PAYLOAD DE AUTENTICACIÓN
# ============================================================

def build_microsoft_auth_payload(
    user,
    request=None,
):
    """
    Genera los tokens y la información de sesión que consume el
    frontend.
    """
    if user is None or not getattr(
        user,
        "pk",
        None,
    ):
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "No fue posible generar la sesión "
                    "del usuario Microsoft."
                )
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not bool(
        getattr(
            user,
            "is_active",
            False,
        )
    ):
        raise MicrosoftAuthServiceError(
            {
                "detail": (
                    "La cuenta Microsoft se encuentra "
                    "inactiva."
                )
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    career = getattr(
        user,
        "carrera",
        None,
    )

    faculty = (
        getattr(
            career,
            "facultad",
            None,
        )
        if career is not None
        else None
    )

    edit_status = get_profile_edit_status(
        user
    )

    refresh = RefreshToken.for_user(
        user
    )

    full_name = (
        f"{_normalize_person_name(getattr(user, 'nombres', ''))} "
        f"{_normalize_person_name(getattr(user, 'apellidos', ''))}"
    ).strip()

    return {
        "tokens": {
            "access": str(
                refresh.access_token
            ),
            "refresh": str(
                refresh
            ),
        },

        "user": {
            "id": user.pk,

            "email": user.email,

            "nombres": user.nombres,

            "apellidos": user.apellidos,

            "full_name": full_name,

            "rol": user.rol,

            "auth_source": getattr(
                user,
                "auth_source",
                MICROSOFT_AUTH_SOURCE,
            ),

            "perfil_completo": bool(
                getattr(
                    user,
                    "perfil_completo",
                    False,
                )
            ),

            "is_active": bool(
                getattr(
                    user,
                    "is_active",
                    False,
                )
            ),

            "is_staff": bool(
                getattr(
                    user,
                    "is_staff",
                    False,
                )
            ),

            "is_superuser": bool(
                getattr(
                    user,
                    "is_superuser",
                    False,
                )
            ),

            "es_admin": bool(
                getattr(
                    user,
                    "is_staff",
                    False,
                )
                or getattr(
                    user,
                    "is_superuser",
                    False,
                )
            ),

            # Facultad derivada desde carrera.
            "facultad_id": getattr(
                career,
                "facultad_id",
                None,
            ),

            "facultad": getattr(
                faculty,
                "nombre",
                None,
            ),

            "carrera_id": getattr(
                user,
                "carrera_id",
                None,
            ),

            "carrera": getattr(
                career,
                "nombre",
                None,
            ),

            "avatar_url": _avatar_url(
                user,
                request=request,
            ),

            # Información Microsoft.
            "microsoft_id": getattr(
                user,
                "microsoft_id",
                None,
            ),

            "ms_graph_id": getattr(
                user,
                "ms_graph_id",
                None,
            ),

            "ms_display_name": getattr(
                user,
                "ms_display_name",
                None,
            ),

            "ms_job_title": getattr(
                user,
                "ms_job_title",
                None,
            ),

            "ms_department": getattr(
                user,
                "ms_department",
                None,
            ),

            "ms_office_location": getattr(
                user,
                "ms_office_location",
                None,
            ),

            "ms_last_sync": getattr(
                user,
                "ms_last_sync",
                None,
            ),

            # Estado de edición del perfil.
            "profile_edit_locked": bool(
                edit_status.get(
                    "profile_edit_locked",
                    False,
                )
            ),

            "profile_edit_lock_reason": (
                edit_status.get(
                    "profile_edit_lock_reason"
                )
            ),

            "profile_edit_attempts_left": int(
                edit_status.get(
                    "attempts_left",
                    0,
                )
                or 0
            ),

            "profile_edit_until": (
                edit_status.get(
                    "profile_edit_until"
                )
            ),

            "profile_edit_available": bool(
                edit_status.get(
                    "available",
                    False,
                )
            ),

            "profile_edit_expired": bool(
                edit_status.get(
                    "expired",
                    False,
                )
            ),
        },
    }