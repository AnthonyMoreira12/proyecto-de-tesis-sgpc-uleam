from django.db.models import Max
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.banners.serializers.banners_banner_serializers import (
    BannerConfiguracionSerializer,
    BannerSerializer,
)
from core.models.banners import (
    DEFAULT_BANNER_EYEBROW,
    DEFAULT_BANNER_RECENT_LABEL,
    DEFAULT_BANNER_TEXT,
    DEFAULT_BANNER_TITLE,
    DISPLAY_MODE_DEFAULT,
    MEDIA_PANE_WIDTH_DEFAULT,
    STAGE_HEIGHT_DEFAULT,
    STAGE_WIDTH_DEFAULT,
    Banner,
    BannerConfiguracion,
)
from core.permisos.es_admin import EsAdmin


class BannerViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = BannerSerializer
    queryset = Banner.objects.all().order_by("-created_at", "-id")
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), EsAdmin()]

        if self.action == "config" and self.request.method.upper() in ["PUT", "PATCH"]:
            return [permissions.IsAuthenticated(), EsAdmin()]

        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def _banner_table_ready(self):
        try:
            list(Banner.objects.values_list("id", flat=True)[:1])
            return True
        except (ProgrammingError, OperationalError):
            return False

    def _config_table_ready(self):
        try:
            BannerConfiguracion.get_solo()
            return True
        except (ProgrammingError, OperationalError):
            return False

    def _tables_unavailable_response(
        self,
        detail="Las tablas de banners aún no han sido migradas.",
    ):
        response = Response(
            {"detail": detail},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        return self._apply_no_cache_headers(response)

    def _default_config_payload(self):
        return {
            "eyebrow": DEFAULT_BANNER_EYEBROW,
            "title": DEFAULT_BANNER_TITLE,
            "text": DEFAULT_BANNER_TEXT,
            "recentLabel": DEFAULT_BANNER_RECENT_LABEL,
            "stageWidth": STAGE_WIDTH_DEFAULT,
            "stageHeight": STAGE_HEIGHT_DEFAULT,
            "mediaPaneWidth": MEDIA_PANE_WIDTH_DEFAULT,
            "displayMode": DISPLAY_MODE_DEFAULT,
            "created_at": None,
            "updated_at": None,
        }

    def _apply_no_cache_headers(self, response):
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response

    def get_queryset(self):
        try:
            list(Banner.objects.values_list("id", flat=True)[:1])
            return Banner.objects.all().order_by("-created_at", "-id")
        except (ProgrammingError, OperationalError):
            return Banner.objects.none()

    def list(self, request, *args, **kwargs):
        if not self._banner_table_ready():
            return self._apply_no_cache_headers(Response([], status=status.HTTP_200_OK))

        response = super().list(request, *args, **kwargs)
        return self._apply_no_cache_headers(response)

    def retrieve(self, request, *args, **kwargs):
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        response = super().retrieve(request, *args, **kwargs)
        return self._apply_no_cache_headers(response)

    def create(self, request, *args, **kwargs):
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        response = super().create(request, *args, **kwargs)
        return self._apply_no_cache_headers(response)

    def update(self, request, *args, **kwargs):
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        response = super().update(request, *args, **kwargs)
        return self._apply_no_cache_headers(response)

    def partial_update(self, request, *args, **kwargs):
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        response = super().partial_update(request, *args, **kwargs)
        return self._apply_no_cache_headers(response)

    def destroy(self, request, *args, **kwargs):
        if not self._banner_table_ready():
            return self._tables_unavailable_response()

        response = super().destroy(request, *args, **kwargs)
        return self._apply_no_cache_headers(response)

    @action(detail=False, methods=["get"], url_path="status")
    def status(self, request):
        try:
            qs = self.get_queryset()
            total = qs.count()
            last_banner_updated = qs.aggregate(last=Max("updated_at")).get("last")

            config_updated = None
            if self._config_table_ready():
                config = BannerConfiguracion.get_solo()
                config_updated = getattr(config, "updated_at", None)

            version_parts = [str(total)]

            if last_banner_updated:
                version_parts.append(last_banner_updated.isoformat())

            if config_updated:
                version_parts.append(config_updated.isoformat())

            version = "|".join(version_parts)

            response = Response(
                {
                    "has_items": total > 0,
                    "total": total,
                    "version": version,
                }
            )
            return self._apply_no_cache_headers(response)
        except (ProgrammingError, OperationalError):
            response = Response(
                {
                    "has_items": False,
                    "total": 0,
                    "version": "",
                }
            )
            return self._apply_no_cache_headers(response)

    @action(detail=False, methods=["get", "patch"], url_path="config")
    def config(self, request):
        try:
            config = BannerConfiguracion.get_solo()
        except (ProgrammingError, OperationalError):
            if request.method.upper() == "GET":
                response = Response(
                    self._default_config_payload(),
                    status=status.HTTP_200_OK,
                )
                return self._apply_no_cache_headers(response)

            response = Response(
                {"detail": "Las tablas de banners aún no han sido migradas."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
            return self._apply_no_cache_headers(response)

        if request.method.upper() == "GET":
            serializer = BannerConfiguracionSerializer(
                config,
                context=self.get_serializer_context(),
            )
            response = Response(serializer.data)
            return self._apply_no_cache_headers(response)

        serializer = BannerConfiguracionSerializer(
            config,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )

        if not serializer.is_valid():
            print("❌ Errores PATCH /api/banners/config/:", serializer.errors)
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return self._apply_no_cache_headers(response)

        serializer.save()

        response = Response(serializer.data, status=status.HTTP_200_OK)
        return self._apply_no_cache_headers(response)