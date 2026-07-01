"""
Servicios para autenticación con Microsoft 365.
Contiene helpers de OAuth, Graph y sincronización del usuario institucional.
"""

import msal
import requests

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from core.auth.services.auth_author_sync_services import asegurar_autor_para_usuario

INST_DOMAIN = "@uleam.edu.ec"
ADMIN_ORIGINAL_EMAIL = "e1316718111@live.uleam.edu.ec"


def _norm_email(email):
    return (email or "").strip().lower()


def is_allowed_institutional_email(email_norm):
    email_norm = _norm_email(email_norm)
    return email_norm.endswith(INST_DOMAIN) or email_norm == ADMIN_ORIGINAL_EMAIL


def _is_admin_original(email_norm):
    email_norm = _norm_email(email_norm)
    return email_norm == ADMIN_ORIGINAL_EMAIL


def _build_msal_app():
    return msal.ConfidentialClientApplication(
        client_id=settings.MICROSOFT_CLIENT_ID,
        client_credential=settings.MICROSOFT_CLIENT_SECRET,
        authority=settings.MICROSOFT_AUTHORITY,
    )


def _microsoft_scopes():
    return ["User.Read"]


def build_microsoft_authorization_url(*, state):
    return _build_msal_app().get_authorization_request_url(
        scopes=_microsoft_scopes(),
        redirect_uri=settings.MICROSOFT_REDIRECT_URI,
        state=state,
        prompt="select_account",
    )


def exchange_microsoft_authorization_code(*, code):
    return _build_msal_app().acquire_token_by_authorization_code(
        code=code,
        scopes=_microsoft_scopes(),
        redirect_uri=settings.MICROSOFT_REDIRECT_URI,
    )


def fetch_graph_profile(access_token):
    if not access_token:
        return {}

    graph_url = (
        "https://graph.microsoft.com/v1.0/me"
        "?$select=id,displayName,givenName,surname,"
        "mail,userPrincipalName,jobTitle,"
        "department,officeLocation,businessPhones,mobilePhone"
    )

    try:
        response = requests.get(
            graph_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            timeout=15,
        )

        if response.ok:
            return response.json()

        return {
            "_error": "graph_failed",
            "_status": response.status_code,
            "_body": response.text,
        }
    except Exception as exc:
        return {
            "_error": "graph_exception",
            "_detail": str(exc),
        }


def obtener_usuario_microsoft_por_id(user_id):
    msal_app = _build_msal_app()
    scopes = ["https://graph.microsoft.com/.default"]
    
    result = msal_app.acquire_token_silent(scopes, account=None)
    if not result:
        result = msal_app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        access_token = result["access_token"]
        endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
                timeout=15,
            )
            
            if response.ok:
                return response.json()
            return {"_error": "graph_failed", "_status": response.status_code}
        except Exception:
            return {"_error": "graph_exception"}
    return {"_error": "msal_token_failed"}


def resolve_microsoft_identity(*, claims, graph):
    claims = claims or {}
    graph = graph or {}

    oid = claims.get("oid") or claims.get("sub")
    email = (claims.get("preferred_username") or claims.get("email") or graph.get("mail") or graph.get("userPrincipalName"))
    display_name = claims.get("name") or graph.get("displayName") or ""
    given = claims.get("given_name") or graph.get("givenName") or ""
    family = claims.get("family_name") or graph.get("surname") or ""

    if (not given and not family) and display_name:
        parts = display_name.split()
        given = parts[0] if parts else "Usuario"
        family = " ".join(parts[1:]) if len(parts) > 1 else ""

    email_norm = _norm_email(email)

    if not oid or not email_norm:
        return None

    return {
        "oid": oid,
        "email": email_norm,
        "display_name": display_name,
        "given": given or "Usuario",
        "family": family or "",
    }


def _assign_if_present(user, field_name, value, updated_fields=None):
    if not hasattr(user, field_name):
        return

    current = getattr(user, field_name, None)

    if updated_fields is None:
        setattr(user, field_name, value)
        return

    if current != value:
        setattr(user, field_name, value)
        updated_fields.append(field_name)


def _apply_claim_fields(user, claims, updated_fields=None):
    if hasattr(user, "ms_raw_claims"):
        _assign_if_present(user, "ms_raw_claims", claims, updated_fields)


def _apply_graph_fields(user, graph, updated_fields=None):
    if not graph or graph.get("_error"):
        return

    mapping = {
        "ms_job_title": graph.get("jobTitle"),
        "ms_department": graph.get("department"),
        "ms_office_location": graph.get("officeLocation"),
        "ms_graph_id": graph.get("id"),
        "ms_display_name": graph.get("displayName"),
        "ms_given_name": graph.get("givenName"),
        "ms_surname": graph.get("surname"),
        "ms_mail": graph.get("mail"),
        "ms_user_principal_name": graph.get("userPrincipalName"),
        "ms_business_phones": graph.get("businessPhones"),
        "ms_mobile_phone": graph.get("mobilePhone"),
        "ms_raw_graph": graph,
    }

    for field_name, value in mapping.items():
        _assign_if_present(user, field_name, value, updated_fields)

    if hasattr(user, "ms_last_sync"):
        _assign_if_present(user, "ms_last_sync", timezone.now(), updated_fields)


def sync_microsoft_user(user_model, *, identity, claims, graph):
    email_norm = identity["email"]
    oid = identity["oid"]
    given = identity["given"]
    family = identity["family"]

    with transaction.atomic():
        user = user_model.objects.select_for_update().filter(
            email__iexact=email_norm
        ).first()

        if user is None:
            user = user_model(
                email=email_norm,
                nombres=given or "Usuario",
                apellidos=family or "",
                rol="autor",
                microsoft_id=oid,
                auth_source="microsoft",
                is_active=True,
            )

            if _is_admin_original(email_norm):
                user.is_staff = True

            user.set_unusable_password()
            _apply_claim_fields(user, claims)
            _apply_graph_fields(user, graph)
            user.save()

        else:
            updated_fields = []
            if getattr(user, "email", None) != email_norm:
                user.email = email_norm
                updated_fields.append("email")
            if getattr(user, "microsoft_id", None) != oid:
                user.microsoft_id = oid
                updated_fields.append("microsoft_id")
            if getattr(user, "auth_source", None) != "microsoft":
                user.auth_source = "microsoft"
                updated_fields.append("auth_source")
            if getattr(user, "rol", None) != "autor":
                user.rol = "autor"
                updated_fields.append("rol")
            if not getattr(user, "is_active", False):
                user.is_active = True
                updated_fields.append("is_active")
            if _is_admin_original(email_norm) and not getattr(user, "is_staff", False):
                user.is_staff = True
                updated_fields.append("is_staff")
            if given and getattr(user, "nombres", "") != given:
                user.nombres = given
                updated_fields.append("nombres")
            if family and getattr(user, "apellidos", "") != family:
                user.apellidos = family
                updated_fields.append("apellidos")

            _apply_claim_fields(user, claims, updated_fields)
            _apply_graph_fields(user, graph, updated_fields)

            if updated_fields:
                user.save(update_fields=list(dict.fromkeys(updated_fields)))

        asegurar_autor_para_usuario(user)
        return user


def _avatar_url(user):
    avatar = getattr(user, "avatar", None)
    if not avatar: return None
    name = getattr(avatar, "name", None)
    if not name: return None
    try: return avatar.url
    except Exception: return None


def build_microsoft_auth_payload(user):
    refresh = RefreshToken.for_user(user)
    return {
        "tokens": {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        "user": {
            "id": user.id,
            "email": user.email,
            "nombres": user.nombres,
            "apellidos": user.apellidos,
            "rol": user.rol,
            "auth_source": getattr(user, "auth_source", "local"),
            "perfil_completo": bool(getattr(user, "perfil_completo", False)),
            "is_staff": bool(getattr(user, "is_staff", False)),
            "is_superuser": bool(getattr(user, "is_superuser", False)),
            "es_admin": bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)),
            "facultad_id": getattr(user, "facultad_id", None),
            "carrera_id": getattr(user, "carrera_id", None),
            "avatar_url": _avatar_url(user),
            # Datos institucionales adicionales para el frontend
            "ms_job_title": getattr(user, "ms_job_title", None),
            "ms_department": getattr(user, "ms_department", None),
            "ms_office_location": getattr(user, "ms_office_location", None),
        },
    }