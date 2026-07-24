"""ViewSet administrativo de autores."""

from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.admin.selectors.admin_autores_selectors import (
    ORDERING_MAP,
    admin_autores_base_queryset,
    filter_admin_autores_queryset,
)
from core.admin.serializers.admin_autores_serializers import (
    AdminAutorSerializer,
)
from core.permisos.es_admin import EsAdmin


TRUE_VALUES = {"1", "true", "yes", "y", "on", "si", "sí"}
FALSE_VALUES = {"0", "false", "no", "n", "off"}


def _optional_bool(value, field):
    if value in (None, ""):
        return None

    normalized = str(value).strip().lower()

    if normalized in TRUE_VALUES:
        return True

    if normalized in FALSE_VALUES:
        return False

    raise ValidationError(
        {field: "El valor debe ser verdadero o falso."}
    )


def _optional_id(value, field):
    if value in (None, ""):
        return None

    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError(
            {field: "Debe ser un entero positivo."}
        ) from exc

    if parsed <= 0:
        raise ValidationError(
            {field: "Debe ser un entero positivo."}
        )

    return parsed


class AdminAutorViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    serializer_class = AdminAutorSerializer
    queryset = admin_autores_base_queryset()
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        base = admin_autores_base_queryset()

        if self.action == "retrieve":
            return base

        params = self.request.query_params
        query = str(params.get("q", "")).strip()

        if len(query) > 200:
            raise ValidationError(
                {"q": "La búsqueda no puede superar 200 caracteres."}
            )

        ordering = str(
            params.get("ordering", "")
        ).strip().lower()

        if ordering and ordering not in ORDERING_MAP:
            raise ValidationError(
                {"ordering": "El ordenamiento no es válido."}
            )

        return filter_admin_autores_queryset(
            base,
            q=query,
            solo_con_usuario=_optional_bool(
                params.get("solo_con_usuario"),
                "solo_con_usuario",
            ),
            autor_id=_optional_id(
                params.get("autor_id"),
                "autor_id",
            ),
            usuario_id=_optional_id(
                params.get("usuario_id"),
                "usuario_id",
            ),
            es_externo=_optional_bool(
                params.get("es_externo"),
                "es_externo",
            ),
            usuario_activo=_optional_bool(
                params.get("usuario_activo"),
                "usuario_activo",
            ),
            ordering=ordering,
        )
