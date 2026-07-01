from .auth_avatar_views import UpdateAvatarView
from .auth_login_views import LoginView
from .auth_logout_views import LogoutView
from .auth_microsoft_views import (
    MicrosoftLoginView,
    MicrosoftCallbackView,
    MicrosoftExchangeView,
)
from .auth_password_reset_views import (
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from .auth_profile_views import ProfileView
from .auth_refresh_token_views import RefreshTokenView
from .auth_register_views import RegisterView

__all__ = [
    "UpdateAvatarView",
    "LoginView",
    "LogoutView",
    "MicrosoftLoginView",
    "MicrosoftCallbackView",
    "MicrosoftExchangeView",
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    "ProfileView",
    "RefreshTokenView",
    "RegisterView",
]