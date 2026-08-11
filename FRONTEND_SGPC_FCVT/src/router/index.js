import {
  createRouter,
  createWebHistory,
} from "vue-router";

import { useUserStore } from "../scripts/stores/userStore";

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
   PUBLICACIONES
========================================================= */

import TiposPublicacionView from
  "../publicaciones/tipos-publicacion/TiposPublicacionView.vue";

import MisPublicacionesView from
  "../publicaciones/mis-publicaciones/MisPublicacionesView.vue";

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

import GestionFacultadesCarrerasView from
  "../administracion/gestion-facultades-carreras/GestionFacultadesCarrerasView.vue";

import AdminPublicacionesView from
  "../administracion/gestion-publicaciones/AdminPublicacionesDelegadasView.vue";

/* =========================================================
   CONFIGURACIÓN GENERAL
========================================================= */

const APP_TITLE = "SGPC ULEAM";

/* =========================================================
   FUNCIONES AUXILIARES
========================================================= */

function resolveDelegatedUserId(route) {
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

  return String(raw).trim();
}

function redirectToDelegatedAdminRoute(
  route,
  targetName
) {
  const usuarioId =
    resolveDelegatedUserId(route);

  if (usuarioId) {
    return {
      name: targetName,

      params: {
        usuarioId,
      },

      query: route.query,
    };
  }

  return {
    name: "AdminPublicaciones",
  };
}

/**
 * Determina si la ruta utiliza el diseño público.
 *
 * Se revisan todos los registros coincidentes para admitir
 * correctamente rutas con alias como /reset-password.
 */
function isPublicRoute(route) {
  return route.matched.some(
    (record) =>
      record.meta?.requiresAuth === false ||
      record.meta?.publicLayout === true
  );
}

/**
 * Evita que un fallo de renovación, una cookie vencida o un
 * error de red interrumpan la navegación y dejen vacío el
 * RouterView.
 */
async function bootstrapAuthSafely(userStore) {
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
  {
    path: "/",
    redirect: "/home",
  },

  /* =======================================================
     AUTENTICACIÓN
  ======================================================= */

  {
    path: "/login",
    name: "Login",
    component: LoginView,

    meta: {
      requiresAuth: false,
      publicLayout: true,
      title: "Iniciar sesión",
    },
  },

  {
    path: "/recuperar-contrasena",
    name: "RecuperarContrasena",
    component: RecuperarContrasenaView,

    meta: {
      requiresAuth: false,
      publicLayout: true,
      title: "Recuperar contraseña",
    },
  },

  {
    path: "/restablecer-contrasena",
    name: "ResetPassword",
    component: RestablecerContrasenaView,

    alias: [
      "/reset-password",
    ],

    meta: {
      requiresAuth: false,
      publicLayout: true,
      title: "Restablecer contraseña",
    },
  },

  /* =======================================================
     INICIO
  ======================================================= */

  {
    path: "/home",
    name: "Home",
    component: HomeWithAvisosView,

    alias: [
      "/inicio",
    ],

    meta: {
      requiresAuth: true,
      title: "Inicio",
    },
  },

  /* =======================================================
     PERFIL DE USUARIO
  ======================================================= */

  {
    path: "/profile",
    name: "Profile",
    component: PerfilUsuarioView,

    alias: [
      "/perfil",
      "/mi-perfil",
    ],

    meta: {
      requiresAuth: true,
      title: "Mi perfil",
    },
  },

  /* =======================================================
     PREFERENCIAS
  ======================================================= */

  {
    path: "/preferencias",
    name: "PreferenciasInterfaz",
    component: PreferenciasInterfazView,

    alias: [
      "/preferencias-interfaz",
      "/configuraciones",
    ],

    meta: {
      requiresAuth: true,
      title: "Preferencias de interfaz",
    },
  },

  /* =======================================================
     BÚSQUEDA Y PERFILES ACADÉMICOS
  ======================================================= */

  {
    path: "/busqueda",
    name: "Busqueda",
    component: BusquedaView,

    alias: [
      "/scholar",
      "/perfiles/google-scholar",
    ],

    meta: {
      requiresAuth: true,
      title: "Búsqueda",
    },
  },

  {
    path: "/perfiles",
    redirect: "/busqueda",

    meta: {
      requiresAuth: true,
      title: "Búsqueda",
    },
  },

  {
    path: "/perfil-academico/me",
    name: "PerfilAcademicoMe",
    component: PerfilAcademicoView,

    alias: [
      "/perfil/me",
    ],

    meta: {
      requiresAuth: true,
      title: "Mi perfil académico",
    },

    props: (route) => ({
      id: "me",
      q: route.query?.q || "",
    }),
  },

  {
    path: "/perfil-academico/:id",
    name: "PerfilAcademico",
    component: PerfilAcademicoView,

    alias: [
      "/perfil/:id",
    ],

    meta: {
      requiresAuth: true,
      title: "Perfil académico",
    },

    props: (route) => ({
      id: route.params.id,
      q: route.query?.q || "",
    }),
  },

  /* =======================================================
     PUBLICACIONES
  ======================================================= */

  {
    path: "/tipos-publicacion",
    name: "TiposPublicacion",
    component: TiposPublicacionView,

    alias: [
      "/publicaciones/tipos",
    ],

    meta: {
      requiresAuth: true,
      title: "Seleccionar tipo de publicación",
    },
  },

  {
    path: "/mis-publicaciones",
    name: "MisPublicaciones",
    component: MisPublicacionesView,

    alias: [
      "/publicaciones/mias",
    ],

    meta: {
      requiresAuth: true,
      title: "Mis publicaciones",
    },
  },

  {
    path: "/publicaciones-listado",
    name: "PublicacionesListado",
    component: PublicacionesListadoView,

    alias: [
      "/publicaciones",
      "/publicaciones/listado",
    ],

    meta: {
      requiresAuth: true,
      title: "Listado de publicaciones",
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
      requiresAuth: true,
      title: "Registrar artículo de alto impacto",
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
      requiresAuth: true,
      title: "Registrar artículo regional",
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
      requiresAuth: true,
      title: "Registrar capítulo de libro",
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
      requiresAuth: true,
      title: "Registrar libro",
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
      requiresAuth: true,
      title: "Registrar ponencia",
    },
  },

  /* =======================================================
     DETALLE Y EDICIÓN DE PUBLICACIONES
  ======================================================= */

  {
    path: "/publicacion/:id",
    name: "PublicacionDetalle",
    component: PublicacionDetalleView,

    alias: [
      "/publicaciones/:id",
    ],

    meta: {
      requiresAuth: true,
      title: "Detalle de publicación",
    },

    props: true,
  },

  {
    path: "/publicacion/:id/editar",
    name: "EditarPublicacion",
    component: PublicacionDetalleView,

    alias: [
      "/publicaciones/:id/editar",
    ],

    meta: {
      requiresAuth: true,
      publicationEdit: true,
      title: "Editar publicación",
    },

    props: true,
  },

  /* =======================================================
     PROYECTOS
  ======================================================= */

  {
    path: "/proyectos",
    name: "ProyectosListado",
    component: ProyectosListadoView,

    alias: [
      "/proyectos-listado",
    ],

    meta: {
      requiresAuth: true,
      title: "Proyectos institucionales",
    },
  },

  {
    path: "/proyectos/nuevo",
    name: "ProyectoNuevo",
    component: ProyectoFormularioView,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Nuevo proyecto",
    },
  },

  {
    path: "/proyectos/:id/editar",
    name: "ProyectoEditar",
    component: ProyectoFormularioView,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Editar proyecto",
    },

    props: true,
  },

  /* =======================================================
     ADMINISTRACIÓN
  ======================================================= */

  {
    path: "/admin",
    redirect: "/admin/panel",

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Administración",
    },
  },

  {
    path: "/admin/panel",
    name: "AdminPanel",
    component: PanelAdministracionView,

    alias: [
      "/admin-panel",
    ],

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Panel de administración",
    },
  },

  {
    path: "/admin/usuarios",
    name: "AdminUsuarios",
    component: AdminUsuariosView,

    alias: [
      "/admin-usuarios",
      "/admin-panel-usuarios",
    ],

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Gestión de usuarios",
    },
  },

  {
    path: "/admin/publicaciones",
    name: "AdminPublicaciones",
    component: AdminPublicacionesView,

    alias: [
      "/admin-publicaciones",
      "/admin-panel-publicaciones",
      "/admin/gestion-publicaciones",
    ],

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Gestión de publicaciones",
    },
  },

  {
    path:
      "/admin/publicaciones/usuario/:usuarioId",

    name:
      "AdminPublicacionesUsuario",

    component:
      AdminPublicacionesView,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Publicaciones del usuario",
    },

    props: (route) => ({
      usuarioId: Number(
        route.params.usuarioId
      ),
    }),
  },

  /* =======================================================
     REGISTRO ADMINISTRATIVO
  ======================================================= */

  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/articulo-alto-impacto",

    name:
      "AdminRegistroArticuloAltoImpactoUsuario",

    component:
      ArticuloAltoImpactoForm,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar artículo de alto impacto",
    },

    props: true,
  },

  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/articulo-regional",

    name:
      "AdminRegistroArticuloRegionalUsuario",

    component:
      ArticuloRegionalForm,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar artículo regional",
    },

    props: true,
  },

  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/ponencia",

    name:
      "AdminRegistroPonenciaUsuario",

    component:
      PonenciaRegistro,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar ponencia",
    },

    props: true,
  },

  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/libro",

    name:
      "AdminRegistroLibroUsuario",

    component:
      LibroForm,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar libro",
    },

    props: true,
  },

  {
    path:
      "/admin/publicaciones/usuario/:usuarioId/registrar/capitulo-libro",

    name:
      "AdminRegistroCapituloLibroUsuario",

    component:
      CapituloLibroForm,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar capítulo de libro",
    },

    props: true,
  },

  /* =======================================================
     REDIRECCIONES ADMINISTRATIVAS
  ======================================================= */

  {
    path:
      "/admin/publicaciones/registrar/articulo-alto-impacto",

    redirect: (to) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroArticuloAltoImpactoUsuario"
      ),
  },

  {
    path:
      "/admin/publicaciones/registrar/articulo-regional",

    redirect: (to) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroArticuloRegionalUsuario"
      ),
  },

  {
    path:
      "/admin/publicaciones/registrar/ponencia",

    redirect: (to) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroPonenciaUsuario"
      ),
  },

  {
    path:
      "/admin/publicaciones/registrar/libro",

    redirect: (to) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroLibroUsuario"
      ),
  },

  {
    path:
      "/admin/publicaciones/registrar/capitulo-libro",

    redirect: (to) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroCapituloLibroUsuario"
      ),
  },

  /* =======================================================
     DETALLE Y EDICIÓN ADMINISTRATIVA
  ======================================================= */

  {
    path: "/admin/publicaciones/:id",
    name: "AdminPublicacionDetalle",
    component: PublicacionDetalleView,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Detalle administrativo de publicación",
    },

    props: true,
  },

  {
    path: "/admin/publicaciones/:id/editar",
    name: "AdminEditarPublicacion",
    component: PublicacionDetalleView,

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      publicationEdit: true,
      title: "Editar publicación",
    },

    props: true,
  },

  /* =======================================================
     FACULTADES Y CARRERAS
  ======================================================= */

  {
    path: "/admin/facultades-carreras",
    name: "GestionFacultadesCarreras",
    component: GestionFacultadesCarrerasView,

    alias: [
      "/admin/catalogos",
      "/admin-catalogos",
      "/admin-panel-catalogos",
    ],

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Administrar facultades y carreras",
    },
  },

  {
    path: "/admin/autores-externos",

    redirect: {
      name: "AdminUsuarios",
    },

    alias: [
      "/admin-autores-externos",
    ],

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Autores externos",
    },
  },

  {
    path: "/admin/facultades",

    redirect: {
      name: "GestionFacultadesCarreras",

      query: {
        tab: "facultades",
      },
    },

    alias: [
      "/admin-facultades",
    ],

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Facultades",
    },
  },

  {
    path: "/admin/carreras",

    redirect: {
      name: "GestionFacultadesCarreras",

      query: {
        tab: "carreras",
      },
    },

    alias: [
      "/admin-carreras",
    ],

    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Carreras",
    },
  },

  /* =======================================================
     RUTA NO ENCONTRADA
  ======================================================= */

  {
    path: "/:pathMatch(.*)*",
    redirect: "/home",
  },
];

/* =========================================================
   INSTANCIA DEL ROUTER
========================================================= */

const router = createRouter({
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
    if (savedPosition) {
      return savedPosition;
    }

    if (to.hash) {
      return {
        el: to.hash,
        top: 88,
        behavior: "auto",
      };
    }

    return {
      top: 0,
      left: 0,
      behavior: "auto",
    };
  },
});

/* =========================================================
   GUARD GLOBAL
========================================================= */

router.beforeEach(async (to) => {
  const userStore =
    useUserStore();

  const comingFromMicrosoftOnLogin =
    to.path === "/login" &&
    Boolean(
      to.query.code ||
      to.query.ms_code ||
      to.query.ms_error
    );

  /*
   * LoginView debe procesar directamente el retorno de
   * Microsoft sin intentar restaurar una sesión anterior.
   */
  if (comingFromMicrosoftOnLogin) {
    return true;
  }

  const publicRoute =
    isPublicRoute(to);

  /*
   * Cualquier error de bootstrap queda controlado. De esta
   * forma el guard siempre devuelve una resolución y el
   * RouterView no se queda vacío.
   */
  const authenticated =
    await bootstrapAuthSafely(
      userStore
    );

  /*
   * Solo el login redirige al inicio cuando la sesión ya es
   * válida. Las pantallas de recuperación continúan accesibles.
   */
  if (publicRoute) {
    if (
      authenticated &&
      to.path === "/login"
    ) {
      return {
        path: "/home",
        replace: true,
      };
    }

    return true;
  }

  if (
    to.meta.requiresAuth &&
    !authenticated
  ) {
    return {
      path: "/login",

      query: {
        redirect:
          to.fullPath !== "/"
            ? to.fullPath
            : "/home",
      },

      replace: true,
    };
  }

  if (
    to.meta.requiresAdmin &&
    !userStore.isAdmin
  ) {
    return {
      path: "/home",
      replace: true,
    };
  }

  if (
    to.meta.delegatedPublication
  ) {
    const usuarioId =
      resolveDelegatedUserId(to);

    if (!usuarioId) {
      return {
        name: "AdminPublicaciones",
        replace: true,
      };
    }
  }

  return true;
});

/* =========================================================
   TÍTULO DEL DOCUMENTO
========================================================= */

router.afterEach((to) => {
  const nearestWithTitle =
    [...to.matched]
      .reverse()
      .find(
        (record) =>
          record.meta?.title
      );

  const pageTitle =
    nearestWithTitle?.meta?.title;

  document.title =
    pageTitle
      ? `${pageTitle} | ${APP_TITLE}`
      : APP_TITLE;
});

export default router;