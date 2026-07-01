# ViewSet administrativo de autores:
# permite listar y consultar autores desde el panel admin, aplicando autenticación JWT,
# permisos de administrador y filtros por búsqueda, usuario vinculado, autor o usuario específico.

from rest_framework import permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.admin.selectors.admin_autores_selectors import (
    admin_autores_base_queryset,
    filter_admin_autores_queryset,
)
from core.admin.serializers.admin_autores_serializers import AdminAutorSerializer
from core.permisos.es_admin import EsAdmin


def _parse_bool(value):
    if value is None:
        return None

    s = str(value).strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return None


class AdminAutorViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    serializer_class = AdminAutorSerializer
    queryset = admin_autores_base_queryset()
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        q = self.request.query_params.get("q", "")
        solo_con_usuario = _parse_bool(self.request.query_params.get("solo_con_usuario"))
        autor_id = self.request.query_params.get("autor_id")
        usuario_id = self.request.query_params.get("usuario_id")

        return filter_admin_autores_queryset(
            admin_autores_base_queryset(),
            q=q,
            solo_con_usuario=solo_con_usuario,
            autor_id=autor_id,
            usuario_id=usuario_id,
        )