import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "../scripts/stores/userStore";

// =========================
// Autenticación
// =========================
import LoginView from "../autenticacion/login/LoginView.vue";
import RestablecerContrasenaView from "../autenticacion/recuperar-contrasena/RestablecerContrasenaView.vue";

// =========================
// Inicio
// =========================
import HomeWithAvisosView from "../inicio/home-with-avisos/HomeWithAvisosView.vue";

// =========================
// Perfiles / Búsqueda académica
// =========================
import PerfilUsuarioView from "../perfiles/perfil-usuario/PerfilUsuarioView.vue";
import BusquedaView from "../perfiles/busqueda/BusquedaView.vue";
import PerfilAcademicoView from "../perfiles/perfil-academico/PerfilAcademicoView.vue";

// =========================
// Preferencias
// =========================
import PreferenciasInterfazView from "../preferencias/preferencias-interfaz/PreferenciasInterfazView.vue";

// =========================
// Publicaciones
// =========================
import TiposPublicacionView from "../publicaciones/tipos-publicacion/TiposPublicacionView.vue";
import MisPublicacionesView from "../publicaciones/mis-publicaciones/MisPublicacionesView.vue";
import PublicacionesListadoView from "../publicaciones/listado-publicaciones/PublicacionesListadoView.vue";
import PublicacionDetalleView from "../publicaciones/detalle-publicacion/PublicacionDetalleView.vue";

import ArticuloAltoImpactoForm from "../publicaciones/articulo-alto-impacto/ArticuloAltoImpactoForm.vue";
import ArticuloRegionalForm from "../publicaciones/articulo-regional/ArticuloRegionalForm.vue";
import CapituloLibroForm from "../publicaciones/capitulo-libro/CapituloLibroForm.vue";
import LibroForm from "../publicaciones/libro/LibroForm.vue";
import PonenciaRegistro from "../publicaciones/ponencia/PonenciaRegistro.vue";

// =========================
// Proyectos
// =========================
import ProyectosListadoView from "../proyectos/listado/ProyectosListadoView.vue";
import ProyectoFormularioView from "../proyectos/formulario/ProyectoFormularioView.vue";

// =========================
// Administración
// =========================
import PanelAdministracionView from "../administracion/panel-administracion/PanelAdministracionView.vue";
import AdminUsuariosView from "../administracion/gestion-usuarios/AdminUsuariosView.vue";
import GestionFacultadesCarrerasView from "../administracion/gestion-facultades-carreras/GestionFacultadesCarrerasView.vue";
import AdminPublicacionesView from "../administracion/gestion-publicaciones/AdminPublicacionesDelegadasView.vue";

const APP_TITLE = "SGPC ULEAM";

function resolveDelegatedUserId(route) {
  const paramId = route?.params?.usuarioId;
  const queryId =
    route?.query?.usuario_id ||
    route?.query?.usuarioId ||
    route?.query?.user_id;

  const raw = paramId || queryId || "";
  return String(raw).trim();
}

function redirectToDelegatedAdminRoute(route, targetName) {
  const usuarioId = resolveDelegatedUserId(route);

  if (usuarioId) {
    return {
      name: targetName,
      params: { usuarioId },
      query: route.query,
    };
  }

  return {
    name: "AdminPublicaciones",
  };
}

const routes = [
  {
    path: "/",
    redirect: "/home",
  },

  // =========================
  // Autenticación
  // =========================
  {
    path: "/login",
    name: "Login",
    component: LoginView,
    meta: {
      requiresAuth: false,
      title: "Iniciar sesión",
    },
  },
  {
    path: "/reset-password",
    name: "ResetPassword",
    component: RestablecerContrasenaView,
    meta: {
      requiresAuth: false,
      title: "Restablecer contraseña",
    },
    alias: ["/restablecer-contrasena"],
  },

  // =========================
  // Inicio
  // =========================
  {
    path: "/home",
    name: "Home",
    component: HomeWithAvisosView,
    meta: {
      requiresAuth: true,
      title: "Inicio",
    },
    alias: ["/inicio"],
  },

  // =========================
  // Perfil de usuario
  // =========================
  {
    path: "/profile",
    name: "Profile",
    component: PerfilUsuarioView,
    meta: {
      requiresAuth: true,
      title: "Mi perfil",
    },
    alias: ["/perfil", "/mi-perfil"],
  },

  // =========================
  // Preferencias
  // =========================
  {
    path: "/preferencias",
    name: "PreferenciasInterfaz",
    component: PreferenciasInterfazView,
    meta: {
      requiresAuth: true,
      title: "Preferencias de interfaz",
    },
    alias: ["/preferencias-interfaz", "/configuraciones"],
  },

  // =========================
  // Búsqueda / Perfiles académicos
  // =========================
  {
    path: "/busqueda",
    name: "Busqueda",
    component: BusquedaView,
    meta: {
      requiresAuth: true,
      title: "Búsqueda",
    },
    alias: ["/scholar", "/perfiles/google-scholar"],
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
    meta: {
      requiresAuth: true,
      title: "Mi perfil académico",
    },
    props: (route) => ({
      id: "me",
      q: route.query?.q || "",
    }),
    alias: ["/perfil/me"],
  },
  {
    path: "/perfil-academico/:id",
    name: "PerfilAcademico",
    component: PerfilAcademicoView,
    meta: {
      requiresAuth: true,
      title: "Perfil académico",
    },
    props: (route) => ({
      id: route.params.id,
      q: route.query?.q || "",
    }),
    alias: ["/perfil/:id"],
  },

  // =========================
  // Publicaciones
  // =========================
  {
    path: "/tipos-publicacion",
    name: "TiposPublicacion",
    component: TiposPublicacionView,
    meta: {
      requiresAuth: true,
      title: "Seleccionar tipo de publicación",
    },
    alias: ["/publicaciones/tipos"],
  },
  {
    path: "/mis-publicaciones",
    name: "MisPublicaciones",
    component: MisPublicacionesView,
    meta: {
      requiresAuth: true,
      title: "Mis publicaciones",
    },
    alias: ["/publicaciones/mias"],
  },
  {
    path: "/publicaciones-listado",
    name: "PublicacionesListado",
    component: PublicacionesListadoView,
    meta: {
      requiresAuth: true,
      title: "Listado de publicaciones",
    },
    alias: ["/publicaciones", "/publicaciones/listado"],
  },

  {
    path: "/publicaciones/registrar/articulo-alto-impacto",
    name: "RegistroArticuloAltoImpacto",
    component: ArticuloAltoImpactoForm,
    meta: {
      requiresAuth: true,
      title: "Registrar artículo de alto impacto",
    },
    alias: ["/registro/aai", "/publicaciones/registrar/articulo_alto_impacto"],
  },
  {
    path: "/publicaciones/registrar/articulo-regional",
    name: "RegistroArticuloRegional",
    component: ArticuloRegionalForm,
    meta: {
      requiresAuth: true,
      title: "Registrar artículo regional",
    },
    alias: ["/registro/ar", "/publicaciones/registrar/articulo_regional"],
  },
  {
    path: "/publicaciones/registrar/capitulo-libro",
    name: "RegistroCapituloLibro",
    component: CapituloLibroForm,
    meta: {
      requiresAuth: true,
      title: "Registrar capítulo de libro",
    },
    alias: [
      "/registro/capitulo-libro",
      "/registro/capitulo_libro",
      "/publicaciones/registrar/capitulo_libro",
    ],
  },
  {
    path: "/publicaciones/registrar/libro",
    name: "RegistroLibro",
    component: LibroForm,
    meta: {
      requiresAuth: true,
      title: "Registrar libro",
    },
    alias: ["/registro/libro"],
  },
  {
    path: "/publicaciones/registrar/ponencia",
    name: "RegistroPonencia",
    component: PonenciaRegistro,
    meta: {
      requiresAuth: true,
      title: "Registrar ponencia",
    },
    alias: ["/registro/ponencia"],
  },

  {
    path: "/publicacion/:id",
    name: "PublicacionDetalle",
    component: PublicacionDetalleView,
    meta: {
      requiresAuth: true,
      title: "Detalle de publicación",
    },
    props: true,
    alias: ["/publicaciones/:id"],
  },
  {
    path: "/publicacion/:id/editar",
    name: "EditarPublicacion",
    component: PublicacionDetalleView,
    meta: {
      requiresAuth: true,
      title: "Editar publicación",
    },
    props: true,
    alias: ["/publicaciones/:id/editar"],
  },

  // =========================
  // Proyectos
  // =========================
  {
    path: "/proyectos",
    name: "ProyectosListado",
    component: ProyectosListadoView,
    meta: {
      requiresAuth: true,
      title: "Proyectos institucionales",
    },
    alias: ["/proyectos-listado"],
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

  // =========================
  // Administración
  // =========================
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
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Panel de administración",
    },
    alias: ["/admin-panel"],
  },
  {
    path: "/admin/usuarios",
    name: "AdminUsuarios",
    component: AdminUsuariosView,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Gestión de usuarios",
    },
    alias: ["/admin-usuarios", "/admin-panel-usuarios"],
  },

  {
    path: "/admin/publicaciones",
    name: "AdminPublicaciones",
    component: AdminPublicacionesView,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Gestión de publicaciones",
    },
    alias: [
      "/admin-publicaciones",
      "/admin-panel-publicaciones",
      "/admin/gestion-publicaciones",
    ],
  },

  {
    path: "/admin/publicaciones/usuario/:usuarioId",
    name: "AdminPublicacionesUsuario",
    component: AdminPublicacionesView,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Publicaciones del usuario",
    },
    props: (route) => ({
      usuarioId: Number(route.params.usuarioId),
    }),
  },

  {
    path: "/admin/publicaciones/usuario/:usuarioId/registrar/articulo-alto-impacto",
    name: "AdminRegistroArticuloAltoImpactoUsuario",
    component: ArticuloAltoImpactoForm,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar artículo de alto impacto",
    },
    props: true,
  },
  {
    path: "/admin/publicaciones/usuario/:usuarioId/registrar/articulo-regional",
    name: "AdminRegistroArticuloRegionalUsuario",
    component: ArticuloRegionalForm,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar artículo regional",
    },
    props: true,
  },
  {
    path: "/admin/publicaciones/usuario/:usuarioId/registrar/ponencia",
    name: "AdminRegistroPonenciaUsuario",
    component: PonenciaRegistro,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar ponencia",
    },
    props: true,
  },
  {
    path: "/admin/publicaciones/usuario/:usuarioId/registrar/libro",
    name: "AdminRegistroLibroUsuario",
    component: LibroForm,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar libro",
    },
    props: true,
  },
  {
    path: "/admin/publicaciones/usuario/:usuarioId/registrar/capitulo-libro",
    name: "AdminRegistroCapituloLibroUsuario",
    component: CapituloLibroForm,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      delegatedPublication: true,
      title: "Registrar capítulo de libro",
    },
    props: true,
  },

  {
    path: "/admin/publicaciones/registrar/articulo-alto-impacto",
    redirect: (to) =>
      redirectToDelegatedAdminRoute(
        to,
        "AdminRegistroArticuloAltoImpactoUsuario"
      ),
  },
  {
    path: "/admin/publicaciones/registrar/articulo-regional",
    redirect: (to) =>
      redirectToDelegatedAdminRoute(to, "AdminRegistroArticuloRegionalUsuario"),
  },
  {
    path: "/admin/publicaciones/registrar/ponencia",
    redirect: (to) =>
      redirectToDelegatedAdminRoute(to, "AdminRegistroPonenciaUsuario"),
  },
  {
    path: "/admin/publicaciones/registrar/libro",
    redirect: (to) =>
      redirectToDelegatedAdminRoute(to, "AdminRegistroLibroUsuario"),
  },
  {
    path: "/admin/publicaciones/registrar/capitulo-libro",
    redirect: (to) =>
      redirectToDelegatedAdminRoute(to, "AdminRegistroCapituloLibroUsuario"),
  },

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
      title: "Editar publicación",
    },
    props: true,
  },

  {
    path: "/admin/facultades-carreras",
    name: "GestionFacultadesCarreras",
    component: GestionFacultadesCarrerasView,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Administrar facultades y carreras",
    },
    alias: ["/admin/catalogos", "/admin-catalogos", "/admin-panel-catalogos"],
  },
  {
    path: "/admin/autores-externos",
    redirect: { name: "AdminUsuarios" },
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Autores externos",
    },
    alias: ["/admin-autores-externos"],
  },
  {
    path: "/admin/facultades",
    redirect: {
      name: "GestionFacultadesCarreras",
      query: { tab: "facultades" },
    },
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Facultades",
    },
    alias: ["/admin-facultades"],
  },
  {
    path: "/admin/carreras",
    redirect: {
      name: "GestionFacultadesCarreras",
      query: { tab: "carreras" },
    },
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Carreras",
    },
    alias: ["/admin-carreras"],
  },

  {
    path: "/:pathMatch(.*)*",
    redirect: "/home",
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
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

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();

  const isResetPasswordRoute =
    to.path === "/reset-password" || to.path === "/restablecer-contrasena";

  if (isResetPasswordRoute) {
    return next();
  }

  const comingFromMicrosoftOnLogin =
    to.path === "/login" &&
    (to.query.code || to.query.ms_code || to.query.ms_error);

  if (comingFromMicrosoftOnLogin) {
    return next();
  }

  await userStore.bootstrapAuth();

  if (to.path === "/login" && userStore.isAuthenticated) {
    return next("/home");
  }

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    return next("/login");
  }

  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    return next("/home");
  }

  if (to.meta.delegatedPublication) {
    const usuarioId = resolveDelegatedUserId(to);

    if (!usuarioId) {
      return next({ name: "AdminPublicaciones" });
    }
  }

  return next();
});

router.afterEach((to) => {
  const nearestWithTitle = [...to.matched]
    .reverse()
    .find((route) => route.meta?.title);

  const pageTitle = nearestWithTitle?.meta?.title;
  document.title = pageTitle ? `${pageTitle} | ${APP_TITLE}` : APP_TITLE;
});

export default router;