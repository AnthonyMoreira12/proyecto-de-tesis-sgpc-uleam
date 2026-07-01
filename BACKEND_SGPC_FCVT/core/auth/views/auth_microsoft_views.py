"""
Views de autenticación con Microsoft 365.
"""

import secrets
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import redirect

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.auth.services.auth_microsoft_services import (
    build_microsoft_authorization_url,
    exchange_microsoft_authorization_code,
    fetch_graph_profile,
    resolve_microsoft_identity,
    is_allowed_institutional_email,
    sync_microsoft_user,
    build_microsoft_auth_payload,
)

User = get_user_model()


class MicrosoftLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        state = str(uuid.uuid4())
        cache.set(f"ms_state:{state}", True, timeout=300)

        auth_url = build_microsoft_authorization_url(state=state)
        return redirect(auth_url)


class MicrosoftCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        frontend_login = f"{settings.FRONTEND_URL.rstrip('/')}/login"

        if request.GET.get("error"):
            return redirect(f"{frontend_login}?ms_error=Error%20Microsoft")

        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code or not state:
            return redirect(f"{frontend_login}?ms_error=Faltan%20parametros")

        if not cache.get(f"ms_state:{state}"):
            return redirect(f"{frontend_login}?ms_error=State%20invalido")

        cache.delete(f"ms_state:{state}")

        result = exchange_microsoft_authorization_code(code=code)
        if not result or "error" in result:
            return redirect(f"{frontend_login}?ms_error=No%20token")

        claims = result.get("id_token_claims") or {}
        access_token = result.get("access_token")
        graph = fetch_graph_profile(access_token) if access_token else {}

        identity = resolve_microsoft_identity(claims=claims, graph=graph)
        if not identity:
            return redirect(f"{frontend_login}?ms_error=Claims%20invalidos")

        if not is_allowed_institutional_email(identity["email"]):
            return redirect(f"{frontend_login}?ms_error=Acceso%20no%20permitido")

        user = sync_microsoft_user(
            User,
            identity=identity,
            claims=claims,
            graph=graph,
        )

        payload = build_microsoft_auth_payload(user)

        one_time_code = secrets.token_urlsafe(32)
        cache.set(f"ms_exchange:{one_time_code}", payload, timeout=120)

        return redirect(f"{frontend_login}?ms_code={one_time_code}")


class MicrosoftExchangeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response(
                {"detail": "Falta code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = cache.get(f"ms_exchange:{code}")
        if not data:
            return Response(
                {"detail": "Code inválido o expirado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        cache.delete(f"ms_exchange:{code}")
        return Response(data, status=status.HTTP_200_OK)