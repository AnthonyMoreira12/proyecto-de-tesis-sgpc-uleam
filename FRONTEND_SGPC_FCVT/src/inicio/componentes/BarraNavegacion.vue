<template>
  <div
    class="sgpc-nav"
    :class="{ 'is-sidebar-collapsed': sidebarCollapsed }"
    :style="{ '--sgpc-nav-offset': `${navOffset}px` }"
  >
    <div
      class="sgpc-nav__overlay"
      :class="{
        'is-visible': panelBackdropVisible,
        'is-drawer-open': drawerOpen,
        'is-search-open': searchPanelOpen,
        'is-account-open': accountOpen
      }"
      aria-hidden="true"
      @click="closeAllPanels"
    ></div>

    <aside
      class="sgpc-nav__sidebar"
      :class="{ 'is-open': drawerOpen }"
      aria-label="Menú de navegación"
    >
      <div class="sgpc-nav__brand-panel">
        <button
          class="sgpc-nav__brand"
          type="button"
          title="Sistema de Gestión de Producción Científica ULEAM"
          aria-label="Ir al inicio de SGPC ULEAM"
          @click="goHomeFromLogo"
        >
          <img
            src="../../assets/LOGO-ULEAM-VERTICAL.png"
            alt="Logo ULEAM"
            class="sgpc-nav__brand-logo"
          />

          <span class="sgpc-nav__brand-copy">
            <strong><span>SGPC</span> ULEAM</strong>
            <small>Producción científica</small>
          </span>
        </button>

        <button
          class="sgpc-nav__close-drawer"
          type="button"
          aria-label="Cerrar menú"
          @click="closeDrawer"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              d="M18 6 6 18M6 6l12 12"
            />
          </svg>
        </button>

        <button
          class="sgpc-nav__collapse-toggle"
          type="button"
          :aria-label="sidebarToggleTitle"
          :title="sidebarToggleTitle"
          @click.stop="toggleSidebarCollapse"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="none"
              stroke="currentColor"
              stroke-width="2.4"
              stroke-linecap="round"
              stroke-linejoin="round"
              :d="
                sidebarCollapsed
                  ? 'M9 5l7 7-7 7'
                  : 'M15 5l-7 7 7 7'
              "
            />
          </svg>
        </button>
      </div>

      <nav
        ref="menuRef"
        class="sgpc-nav__menu"
        aria-label="Opciones del sistema"
        @mouseover="handleCollapsedMenuPointer"
        @mouseout="handleCollapsedMenuPointerLeave"
        @focusin="handleCollapsedMenuFocus"
        @focusout="handleCollapsedMenuFocusLeave"
      >
        <div class="sgpc-nav__section-title sgpc-nav__section-title--principal">
          Principal
        </div>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isRouteActive(
                '/home',
                '/inicio'
              )
          }"
          title="Inicio"
          @click="goHomeFromLogo"
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M12 3l9 8h-3v10h-5v-6H11v6H6V11H3l9-8z"
              />
            </svg>
          </span>

          <span>Inicio</span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isRouteActive(
                '/tipos-publicacion'
              )
          }"
          title="Registrar publicación"
          @click="go('/tipos-publicacion')"
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M19 11H13V5h-2v6H5v2h6v6h2v-6h6v-2z"
              />
            </svg>
          </span>

          <span>
            Registrar publicación
          </span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isAvisosRouteActive
          }"
          title="Avisos"
          @click="goAvisos"
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M4 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-5 4V5Zm2 0v10.17L8.28 14H18V5H6Zm2 2h8v2H8V7Zm0 4h6v2H8v-2Z"
              />
            </svg>
          </span>

          <span>Avisos</span>
        </button>

        <button
          v-if="isAuthenticated"
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isRouteActive(
                '/notificaciones',
                '/notifications'
              )
          }"
          title="Notificaciones"
          @click="
            go('/notificaciones')
          "
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-5v-5a7 7 0 0 0-5-6.71V4a2 2 0 1 0-4 0v1.29A7 7 0 0 0 5 12v5l-2 2h18l-2-2Zm-2 0H7v-5a5 5 0 0 1 10 0v5Z"
              />
            </svg>
          </span>

          <span>
            Notificaciones
          </span>
        </button>

        <div class="sgpc-nav__section-title sgpc-nav__section-title--academic">
          Académico
        </div>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isRouteActive(
                '/perfil/me',
                '/perfil-academico/me'
              )
          }"
          title="Mi perfil académico"
          @click="goMyScholarProfile"
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2-8 4.5V20h16v-1.5C20 16 16.42 14 12 14Z"
              />
            </svg>
          </span>

          <span>
            Mi perfil académico
          </span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isRouteActive(
                '/proyectos-listado'
              )
          }"
          title="Proyectos"
          @click="
            go('/proyectos-listado')
          "
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M4 7a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Zm3-1a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H7Z"
              />
            </svg>
          </span>

          <span>Proyectos</span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isRouteActive(
                '/mis-publicaciones'
              )
          }"
          title="Mis publicaciones"
          @click="
            go('/mis-publicaciones')
          "
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M4 5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2V5Zm2 0v14h10V5H6Z"
              />
            </svg>
          </span>

          <span>
            Mis publicaciones
          </span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{ 'is-active': isRouteActive('/informacion-pendiente') }"
          title="Información pendiente"
          @click="go('/informacion-pendiente')"
        >
          <span class="sgpc-nav__menu-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5Zm2 4v2h10V7H7Zm0 4v2h7v-2H7Zm0 4v2h5v-2H7Z"/></svg>
          </span>
          <span class="sgpc-nav__menu-label">
            Información pendiente
          </span>

          <span
            v-if="pendingUpdatesCount"
            class="sgpc-nav__menu-count"
          >
            {{ pendingUpdatesCount }}
          </span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isRouteActive(
                '/mis-reportes'
              )
          }"
          title="Mi producción científica"
          @click="
            go('/mis-reportes')
          "
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm2 11v3h2v-3H7Zm4-5v8h2V9h-2Zm4 2v6h2v-6h-2Z"
              />
            </svg>
          </span>

          <span>
            Mi producción científica
          </span>
        </button>

        <button
          type="button"
          class="sgpc-nav__menu-item"
          :class="{
            'is-active':
              isRouteActive(
                '/publicaciones-listado'
              )
          }"
          :title="publicationsListLabel"
          @click="
            go('/publicaciones-listado')
          "
        >
          <span class="sgpc-nav__menu-icon">
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fill="currentColor"
                d="M3 5h18v2H3V5Zm0 6h18v2H3v-2Zm0 6h18v2H3v-2Z"
              />
            </svg>
          </span>

          <span>
            {{ publicationsMenuLabel }}
          </span>
        </button>

        <template v-if="isAdmin">
          <div class="sgpc-nav__section-title sgpc-nav__section-title--admin">
            Administración
          </div>

          <button
            type="button"
            class="sgpc-nav__menu-item"
            :class="{
              'is-active':
                isRouteActive(
                  '/admin/panel',
                  '/admin-panel'
                )
            }"
            title="Panel administrativo"
            @click="go('/admin/panel')"
          >
            <span class="sgpc-nav__menu-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="currentColor"
                  d="M4 4h7v7H4V4Zm9 0h7v5h-7V4ZM4 13h7v7H4v-7Zm9-2h7v9h-7v-9Z"
                />
              </svg>
            </span>

            <span>Panel</span>
          </button>

          <!-- =================================================
               PRODUCCIÓN CIENTÍFICA
          ================================================== -->
          <div class="sgpc-nav__admin-group">
            <button
              type="button"
              class="sgpc-nav__menu-item sgpc-nav__admin-group-toggle"
              :class="{
                'is-open': adminOpenGroups.produccion,
                'is-group-active': isAdminGroupActive('produccion')
              }"
              title="Producción científica"
              :aria-expanded="adminOpenGroups.produccion ? 'true' : 'false'"
              aria-controls="sgpc-admin-group-produccion"
              @click="toggleAdminGroup('produccion')"
            >
              <span class="sgpc-nav__menu-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h4M8 13h8v2H8v-2Zm0 4h5v2H8v-2Z"
                  />
                </svg>
              </span>

              <span class="sgpc-nav__admin-group-label">
                Producción científica
                <svg
                  class="sgpc-nav__admin-chevron"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m8 10 4 4 4-4"
                  />
                </svg>
              </span>
            </button>

            <Transition name="sgpc-nav-submenu">
              <div
                v-show="adminOpenGroups.produccion"
                id="sgpc-admin-group-produccion"
                class="sgpc-nav__admin-submenu"
              >
                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active':
                      isRouteActive(
                        '/admin/revision',
                        '/admin/revision-publicaciones',
                        '/admin/cola-revision'
                      )
                  }"
                  title="Revisión de publicaciones"
                  @click="go('/admin/revision')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h4M8 13h5v2H8v-2Zm0 4h4v2H8v-2Zm9.3-4.7 1.4 1.4-4.9 4.9-2.5-2.5 1.4-1.4 1.1 1.1 3.5-3.5Z"
                      />
                    </svg>
                  </span>
                  <span>Revisión de publicaciones</span>
                </button>

                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active':
                      isRouteActive(
                        '/admin/publicaciones',
                        '/admin-publicaciones',
                        '/admin-panel-publicaciones'
                      )
                  }"
                  title="Registrar para usuario"
                  @click="go('/admin/publicaciones')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M6 2h9l5 5v15H6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 2v5h4M8 13h8v2H8v-2Zm0 4h5v2H8v-2Zm9-7h2v3h3v2h-3v3h-2v-3h-3v-2h3v-3Z"
                      />
                    </svg>
                  </span>
                  <span>Registrar para usuario</span>
                </button>

                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active':
                      isRouteActive(
                        '/admin/solicitudes-modificacion-publicaciones'
                      )
                  }"
                  title="Solicitudes de modificación"
                  @click="go('/admin/solicitudes-modificacion-publicaciones')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M5 3h14v18H5V3Zm3 4h8v2H8V7Zm0 4h8v2H8v-2Zm0 4h5v2H8v-2Z"
                      />
                    </svg>
                  </span>
                  <span>Solicitudes de modificación</span>
                </button>
              </div>
            </Transition>
          </div>

          <!-- =================================================
               PERSONAS
          ================================================== -->
          <div class="sgpc-nav__admin-group">
            <button
              type="button"
              class="sgpc-nav__menu-item sgpc-nav__admin-group-toggle"
              :class="{
                'is-open': adminOpenGroups.personas,
                'is-group-active': isAdminGroupActive('personas')
              }"
              title="Personas"
              :aria-expanded="adminOpenGroups.personas ? 'true' : 'false'"
              aria-controls="sgpc-admin-group-personas"
              @click="toggleAdminGroup('personas')"
            >
              <span class="sgpc-nav__menu-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm6-1a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM9 13c-4.42 0-8 2.24-8 5v2h12v-2c0-1.22.5-2.34 1.35-3.28C12.93 13.64 11.05 13 9 13Zm6 0c-.46 0-.9.04-1.33.11A5.7 5.7 0 0 1 15 18v2h8v-1.5c0-3.04-3.58-5.5-8-5.5Z"
                  />
                </svg>
              </span>

              <span class="sgpc-nav__admin-group-label">
                Personas
                <svg class="sgpc-nav__admin-chevron" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m8 10 4 4 4-4"
                  />
                </svg>
              </span>
            </button>

            <Transition name="sgpc-nav-submenu">
              <div
                v-show="adminOpenGroups.personas"
                id="sgpc-admin-group-personas"
                class="sgpc-nav__admin-submenu"
              >
                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active':
                      isRouteActive(
                        '/admin/usuarios',
                        '/admin-usuarios',
                        '/admin-panel-usuarios'
                      )
                  }"
                  title="Usuarios"
                  @click="go('/admin/usuarios')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2.24-8 5v1h16v-1c0-2.76-3.58-5-8-5Z"
                      />
                    </svg>
                  </span>
                  <span>Usuarios</span>
                </button>
              </div>
            </Transition>
          </div>

          <!-- =================================================
               INSTITUCIÓN
          ================================================== -->
          <div class="sgpc-nav__admin-group">
            <button
              type="button"
              class="sgpc-nav__menu-item sgpc-nav__admin-group-toggle"
              :class="{
                'is-open': adminOpenGroups.institucion,
                'is-group-active': isAdminGroupActive('institucion')
              }"
              title="Institución"
              :aria-expanded="adminOpenGroups.institucion ? 'true' : 'false'"
              aria-controls="sgpc-admin-group-institucion"
              @click="toggleAdminGroup('institucion')"
            >
              <span class="sgpc-nav__menu-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M3 10.5 12 4l9 6.5v1.8H3v-1.8ZM5 14h2v5H5v-5Zm4 0h2v5H9v-5Zm4 0h2v5h-2v-5Zm4 0h2v5h-2v-5ZM3 21v-2h18v2H3Z"
                  />
                </svg>
              </span>

              <span class="sgpc-nav__admin-group-label">
                Institución
                <svg class="sgpc-nav__admin-chevron" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m8 10 4 4 4-4"
                  />
                </svg>
              </span>
            </button>

            <Transition name="sgpc-nav-submenu">
              <div
                v-show="adminOpenGroups.institucion"
                id="sgpc-admin-group-institucion"
                class="sgpc-nav__admin-submenu"
              >
                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active':
                      isRouteActive(
                        '/admin/estructura',
                        '/admin/facultades-carreras',
                        '/admin/catalogos',
                        '/admin-catalogos',
                        '/admin-panel-catalogos',
                        '/admin/facultades',
                        '/admin/carreras'
                      )
                  }"
                  title="Estructura académica"
                  @click="go('/admin/estructura/facultades')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M3 10.5 12 4l9 6.5v1.8H3v-1.8ZM5 14h2v5H5v-5Zm4 0h2v5H9v-5Zm4 0h2v5h-2v-5Zm4 0h2v5h-2v-5ZM3 21v-2h18v2H3Z"
                      />
                    </svg>
                  </span>
                  <span>Estructura académica</span>
                </button>
              </div>
            </Transition>
          </div>

          <!-- =================================================
               CONTROL
          ================================================== -->
          <div class="sgpc-nav__admin-group">
            <button
              type="button"
              class="sgpc-nav__menu-item sgpc-nav__admin-group-toggle"
              :class="{
                'is-open': adminOpenGroups.control,
                'is-group-active': isAdminGroupActive('control')
              }"
              title="Control"
              :aria-expanded="adminOpenGroups.control ? 'true' : 'false'"
              aria-controls="sgpc-admin-group-control"
              @click="toggleAdminGroup('control')"
            >
              <span class="sgpc-nav__menu-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M12 2 4 5v6c0 5.2 3.4 9.8 8 11 4.6-1.2 8-5.8 8-11V5l-8-3Zm0 2.1L18 6.3V11c0 4.1-2.5 7.8-6 9-3.5-1.2-6-4.9-6-9V6.3l6-2.2Z"
                  />
                </svg>
              </span>

              <span class="sgpc-nav__admin-group-label">
                Control
                <svg class="sgpc-nav__admin-chevron" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m8 10 4 4 4-4"
                  />
                </svg>
              </span>
            </button>

            <Transition name="sgpc-nav-submenu">
              <div
                v-show="adminOpenGroups.control"
                id="sgpc-admin-group-control"
                class="sgpc-nav__admin-submenu"
              >
                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active': isRouteActive('/admin/auditoria')
                  }"
                  title="Auditoría"
                  @click="go('/admin/auditoria')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M4 3h16v18H4V3Zm2 2v14h12V5H6Zm2 3h8v2H8V8Zm0 4h8v2H8v-2Zm0 4h5v2H8v-2Z"
                      />
                    </svg>
                  </span>
                  <span>Auditoría</span>
                </button>

                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active': isRouteActive('/admin/actualizaciones')
                  }"
                  title="Actualización de datos"
                  @click="go('/admin/actualizaciones')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M12 2a10 10 0 1 0 9.54 13H19.4A8 8 0 1 1 12 4V1l4 4-4 4V6a6 6 0 1 0 5.65 8H20A8 8 0 1 1 12 4V2Z"
                      />
                    </svg>
                  </span>
                  <span>Actualización de datos</span>
                </button>
              </div>
            </Transition>
          </div>

          <!-- =================================================
               HERRAMIENTAS AVANZADAS
          ================================================== -->
          <div class="sgpc-nav__admin-group sgpc-nav__admin-group--advanced">
            <button
              type="button"
              class="sgpc-nav__menu-item sgpc-nav__admin-group-toggle"
              :class="{
                'is-open': adminOpenGroups.avanzadas,
                'is-group-active': isAdminGroupActive('avanzadas')
              }"
              title="Herramientas avanzadas"
              :aria-expanded="adminOpenGroups.avanzadas ? 'true' : 'false'"
              aria-controls="sgpc-admin-group-avanzadas"
              @click="toggleAdminGroup('avanzadas')"
            >
              <span class="sgpc-nav__menu-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="currentColor"
                    d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm9 4-2.3-1.1.2-2.6-2.1-2.1-2.6.2L13 4h-2l-1.1 2.4-2.6-.2-2.1 2.1.2 2.6L3 12v2l2.4 1.1-.2 2.6 2.1 2.1 2.6-.2L11 22h2l1.1-2.4 2.6.2 2.1-2.1-.2-2.6L21 14v-2Z"
                  />
                </svg>
              </span>

              <span class="sgpc-nav__admin-group-label">
                Herramientas avanzadas
                <svg class="sgpc-nav__admin-chevron" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="m8 10 4 4 4-4"
                  />
                </svg>
              </span>
            </button>

            <Transition name="sgpc-nav-submenu">
              <div
                v-show="adminOpenGroups.avanzadas"
                id="sgpc-admin-group-avanzadas"
                class="sgpc-nav__admin-submenu"
              >
                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active': isRouteActive('/admin/integridad-documental')
                  }"
                  title="Control de documentos"
                  @click="go('/admin/integridad-documental')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M12 2 4 5v6c0 5.2 3.4 9.8 8 11 4.6-1.2 8-5.8 8-11V5l-8-3Zm-1 14-4-4 1.4-1.4L11 13.2l4.6-4.6L17 10l-6 6Z"
                      />
                    </svg>
                  </span>
                  <span>Control de documentos</span>
                </button>

                <button
                  type="button"
                  class="sgpc-nav__menu-item sgpc-nav__admin-subitem"
                  :class="{
                    'is-active': isRouteActive('/admin/preparacion-produccion')
                  }"
                  title="Preparación de actualización"
                  @click="go('/admin/preparacion-produccion')"
                >
                  <span class="sgpc-nav__menu-icon">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M4 4h16v4H4V4Zm0 6h10v10H4V10Zm12 0h4v4h-4v-4Zm0 6h4v4h-4v-4ZM7 13h4v2H7v-2Z"
                      />
                    </svg>
                  </span>
                  <span>Preparación de actualización</span>
                </button>
              </div>
            </Transition>
          </div>
        </template>
      </nav>
    </aside>

    <Teleport to="body">
      <Transition name="sgpc-nav-tooltip">
        <div
          v-if="collapsedTooltip.visible"
          class="sgpc-nav__collapsed-tooltip"
          :style="{
            top: `${collapsedTooltip.top}px`,
            left: `${collapsedTooltip.left}px`
          }"
          role="tooltip"
        >
          {{ collapsedTooltip.label }}
        </div>
      </Transition>
    </Teleport>

    <header
      ref="headerEl"
      class="sgpc-nav__topbar"
      :class="{
        'is-loaded': loaded,
        'is-scrolled': isScrolled,
        'has-open-panel':
          drawerOpen ||
          searchPanelOpen ||
          accountOpen
      }"
    >
      <!--
        Ya no mostramos el nombre de la interfaz.
        Este contenedor queda reservado para
        el botón hamburguesa en dispositivos móviles.
      -->
      <div class="sgpc-nav__topbar-left">
        <button
          class="sgpc-nav__menu-toggle"
          type="button"
          aria-label="Abrir menú"
          @click="openDrawer"
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              fill="currentColor"
              d="M3 6h18v2H3V6zm0 5h18v2H3v-2zm0 5h18v2H3v-2z"
            />
          </svg>
        </button>
      </div>

      <div class="sgpc-nav__topbar-right">
        <button
          ref="searchTrigger"
          class="
            sgpc-nav__top-action
            sgpc-nav__top-search
          "
          :class="{
            'is-open':
              searchPanelOpen
          }"
          type="button"
          aria-label="Abrir búsqueda global"
          :aria-expanded="
            searchPanelOpen
              ? 'true'
              : 'false'
          "
          aria-haspopup="dialog"
          title="Buscar (Ctrl + K)"
          @click.stop="toggleSearch"
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              fill="currentColor"
              d="M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z"
            />
          </svg>

          <span>Buscar</span>

          <kbd>Ctrl K</kbd>
        </button>

        <button
          class="
            sgpc-nav__top-action
            sgpc-nav__theme-top-btn
          "
          :class="{
            'is-active':
              uiDarkMode
          }"
          type="button"
          :aria-label="
            themeToggleTitle
          "
          :title="
            themeToggleTitle
          "
          :aria-pressed="
            uiDarkMode
              ? 'true'
              : 'false'
          "
          @click.stop="
            toggleDarkMode
          "
        >
          <svg
            v-if="uiDarkMode"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              fill="currentColor"
              d="M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12Zm0-2a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm-1-14h2v3h-2V2Zm0 17h2v3h-2v-3ZM4.22 5.64l1.42-1.42 2.12 2.12-1.42 1.42-2.12-2.12Zm12.02 12.02 1.42-1.42 2.12 2.12-1.42 1.42-2.12-2.12ZM2 11h3v2H2v-2Zm17 0h3v2h-3v-2ZM4.22 18.36l2.12-2.12 1.42 1.42-2.12 2.12-1.42-1.42ZM16.24 6.34l2.12-2.12 1.42 1.42-2.12 2.12-1.42-1.42Z"
            />
          </svg>

          <svg
            v-else
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              fill="currentColor"
              d="M21 14.56A8.8 8.8 0 0 1 9.44 3a7.15 7.15 0 1 0 11.56 11.56Z"
            />
          </svg>
        </button>

        <template
          v-if="
            !isAuthenticated
          "
        >
          <button
            class="
              sgpc-nav__login-btn
            "
            type="button"
            @click="go('/login')"
          >
            Iniciar sesión
          </button>
        </template>

        <template v-else>
          <NotificacionesDropdown
            ref="notificationsDropdown"
            @opened="
              handleNotificationsOpened
            "
          />

          <div
            ref="accountWrap"
            class="
              sgpc-nav__account-wrap
            "
          >
            <button
              ref="accountTrigger"
              class="
                sgpc-nav__account-trigger
              "
              :class="{
                'is-open':
                  accountOpen
              }"
              type="button"
              aria-label="Cuenta"
              aria-haspopup="dialog"
              aria-controls="
                sgpc-nav-account-card
              "
              :aria-expanded="
                accountOpen
                  ? 'true'
                  : 'false'
              "
              @click.stop="
                toggleAccount
              "
            >
              <span
                class="
                  sgpc-nav__avatar-btn
                "
                aria-hidden="true"
              >
                <img
                  v-if="
                    userAvatar
                  "
                  :src="userAvatar"
                  class="
                    sgpc-nav__avatar-img
                  "
                  alt=""
                  loading="eager"
                  decoding="async"
                  fetchpriority="high"
                  @error="
                    handleAvatarImgError
                  "
                />

                <span
                  v-else
                  class="
                    sgpc-nav__avatar-initial
                  "
                >
                  {{ userInitial }}
                </span>
              </span>

              <span
                class="
                  sgpc-nav__account-name
                "
              >
                {{ userName }}
              </span>
            </button>

            <div
              id="
                sgpc-nav-account-card
              "
              ref="accountCard"
              class="
                sgpc-nav__account-card
              "
              :class="{
                'is-open':
                  accountOpen
              }"
              role="dialog"
              aria-modal="false"
              aria-label="
                Panel de cuenta
              "
              tabindex="-1"
              @click.stop
            >
              <div
                class="
                  sgpc-nav__account-top
                "
              >
                <div
                  class="
                    sgpc-nav__account-photo
                  "
                  aria-hidden="true"
                >
                  <img
                    v-if="
                      userAvatar
                    "
                    :src="userAvatar"
                    class="
                      sgpc-nav__account-photo-img
                    "
                    alt=""
                    loading="eager"
                    decoding="async"
                    fetchpriority="high"
                    @error="
                      handleAvatarImgError
                    "
                  />

                  <div
                    v-else
                    class="
                      sgpc-nav__account-photo-inner
                    "
                  >
                    {{ userInitial }}
                  </div>
                </div>

                <div
                  class="
                    sgpc-nav__account-meta
                  "
                >
                  <p
                    class="
                      sgpc-nav__account-user
                    "
                  >
                    {{ userName }}
                  </p>

                  <p
                    class="
                      sgpc-nav__account-email
                    "
                  >
                    {{
                      userStore.email ||
                      ""
                    }}
                  </p>

                  <p
                    v-if="isAdmin"
                    class="
                      sgpc-nav__account-role
                    "
                  >
                    Administrador
                  </p>
                </div>
              </div>

              <div
                class="
                  sgpc-nav__divider
                "
              ></div>

              <div
                class="
                  sgpc-nav__account-body
                "
              >
                <button
                  class="
                    sgpc-nav__account-link
                  "
                  :class="{
                    'is-active':
                      isRouteActive(
                        '/profile'
                      )
                  }"
                  type="button"
                  @click="
                    goMyAccount
                  "
                >
                  <span>
                    Mi cuenta
                  </span>
                </button>

                <button
                  class="
                    sgpc-nav__account-link
                  "
                  :class="{
                    'is-active':
                      isRouteActive(
                        '/preferencias',
                        '/preferencias-interfaz',
                        '/configuraciones'
                      )
                  }"
                  type="button"
                  @click="
                    goConfig
                  "
                >
                  <span>
                    Preferencias
                  </span>
                </button>

                <button
                  v-if="isAdmin"
                  class="
                    sgpc-nav__account-link
                  "
                  :class="{
                    'is-active':
                      isRouteActive(
                        '/admin',
                        '/admin/panel',
                        '/admin-panel'
                      )
                  }"
                  type="button"
                  @click="
                    goAdminPanel
                  "
                >
                  <span>
                    Administración
                  </span>
                </button>

                <button
                  class="
                    sgpc-nav__account-btn
                    sgpc-nav__account-btn--danger
                  "
                  type="button"
                  @click="logout"
                >
                  <span>
                    Cerrar sesión
                  </span>
                </button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </header>

    <Transition
      name="
        sgpc-nav-command-fade
      "
    >
      <div
        v-if="searchPanelOpen"
        ref="searchPanel"
        class="
          sgpc-nav__command
        "
        :class="{
          'is-idle':
            !showCommandBody,
          'has-body':
            showCommandBody
        }"
        role="dialog"
        aria-modal="true"
        aria-label="
          Búsqueda global
        "
        @click.stop
      >
        <div
          class="
            sgpc-nav__command-head
          "
        >
          <span
            class="
              sgpc-nav__command-icon
            "
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z"
              />
            </svg>
          </span>

          <input
            ref="searchInput"
            v-model="queryLocal"
            type="search"
            class="
              sgpc-nav__command-input
            "
            placeholder="
              Buscar publicaciones, autores o proyectos
            "
            title="Buscar"
            role="combobox"
            aria-autocomplete="list"
            aria-label="Buscar"
            :aria-expanded="
              showCommandBody
                ? 'true'
                : 'false'
            "
            :aria-controls="
              showCommandBody
                ? 'sgpc-nav-command-listbox'
                : undefined
            "
            :aria-activedescendant="
              activeDescendantId ||
              undefined
            "
            @input="onInput"
            @keydown.down.prevent="
              move(1)
            "
            @keydown.up.prevent="
              move(-1)
            "
            @keydown.enter.prevent="
              acceptActive
            "
            @keydown.esc.prevent="
              closeSearchPanel(true)
            "
          />
        </div>

        <div
          v-if="showCommandBody"
          id="
            sgpc-nav-command-listbox
          "
          class="
            sgpc-nav__command-body
          "
          role="listbox"
          aria-label="
            Resultados de búsqueda
          "
        >
          <button
            v-if="
              queryLocal.trim()
            "
            class="
              sgpc-nav__command-action
            "
            type="button"
            @click="
              submitSearch
            "
          >
            <span
              class="
                sgpc-nav__command-item-icon
              "
              aria-hidden="true"
            >
              <svg viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z"
                />
              </svg>
            </span>

            <span
              class="
                sgpc-nav__command-item-copy
              "
            >
              <span
                class="
                  sgpc-nav__command-item-title
                "
              >
                Buscar “{{
                  queryLocal.trim()
                }}”
              </span>

              <small
                class="
                  sgpc-nav__command-item-subtitle
                "
              >
                Ver todos los resultados
              </small>
            </span>
          </button>

          <div
            v-if="
              suggestLoading
            "
            class="
              sgpc-nav__loading
            "
          >
            <span
              class="
                sgpc-nav__dot
              "
            ></span>

            <span
              class="
                sgpc-nav__dot
              "
            ></span>

            <span
              class="
                sgpc-nav__dot
              "
            ></span>

            <span
              class="
                sgpc-nav__loading-text
              "
            >
              Buscando…
            </span>
          </div>

          <template v-else>
            <template
              v-if="
                normalizedSuggestions.length
              "
            >
              <button
                v-for="
                  s in
                    normalizedSuggestions
                "
                :id="s._optionId"
                :key="s._key"
                type="button"
                class="
                  sgpc-nav__command-item
                "
                :class="{
                  'is-active':
                    activeIndex ===
                    s._flatIndex
                }"
                role="option"
                :aria-selected="
                  activeIndex ===
                  s._flatIndex
                    ? 'true'
                    : 'false'
                "
                @mousemove="
                  activeIndex =
                    s._flatIndex
                "
                @click="
                  applySuggestion(s)
                "
              >
                <span
                  class="
                    sgpc-nav__command-item-icon
                  "
                  aria-hidden="true"
                >
                  <svg
                    viewBox="
                      0 0 24 24
                    "
                  >
                    <path
                      :d="
                        kindIconPath(
                          s.kind
                        )
                      "
                      fill="
                        currentColor
                      "
                    />
                  </svg>
                </span>

                <span
                  class="
                    sgpc-nav__command-item-copy
                  "
                >
                  <span
                    class="
                      sgpc-nav__command-item-title
                    "
                    v-html="
                      highlight(
                        s.label,
                        queryLocal
                      )
                    "
                  ></span>

                  <small
                    class="
                      sgpc-nav__command-item-subtitle
                    "
                  >
                    {{
                      buildSuggestionSubtitle(
                        s
                      )
                    }}
                  </small>
                </span>
              </button>
            </template>

            <p
              v-else
              class="
                sgpc-nav__no-results
              "
            >
              No hay coincidencias
              directas. Presione
              <b>Enter</b> para ver
              todos los resultados.
            </p>
          </template>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";

import {
  storeToRefs,
} from "pinia";

import {
  useRouter,
  useRoute,
} from "vue-router";

import {
  useThemeStore,
} from "../../scripts/stores/themeStore";

import {
  useUserStore,
} from "../../scripts/stores/userStore";

import {
  useScholarStore,
} from "../../scripts/stores/scholarStore";

import NotificacionesDropdown from
  "../../notificaciones/componentes/NotificacionesDropdown.vue";

import {
  asResults,
  listarMisActualizaciones,
} from "../../scripts/api/actualizacionesApi";


/* ============================================================
   STORES / ROUTER
============================================================ */

const themeStore =
  useThemeStore();

const {
  darkMode,
} =
  storeToRefs(
    themeStore
  );

const userStore =
  useUserStore();

const scholarStore =
  useScholarStore();

const router =
  useRouter();

const route =
  useRoute();


/* ============================================================
   ESTADO
============================================================ */

const loaded =
  ref(false);

const isScrolled =
  ref(false);

const drawerOpen =
  ref(false);

const accountOpen =
  ref(false);

const searchPanelOpen =
  ref(false);

const activeIndex =
  ref(-1);

const navOffset =
  ref(66);

const sidebarCollapsed =
  ref(false);

const collapsedTooltip =
  ref({
    visible: false,
    label: "",
    top: 0,
    left: 0,
  });

const avatarBroken =
  ref(false);

const pendingUpdatesCount =
  ref(0);

const adminOpenGroups =
  ref({
    produccion: false,
    personas: false,
    institucion: false,
    control: false,
    avanzadas: false,
  });


/* ============================================================
   REFERENCIAS
============================================================ */

const menuRef =
  ref(null);

const accountWrap =
  ref(null);

const accountTrigger =
  ref(null);

const accountCard =
  ref(null);

const notificationsDropdown =
  ref(null);

const searchTrigger =
  ref(null);

const searchPanel =
  ref(null);

const searchInput =
  ref(null);

const headerEl =
  ref(null);

const queryLocal =
  ref("");


/* ============================================================
   INTERNOS
============================================================ */

let headerResizeObserver =
  null;

let collapsedTooltipTimer =
  null;

const SIDEBAR_COLLAPSE_STORAGE_KEY =
  "sgpc_sidebar_collapsed";


/* ============================================================
   TEMA
============================================================ */

const uiDarkMode =
  computed({
    get: () =>
      !!darkMode.value,

    set: (
      value
    ) =>
      themeStore.setDark?.(
        !!value
      ),
  });


/* ============================================================
   USUARIO
============================================================ */

const isAuthenticated =
  computed(
    () =>
      !!userStore.isAuthenticated
  );

const userName =
  computed(
    () =>
      userStore.fullName ||
      "Usuario"
  );

const userInitial =
  computed(
    () =>
      userStore.inicial ||
      "U"
  );

const isAdmin =
  computed(
    () =>
      !!userStore.isAdmin
  );

const suggestLoading =
  computed(
    () =>
      !!scholarStore.suggestLoading
  );


/* ============================================================
   ETIQUETAS
============================================================ */

const sidebarToggleTitle =
  computed(
    () =>
      sidebarCollapsed.value
        ? "Expandir menú"
        : "Ocultar menú"
  );

const themeToggleTitle =
  computed(
    () =>
      uiDarkMode.value
        ? "Cambiar a modo claro"
        : "Cambiar a modo oscuro"
  );

const publicationsListLabel =
  computed(
    () =>
      "Publicaciones"
  );

const publicationsMenuLabel =
  computed(
    () =>
      "Publicaciones"
  );


/* ============================================================
   ESTADO DE PANELES
============================================================ */

const panelBackdropVisible =
  computed(
    () =>
      drawerOpen.value ||
      searchPanelOpen.value ||
      accountOpen.value
  );

const shouldLockScroll =
  computed(
    () =>
      drawerOpen.value ||
      searchPanelOpen.value ||
      accountOpen.value
  );


/* ============================================================
   AVISOS
============================================================ */

const isAvisosRouteActive =
  computed(() => {
    return (
      String(
        route.query?.modal ||
          ""
      )
        .trim()
        .toLowerCase() ===
      "avisos"
    );
  });


/* ============================================================
   UTILIDADES
============================================================ */

const normalizeNullableString =
  (
    value
  ) => {
    const text =
      String(
        value ?? ""
      ).trim();

    if (!text) {
      return "";
    }

    const lowered =
      text.toLowerCase();

    if (
      lowered === "null" ||
      lowered === "undefined" ||
      lowered === "none" ||
      lowered === "nan" ||
      lowered === "false"
    ) {
      return "";
    }

    return text;
  };


const firstFilled =
  (...values) => {
    return (
      values
        .map(
          normalizeNullableString
        )
        .find(Boolean) ||
      ""
    );
  };


const readStoredUser =
  () => {
    if (
      typeof window ===
      "undefined"
    ) {
      return {};
    }

    try {
      const parsed =
        JSON.parse(
          localStorage.getItem(
            "user"
          ) ||
            "{}"
        );

      return (
        parsed &&
        typeof parsed ===
          "object" &&
        !Array.isArray(
          parsed
        )
      )
        ? parsed
        : {};
    } catch {
      return {};
    }
  };


const resolveAssetUrl =
  (
    value
  ) => {
    const raw =
      normalizeNullableString(
        value
      );

    if (!raw) {
      return "";
    }

    if (
      /^(https?:|data:|blob:)/i.test(
        raw
      )
    ) {
      return raw;
    }

    const apiBase =
      String(
        import.meta.env
          .VITE_API_URL ||
          ""
      ).trim();

    try {
      if (apiBase) {
        const baseUrl =
          new URL(
            apiBase,
            window.location.origin
          );

        const origin =
          `${baseUrl.origin}/`;

        return new URL(
          raw.startsWith("/")
            ? raw.slice(1)
            : raw,
          origin
        ).toString();
      }
    } catch {
      //
    }

    try {
      return new URL(
        raw,
        window.location.origin
      ).toString();
    } catch {
      return raw;
    }
  };


/* ============================================================
   AVATAR
============================================================ */

const userAvatar =
  computed(() => {
    if (
      avatarBroken.value
    ) {
      return null;
    }

    const cached =
      readStoredUser();

    return (
      resolveAssetUrl(
        firstFilled(
          userStore.avatarUrl,
          userStore.avatar,

          userStore.user
            ?.avatar_url,

          userStore.user
            ?.avatarUrl,

          userStore.user
            ?.avatar,

          userStore.user
            ?.foto_url,

          userStore.user
            ?.foto,

          cached.avatar_url,
          cached.avatarUrl,
          cached.avatar,
          cached.foto_url,
          cached.foto
        )
      ) ||
      null
    );
  });


const handleAvatarImgError =
  async () => {
    avatarBroken.value =
      true;

    try {
      await userStore
        .refreshProfile?.();

      avatarBroken.value =
        false;
    } catch {
      avatarBroken.value =
        true;
    }
  };


/* ============================================================
   SIDEBAR
============================================================ */

const isDesktopViewport =
  () => {
    if (
      typeof window ===
      "undefined"
    ) {
      return true;
    }

    return (
      window.matchMedia?.(
        "(min-width: 981px)"
      )?.matches ??
      true
    );
  };


const applySidebarCollapseState =
  () => {
    if (
      typeof document ===
      "undefined"
    ) {
      return;
    }

    document
      .documentElement
      .classList
      .toggle(
        "sgpc-sidebar-collapsed",
        sidebarCollapsed.value &&
          isDesktopViewport()
      );
  };


const loadSidebarCollapsePreference =
  () => {
    if (
      typeof window ===
      "undefined"
    ) {
      sidebarCollapsed.value =
        false;
      return;
    }

    try {
      sidebarCollapsed.value =
        localStorage.getItem(
          SIDEBAR_COLLAPSE_STORAGE_KEY
        ) === "true";
    } catch {
      sidebarCollapsed.value =
        false;
    }
  };


const saveSidebarCollapsePreference =
  () => {
    if (
      typeof window ===
      "undefined"
    ) {
      return;
    }

    try {
      localStorage.setItem(
        SIDEBAR_COLLAPSE_STORAGE_KEY,
        sidebarCollapsed.value
          ? "true"
          : "false"
      );
    } catch {
      // La navegación sigue funcionando aunque el navegador bloquee storage.
    }
  };


const hideCollapsedTooltip =
  (
    immediate = false
  ) => {
    if (
      collapsedTooltipTimer
    ) {
      clearTimeout(
        collapsedTooltipTimer
      );
      collapsedTooltipTimer =
        null;
    }

    const close =
      () => {
        collapsedTooltip.value = {
          ...collapsedTooltip.value,
          visible: false,
        };
      };

    if (immediate) {
      close();
      return;
    }

    collapsedTooltipTimer =
      setTimeout(
        close,
        45
      );
  };


const showCollapsedTooltip =
  (button) => {
    if (
      !sidebarCollapsed.value ||
      !isDesktopViewport() ||
      !button
    ) {
      hideCollapsedTooltip(
        true
      );
      return;
    }

    const label =
      String(
        button.getAttribute?.(
          "title"
        ) ||
        ""
      ).trim();

    if (!label) {
      return;
    }

    const rect =
      button.getBoundingClientRect?.();

    if (!rect) {
      return;
    }

    if (collapsedTooltipTimer) {
      clearTimeout(
        collapsedTooltipTimer
      );
      collapsedTooltipTimer =
        null;
    }

    collapsedTooltip.value = {
      visible: true,
      label,
      top: Math.round(
        rect.top +
        rect.height / 2
      ),
      left: Math.round(
        rect.right + 10
      ),
    };
  };


const menuButtonFromTarget =
  (target) =>
    target?.closest?.(
      ".sgpc-nav__menu-item[title]"
    ) ||
    null;


const handleCollapsedMenuPointer =
  (event) => {
    const button =
      menuButtonFromTarget(
        event.target
      );

    if (!button) {
      return;
    }

    const previousButton =
      menuButtonFromTarget(
        event.relatedTarget
      );

    if (
      previousButton ===
      button
    ) {
      return;
    }

    showCollapsedTooltip(
      button
    );
  };


const handleCollapsedMenuPointerLeave =
  (event) => {
    const button =
      menuButtonFromTarget(
        event.target
      );

    if (!button) {
      return;
    }

    const nextButton =
      menuButtonFromTarget(
        event.relatedTarget
      );

    if (
      nextButton ===
      button
    ) {
      return;
    }

    if (nextButton) {
      showCollapsedTooltip(
        nextButton
      );
      return;
    }

    hideCollapsedTooltip();
  };


const handleCollapsedMenuFocus =
  (event) => {
    showCollapsedTooltip(
      menuButtonFromTarget(
        event.target
      )
    );
  };


const handleCollapsedMenuFocusLeave =
  (event) => {
    const nextButton =
      menuButtonFromTarget(
        event.relatedTarget
      );

    if (nextButton) {
      showCollapsedTooltip(
        nextButton
      );
      return;
    }

    hideCollapsedTooltip();
  };


const handleSidebarViewportChange =
  () => {
    hideCollapsedTooltip(
      true
    );

    applySidebarCollapseState();

    nextTick(
      () =>
        syncNavOffset()
    );
  };


const toggleSidebarCollapse =
  () => {
    hideCollapsedTooltip(
      true
    );

    if (
      !isDesktopViewport()
    ) {
      openDrawer();
      return;
    }

    sidebarCollapsed.value =
      !sidebarCollapsed.value;

    saveSidebarCollapsePreference();

    applySidebarCollapseState();

    nextTick(() => {
      syncNavOffset();
    });
  };


/* ============================================================
   GRUPOS DE ADMINISTRACIÓN
============================================================ */

const ADMIN_GROUP_ROUTES = {
  produccion: [
    "/admin/revision",
    "/admin/revision-publicaciones",
    "/admin/cola-revision",
    "/admin/publicaciones",
    "/admin-publicaciones",
    "/admin-panel-publicaciones",
    "/admin/solicitudes-modificacion-publicaciones",
  ],

  personas: [
    "/admin/usuarios",
    "/admin-usuarios",
    "/admin-panel-usuarios",
  ],

  institucion: [
    "/admin/estructura",
    "/admin/facultades-carreras",
    "/admin/catalogos",
    "/admin-catalogos",
    "/admin-panel-catalogos",
    "/admin/facultades",
    "/admin/carreras",
  ],

  control: [
    "/admin/auditoria",
    "/admin/actualizaciones",
  ],

  avanzadas: [
    "/admin/integridad-documental",
    "/admin/preparacion-produccion",
  ],
};


const routeMatchesBase =
  (
    currentPath,
    basePath
  ) =>
    currentPath === basePath ||
    currentPath.startsWith(
      `${basePath}/`
    );


const adminGroupForPath =
  (
    path = route.path
  ) => {
    const currentPath =
      String(path || "");

    for (
      const [
        group,
        paths,
      ] of Object.entries(
        ADMIN_GROUP_ROUTES
      )
    ) {
      if (
        paths.some(
          (basePath) =>
            routeMatchesBase(
              currentPath,
              basePath
            )
        )
      ) {
        return group;
      }
    }

    return null;
  };


const isAdminGroupActive =
  (group) =>
    adminGroupForPath(
      route.path
    ) === group;


const syncAdminGroupWithRoute =
  () => {
    const group =
      adminGroupForPath(
        route.path
      );

    // La ruta activa abre su grupo, pero no cierra
    // los demás. Así el administrador puede mantener
    // varios grupos desplegados al mismo tiempo.
    if (
      group &&
      Object.prototype.hasOwnProperty.call(
        adminOpenGroups.value,
        group
      )
    ) {
      adminOpenGroups.value[group] =
        true;
    }
  };


const toggleAdminGroup =
  async (group) => {
    hideCollapsedTooltip(
      true
    );

    if (
      sidebarCollapsed.value &&
      isDesktopViewport()
    ) {
      sidebarCollapsed.value =
        false;

      saveSidebarCollapsePreference();
      applySidebarCollapseState();

      await nextTick();
      syncNavOffset();
    }

    if (
      !Object.prototype.hasOwnProperty.call(
        adminOpenGroups.value,
        group
      )
    ) {
      return;
    }

    adminOpenGroups.value[group] =
      !adminOpenGroups.value[group];

    if (
      adminOpenGroups.value[group] &&
      isAdminGroupActive(group)
    ) {
      await scrollActiveMenuItemIntoView();
    }
  };


const scrollActiveMenuItemIntoView =
  async () => {
    await nextTick();

    const menu =
      menuRef.value;

    if (!menu) {
      return;
    }

    if (
      !isDesktopViewport() &&
      !drawerOpen.value
    ) {
      return;
    }

    const activeItem =
      menu.querySelector(
        ".sgpc-nav__menu-item.is-active"
      );

    if (!activeItem) {
      return;
    }

    const menuRect =
      menu.getBoundingClientRect();

    const itemRect =
      activeItem.getBoundingClientRect();

    const safeTop =
      menuRect.top + 10;

    const safeBottom =
      menuRect.bottom - 16;

    if (
      itemRect.top >= safeTop &&
      itemRect.bottom <= safeBottom
    ) {
      return;
    }

    activeItem.scrollIntoView({
      block: "nearest",
      inline: "nearest",
      behavior: "auto",
    });
  };


/* ============================================================
   OFFSET DE NAVEGACIÓN
============================================================ */

const setGlobalNavOffset =
  () => {
    if (
      typeof document ===
      "undefined"
    ) {
      return;
    }

    document
      .documentElement
      .style
      .setProperty(
        "--sgpc-nav-offset",
        `${navOffset.value}px`
      );
  };


const syncNavOffset =
  () => {
    if (
      !headerEl.value
    ) {
      return;
    }

    navOffset.value =
      Math.ceil(
        headerEl.value
          .offsetHeight ||
          66
      );

    setGlobalNavOffset();
  };


/* ============================================================
   SCROLL
============================================================ */

const updateNavbarState =
  () => {
    if (
      typeof window ===
      "undefined"
    ) {
      return;
    }

    const currentY =
      Math.max(
        window.scrollY ||
          0,
        0
      );

    isScrolled.value =
      currentY > 8;
  };


/* ============================================================
   NAVEGACIÓN
============================================================ */

const navigateTo =
  (
    target,
    replace = false
  ) => {
    closeAllPanels();

    const resolved =
      router.resolve(
        target
      );

    if (
      resolved.fullPath ===
      route.fullPath
    ) {
      return null;
    }

    return replace
      ? router.replace(
          target
        )
      : router.push(
          target
        );
  };


const go =
  (
    path
  ) =>
    navigateTo(
      path
    );


const isRouteActive =
  (
    ...paths
  ) =>
    paths.some(
      (
        path
      ) =>
        route.path ===
          path ||
        route.path.startsWith(
          `${path}/`
        )
    );


const goHomeFromLogo =
  () => {
    navigateTo(
      isAuthenticated.value
        ? "/home"
        : "/login"
    );
  };


const goAvisos =
  () => {
    navigateTo({
      path: "/home",

      query: {
        modal:
          "avisos",

        ts:
          Date.now()
            .toString(),
      },
    });
  };


const goMyScholarProfile =
  () => {
    navigateTo(
      "/perfil/me"
    );
  };


const goMyAccount =
  () => {
    navigateTo(
      "/profile"
    );
  };


const goConfig =
  () => {
    navigateTo(
      "/preferencias"
    );
  };


const goAdminPanel =
  () => {
    navigateTo(
      "/admin/panel"
    );
  };


/* ============================================================
   DRAWER
============================================================ */

const openDrawer =
  () => {
    drawerOpen.value =
      true;

    accountOpen.value =
      false;

    closeSearchPanel(
      false
    );

    closeNotifications(
      false
    );
  };


const closeDrawer =
  () => {
    drawerOpen.value =
      false;
  };


/* ============================================================
   CUENTA
============================================================ */

const toggleAccount =
  async () => {
    if (
      accountOpen.value
    ) {
      closeAccount(
        true
      );

      return;
    }

    accountOpen.value =
      true;

    closeSearchPanel(
      false
    );

    closeNotifications(
      false
    );

    if (
      typeof window !==
        "undefined" &&
      window.matchMedia?.(
        "(max-width: 980px)"
      )?.matches
    ) {
      drawerOpen.value =
        false;
    }

    await nextTick();

    accountCard.value
      ?.focus?.();
  };


const closeAccount =
  (
    restoreFocus =
      false
  ) => {
    accountOpen.value =
      false;

    if (
      restoreFocus
    ) {
      nextTick(
        () => {
          accountTrigger
            .value
            ?.focus?.();
        }
      );
    }
  };


/* ============================================================
   NOTIFICACIONES
============================================================ */

const closeNotifications =
  (
    restoreFocus =
      false
  ) => {
    notificationsDropdown
      .value
      ?.close?.(
        restoreFocus
      );
  };


const handleNotificationsOpened =
  () => {
    accountOpen.value =
      false;

    closeSearchPanel(
      false
    );

    if (
      typeof window !==
        "undefined" &&
      window.matchMedia?.(
        "(max-width: 980px)"
      )?.matches
    ) {
      drawerOpen.value =
        false;
    }
  };


/* ============================================================
   BÚSQUEDA
============================================================ */

const closeSearchPanel =
  (
    restoreFocus =
      false
  ) => {
    searchPanelOpen.value =
      false;

    activeIndex.value =
      -1;

    scholarStore
      .clearSuggestions?.();

    if (
      restoreFocus
    ) {
      nextTick(
        () => {
          searchTrigger
            .value
            ?.focus?.();
        }
      );
    }
  };


const closeAllPanels =
  () => {
    closeDrawer();

    closeAccount(
      false
    );

    closeSearchPanel(
      false
    );

    closeNotifications(
      false
    );
  };


const toggleDarkMode =
  () => {
    uiDarkMode.value =
      !uiDarkMode.value;
  };


/* ============================================================
   LOGOUT
============================================================ */

const logout =
  async () => {
    closeAllPanels();

    try {
      await userStore
        .logout?.();
    } catch {
      //
    }

    userStore
      .clearUser?.();

    scholarStore
      .clearAll?.();

    if (
      route.path !==
      "/login"
    ) {
      await router.replace(
        "/login"
      );
    }
  };


/* ============================================================
   SUGERENCIAS
============================================================ */

const normalizeSuggestionKind =
  (
    kind
  ) => {
    const value =
      String(
        kind ||
          ""
      )
        .trim()
        .toLowerCase();

    if (
      value.includes(
        "profile"
      ) ||
      value.includes(
        "perfil"
      ) ||
      value.includes(
        "author"
      ) ||
      value.includes(
        "autor"
      ) ||
      value.includes(
        "investigador"
      )
    ) {
      return "profile";
    }

    if (
      value.includes(
        "publication"
      ) ||
      value.includes(
        "publicacion"
      ) ||
      value.includes(
        "paper"
      ) ||
      value.includes(
        "article"
      ) ||
      value.includes(
        "articulo"
      ) ||
      value.includes(
        "work"
      )
    ) {
      return "publication";
    }

    if (
      value.includes(
        "project"
      ) ||
      value.includes(
        "proyecto"
      )
    ) {
      return "project";
    }

    if (
      value.includes(
        "keyword"
      ) ||
      value.includes(
        "topic"
      ) ||
      value.includes(
        "tema"
      ) ||
      value.includes(
        "tag"
      )
    ) {
      return "keyword";
    }

    return "suggestion";
  };


const normalizedSuggestions =
  computed(() => {
    const raw =
      Array.isArray(
        scholarStore.suggestions
      )
        ? scholarStore.suggestions
        : [];

    return raw
      .map(
        (
          item,
          index
        ) => {
          const label =
            String(
              item?.label ||
                ""
            ).trim();

          if (
            !label
          ) {
            return null;
          }

          const kind =
            normalizeSuggestionKind(
              item?.kind
            );

          return {
            ...item,

            kind,

            label,

            extra:
              String(
                item?.extra ||
                  ""
              ).trim(),

            _flatIndex:
              index,

            _key:
              `${kind}:${
                item?.id ??
                label
              }:${index}`,

            _optionId:
              `sgpc-nav-option-${index}`,
          };
        }
      )
      .filter(Boolean);
  });


const showCommandBody =
  computed(() => {
    const q =
      queryLocal.value
        .trim();

    return (
      suggestLoading.value ||
      normalizedSuggestions
        .value
        .length >
        0 ||
      q.length >=
        2
    );
  });


const activeDescendantId =
  computed(() => {
    const item =
      normalizedSuggestions
        .value[
        activeIndex.value
      ];

    return (
      item?._optionId ||
      ""
    );
  });


const openSearchPanel =
  async () => {
    const q =
      queryLocal.value
        .trim();

    searchPanelOpen.value =
      true;

    activeIndex.value =
      -1;

    accountOpen.value =
      false;

    closeNotifications(
      false
    );

    if (
      typeof window !==
        "undefined" &&
      window.matchMedia?.(
        "(max-width: 980px)"
      )?.matches
    ) {
      drawerOpen.value =
        false;
    }

    await nextTick();

    searchInput.value
      ?.focus?.();

    if (
      q.length >= 2
    ) {
      await scholarStore
        .suggestSmart?.(
          q
        );
    } else {
      scholarStore
        .clearSuggestions?.();
    }
  };


const toggleSearch =
  async () => {
    if (
      searchPanelOpen.value
    ) {
      closeSearchPanel(
        true
      );

      return;
    }

    await openSearchPanel();
  };


const scrollActiveIntoView =
  async () => {
    await nextTick();

    const id =
      activeDescendantId
        .value;

    if (
      !id ||
      typeof document ===
        "undefined"
    ) {
      return;
    }

    const node =
      document.getElementById(
        id
      );

    node?.scrollIntoView?.({
      block:
        "nearest",

      inline:
        "nearest",
    });
  };


const onInput =
  async () => {
    const q =
      queryLocal.value
        .trim();

    activeIndex.value =
      -1;

    if (
      q.length < 2
    ) {
      scholarStore
        .clearSuggestions?.();

      return;
    }

    await scholarStore
      .suggestSmart?.(
        q
      );
  };


const move =
  async (
    dir
  ) => {
    const max =
      normalizedSuggestions
        .value
        .length -
      1;

    if (
      max < 0
    ) {
      return;
    }

    const next =
      activeIndex.value +
      dir;

    if (
      next < 0
    ) {
      activeIndex.value =
        max;
    } else if (
      next > max
    ) {
      activeIndex.value =
        0;
    } else {
      activeIndex.value =
        next;
    }

    await scrollActiveIntoView();
  };


const submitSearch =
  () => {
    const q =
      queryLocal.value
        .trim();

    if (!q) {
      closeSearchPanel(
        true
      );

      return;
    }

    navigateTo({
      path:
        "/busqueda",

      query: {
        q,
      },
    });
  };


const applySuggestion =
  (
    suggestion
  ) => {
    if (
      !suggestion
    ) {
      return;
    }

    const id =
      suggestion.id ??
      suggestion.value ??
      suggestion.pk ??
      "";

    const label =
      String(
        suggestion.label ||
          ""
      ).trim();

    const q =
      label ||
      queryLocal.value
        .trim();

    if (
      suggestion.kind ===
        "publication" &&
      id
    ) {
      navigateTo(
        `/publicacion/${id}`
      );

      return;
    }

    if (
      suggestion.kind ===
        "profile" &&
      id
    ) {
      navigateTo(
        `/perfil/${id}`
      );

      return;
    }

    if (
      suggestion.kind ===
      "project"
    ) {
      navigateTo({
        path:
          "/proyectos-listado",

        query:
          q
            ? {
                q,
              }
            : {},
      });

      return;
    }

    navigateTo({
      path:
        "/busqueda",

      query:
        q
          ? {
              q,
            }
          : {},
    });
  };


const acceptActive =
  () => {
    const item =
      normalizedSuggestions
        .value[
        activeIndex.value
      ];

    if (item) {
      applySuggestion(
        item
      );

      return;
    }

    submitSearch();
  };


const buildSuggestionSubtitle =
  (
    suggestion
  ) => {
    const extra =
      String(
        suggestion?.extra ||
          ""
      ).trim();

    if (extra) {
      return extra;
    }

    if (
      suggestion.kind ===
      "publication"
    ) {
      return "Publicación científica";
    }

    if (
      suggestion.kind ===
      "profile"
    ) {
      return "Perfil académico";
    }

    if (
      suggestion.kind ===
      "project"
    ) {
      return "Proyecto";
    }

    if (
      suggestion.kind ===
      "keyword"
    ) {
      return "Tema de búsqueda";
    }

    return "Sugerencia";
  };


const kindIconPath =
  (
    kind
  ) => {
    if (
      kind ===
      "profile"
    ) {
      return "M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2-8 4.5V20h16v-1.5C20 16 16.42 14 12 14Z";
    }

    if (
      kind ===
      "publication"
    ) {
      return "M6 2h9l5 5v15H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 1.5V8h4.5L14 3.5ZM8 12h8v2H8v-2Zm0 4h8v2H8v-2Z";
    }

    if (
      kind ===
      "project"
    ) {
      return "M4 7a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Zm3-1a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H7Z";
    }

    return "M10 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm11 3-6-6 1.4-1.4 6 6L21 21Z";
  };


/* ============================================================
   ESCAPE / HIGHLIGHT
============================================================ */

const escapeHtml =
  (
    value
  ) =>
    String(
      value ?? ""
    )
      .replace(
        /&/g,
        "&amp;"
      )
      .replace(
        /</g,
        "&lt;"
      )
      .replace(
        />/g,
        "&gt;"
      )
      .replace(
        /"/g,
        "&quot;"
      )
      .replace(
        /'/g,
        "&#039;"
      );


const escapeRegExp =
  (
    value
  ) =>
    String(
      value ?? ""
    ).replace(
      /[.*+?^${}()|[\]\\]/g,
      "\\$&"
    );


const highlight =
  (
    label,
    query
  ) => {
    const safeLabel =
      escapeHtml(
        label
      );

    const q =
      String(
        query ||
          ""
      ).trim();

    if (!q) {
      return safeLabel;
    }

    try {
      const regex =
        new RegExp(
          `(${escapeRegExp(
            q
          )})`,
          "ig"
        );

      return safeLabel.replace(
        regex,
        "<mark>$1</mark>"
      );
    } catch {
      return safeLabel;
    }
  };


/* ============================================================
   EVENTOS GLOBALES
============================================================ */

const onClickOutside =
  (
    event
  ) => {
    const target =
      event.target;

    if (
      accountOpen.value &&
      accountWrap.value &&
      !accountWrap.value.contains(
        target
      )
    ) {
      closeAccount(
        false
      );
    }

    if (
      searchPanelOpen.value &&
      searchPanel.value &&
      searchTrigger.value &&
      !searchPanel.value.contains(
        target
      ) &&
      !searchTrigger.value.contains(
        target
      )
    ) {
      closeSearchPanel(
        false
      );
    }
  };


const onEsc =
  (
    event
  ) => {
    if (
      event.key !==
      "Escape"
    ) {
      return;
    }

    closeAllPanels();
  };


const onGlobalShortcut =
  (
    event
  ) => {
    if (
      typeof document !== "undefined" &&
      document.documentElement.classList.contains(
        "sgpc-modal-open"
      )
    ) {
      return;
    }

    const key =
      String(
        event.key ||
          ""
      ).toLowerCase();

    if (
      (
        event.ctrlKey ||
        event.metaKey
      ) &&
      key === "k"
    ) {
      event.preventDefault();

      toggleSearch();
    }
  };


/* ============================================================
   WATCHERS
============================================================ */

watch(
  () =>
    route.fullPath,

  async () => {
    hideCollapsedTooltip(
      true
    );

    closeDrawer();

    closeAccount(
      false
    );

    closeSearchPanel(
      false
    );

    closeNotifications(
      false
    );

    syncAdminGroupWithRoute();

    queryLocal.value =
      String(
        route.query?.q ||
          ""
      );

    await nextTick();

    await scrollActiveMenuItemIntoView();

    syncNavOffset();

    updateNavbarState();
  }
);


watch(
  () =>
    shouldLockScroll.value,

  (
    value
  ) => {
    if (
      typeof document ===
      "undefined"
    ) {
      return;
    }

    document
      .documentElement
      .classList
      .toggle(
        "sgpc-nav-lock",
        value
      );

    document
      .body
      .classList
      .toggle(
        "sgpc-nav-lock",
        value
      );
  }
);


watch(
  () =>
    userAvatar.value,

  () => {
    avatarBroken.value =
      false;
  }
);


/* ============================================================
   MONTAJE
============================================================ */

async function loadPendingUpdatesCount() {
  if (!isAuthenticated.value) { pendingUpdatesCount.value = 0; return; }
  try {
    const payload = await listarMisActualizaciones();
    pendingUpdatesCount.value = asResults(payload).filter((item) => item.estado !== "completada" && (item.campos_pendientes || []).length).length;
  } catch {
    pendingUpdatesCount.value = 0;
  }
}

onMounted(
  async () => {
    await loadPendingUpdatesCount();
    loaded.value =
      true;

    queryLocal.value =
      String(
        route.query?.q ||
          ""
      );

    loadSidebarCollapsePreference();

    applySidebarCollapseState();

    syncAdminGroupWithRoute();

    await nextTick();

    await scrollActiveMenuItemIntoView();

    syncNavOffset();

    updateNavbarState();

    if (
      typeof window !==
      "undefined"
    ) {
      window.addEventListener(
        "scroll",
        updateNavbarState,
        {
          passive:
            true,
        }
      );

      window.addEventListener(
        "keydown",
        onGlobalShortcut
      );

      window.addEventListener(
        "sgpc:modal-open",
        closeAllPanels
      );

      window.addEventListener(
        "resize",
        syncNavOffset,
        {
          passive:
            true,
        }
      );

      window.addEventListener(
        "resize",
        handleSidebarViewportChange,
        {
          passive:
            true,
        }
      );
    }

    if (
      typeof ResizeObserver !==
        "undefined" &&
      headerEl.value
    ) {
      headerResizeObserver =
        new ResizeObserver(
          () => {
            syncNavOffset();
          }
        );

      headerResizeObserver.observe(
        headerEl.value
      );
    }

    if (
      typeof document !==
      "undefined"
    ) {
      document.addEventListener(
        "click",
        onClickOutside
      );

      document.addEventListener(
        "keydown",
        onEsc
      );

      setGlobalNavOffset();
    }

    if (
      typeof userStore
        .bootstrapAuth ===
      "function"
    ) {
      await userStore.bootstrapAuth({
        force:
          true,
      });
    } else {
      await userStore
        .hydrate?.();

      await userStore
        .refreshProfile?.()
        .catch(
          () =>
            null
        );
    }

    if (
      userStore.isAuthenticated &&
      !String(
        userStore.autorId ||
          ""
      ).trim()
    ) {
      try {
        const {
          data,
        } =
          await import(
            "../../scripts/api/axios"
          ).then(
            (
              mod
            ) =>
              mod.default.get(
                "/scholar/perfiles/me/"
              )
          );

        const authorId =
          data?.id;

        if (
          authorId !=
          null
        ) {
          userStore
            .setAutorId?.(
              authorId
            );
        }
      } catch {
        //
      }
    }

    await nextTick();

    syncNavOffset();
  }
);


/* ============================================================
   DESMONTAJE
============================================================ */

onBeforeUnmount(
  () => {
    hideCollapsedTooltip(
      true
    );

    if (collapsedTooltipTimer) {
      clearTimeout(
        collapsedTooltipTimer
      );
      collapsedTooltipTimer =
        null;
    }

    if (
      typeof document !==
      "undefined"
    ) {
      document
        .documentElement
        .classList
        .remove(
          "sgpc-nav-lock"
        );

      document
        .documentElement
        .classList
        .remove(
          "sgpc-sidebar-collapsed"
        );

      document
        .body
        .classList
        .remove(
          "sgpc-nav-lock"
        );

      document.removeEventListener(
        "click",
        onClickOutside
      );

      document.removeEventListener(
        "keydown",
        onEsc
      );

      document
        .documentElement
        .style
        .removeProperty(
          "--sgpc-nav-offset"
        );
    }

    if (
      typeof window !==
      "undefined"
    ) {
      window.removeEventListener(
        "scroll",
        updateNavbarState
      );

      window.removeEventListener(
        "keydown",
        onGlobalShortcut
      );

      window.removeEventListener(
        "sgpc:modal-open",
        closeAllPanels
      );

      window.removeEventListener(
        "resize",
        syncNavOffset
      );

      window.removeEventListener(
        "resize",
        handleSidebarViewportChange
      );
    }

    if (
      headerResizeObserver
    ) {
      headerResizeObserver.disconnect();

      headerResizeObserver =
        null;
    }
  }
);
</script>

<style src="./barra-navegacion.css"></style>