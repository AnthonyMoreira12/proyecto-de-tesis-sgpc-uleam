<template>
  <main class="perfil-container">
    <div
      v-if="loading"
      class="perfil-shell"
      aria-label="Cargando perfil"
      aria-busy="true"
    >
      <section class="perfil-context perfil-context--loading">
        <div class="perfil-skeleton sk-line sk-line--text"></div>
        <div class="perfil-skeleton sk-line sk-line--small"></div>
      </section>

      <div class="perfil-layout">
        <aside class="perfil-sidebar-card perfil-sidebar-card--loading">
          <div class="perfil-skeleton sk-avatar"></div>
          <div class="perfil-skeleton sk-line sk-line--name"></div>
          <div class="perfil-skeleton sk-line sk-line--email"></div>
          <div class="perfil-skeleton sk-block"></div>
        </aside>

        <div class="perfil-main">
          <div class="perfil-card perfil-loading-card">
            <div class="perfil-skeleton sk-line sk-line--section"></div>
            <div class="perfil-skeleton sk-grid"></div>
          </div>

          <div class="perfil-card perfil-loading-card">
            <div class="perfil-skeleton sk-line sk-line--section"></div>
            <div class="perfil-skeleton sk-grid sk-grid--fields"></div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-else-if="user"
      class="perfil-shell"
    >
      <header
        class="perfil-context page-stage page-stage-1"
        aria-label="Acciones del perfil"
      >
        <h1 class="perfil-context__title">
          Perfil
        </h1>

        <button
          class="perfil-primary-button perfil-context__action"
          :class="{
            'is-request': !canEditProfile,
          }"
          type="button"
          :title="
            canEditProfile
              ? 'Editar información del perfil'
              : 'Solicitar más tiempo para editar el perfil'
          "
          @click="handleEditAction"
        >
          <svg
            v-if="canEditProfile"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              d="m12.7 4.2 3.1 3.1M4 16l2.8-.6 8.4-8.4a1.6 1.6 0 0 0 0-2.3 1.6 1.6 0 0 0-2.3 0L4.6 13.2 4 16Z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>

          <svg
            v-else
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              d="M3.5 5.5A1.5 1.5 0 0 1 5 4h10a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 15 16H5a1.5 1.5 0 0 1-1.5-1.5v-9Z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            />

            <path
              d="m4 6 6 4.5L16 6"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>

          <span>
            {{
              canEditProfile
                ? "Editar perfil"
                : "Solicitar más tiempo"
            }}
          </span>
        </button>
      </header>

      <div class="perfil-layout page-stage page-stage-2">
        <aside class="perfil-sidebar">
          <section class="perfil-sidebar-card">
            <div class="perfil-avatar-area">
              <button
                class="perfil-avatar-button"
                type="button"
                :title="avatarButtonLabel"
                :aria-label="avatarButtonLabel"
                @click="openAvatarFlow"
              >
                <img
                  v-if="hasAvatar"
                  :src="user.avatar_url"
                  alt="Foto de perfil"
                  class="perfil-avatar"
                  @error="avatarBroken = true"
                />

                <span
                  v-else
                  class="perfil-avatar-placeholder"
                  aria-hidden="true"
                >
                  {{ initials }}
                </span>

                <span class="perfil-avatar-edit" aria-hidden="true">
                  <svg viewBox="0 0 20 20">
                    <path
                      d="M4 6.5A2.5 2.5 0 0 1 6.5 4H8l1-1.3h2L12 4h1.5A2.5 2.5 0 0 1 16 6.5v7a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 4 13.5v-7Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />

                    <circle
                      cx="10"
                      cy="10"
                      r="2.4"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />
                  </svg>
                </span>
              </button>
            </div>

            <div class="perfil-identidad">
              <span class="perfil-eyebrow">
                {{ roleLabel }}
              </span>

              <h2 class="perfil-nombre">
                {{ displayName }}
              </h2>

              <p class="perfil-correo">
                {{ user.email || "Sin correo registrado" }}
              </p>
            </div>

            
            

            <div class="perfil-sidebar-divider"></div>

            <nav
              class="perfil-sidebar-nav"
              aria-label="Accesos personales"
            >
              <button
                type="button"
                @click="irPerfilAcademico"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <circle
                    cx="10"
                    cy="6"
                    r="3"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />

                  <path
                    d="M4 17c.5-3.4 2.6-5.2 6-5.2s5.5 1.8 6 5.2"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>

                <span>Perfil académico</span>
              </button>

              <button
                type="button"
                @click="irMisPublicaciones"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="M5 2.8h7.2L15.5 6v11.2H5V2.8Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linejoin="round"
                  />

                  <path
                    d="M12 3v3.2h3.2M7.7 9h5M7.7 12h5M7.7 15h3.4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.4"
                    stroke-linecap="round"
                  />
                </svg>

                <span>Mis publicaciones</span>
              </button>

              <button
                type="button"
                @click="irMisReportes"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="M3.5 16.5h13M5.2 14V9.8M9.1 14V5.8M13 14V8M16.8 14V3.8"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>

                <span>Mi producción científica</span>
              </button>

              <button
                type="button"
                @click="irPreferencias"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="M10 7.2A2.8 2.8 0 1 0 10 12.8 2.8 2.8 0 0 0 10 7.2Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />

                  <path
                    d="m10 2 .9 1.8 2-.1.6 1.9 1.8.9-.7 1.9 1.3 1.5-1.3 1.5.7 1.9-1.8.9-.6 1.9-2-.1L10 18l-.9-1.8-2 .1-.6-1.9-1.8-.9.7-1.9L4.1 10l1.3-1.5-.7-1.9 1.8-.9.6-1.9 2 .1L10 2Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.2"
                    stroke-linejoin="round"
                  />
                </svg>

                <span>Preferencias</span>
              </button>
            </nav>

            <div class="perfil-sidebar-spacer"></div>

            <nav
              class="perfil-sidebar-account"
              aria-label="Cuenta y administración"
            >
              <button
                v-if="isAdmin"
                type="button"
                @click="irAPanelAdmin"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="M10 2.5 3.5 5.4v4.4c0 3.7 2.7 7.1 6.5 8 3.8-.9 6.5-4.3 6.5-8V5.4L10 2.5Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linejoin="round"
                  />
                </svg>

                <span>Administración</span>
              </button>

              <button
                class="is-danger"
                type="button"
                @click="cerrarSesion"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="M8 3H4.5A1.5 1.5 0 0 0 3 4.5v11A1.5 1.5 0 0 0 4.5 17H8M12.5 6.5 16 10l-3.5 3.5M7 10h9"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>

                <span>Cerrar sesión</span>
              </button>
            </nav>
          </section>
        </aside>

        <div class="perfil-main">
          <section
            v-if="showIncompleteBanner"
            class="perfil-notice"
          >
            <span class="perfil-notice__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path
                  d="M12 3 2.8 19h18.4L12 3Z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linejoin="round"
                />

                <path
                  d="M12 9v4M12 16.5h.01"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>
            </span>

            <div class="perfil-notice__content">
              <h2>Información pendiente</h2>

              <div class="perfil-notice__details">
                <span v-if="missingFields.length">
                  Pendiente:
                  <strong>{{ missingFields.join(", ") }}</strong>
                </span>

                <span v-if="tiempoRestante">
                  Disponible:
                  <strong>
                    {{ tiempoRestante.horas }}h
                    {{ tiempoRestante.minutos }}m
                  </strong>
                </span>
              </div>
            </div>

            <div class="perfil-notice__actions">
              <button
                type="button"
                class="perfil-notice__primary"
                @click="handleEditAction"
              >
                Completar datos
              </button>

              <button
                type="button"
                class="perfil-notice__secondary"
                @click="dismissIncompleteBanner"
              >
                Ocultar
              </button>
            </div>
          </section>

          <section
            class="perfil-card"
            aria-labelledby="account-summary-title"
          >
            <header class="perfil-card__head">
              <div>
                <h2 id="account-summary-title">
                  Cuenta
                </h2>

              </div>
            </header>

            <div class="perfil-summary-grid">
              <article class="perfil-summary-item">
                <span class="perfil-summary-item__icon">
                  <svg viewBox="0 0 20 20" aria-hidden="true">
                    <path
                      d="M10 2.5 3.5 5.4v4.4c0 3.7 2.7 7.1 6.5 8 3.8-.9 6.5-4.3 6.5-8V5.4L10 2.5Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />
                  </svg>
                </span>

                <div>
                  <span class="perfil-summary-item__label">
                    Inicio de sesión
                  </span>

                  <strong>
                    {{
                      user.auth_source === "microsoft"
                        ? "Microsoft 365"
                        : "Correo y contraseña"
                    }}
                  </strong>

                </div>
              </article>

              
              <article class="perfil-summary-item">
                <span class="perfil-summary-item__icon">
                  <svg viewBox="0 0 20 20" aria-hidden="true">
                    <circle
                      cx="10"
                      cy="10"
                      r="7"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />

                    <path
                      d="M10 6v4l2.5 1.5"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                    />
                  </svg>
                </span>

                <div>
                  <span class="perfil-summary-item__label">
                    Edición
                  </span>

                  <strong>
                    <template v-if="tiempoRestante">
                      Disponible por
                      {{ tiempoRestante.horas }}h
                      {{ tiempoRestante.minutos }}m
                    </template>

                    <template v-else>
                      No disponible
                    </template>
                  </strong>

                </div>
              </article>
            </div>

            <div
              v-if="!canEditProfile"
              ref="extensionRequestSectionRef"
              class="perfil-extension-request"
              :class="{
                'is-expanded': extensionRequestExpanded,
                'is-pending': extensionRequestPending,
                'is-rejected': extensionRequestRejected,
              }"
            >
              <div class="perfil-extension-request__summary">
                <span
                  class="perfil-extension-request__icon"
                  aria-hidden="true"
                >
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M4 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.7"
                    />

                    <path
                      d="m5 7 7 5 7-5"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.7"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>

                <div class="perfil-extension-request__content">
                  <h3>
                    {{
                      extensionRequestPending
                        ? "Solicitud pendiente"
                        : extensionRequestRejected
                          ? "Solicitud rechazada"
                          : "Solicitar más tiempo"
                    }}
                  </h3>

                  <p v-if="extensionRequestPending">
                    {{ extensionRequestStatus.horas_solicitadas }} horas solicitadas · Pendiente de revisión.
                  </p>

                  <p v-else-if="extensionRequestRejected">
                    {{
                      extensionRequestStatus?.motivo_resolucion ||
                      "La solicitud no fue aprobada. Puede enviar una nueva solicitud si aún necesita más tiempo."
                    }}
                  </p>

                  <p v-else-if="extensionRequestExpanded">
                    Indique brevemente el motivo.
                  </p>
                </div>

                <button
                  v-if="!extensionRequestPending"
                  class="perfil-extension-request__toggle"
                  type="button"
                  :disabled="sendingExtensionRequest"
                  :aria-expanded="extensionRequestExpanded ? 'true' : 'false'"
                  aria-controls="perfil-extension-form"
                  @click="toggleExtensionRequest"
                >
                  <span>
                    {{
                      extensionRequestExpanded
                        ? "Cerrar"
                        : extensionRequestRejected
                          ? "Solicitar nuevamente"
                          : "Solicitar"
                    }}
                  </span>

                  <svg
                    viewBox="0 0 20 20"
                    aria-hidden="true"
                  >
                    <path
                      d="m6 8 4 4 4-4"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.7"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </button>
              </div>

              <Transition name="perfil-extension-collapse">
                <form
                  v-if="extensionRequestExpanded && !extensionRequestPending"
                  id="perfil-extension-form"
                  class="perfil-extension-request__form"
                  @submit.prevent="requestEditExtension"
                >
                  <label class="perfil-extension-request__field">
                    <span>Tiempo adicional</span>

                    <select
                      v-model.number="extensionRequestHours"
                      :disabled="sendingExtensionRequest"
                    >
                      <option :value="24">24 horas</option>
                      <option :value="48">48 horas</option>
                      <option :value="72">72 horas</option>
                    </select>
                  </label>

                  <label class="perfil-extension-request__field is-wide">
                    <span>Motivo</span>

                    <textarea
                      ref="extensionReasonInputRef"
                      v-model="extensionRequestReason"
                      rows="4"
                      minlength="20"
                      maxlength="1000"
                      :disabled="sendingExtensionRequest"
                      placeholder="Explique brevemente por qué necesita más tiempo para editar su perfil."
                    ></textarea>
                  </label>

                  <div class="perfil-extension-request__footer">
                    <small>
                      {{ extensionRequestReason.trim().length }}/1000 caracteres
                    </small>

                    <div class="perfil-extension-request__footer-actions">

                      <button
                        class="perfil-extension-request__submit"
                        type="submit"
                        :disabled="
                          sendingExtensionRequest ||
                          extensionRequestReason.trim().length < 20
                        "
                      >
                        <span
                          v-if="sendingExtensionRequest"
                          class="perfil-edit-spinner"
                          aria-hidden="true"
                        ></span>

                        <svg
                          v-else
                          viewBox="0 0 20 20"
                          aria-hidden="true"
                        >
                          <path
                            d="M3.5 5.5A1.5 1.5 0 0 1 5 4h10a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 15 16H5a1.5 1.5 0 0 1-1.5-1.5v-9Z"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                          />

                          <path
                            d="m4 6 6 4.5L16 6"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          />
                        </svg>

                        <span>
                          {{
                            sendingExtensionRequest
                              ? "Enviando solicitud..."
                              : "Enviar solicitud"
                          }}
                        </span>
                      </button>
                    </div>
                  </div>
                </form>
              </Transition>
            </div>
          </section>

          <section
            class="perfil-card"
            aria-labelledby="account-data-title"
          >
            <header class="perfil-card__head">
              <div>
                <h2 id="account-data-title">
                  {{ profileDataTitle }}
                </h2>

              </div>

                          </header>

            <dl class="perfil-fields">
              <div class="perfil-field perfil-field--wide">
                <dt>{{ correoLabel }}</dt>

                <dd>
                  <span class="perfil-field__value mono">
                    {{ user.email || "—" }}
                  </span>

                  <button
                    v-if="user.email"
                    class="perfil-copy-button"
                    type="button"
                    aria-label="Copiar correo"
                    title="Copiar correo"
                    @click="copyText(user.email)"
                  >
                    <svg viewBox="0 0 20 20" aria-hidden="true">
                      <rect
                        x="6.5"
                        y="6.5"
                        width="9"
                        height="9"
                        rx="1.5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                      />

                      <path
                        d="M5 13.5H4.5A1.5 1.5 0 0 1 3 12V4.5A1.5 1.5 0 0 1 4.5 3H12a1.5 1.5 0 0 1 1.5 1.5V5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                      />
                    </svg>
                  </button>
                </dd>
              </div>

              <div class="perfil-field">
                <dt>Número de cédula</dt>

                <dd>
                  <span
                    class="perfil-field__value mono"
                    :class="{
                      'is-empty': !user.identificacion,
                    }"
                  >
                    {{ user.identificacion || "Pendiente" }}
                  </span>

                  <button
                    v-if="user.identificacion"
                    class="perfil-copy-button"
                    type="button"
                    aria-label="Copiar número de cédula"
                    title="Copiar número de cédula"
                    @click="copyText(String(user.identificacion))"
                  >
                    <svg viewBox="0 0 20 20" aria-hidden="true">
                      <rect
                        x="6.5"
                        y="6.5"
                        width="9"
                        height="9"
                        rx="1.5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                      />

                      <path
                        d="M5 13.5H4.5A1.5 1.5 0 0 1 3 12V4.5A1.5 1.5 0 0 1 4.5 3H12a1.5 1.5 0 0 1 1.5 1.5V5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                      />
                    </svg>
                  </button>
                </dd>
              </div>

              <div
                v-if="isInstitutionalUser"
                class="perfil-field"
              >
                <dt>Sede</dt>

                <dd>
                  <span
                    class="perfil-field__value"
                    :class="{
                      'is-empty': !sedeLabel,
                    }"
                  >
                    {{ sedeLabel || "Pendiente" }}
                  </span>
                </dd>
              </div>

              <div
                v-if="isInstitutionalUser"
                class="perfil-field"
              >
                <dt>Facultad</dt>

                <dd>
                  <span
                    class="perfil-field__value"
                    :class="{
                      'is-empty': !facultadLabel,
                    }"
                  >
                    {{ facultadLabel || "Pendiente" }}
                  </span>
                </dd>
              </div>

              <div
                v-if="isInstitutionalUser"
                class="perfil-field"
              >
                <dt>Carrera</dt>

                <dd>
                  <span
                    class="perfil-field__value"
                    :class="{
                      'is-empty': !carreraLabel,
                    }"
                  >
                    {{ carreraLabel || "Pendiente" }}
                  </span>
                </dd>
              </div>

              <div class="perfil-field">
                <dt>Fecha de registro</dt>

                <dd>
                  <span class="perfil-field__value">
                    {{
                      user.fecha_registro
                        ? formatFecha(user.fecha_registro)
                        : "No disponible"
                    }}
                  </span>
                </dd>
              </div>

                          </dl>
          </section>
        </div>
      </div>
    </div>

    <section
      v-else
      class="perfil-shell perfil-error-state"
      role="alert"
    >
      <span class="perfil-error-state__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24">
          <circle
            cx="12"
            cy="12"
            r="9"
            fill="none"
            stroke="currentColor"
            stroke-width="1.7"
          />

          <path
            d="M12 7.5V13M12 16.5h.01"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
          />
        </svg>
      </span>

      <div>
        <h1>No se pudo cargar el perfil</h1>

        <p>
          Intente nuevamente en unos momentos.
        </p>

        <button
          type="button"
          @click="reloadProfile"
        >
          Reintentar
        </button>
      </div>
    </section>

    <Teleport to="body">
      <Transition name="perfil-toast">
        <div
          v-if="toast.show"
          class="perfil-toast"
          :class="`is-${toast.type}`"
          role="status"
          aria-live="polite"
        >
          <span class="perfil-toast__indicator" aria-hidden="true"></span>

          <span class="perfil-toast__message">
            {{ toast.message }}
          </span>

          <button
            type="button"
            aria-label="Cerrar notificación"
            @click="hideToast"
          >
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <path
                d="m5 5 10 10M15 5 5 15"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>
      </Transition>
    </Teleport>

    <PerfilAvatarModal
      v-model="showAvatarModal"
      :user="user"
      :initials="initials"
      :has-avatar="hasAvatar"
      :max-file-size="MAX_AVATAR_FILE_SIZE"
      :avatar-max-size-label="avatarMaxSizeLabel"
      @updated="handleAvatarUpdated"
      @toast="showToast"
    />

    <Teleport to="body">
      <Transition name="perfil-modal">
        <div
          v-if="showEditModal"
          class="perfil-modal-overlay"
          @click.self="closeEditModal"
        >
          <section
            ref="editModalRef"
            class="perfil-edit-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="edit-profile-title"
            tabindex="-1"
          >
            <header class="perfil-edit-modal__head">
              <div class="perfil-edit-modal__identity">
                <span class="perfil-edit-modal__icon" aria-hidden="true">
                  <svg viewBox="0 0 20 20">
                    <path
                      d="m12.7 4.2 3.1 3.1M4 16l2.8-.6 8.4-8.4a1.6 1.6 0 0 0 0-2.3 1.6 1.6 0 0 0-2.3 0L4.6 13.2 4 16Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>

                <div>
                  <h2 id="edit-profile-title">
                    Editar perfil
                  </h2>

                </div>
              </div>

              <button
                class="perfil-edit-modal__close"
                type="button"
                :disabled="savingProfile"
                aria-label="Cerrar ventana"
                title="Cerrar"
                @click="closeEditModal"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="m5 5 10 10M15 5 5 15"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                  />
                </svg>
              </button>
            </header>

            <div class="perfil-edit-modal__body">
              <div
                v-if="tiempoRestante"
                class="perfil-edit-time"
              >
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <circle
                    cx="10"
                    cy="10"
                    r="7"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />

                  <path
                    d="M10 6v4l2.5 1.5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>

                <span>
                  Disponible:
                  <strong>
                    {{ tiempoRestante.horas }}h
                    {{ tiempoRestante.minutos }}m
                  </strong>
                </span>
              </div>

              <form
                class="perfil-edit-form"
                @submit.prevent="saveProfile"
              >
                <div
                  v-if="isExternalAuthor"
                  class="perfil-edit-form__grid"
                >
                  <label class="perfil-form-field">
                    <span class="perfil-form-field__label">
                      Nombres
                    </span>

                    <input
                      ref="firstNameInputRef"
                      v-model="form.nombres"
                      type="text"
                      maxlength="100"
                      autocomplete="given-name"
                      placeholder="Ingrese sus nombres"
                      :disabled="!canEditProfile || savingProfile"
                    />

                  </label>

                  <label class="perfil-form-field">
                    <span class="perfil-form-field__label">
                      Apellidos
                    </span>

                    <input
                      v-model="form.apellidos"
                      type="text"
                      maxlength="100"
                      autocomplete="family-name"
                      placeholder="Ingrese sus apellidos"
                      :disabled="!canEditProfile || savingProfile"
                    />

                    <small>
                      Este cambio también se reflejará en sus publicaciones.
                    </small>
                  </label>
                </div>

                <label class="perfil-form-field">
                  <span class="perfil-form-field__label">
                    Número de cédula
                  </span>

                  <input
                    ref="identificationInputRef"
                    v-model.trim="form.identificacion"
                    type="text"
                    maxlength="10"
                    inputmode="numeric"
                    autocomplete="off"
                    placeholder="Ingrese los 10 dígitos de la cédula"
                    :disabled="!canEditProfile || savingProfile"
                    @input="onCedulaInput"
                  />

                </label>

                <template v-if="isInstitutionalUser">
                  <div class="perfil-edit-form__grid">
                    <label class="perfil-form-field">
                      <span class="perfil-form-field__label">
                        Sede
                      </span>

                      <select
                        v-model="form.sede_id"
                        :disabled="!canEditProfile || savingProfile || loadingSedes"
                        @change="onSedeChange"
                      >
                        <option value="">
                          {{ loadingSedes ? "Cargando sedes..." : "Seleccione una sede" }}
                        </option>

                        <option
                          v-for="sede in sedes"
                          :key="sede.id"
                          :value="sede.id"
                        >
                          {{ sede.nombre }}
                        </option>
                      </select>

                    </label>

                    <label class="perfil-form-field">
                      <span class="perfil-form-field__label">
                        Facultad
                      </span>

                      <select
                        v-model="form.facultad_id"
                        :disabled="!canEditProfile || savingProfile || !form.sede_id"
                        @change="onFacultadChange"
                      >
                        <option value="">
                          Seleccione una facultad
                        </option>

                        <option
                          v-for="facultad in facultades"
                          :key="facultad.id"
                          :value="facultad.id"
                        >
                          {{ facultad.nombre }}
                        </option>
                      </select>
                    </label>

                    <label class="perfil-form-field">
                      <span class="perfil-form-field__label">
                        Carrera
                      </span>

                      <select
                        v-model="form.carrera_id"
                        :disabled="
                          !canEditProfile ||
                          savingProfile ||
                          loadingCarreras ||
                          !form.sede_id ||
                          !form.facultad_id
                        "
                      >
                        <option value="">
                          {{
                            loadingCarreras
                              ? "Cargando carreras..."
                              : "Seleccione una carrera"
                          }}
                        </option>

                        <option
                          v-for="carrera in carreras"
                          :key="carrera.id"
                          :value="carrera.id"
                        >
                          {{ carrera.nombre }}
                        </option>
                      </select>

                      <small
                        v-if="
                          form.facultad_id &&
                          !loadingCarreras &&
                          !carreras.length
                        "
                      >
                        No hay carreras disponibles para esta selección.
                      </small>
                    </label>
                  </div>
                </template>

                <p
                  v-if="editError"
                  class="perfil-edit-error"
                  role="alert"
                >
                  <svg viewBox="0 0 20 20" aria-hidden="true">
                    <circle
                      cx="10"
                      cy="10"
                      r="8"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />

                    <path
                      d="M10 5.8v5M10 14.3h.01"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.7"
                      stroke-linecap="round"
                    />
                  </svg>

                  <span>{{ editError }}</span>
                </p>
              </form>
            </div>

            <footer class="perfil-edit-modal__actions">
              <button
                class="perfil-edit-button perfil-edit-button--secondary"
                type="button"
                :disabled="savingProfile"
                @click="closeEditModal"
              >
                Cancelar
              </button>

              <button
                class="perfil-edit-button perfil-edit-button--primary"
                type="button"
                :disabled="!canEditProfile || savingProfile"
                @click="saveProfile"
              >
                <span
                  v-if="savingProfile"
                  class="perfil-edit-spinner"
                  aria-hidden="true"
                ></span>

                <svg
                  v-else
                  viewBox="0 0 20 20"
                  aria-hidden="true"
                >
                  <path
                    d="m5 10 3 3 7-7"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>

                <span>
                  {{ savingProfile ? "Guardando..." : "Guardar cambios" }}
                </span>
              </button>
            </footer>
          </section>
        </div>
      </Transition>
    </Teleport>
  </main>
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

import { useRouter } from "vue-router";

import api from "../../scripts/api/axios";
import { useUserStore } from "../../scripts/stores/userStore";

import PerfilAvatarModal from "./componentes/PerfilAvatarModal.vue";

const router = useRouter();
const userStore = useUserStore();

const MAX_AVATAR_FILE_SIZE =
  1 * 1024 * 1024;

const user = ref(null);
const loading = ref(true);
const now = ref(Date.now());

const showAvatarModal = ref(false);
const showEditModal = ref(false);
const savingProfile = ref(false);
const editError = ref("");

const sendingExtensionRequest = ref(false);
const extensionRequestStatus = ref(null);
const extensionRequestStatusReady = ref(false);
const extensionRequestStatusError = ref("");
const extensionRequestSyncing = ref(false);
const extensionRequestExpanded = ref(false);
const extensionRequestReason = ref("");
const extensionRequestHours = ref(48);

const editModalRef = ref(null);
const firstNameInputRef = ref(null);
const identificationInputRef = ref(null);
const extensionRequestSectionRef = ref(null);
const extensionReasonInputRef = ref(null);

const sedes = ref([]);
const facultades = ref([]);
const carreras = ref([]);
const loadingSedes = ref(false);
const loadingCarreras = ref(false);

const avatarBroken = ref(false);

let clockId = null;
let profileRefreshPromise = null;

const toast = ref({
  show: false,
  type: "info",
  message: "",
  t: null,
});

const form = ref({
  nombres: "",
  apellidos: "",
  identificacion: "",
  sede_id: "",
  facultad_id: "",
  carrera_id: "",
});

const prettyBytes = (bytes) => {
  const size = Number(bytes || 0);

  if (size <= 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];

  let value = size;
  let index = 0;

  while (
    value >= 1024 &&
    index < units.length - 1
  ) {
    value /= 1024;
    index += 1;
  }

  return `${value.toFixed(index === 0 ? 0 : 2)} ${units[index]}`;
};

const avatarMaxSizeLabel =
  prettyBytes(MAX_AVATAR_FILE_SIZE);

const asArray = (data) => {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  return [];
};

const firstFilled = (...values) => {
  return (
    values
      .map((value) =>
        String(value ?? "").trim()
      )
      .find(Boolean) ||
    ""
  );
};

const getUserSedeId = (currentUser) => {
  return (
    currentUser?.sede_id ||
    currentUser?.sede?.id ||
    ""
  );
};

const getUserSedeLabel = (currentUser) => {
  return firstFilled(
    currentUser?.sede_nombre,
    typeof currentUser?.sede === "object"
      ? currentUser.sede?.nombre
      : currentUser?.sede
  );
};

const getUserFacultadId = (currentUser) => {
  return (
    currentUser?.facultad_id ||
    currentUser?.carrera?.facultad_id ||
    currentUser?.carrera?.facultad?.id ||
    ""
  );
};

const getUserCarreraId = (currentUser) => {
  return (
    currentUser?.carrera_id ||
    currentUser?.carrera?.id ||
    ""
  );
};

const getUserFacultadLabel = (currentUser) => {
  return firstFilled(
    currentUser?.carrera?.facultad?.nombre,
    currentUser?.carrera?.facultad_nombre,
    currentUser?.facultad_nombre,
    typeof currentUser?.facultad === "object"
      ? currentUser.facultad?.nombre
      : currentUser?.facultad
  );
};

const getUserCarreraLabel = (currentUser) => {
  return firstFilled(
    currentUser?.carrera?.nombre,
    currentUser?.carrera_nombre,
    typeof currentUser?.carrera === "string"
      ? currentUser.carrera
      : ""
  );
};

const sedeLabel = computed(() => {
  return getUserSedeLabel(user.value);
});

const facultadLabel = computed(() => {
  return getUserFacultadLabel(user.value);
});

const carreraLabel = computed(() => {
  return getUserCarreraLabel(user.value);
});

const correoLabel = computed(() => {
  return isInstitutionalUser.value
    ? "Correo institucional"
    : "Correo electrónico";
});

const initials = computed(() => {
  const nombres = String(
    user.value?.nombres || ""
  ).trim();

  const apellidos = String(
    user.value?.apellidos || ""
  ).trim();

  return (
    `${nombres[0] || ""}${apellidos[0] || ""}`.toUpperCase() ||
    "U"
  );
});

const displayName = computed(() => {
  if (
    user.value?.auth_source === "microsoft" &&
    user.value?.ms_display_name
  ) {
    return user.value.ms_display_name;
  }

  return (
    `${user.value?.nombres || ""} ${user.value?.apellidos || ""}`.trim() ||
    "Usuario"
  );
});

const hasAvatar = computed(() => {
  return Boolean(
    user.value?.avatar_url &&
    !avatarBroken.value
  );
});

const avatarButtonLabel = computed(() => {
  return hasAvatar.value
    ? "Actualizar foto de perfil"
    : "Agregar foto de perfil";
});

const normalizeAccountValue = (value) => {
  return String(value || "")
    .trim()
    .toLowerCase();
};

const hasValidCedula = (value) => {
  return /^\d{10}$/.test(
    String(value || "").trim()
  );
};

const isExternalAuthor = computed(() => {
  const currentUser = user.value;

  if (!currentUser) {
    return false;
  }

  return Boolean(
    currentUser.es_externo === true ||
    (
      normalizeAccountValue(
        currentUser.rol
      ) === "autor_externo" &&
      normalizeAccountValue(
        currentUser.auth_source
      ) === "local"
    )
  );
});

const isInstitutionalUser = computed(() => {
  const currentUser = user.value;

  if (!currentUser) {
    return false;
  }

  return Boolean(
    currentUser.es_institucional === true ||
    (
      normalizeAccountValue(
        currentUser.rol
      ) === "autor" &&
      normalizeAccountValue(
        currentUser.auth_source
      ) === "microsoft"
    )
  );
});

const isAdmin = computed(() => {
  const currentUser = user.value;

  return Boolean(
    currentUser?.is_staff ||
    currentUser?.is_superuser ||
    currentUser?.es_admin ||
    currentUser?.is_admin
  );
});

const accountTypeLabel = computed(() => {
  if (
    String(
      user.value?.tipo_cuenta_label || ""
    ).trim()
  ) {
    return user.value.tipo_cuenta_label;
  }

  if (isExternalAuthor.value) {
    return "Cuenta externa";
  }

  if (isInstitutionalUser.value) {
    return "Cuenta institucional";
  }

  return "Cuenta sin clasificación válida";
});

const accountTypeDescription = computed(() => {
  if (isExternalAuthor.value) {
    return "Usuario externo registrado en el sistema.";
  }

  if (isInstitutionalUser.value) {
    return "Usuario institucional.";
  }

  return "Revise la información de su cuenta.";
});

const profileDataTitle = computed(() => {
  return isInstitutionalUser.value
    ? "Datos institucionales"
    : "Datos de la cuenta";
});

const profilePendingMessage = computed(() => {
  if (isInstitutionalUser.value) {
    return "Existen datos institucionales pendientes.";
  }

  if (isExternalAuthor.value) {
    return "Existen datos de la cuenta pendientes.";
  }

  return "Revise la información pendiente de su cuenta.";
});

const incompleteProfileMessage = computed(() => {
  if (isInstitutionalUser.value) {
    return (
      "Complete los datos requeridos para mantener " +
      "actualizado su perfil institucional."
    );
  }

  if (isExternalAuthor.value) {
    return (
      "Complete el número de cédula requerido para " +
      "mantener actualizada su cuenta."
    );
  }

  return (
    "La clasificación de esta cuenta debe ser revisada " +
    "por un administrador."
  );
});

const roleLabel = computed(() => {
  const backendLabel = String(
    user.value?.rol_label || ""
  ).trim();

  if (backendLabel) {
    return backendLabel;
  }

  if (isExternalAuthor.value) {
    return "Autor externo";
  }

  if (isInstitutionalUser.value) {
    return "Autor institucional";
  }

  return "Usuario sin clasificación válida";
});

const perfilCompletoCalculado = computed(() => {
  const currentUser = user.value;

  if (!currentUser) {
    return false;
  }

  const cedulaCompleta = hasValidCedula(
    currentUser.identificacion
  );

  if (isExternalAuthor.value) {
    return cedulaCompleta;
  }

  if (!isInstitutionalUser.value) {
    return false;
  }

  const sedeCompleta =
    Boolean(
      getUserSedeId(currentUser) ||
      getUserSedeLabel(currentUser)
    );

  const facultadCompleta =
    Boolean(
      getUserFacultadId(currentUser) ||
      getUserFacultadLabel(currentUser)
    );

  const carreraCompleta =
    Boolean(
      getUserCarreraId(currentUser) ||
      getUserCarreraLabel(currentUser)
    );

  return (
    cedulaCompleta &&
    sedeCompleta &&
    facultadCompleta &&
    carreraCompleta
  );
});

const canEditProfile = computed(() => {
  const currentUser = user.value;

  if (!currentUser) {
    return false;
  }

  if (
    currentUser.profile_edit_available === false
  ) {
    return false;
  }

  if (currentUser.profile_edit_locked) {
    return false;
  }

  if (currentUser.profile_edit_until) {
    const limit =
      new Date(
        currentUser.profile_edit_until
      );

    if (!Number.isNaN(limit.getTime())) {
      return now.value <= limit.getTime();
    }
  }

  if (!currentUser.fecha_registro) {
    return true;
  }

  const created =
    new Date(
      currentUser.fecha_registro
    );

  if (Number.isNaN(created.getTime())) {
    return true;
  }

  const elapsedHours =
    (now.value - created.getTime()) /
    (1000 * 60 * 60);

  return elapsedHours <= 48;
});

const tiempoRestante = computed(() => {
  const currentUser = user.value;

  if (!currentUser) {
    return null;
  }

  let limitMilliseconds = null;

  if (currentUser.profile_edit_until) {
    const limit =
      new Date(
        currentUser.profile_edit_until
      ).getTime();

    if (!Number.isNaN(limit)) {
      limitMilliseconds = limit;
    }
  }

  if (!limitMilliseconds) {
    if (!currentUser.fecha_registro) {
      return null;
    }

    const created =
      new Date(
        currentUser.fecha_registro
      ).getTime();

    if (Number.isNaN(created)) {
      return null;
    }

    limitMilliseconds =
      created +
      48 * 60 * 60 * 1000;
  }

  const difference =
    limitMilliseconds -
    now.value;

  if (difference <= 0) {
    return null;
  }

  const horas =
    Math.floor(
      difference /
      (1000 * 60 * 60)
    );

  const minutos =
    Math.floor(
      (
        difference %
        (1000 * 60 * 60)
      ) /
      (1000 * 60)
    );

  return {
    horas,
    minutos,
  };
});

const editDisabledReason = computed(() => {
  if (user.value?.profile_edit_locked) {
    return (
      user.value?.profile_edit_lock_reason ||
      "La edición del perfil está bloqueada."
    );
  }

  return "El periodo de edición finalizó. Solicite los cambios al administrador.";
});

const showIncompleteBanner = computed(() => {
  const currentUser = user.value;

  if (!currentUser) {
    return false;
  }

  if (perfilCompletoCalculado.value) {
    return false;
  }

  if (
    currentUser.perfil_banner_snooze_until
  ) {
    const limit =
      new Date(
        currentUser.perfil_banner_snooze_until
      );

    if (
      !Number.isNaN(limit.getTime()) &&
      now.value < limit.getTime()
    ) {
      return false;
    }
  }

  return canEditProfile.value;
});

const missingFields = computed(() => {
  const currentUser = user.value;

  if (!currentUser) {
    return [];
  }

  const missing = [];

  if (
    !hasValidCedula(
      currentUser.identificacion
    )
  ) {
    missing.push("Número de cédula");
  }

  if (isInstitutionalUser.value) {
    if (
      !getUserSedeId(currentUser) &&
      !getUserSedeLabel(currentUser)
    ) {
      missing.push("Sede");
    }

    if (
      !getUserFacultadId(currentUser) &&
      !getUserFacultadLabel(currentUser)
    ) {
      missing.push("Facultad");
    }

    if (
      !getUserCarreraId(currentUser) &&
      !getUserCarreraLabel(currentUser)
    ) {
      missing.push("Carrera");
    }
  } else if (!isExternalAuthor.value) {
    missing.push("Clasificación de cuenta");
  }

  return missing;
});

const profileCompletion = computed(() => {
  const currentUser = user.value;

  if (!currentUser) {
    return 0;
  }

  const cedulaCompleta = hasValidCedula(
    currentUser.identificacion
  );

  if (isExternalAuthor.value) {
    return cedulaCompleta
      ? 100
      : 0;
  }

  if (!isInstitutionalUser.value) {
    return 0;
  }

  let completed = 0;

  if (cedulaCompleta) {
    completed += 1;
  }

  if (
    getUserSedeId(currentUser) ||
    getUserSedeLabel(currentUser)
  ) {
    completed += 1;
  }

  if (
    getUserFacultadId(currentUser) ||
    getUserFacultadLabel(currentUser)
  ) {
    completed += 1;
  }

  if (
    getUserCarreraId(currentUser) ||
    getUserCarreraLabel(currentUser)
  ) {
    completed += 1;
  }

  return Math.round(
    (completed / 4) * 100
  );
});

const authSourceNote = computed(() => {
  if (
    user.value?.auth_source === "microsoft"
  ) {
    return "Ingrese con su cuenta institucional de Microsoft 365.";
  }

  return "Ingrese con su correo y contraseña registrados.";
});

const safeReadStoredUser = () => {
  try {
    const raw =
      localStorage.getItem("user");

    return raw
      ? JSON.parse(raw)
      : null;
  } catch {
    return null;
  }
};

const syncUserState = (data) => {
  if (!data) {
    user.value = null;
    return;
  }

  const mergedUser = {
    ...(user.value || {}),
    ...data,
  };

  user.value = mergedUser;

  localStorage.setItem(
    "user",
    JSON.stringify(mergedUser)
  );

  userStore.setUserData?.(mergedUser);
  userStore.setAvatar?.(
    mergedUser.avatar_url || null
  );
};

const resetEditForm = () => {
  form.value = {
    nombres:
      isExternalAuthor.value
        ? String(user.value?.nombres || "")
        : "",

    apellidos:
      isExternalAuthor.value
        ? String(user.value?.apellidos || "")
        : "",

    identificacion:
      user.value?.identificacion || "",

    sede_id:
      isInstitutionalUser.value
        ? getUserSedeId(user.value)
        : "",

    facultad_id:
      isInstitutionalUser.value
        ? getUserFacultadId(user.value)
        : "",

    carrera_id:
      isInstitutionalUser.value
        ? getUserCarreraId(user.value)
        : "",
  };
};

const onCedulaInput = (event) => {
  const digits = String(
    event?.target?.value || ""
  )
    .replace(/\D/g, "")
    .slice(0, 10);

  form.value.identificacion = digits;

  if (
    event?.target &&
    event.target.value !== digits
  ) {
    event.target.value = digits;
  }
};

const showToast = (
  type,
  message,
  milliseconds = 2800
) => {
  if (toast.value.t) {
    clearTimeout(toast.value.t);
  }

  toast.value.type = type;
  toast.value.message = message;
  toast.value.show = true;

  toast.value.t =
    setTimeout(() => {
      toast.value.show = false;
      toast.value.t = null;
    }, milliseconds);
};

const hideToast = () => {
  if (toast.value.t) {
    clearTimeout(toast.value.t);
  }

  toast.value.show = false;
  toast.value.t = null;
};

const copyText = async (text) => {
  const value = String(text ?? "");

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(
        value
      );
    } else {
      const textarea =
        document.createElement("textarea");

      textarea.value = value;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";

      document.body.appendChild(textarea);
      textarea.select();

      document.execCommand("copy");
      textarea.remove();
    }

    showToast(
      "success",
      "Información copiada."
    );
  } catch (error) {
    console.error(error);

    showToast(
      "error",
      "No se pudo copiar la información."
    );
  }
};

const formatFecha = (dateValue) => {
  if (!dateValue) {
    return "No disponible";
  }

  const date =
    new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "No disponible";
  }

  return date.toLocaleDateString(
    "es-EC",
    {
      day: "2-digit",
      month: "long",
      year: "numeric",
    }
  );
};

const formatFechaTime = (dateValue) => {
  if (!dateValue) {
    return "No disponible";
  }

  const date =
    new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "No disponible";
  }

  return date.toLocaleString(
    "es-EC",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  );
};

const cerrarSesion = async () => {
  try {
    await userStore.logout?.();
  } catch {
    // Se continúa con la limpieza local.
  }

  userStore.clearUser?.();

  localStorage.removeItem(
    "access_token"
  );

  localStorage.removeItem(
    "refresh_token"
  );

  localStorage.removeItem("user");

  await router.replace("/login");
};

const irPerfilAcademico = () => {
  router.push("/perfil-academico/me");
};

const irMisPublicaciones = () => {
  router.push("/mis-publicaciones");
};

const irMisReportes = () => {
  router.push("/mis-reportes");
};

const irPreferencias = () => {
  router.push("/preferencias");
};

const irAPanelAdmin = () => {
  router.push("/admin/panel");
};

const openAvatarFlow = () => {
  showAvatarModal.value = true;
};

const handleAvatarUpdated = (nextUser) => {
  avatarBroken.value = false;
  syncUserState(nextUser);
};

const closeEditModal = () => {
  if (savingProfile.value) {
    return;
  }

  showEditModal.value = false;
  editError.value = "";
};

const extensionRequestPending = computed(
  () =>
    extensionRequestStatus.value?.estado ===
    "pendiente"
);

const extensionRequestRejected = computed(
  () =>
    extensionRequestStatus.value?.estado ===
    "rechazada"
);

const loadExtensionRequestStatus = async (
  { silent = false } = {}
) => {
  try {
    const response = await api.get(
      "auth/profile/solicitar-extension/"
    );

    extensionRequestStatus.value =
      response?.data?.solicitud || null;

    extensionRequestStatusReady.value = true;
    extensionRequestStatusError.value = "";

    return true;
  } catch (error) {
    console.warn(
      "No se pudo consultar el estado de la solicitud de extensión.",
      error
    );

    extensionRequestStatusReady.value = false;
    extensionRequestStatusError.value =
      resolveApiErrorMessage(
        error,
        "No pudimos verificar el estado de su solicitud. Intente nuevamente."
      );

    if (!silent) {
      showToast(
        "error",
        extensionRequestStatusError.value,
        5200
      );
    }

    return false;
  }
};

const technicalErrorPattern = /\b(api|backend|endpoint|serializer|queryset|jwt|token|sql|postgres(?:ql)?|database|constraint|traceback|exception|integrityerror|typeerror|valueerror|http\s*\d{3}|request|response)\b/i;

const safeUserMessage = (value, fallback) => {
  const message = String(value || "").trim();

  if (!message || technicalErrorPattern.test(message)) {
    return fallback;
  }

  return message;
};

const resolveApiErrorMessage = (error, fallback) => {
  const data = error?.response?.data;

  if (typeof data?.detail === "string") {
    return safeUserMessage(data.detail, fallback);
  }

  const motivo = Array.isArray(data?.motivo)
    ? data.motivo[0]
    : data?.motivo;

  return safeUserMessage(motivo, fallback);
};

const openExtensionRequest = async () => {
  if (extensionRequestPending.value) {
    return;
  }

  if (
    !extensionRequestStatusReady.value ||
    extensionRequestStatusError.value
  ) {
    const loaded =
      await loadExtensionRequestStatus({
        silent: true,
      });

    if (!loaded) {
      showToast(
        "error",
        extensionRequestStatusError.value ||
          "No pudimos verificar si ya existe una solicitud pendiente.",
        5200
      );
      return;
    }

    if (extensionRequestPending.value) {
      return;
    }
  }

  extensionRequestExpanded.value = true;

  await nextTick();

  extensionRequestSectionRef.value?.scrollIntoView?.({
    behavior: "smooth",
    block: "center",
  });

  window.setTimeout(() => {
    extensionReasonInputRef.value?.focus?.({
      preventScroll: true,
    });
  }, 240);
};

const closeExtensionRequest = () => {
  if (sendingExtensionRequest.value) {
    return;
  }

  extensionRequestExpanded.value = false;
};

const toggleExtensionRequest = async () => {
  if (extensionRequestExpanded.value) {
    closeExtensionRequest();
    return;
  }

  await openExtensionRequest();
};

const focusExtensionRequest = async () => {
  await openExtensionRequest();
};

const requestEditExtension = async () => {
  if (
    !extensionRequestStatusReady.value ||
    extensionRequestStatusError.value
  ) {
    const loaded =
      await loadExtensionRequestStatus({
        silent: true,
      });

    if (!loaded) {
      showToast(
        "error",
        extensionRequestStatusError.value ||
          "No pudimos verificar si ya existe una solicitud pendiente.",
        5200
      );
      return;
    }
  }

  if (extensionRequestPending.value) {
    showToast(
      "info",
      "Ya tiene una solicitud pendiente de revisión administrativa.",
      4200
    );
    return;
  }

  if (sendingExtensionRequest.value) {
    return;
  }

  const motivo = String(
    extensionRequestReason.value || ""
  ).trim();

  if (motivo.length < 20) {
    showToast(
      "error",
      "El motivo debe contener al menos 20 caracteres.",
      4200
    );

    await focusExtensionRequest();
    return;
  }

  sendingExtensionRequest.value = true;

  try {
    const response = await api.post(
      "auth/profile/solicitar-extension/",
      {
        motivo,
        horas_solicitadas:
          Number(extensionRequestHours.value) || 48,
      }
    );

    extensionRequestStatus.value =
      response?.data?.solicitud || null;
    extensionRequestStatusReady.value = true;
    extensionRequestStatusError.value = "";
    extensionRequestReason.value = "";
    extensionRequestExpanded.value = false;

    showToast(
      "success",
      response?.data?.detail ||
        "La solicitud fue enviada correctamente.",
      5200
    );
  } catch (error) {
    console.error(error);

    if (error?.response?.data?.solicitud) {
      extensionRequestStatus.value =
        error.response.data.solicitud;
      extensionRequestStatusReady.value = true;
      extensionRequestStatusError.value = "";
      extensionRequestExpanded.value = false;
    }

    showToast(
      "error",
      resolveApiErrorMessage(
        error,
        "No pudimos enviar la solicitud. Intente nuevamente."
      ),
      5200
    );
  } finally {
    sendingExtensionRequest.value = false;
  }
};

const handleEditAction = async () => {
  if (!canEditProfile.value) {
    await focusExtensionRequest();
    return;
  }

  await openEditProfileModal();
};

const loadSedes = async () => {
  if (!isInstitutionalUser.value) {
    sedes.value = [];
    return;
  }

  loadingSedes.value = true;

  try {
    const response =
      await api.get(
        "selects/sedes/"
      );

    sedes.value =
      asArray(response.data);
  } finally {
    loadingSedes.value = false;
  }
};

const loadFacultades = async () => {
  if (!isInstitutionalUser.value) {
    facultades.value = [];
    return;
  }

  const response =
    await api.get(
      "selects/facultades/"
    );

  facultades.value =
    asArray(response.data);
};

const loadCarreras = async (
  facultadId,
  sedeId = form.value.sede_id
) => {
  if (!facultadId || !sedeId) {
    carreras.value = [];
    return;
  }

  loadingCarreras.value = true;

  try {
    const response =
      await api.get(
        "selects/carreras/",
        {
          params: {
            sede_id: sedeId,
            facultad_id: facultadId,
          },
        }
      );

    carreras.value =
      asArray(response.data);
  } finally {
    loadingCarreras.value = false;
  }
};

const onSedeChange = async () => {
  form.value.facultad_id = "";
  form.value.carrera_id = "";
  carreras.value = [];
};

const onFacultadChange = async () => {
  form.value.carrera_id = "";

  await loadCarreras(
    form.value.facultad_id,
    form.value.sede_id
  );
};

const openEditProfileModal = async () => {
  editError.value = "";
  resetEditForm();

  showEditModal.value = true;

  await nextTick();

  const initialField =
    isExternalAuthor.value
      ? firstNameInputRef.value
      : identificationInputRef.value;

  initialField?.focus?.({
    preventScroll: true,
  });

  if (
    !canEditProfile.value ||
    !isInstitutionalUser.value
  ) {
    sedes.value = [];
    facultades.value = [];
    carreras.value = [];
    return;
  }

  try {
    await Promise.all([
      loadSedes(),
      loadFacultades(),
    ]);

    if (form.value.sede_id && form.value.facultad_id) {
      await loadCarreras(
        form.value.facultad_id,
        form.value.sede_id
      );

      const exists =
        carreras.value.some(
          (career) =>
            String(career.id) ===
            String(form.value.carrera_id)
        );

      if (!exists) {
        form.value.carrera_id = "";
      }
    } else {
      carreras.value = [];
      form.value.carrera_id = "";
    }
  } catch (error) {
    console.error(error);

    editError.value =
      "No se pudieron cargar las sedes, facultades y carreras.";
  }
};

const resolveProfileError = (
  data,
  fallback
) => {
  if (!data) {
    return fallback;
  }

  if (typeof data.detail === "string") {
    return safeUserMessage(data.detail, fallback);
  }

  if (typeof data.error === "string") {
    return safeUserMessage(data.error, fallback);
  }

  const keys = [
    "nombres",
    "apellidos",
    "identificacion",
    "sede_set",
    "sede",
    "facultad_set",
    "carrera_set",
    "carrera",
    "non_field_errors",
  ];

  for (const key of keys) {
    const value = data[key];

    if (
      Array.isArray(value) &&
      value[0]
    ) {
      return safeUserMessage(value[0], fallback);
    }

    if (
      typeof value === "string" &&
      value
    ) {
      return safeUserMessage(value, fallback);
    }
  }

  return fallback;
};

const normalizeNullableId = (value) => {
  if (
    value === "" ||
    value === null ||
    value === undefined
  ) {
    return null;
  }

  const parsed = Number(value);

  return (
    Number.isFinite(parsed) &&
    parsed > 0
  )
    ? parsed
    : null;
};

const saveProfile = async () => {
  if (savingProfile.value) {
    return;
  }

  if (!canEditProfile.value) {
    editError.value =
      editDisabledReason.value;

    showToast(
      "error",
      editError.value
    );

    return;
  }

  const normalizePersonName = (value) => {
    return String(value || "")
      .trim()
      .replace(/\s+/g, " ");
  };

  const nombres = normalizePersonName(
    form.value.nombres
  );

  const apellidos = normalizePersonName(
    form.value.apellidos
  );

  if (isExternalAuthor.value) {
    if (!nombres) {
      editError.value =
        "Los nombres son obligatorios.";

      firstNameInputRef.value?.focus?.();
      return;
    }

    if (!apellidos) {
      editError.value =
        "Los apellidos son obligatorios.";
      return;
    }

    if (
      nombres.length > 100 ||
      apellidos.length > 100
    ) {
      editError.value =
        "Los nombres y apellidos no pueden superar los 100 caracteres.";
      return;
    }
  }

  const cedula =
    String(
      form.value.identificacion || ""
    ).trim();

  if (
    !hasValidCedula(cedula)
  ) {
    editError.value =
      "La cédula debe contener exactamente 10 dígitos numéricos.";

    return;
  }

  let sedeId = null;
  let facultadId = null;
  let carreraId = null;

  if (isInstitutionalUser.value) {
    sedeId =
      normalizeNullableId(
        form.value.sede_id
      );

    facultadId =
      normalizeNullableId(
        form.value.facultad_id
      );

    carreraId =
      normalizeNullableId(
        form.value.carrera_id
      );

    if (
      !sedeId ||
      !facultadId ||
      !carreraId
    ) {
      editError.value =
        "Seleccione la sede, la facultad y la carrera correspondientes.";

      return;
    }
  }

  savingProfile.value = true;
  editError.value = "";

  try {
    const payload = {
      identificacion: cedula,
    };

    if (isExternalAuthor.value) {
      payload.nombres = nombres;
      payload.apellidos = apellidos;
    }

    if (isInstitutionalUser.value) {
      payload.sede_set =
        sedeId;

      payload.facultad_set =
        facultadId;

      payload.carrera_set =
        carreraId;
    }

    const response =
      await api.patch(
        "auth/profile/",
        payload
      );

    syncUserState(response.data);

    showToast(
      "success",
      isExternalAuthor.value
        ? "Sus datos personales se actualizaron correctamente."
        : "El perfil se actualizó correctamente."
    );

    showEditModal.value = false;
  } catch (error) {
    console.error(error);

    const status =
      error?.response?.status;

    const data =
      error?.response?.data || {};

    if (status === 403) {
      editError.value =
        resolveProfileError(
          data,
          "La edición del perfil está bloqueada."
        );
    } else if (
      status === 400 ||
      status === 409
    ) {
      editError.value =
        resolveProfileError(
          data,
          isInstitutionalUser.value
            ? "Revise la cédula, facultad y carrera."
            : "Revise el número de cédula."
        );
    } else {
      editError.value =
        "No se pudo actualizar el perfil.";
    }

    showToast(
      "error",
      editError.value
    );
  } finally {
    savingProfile.value = false;
  }
};

const dismissIncompleteBanner = async () => {
  try {
    await api.patch(
      "auth/profile/",
      {
        snooze_hours: 5,
      }
    );

    await reloadProfile();

    showToast(
      "info",
      "El recordatorio volverá a mostrarse más tarde."
    );
  } catch (error) {
    console.error(error);

    showToast(
      "error",
      "No se pudo posponer el recordatorio."
    );
  }
};

const reloadProfile = async (
  { silent = false } = {}
) => {
  if (!silent) {
    loading.value = true;
  }

  try {
    const response =
      await api.get(
        "auth/profile/"
      );

    syncUserState(response.data);
    avatarBroken.value = false;

    return true;
  } catch (error) {
    console.error(error);

    if (!silent) {
      const cached =
        safeReadStoredUser();

      if (cached) {
        syncUserState(cached);
      } else {
        user.value = null;
      }
    }

    return false;
  } finally {
    if (!silent) {
      loading.value = false;
    }
  }
};

const refreshProfileExtensionState = async (
  { silent = true } = {}
) => {
  if (extensionRequestSyncing.value) {
    return profileRefreshPromise;
  }

  extensionRequestSyncing.value = true;

  profileRefreshPromise = Promise.all([
    reloadProfile({ silent }),
    loadExtensionRequestStatus({ silent: true }),
  ])
    .then(([profileLoaded, requestLoaded]) => {
      now.value = Date.now();

      return Boolean(
        profileLoaded &&
        requestLoaded
      );
    })
    .finally(() => {
      extensionRequestSyncing.value = false;
      profileRefreshPromise = null;
    });

  return profileRefreshPromise;
};

const handleWindowFocus = () => {
  refreshProfileExtensionState({
    silent: true,
  });
};

const handleVisibilityChange = () => {
  if (
    document.visibilityState ===
    "visible"
  ) {
    refreshProfileExtensionState({
      silent: true,
    });
  }
};

const onKeyDown = (event) => {
  if (event.key !== "Escape") {
    return;
  }

  if (showEditModal.value) {
    closeEditModal();
    return;
  }

  if (extensionRequestExpanded.value) {
    closeExtensionRequest();
  }
};

watch(
  showEditModal,
  async (isOpen) => {
    if (typeof document === "undefined") {
      return;
    }

    document.documentElement.classList.toggle(
      "perfil-modal-lock",
      isOpen
    );

    document.body.classList.toggle(
      "perfil-modal-lock",
      isOpen
    );

    if (isOpen) {
      await nextTick();

      editModalRef.value?.focus?.({
        preventScroll: true,
      });
    }
  }
);

watch(
  () => user.value?.avatar_url,
  () => {
    avatarBroken.value = false;
  }
);

onMounted(async () => {
  window.addEventListener(
    "keydown",
    onKeyDown
  );

  window.addEventListener(
    "focus",
    handleWindowFocus
  );

  document.addEventListener(
    "visibilitychange",
    handleVisibilityChange
  );

  clockId = window.setInterval(
    () => {
      now.value = Date.now();
    },
    60000
  );

  const token =
    localStorage.getItem(
      "access_token"
    );

  if (!token) {
    loading.value = false;

    await router.replace("/login");
    return;
  }

  const cached =
    safeReadStoredUser();

  if (cached) {
    syncUserState(cached);
  }

  const [, requestLoaded] =
    await Promise.all([
      reloadProfile(),
      loadExtensionRequestStatus({
        silent: true,
      }),
    ]);

  if (!requestLoaded) {
    showToast(
      "error",
      extensionRequestStatusError.value ||
        "No pudimos verificar el estado de su solicitud de extensión.",
      5200
    );
  }
});

onBeforeUnmount(() => {
  window.removeEventListener(
    "keydown",
    onKeyDown
  );

  window.removeEventListener(
    "focus",
    handleWindowFocus
  );

  document.removeEventListener(
    "visibilitychange",
    handleVisibilityChange
  );

  document.documentElement.classList.remove(
    "perfil-modal-lock"
  );

  document.body.classList.remove(
    "perfil-modal-lock"
  );

  if (clockId) {
    clearInterval(clockId);
    clockId = null;
  }

  if (toast.value.t) {
    clearTimeout(toast.value.t);
  }
});
</script>

<style src="./perfil-usuario.css"></style>
