"""Expone el request actual a las señales de auditoría.

No registra nada por sí mismo. Solo conserva el objeto request durante
el ciclo de la petición para que los signals puedan conocer al actor,
IP, ruta y método una vez DRF haya resuelto la autenticación JWT.
"""

from core.auditoria.context import reset_current_request, set_current_request


class AuditoriaRequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = set_current_request(request)
        try:
            return self.get_response(request)
        finally:
            reset_current_request(token)
