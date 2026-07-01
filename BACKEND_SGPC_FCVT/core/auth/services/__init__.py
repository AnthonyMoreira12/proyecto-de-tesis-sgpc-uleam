from .auth_author_sync_services import asegurar_autor_para_usuario
from .auth_microsoft_services import (
    build_microsoft_authorization_url,
    exchange_microsoft_authorization_code,
    fetch_graph_profile,
    resolve_microsoft_identity,
    is_allowed_institutional_email,
    sync_microsoft_user,
    build_microsoft_auth_payload,
)
from .auth_profile_services import (
    ProfileEditServiceError,
    ensure_profile_edit_allowed,
    register_failed_profile_attempt,
    finalize_profile_update,
)

__all__ = [
    "asegurar_autor_para_usuario",
    "build_microsoft_authorization_url",
    "exchange_microsoft_authorization_code",
    "fetch_graph_profile",
    "resolve_microsoft_identity",
    "is_allowed_institutional_email",
    "sync_microsoft_user",
    "build_microsoft_auth_payload",
    "ProfileEditServiceError",
    "ensure_profile_edit_allowed",
    "register_failed_profile_attempt",
    "finalize_profile_update",
]