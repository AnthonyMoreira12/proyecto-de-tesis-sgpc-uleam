<template>
  <div class="avn-content">
    <section
      class="avn-stage-card"
      :class="{
        'is-manage-open': manageModeActive,
        'is-banner-mode': isBannerOnly,
        'is-text-mode': isTextOnly,
      }"
      :style="stageCardStyle"
    >
      <button
        class="avn-close"
        type="button"
        aria-label="Cerrar avisos institucionales"
        title="Cerrar"
        @click="handleContinue"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
          <path
            fill="currentColor"
            d="M6.7 5.3 12 10.6l5.3-5.3 1.4 1.4-5.3 5.3 5.3 5.3-1.4 1.4-5.3-5.3-5.3 5.3-1.4-1.4 5.3-5.3-5.3-5.3 1.4-1.4Z"
          />
        </svg>
      </button>

      <section
        v-if="loading || !heroReady"
        class="avn-stage-card__loading"
        aria-busy="true"
        aria-label="Cargando avisos institucionales"
      >
        <div class="avn-skeleton avn-skeleton--media"></div>

        <div class="avn-skeleton avn-skeleton--content">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </section>

      <template v-else-if="showCarousel">
        <div
          class="avn-stage-main"
          :class="{
            'avn-stage-main--mixed': isMixedMode,
            'avn-stage-main--banner': isBannerOnly,
            'avn-stage-main--text': isTextOnly,
          }"
          :style="stageGridStyle"
          tabindex="0"
          role="region"
          aria-roledescription="carrusel"
          :aria-label="`Avisos institucionales. Aviso ${currentBanner + 1} de ${bannersNormalized.length}`"
          @mouseenter="pauseCarousel"
          @mouseleave="resumeCarousel"
          @keydown="onCarouselKeydown"
        >
          <p class="sr-only" aria-live="polite">
            Aviso {{ currentBanner + 1 }} de {{ bannersNormalized.length }}.
          </p>

          <section v-if="!isTextOnly" class="avn-stage__media">
            <div class="avn-slides">
              <article
                v-for="(banner, index) in bannersNormalized"
                :key="banner.id"
                class="avn-slide"
                :class="{ 'is-active': index === currentBanner }"
                :aria-hidden="index !== currentBanner"
              >
                <img
                  :src="banner.image_url"
                  :alt="`Imagen del aviso institucional ${index + 1}`"
                  class="avn-slide__img"
                  :loading="index === currentBanner ? 'eager' : 'lazy'"
                  :fetchpriority="index === currentBanner ? 'high' : 'low'"
                  :decoding="index === currentBanner ? 'sync' : 'async'"
                />
              </article>
            </div>

            <div class="avn-media__shade" aria-hidden="true"></div>

            <span class="avn-media__brand">
              SGPC ULEAM
            </span>
          </section>

          <section v-if="!isBannerOnly" class="avn-stage__aside">
            <div class="avn-stage__copy">
              <div class="avn-stage__eyebrow-row">
                <span class="avn-stage__eyebrow">
                  {{ panelDisplayContent.eyebrow }}
                </span>

                <span
                  v-if="panelDisplayContent.recentLabel"
                  class="avn-stage__badge"
                >
                  {{ panelDisplayContent.recentLabel }}
                </span>
              </div>

              <h2 class="avn-stage__title">
                {{ panelDisplayContent.title }}
              </h2>

              <p class="avn-stage__text">
                {{ panelDisplayContent.text }}
              </p>

              <div class="avn-stage__meta">
                <span class="avn-chip">
                  Comunicado institucional
                </span>

                <span
                  v-if="manageModeActive"
                  class="avn-chip avn-chip--accent"
                >
                  {{ displayModeLabel }}
                </span>
              </div>
            </div>
          </section>
        </div>

        <footer class="avn-stage-footer">
          <div class="avn-carousel-controls">
            <template v-if="bannersNormalized.length > 1">
              <button
                class="avn-pager-btn"
                type="button"
                aria-label="Aviso anterior"
                @click="prev"
              >
                <svg
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  aria-hidden="true"
                >
                  <path
                    fill="currentColor"
                    d="m15.4 5.4-1.4-1.4L6 12l8 8 1.4-1.4L8.8 12l6.6-6.6Z"
                  />
                </svg>

                <span>Anterior</span>
              </button>

              <div
                class="avn-dots"
                aria-label="Seleccionar aviso"
              >
                <button
                  v-for="(banner, index) in bannersNormalized"
                  :key="banner.id"
                  class="avn-dot"
                  :class="{ 'is-active': index === currentBanner }"
                  type="button"
                  :aria-label="`Ir al aviso ${index + 1}`"
                  :aria-current="index === currentBanner ? 'true' : 'false'"
                  @click="goTo(index)"
                ></button>
              </div>

              <button
                class="avn-pager-btn"
                type="button"
                aria-label="Siguiente aviso"
                @click="next"
              >
                <span>Siguiente</span>

                <svg
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  aria-hidden="true"
                >
                  <path
                    fill="currentColor"
                    d="m8.6 18.6 1.4 1.4 8-8-8-8-1.4 1.4 6.6 6.6-6.6 6.6Z"
                  />
                </svg>
              </button>
            </template>

            <span v-else class="avn-carousel-counter">
              Aviso institucional
            </span>
          </div>

          <div class="avn-stage-actions">
            <button
              v-if="showAdminPanel"
              class="avn-btn avn-btn--secondary"
              type="button"
              @click="toggleGestion"
            >
              {{ panelAbierto ? "Cerrar edición" : "Administrar avisos" }}
            </button>

            <button
              class="avn-btn avn-btn--primary"
              type="button"
              data-autofocus="true"
              @click="handleContinue"
            >
              Entendido
            </button>
          </div>
        </footer>
      </template>

      <section v-else class="avn-empty">
        <div class="avn-empty__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="30" height="30">
            <path
              fill="currentColor"
              d="M4 4h16v13H7l-3 3V4Zm2 2v9.2L6.2 15H18V6H6Zm2 2h8v2H8V8Zm0 4h6v2H8v-2Z"
            />
          </svg>
        </div>

        <p class="avn-empty__kicker">
          SGPC ULEAM
        </p>

        <h2 class="avn-empty__title">
          {{
            isAdmin
              ? "No hay avisos publicados"
              : "No hay avisos disponibles"
          }}
        </h2>

        <p class="avn-empty__text">
          {{
            isAdmin
              ? "Publica el primer comunicado institucional para mostrarlo a los usuarios."
              : "En este momento no existen comunicados institucionales activos."
          }}
        </p>

        <div class="avn-empty__actions">
          <button
            v-if="isAdmin"
            class="avn-btn avn-btn--secondary"
            type="button"
            @click="openPublishTab"
          >
            Publicar aviso
          </button>

          <button
            class="avn-btn avn-btn--primary"
            type="button"
            @click="handleContinue"
          >
            Entendido
          </button>
        </div>
      </section>
    </section>

    <section
      v-if="showAdminPanel && panelAbierto"
      class="avn-admin-shell"
      :style="stageShellStyle"
      aria-labelledby="avn-admin-title"
    >
      <div class="avn-admin">
        <header class="avn-admin__header">
          <div>
            <p class="avn-admin__eyebrow">
              Herramientas administrativas
            </p>

            <h3 id="avn-admin-title" class="avn-admin__title">
              Administración de avisos
            </h3>

            <p class="avn-admin__subtitle">
              Gestiona los comunicados sin alterar la estructura general del
              inicio.
            </p>
          </div>

          <div class="avn-admin__summary">
            <span class="avn-admin-chip">
              {{ bannersNormalized.length }}
              publicado<span v-if="bannersNormalized.length !== 1">s</span>
            </span>

            <span
              v-if="pendingChangeCount"
              class="avn-admin-chip avn-admin-chip--accent"
            >
              {{ pendingChangeCount }}
              cambio<span v-if="pendingChangeCount !== 1">s</span>
              pendiente<span v-if="pendingChangeCount !== 1">s</span>
            </span>
          </div>
        </header>

        <nav
          class="avn-admin-tabs"
          role="tablist"
          aria-label="Secciones de administración"
        >
          <button
            v-for="tab in adminTabs"
            :id="`avn-tab-${tab.value}`"
            :key="tab.value"
            class="avn-admin-tab"
            :class="{ 'is-active': activeAdminTab === tab.value }"
            type="button"
            role="tab"
            :aria-selected="
              activeAdminTab === tab.value
                ? 'true'
                : 'false'
            "
            :aria-controls="`avn-panel-${tab.value}`"
            @click="activeAdminTab = tab.value"
          >
            <span>{{ tab.label }}</span>

            <span
              v-if="tab.value === 'published'"
              class="avn-admin-tab__count"
            >
              {{ bannersNormalized.length }}
            </span>
          </button>
        </nav>

        <p
          v-if="editorStatus"
          class="avn-alert avn-alert--success"
          role="status"
          aria-live="polite"
        >
          {{ editorStatus }}
        </p>

        <p
          v-if="panelError || loadError"
          class="avn-alert avn-alert--error"
          role="alert"
        >
          {{ panelError || loadError }}
        </p>

        <section
          v-show="activeAdminTab === 'published'"
          id="avn-panel-published"
          class="avn-admin-panel"
          role="tabpanel"
          aria-labelledby="avn-tab-published"
        >
          <div class="avn-panel-heading">
            <div>
              <h4>Avisos publicados</h4>

              <p>
                Selecciona un aviso para visualizarlo, editarlo o eliminarlo.
              </p>
            </div>

            <button
              class="avn-btn avn-btn--primary"
              type="button"
              @click="activeAdminTab = 'publish'"
            >
              Nuevo aviso
            </button>
          </div>

          <div
            v-if="bannersNormalized.length"
            class="avn-bulk-bar"
          >
            <label
              class="avn-check-label"
              for="avn-select-all"
            >
              <input
                id="avn-select-all"
                type="checkbox"
                :checked="allSelected"
                :disabled="uploading || deletingBulk"
                @change="toggleSelectAll"
              />

              <span>Seleccionar todos</span>
            </label>

            <div class="avn-bulk-bar__actions">
              <span>
                {{ selectedBannerIds.length }}
                seleccionado<span v-if="selectedBannerIds.length !== 1">s</span>
              </span>

              <button
                v-if="selectedBannerIds.length"
                class="avn-btn avn-btn--danger"
                type="button"
                :disabled="deletingBulk"
                @click="eliminarSeleccionados"
              >
                {{
                  deletingBulk
                    ? bulkDeleteLabel
                    : "Eliminar seleccionados"
                }}
              </button>
            </div>
          </div>

          <div
            v-if="bannersNormalized.length"
            class="avn-published-grid"
          >
            <article
              v-for="(banner, index) in bannersNormalized"
              :key="banner.id"
              class="avn-published-item"
              :class="{
                'is-active': index === currentBanner,
                'is-selected': isSelected(banner.id),
              }"
            >
              <div class="avn-published-item__media">
                <button
                  class="avn-published-item__preview"
                  type="button"
                  :aria-label="`Visualizar aviso ${index + 1}`"
                  @click="selectBanner(index)"
                >
                  <img
                    :src="banner.image_url"
                    :alt="`Aviso publicado ${index + 1}`"
                    loading="lazy"
                  />
                </button>

                <label
                  class="avn-published-item__check"
                  :for="`avn-select-${banner.id}`"
                >
                  <input
                    :id="`avn-select-${banner.id}`"
                    type="checkbox"
                    :checked="isSelected(banner.id)"
                    :disabled="
                      deletingBulk ||
                      deletingId === banner.id
                    "
                    @change="toggleBannerSelection(banner.id)"
                  />

                  <span class="sr-only">
                    Seleccionar aviso {{ index + 1 }}
                  </span>
                </label>

                <span
                  v-if="index === currentBanner"
                  class="avn-published-item__active"
                >
                  Activo
                </span>
              </div>

              <div class="avn-published-item__body">
                <div>
                  <strong>
                    Aviso {{ index + 1 }}
                  </strong>

                  <span>
                    {{ resolveBannerContent(banner).title }}
                  </span>
                </div>

                <div class="avn-published-item__actions">
                  <button
                    class="avn-icon-btn"
                    type="button"
                    aria-label="Editar contenido del aviso"
                    title="Editar contenido"
                    @click="editBanner(index)"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      width="18"
                      height="18"
                      aria-hidden="true"
                    >
                      <path
                        fill="currentColor"
                        d="m4 15.5 9.9-9.9 4.5 4.5-9.9 9.9H4v-4.5Zm11.3-11.3 1.4-1.4a2 2 0 0 1 2.8 0l1.7 1.7a2 2 0 0 1 0 2.8l-1.4 1.4-4.5-4.5Z"
                      />
                    </svg>
                  </button>

                  <button
                    class="avn-icon-btn avn-icon-btn--danger"
                    type="button"
                    :disabled="
                      deletingId === banner.id ||
                      deletingBulk
                    "
                    aria-label="Eliminar aviso"
                    title="Eliminar"
                    @click="eliminarBanner(banner.id)"
                  >
                    <svg
                      viewBox="0 0 24 24"
                      width="18"
                      height="18"
                      aria-hidden="true"
                    >
                      <path
                        fill="currentColor"
                        d="M9 3h6l1 2h4v2H4V5h4l1-2Zm-2 6h10l-1 11H8L7 9Zm3 2v7h2v-7h-2Zm4 0v7h2v-7h-2Z"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </article>
          </div>

          <div v-else class="avn-panel-empty">
            <p>No existen avisos publicados.</p>

            <button
              class="avn-btn avn-btn--primary"
              type="button"
              @click="activeAdminTab = 'publish'"
            >
              Publicar el primero
            </button>
          </div>
        </section>

        <section
          v-show="activeAdminTab === 'content'"
          id="avn-panel-content"
          class="avn-admin-panel"
          role="tabpanel"
          aria-labelledby="avn-tab-content"
        >
          <div class="avn-panel-heading">
            <div>
              <h4>Contenido del aviso activo</h4>

              <p>
                Edita el texto asociado al aviso que se muestra en la vista
                previa.
              </p>
            </div>

            <span
              v-if="showCarousel"
              class="avn-panel-heading__status"
            >
              Aviso {{ currentBanner + 1 }} de
              {{ bannersNormalized.length }}
            </span>
          </div>

          <form
            v-if="showCarousel"
            class="avn-form-grid"
            @submit.prevent="saveActiveBannerContent"
          >
            <label
              class="avn-field avn-field--half"
              for="avn-content-eyebrow"
            >
              <span>Etiqueta superior</span>

              <input
                id="avn-content-eyebrow"
                v-model="activeBannerContentDraft.eyebrow"
                type="text"
                maxlength="60"
                autocomplete="off"
              />

              <small>
                Ejemplo: Comunicado institucional.
              </small>
            </label>

            <label
              class="avn-field avn-field--half"
              for="avn-content-recent"
            >
              <span>Etiqueta de actualización</span>

              <input
                id="avn-content-recent"
                v-model="activeBannerContentDraft.recentLabel"
                type="text"
                maxlength="60"
                autocomplete="off"
              />

              <small>
                Ejemplo: Nuevo o Actualizado.
              </small>
            </label>

            <label
              class="avn-field"
              for="avn-content-title"
            >
              <span>Título</span>

              <textarea
                id="avn-content-title"
                v-model="activeBannerContentDraft.title"
                rows="3"
                maxlength="220"
              ></textarea>
            </label>

            <label
              class="avn-field"
              for="avn-content-text"
            >
              <span>Mensaje</span>

              <textarea
                id="avn-content-text"
                v-model="activeBannerContentDraft.text"
                rows="6"
                maxlength="700"
              ></textarea>
            </label>

            <div class="avn-form-actions">
              <button
                class="avn-btn avn-btn--ghost"
                type="button"
                :disabled="
                  !hasActiveBannerContentChanges ||
                  savingBannerContent
                "
                @click="cancelActiveBannerContent"
              >
                Descartar cambios
              </button>

              <button
                class="avn-btn avn-btn--secondary"
                type="button"
                :disabled="savingBannerContent"
                @click="resetActiveBannerContent"
              >
                Usar texto global
              </button>

              <button
                class="avn-btn avn-btn--primary"
                type="submit"
                :disabled="
                  !hasActiveBannerContentChanges ||
                  savingBannerContent
                "
              >
                {{
                  savingBannerContent
                    ? "Guardando…"
                    : "Guardar contenido"
                }}
              </button>
            </div>
          </form>

          <div v-else class="avn-panel-empty">
            <p>
              Publica un aviso para habilitar la edición de contenido.
            </p>

            <button
              class="avn-btn avn-btn--primary"
              type="button"
              @click="activeAdminTab = 'publish'"
            >
              Ir a publicar
            </button>
          </div>
        </section>

        <section
          v-show="activeAdminTab === 'design'"
          id="avn-panel-design"
          class="avn-admin-panel"
          role="tabpanel"
          aria-labelledby="avn-tab-design"
        >
          <div class="avn-panel-heading">
            <div>
              <h4>Diseño y presentación</h4>

              <p>
                Utiliza configuraciones predeterminadas para mantener una
                composición consistente.
              </p>
            </div>
          </div>

          <div class="avn-design-sections">
            <fieldset class="avn-option-group">
              <legend>Modo de visualización</legend>

              <p>
                Define qué contenido se muestra en el aviso.
              </p>

              <div class="avn-choice-grid avn-choice-grid--three">
                <button
                  v-for="option in displayModeOptions"
                  :key="option.value"
                  class="avn-choice-card"
                  :class="{
                    'is-active': displayMode === option.value,
                  }"
                  type="button"
                  :aria-pressed="
                    displayMode === option.value
                      ? 'true'
                      : 'false'
                  "
                  @click="setDisplayMode(option.value)"
                >
                  <strong>{{ option.label }}</strong>
                  <span>{{ option.description }}</span>
                </button>
              </div>
            </fieldset>

            <fieldset class="avn-option-group">
              <legend>Tamaño del aviso</legend>

              <p>
                Evita redimensionamientos libres y conserva proporciones
                institucionales.
              </p>

              <div class="avn-choice-grid avn-choice-grid--three">
                <button
                  v-for="option in sizePresets"
                  :key="option.value"
                  class="avn-choice-card"
                  :class="{
                    'is-active': activeSizePreset === option.value,
                  }"
                  type="button"
                  :aria-pressed="
                    activeSizePreset === option.value
                      ? 'true'
                      : 'false'
                  "
                  @click="applySizePreset(option.value)"
                >
                  <strong>{{ option.label }}</strong>
                  <span>{{ option.description }}</span>
                </button>
              </div>
            </fieldset>

            <fieldset
              class="avn-option-group"
              :disabled="!isMixedMode"
            >
              <legend>Distribución</legend>

              <p>
                Determina la proporción entre la imagen y el texto.
              </p>

              <div class="avn-choice-grid avn-choice-grid--three">
                <button
                  v-for="option in distributionPresets"
                  :key="option.value"
                  class="avn-choice-card"
                  :class="{
                    'is-active':
                      activeDistributionPreset === option.value,
                  }"
                  type="button"
                  :disabled="!isMixedMode"
                  :aria-pressed="
                    activeDistributionPreset === option.value
                      ? 'true'
                      : 'false'
                  "
                  @click="applyDistributionPreset(option.value)"
                >
                  <strong>{{ option.label }}</strong>
                  <span>{{ option.description }}</span>
                </button>
              </div>
            </fieldset>
          </div>

          <div class="avn-form-actions avn-form-actions--design">
            <span
              v-if="isLayoutDirty"
              class="avn-unsaved-indicator"
            >
              Hay cambios de diseño sin guardar.
            </span>

            <button
              class="avn-btn avn-btn--primary"
              type="button"
              :disabled="savingLayout || !isLayoutDirty"
              @click="saveCurrentLayout"
            >
              {{
                savingLayout
                  ? "Guardando…"
                  : "Guardar diseño"
              }}
            </button>
          </div>
        </section>

        <section
          v-show="activeAdminTab === 'publish'"
          id="avn-panel-publish"
          class="avn-admin-panel"
          role="tabpanel"
          aria-labelledby="avn-tab-publish"
        >
          <div class="avn-panel-heading">
            <div>
              <h4>Publicar nuevos avisos</h4>

              <p>
                Agrega imágenes JPG o PNG al carrusel institucional.
              </p>
            </div>
          </div>

          <div
            class="avn-dropzone"
            :class="{ 'is-dragging': dragging }"
            role="button"
            tabindex="0"
            aria-label="Seleccionar imágenes para publicar"
            @click="openPicker"
            @keydown.enter.prevent="openPicker"
            @keydown.space.prevent="openPicker"
            @dragover.prevent="onDragOver"
            @dragenter.prevent="onDragEnter"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
          >
            <div class="avn-dropzone__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="28" height="28">
                <path
                  fill="currentColor"
                  d="M11 16V8.8L8.4 11.4 7 10l5-5 5 5-1.4 1.4L13 8.8V16h-2ZM5 19v-4h2v2h10v-2h2v4H5Z"
                />
              </svg>
            </div>

            <strong>
              Arrastra las imágenes aquí
            </strong>

            <span>
              o haz clic para buscarlas en tu equipo
            </span>

            <small>
              JPG o PNG · máximo {{ bannerMaxSizeLabel }} por imagen
            </small>
          </div>

          <div
            v-if="previews.length"
            class="avn-preview-grid"
          >
            <article
              v-for="(preview, index) in previews"
              :key="`${preview}-${index}`"
              class="avn-upload-preview"
            >
              <img
                :src="preview"
                :alt="`Vista previa de la imagen ${index + 1}`"
              />

              <div class="avn-upload-preview__meta">
                <span>
                  {{
                    files[index]?.name ||
                    `Imagen ${index + 1}`
                  }}
                </span>

                <small>
                  {{ prettyBytes(files[index]?.size || 0) }}
                </small>
              </div>

              <button
                class="avn-icon-btn avn-icon-btn--danger"
                type="button"
                aria-label="Quitar imagen"
                :disabled="uploading"
                @click="removeFileAt(index)"
              >
                <svg
                  viewBox="0 0 24 24"
                  width="17"
                  height="17"
                  aria-hidden="true"
                >
                  <path
                    fill="currentColor"
                    d="M6.7 5.3 12 10.6l5.3-5.3 1.4 1.4-5.3 5.3 5.3 5.3-1.4 1.4-5.3-5.3-5.3 5.3-1.4-1.4 5.3-5.3-5.3-5.3 1.4-1.4Z"
                  />
                </svg>
              </button>
            </article>
          </div>

          <div class="avn-form-actions">
            <button
              class="avn-btn avn-btn--secondary"
              type="button"
              :disabled="uploading || deletingBulk"
              @click="openPicker"
            >
              Seleccionar imágenes
            </button>

            <button
              class="avn-btn avn-btn--primary"
              type="button"
              :disabled="
                !files.length ||
                uploading ||
                deletingBulk
              "
              @click="subirBanners"
            >
              {{
                uploading
                  ? uploadLabel
                  : "Publicar avisos"
              }}
            </button>
          </div>
        </section>
      </div>
    </section>

    <div
      v-if="dialogData.visible"
      class="avn-confirm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="avn-confirm-title"
      @keydown.stop="onConfirmKeydown"
    >
      <button
        class="avn-confirm__backdrop"
        type="button"
        tabindex="-1"
        aria-label="Cancelar eliminación"
        @click="cerrarDialogo(false)"
      ></button>

      <section
        ref="modalCard"
        class="avn-confirm__card"
        tabindex="-1"
      >
        <div class="avn-confirm__icon" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            width="22"
            height="22"
          >
            <path
              fill="currentColor"
              d="M12 2a10 10 0 1 0 .001 20.001A10 10 0 0 0 12 2Zm1 15h-2v-2h2v2Zm0-4h-2V7h2v6Z"
            />
          </svg>
        </div>

        <div class="avn-confirm__content">
          <h2 id="avn-confirm-title">
            {{ dialogData.titulo }}
          </h2>

          <p>
            {{ dialogData.mensaje }}
          </p>

          <small>
            Esta acción no se puede deshacer.
          </small>
        </div>

        <img
          v-if="dialogData.bannerImg"
          :src="dialogData.bannerImg"
          alt="Vista previa del aviso que se eliminará"
          class="avn-confirm__preview"
        />

        <div class="avn-confirm__actions">
          <button
            class="avn-btn avn-btn--secondary"
            type="button"
            @click="cerrarDialogo(false)"
          >
            Cancelar
          </button>

          <button
            class="avn-btn avn-btn--danger"
            type="button"
            @click="cerrarDialogo(true)"
          >
            Eliminar
          </button>
        </div>
      </section>
    </div>

    <input
      id="avn-file-input"
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png"
      multiple
      class="sr-only"
      @change="onFileChange"
    />
  </div>
</template>

<script setup>
import {
  computed,
  nextTick,
  onMounted,
  onUnmounted,
  ref,
  watch,
} from "vue";

import api from "../../scripts/api/axios";

import {
  DEFAULT_AVISOS_CONTENT,
  getAvisosCombinedVersion,
  getAvisosContent,
  getAvisosLayout,
  getAvisosStatus,
  hydrateAvisosConfig,
  saveAvisosLayout,
} from "../../scripts/utils/avisosGate";

const props = defineProps({
  user: {
    type: Object,
    default: null,
  },

  version: {
    type: String,
    default: "",
  },

  initialManage: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "continue",
  "version-change",
]);

const ALLOWED_IMAGE_TYPES = new Set([
  "image/jpeg",
  "image/png",
]);

const MAX_BANNER_FILE_SIZE =
  2 * 1024 * 1024;

const CAROUSEL_CYCLE_MS = 5200;
const TEMPORARY_PAUSE_MS = 4000;
const COMPACT_BREAKPOINT = 920;

const FOCUSABLE_SELECTOR = [
  "button:not([disabled])",
  "[href]",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

const DISPLAY_MODE_DEFAULT = "mixed";

const DISPLAY_MODE_VALUES = new Set([
  "mixed",
  "banner",
  "text",
]);

const SIZE_PRESETS = Object.freeze({
  compact: Object.freeze({
    width: 840,
    height: 440,
  }),

  standard: Object.freeze({
    width: 1000,
    height: 520,
  }),

  wide: Object.freeze({
    width: 1120,
    height: 580,
  }),
});

const DISTRIBUTION_PRESETS = Object.freeze({
  image: 0.68,
  balanced: 0.58,
  text: 0.44,
});

const STAGE_WIDTH_MIN = 760;
const STAGE_WIDTH_MAX = 1120;

const STAGE_HEIGHT_MIN = 420;
const STAGE_HEIGHT_MAX = 580;

const ASIDE_WIDTH_MIN = 300;
const MEDIA_WIDTH_MIN = 320;

const adminTabs = [
  {
    value: "published",
    label: "Publicados",
  },
  {
    value: "content",
    label: "Contenido",
  },
  {
    value: "design",
    label: "Diseño",
  },
  {
    value: "publish",
    label: "Publicar",
  },
];

const displayModeOptions = [
  {
    value: "mixed",
    label: "Banner + texto",
    description:
      "Presenta la imagen y el contenido informativo.",
  },
  {
    value: "banner",
    label: "Solo banner",
    description:
      "Utiliza toda el área para la imagen.",
  },
  {
    value: "text",
    label: "Solo texto",
    description:
      "Prioriza el contenido escrito del aviso.",
  },
];

const sizePresets = [
  {
    value: "compact",
    label: "Compacto",
    description:
      "Adecuado para mensajes breves.",
  },
  {
    value: "standard",
    label: "Estándar",
    description:
      "Equilibrio recomendado para uso general.",
  },
  {
    value: "wide",
    label: "Amplio",
    description:
      "Mayor espacio para imágenes y textos extensos.",
  },
];

const distributionPresets = [
  {
    value: "image",
    label: "Imagen predominante",
    description:
      "Asigna más espacio visual al banner.",
  },
  {
    value: "balanced",
    label: "Equilibrado",
    description:
      "Distribuye de forma uniforme imagen y texto.",
  },
  {
    value: "text",
    label: "Texto predominante",
    description:
      "Reserva mayor amplitud para el comunicado.",
  },
];

const prettyBytes = (bytes) => {
  const size = Number(bytes || 0);

  if (size <= 0) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  let value = size;
  let index = 0;

  while (
    value >= 1024 &&
    index < units.length - 1
  ) {
    value /= 1024;
    index += 1;
  }

  return `${value.toFixed(
    index === 0 ? 0 : 2
  )} ${units[index]}`;
};

const bannerMaxSizeLabel =
  prettyBytes(MAX_BANNER_FILE_SIZE);

const clamp = (value, min, max) => {
  return Math.min(
    max,
    Math.max(min, value)
  );
};

const safeNumber = (value, fallback) => {
  const parsed = Number(value);

  return Number.isFinite(parsed)
    ? parsed
    : fallback;
};

const sanitizeDisplayMode = (value) => {
  const normalized = String(value || "")
    .trim()
    .toLowerCase();

  return DISPLAY_MODE_VALUES.has(normalized)
    ? normalized
    : DISPLAY_MODE_DEFAULT;
};

const cloneContent = (value) => {
  return {
    ...DEFAULT_AVISOS_CONTENT,
    ...(value || {}),
  };
};

const normalizeContent = (value) => {
  const next = cloneContent(value);

  return {
    eyebrow:
      String(next.eyebrow || "").trim() ||
      DEFAULT_AVISOS_CONTENT.eyebrow,

    title:
      String(next.title || "").trim() ||
      DEFAULT_AVISOS_CONTENT.title,

    text:
      String(next.text || "").trim() ||
      DEFAULT_AVISOS_CONTENT.text,

    recentLabel:
      String(next.recentLabel || "").trim() ||
      DEFAULT_AVISOS_CONTENT.recentLabel,
  };
};

const getRawBannerContent = (banner) => {
  return {
    eyebrow: String(
      banner?.eyebrow || ""
    ).trim(),

    title: String(
      banner?.title || ""
    ).trim(),

    text: String(
      banner?.text || ""
    ).trim(),

    recentLabel: String(
      banner?.recentLabel || ""
    ).trim(),
  };
};

const sanitizeStageWidth = (value) => {
  return Math.round(
    clamp(
      safeNumber(
        value,
        SIZE_PRESETS.standard.width
      ),
      STAGE_WIDTH_MIN,
      STAGE_WIDTH_MAX
    )
  );
};

const sanitizeStageHeight = (value) => {
  return Math.round(
    clamp(
      safeNumber(
        value,
        SIZE_PRESETS.standard.height
      ),
      STAGE_HEIGHT_MIN,
      STAGE_HEIGHT_MAX
    )
  );
};

const getMediaWidthMax = (width) => {
  return Math.max(
    MEDIA_WIDTH_MIN,
    width - ASIDE_WIDTH_MIN
  );
};

const sanitizeMediaWidth = (
  value,
  width
) => {
  return Math.round(
    clamp(
      safeNumber(
        value,
        width *
          DISTRIBUTION_PRESETS.balanced
      ),
      MEDIA_WIDTH_MIN,
      getMediaWidthMax(width)
    )
  );
};

const banners = ref([]);
const currentBanner = ref(0);
const usuario = ref(props.user || null);

const loading = ref(true);
const heroReady = ref(false);

const panelAbierto = ref(false);
const activeAdminTab = ref("published");

const paused = ref(false);
const isCompactScreen = ref(false);

const uploading = ref(false);
const deletingId = ref(null);
const deletingBulk = ref(false);

const bulkDeleteProgress = ref(0);
const bulkDeleteTotal = ref(0);

const savingLayout = ref(false);
const savingBannerContent = ref(false);

const uploadIndex = ref(0);
const uploadTotal = ref(0);

const files = ref([]);
const previews = ref([]);

const fileInput = ref(null);

const dragging = ref(false);
const dragDepth = ref(0);

const selectedBannerIds = ref([]);

const loadError = ref("");
const panelError = ref("");
const editorStatus = ref("");

const dialogData = ref({
  visible: false,
  titulo: "",
  mensaje: "",
  bannerImg: "",
  count: 0,
  resolve: null,
});

const modalCard = ref(null);

const layoutLoaded = ref(false);

const stageWidth = ref(
  SIZE_PRESETS.standard.width
);

const stageHeight = ref(
  SIZE_PRESETS.standard.height
);

const mediaPaneWidth = ref(
  Math.round(
    SIZE_PRESETS.standard.width *
      DISTRIBUTION_PRESETS.balanced
  )
);

const displayMode = ref(
  DISPLAY_MODE_DEFAULT
);

const persistedStageWidth = ref(
  stageWidth.value
);

const persistedStageHeight = ref(
  stageHeight.value
);

const persistedMediaPaneWidth = ref(
  mediaPaneWidth.value
);

const persistedDisplayMode = ref(
  displayMode.value
);

const refreshingFromVersion = ref(false);
const pendingRemoteVersionSync = ref(false);

const contentSaved = ref(
  cloneContent(getAvisosContent())
);

const activeBannerContentSaved = ref(
  cloneContent(DEFAULT_AVISOS_CONTENT)
);

const activeBannerContentDraft = ref(
  cloneContent(DEFAULT_AVISOS_CONTENT)
);

let carouselTimer = null;
let pauseTimeout = null;
let panelErrorTimeout = null;
let editorStatusTimeout = null;
let lastFocusedElement = null;

const preloadedSources = new Set();

const isAdmin = computed(() => {
  return Boolean(
    usuario.value?.is_staff ||
      usuario.value?.is_superuser ||
      usuario.value?.es_admin ||
      usuario.value?.is_admin
  );
});

const bannersNormalized = computed(() => {
  return (
    Array.isArray(banners.value)
      ? banners.value
      : []
  ).filter((banner) => {
    return Boolean(banner?.image_url);
  });
});

const activeBannerItem = computed(() => {
  return (
    bannersNormalized.value[
      currentBanner.value
    ] || null
  );
});

const resolveBannerContent = (banner) => {
  const raw =
    getRawBannerContent(banner);

  return {
    eyebrow:
      raw.eyebrow ||
      contentSaved.value.eyebrow,

    title:
      raw.title ||
      contentSaved.value.title,

    text:
      raw.text ||
      contentSaved.value.text,

    recentLabel:
      raw.recentLabel ||
      contentSaved.value.recentLabel,
  };
};

const hasBanners = computed(() => {
  return bannersNormalized.value.length > 0;
});

const showCarousel = computed(() => {
  return (
    !loading.value &&
    heroReady.value &&
    hasBanners.value
  );
});

const showAdminPanel = computed(() => {
  return isAdmin.value;
});

const manageModeActive = computed(() => {
  return (
    showAdminPanel.value &&
    panelAbierto.value
  );
});

const isMixedMode = computed(() => {
  return displayMode.value === "mixed";
});

const isBannerOnly = computed(() => {
  return displayMode.value === "banner";
});

const isTextOnly = computed(() => {
  return displayMode.value === "text";
});

const displayModeLabel = computed(() => {
  if (isBannerOnly.value) {
    return "Solo banner";
  }

  if (isTextOnly.value) {
    return "Solo texto";
  }

  return "Banner + texto";
});

const panelDisplayContent = computed(() => {
  if (!activeBannerItem.value) {
    return contentSaved.value;
  }

  return resolveBannerContent(
    activeBannerItem.value
  );
});

const hasActiveBannerContentChanges =
  computed(() => {
    return (
      JSON.stringify(
        normalizeContent(
          activeBannerContentDraft.value
        )
      ) !==
      JSON.stringify(
        normalizeContent(
          activeBannerContentSaved.value
        )
      )
    );
  });

const isLayoutDirty = computed(() => {
  return (
    stageWidth.value !==
      persistedStageWidth.value ||
    stageHeight.value !==
      persistedStageHeight.value ||
    mediaPaneWidth.value !==
      persistedMediaPaneWidth.value ||
    displayMode.value !==
      persistedDisplayMode.value
  );
});

const activeSizePreset = computed(() => {
  const entries =
    Object.entries(SIZE_PRESETS);

  return entries.reduce(
    (best, [key, preset]) => {
      const distance =
        Math.abs(
          stageWidth.value -
            preset.width
        ) +
        Math.abs(
          stageHeight.value -
            preset.height
        );

      return distance < best.distance
        ? {
            key,
            distance,
          }
        : best;
    },
    {
      key: "standard",
      distance:
        Number.POSITIVE_INFINITY,
    }
  ).key;
});

const activeDistributionPreset =
  computed(() => {
    const ratio = stageWidth.value
      ? mediaPaneWidth.value /
        stageWidth.value
      : DISTRIBUTION_PRESETS.balanced;

    return Object.entries(
      DISTRIBUTION_PRESETS
    ).reduce(
      (
        best,
        [key, presetRatio]
      ) => {
        const distance = Math.abs(
          ratio - presetRatio
        );

        return distance < best.distance
          ? {
              key,
              distance,
            }
          : best;
      },
      {
        key: "balanced",
        distance:
          Number.POSITIVE_INFINITY,
      }
    ).key;
  });

const pendingChangeCount = computed(() => {
  let count = 0;

  if (
    hasActiveBannerContentChanges.value
  ) {
    count += 1;
  }

  if (files.value.length) {
    count += 1;
  }

  if (isLayoutDirty.value) {
    count += 1;
  }

  return count;
});

const uploadLabel = computed(() => {
  const current = Math.min(
    uploadIndex.value,
    uploadTotal.value
  );

  return `Publicando… ${current} de ${uploadTotal.value}`;
});

const bulkDeleteLabel = computed(() => {
  const current = Math.min(
    bulkDeleteProgress.value,
    bulkDeleteTotal.value
  );

  return `Eliminando… ${current} de ${bulkDeleteTotal.value}`;
});

const allSelected = computed(() => {
  return (
    bannersNormalized.value.length > 0 &&
    selectedBannerIds.value.length ===
      bannersNormalized.value.length
  );
});

const stageShellStyle = computed(() => {
  if (isCompactScreen.value) {
    return {};
  }

  return {
    width: `${stageWidth.value}px`,
    maxWidth:
      "calc(100vw - 24px)",
  };
});

const stageCardStyle = computed(() => {
  if (isCompactScreen.value) {
    return {};
  }

  return {
    width: `${stageWidth.value}px`,
    height: `${stageHeight.value}px`,
    maxWidth:
      "calc(100vw - 24px)",
  };
});

const stageGridStyle = computed(() => {
  if (
    isCompactScreen.value ||
    !isMixedMode.value
  ) {
    return {};
  }

  return {
    gridTemplateColumns:
      `${mediaPaneWidth.value}px minmax(0, 1fr)`,
  };
});

const updateCompactScreen = () => {
  if (typeof window === "undefined") {
    return;
  }

  isCompactScreen.value =
    window.innerWidth <=
    COMPACT_BREAKPOINT;
};

const setDisplayMode = (mode) => {
  displayMode.value =
    sanitizeDisplayMode(mode);
};

const applySizePreset = (
  presetName
) => {
  const preset =
    SIZE_PRESETS[presetName];

  if (!preset) {
    return;
  }

  const ratio =
    DISTRIBUTION_PRESETS[
      activeDistributionPreset.value
    ] ||
    DISTRIBUTION_PRESETS.balanced;

  stageWidth.value =
    sanitizeStageWidth(preset.width);

  stageHeight.value =
    sanitizeStageHeight(
      preset.height
    );

  mediaPaneWidth.value =
    sanitizeMediaWidth(
      stageWidth.value * ratio,
      stageWidth.value
    );
};

const applyDistributionPreset = (
  presetName
) => {
  const ratio =
    DISTRIBUTION_PRESETS[
      presetName
    ];

  if (!ratio) {
    return;
  }

  mediaPaneWidth.value =
    sanitizeMediaWidth(
      stageWidth.value * ratio,
      stageWidth.value
    );
};

const setEditorStatus = (
  message,
  duration = 2800
) => {
  editorStatus.value = message;

  window.clearTimeout(
    editorStatusTimeout
  );

  if (message) {
    editorStatusTimeout =
      window.setTimeout(() => {
        editorStatus.value = "";
      }, duration);
  }
};

const clearPanelError = () => {
  window.clearTimeout(
    panelErrorTimeout
  );

  panelError.value = "";
};

const setPanelError = (
  message,
  duration = 4800
) => {
  panelError.value = message;

  window.clearTimeout(
    panelErrorTimeout
  );

  if (message) {
    panelErrorTimeout =
      window.setTimeout(() => {
        panelError.value = "";
      }, duration);
  }
};

const requestVersionSync = async ({
  force = false,
} = {}) => {
  if (
    manageModeActive.value &&
    !force
  ) {
    pendingRemoteVersionSync.value =
      true;

    return;
  }

  const status =
    await getAvisosStatus().catch(
      () => null
    );

  const nextVersion =
    status?.notifyVersion ||
    status?.version ||
    getAvisosCombinedVersion(
      props.version
    );

  emit(
    "version-change",
    nextVersion
  );

  pendingRemoteVersionSync.value =
    false;
};

const syncPersistedLayout = () => {
  persistedStageWidth.value =
    stageWidth.value;

  persistedStageHeight.value =
    stageHeight.value;

  persistedMediaPaneWidth.value =
    mediaPaneWidth.value;

  persistedDisplayMode.value =
    displayMode.value;
};

const applyRemoteConfig = (
  config = {}
) => {
  contentSaved.value = cloneContent({
    eyebrow: config?.eyebrow,
    title: config?.title,
    text: config?.text,
    recentLabel:
      config?.recentLabel,
  });

  const width =
    sanitizeStageWidth(
      config?.stageWidth
    );

  const height =
    sanitizeStageHeight(
      config?.stageHeight
    );

  const sourceWidth =
    safeNumber(
      config?.stageWidth,
      width
    );

  const sourceMedia =
    safeNumber(
      config?.mediaPaneWidth,
      sourceWidth *
        DISTRIBUTION_PRESETS.balanced
    );

  const ratio = sourceWidth
    ? sourceMedia / sourceWidth
    : DISTRIBUTION_PRESETS.balanced;

  stageWidth.value = width;
  stageHeight.value = height;

  mediaPaneWidth.value =
    sanitizeMediaWidth(
      width * ratio,
      width
    );

  displayMode.value =
    sanitizeDisplayMode(
      config?.displayMode
    );

  syncPersistedLayout();

  layoutLoaded.value = true;
};

const loadRemoteConfig = async () => {
  try {
    const config =
      await hydrateAvisosConfig();

    applyRemoteConfig(config);
  } catch (error) {
    console.error(error);

    applyRemoteConfig({
      ...getAvisosContent(),
      ...getAvisosLayout(),
    });
  }
};

const syncActiveBannerEditor = () => {
  const resolved =
    activeBannerItem.value
      ? resolveBannerContent(
          activeBannerItem.value
        )
      : contentSaved.value;

  activeBannerContentSaved.value =
    cloneContent(resolved);

  activeBannerContentDraft.value =
    cloneContent(resolved);
};

const updateBannerInList = (
  savedBanner
) => {
  banners.value =
    banners.value.map((item) => {
      return item.id === savedBanner.id
        ? {
            ...item,
            ...savedBanner,
          }
        : item;
    });

  syncActiveBannerEditor();
};

const refreshRemoteStateFromVersion =
  async () => {
    if (
      refreshingFromVersion.value ||
      manageModeActive.value
    ) {
      return;
    }

    refreshingFromVersion.value =
      true;

    try {
      await Promise.allSettled([
        loadRemoteConfig(),
        cargarBanners(),
      ]);

      syncActiveBannerEditor();
    } finally {
      refreshingFromVersion.value =
        false;
    }
  };

const persistRemoteLayout = async ({
  showFeedback = false,
} = {}) => {
  if (
    !isAdmin.value ||
    !layoutLoaded.value ||
    savingLayout.value
  ) {
    return false;
  }

  savingLayout.value = true;

  clearPanelError();

  try {
    const saved =
      await saveAvisosLayout({
        stageWidth:
          stageWidth.value,

        stageHeight:
          stageHeight.value,

        mediaPaneWidth:
          mediaPaneWidth.value,

        displayMode:
          displayMode.value,
      });

    applyRemoteConfig({
      ...contentSaved.value,
      ...saved,

      displayMode:
        saved?.displayMode ??
        displayMode.value,
    });

    await requestVersionSync();

    if (showFeedback) {
      setEditorStatus(
        "Diseño guardado correctamente."
      );
    }

    return true;
  } catch (error) {
    console.error(error);

    setPanelError(
      "No fue posible guardar el diseño del aviso."
    );

    return false;
  } finally {
    savingLayout.value = false;
  }
};

const saveCurrentLayout = () => {
  return persistRemoteLayout({
    showFeedback: true,
  });
};

const saveActiveBannerContent =
  async () => {
    if (
      !isAdmin.value ||
      !activeBannerItem.value ||
      savingBannerContent.value
    ) {
      return;
    }

    savingBannerContent.value =
      true;

    clearPanelError();

    try {
      const payload =
        normalizeContent(
          activeBannerContentDraft.value
        );

      const { data } =
        await api.patch(
          `banners/${activeBannerItem.value.id}/`,
          payload
        );

      updateBannerInList(data);

      setEditorStatus(
        "Contenido del aviso guardado."
      );

      await requestVersionSync();
    } catch (error) {
      console.error(error);

      setPanelError(
        "No fue posible guardar el contenido del aviso activo."
      );
    } finally {
      savingBannerContent.value =
        false;
    }
  };

const cancelActiveBannerContent =
  () => {
    activeBannerContentDraft.value =
      cloneContent(
        activeBannerContentSaved.value
      );
  };

const resetActiveBannerContent =
  async () => {
    if (
      !isAdmin.value ||
      !activeBannerItem.value ||
      savingBannerContent.value
    ) {
      return;
    }

    savingBannerContent.value =
      true;

    clearPanelError();

    try {
      const { data } =
        await api.patch(
          `banners/${activeBannerItem.value.id}/`,
          {
            eyebrow: "",
            title: "",
            text: "",
            recentLabel: "",
          }
        );

      updateBannerInList(data);

      setEditorStatus(
        "El aviso volvió a utilizar el contenido global."
      );

      await requestVersionSync();
    } catch (error) {
      console.error(error);

      setPanelError(
        "No fue posible restablecer el contenido del aviso."
      );
    } finally {
      savingBannerContent.value =
        false;
    }
  };

const toggleGestion = async () => {
  panelAbierto.value =
    !panelAbierto.value;

  if (panelAbierto.value) {
    activeAdminTab.value =
      hasBanners.value
        ? "published"
        : "publish";

    paused.value = true;

    return;
  }

  if (
    pendingRemoteVersionSync.value
  ) {
    await requestVersionSync({
      force: true,
    });
  }
};

const openPublishTab = () => {
  panelAbierto.value = true;
  activeAdminTab.value = "publish";
};

const handleContinue = async () => {
  if (dialogData.value.visible) {
    return;
  }

  if (
    isAdmin.value &&
    isLayoutDirty.value &&
    !savingLayout.value
  ) {
    await persistRemoteLayout();
  }

  if (
    pendingRemoteVersionSync.value
  ) {
    await requestVersionSync({
      force: true,
    });
  }

  emit("continue");
};

const selectBanner = (index) => {
  moveToBanner(index, true);
};

const editBanner = (index) => {
  moveToBanner(index, true);

  activeAdminTab.value =
    "content";
};

const syncSelectionWithBanners =
  () => {
    const validIds = new Set(
      bannersNormalized.value.map(
        (banner) => banner.id
      )
    );

    selectedBannerIds.value =
      selectedBannerIds.value.filter(
        (id) => validIds.has(id)
      );
  };

const isSelected = (id) => {
  return selectedBannerIds.value.includes(
    id
  );
};

const toggleBannerSelection = (id) => {
  selectedBannerIds.value =
    isSelected(id)
      ? selectedBannerIds.value.filter(
          (item) => item !== id
        )
      : [
          ...selectedBannerIds.value,
          id,
        ];
};

const toggleSelectAll = () => {
  selectedBannerIds.value =
    allSelected.value
      ? []
      : bannersNormalized.value.map(
          (banner) => banner.id
        );
};

const stopCarousel = () => {
  if (!carouselTimer) {
    return;
  }

  window.clearInterval(
    carouselTimer
  );

  carouselTimer = null;
};

const moveToBanner = (
  index,
  temporaryPause = true
) => {
  const total =
    bannersNormalized.value.length;

  if (!total) {
    return;
  }

  currentBanner.value = clamp(
    index,
    0,
    total - 1
  );

  if (temporaryPause) {
    paused.value = true;

    window.clearTimeout(
      pauseTimeout
    );

    pauseTimeout =
      window.setTimeout(() => {
        if (
          !document.hidden &&
          !dialogData.value.visible &&
          !manageModeActive.value
        ) {
          paused.value = false;
        }
      }, TEMPORARY_PAUSE_MS);
  }
};

const startCarousel = () => {
  stopCarousel();

  if (
    bannersNormalized.value.length <= 1
  ) {
    return;
  }

  carouselTimer =
    window.setInterval(() => {
      if (
        paused.value ||
        bannersNormalized.value.length <=
          1
      ) {
        return;
      }

      moveToBanner(
        (currentBanner.value + 1) %
          bannersNormalized.value.length,
        false
      );
    }, CAROUSEL_CYCLE_MS);
};

const pauseCarousel = () => {
  paused.value = true;
};

const resumeCarousel = () => {
  if (
    !document.hidden &&
    !dialogData.value.visible &&
    !manageModeActive.value
  ) {
    paused.value = false;
  }
};

const goTo = (index) => {
  moveToBanner(index, true);
};

const next = () => {
  const total =
    bannersNormalized.value.length;

  if (total > 1) {
    moveToBanner(
      (currentBanner.value + 1) %
        total,
      true
    );
  }
};

const prev = () => {
  const total =
    bannersNormalized.value.length;

  if (total > 1) {
    moveToBanner(
      (currentBanner.value -
        1 +
        total) %
        total,
      true
    );
  }
};

const onCarouselKeydown = (event) => {
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    prev();

    return;
  }

  if (event.key === "ArrowRight") {
    event.preventDefault();
    next();
  }
};

const onVisibilityChange = () => {
  paused.value =
    document.hidden ||
    dialogData.value.visible ||
    manageModeActive.value;
};

const revokeAllPreviews = () => {
  previews.value.forEach((url) => {
    URL.revokeObjectURL(url);
  });
};

const setFiles = (
  selectedFiles
) => {
  revokeAllPreviews();

  files.value = selectedFiles;

  previews.value =
    selectedFiles.map((file) => {
      return URL.createObjectURL(file);
    });
};

const normalizePickedImages = (
  selectedFiles
) => {
  const validImages = [];

  let invalidType = 0;
  let invalidSize = 0;

  selectedFiles.forEach((file) => {
    if (
      !ALLOWED_IMAGE_TYPES.has(
        file.type
      )
    ) {
      invalidType += 1;

      return;
    }

    if (
      Number(file.size || 0) >
      MAX_BANNER_FILE_SIZE
    ) {
      invalidSize += 1;

      return;
    }

    validImages.push(file);
  });

  if (
    invalidType &&
    invalidSize
  ) {
    setPanelError(
      "Algunos archivos no son JPG o PNG y otros superan el límite de 2 MB."
    );
  } else if (invalidType) {
    setPanelError(
      "Solo se admiten imágenes JPG o PNG."
    );
  } else if (invalidSize) {
    setPanelError(
      "Cada imagen debe pesar como máximo 2 MB."
    );
  } else {
    clearPanelError();
  }

  return validImages;
};

const preloadImage = (src) => {
  return new Promise((resolve) => {
    if (
      !src ||
      preloadedSources.has(src)
    ) {
      resolve();

      return;
    }

    const image = new Image();

    const finish = () => {
      preloadedSources.add(src);
      resolve();
    };

    image.onload = finish;
    image.onerror = finish;
    image.src = src;
  });
};

const prefetchNeighborBanners = (
  index
) => {
  const list =
    bannersNormalized.value;

  if (!list.length) {
    return;
  }

  preloadImage(
    list[index]?.image_url
  );

  preloadImage(
    list[
      (index + 1) % list.length
    ]?.image_url
  );

  if (list.length > 2) {
    preloadImage(
      list[
        (index - 1 + list.length) %
          list.length
      ]?.image_url
    );
  }
};

const openPicker = () => {
  if (
    !uploading.value &&
    !deletingBulk.value
  ) {
    fileInput.value?.click();
  }
};

const onFileChange = (event) => {
  const selectedFiles =
    Array.from(
      event.target?.files || []
    );

  const normalized =
    normalizePickedImages(
      selectedFiles
    );

  setFiles(normalized);

  if (event.target) {
    event.target.value = "";
  }
};

const onDragOver = (event) => {
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect =
      "copy";
  }
};

const onDragEnter = () => {
  dragDepth.value += 1;
  dragging.value = true;
};

const onDragLeave = () => {
  dragDepth.value = Math.max(
    0,
    dragDepth.value - 1
  );

  if (!dragDepth.value) {
    dragging.value = false;
  }
};

const onDrop = (event) => {
  dragDepth.value = 0;
  dragging.value = false;

  const selectedFiles =
    Array.from(
      event.dataTransfer?.files || []
    );

  const picked =
    normalizePickedImages(
      selectedFiles
    );

  if (picked.length) {
    setFiles(picked);
  }
};

const removeFileAt = (index) => {
  const nextFiles = [
    ...files.value,
  ];

  nextFiles.splice(index, 1);

  setFiles(nextFiles);
};

const cargarBanners = async ({
  preserveActive = true,
  showLoading = true,
  preferredBannerId = null,
} = {}) => {
  const previousIndex =
    currentBanner.value;

  const previousActiveId =
    preferredBannerId ??
    (
      preserveActive
        ? activeBannerItem.value?.id ??
          null
        : null
    );

  const mustShowLoading =
    showLoading ||
    !heroReady.value;

  if (mustShowLoading) {
    loading.value = true;
    heroReady.value = false;
  }

  loadError.value = "";

  try {
    const response =
      await api.get(
        "banners/",
        {
          params: {
            _ts: Date.now(),
          },
        }
      );

    const list =
      Array.isArray(response.data)
        ? response.data
        : [];

    banners.value = list;

    if (list.length) {
      let nextIndex = 0;

      if (previousActiveId) {
        const foundIndex =
          list.findIndex(
            (item) =>
              item.id ===
              previousActiveId
          );

        nextIndex =
          foundIndex >= 0
            ? foundIndex
            : Math.min(
                previousIndex,
                list.length - 1
              );
      }

      currentBanner.value =
        nextIndex;

      await preloadImage(
        list[nextIndex]?.image_url
      );

      prefetchNeighborBanners(
        nextIndex
      );
    } else {
      currentBanner.value = 0;
    }

    heroReady.value = true;

    syncSelectionWithBanners();
    syncActiveBannerEditor();
  } catch (error) {
    console.error(error);

    banners.value = [];

    selectedBannerIds.value = [];

    loadError.value =
      "No fue posible cargar los avisos en este momento.";

    heroReady.value = true;

    syncActiveBannerEditor();
  } finally {
    if (mustShowLoading) {
      loading.value = false;
    }
  }
};

const subirBanners = async () => {
  if (
    !files.value.length ||
    uploading.value ||
    deletingBulk.value
  ) {
    return;
  }

  uploading.value = true;

  clearPanelError();

  uploadIndex.value = 0;
  uploadTotal.value =
    files.value.length;

  const activeIdBeforeUpload =
    activeBannerItem.value?.id ??
    null;

  let success = true;

  try {
    for (
      let index = 0;
      index < files.value.length;
      index += 1
    ) {
      uploadIndex.value =
        index + 1;

      const form = new FormData();

      form.append(
        "image",
        files.value[index]
      );

      await api.post(
        "banners/",
        form,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );
    }
  } catch (error) {
    console.error(error);

    success = false;

    setPanelError(
      "No fue posible publicar los avisos. Intenta nuevamente."
    );
  } finally {
    if (success) {
      setFiles([]);
    }

    await cargarBanners({
      preserveActive: true,
      showLoading: false,
      preferredBannerId:
        activeIdBeforeUpload,
    });

    if (success) {
      setEditorStatus(
        "Avisos publicados correctamente."
      );

      activeAdminTab.value =
        "published";

      await requestVersionSync();
    }

    uploading.value = false;
    uploadIndex.value = 0;
    uploadTotal.value = 0;
  }
};

const mostrarDialogoEliminar = ({
  banner = null,
  count = 1,
} = {}) => {
  return new Promise((resolve) => {
    dialogData.value = {
      visible: true,

      titulo:
        count > 1
          ? "Eliminar avisos"
          : "Eliminar aviso",

      mensaje:
        count > 1
          ? `Se eliminarán ${count} avisos seleccionados.`
          : "Se eliminará el aviso seleccionado.",

      bannerImg:
        banner?.image_url || "",

      count,
      resolve,
    };
  });
};

const cerrarDialogo = (
  confirmed
) => {
  if (
    typeof dialogData.value
      .resolve === "function"
  ) {
    dialogData.value.resolve(
      confirmed
    );
  }

  dialogData.value = {
    visible: false,
    titulo: "",
    mensaje: "",
    bannerImg: "",
    count: 0,
    resolve: null,
  };
};

const eliminarBanner = async (id) => {
  const banner =
    bannersNormalized.value.find(
      (item) => item.id === id
    );

  const confirmed =
    await mostrarDialogoEliminar({
      banner,
    });

  if (!confirmed) {
    return;
  }

  deletingId.value = id;

  clearPanelError();

  const currentActiveId =
    activeBannerItem.value?.id ??
    null;

  const preferredBannerId =
    currentActiveId === id
      ? null
      : currentActiveId;

  try {
    await api.delete(
      `banners/${id}/`
    );

    selectedBannerIds.value =
      selectedBannerIds.value.filter(
        (item) => item !== id
      );

    await cargarBanners({
      preserveActive: true,
      showLoading: false,
      preferredBannerId,
    });

    setEditorStatus(
      "Aviso eliminado."
    );

    await requestVersionSync();
  } catch (error) {
    console.error(error);

    setPanelError(
      "No fue posible eliminar el aviso seleccionado."
    );
  } finally {
    deletingId.value = null;
  }
};

const eliminarSeleccionados =
  async () => {
    if (
      !selectedBannerIds.value
        .length ||
      deletingBulk.value ||
      uploading.value
    ) {
      return;
    }

    const ids = [
      ...selectedBannerIds.value,
    ];

    const confirmed =
      await mostrarDialogoEliminar({
        count: ids.length,
      });

    if (!confirmed) {
      return;
    }

    deletingBulk.value = true;

    bulkDeleteProgress.value = 0;
    bulkDeleteTotal.value =
      ids.length;

    clearPanelError();

    const activeId =
      activeBannerItem.value?.id ??
      null;

    const preferredBannerId =
      ids.includes(activeId)
        ? null
        : activeId;

    let failed = 0;

    try {
      for (
        let index = 0;
        index < ids.length;
        index += 1
      ) {
        bulkDeleteProgress.value =
          index + 1;

        try {
          await api.delete(
            `banners/${ids[index]}/`
          );
        } catch {
          failed += 1;
        }
      }

      selectedBannerIds.value = [];

      await cargarBanners({
        preserveActive: true,
        showLoading: false,
        preferredBannerId,
      });

      if (failed) {
        setPanelError(
          failed === ids.length
            ? "No fue posible eliminar los avisos seleccionados."
            : `${failed} aviso${
                failed !== 1 ? "s" : ""
              } no pudo${
                failed !== 1
                  ? "ieron"
                  : ""
              } eliminarse.`
        );
      } else {
        setEditorStatus(
          "Avisos eliminados."
        );

        await requestVersionSync();
      }
    } finally {
      deletingBulk.value = false;

      bulkDeleteProgress.value = 0;
      bulkDeleteTotal.value = 0;
    }
  };

const getModalFocusableElements =
  () => {
    if (!modalCard.value) {
      return [];
    }

    return [
      ...modalCard.value.querySelectorAll(
        FOCUSABLE_SELECTOR
      ),
    ];
  };

const onConfirmKeydown = (event) => {
  if (event.key === "Escape") {
    event.preventDefault();

    cerrarDialogo(false);

    return;
  }

  if (event.key !== "Tab") {
    return;
  }

  const focusable =
    getModalFocusableElements();

  if (!focusable.length) {
    event.preventDefault();

    modalCard.value?.focus();

    return;
  }

  const first = focusable[0];

  const last =
    focusable[
      focusable.length - 1
    ];

  const active =
    document.activeElement;

  if (
    event.shiftKey &&
    active === first
  ) {
    event.preventDefault();
    last.focus();

    return;
  }

  if (
    !event.shiftKey &&
    active === last
  ) {
    event.preventDefault();
    first.focus();
  }
};

watch(
  () => props.user,
  (value) => {
    usuario.value =
      value || null;
  },
  {
    immediate: true,
    deep: true,
  }
);

watch(
  () => props.version,
  async (
    nextVersion,
    previousVersion
  ) => {
    const next = String(
      nextVersion || ""
    );

    const previous = String(
      previousVersion || ""
    );

    if (
      next &&
      next !== previous
    ) {
      await refreshRemoteStateFromVersion();
    }
  }
);

watch(
  () => manageModeActive.value,
  async (active) => {
    paused.value =
      active ||
      document.hidden ||
      dialogData.value.visible;

    syncActiveBannerEditor();

    if (
      !active &&
      pendingRemoteVersionSync.value
    ) {
      await requestVersionSync({
        force: true,
      });
    }
  },
  {
    immediate: true,
  }
);

watch(
  () =>
    bannersNormalized.value.length,
  (length) => {
    if (!length) {
      currentBanner.value = 0;

      stopCarousel();
      syncActiveBannerEditor();

      return;
    }

    currentBanner.value =
      Math.min(
        currentBanner.value,
        length - 1
      );

    if (length > 1) {
      startCarousel();
    } else {
      stopCarousel();
    }
  },
  {
    immediate: true,
  }
);

watch(
  () => currentBanner.value,
  (index) => {
    prefetchNeighborBanners(index);
    syncActiveBannerEditor();
  }
);

watch(
  () => bannersNormalized.value,
  () => {
    syncSelectionWithBanners();
  },
  {
    deep: true,
    immediate: true,
  }
);

watch(
  () => dialogData.value.visible,
  async (visible) => {
    if (visible) {
      lastFocusedElement =
        document.activeElement instanceof
        HTMLElement
          ? document.activeElement
          : null;

      paused.value = true;

      await nextTick();

      modalCard.value?.focus();

      return;
    }

    lastFocusedElement?.focus?.();

    lastFocusedElement = null;

    if (
      !document.hidden &&
      !manageModeActive.value
    ) {
      paused.value = false;
    }
  }
);

onMounted(async () => {
  updateCompactScreen();

  document.addEventListener(
    "visibilitychange",
    onVisibilityChange
  );

  window.addEventListener(
    "resize",
    updateCompactScreen
  );

  const token =
    localStorage.getItem(
      "access_token"
    );

  const profilePromise =
    props.user
      ? Promise.resolve().then(() => {
          usuario.value =
            props.user;
        })
      : token
        ? api
            .get("auth/profile/")
            .then(({ data }) => {
              usuario.value = data;
            })
            .catch(() => {
              usuario.value = null;
            })
        : Promise.resolve().then(
            () => {
              usuario.value = null;
            }
          );

  const layout =
    getAvisosLayout();

  stageWidth.value =
    sanitizeStageWidth(
      layout?.stageWidth
    );

  stageHeight.value =
    sanitizeStageHeight(
      layout?.stageHeight
    );

  mediaPaneWidth.value =
    sanitizeMediaWidth(
      layout?.mediaPaneWidth,
      stageWidth.value
    );

  displayMode.value =
    sanitizeDisplayMode(
      layout?.displayMode
    );

  syncPersistedLayout();

  await Promise.allSettled([
    profilePromise,
    loadRemoteConfig(),
    cargarBanners(),
  ]);

  syncActiveBannerEditor();

  if (
    props.initialManage &&
    isAdmin.value
  ) {
    panelAbierto.value = true;

    activeAdminTab.value =
      hasBanners.value
        ? "published"
        : "publish";
  }
});

onUnmounted(() => {
  stopCarousel();
  revokeAllPreviews();

  window.clearTimeout(
    pauseTimeout
  );

  window.clearTimeout(
    panelErrorTimeout
  );

  window.clearTimeout(
    editorStatusTimeout
  );

  document.removeEventListener(
    "visibilitychange",
    onVisibilityChange
  );

  window.removeEventListener(
    "resize",
    updateCompactScreen
  );
});
</script>

<style scoped src="./banner-principal.css"></style>