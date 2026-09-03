# ============================================================
# SGPC ULEAM — Rutas principales
# ============================================================

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# ============================================================
# VIEWSETS (CRUD)
# ============================================================

# Publicaciones
from core.publicaciones.views.publicaciones_ponencia_viewsets import (
    PonenciaViewSet,
)
from core.publicaciones.views.publicaciones_libro_viewsets import (
    LibroViewSet,
)
from core.publicaciones.views.publicaciones_capitulo_libro_viewsets import (
    CapituloLibroViewSet,
)
from core.publicaciones.views.publicaciones_archivos_viewsets import (
    PublicacionArchivoViewSet,
)

from core.publicaciones.solicitudes.solicitudes_modificacion_views import (
    SolicitudModificacionPublicacionViewSet,
    AdminSolicitudModificacionPublicacionViewSet,
)

# Base
from core.banners.views.banners_banner_viewsets import BannerViewSet
from core.proyectos.views.proyectos_proyecto_viewsets import ProyectoViewSet
from core.autores.views.autores_autor_viewsets import AutoresViewSet
from core.catalogos.views.catalogos_selects_viewsets import SelectsViewSet
from core.notificaciones.views.notificaciones_viewsets import (
    NotificacionViewSet,
)
from core.comunicaciones.views.comunicaciones_viewsets import (
    ComunicacionGlobalViewSet,
)

# Admin
from core.admin.views.admin_catalogos_views import (
    AdminFacultadViewSet,
    AdminCarreraViewSet,
    AdminSedeViewSet,
    AdminCarreraSedeViewSet,
)
from core.admin.views.admin_usuarios_views import AdminUsuariosViewSet
from core.admin.views.admin_autores_views import AdminAutorViewSet
from core.admin.views.admin_publicaciones_views import (
    AdminPublicacionViewSet,
)

# Actualizaciones globales / Auditoría
from core.actualizaciones.views.actualizaciones_viewsets import (
    AdminCampaniaActualizacionViewSet,
    MisActualizacionesViewSet,
)
from core.auditoria.views.auditoria_viewsets import (
    AdminAuditoriaSistemaViewSet,
)

# ============================================================
# APIViews (consultas / endpoints específicos)
# ============================================================

# Publicaciones
from core.publicaciones.views.publicaciones_listado_views import (
    PublicacionAvailableYearsAPIView,
    PublicacionListAPIView,
)
from core.publicaciones.views.publicaciones_mis_listados_views import (
    MyPublicacionAvailableYearsAPIView,
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
from core.publicaciones.views.publicaciones_estado_views import (
    PublicacionEnviarRevisionAPIView,
    PublicacionReenviarRevisionAPIView,
)
from core.publicaciones.views.publicaciones_duplicados_views import (
    PublicacionValidarDuplicadosAPIView,
)
from core.publicaciones.views.publicaciones_prevalidacion_views import (
    PublicacionPrevalidarAPIView,
)

from core.publicaciones.views.publicaciones_integridad_admin_views import (
    AdminIntegridadDocumentalDiagnosticoAPIView,
    AdminIntegridadDocumentalBackfillAPIView,
)

from core.migracion_produccion.views.migracion_produccion_views import (
    AdminPreparacionProduccionDiagnosticoAPIView,
    AdminPreparacionProduccionNormalizarAPIView,
    AdminPreparacionProduccionVerificarAPIView,
)

# Reportes
from core.reportes.views.reportes_publicaciones_views import (
    ExportarPublicacionesExcelView,
    ExportarPublicacionesPdfView,
    VistaPreviaPublicacionesExcelView,
)
from core.reportes.views.reportes_gestion_views import (
    ExportarReporteGestionExcelView,
    VistaPreviaReporteGestionView,
)
from core.reportes.views.reportes_produccion_views import (
    ExportarMiReporteProduccionExcelView,
    ExportarMiReporteProduccionPdfView,
    ExportarReporteProduccionAdminExcelView,
    VistaPreviaMiReporteProduccionView,
    VistaPreviaReporteProduccionAdminView,
)

# Búsqueda
from core.busqueda.views.busqueda_general_views import (
    BusquedaGeneralAPIView,
)

# Scholar
from core.scholar.views.scholar_publicaciones_views import (
    PublicacionesScholarAPIView,
)
from core.scholar.views.scholar_perfiles_views import (
    PerfilesScholarAPIView,
    PerfilScholarDetailAPIView,
    PerfilScholarMeAPIView,
)
from core.scholar.views.scholar_sugerencias_views import (
    ScholarSuggestAPIView,
)
from core.scholar.views.scholar_tipos_publicacion_views import (
    TiposPublicacionListAPIView,
)

# Dashboard
from core.dashboard import (
    DashboardResumenView,
    DashboardReporteExcelView,
    DashboardReportePdfView,
)
from core.dashboard_gestion import (
    DashboardGestionView,
)

# Auth
from core.auth.views.auth_login_views import LoginView
from core.auth.views.auth_logout_views import LogoutView
from core.auth.views.auth_register_views import RegisterView
from core.auth.views.auth_refresh_token_views import RefreshTokenView
from core.auth.views.auth_profile_views import (
    ProfileView,
    ProfileEditExtensionRequestView,
    AdminProfileEditExtensionRequestsView,
    AdminProfileEditExtensionRequestDetailView,
)
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
router.register(
    r"ponencias",
    PonenciaViewSet,
    basename="ponencias",
)

router.register(
    r"libros",
    LibroViewSet,
    basename="libros",
)

router.register(
    r"capitulos-libro",
    CapituloLibroViewSet,
    basename="capitulos-libro",
)

router.register(
    r"archivos-publicacion",
    PublicacionArchivoViewSet,
    basename="archivos-publicacion",
)

router.register(
    r"solicitudes-modificacion-publicaciones",
    SolicitudModificacionPublicacionViewSet,
    basename="solicitudes-modificacion-publicaciones",
)

# Base
router.register(
    r"banners",
    BannerViewSet,
    basename="banners",
)

router.register(
    r"proyectos",
    ProyectoViewSet,
    basename="proyectos",
)

router.register(
    r"autores",
    AutoresViewSet,
    basename="autores",
)

router.register(
    r"notificaciones",
    NotificacionViewSet,
    basename="notificaciones",
)

router.register(
    r"comunicaciones-globales",
    ComunicacionGlobalViewSet,
    basename="comunicaciones-globales",
)

# Admin
router.register(
    r"admin/facultades",
    AdminFacultadViewSet,
    basename="admin-facultades",
)

router.register(
    r"admin/sedes",
    AdminSedeViewSet,
    basename="admin-sedes",
)

router.register(
    r"admin/carreras-sedes",
    AdminCarreraSedeViewSet,
    basename="admin-carreras-sedes",
)

router.register(
    r"admin/carreras",
    AdminCarreraViewSet,
    basename="admin-carreras",
)

router.register(
    r"admin/usuarios",
    AdminUsuariosViewSet,
    basename="admin-usuarios",
)

router.register(
    r"admin/autores",
    AdminAutorViewSet,
    basename="admin-autores",
)

router.register(
    r"admin/publicaciones",
    AdminPublicacionViewSet,
    basename="admin-publicaciones",
)

router.register(
    r"admin/solicitudes-modificacion-publicaciones",
    AdminSolicitudModificacionPublicacionViewSet,
    basename="admin-solicitudes-modificacion-publicaciones",
)

router.register(
    r"admin/actualizaciones",
    AdminCampaniaActualizacionViewSet,
    basename="admin-actualizaciones",
)

router.register(
    r"admin/auditoria",
    AdminAuditoriaSistemaViewSet,
    basename="admin-auditoria",
)

router.register(
    r"mis-actualizaciones",
    MisActualizacionesViewSet,
    basename="mis-actualizaciones",
)

# ============================================================
# URLPATTERNS — Rutas finales
# ============================================================

urlpatterns = [
    # ========================================================
    # AUTH
    # ========================================================
    path(
        "auth/login/",
        LoginView.as_view(),
        name="auth-login",
    ),

    path(
        "auth/logout/",
        LogoutView.as_view(),
        name="auth-logout",
    ),

    path(
        "auth/register/",
        RegisterView.as_view(),
        name="auth-register",
    ),

    path(
        "auth/refresh/",
        RefreshTokenView.as_view(),
        name="auth-refresh",
    ),

    path(
        "auth/profile/",
        ProfileView.as_view(),
        name="auth-profile",
    ),

    # Solicitud de extensión del plazo de edición.
    # Este endpoint funciona aunque el plazo ya haya finalizado.
    path(
        "auth/profile/solicitar-extension/",
        ProfileEditExtensionRequestView.as_view(),
        name="auth-profile-solicitar-extension",
    ),

    # Gestión administrativa de solicitudes de extensión.
    path(
        "admin/profile-extension-requests/",
        AdminProfileEditExtensionRequestsView.as_view(),
        name="admin-profile-extension-requests",
    ),

    path(
        "admin/profile-extension-requests/<int:pk>/",
        AdminProfileEditExtensionRequestDetailView.as_view(),
        name="admin-profile-extension-request-detail",
    ),

    path(
        "auth/avatar/",
        UpdateAvatarView.as_view(),
        name="auth-avatar",
    ),

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

    # ========================================================
    # CATÁLOGOS
    # ========================================================
    path(
        "catalogos/tipos-publicacion/",
        TiposPublicacionListAPIView.as_view(),
        name="catalogos-tipos-publicacion",
    ),

    # ========================================================
    # DASHBOARD
    # ========================================================
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
        "dashboard/gestion/",
        DashboardGestionView.as_view(),
        name="dashboard-gestion",
    ),

    path(
        "dashboard/reporte/excel/",
        DashboardReporteExcelView.as_view(),
        name="dashboard-reporte-excel",
    ),

    path(
        "dashboard/reporte/pdf/",
        DashboardReportePdfView.as_view(),
        name="dashboard-reporte-pdf",
    ),

    # ========================================================
    # PUBLICACIONES
    # ========================================================
    path(
        "publicaciones/anios-disponibles/",
        PublicacionAvailableYearsAPIView.as_view(),
        name="publicaciones-anios-disponibles",
    ),

    path(
        "publicaciones/mias/anios-disponibles/",
        MyPublicacionAvailableYearsAPIView.as_view(),
        name="publicaciones-mias-anios-disponibles",
    ),

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
        "publicaciones/validar-duplicados/",
        PublicacionValidarDuplicadosAPIView.as_view(),
        name="publicacion-validar-duplicados",
    ),

    path(
        "publicaciones/prevalidar/",
        PublicacionPrevalidarAPIView.as_view(),
        name="publicacion-prevalidar",
    ),

    path(
        "publicaciones/<int:id>/enviar-revision/",
        PublicacionEnviarRevisionAPIView.as_view(),
        name="publicacion-enviar-revision",
    ),

    path(
        "publicaciones/<int:id>/reenviar-revision/",
        PublicacionReenviarRevisionAPIView.as_view(),
        name="publicacion-reenviar-revision",
    ),

    path(
        "publicaciones/<int:id>/",
        PublicacionDetailAPIView.as_view(),
        name="publicacion-detalle",
    ),

    # ========================================================
    # REPORTES
    # ========================================================
    path(
        "reportes/publicaciones/excel/",
        ExportarPublicacionesExcelView.as_view(),
        name="exportar-publicaciones-excel",
    ),

    path(
        "reportes/publicaciones/pdf/",
        ExportarPublicacionesPdfView.as_view(),
        name="exportar-publicaciones-pdf",
    ),

    path(
        "reportes/publicaciones/excel/preview/",
        VistaPreviaPublicacionesExcelView.as_view(),
        name="preview-publicaciones-excel",
    ),

    path(
        "reportes/gestion/preview/",
        VistaPreviaReporteGestionView.as_view(),
        name="preview-reporte-gestion",
    ),

    path(
        "reportes/gestion/excel/",
        ExportarReporteGestionExcelView.as_view(),
        name="exportar-reporte-gestion-excel",
    ),

    # Producción científica aprobada - alcance institucional
    path(
        "reportes/produccion/preview/",
        VistaPreviaReporteProduccionAdminView.as_view(),
        name="preview-reporte-produccion-admin",
    ),

    path(
        "reportes/produccion/excel/",
        ExportarReporteProduccionAdminExcelView.as_view(),
        name="exportar-reporte-produccion-admin-excel",
    ),

    # Producción científica del usuario autenticado. El backend determina
    # el docente desde request.user; no recibe IDs de usuario desde Vue.
    path(
        "reportes/mios/preview/",
        VistaPreviaMiReporteProduccionView.as_view(),
        name="preview-mi-reporte-produccion",
    ),

    path(
        "reportes/mios/excel/",
        ExportarMiReporteProduccionExcelView.as_view(),
        name="exportar-mi-reporte-produccion-excel",
    ),

    path(
        "reportes/mios/pdf/",
        ExportarMiReporteProduccionPdfView.as_view(),
        name="exportar-mi-reporte-produccion-pdf",
    ),

    # ========================================================
    # BÚSQUEDA
    # ========================================================
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

    # ========================================================
    # SCHOLAR
    # ========================================================
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

    # ========================================================
    # SELECTS DINÁMICOS
    # ========================================================
    path(
        "selects/sedes/",
        SelectsViewSet.as_view(
            {
                "get": "get_sedes",
            }
        ),
        name="select-sedes",
    ),

    path(
        "selects/facultades/",
        SelectsViewSet.as_view(
            {
                "get": "get_facultades",
            }
        ),
        name="select-facultades",
    ),

    path(
        "selects/carreras/",
        SelectsViewSet.as_view(
            {
                "get": "get_carreras",
            }
        ),
        name="select-carreras-filtros",
    ),

    path(
        "selects/carreras/sede/<int:sede_id>/",
        SelectsViewSet.as_view(
            {
                "get": "get_carreras",
            }
        ),
        name="select-carreras-sede",
    ),

    path(
        "selects/carreras/<int:facultad_id>/",
        SelectsViewSet.as_view(
            {
                "get": "get_carreras",
            }
        ),
        name="select-carreras",
    ),

    path(
        "selects/proyectos/<int:carrera_id>/",
        SelectsViewSet.as_view(
            {
                "get": "get_proyectos",
            }
        ),
        name="select-proyectos",
    ),

    path(
        "selects/paises/",
        SelectsViewSet.as_view(
            {
                "get": "get_paises",
            }
        ),
        name="select-paises",
    ),

    path(
        "selects/ciudades/<int:pais_id>/",
        SelectsViewSet.as_view(
            {
                "get": "get_ciudades",
            }
        ),
        name="select-ciudades",
    ),

    path(
        "selects/areas/",
        SelectsViewSet.as_view(
            {
                "get": "get_areas",
            }
        ),
        name="select-areas",
    ),

    path(
        "selects/subareas/<int:area_id>/",
        SelectsViewSet.as_view(
            {
                "get": "get_subareas",
            }
        ),
        name="select-subareas",
    ),

    path(
        "selects/autores/",
        SelectsViewSet.as_view(
            {
                "get": "get_autores",
            }
        ),
        name="select-autores",
    ),

    # ========================================================
    # ROUTER
    # ========================================================
    path(
        "",
        include(router.urls),
    ),
    path(
        "admin/integridad-documental/diagnostico/",
        AdminIntegridadDocumentalDiagnosticoAPIView.as_view(),
        name="admin-integridad-documental-diagnostico",
    ),
    path(
        "admin/integridad-documental/backfill/",
        AdminIntegridadDocumentalBackfillAPIView.as_view(),
        name="admin-integridad-documental-backfill",
    ),
    path(
        "admin/preparacion-produccion/diagnostico/",
        AdminPreparacionProduccionDiagnosticoAPIView.as_view(),
        name="admin-preparacion-produccion-diagnostico",
    ),
    path(
        "admin/preparacion-produccion/normalizar/",
        AdminPreparacionProduccionNormalizarAPIView.as_view(),
        name="admin-preparacion-produccion-normalizar",
    ),
    path(
        "admin/preparacion-produccion/verificar/",
        AdminPreparacionProduccionVerificarAPIView.as_view(),
        name="admin-preparacion-produccion-verificar",
    ),

]