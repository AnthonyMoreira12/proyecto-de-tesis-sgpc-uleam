import {
  createRouter,
  createWebHistory,
} from "vue-router";

import {
  useUserStore,
} from "../scripts/stores/userStore";


/* =========================================================
   AUTENTICACIÓN
========================================================= */

import LoginView from
  "../autenticacion/login/LoginView.vue";

import RecuperarContrasenaView from
  "../autenticacion/recuperar-contrasena/RecuperarContrasenaView.vue";

import RestablecerContrasenaView from
  "../autenticacion/restablecer-contrasena/RestablecerContrasenaView.vue";


/* =========================================================
   INICIO
========================================================= */

import HomeWithAvisosView from
  "../inicio/home-with-avisos/HomeWithAvisosView.vue";


/* =========================================================
   PERFILES Y BÚSQUEDA ACADÉMICA
========================================================= */

import PerfilUsuarioView from
  "../perfiles/perfil-usuario/PerfilUsuarioView.vue";

import BusquedaView from
  "../perfiles/busqueda/BusquedaView.vue";

import PerfilAcademicoView from
  "../perfiles/perfil-academico/PerfilAcademicoView.vue";


/* =========================================================
   PREFERENCIAS
========================================================= */

import PreferenciasInterfazView from
  "../preferencias/preferencias-interfaz/PreferenciasInterfazView.vue";


/* =========================================================
   NOTIFICACIONES
========================================================= */

import NotificacionesView from
  "../notificaciones/NotificacionesView.vue";


/* =========================================================
   PUBLICACIONES
========================================================= */

import TiposPublicacionView from
  "../publicaciones/tipos-publicacion/TiposPublicacionView.vue";

import MisPublicacionesView from
  "../publicaciones/mis-publicaciones/MisPublicacionesView.vue";

import MisReportesView from
  "../reportes/mis-reportes/MisReportesView.vue";

import PublicacionesListadoView from
  "../publicaciones/listado-publicaciones/PublicacionesListadoView.vue";

import PublicacionDetalleView from
  "../publicaciones/detalle-publicacion/PublicacionDetalleView.vue";

import ArticuloAltoImpactoForm from
  "../publicaciones/articulo-alto-impacto/ArticuloAltoImpactoForm.vue";

import ArticuloRegionalForm from
  "../publicaciones/articulo-regional/ArticuloRegionalForm.vue";

import CapituloLibroForm from
  "../publicaciones/capitulo-libro/CapituloLibroForm.vue";

import LibroForm from
  "../publicaciones/libro/LibroForm.vue";

import PonenciaRegistro from
  "../publicaciones/ponencia/PonenciaRegistro.vue";


/* =========================================================
   PROYECTOS
========================================================= */

import ProyectosListadoView from
  "../proyectos/listado/ProyectosListadoView.vue";

import ProyectoFormularioView from
  "../proyectos/formulario/ProyectoFormularioView.vue";


/* =========================================================
   ADMINISTRACIÓN
========================================================= */

import PanelAdministracionView from
  "../administracion/panel-administracion/PanelAdministracionView.vue";

import AdminUsuariosView from
  "../administracion/gestion-usuarios/AdminUsuariosView.vue";

import AdminUsuarioDetalleView from
  "../administracion/gestion-usuarios/AdminUsuarioDetalleView.vue";

import AdminUsuarioEditarView from
  "../administracion/gestion-usuarios/AdminUsuarioEditarView.vue";

import GestionFacultadesCarrerasView from
  "../administracion/gestion-facultades-carreras/GestionFacultadesCarrerasView.vue";

import AdminPublicacionesView from
  "../administracion/gestion-publicaciones/AdminPublicacionesDelegadasView.vue";

import AdminPublicacionesUsuarioView from
  "../administracion/gestion-publicaciones/AdminPublicacionesUsuarioView.vue";

import AdminRevisionPublicacionesView from
  "../administracion/revision-publicaciones/AdminRevisionPublicacionesView.vue";

import AdminRevisionDetalleView from
  "../administracion/revision-publicaciones/AdminRevisionDetalleView.vue";

import AdminActualizacionesView from
  "../administracion/actualizaciones/AdminActualizacionesView.vue";

import AdminAuditoriaView from
  "../administracion/auditoria/AdminAuditoriaView.vue";

import InformacionPendienteView from
  "../actualizaciones/InformacionPendienteView.vue";

import ActualizacionPerfilView from
  "../actualizaciones/ActualizacionPerfilView.vue";

import ActualizacionPublicacionView from
  "../actualizaciones/ActualizacionPublicacionView.vue";

import ActualizacionProyectoView from
  "../actualizaciones/ActualizacionProyectoView.vue";

import SolicitudModificacionPublicacionView from
  "../publicaciones/solicitudes-modificacion/SolicitudModificacionPublicacionView.vue";

import AdminSolicitudesModificacionView from
  "../administracion/solicitudes-modificacion/AdminSolicitudesModificacionView.vue";

import AdminIntegridadDocumentalView from
  "../administracion/integridad-documental/AdminIntegridadDocumentalView.vue";

import AdminPreparacionProduccionView from
  "../administracion/preparacion-produccion/AdminPreparacionProduccionView.vue";


/* =========================================================
   CONFIGURACIÓN GENERAL
========================================================= */

const APP_TITLE =
  "SGPC ULEAM";


/* =========================================================
   FUNCIONES AUXILIARES
========================================================= */

function resolveDelegatedUserId(
  route
) {
  const paramId =
    route?.params?.usuarioId;

  const queryId =
    route?.query?.usuario_id ||
    route?.query?.usuarioId ||
    route?.query?.user_id;

  const raw =
    paramId ||
    queryId ||
    "";

  return String(
    raw
  ).trim();
}


function redirectToDelegatedAdminRoute(
  route,
  targetName
) {
  const usuarioId =
    resolveDelegatedUserId(
      route
    );

  if (usuarioId) {
    return {
      name:
        targetName,

      params: {
        usuarioId,
      },

      query:
        route.query,
    };
  }

  return {
    name:
      "AdminPublicaciones",
  };
}


const ACADEMIC_STRUCTURE_ROUTE_BY_TAB =
  Object.freeze({
    facultades:
      "AdminEstructuraFacultades",

    carreras:
      "AdminEstructuraCarreras",

    sedes:
      "AdminEstructuraSedes",

    "carreras-sedes":
      "AdminEstructuraCarrerasSedes",
  });


function resolveAcademicStructureTab(
  route,
  fallback = "facultades"
) {
  const rawTab =
    String(
      route?.query?.tab ||
      route?.meta?.structureTab ||
      fallback
    )
      .trim()
      .toLowerCase();

  return (
    Object.prototype.hasOwnProperty.call(
      ACADEMIC_STRUCTURE_ROUTE_BY_TAB,
      rawTab
    )
      ? rawTab
      : fallback
  );
}


/**
 * Convierte URLs históricas del catálogo académico
 * en las rutas canónicas.
 */
function redirectToAcademicStructureRoute(
  route,
  fallbackTab = "facultades"
) {
  const tab =
    resolveAcademicStructureTab(
      route,
      fallbackTab
    );

  const query = {
    ...route.query,
  };

  delete query.tab;

  return {
    name:
      ACADEMIC_STRUCTURE_ROUTE_BY_TAB[
        tab
      ],

    query,

    replace:
      true,
  };
}


/**
 * Determina si la ruta utiliza el diseño público.
 */
function isPublicRoute(
  route
) {
  return route.matched.some(
    (record) =>
      record.meta?.requiresAuth ===
        false ||
      record.meta?.publicLayout ===
        true
  );
}


/**
 * Evita que un fallo de renovación,
 * cookie vencida o problema de red
 * deje el RouterView vacío.
 */
async function bootstrapAuthSafely(
  userStore
) {
  try {
    await userStore.bootstrapAuth();

    return Boolean(
      userStore.isAuthenticated
    );
  } catch (error) {
    console.warn(
      "No fue posible restaurar la sesión guardada.",
      error
    );

    return false;
  }
}


/* =========================================================
   RUTAS
========================================================= */

const routes = [

  /* =======================================================
     RAÍZ
  ======================================================= */

  {
    path: "/",

    redirect:
      "/home",
  },


  /* =======================================================
     AUTENTICACIÓN
  ======================================================= */

  {
    path:
      "/login",

    name:
      "Login",

    component:
      LoginView,

    meta: {
      requiresAuth:
        false,

      publicLayout:
        true,

      title:
        "Iniciar sesión",
    },
  },


  {
    path:
      "/recuperar-contrasena",

    name:
      "RecuperarContrasena",

    component:
      RecuperarContrasenaView,

    meta: {
      requiresAuth:
        false,

      publicLayout:
        true,

      title:
        "Recuperar contraseña",
    },
  },


  {
    path:
      "/restablecer-contrasena",

    name:
      "ResetPassword",

    component:
      RestablecerContrasenaView,

    alias: [
      "/reset-password",
    ],

    meta: {
      requiresAuth:
        false,

      publicLayout:
        true,

      title:
        "Restablecer contraseña",
    },
  },


  /* =======================================================
     INICIO
  ======================================================= */

  {
    path:
      "/home",

    name:
      "Home",

    component:
      HomeWithAvisosView,

    alias: [
      "/inicio",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Inicio",
    },
  },


  /* =======================================================
     PERFIL DE USUARIO
  ======================================================= */

  {
    path:
      "/profile",

    name:
      "Profile",

    component:
      PerfilUsuarioView,

    alias: [
      "/perfil",
      "/mi-perfil",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Mi perfil",
    },
  },


  /* =======================================================
     PREFERENCIAS
  ======================================================= */

  {
    path:
      "/preferencias",

    name:
      "PreferenciasInterfaz",

    component:
      PreferenciasInterfazView,

    alias: [
      "/preferencias-interfaz",
      "/configuraciones",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Preferencias de interfaz",
    },
  },


  /* =======================================================
     NOTIFICACIONES
  ======================================================= */

  {
    path:
      "/notificaciones",

    name:
      "Notificaciones",

    component:
      NotificacionesView,

    alias: [
      "/notifications",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Notificaciones",
    },
  },


  /* =======================================================
     BÚSQUEDA Y PERFILES ACADÉMICOS
  ======================================================= */

  {
    path:
      "/busqueda",

    name:
      "Busqueda",

    component:
      BusquedaView,

    alias: [
      "/scholar",
      "/perfiles/google-scholar",
    ],

    meta: {
      requiresAuth:
        false,

      title:
        "Búsqueda",
    },
  },


  {
    path:
      "/perfiles",

    redirect:
      "/busqueda",

    meta: {
      requiresAuth:
        false,

      title:
        "Búsqueda",
    },
  },


  {
    path:
      "/perfil-academico/me",

    name:
      "PerfilAcademicoMe",

    component:
      PerfilAcademicoView,

    alias: [
      "/perfil/me",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Mi perfil académico",
    },

    props: (
      route
    ) => ({
      id:
        "me",

      q:
        route.query?.q ||
        "",
    }),
  },


  {
    path:
      "/perfil-academico/:id",

    name:
      "PerfilAcademico",

    component:
      PerfilAcademicoView,

    alias: [
      "/perfil/:id",
    ],

    meta: {
      requiresAuth:
        false,

      title:
        "Perfil académico",
    },

    props: (
      route
    ) => ({
      id:
        route.params.id,

      q:
        route.query?.q ||
        "",
    }),
  },


  /* =======================================================
     PUBLICACIONES
  ======================================================= */

  {
    path:
      "/tipos-publicacion",

    name:
      "TiposPublicacion",

    component:
      TiposPublicacionView,

    alias: [
      "/publicaciones/tipos",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Seleccionar tipo de publicación",
    },
  },


  {
    path:
      "/mis-publicaciones",

    name:
      "MisPublicaciones",

    component:
      MisPublicacionesView,

    alias: [
      "/publicaciones/mias",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Mis publicaciones",
    },
  },


  {
    path:
      "/mis-reportes",

    name:
      "MisReportes",

    component:
      MisReportesView,

    meta: {
      requiresAuth:
        true,

      title:
        "Mi producción científica",
    },
  },


  {
    path:
      "/publicaciones-listado",

    name:
      "PublicacionesListado",

    component:
      PublicacionesListadoView,

    alias: [
      "/publicaciones",
      "/publicaciones/listado",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Listado de publicaciones",
    },
  },


  /* =======================================================
     REGISTRO DE PUBLICACIONES
  ======================================================= */

  {
    path:
      "/publicaciones/registrar/articulo-alto-impacto",

    name:
      "RegistroArticuloAltoImpacto",

    component:
      ArticuloAltoImpactoForm,

    alias: [
      "/registro/aai",
      "/publicaciones/registrar/articulo_alto_impacto",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Registrar artículo de alto impacto",
    },
  },


  {
    path:
      "/publicaciones/registrar/articulo-regional",

    name:
      "RegistroArticuloRegional",

    component:
      ArticuloRegionalForm,

    alias: [
      "/registro/ar",
      "/publicaciones/registrar/articulo_regional",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Registrar artículo regional",
    },
  },


  {
    path:
      "/publicaciones/registrar/capitulo-libro",

    name:
      "RegistroCapituloLibro",

    component:
      CapituloLibroForm,

    alias: [
      "/registro/capitulo-libro",
      "/registro/capitulo_libro",
      "/publicaciones/registrar/capitulo_libro",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Registrar capítulo de libro",
    },
  },


  {
    path:
      "/publicaciones/registrar/libro",

    name:
      "RegistroLibro",

    component:
      LibroForm,

    alias: [
      "/registro/libro",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Registrar libro",
    },
  },


  {
    path:
      "/publicaciones/registrar/ponencia",

    name:
      "RegistroPonencia",

    component:
      PonenciaRegistro,

    alias: [
      "/registro/ponencia",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Registrar ponencia",
    },
  },


  /* =======================================================
     DETALLE Y EDICIÓN DE PUBLICACIONES
  ======================================================= */

  {
    path:
      "/publicacion/:id",

    name:
      "PublicacionDetalle",

    component:
      PublicacionDetalleView,

    alias: [
      "/publicaciones/:id",
    ],

    meta: {
      requiresAuth:
        false,

      title:
        "Detalle de publicación",
    },

    props:
      true,
  },


  {
    path:
      "/publicacion/:id/editar",

    name:
      "EditarPublicacion",

    component:
      PublicacionDetalleView,

    alias: [
      "/publicaciones/:id/editar",
    ],

    meta: {
      requiresAuth:
        true,

      publicationEdit:
        true,

      title:
        "Editar publicación",
    },

    props:
      true,
  },


  /* =======================================================
     PROYECTOS
  ======================================================= */

  {
    path:
      "/proyectos",

    name:
      "ProyectosListado",

    component:
      ProyectosListadoView,

    alias: [
      "/proyectos-listado",
    ],

    meta: {
      requiresAuth:
        true,

      title:
        "Proyectos institucionales",
    },
  },


  {
    path:
      "/proyectos/nuevo",

    name:
      "ProyectoNuevo",

    component:
      ProyectoFormularioView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      title:
        "Nuevo proyecto",
    },
  },


  {
    path:
      "/proyectos/:id/editar",

    name:
      "ProyectoEditar",

    component:
      ProyectoFormularioView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      title:
        "Editar proyecto",
    },

    props:
      true,
  },


  /* =======================================================
     ADMINISTRACIÓN
  ======================================================= */

  {
    path:
      "/admin",

    redirect: {
      name:
        "AdminPanel",
    },

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "resumen",

      title:
        "Administración",
    },
  },


  /* =====================================================
     1. RESUMEN ADMINISTRATIVO
  ===================================================== */

  {
    path:
      "/admin/panel",

    name:
      "AdminPanel",

    component:
      PanelAdministracionView,

    alias: [
      "/admin-panel",
    ],

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "resumen",

      title:
        "Administración",
    },
  },


  /* =====================================================
     2. REVISIÓN CIENTÍFICA
  ===================================================== */

  {
    path:
      "/admin/revision",

    name:
      "AdminRevisionPublicaciones",

    component:
      AdminRevisionPublicacionesView,

    alias: [
      "/admin/revision-publicaciones",
      "/admin/cola-revision",
    ],

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "revision",

      title:
        "Revisión científica",
    },
  },


  {
    path:
      "/admin/revision/:id",

    name:
      "AdminRevisionDetalle",

    component:
      AdminRevisionDetalleView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "revision",

      title:
        "Revisión de publicación",
    },

    props:
      true,
  },


  /* =====================================================
     3. USUARIOS
  ===================================================== */

  {
    path:
      "/admin/usuarios",

    name:
      "AdminUsuarios",

    component:
      AdminUsuariosView,

    alias: [
      "/admin-usuarios",
      "/admin-panel-usuarios",
    ],

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "usuarios",

      title:
        "Usuarios",
    },
  },


  {
    path:
      "/admin/usuarios/:id/editar",

    name:
      "AdminUsuarioEditar",

    component:
      AdminUsuarioEditarView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "usuarios",

      title:
        "Editar usuario",
    },

    props:
      true,
  },


  {
    path:
      "/admin/usuarios/:id",

    name:
      "AdminUsuarioDetalle",

    component:
      AdminUsuarioDetalleView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "usuarios",

      title:
        "Detalle de usuario",
    },

    props:
      true,
  },


  {
    path:
      "/admin/autores-externos",

    redirect: {
      name:
        "AdminUsuarios",
    },

    alias: [
      "/admin-autores-externos",
    ],

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "usuarios",

      title:
        "Autores externos",
    },
  },


  /* =====================================================
     4. PUBLICACIONES ADMINISTRATIVAS
  ===================================================== */

  {
    path:
      "/admin/publicaciones",

    name:
      "AdminPublicaciones",

    component:
      AdminPublicacionesView,

    alias: [
      "/admin-publicaciones",
      "/admin-panel-publicaciones",
      "/admin/gestion-publicaciones",
    ],

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "publicaciones",

      title:
        "Registrar publicación",
    },
  },


  {
    path:
      "/admin/publicaciones/registrar",

    name:
      "AdminRegistroDelegado",

    redirect: {
      name:
        "AdminPublicaciones",
    },

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "publicaciones",

      title:
        "Registrar para un usuario",
    },
  },


  {
    path:
      "/admin/publicaciones/usuario/:usuarioId",

    name:
      "AdminPublicacionesUsuario",

    component:
      AdminPublicacionesUsuarioView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      delegatedPublication:
        true,

      adminSection:
        "publicaciones",

      title:
        "Publicaciones del usuario",
    },

    props: (
      route
    ) => ({
      usuarioId:
        Number(
          route.params.usuarioId
        ),
    }),
  },


  /* =====================================================
     4.1 REGISTRO PARA USUARIO
  ===================================================== */

  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/articulo-alto-impacto",

    name:
      "AdminRegistroArticuloAltoImpactoUsuario",

    component:
      ArticuloAltoImpactoForm,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      delegatedPublication:
        true,

      adminSection:
        "publicaciones",

      title:
        "Registrar artículo de alto impacto",
    },

    props:
      true,
  },


  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/articulo-regional",

    name:
      "AdminRegistroArticuloRegionalUsuario",

    component:
      ArticuloRegionalForm,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      delegatedPublication:
        true,

      adminSection:
        "publicaciones",

      title:
        "Registrar artículo regional",
    },

    props:
      true,
  },


  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/ponencia",

    name:
      "AdminRegistroPonenciaUsuario",

    component:
      PonenciaRegistro,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      delegatedPublication:
        true,

      adminSection:
        "publicaciones",

      title:
        "Registrar ponencia",
    },

    props:
      true,
  },


  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/libro",

    name:
      "AdminRegistroLibroUsuario",

    component:
      LibroForm,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      delegatedPublication:
        true,

      adminSection:
        "publicaciones",

      title:
        "Registrar libro",
    },

    props:
      true,
  },


  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/capitulo-libro",

    name:
      "AdminRegistroCapituloLibroUsuario",

    component:
      CapituloLibroForm,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      delegatedPublication:
        true,

      adminSection:
        "publicaciones",

      title:
        "Registrar capítulo de libro",
    },

    props:
      true,
  },


  /* =====================================================
     4.2 COMPATIBILIDAD CON URLS ANTERIORES
  ===================================================== */

  {
    path:
      "/admin/publicaciones/registrar/articulo-alto-impacto",

    redirect: (
      to
    ) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroArticuloAltoImpactoUsuario"
      ),
  },


  {
    path:
      "/admin/publicaciones/registrar/articulo-regional",

    redirect: (
      to
    ) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroArticuloRegionalUsuario"
      ),
  },


  {
    path:
      "/admin/publicaciones/registrar/ponencia",

    redirect: (
      to
    ) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroPonenciaUsuario"
      ),
  },


  {
    path:
      "/admin/publicaciones/registrar/libro",

    redirect: (
      to
    ) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroLibroUsuario"
      ),
  },


  {
    path:
      "/admin/publicaciones/registrar/capitulo-libro",

    redirect: (
      to
    ) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroCapituloLibroUsuario"
      ),
  },


  /* =====================================================
     4.3 DETALLE Y EDICIÓN ADMINISTRATIVA
  ===================================================== */

  {
    path:
      "/admin/publicaciones/:id",

    name:
      "AdminPublicacionDetalle",

    component:
      PublicacionDetalleView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "publicaciones",

      title:
        "Detalle de publicación",
    },

    props:
      true,
  },


  {
    path:
      "/admin/publicaciones/:id/editar",

    name:
      "AdminEditarPublicacion",

    component:
      PublicacionDetalleView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      publicationEdit:
        true,

      adminSection:
        "publicaciones",

      title:
        "Editar publicación",
    },

    props:
      true,
  },


  /* =====================================================
     5. ESTRUCTURA ACADÉMICA
  ===================================================== */

  {
    path:
      "/admin/estructura",

    name:
      "AdminEstructura",

    redirect: {
      name:
        "AdminEstructuraFacultades",
    },

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "estructura",

      title:
        "Estructura académica",
    },
  },


  {
    path:
      "/admin/estructura/facultades",

    name:
      "AdminEstructuraFacultades",

    component:
      GestionFacultadesCarrerasView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "estructura",

      structureTab:
        "facultades",

      title:
        "Facultades",
    },
  },


  {
    path:
      "/admin/estructura/carreras",

    name:
      "AdminEstructuraCarreras",

    component:
      GestionFacultadesCarrerasView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "estructura",

      structureTab:
        "carreras",

      title:
        "Carreras",
    },
  },


  {
    path:
      "/admin/estructura/sedes",

    name:
      "AdminEstructuraSedes",

    component:
      GestionFacultadesCarrerasView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "estructura",

      structureTab:
        "sedes",

      title:
        "Sedes",
    },
  },


  {
    path:
      "/admin/estructura/carreras-sedes",

    name:
      "AdminEstructuraCarrerasSedes",

    component:
      GestionFacultadesCarrerasView,

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "estructura",

      structureTab:
        "carreras-sedes",

      title:
        "Carreras por sede",
    },
  },


  /* =====================================================
     5.1 COMPATIBILIDAD CON URLS HISTÓRICAS
  ===================================================== */

  {
    path:
      "/admin/facultades-carreras",

    name:
      "GestionFacultadesCarreras",

    redirect: (
      to
    ) =>
      redirectToAcademicStructureRoute(
        to,
        "facultades"
      ),

    alias: [
      "/admin/catalogos",
      "/admin-catalogos",
      "/admin-panel-catalogos",
    ],

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "estructura",

      title:
        "Estructura académica y sedes",
    },
  },


  {
    path:
      "/admin/facultades",

    redirect: (
      to
    ) =>
      redirectToAcademicStructureRoute(
        to,
        "facultades"
      ),

    alias: [
      "/admin-facultades",
    ],

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "estructura",

      title:
        "Facultades",
    },
  },


  {
    path:
      "/admin/carreras",

    redirect: (
      to
    ) =>
      redirectToAcademicStructureRoute(
        to,
        "carreras"
      ),

    alias: [
      "/admin-carreras",
    ],

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "estructura",

      title:
        "Carreras",
    },
  },


  /* =======================================================
     COMPATIBILIDAD — ANTIGUO ADMIN REPORTES
  ======================================================= */

  {
    path:
      "/admin/reportes",

    redirect: {
      name:
        "AdminPanel",
    },

    meta: {
      requiresAuth:
        true,

      requiresAdmin:
        true,

      adminSection:
        "resumen",

      title:
        "Administración",
    },
  },


  /* =======================================================
     RUTA NO ENCONTRADA
  ======================================================= */

  /* =======================================================
     ACTUALIZACIÓN DE INFORMACIÓN
  ======================================================= */

  {
    path: "/informacion-pendiente",
    name: "InformacionPendiente",
    component: InformacionPendienteView,
    meta: { requiresAuth: true, title: "Información pendiente" },
  },
  {
    path: "/informacion-pendiente/perfil",
    name: "ActualizacionPerfil",
    component: ActualizacionPerfilView,
    meta: { requiresAuth: true, title: "Actualizar perfil" },
  },
  {
    path: "/informacion-pendiente/publicacion/:id",
    name: "ActualizacionPublicacion",
    component: ActualizacionPublicacionView,
    meta: { requiresAuth: true, title: "Actualizar publicación" },
    props: true,
  },
  {
    path: "/informacion-pendiente/proyecto/:id",
    name: "ActualizacionProyecto",
    component: ActualizacionProyectoView,
    meta: { requiresAuth: true, title: "Actualizar proyecto" },
    props: true,
  },

  {
    path: "/admin/actualizaciones",
    name: "AdminActualizaciones",
    component: AdminActualizacionesView,
    meta: { requiresAuth: true, requiresAdmin: true, adminSection: "actualizaciones", title: "Actualización de datos" },
  },
  {
    path: "/admin/auditoria",
    name: "AdminAuditoria",
    component: AdminAuditoriaView,
    meta: { requiresAuth: true, requiresAdmin: true, adminSection: "auditoria", title: "Auditoría" },
  },

  {
    path: "/publicaciones/:id/solicitar-modificacion",
    name: "SolicitudModificacionPublicacion",
    component: SolicitudModificacionPublicacionView,
    meta: { requiresAuth: true, title: "Solicitar modificación" },
    props: true,
  },

  {
    path: "/admin/solicitudes-modificacion-publicaciones",
    name: "AdminSolicitudesModificacion",
    component: AdminSolicitudesModificacionView,
    meta: { requiresAuth: true, requiresAdmin: true, adminSection: "solicitudes-modificacion", title: "Solicitudes de modificación" },
  },
  {
    path: "/admin/integridad-documental",
    name: "AdminIntegridadDocumental",
    component: AdminIntegridadDocumentalView,
    meta: { requiresAuth: true, requiresAdmin: true, adminSection: "integridad-documental", title: "Integridad documental" },
  },
  {
    path: "/admin/preparacion-produccion",
    name: "AdminPreparacionProduccion",
    component: AdminPreparacionProduccionView,
    meta: { requiresAuth: true, requiresAdmin: true, adminSection: "preparacion-produccion", title: "Preparación de actualización" },
  },

  {
    path:
      "/:pathMatch(.*)*",

    redirect:
      "/home",
  },
];


/* =========================================================
   INSTANCIA DEL ROUTER
========================================================= */

const router =
  createRouter({
    history:
      createWebHistory(
        import.meta.env.BASE_URL
      ),

    routes,

    scrollBehavior(
      to,
      _from,
      savedPosition
    ) {
      if (
        savedPosition
      ) {
        return savedPosition;
      }

      if (
        to.hash
      ) {
        return {
          el:
            to.hash,

          top:
            88,

          behavior:
            "auto",
        };
      }

      return {
        top:
          0,

        left:
          0,

        behavior:
          "auto",
      };
    },
  });


/* =========================================================
   GUARD GLOBAL
========================================================= */

router.beforeEach(
  async (
    to
  ) => {
    const userStore =
      useUserStore();

    const comingFromMicrosoftOnLogin =
      (
        to.path ===
        "/login"
      ) &&
      Boolean(
        to.query.code ||
        to.query.ms_code ||
        to.query.ms_error
      );

    /*
     * El retorno de Microsoft debe procesarse
     * directamente dentro del LoginView.
     */
    if (
      comingFromMicrosoftOnLogin
    ) {
      return true;
    }

    const publicRoute =
      isPublicRoute(
        to
      );

    const authenticated =
      await bootstrapAuthSafely(
        userStore
      );

    /*
     * Las rutas públicas permanecen accesibles.
     */
    if (
      publicRoute
    ) {
      if (
        authenticated &&
        to.path ===
          "/login"
      ) {
        return {
          path:
            "/home",

          replace:
            true,
        };
      }

      return true;
    }

    /*
     * Rutas que requieren autenticación.
     */
    if (
      to.meta.requiresAuth &&
      !authenticated
    ) {
      return {
        path:
          "/login",

        query: {
          redirect:
            to.fullPath !==
              "/"
              ? to.fullPath
              : "/home",
        },

        replace:
          true,
      };
    }

    /*
     * Rutas exclusivamente administrativas.
     */
    if (
      to.meta.requiresAdmin &&
      !userStore.isAdmin
    ) {
      return {
        path:
          "/home",

        replace:
          true,
      };
    }

    /*
     * Registro delegado de publicaciones.
     */
    if (
      to.meta.delegatedPublication
    ) {
      const usuarioId =
        resolveDelegatedUserId(
          to
        );

      if (
        !usuarioId
      ) {
        return {
          name:
            "AdminPublicaciones",

          replace:
            true,
        };
      }
    }

    return true;
  }
);


/* =========================================================
   TÍTULO DEL DOCUMENTO
========================================================= */

router.afterEach(
  (
    to
  ) => {
    const nearestWithTitle =
      [
        ...to.matched,
      ]
        .reverse()
        .find(
          (
            record
          ) =>
            record.meta?.title
        );

    const pageTitle =
      nearestWithTitle
        ?.meta
        ?.title;

    document.title =
      pageTitle
        ? `${pageTitle} | ${APP_TITLE}`
        : APP_TITLE;
  }
);


export default router;