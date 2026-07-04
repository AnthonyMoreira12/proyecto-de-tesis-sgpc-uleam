# core/urls.py
# ============================================================
# SGPC ULEAM — Rutas principales
# ============================================================

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# ============================================================
# VIEWSETS (CRUD)
# ============================================================

# Publicaciones
from core.publicaciones.views.publicaciones_ponencia_viewsets import PonenciaViewSet
from core.publicaciones.views.publicaciones_libro_viewsets import LibroViewSet
from core.publicaciones.views.publicaciones_capitulo_libro_viewsets import (
    CapituloLibroViewSet,
)
from core.publicaciones.views.publicaciones_archivos_viewsets import (
    PublicacionArchivoViewSet,
)

# Base
from core.banners.views.banners_banner_viewsets import BannerViewSet
from core.proyectos.views.proyectos_proyecto_viewsets import ProyectoViewSet
from core.autores.views.autores_autor_viewsets import AutoresViewSet
from core.catalogos.views.catalogos_selects_viewsets import SelectsViewSet

# Admin
from core.admin.views.admin_catalogos_views import (
    AdminFacultadViewSet,
    AdminCarreraViewSet,
)
from core.admin.views.admin_usuarios_views import AdminUsuariosViewSet
from core.admin.views.admin_autores_views import AdminAutorViewSet
from core.admin.views.admin_publicaciones_views import AdminPublicacionViewSet

# ============================================================
# APIViews (consultas / endpoints específicos)
# ============================================================

# Publicaciones
from core.publicaciones.views.publicaciones_listado_views import (
    PublicacionListAPIView,
)
from core.publicaciones.views.publicaciones_mis_listados_views import (
    MyPublicacionListAPIView,
)
from core.publicaciones.views.publicaciones_detalle_views import (
    PublicacionDetailAPIView,
)
from core.publicaciones.views.publicaciones_articulo_create_views import (
    ArticuloCreateAPIView,
)
from core.publicaciones.views.publicaciones_pdf_views import (
    PublicacionPdfInlineAPIView,
)

# Reportes
from core.reportes.views.reportes_publicaciones_views import (
    ExportarPublicacionesExcelView,
)

# Búsqueda
from core.busqueda.views.busqueda_general_views import BusquedaGeneralAPIView

# Scholar
from core.scholar.views.scholar_publicaciones_views import PublicacionesScholarAPIView
from core.scholar.views.scholar_perfiles_views import (
    PerfilesScholarAPIView,
    PerfilScholarDetailAPIView,
    PerfilScholarMeAPIView,
)
from core.scholar.views.scholar_sugerencias_views import ScholarSuggestAPIView
from core.scholar.views.scholar_tipos_publicacion_views import TiposPublicacionListAPIView

# Dashboard
from core.dashboard import (
    DashboardResumenView,
    DashboardReporteExcelView,
)

# Auth
from core.auth.views.auth_login_views import LoginView
from core.auth.views.auth_logout_views import LogoutView
from core.auth.views.auth_register_views import RegisterView
from core.auth.views.auth_refresh_token_views import RefreshTokenView
from core.auth.views.auth_profile_views import ProfileView
from core.auth.views.auth_avatar_views import UpdateAvatarView
from core.auth.views.auth_password_reset_views import (
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from core.auth.views.auth_microsoft_views import (
    MicrosoftLoginView,
    MicrosoftCallbackView,
    MicrosoftExchangeView,
)

# ============================================================
# ROUTER — ViewSets automáticos
# ============================================================

router = DefaultRouter()

# Publicaciones
router.register(r"ponencias", PonenciaViewSet, basename="ponencias")
router.register(r"libros", LibroViewSet, basename="libros")
router.register(r"capitulos-libro", CapituloLibroViewSet, basename="capitulos-libro")
router.register(
    r"archivos-publicacion",
    PublicacionArchivoViewSet,
    basename="archivos-publicacion",
)

# Base
router.register(r"banners", BannerViewSet, basename="banners")
router.register(r"proyectos", ProyectoViewSet, basename="proyectos")
router.register(r"autores", AutoresViewSet, basename="autores")

# Admin
router.register(r"admin/facultades", AdminFacultadViewSet, basename="admin-facultades")
router.register(r"admin/carreras", AdminCarreraViewSet, basename="admin-carreras")
router.register(r"admin/usuarios", AdminUsuariosViewSet, basename="admin-usuarios")
router.register(r"admin/autores", AdminAutorViewSet, basename="admin-autores")
router.register(
    r"admin/publicaciones",
    AdminPublicacionViewSet,
    basename="admin-publicaciones",
)

# ============================================================
# URLPATTERNS — Rutas finales
# ============================================================

urlpatterns = [
    # ----------------------------
    # Auth
    # ----------------------------
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/profile/", ProfileView.as_view(), name="auth-profile"),
    path("auth/avatar/", UpdateAvatarView.as_view(), name="auth-avatar"),
    path(
        "auth/password-reset/request/",
        PasswordResetRequestView.as_view(),
        name="auth-password-reset-request",
    ),
    path(
        "auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="auth-password-reset-confirm",
    ),
    path(
        "auth/microsoft/login/",
        MicrosoftLoginView.as_view(),
        name="ms-login",
    ),
    path(
        "auth/microsoft/callback/",
        MicrosoftCallbackView.as_view(),
        name="ms-callback",
    ),
    path(
        "auth/microsoft/exchange/",
        MicrosoftExchangeView.as_view(),
        name="ms-exchange",
    ),

    # ----------------------------
    # Catálogos
    # ----------------------------
    path(
        "catalogos/tipos-publicacion/",
        TiposPublicacionListAPIView.as_view(),
        name="catalogos-tipos-publicacion",
    ),

    # ----------------------------
    # Dashboard
    # ----------------------------
    path(
        "dashboard/",
        DashboardResumenView.as_view(),
        name="dashboard",
    ),
    path(
        "dashboard/resumen/",
        DashboardResumenView.as_view(),
        name="dashboard-resumen",
    ),
    path(
        "dashboard/reporte/excel/",
        DashboardReporteExcelView.as_view(),
        name="dashboard-reporte-excel",
    ),

    # ----------------------------
    # Publicaciones
    # ----------------------------
    path(
        "publicaciones/",
        PublicacionListAPIView.as_view(),
        name="publicaciones-list",
    ),
    path(
        "publicaciones/mias/",
        MyPublicacionListAPIView.as_view(),
        name="publicaciones-mias",
    ),
    path(
        "publicaciones/articulos/crear/",
        ArticuloCreateAPIView.as_view(),
        name="articulo-crear",
    ),
    path(
        "publicaciones/<int:id>/pdf/",
        PublicacionPdfInlineAPIView.as_view(),
        name="publicacion-pdf-inline",
    ),
    path(
        "publicaciones/<int:id>/",
        PublicacionDetailAPIView.as_view(),
        name="publicacion-detalle",
    ),

    # ----------------------------
    # Reportes
    # ----------------------------
    path(
        "reportes/publicaciones/excel/",
        ExportarPublicacionesExcelView.as_view(),
        name="exportar-publicaciones-excel",
    ),

    # ----------------------------
    # Búsqueda
    # ----------------------------
    path(
        "busqueda/",
        BusquedaGeneralAPIView.as_view(),
        name="busqueda-general",
    ),
    path(
        "busqueda/publicaciones/",
        PublicacionesScholarAPIView.as_view(),
        name="publicaciones-scholar",
    ),

    # ----------------------------
    # Scholar
    # ----------------------------
    path(
        "scholar/perfiles/",
        PerfilesScholarAPIView.as_view(),
        name="scholar-perfiles",
    ),
    path(
        "scholar/perfiles/me/",
        PerfilScholarMeAPIView.as_view(),
        name="scholar-perfil-me",
    ),
    path(
        "scholar/perfiles/<int:id>/",
        PerfilScholarDetailAPIView.as_view(),
        name="scholar-perfil-detalle",
    ),
    path(
        "scholar/suggest/",
        ScholarSuggestAPIView.as_view(),
        name="scholar-suggest",
    ),

    # ----------------------------
    # Selects dinámicos
    # ----------------------------
    path(
        "selects/facultades/",
        SelectsViewSet.as_view({"get": "get_facultades"}),
        name="select-facultades",
    ),
    path(
        "selects/carreras/<int:facultad_id>/",
        SelectsViewSet.as_view({"get": "get_carreras"}),
        name="select-carreras",
    ),
    path(
        "selects/proyectos/<int:carrera_id>/",
        SelectsViewSet.as_view({"get": "get_proyectos"}),
        name="select-proyectos",
    ),
    path(
        "selects/paises/",
        SelectsViewSet.as_view({"get": "get_paises"}),
        name="select-paises",
    ),
    path(
        "selects/ciudades/<int:pais_id>/",
        SelectsViewSet.as_view({"get": "get_ciudades"}),
        name="select-ciudades",
    ),
    path(
        "selects/areas/",
        SelectsViewSet.as_view({"get": "get_areas"}),
        name="select-areas",
    ),
    path(
        "selects/subareas/<int:area_id>/",
        SelectsViewSet.as_view({"get": "get_subareas"}),
        name="select-subareas",
    ),
    path(
        "selects/autores/",
        SelectsViewSet.as_view({"get": "get_autores"}),
        name="select-autores",
    ),

    # ----------------------------
    # Router
    # ----------------------------
    path("", include(router.urls)),
]