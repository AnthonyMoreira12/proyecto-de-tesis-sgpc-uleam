<template>
  <div class="avn-content">
    <section
      class="avn-stage-card"
      :class="{ 'is-manage-active': showContainerResizeHandles }"
      :style="stageCardStyle"
    >
      <button
        class="avn-close"
        type="button"
        aria-label="Cerrar avisos"
        @click="handleContinue"
      >
        ×
      </button>

      <template v-if="showContainerResizeHandles">
        <button
          v-for="direction in resizeDirections"
          :key="direction"
          class="avn-window-handle"
          :class="`avn-window-handle--${direction}`"
          type="button"
          :aria-label="getResizeAriaLabel(direction)"
          @pointerdown.prevent="startContainerResize(direction, $event)"
        ></button>

        <div class="avn-window-grip" aria-hidden="true"></div>
      </template>

      <section
        v-if="loading || !heroReady"
        class="avn-stage-card__loading"
        aria-busy="true"
        aria-label="Cargando avisos"
      >
        <div class="avn-stage-card__shimmer"></div>
      </section>

      <template v-else-if="showCarousel">
        <div
          class="avn-stage"
          :class="{
            'avn-stage--mixed': isMixedMode,
            'avn-stage--banner-only': isBannerOnly,
            'avn-stage--text-only': isTextOnly
          }"
          :style="stageGridStyle"
        >
          <section
            v-if="!isTextOnly"
            class="avn-stage__media"
            :class="{ 'is-full': isBannerOnly }"
          >
            <div
              class="avn-carousel"
              tabindex="0"
              role="region"
              aria-roledescription="carrusel"
              :aria-label="`Avisos institucionales (${currentBanner + 1} de ${bannersNormalized.length})`"
              @mouseenter="pauseCarousel"
              @mouseleave="resumeCarousel"
              @keydown="onCarouselKeydown"
            >
              <p class="sr-only" aria-live="polite">
                Aviso {{ currentBanner + 1 }} de {{ bannersNormalized.length }}.
              </p>

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
                    :alt="`Aviso institucional ${index + 1}`"
                    class="avn-slide__img"
                    :loading="index === currentBanner ? 'eager' : 'lazy'"
                    :fetchpriority="index === currentBanner ? 'high' : 'low'"
                    :decoding="index === currentBanner ? 'sync' : 'async'"
                  />
                </article>
              </div>

              <button
                v-if="bannersNormalized.length > 1"
                class="avn-nav avn-nav--prev"
                type="button"
                aria-label="Aviso anterior"
                @click="prev"
              >
                ‹
              </button>

              <button
                v-if="bannersNormalized.length > 1"
                class="avn-nav avn-nav--next"
                type="button"
                aria-label="Siguiente aviso"
                @click="next"
              >
                ›
              </button>

              <div
                v-if="bannersNormalized.length > 1"
                class="avn-dots"
                aria-label="Seleccionar aviso"
              >
                <button
                  v-for="(banner, i) in bannersNormalized"
                  :key="banner.id"
                  class="avn-dot"
                  :class="{ 'is-active': i === currentBanner }"
                  type="button"
                  :aria-label="`Ir al aviso ${i + 1}`"
                  :aria-current="i === currentBanner ? 'true' : 'false'"
                  @click="goTo(i)"
                />
              </div>
            </div>
          </section>

          <button
            v-if="isMixedMode && showContainerResizeHandles"
            class="avn-stage__splitter"
            type="button"
            aria-label="Mover división entre banner y texto"
            @pointerdown.prevent="startPaneResize($event)"
          ></button>

          <div
            v-else-if="isMixedMode && !isCompactScreen"
            class="avn-stage__divider"
            aria-hidden="true"
          ></div>

          <section
            v-if="!isBannerOnly"
            class="avn-stage__aside"
            :class="{ 'is-full': isTextOnly }"
          >
            <div class="avn-stage__panel">
              <div
                class="avn-stage__body"
                :class="{ 'is-text-only': isTextOnly }"
              >
                <template v-if="isTextOnly">
                  <div class="avn-stage__text-shell">
                    <div
                      v-if="bannersNormalized.length > 1 || panelDisplayContent.recentLabel"
                      class="avn-stage__text-topbar"
                    >
                      <div class="avn-stage__text-topbar-left">
                        <span class="avn-stage__text-kicker">
                          Comunicado institucional
                        </span>

                        <span
                          v-if="panelDisplayContent.recentLabel"
                          class="avn-stage__text-badge"
                        >
                          {{ panelDisplayContent.recentLabel }}
                        </span>
                      </div>

                      <span
                        v-if="bannersNormalized.length > 1"
                        class="avn-stage__text-counter"
                      >
                        {{ currentBanner + 1 }} / {{ bannersNormalized.length }}
                      </span>
                    </div>

                    <div class="avn-stage__copy avn-stage__copy--text-only">
                      <div class="avn-stage__eyebrow-row">
                        <span v-if="!showInlineEditor" class="avn-stage__eyebrow">
                          {{ panelDisplayContent.eyebrow }}
                        </span>

                        <label
                          v-else
                          class="avn-inline-pill"
                          for="avn-active-eyebrow"
                        >
                          <span class="sr-only">Etiqueta superior del aviso</span>
                          <input
                            id="avn-active-eyebrow"
                            name="active_eyebrow"
                            autocomplete="off"
                            v-model="activeBannerContentDraft.eyebrow"
                            type="text"
                            class="avn-inline-pill__input"
                            maxlength="60"
                          />
                        </label>
                      </div>

                      <h2 v-if="!showInlineEditor" class="avn-stage__title">
                        {{ panelDisplayContent.title }}
                      </h2>

                      <label
                        v-else
                        class="avn-inline-field avn-inline-field--title"
                        for="avn-active-title"
                      >
                        <span class="sr-only">Título del aviso</span>
                        <textarea
                          id="avn-active-title"
                          name="active_title"
                          autocomplete="off"
                          v-model="activeBannerContentDraft.title"
                          rows="3"
                          class="avn-inline-field__textarea avn-inline-field__textarea--title"
                          maxlength="220"
                        ></textarea>
                      </label>

                      <p v-if="!showInlineEditor" class="avn-stage__text">
                        {{ panelDisplayContent.text }}
                      </p>

                      <label
                        v-else
                        class="avn-inline-field"
                        for="avn-active-text"
                      >
                        <span class="sr-only">Mensaje principal del aviso</span>
                        <textarea
                          id="avn-active-text"
                          name="active_text"
                          autocomplete="off"
                          v-model="activeBannerContentDraft.text"
                          rows="6"
                          class="avn-inline-field__textarea"
                          maxlength="700"
                        ></textarea>
                      </label>

                      <div class="avn-stage__meta">
                        <span
                          v-if="manageModeActive"
                          class="avn-chip"
                        >
                          Aviso {{ currentBanner + 1 }} de {{ bannersNormalized.length }}
                        </span>

                        <span
                          v-if="manageModeActive"
                          class="avn-chip avn-chip--mode"
                        >
                          {{ displayModeLabel }}
                        </span>

                        <template v-if="showInlineEditor">
                          <label
                            class="avn-inline-pill avn-inline-pill--meta"
                            for="avn-active-recent-label-inline"
                          >
                            <span class="avn-inline-pill__prefix">Actualización</span>
                            <input
                              id="avn-active-recent-label-inline"
                              name="active_recent_label_inline"
                              autocomplete="off"
                              v-model="activeBannerContentDraft.recentLabel"
                              type="text"
                              class="avn-inline-pill__input avn-inline-pill__input--meta"
                              maxlength="60"
                            />
                          </label>

                          <span
                            v-if="hasActiveBannerContentChanges"
                            class="avn-chip avn-chip--pending"
                          >
                            Cambios sin guardar
                          </span>
                        </template>
                      </div>
                    </div>

                    <div
                      v-if="bannersNormalized.length > 1"
                      class="avn-stage__text-nav"
                    >
                      <div class="avn-stage__text-nav-copy">
                        <span class="avn-stage__text-nav-label">Más avisos</span>
                        <strong class="avn-stage__text-nav-title">
                          Navega entre los comunicados disponibles
                        </strong>
                      </div>

                      <div class="avn-stage__text-nav-actions">
                        <div class="avn-stage__nav-user-buttons">
                          <button
                            class="avn-pager-btn"
                            type="button"
                            aria-label="Aviso anterior"
                            @click="prev"
                          >
                            ‹
                          </button>

                          <button
                            class="avn-pager-btn"
                            type="button"
                            aria-label="Siguiente aviso"
                            @click="next"
                          >
                            ›
                          </button>
                        </div>

                        <div
                          class="avn-stage__dots-inline"
                          aria-label="Seleccionar aviso"
                        >
                          <button
                            v-for="(banner, i) in bannersNormalized"
                            :key="banner.id"
                            class="avn-dot"
                            :class="{ 'is-active': i === currentBanner }"
                            type="button"
                            :aria-label="`Ir al aviso ${i + 1}`"
                            :aria-current="i === currentBanner ? 'true' : 'false'"
                            @click="goTo(i)"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </template>

                <template v-else>
                  <div class="avn-stage__copy">
                    <div class="avn-stage__eyebrow-row">
                      <span v-if="!showInlineEditor" class="avn-stage__eyebrow">
                        {{ panelDisplayContent.eyebrow }}
                      </span>

                      <label
                        v-else
                        class="avn-inline-pill"
                        for="avn-active-eyebrow"
                      >
                        <span class="sr-only">Etiqueta superior del aviso</span>
                        <input
                          id="avn-active-eyebrow"
                          name="active_eyebrow"
                          autocomplete="off"
                          v-model="activeBannerContentDraft.eyebrow"
                          type="text"
                          class="avn-inline-pill__input"
                          maxlength="60"
                        />
                      </label>
                    </div>

                    <h2 v-if="!showInlineEditor" class="avn-stage__title">
                      {{ panelDisplayContent.title }}
                    </h2>

                    <label
                      v-else
                      class="avn-inline-field avn-inline-field--title"
                      for="avn-active-title"
                    >
                      <span class="sr-only">Título del aviso</span>
                      <textarea
                        id="avn-active-title"
                        name="active_title"
                        autocomplete="off"
                        v-model="activeBannerContentDraft.title"
                        rows="3"
                        class="avn-inline-field__textarea avn-inline-field__textarea--title"
                        maxlength="220"
                      ></textarea>
                    </label>

                    <p v-if="!showInlineEditor" class="avn-stage__text">
                      {{ panelDisplayContent.text }}
                    </p>

                    <label
                      v-else
                      class="avn-inline-field"
                      for="avn-active-text"
                    >
                      <span class="sr-only">Mensaje principal del aviso</span>
                      <textarea
                        id="avn-active-text"
                        name="active_text"
                        autocomplete="off"
                        v-model="activeBannerContentDraft.text"
                        rows="6"
                        class="avn-inline-field__textarea"
                        maxlength="700"
                      ></textarea>
                    </label>

                    <div class="avn-stage__meta">
                      <span class="avn-chip">
                        Aviso {{ currentBanner + 1 }} de {{ bannersNormalized.length }}
                      </span>

                      <span
                        v-if="manageModeActive"
                        class="avn-chip avn-chip--mode"
                      >
                        {{ displayModeLabel }}
                      </span>

                      <template v-if="!showInlineEditor">
                        <span
                          v-if="bannersNormalized.length > 1 && panelDisplayContent.recentLabel"
                          class="avn-chip"
                        >
                          {{ panelDisplayContent.recentLabel }}
                        </span>
                      </template>

                      <template v-else>
                        <label
                          class="avn-inline-pill avn-inline-pill--meta"
                          for="avn-active-recent-label-inline"
                        >
                          <span class="avn-inline-pill__prefix">Actualización</span>
                          <input
                            id="avn-active-recent-label-inline"
                            name="active_recent_label_inline"
                            autocomplete="off"
                            v-model="activeBannerContentDraft.recentLabel"
                            type="text"
                            class="avn-inline-pill__input avn-inline-pill__input--meta"
                            maxlength="60"
                          />
                        </label>

                        <span
                          v-if="hasActiveBannerContentChanges"
                          class="avn-chip avn-chip--pending"
                        >
                          Cambios sin guardar
                        </span>
                      </template>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </section>
        </div>
      </template>

      <div v-else class="avn-stage avn-stage--empty">
        <div class="avn-stage__empty">
          <section class="avn-empty">
            <div class="avn-empty__seal" aria-hidden="true">
              SGPC ULEAM
            </div>

            <p class="avn-empty__kicker">Avisos</p>

            <h2 class="avn-empty__title">
              {{ isAdmin ? "Sin avisos publicados" : "Sin avisos disponibles" }}
            </h2>

            <p class="avn-empty__text">
              {{
                isAdmin
                  ? "Crea un aviso para mostrarlo en el inicio."
                  : "No hay comunicados activos por ahora."
              }}
            </p>

            <button
              v-if="isAdmin"
              class="avn-btn avn-btn--primary avn-empty__btn"
              type="button"
              @click="toggleGestion"
            >
              Administrar avisos
            </button>
          </section>
        </div>
      </div>
    </section>

    <div
      v-if="showAdminPanel && !loading && heroReady && !panelAbierto && hasBanners"
      class="avn-manage-fab-shell"
      :style="stageShellStyle"
    >
      <button
        class="avn-manage-fab"
        type="button"
        @click="toggleGestion"
      >
        Administrar avisos
      </button>
    </div>

    <section
      v-if="showAdminPanel && panelAbierto"
      class="avn-admin-shell"
      :style="stageShellStyle"
      aria-label="Panel de edición de avisos"
    >
      <transition name="drawer" appear>
        <section class="avn-admin">
          <div class="avn-admin__top">
            <div class="avn-admin__summary">
              <div class="avn-admin__summary-copy">
                <h3 class="avn-admin__title">Administración de avisos</h3>
                <p class="avn-admin__subtitle">
                  Edita el aviso activo, organiza los publicados, ajusta la presentación y publica nuevas imágenes desde una sola vista.
                </p>
              </div>

              <div class="avn-admin__chips">
                <span class="avn-admin-chip">
                  {{ bannersNormalized.length }} publicado<span v-if="bannersNormalized.length !== 1">s</span>
                </span>

                <span v-if="showCarousel" class="avn-admin-chip">
                  Activo {{ currentBanner + 1 }}/{{ bannersNormalized.length }}
                </span>

                <span class="avn-admin-chip">
                  {{ displayModeLabel }}
                </span>

                <span
                  v-if="pendingChangeCount"
                  class="avn-admin-chip avn-admin-chip--accent"
                >
                  Pendiente<span v-if="pendingChangeCount !== 1">s</span>: {{ pendingChangeCount }}
                </span>
              </div>
            </div>

            <div class="avn-admin__toolbar">
              <button
                class="avn-btn avn-btn--subtle"
                type="button"
                @click="toggleGestion"
              >
                Ocultar edición
              </button>
            </div>
          </div>

          <p
            v-if="editorStatus"
            class="avn-alert avn-admin__flash"
          >
            {{ editorStatus }}
          </p>

          <p
            v-if="panelError || loadError"
            class="avn-alert avn-alert--error avn-admin__flash"
            role="alert"
          >
            {{ panelError || loadError }}
          </p>

          <div class="avn-admin__grid">
            <div class="avn-card avn-card--published">
              <div class="avn-card__head avn-card__head--stack">
                <div>
                  <h4 class="avn-card__title">Avisos publicados</h4>
                  <p class="avn-card__sub">
                    Selecciona, revisa y elimina los avisos visibles.
                  </p>
                </div>
              </div>

              <div v-if="bannersNormalized.length" class="avn-bulk-actions avn-bulk-actions--block">
                <div class="avn-bulk-actions__left">
                  <label class="avn-bulk-check" for="avn-select-all">
                    <input
                      id="avn-select-all"
                      name="select_all_banners"
                      type="checkbox"
                      :checked="allSelected"
                      :disabled="uploading || deletingBulk"
                      @change="toggleSelectAll"
                    />
                    <span>Seleccionar todo</span>
                  </label>

                  <span class="avn-bulk-count">
                    Seleccionados: {{ selectedBannerIds.length }}
                  </span>
                </div>

                <div class="avn-bulk-actions__right">
                  <button
                    v-if="selectedBannerIds.length"
                    class="avn-btn avn-btn--danger"
                    type="button"
                    :disabled="uploading || deletingBulk"
                    @click="eliminarSeleccionados"
                  >
                    {{ deletingBulk ? bulkDeleteLabel : "Eliminar seleccionados" }}
                  </button>
                </div>
              </div>

              <div v-if="bannersNormalized.length" class="avn-grid-mini">
                <div
                  v-for="banner in bannersNormalized"
                  :key="banner.id"
                  class="avn-mini"
                  :class="{ 'is-selected': isSelected(banner.id) }"
                >
                  <div class="avn-mini__media">
                    <label
                      class="avn-mini__select"
                      :for="`avn-banner-select-${banner.id}`"
                    >
                      <input
                        :id="`avn-banner-select-${banner.id}`"
                        :name="`banner_select_${banner.id}`"
                        type="checkbox"
                        :checked="isSelected(banner.id)"
                        :disabled="uploading || deletingBulk || deletingId === banner.id"
                        @change="toggleBannerSelection(banner.id)"
                      />
                      <span class="sr-only">Seleccionar aviso</span>
                    </label>

                    <img
                      class="avn-mini__img"
                      :src="banner.image_url"
                      alt="Aviso publicado"
                      loading="lazy"
                      decoding="async"
                    />

                    <button
                      class="avn-mini__del"
                      :class="{ 'is-loading': deletingId === banner.id }"
                      type="button"
                      :disabled="uploading || deletingBulk || deletingId === banner.id"
                      aria-label="Eliminar aviso"
                      title="Eliminar"
                      @click="eliminarBanner(banner.id)"
                    >
                      <span class="sr-only">Eliminar</span>

                      <svg
                        v-if="deletingId !== banner.id"
                        viewBox="0 0 24 24"
                        width="18"
                        height="18"
                        aria-hidden="true"
                      >
                        <path
                          fill="currentColor"
                          d="M9 3h6l1 2h4v2H4V5h4l1-2Zm1 7h2v9h-2v-9Zm4 0h2v9h-2v-9ZM7 10h2v9H7v-9Z"
                        />
                      </svg>

                      <span v-else aria-hidden="true">…</span>
                    </button>
                  </div>
                </div>
              </div>

              <p v-else class="avn-muted">No hay avisos publicados.</p>
            </div>

            <div class="avn-admin__side">
              <div class="avn-card avn-card--editor">
                <div class="avn-card__head">
                  <div>
                    <h4 class="avn-card__title">Edición actual</h4>
                    <p class="avn-card__sub">
                      {{
                        showCarousel
                          ? isBannerOnly
                            ? "El modo solo banner oculta el texto en la vista previa. Edita aquí su contenido."
                            : "El texto del aviso se edita directamente en la vista previa."
                          : "Publica un aviso para habilitar la edición."
                      }}
                    </p>
                  </div>
                </div>

                <div class="avn-card__stack">
                  <div class="avn-action-group">
                    <span class="avn-action-group__label">Contenido</span>

                    <div v-if="showCarousel && isBannerOnly" class="avn-editor-form">
                      <label class="avn-field-stack" for="avn-panel-eyebrow">
                        <span class="avn-field-stack__label">Etiqueta superior</span>
                        <input
                          id="avn-panel-eyebrow"
                          v-model="activeBannerContentDraft.eyebrow"
                          type="text"
                          maxlength="60"
                          class="avn-inline-field__input"
                          autocomplete="off"
                        />
                      </label>

                      <label class="avn-field-stack" for="avn-panel-title">
                        <span class="avn-field-stack__label">Título</span>
                        <textarea
                          id="avn-panel-title"
                          v-model="activeBannerContentDraft.title"
                          rows="3"
                          maxlength="220"
                          class="avn-inline-field__textarea avn-inline-field__textarea--title"
                          autocomplete="off"
                        ></textarea>
                      </label>

                      <label class="avn-field-stack" for="avn-panel-text">
                        <span class="avn-field-stack__label">Mensaje</span>
                        <textarea
                          id="avn-panel-text"
                          v-model="activeBannerContentDraft.text"
                          rows="6"
                          maxlength="700"
                          class="avn-inline-field__textarea"
                          autocomplete="off"
                        ></textarea>
                      </label>

                      <label class="avn-field-stack" for="avn-panel-recent">
                        <span class="avn-field-stack__label">Etiqueta de actualización</span>
                        <input
                          id="avn-panel-recent"
                          v-model="activeBannerContentDraft.recentLabel"
                          type="text"
                          maxlength="60"
                          class="avn-inline-field__input"
                          autocomplete="off"
                        />
                      </label>
                    </div>

                    <div v-if="showCarousel" class="avn-btn-group avn-btn-group--end avn-btn-group--wrap">
                      <button
                        class="avn-btn avn-btn--subtle"
                        type="button"
                        :disabled="!hasActiveBannerContentChanges || savingBannerContent"
                        @click="cancelActiveBannerContent"
                      >
                        Descartar
                      </button>

                      <button
                        class="avn-btn avn-btn--ghost"
                        type="button"
                        :disabled="savingBannerContent"
                        @click="resetActiveBannerContent"
                      >
                        Restablecer
                      </button>

                      <button
                        class="avn-btn avn-btn--primary"
                        type="button"
                        :disabled="!hasActiveBannerContentChanges || savingBannerContent"
                        @click="saveActiveBannerContent"
                      >
                        Guardar cambios
                      </button>
                    </div>

                    <p v-else class="avn-muted">Sin aviso activo.</p>
                  </div>

                  <div class="avn-action-group">
                    <span class="avn-action-group__label">Diseño</span>

                    <div class="avn-layout-switch" role="tablist" aria-label="Modo de visualización del aviso">
                      <button
                        v-for="option in displayModeOptions"
                        :key="option.value"
                        class="avn-layout-option"
                        :class="{ 'is-active': displayMode === option.value }"
                        type="button"
                        role="tab"
                        :aria-selected="displayMode === option.value ? 'true' : 'false'"
                        @click="setDisplayMode(option.value)"
                      >
                        {{ option.label }}
                      </button>
                    </div>

                    <div class="avn-btn-group avn-btn-group--end">
                      <button
                        class="avn-btn avn-btn--ghost"
                        type="button"
                        :disabled="savingLayout || !isLayoutDirty"
                        @click="saveCurrentLayout"
                      >
                        {{ savingLayout ? "Guardando diseño..." : "Guardar diseño" }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="avn-card avn-card--upload">
                <div class="avn-card__head">
                  <div>
                    <h4 class="avn-card__title">Publicar avisos</h4>
                    <p class="avn-card__sub">
                      Sube imágenes en formato JPG o PNG para agregarlas al carrusel institucional.
                    </p>
                  </div>
                </div>

                <div
                  class="avn-drop"
                  :class="{ 'is-dragging': dragging }"
                  @dragover.prevent="onDragOver"
                  @dragenter.prevent="onDragEnter"
                  @dragleave.prevent="onDragLeave"
                  @drop.prevent="onDrop"
                >
                  <div class="avn-drop__icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
                      <path
                        fill="currentColor"
                        d="M12 3l4 4h-3v7h-2V7H8l4-4Zm-7 14h14v2H5v-2Z"
                      />
                    </svg>
                  </div>

                  <div class="avn-drop__text">
                    <strong>Arrastra imágenes aquí</strong>
                    <span>Formatos admitidos: JPG o PNG · máximo {{ bannerMaxSizeLabel }} por imagen</span>
                  </div>
                </div>

                <div v-if="previews.length" class="avn-previews">
                  <div
                    v-for="(preview, i) in previews"
                    :key="`${preview}-${i}`"
                    class="avn-preview"
                  >
                    <img :src="preview" alt="Vista previa del aviso" />

                    <button
                      class="avn-preview__x"
                      type="button"
                      aria-label="Quitar imagen"
                      :disabled="uploading || deletingBulk"
                      @click="removeFileAt(i)"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <div class="avn-btn-group avn-btn-group--between avn-btn-group--wrap avn-btn-group--publish">
                  <button
                    class="avn-btn avn-btn--ghost"
                    type="button"
                    :disabled="uploading || deletingBulk"
                    @click="openPicker"
                  >
                    Seleccionar imágenes
                  </button>

                  <button
                    class="avn-btn avn-btn--primary avn-btn--publish"
                    :class="{ 'is-loading': uploading }"
                    type="button"
                    :disabled="!files.length || uploading || deletingBulk"
                    @click="subirBanners"
                  >
                    {{ uploading ? uploadLabel : "Publicar" }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </transition>
    </section>

    <div
      v-if="dialogData.visible"
      class="avn-confirm"
      role="dialog"
      aria-modal="true"
      aria-label="Confirmar eliminación"
    >
      <div class="avn-confirm__overlay" @click="cerrarDialogo(false)"></div>

      <div class="avn-confirm__card" ref="modalCard" tabindex="-1">
        <div class="avn-confirm__head">
          <div class="avn-confirm__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <path
                fill="currentColor"
                d="M12 2a10 10 0 1 0 .001 20.001A10 10 0 0 0 12 2Zm1 15h-2v-2h2v2Zm0-4h-2V7h2v6Z"
              />
            </svg>
          </div>

          <div>
            <h2 class="avn-confirm__title">{{ dialogData.titulo }}</h2>
            <p class="avn-confirm__msg">{{ dialogData.mensaje }}</p>
            <p class="avn-confirm__hint">Esta acción no se puede deshacer.</p>
          </div>
        </div>

        <img
          v-if="dialogData.bannerImg"
          :src="dialogData.bannerImg"
          alt="Aviso seleccionado"
          class="avn-confirm__preview"
        />

        <div
          v-else-if="dialogData.visible && dialogData.count > 1"
          class="avn-confirm__bulk"
        >
          <strong>{{ dialogData.count }}</strong>
          <span>avisos seleccionados para eliminar.</span>
        </div>

        <div class="avn-btn-group avn-btn-group--end avn-btn-group--modal">
          <button
            class="avn-btn avn-btn--ghost"
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
      </div>
    </div>

    <input
      id="avn-file-input"
      ref="fileInput"
      name="banners_images"
      type="file"
      accept="image/jpeg,image/png"
      multiple
      class="sr-only"
      @change="onFileChange"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import api from "../../scripts/api/axios";
import {
  DEFAULT_AVISOS_CONTENT,
  DEFAULT_AVISOS_LAYOUT,
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

const emit = defineEmits(["continue", "version-change"]);

const ALLOWED_IMAGE_TYPES = new Set(["image/jpeg", "image/png"]);
const MAX_BANNER_FILE_SIZE = 2 * 1024 * 1024;
const CAROUSEL_CYCLE_MS = 5200;
const TEMPORARY_PAUSE_MS = 4000;
const FOCUSABLE_SELECTOR =
  'button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])';

const COMPACT_BREAKPOINT = 980;

const STAGE_WIDTH_DEFAULT = DEFAULT_AVISOS_LAYOUT.stageWidth;
const STAGE_WIDTH_MIN = 900;
const STAGE_WIDTH_MAX = 1500;

const STAGE_HEIGHT_DEFAULT = DEFAULT_AVISOS_LAYOUT.stageHeight;
const STAGE_HEIGHT_MIN = 440;
const STAGE_HEIGHT_MAX = 900;

const SPLITTER_WIDTH = 14;
const MEDIA_WIDTH_RATIO_DEFAULT = 0.64;
const MEDIA_WIDTH_MIN = 420;
const ASIDE_WIDTH_MIN = 320;

const DISPLAY_MODE_DEFAULT = "mixed";
const DISPLAY_MODE_VALUES = new Set(["mixed", "banner", "text"]);

const displayModeOptions = [
  { value: "mixed", label: "Banner + texto" },
  { value: "banner", label: "Solo banner" },
  { value: "text", label: "Solo texto" },
];

const resizeDirections = ["n", "e", "s", "w", "nw", "ne", "sw", "se"];

const prettyBytes = (bytes) => {
  const size = Number(bytes || 0);
  if (size <= 0) return "0 B";

  const units = ["B", "KB", "MB", "GB"];
  let value = size;
  let index = 0;

  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }

  return `${value.toFixed(index === 0 ? 0 : 2)} ${units[index]}`;
};

const bannerMaxSizeLabel = prettyBytes(MAX_BANNER_FILE_SIZE);

const cloneContent = (value) => {
  return {
    ...DEFAULT_AVISOS_CONTENT,
    ...(value || {}),
  };
};

const normalizeContent = (value) => {
  const next = cloneContent(value);

  return {
    eyebrow: String(next.eyebrow || "").trim() || DEFAULT_AVISOS_CONTENT.eyebrow,
    title: String(next.title || "").trim() || DEFAULT_AVISOS_CONTENT.title,
    text: String(next.text || "").trim() || DEFAULT_AVISOS_CONTENT.text,
    recentLabel:
      String(next.recentLabel || "").trim() || DEFAULT_AVISOS_CONTENT.recentLabel,
  };
};

const getRawBannerContent = (banner) => {
  return {
    eyebrow: String(banner?.eyebrow || "").trim(),
    title: String(banner?.title || "").trim(),
    text: String(banner?.text || "").trim(),
    recentLabel: String(banner?.recentLabel || "").trim(),
  };
};

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

const safeInt = (value, fallback) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.round(parsed) : Math.round(fallback);
};

const sanitizeDisplayMode = (value) => {
  const normalized = String(value || "").trim().toLowerCase();
  return DISPLAY_MODE_VALUES.has(normalized) ? normalized : DISPLAY_MODE_DEFAULT;
};

const getStageWidthMax = () => {
  if (typeof window === "undefined") return STAGE_WIDTH_MAX;
  const gutter = window.innerWidth <= COMPACT_BREAKPOINT ? 24 : 64;
  return Math.max(
    STAGE_WIDTH_MIN,
    Math.min(STAGE_WIDTH_MAX, Math.round(window.innerWidth - gutter))
  );
};

const getStageHeightMax = () => {
  if (typeof window === "undefined") return STAGE_HEIGHT_MAX;
  return Math.max(
    STAGE_HEIGHT_MIN,
    Math.min(STAGE_HEIGHT_MAX, Math.round(window.innerHeight - 48))
  );
};

const getMediaWidthMax = (width = STAGE_WIDTH_DEFAULT) => {
  return Math.max(
    MEDIA_WIDTH_MIN,
    safeInt(width, STAGE_WIDTH_DEFAULT) - ASIDE_WIDTH_MIN - SPLITTER_WIDTH
  );
};

const getDefaultMediaWidth = (width = STAGE_WIDTH_DEFAULT) => {
  const base = Math.round(
    safeInt(width, STAGE_WIDTH_DEFAULT) * MEDIA_WIDTH_RATIO_DEFAULT
  );
  return clamp(base, MEDIA_WIDTH_MIN, getMediaWidthMax(width));
};

const sanitizeStageWidth = (value) =>
  clamp(safeInt(value, STAGE_WIDTH_DEFAULT), STAGE_WIDTH_MIN, getStageWidthMax());

const sanitizeStageHeight = (value) =>
  clamp(safeInt(value, STAGE_HEIGHT_DEFAULT), STAGE_HEIGHT_MIN, getStageHeightMax());

const sanitizeMediaWidth = (value, width = STAGE_WIDTH_DEFAULT) =>
  clamp(
    safeInt(value, getDefaultMediaWidth(width)),
    MEDIA_WIDTH_MIN,
    getMediaWidthMax(width)
  );

const getScaledMediaWidthForViewport = (
  rawStageWidth,
  rawMediaWidth,
  appliedStageWidth
) => {
  const sourceStageWidth = safeInt(rawStageWidth, STAGE_WIDTH_DEFAULT);
  const sourceMediaWidth = safeInt(
    rawMediaWidth,
    getDefaultMediaWidth(sourceStageWidth)
  );
  const targetStageWidth = safeInt(appliedStageWidth, sourceStageWidth);

  if (!sourceStageWidth || sourceStageWidth <= 0) {
    return sanitizeMediaWidth(sourceMediaWidth, targetStageWidth);
  }

  const ratio = sourceMediaWidth / sourceStageWidth;
  const scaledMediaWidth = Math.round(targetStageWidth * ratio);

  return sanitizeMediaWidth(scaledMediaWidth, targetStageWidth);
};

const scaleMediaWidthByStage = (
  currentStageWidth,
  nextStageWidth,
  currentMediaWidth
) => {
  const sourceStageWidth = safeInt(currentStageWidth, STAGE_WIDTH_DEFAULT);
  const targetStageWidth = safeInt(nextStageWidth, sourceStageWidth);
  const sourceMediaWidth = safeInt(
    currentMediaWidth,
    getDefaultMediaWidth(sourceStageWidth)
  );

  if (
    !sourceStageWidth ||
    sourceStageWidth <= 0 ||
    sourceStageWidth === targetStageWidth
  ) {
    return sanitizeMediaWidth(sourceMediaWidth, targetStageWidth);
  }

  const ratio = sourceMediaWidth / sourceStageWidth;
  return sanitizeMediaWidth(Math.round(targetStageWidth * ratio), targetStageWidth);
};

const banners = ref([]);
const currentBanner = ref(0);
const usuario = ref(props.user || null);

const loading = ref(true);
const heroReady = ref(false);

const panelAbierto = ref(false);
const paused = ref(false);

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
const stageWidth = ref(STAGE_WIDTH_DEFAULT);
const stageHeight = ref(STAGE_HEIGHT_DEFAULT);
const mediaPaneWidth = ref(getDefaultMediaWidth(STAGE_WIDTH_DEFAULT));
const displayMode = ref(DISPLAY_MODE_DEFAULT);

const persistedStageWidth = ref(STAGE_WIDTH_DEFAULT);
const persistedStageHeight = ref(STAGE_HEIGHT_DEFAULT);
const persistedMediaPaneWidth = ref(getDefaultMediaWidth(STAGE_WIDTH_DEFAULT));
const persistedDisplayMode = ref(DISPLAY_MODE_DEFAULT);

const isCompactScreen = ref(false);
const refreshingFromVersion = ref(false);
const pendingRemoteVersionSync = ref(false);

const contentSaved = ref(cloneContent(getAvisosContent()));

const activeBannerContentSaved = ref(cloneContent(DEFAULT_AVISOS_CONTENT));
const activeBannerContentDraft = ref(cloneContent(DEFAULT_AVISOS_CONTENT));

let carouselTimer = null;
let pauseTimeout = null;
let panelErrorTimeout = null;
let editorStatusTimeout = null;
let lastFocusedElement = null;
let activeLayoutInteraction = null;

const cycleMs = CAROUSEL_CYCLE_MS;
const preloadedSources = new Set();

const isAdmin = computed(() =>
  !!(
    usuario.value?.is_staff ||
    usuario.value?.is_superuser ||
    usuario.value?.es_admin ||
    usuario.value?.is_admin
  )
);

const bannersNormalized = computed(() => {
  return (Array.isArray(banners.value) ? banners.value : []).filter(
    (banner) => !!banner?.image_url
  );
});

const activeBannerItem = computed(() => {
  return bannersNormalized.value[currentBanner.value] || null;
});

const resolveBannerContent = (banner) => {
  const raw = getRawBannerContent(banner);

  return {
    eyebrow: raw.eyebrow || contentSaved.value.eyebrow,
    title: raw.title || contentSaved.value.title,
    text: raw.text || contentSaved.value.text,
    recentLabel: raw.recentLabel || contentSaved.value.recentLabel,
  };
};

const hasBanners = computed(() => bannersNormalized.value.length > 0);

const showCarousel = computed(
  () => !loading.value && heroReady.value && hasBanners.value
);

const showAdminPanel = computed(() => isAdmin.value);
const manageModeActive = computed(() => showAdminPanel.value && panelAbierto.value);

const isMixedMode = computed(() => displayMode.value === "mixed");
const isBannerOnly = computed(() => displayMode.value === "banner");
const isTextOnly = computed(() => displayMode.value === "text");

const showInlineEditor = computed(
  () =>
    manageModeActive.value &&
    showCarousel.value &&
    !isBannerOnly.value
);

const showContainerResizeHandles = computed(
  () => manageModeActive.value && !isCompactScreen.value
);

const displayModeLabel = computed(() => {
  if (isBannerOnly.value) return "Solo banner";
  if (isTextOnly.value) return "Solo texto";
  return "Banner + texto";
});

const panelDisplayContent = computed(() => {
  if (!showCarousel.value) {
    return contentSaved.value;
  }

  if (showInlineEditor.value) {
    return activeBannerContentDraft.value;
  }

  return resolveBannerContent(activeBannerItem.value);
});

const hasActiveBannerContentChanges = computed(() => {
  return (
    JSON.stringify(normalizeContent(activeBannerContentDraft.value)) !==
    JSON.stringify(normalizeContent(activeBannerContentSaved.value))
  );
});

const isLayoutDirty = computed(() => {
  return (
    stageWidth.value !== persistedStageWidth.value ||
    stageHeight.value !== persistedStageHeight.value ||
    mediaPaneWidth.value !== persistedMediaPaneWidth.value ||
    displayMode.value !== persistedDisplayMode.value
  );
});

const uploadLabel = computed(() => {
  const current = Math.min(uploadIndex.value, uploadTotal.value);
  return `Publicando… ${current} de ${uploadTotal.value}`;
});

const bulkDeleteLabel = computed(() => {
  const current = Math.min(bulkDeleteProgress.value, bulkDeleteTotal.value);
  return `Eliminando… ${current} de ${bulkDeleteTotal.value}`;
});

const allSelected = computed(() => {
  return (
    bannersNormalized.value.length > 0 &&
    selectedBannerIds.value.length === bannersNormalized.value.length
  );
});

const pendingChangeCount = computed(() => {
  let count = 0;
  if (hasActiveBannerContentChanges.value) count += 1;
  if (files.value.length) count += 1;
  if (isLayoutDirty.value) count += 1;
  return count;
});

const stageShellStyle = computed(() => {
  if (isCompactScreen.value) return {};

  return {
    width: `${stageWidth.value}px`,
    maxWidth: "calc(100vw - 24px)",
  };
});

const stageCardStyle = computed(() => {
  if (isCompactScreen.value) return {};

  return {
    width: `${stageWidth.value}px`,
    maxWidth: "calc(100vw - 24px)",
    height: `${stageHeight.value}px`,
    minHeight: `${stageHeight.value}px`,
  };
});

const stageGridStyle = computed(() => {
  if (isCompactScreen.value || !isMixedMode.value) return {};

  return {
    gridTemplateColumns: `${mediaPaneWidth.value}px ${SPLITTER_WIDTH}px minmax(${ASIDE_WIDTH_MIN}px, 1fr)`,
  };
});

const updateCompactScreen = () => {
  if (typeof window === "undefined") return;

  const prevWidth = stageWidth.value;
  const prevMediaWidth = mediaPaneWidth.value;

  isCompactScreen.value = window.innerWidth <= COMPACT_BREAKPOINT;

  stageWidth.value = sanitizeStageWidth(stageWidth.value);
  stageHeight.value = sanitizeStageHeight(stageHeight.value);

  if (prevWidth !== stageWidth.value) {
    mediaPaneWidth.value = scaleMediaWidthByStage(
      prevWidth,
      stageWidth.value,
      prevMediaWidth
    );
  } else {
    mediaPaneWidth.value = sanitizeMediaWidth(mediaPaneWidth.value, stageWidth.value);
  }
};

const setDisplayMode = (mode) => {
  displayMode.value = sanitizeDisplayMode(mode);
};

const setEditorStatus = (message, duration = 2600) => {
  editorStatus.value = message;
  clearTimeout(editorStatusTimeout);

  if (message) {
    editorStatusTimeout = setTimeout(() => {
      editorStatus.value = "";
    }, duration);
  }
};

const clearPanelError = () => {
  clearTimeout(panelErrorTimeout);
  panelError.value = "";
};

const setPanelError = (message, duration = 4000) => {
  panelError.value = message;
  clearTimeout(panelErrorTimeout);

  if (message) {
    panelErrorTimeout = setTimeout(() => {
      panelError.value = "";
    }, duration);
  }
};

const requestVersionSync = async ({ force = false } = {}) => {
  if (manageModeActive.value && !force) {
    pendingRemoteVersionSync.value = true;
    return;
  }

  const status = await getAvisosStatus().catch(() => null);
  const nextVersion =
    status?.notifyVersion ||
    status?.version ||
    getAvisosCombinedVersion(props.version);

  emit("version-change", nextVersion);
  pendingRemoteVersionSync.value = false;
};

const syncPersistedLayout = ({
  stageWidth: nextStageWidth = stageWidth.value,
  stageHeight: nextStageHeight = stageHeight.value,
  mediaPaneWidth: nextMediaPaneWidth = mediaPaneWidth.value,
  displayMode: nextDisplayMode = displayMode.value,
} = {}) => {
  persistedStageWidth.value = safeInt(nextStageWidth, STAGE_WIDTH_DEFAULT);
  persistedStageHeight.value = safeInt(nextStageHeight, STAGE_HEIGHT_DEFAULT);
  persistedMediaPaneWidth.value = safeInt(
    nextMediaPaneWidth,
    getDefaultMediaWidth(persistedStageWidth.value)
  );
  persistedDisplayMode.value = sanitizeDisplayMode(nextDisplayMode);
};

const applyRemoteConfig = (config = {}) => {
  const nextContent = cloneContent({
    eyebrow: config?.eyebrow,
    title: config?.title,
    text: config?.text,
    recentLabel: config?.recentLabel,
  });

  const rawStageWidth = safeInt(config?.stageWidth, STAGE_WIDTH_DEFAULT);
  const rawStageHeight = safeInt(config?.stageHeight, STAGE_HEIGHT_DEFAULT);
  const rawMediaPaneWidth = safeInt(
    config?.mediaPaneWidth,
    getDefaultMediaWidth(rawStageWidth)
  );

  const nextWidth = sanitizeStageWidth(rawStageWidth);
  const nextHeight = sanitizeStageHeight(rawStageHeight);

  const nextMediaWidth =
    rawStageWidth === nextWidth
      ? sanitizeMediaWidth(rawMediaPaneWidth, nextWidth)
      : getScaledMediaWidthForViewport(rawStageWidth, rawMediaPaneWidth, nextWidth);

  const nextDisplayMode = sanitizeDisplayMode(config?.displayMode);

  contentSaved.value = nextContent;
  stageWidth.value = nextWidth;
  stageHeight.value = nextHeight;
  mediaPaneWidth.value = nextMediaWidth;
  displayMode.value = nextDisplayMode;

  syncPersistedLayout({
    stageWidth: nextWidth,
    stageHeight: nextHeight,
    mediaPaneWidth: nextMediaWidth,
    displayMode: nextDisplayMode,
  });

  layoutLoaded.value = true;
};

const syncActiveBannerEditor = () => {
  if (!activeBannerItem.value) {
    activeBannerContentSaved.value = cloneContent(contentSaved.value);
    activeBannerContentDraft.value = cloneContent(contentSaved.value);
    return;
  }

  const resolved = resolveBannerContent(activeBannerItem.value);
  activeBannerContentSaved.value = cloneContent(resolved);
  activeBannerContentDraft.value = cloneContent(resolved);
};

const updateBannerInList = (savedBanner) => {
  banners.value = banners.value.map((item) =>
    item.id === savedBanner.id ? { ...item, ...savedBanner } : item
  );
  syncActiveBannerEditor();
};

const loadRemoteConfig = async () => {
  try {
    const config = await hydrateAvisosConfig();
    applyRemoteConfig(config);
  } catch (error) {
    console.error(error);

    applyRemoteConfig({
      ...getAvisosContent(),
      ...getAvisosLayout(),
    });
  }
};

const refreshRemoteStateFromVersion = async () => {
  if (refreshingFromVersion.value) return;
  if (manageModeActive.value) return;

  refreshingFromVersion.value = true;

  try {
    await Promise.allSettled([loadRemoteConfig(), cargarBanners()]);
    syncActiveBannerEditor();
  } finally {
    refreshingFromVersion.value = false;
  }
};

const persistRemoteLayout = async ({ showFeedback = false } = {}) => {
  if (!isAdmin.value || !layoutLoaded.value) return false;
  if (savingLayout.value) return false;

  savingLayout.value = true;

  try {
    const saved = await saveAvisosLayout({
      stageWidth: stageWidth.value,
      stageHeight: stageHeight.value,
      mediaPaneWidth: mediaPaneWidth.value,
      displayMode: displayMode.value,
    });

    applyRemoteConfig({
      ...saved,
      displayMode:
        saved?.displayMode != null ? saved.displayMode : displayMode.value,
    });

    if (showFeedback) {
      setEditorStatus("Diseño guardado correctamente.");
    }

    return true;
  } catch (error) {
    console.error(error);
    setPanelError("No fue posible guardar el diseño del aviso.");
    return false;
  } finally {
    savingLayout.value = false;
  }
};

const saveCurrentLayout = async () => {
  await persistRemoteLayout({ showFeedback: true });
};

const saveActiveBannerContent = async () => {
  if (!isAdmin.value || !activeBannerItem.value) return;

  savingBannerContent.value = true;
  clearPanelError();

  try {
    const payload = normalizeContent(activeBannerContentDraft.value);
    const { data } = await api.patch(`banners/${activeBannerItem.value.id}/`, payload);

    updateBannerInList(data);
    setEditorStatus("Texto del aviso guardado.");
    await requestVersionSync();
  } catch (error) {
    console.error(error);
    setPanelError("No fue posible guardar el texto del aviso activo.");
  } finally {
    savingBannerContent.value = false;
  }
};

const cancelActiveBannerContent = () => {
  activeBannerContentDraft.value = cloneContent(activeBannerContentSaved.value);
  setEditorStatus("");
};

const resetActiveBannerContent = async () => {
  if (!isAdmin.value || !activeBannerItem.value) return;

  savingBannerContent.value = true;
  clearPanelError();

  try {
    const { data } = await api.patch(`banners/${activeBannerItem.value.id}/`, {
      eyebrow: "",
      title: "",
      text: "",
      recentLabel: "",
    });

    updateBannerInList(data);
    setEditorStatus("Este aviso volvió a usar el texto global.");
    await requestVersionSync();
  } catch (error) {
    console.error(error);
    setPanelError("No fue posible restablecer el texto del aviso activo.");
  } finally {
    savingBannerContent.value = false;
  }
};

const toggleGestion = async () => {
  const nextState = !panelAbierto.value;
  panelAbierto.value = nextState;

  if (!nextState && pendingRemoteVersionSync.value) {
    await requestVersionSync({ force: true });
  }
};

const handleContinue = async () => {
  if (dialogData.value.visible) return;

  if (isAdmin.value && isLayoutDirty.value && !savingLayout.value) {
    await persistRemoteLayout({
      showFeedback: false,
    });
  }

  if (pendingRemoteVersionSync.value) {
    await requestVersionSync({ force: true });
  }

  emit("continue");
};

const syncSelectionWithBanners = () => {
  const validIds = new Set(bannersNormalized.value.map((banner) => banner.id));
  selectedBannerIds.value = selectedBannerIds.value.filter((id) =>
    validIds.has(id)
  );
};

const isSelected = (id) => selectedBannerIds.value.includes(id);

const toggleBannerSelection = (id) => {
  if (isSelected(id)) {
    selectedBannerIds.value = selectedBannerIds.value.filter(
      (item) => item !== id
    );
    return;
  }

  selectedBannerIds.value = [...selectedBannerIds.value, id];
};

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedBannerIds.value = [];
    return;
  }

  selectedBannerIds.value = bannersNormalized.value.map((banner) => banner.id);
};

const stopCarousel = () => {
  if (carouselTimer) {
    clearInterval(carouselTimer);
    carouselTimer = null;
  }
};

const moveToBanner = (index, temporaryPause = true) => {
  const total = bannersNormalized.value.length;
  if (!total) return;

  currentBanner.value = Math.max(0, Math.min(index, total - 1));

  if (temporaryPause) {
    paused.value = true;
    clearTimeout(pauseTimeout);

    pauseTimeout = setTimeout(() => {
      if (!document.hidden && !dialogData.value.visible && !manageModeActive.value) {
        paused.value = false;
      }
    }, TEMPORARY_PAUSE_MS);
  }
};

const startCarousel = () => {
  stopCarousel();

  if (bannersNormalized.value.length <= 1) return;

  carouselTimer = setInterval(() => {
    if (paused.value || bannersNormalized.value.length <= 1) return;
    moveToBanner((currentBanner.value + 1) % bannersNormalized.value.length, false);
  }, cycleMs);
};

const pauseCarousel = () => {
  paused.value = true;
};

const resumeCarousel = () => {
  if (!document.hidden && !dialogData.value.visible && !manageModeActive.value) {
    paused.value = false;
  }
};

const goTo = (index) => {
  moveToBanner(index, true);
};

const next = () => {
  const total = bannersNormalized.value.length;
  if (total <= 1) return;
  moveToBanner((currentBanner.value + 1) % total, true);
};

const prev = () => {
  const total = bannersNormalized.value.length;
  if (total <= 1) return;
  moveToBanner((currentBanner.value - 1 + total) % total, true);
};

const onVisibilityChange = () => {
  paused.value =
    document.hidden || dialogData.value.visible || manageModeActive.value;
};

const revokeAllPreviews = () => {
  previews.value.forEach((url) => URL.revokeObjectURL(url));
};

const setFiles = (selectedFiles) => {
  revokeAllPreviews();
  files.value = selectedFiles;
  previews.value = selectedFiles.map((file) => URL.createObjectURL(file));
};

const normalizePickedImages = (selectedFiles) => {
  const images = [];
  let invalidType = 0;
  let invalidSize = 0;

  for (const file of selectedFiles) {
    if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
      invalidType += 1;
      continue;
    }

    if (Number(file.size || 0) > MAX_BANNER_FILE_SIZE) {
      invalidSize += 1;
      continue;
    }

    images.push(file);
  }

  if (invalidType > 0 && invalidSize > 0) {
    setPanelError(
      "Algunos archivos fueron rechazados. Solo se admiten imágenes JPG o PNG y cada banner debe pesar máximo 2 MB."
    );
  } else if (invalidType > 0) {
    setPanelError("Solo se admiten imágenes en formato JPG o PNG.");
  } else if (invalidSize > 0) {
    setPanelError("Cada banner debe pesar máximo 2 MB.");
  } else {
    clearPanelError();
  }

  return images;
};

const preloadImage = (src) => {
  return new Promise((resolve) => {
    if (!src || preloadedSources.has(src)) {
      resolve();
      return;
    }

    let settled = false;

    const finish = () => {
      if (settled) return;
      settled = true;
      preloadedSources.add(src);
      resolve();
    };

    const img = new Image();

    img.onload = async () => {
      try {
        if (typeof img.decode === "function") {
          await img.decode();
        }
      } catch {
        //
      }
      finish();
    };

    img.onerror = finish;
    img.src = src;

    if (img.complete) {
      Promise.resolve().finally(finish);
    }
  });
};

const prefetchNeighborBanners = (index) => {
  const list = bannersNormalized.value;
  if (!list.length) return;

  const current = list[index];
  const nextBanner = list[(index + 1) % list.length];
  const prevBanner = list[(index - 1 + list.length) % list.length];

  preloadImage(current?.image_url);
  preloadImage(nextBanner?.image_url);

  if (list.length > 2) {
    preloadImage(prevBanner?.image_url);
  }
};

const openPicker = () => {
  if (!uploading.value && !deletingBulk.value) {
    fileInput.value?.click();
  }
};

const onFileChange = (event) => {
  const rawFiles = Array.from(event.target.files || []);
  const pickedImages = normalizePickedImages(rawFiles);
  setFiles(pickedImages);

  if (event?.target) {
    event.target.value = "";
  }
};

const onDragOver = (event) => {
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = "copy";
  }
};

const onDragEnter = () => {
  dragDepth.value += 1;
  dragging.value = true;
};

const onDragLeave = () => {
  dragDepth.value = Math.max(0, dragDepth.value - 1);
  if (dragDepth.value === 0) {
    dragging.value = false;
  }
};

const onDrop = (event) => {
  dragDepth.value = 0;
  dragging.value = false;

  const rawFiles = Array.from(event.dataTransfer?.files || []);
  const pickedImages = normalizePickedImages(rawFiles);

  if (pickedImages.length) {
    setFiles(pickedImages);
  }
};

const removeFileAt = (index) => {
  const nextFiles = [...files.value];
  nextFiles.splice(index, 1);
  setFiles(nextFiles);
};

const cargarBanners = async ({
  preserveActive = true,
  showLoading = true,
  preferredBannerId = null,
} = {}) => {
  const previousIndex = currentBanner.value;
  const previousActiveId =
    preferredBannerId ?? (preserveActive ? activeBannerItem.value?.id ?? null : null);
  const shouldShowLoading = showLoading || !heroReady.value;

  if (shouldShowLoading) {
    loading.value = true;
    heroReady.value = false;
  }

  loadError.value = "";

  try {
    const response = await api.get("banners/", {
      params: {
        _ts: Date.now(),
      },
    });

    const list = Array.isArray(response.data) ? response.data : [];
    banners.value = list;

    if (list.length) {
      let nextIndex = 0;

      if (previousActiveId) {
        const foundIndex = list.findIndex((item) => item.id === previousActiveId);
        if (foundIndex >= 0) {
          nextIndex = foundIndex;
        } else {
          nextIndex = Math.min(previousIndex, list.length - 1);
        }
      }

      currentBanner.value = nextIndex;
      await preloadImage(list[nextIndex]?.image_url);
      prefetchNeighborBanners(nextIndex);
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
    loadError.value = "No fue posible cargar los avisos en este momento.";
    heroReady.value = true;
    syncActiveBannerEditor();
  } finally {
    if (shouldShowLoading) {
      loading.value = false;
    }
  }
};

const subirBanners = async () => {
  if (!files.value.length || uploading.value || deletingBulk.value) return;

  uploading.value = true;
  clearPanelError();
  uploadIndex.value = 0;
  uploadTotal.value = files.value.length;

  const activeIdBeforeUpload = activeBannerItem.value?.id ?? null;
  let success = true;

  try {
    for (let i = 0; i < files.value.length; i += 1) {
      uploadIndex.value = i + 1;

      const form = new FormData();
      form.append("image", files.value[i]);

      await api.post("banners/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    }
  } catch (error) {
    console.error(error);
    success = false;
    setPanelError("No fue posible publicar los avisos. Intente nuevamente.");
  } finally {
    if (success) {
      setFiles([]);
    }

    await cargarBanners({
      preserveActive: true,
      showLoading: false,
      preferredBannerId: activeIdBeforeUpload,
    });

    if (success) {
      await requestVersionSync();
      setEditorStatus("Avisos publicados.");
    }

    uploading.value = false;
    uploadIndex.value = 0;
    uploadTotal.value = 0;
  }
};

const mostrarDialogoEliminar = ({ banner = null, count = 1 } = {}) => {
  const isBulk = count > 1;

  return new Promise((resolve) => {
    dialogData.value = {
      visible: true,
      titulo: isBulk ? "Eliminar avisos" : "Eliminar aviso",
      mensaje: isBulk
        ? `Se eliminarán ${count} avisos seleccionados.`
        : "Se eliminará el aviso seleccionado.",
      bannerImg: banner?.image_url || "",
      count,
      resolve,
    };
  });
};

const cerrarDialogo = (confirmado) => {
  if (typeof dialogData.value.resolve === "function") {
    dialogData.value.resolve(confirmado);
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
  const banner = bannersNormalized.value.find((item) => item.id === id);
  const confirmado = await mostrarDialogoEliminar({ banner, count: 1 });
  if (!confirmado) return;

  deletingId.value = id;
  clearPanelError();

  const currentActiveId = activeBannerItem.value?.id ?? null;
  const preferredBannerId = currentActiveId === id ? null : currentActiveId;

  try {
    await api.delete(`banners/${id}/`);
    selectedBannerIds.value = selectedBannerIds.value.filter((item) => item !== id);

    await cargarBanners({
      preserveActive: true,
      showLoading: false,
      preferredBannerId,
    });

    setEditorStatus("Aviso eliminado.");
  } catch (error) {
    console.error(error);
    setPanelError("No fue posible eliminar el aviso seleccionado.");
  } finally {
    deletingId.value = null;
  }
};

const eliminarSeleccionados = async () => {
  if (!selectedBannerIds.value.length || deletingBulk.value || uploading.value) return;

  const ids = [...selectedBannerIds.value];
  const confirmado = await mostrarDialogoEliminar({ count: ids.length });
  if (!confirmado) return;

  deletingBulk.value = true;
  bulkDeleteProgress.value = 0;
  bulkDeleteTotal.value = ids.length;
  clearPanelError();

  const currentActiveId = activeBannerItem.value?.id ?? null;
  const preferredBannerId = ids.includes(currentActiveId) ? null : currentActiveId;

  let failed = 0;

  try {
    for (let i = 0; i < ids.length; i += 1) {
      bulkDeleteProgress.value = i + 1;

      try {
        await api.delete(`banners/${ids[i]}/`);
      } catch {
        failed += 1;
      }
    }

    if (failed > 0) {
      setPanelError(
        failed === ids.length
          ? "No fue posible eliminar los avisos seleccionados."
          : `Se eliminaron algunos avisos, pero ${failed} no pudieron eliminarse.`
      );
    }

    selectedBannerIds.value = [];

    await cargarBanners({
      preserveActive: true,
      showLoading: false,
      preferredBannerId,
    });

    if (failed === 0) {
      setEditorStatus("Avisos eliminados.");
    }
  } finally {
    deletingBulk.value = false;
    bulkDeleteProgress.value = 0;
    bulkDeleteTotal.value = 0;
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

const getModalFocusableElements = () => {
  const root = modalCard.value;
  if (!root) return [];

  return [...root.querySelectorAll(FOCUSABLE_SELECTOR)].filter((element) => {
    return !element.hasAttribute("disabled") && !element.getAttribute("aria-hidden");
  });
};

const trapFocusInModal = (event) => {
  if (event.key !== "Tab") return;

  const focusable = getModalFocusableElements();
  if (!focusable.length) {
    event.preventDefault();
    return;
  }

  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  const active = document.activeElement;

  if (event.shiftKey && active === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && active === last) {
    event.preventDefault();
    first.focus();
  }
};

const isEditableTarget = (target) => {
  if (!(target instanceof HTMLElement)) return false;
  return !!target.closest("input, textarea, [contenteditable='true']");
};

const onGlobalKeydown = (event) => {
  if (dialogData.value.visible) {
    if (event.key === "Escape") {
      event.preventDefault();
      cerrarDialogo(false);
      return;
    }

    trapFocusInModal(event);
    return;
  }

  if (event.key === "Escape") {
    if (manageModeActive.value && isEditableTarget(event.target)) {
      return;
    }

    event.preventDefault();
    handleContinue();
  }
};

const stopLayoutInteraction = () => {
  if (!activeLayoutInteraction) return;

  window.removeEventListener("pointermove", onLayoutPointerMove);
  window.removeEventListener("pointerup", stopLayoutInteraction);
  activeLayoutInteraction = null;
};

const startContainerResize = (direction, event) => {
  if (!showContainerResizeHandles.value) return;
  if (event.button !== undefined && event.button !== 0) return;

  activeLayoutInteraction = {
    type: "container",
    direction,
    startX: event.clientX,
    startY: event.clientY,
    width: stageWidth.value,
    height: stageHeight.value,
  };

  window.addEventListener("pointermove", onLayoutPointerMove);
  window.addEventListener("pointerup", stopLayoutInteraction);
};

const startPaneResize = (event) => {
  if (!showContainerResizeHandles.value || !isMixedMode.value) return;
  if (event.button !== undefined && event.button !== 0) return;

  activeLayoutInteraction = {
    type: "divider",
    startX: event.clientX,
    mediaWidth: mediaPaneWidth.value,
  };

  window.addEventListener("pointermove", onLayoutPointerMove);
  window.addEventListener("pointerup", stopLayoutInteraction);
};

const onLayoutPointerMove = (event) => {
  if (!activeLayoutInteraction) return;

  if (activeLayoutInteraction.type === "container") {
    const dx = event.clientX - activeLayoutInteraction.startX;
    const dy = event.clientY - activeLayoutInteraction.startY;

    const isEast = activeLayoutInteraction.direction.includes("e");
    const isWest = activeLayoutInteraction.direction.includes("w");
    const isNorth = activeLayoutInteraction.direction.includes("n");
    const isSouth = activeLayoutInteraction.direction.includes("s");

    const nextWidth = sanitizeStageWidth(
      activeLayoutInteraction.width + (isEast ? dx : 0) - (isWest ? dx : 0)
    );

    const nextHeight = sanitizeStageHeight(
      activeLayoutInteraction.height + (isSouth ? dy : 0) - (isNorth ? dy : 0)
    );

    stageWidth.value = nextWidth;
    stageHeight.value = nextHeight;

    if (isMixedMode.value) {
      mediaPaneWidth.value = sanitizeMediaWidth(mediaPaneWidth.value, nextWidth);
    }

    return;
  }

  if (activeLayoutInteraction.type === "divider" && isMixedMode.value) {
    const dx = event.clientX - activeLayoutInteraction.startX;
    mediaPaneWidth.value = sanitizeMediaWidth(
      activeLayoutInteraction.mediaWidth + dx,
      stageWidth.value
    );
  }
};

const getResizeAriaLabel = (direction) => {
  const labels = {
    n: "Redimensionar contenedor desde borde superior",
    e: "Redimensionar contenedor desde borde derecho",
    s: "Redimensionar contenedor desde borde inferior",
    w: "Redimensionar contenedor desde borde izquierdo",
    nw: "Redimensionar contenedor desde esquina superior izquierda",
    ne: "Redimensionar contenedor desde esquina superior derecha",
    sw: "Redimensionar contenedor desde esquina inferior izquierda",
    se: "Redimensionar contenedor desde esquina inferior derecha",
  };

  return labels[direction] || "Redimensionar contenedor";
};

watch(
  () => props.user,
  (value) => {
    usuario.value = value || null;
  },
  { immediate: true, deep: true }
);

watch(
  () => props.version,
  async (nextVersion, prevVersion) => {
    const next = String(nextVersion || "");
    const prev = String(prevVersion || "");

    if (!next || next === prev) return;
    await refreshRemoteStateFromVersion();
  }
);

watch(
  () => manageModeActive.value,
  async (active) => {
    paused.value = active || document.hidden || dialogData.value.visible;
    syncActiveBannerEditor();

    if (!active) {
      stopLayoutInteraction();

      if (!document.hidden && !dialogData.value.visible) {
        paused.value = false;
      }

      if (pendingRemoteVersionSync.value) {
        await requestVersionSync({ force: true });
      }
    }
  },
  { immediate: true }
);

watch(
  () => isCompactScreen.value,
  (compact) => {
    if (compact) {
      stopLayoutInteraction();
    }
  }
);

watch(
  () => stageWidth.value,
  (width) => {
    if (isMixedMode.value) {
      mediaPaneWidth.value = sanitizeMediaWidth(mediaPaneWidth.value, width);
    }
  }
);

watch(
  () => bannersNormalized.value.length,
  (length) => {
    if (!length) {
      currentBanner.value = 0;
      stopCarousel();
      syncActiveBannerEditor();
      return;
    }

    currentBanner.value = Math.min(currentBanner.value, length - 1);

    if (length > 1) {
      startCarousel();
    } else {
      stopCarousel();
    }
  },
  { immediate: true }
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
  { deep: true, immediate: true }
);

watch(
  () => dialogData.value.visible,
  async (visible) => {
    if (visible) {
      lastFocusedElement =
        document.activeElement instanceof HTMLElement ? document.activeElement : null;

      paused.value = true;

      await nextTick();
      modalCard.value?.focus?.();
      return;
    }

    if (lastFocusedElement?.focus) {
      lastFocusedElement.focus();
    }

    lastFocusedElement = null;

    if (!document.hidden && !manageModeActive.value) {
      paused.value = false;
    }
  }
);

onMounted(async () => {
  updateCompactScreen();

  document.addEventListener("visibilitychange", onVisibilityChange);
  window.addEventListener("keydown", onGlobalKeydown);
  window.addEventListener("resize", updateCompactScreen);

  const token = localStorage.getItem("access_token");

  const profilePromise = props.user
    ? Promise.resolve().then(() => {
        usuario.value = props.user;
      })
    : token
      ? api
          .get("auth/profile/")
          .then((response) => {
            usuario.value = response.data;
          })
          .catch(() => {
            usuario.value = null;
          })
      : Promise.resolve().then(() => {
          usuario.value = null;
        });

  const layout = getAvisosLayout();

  stageWidth.value = sanitizeStageWidth(layout.stageWidth);
  stageHeight.value = sanitizeStageHeight(layout.stageHeight);
  mediaPaneWidth.value = sanitizeMediaWidth(layout.mediaPaneWidth, stageWidth.value);
  displayMode.value = sanitizeDisplayMode(layout.displayMode);

  syncPersistedLayout({
    stageWidth: stageWidth.value,
    stageHeight: stageHeight.value,
    mediaPaneWidth: mediaPaneWidth.value,
    displayMode: displayMode.value,
  });

  await Promise.allSettled([profilePromise, loadRemoteConfig(), cargarBanners()]);
  syncActiveBannerEditor();

  if (props.initialManage && isAdmin.value) {
    panelAbierto.value = true;
  }
});

onUnmounted(() => {
  stopCarousel();
  stopLayoutInteraction();
  revokeAllPreviews();

  clearTimeout(pauseTimeout);
  clearTimeout(panelErrorTimeout);
  clearTimeout(editorStatusTimeout);

  document.removeEventListener("visibilitychange", onVisibilityChange);
  window.removeEventListener("keydown", onGlobalKeydown);
  window.removeEventListener("resize", updateCompactScreen);
});
</script>

<style scoped src="./banner-principal.css"></style>