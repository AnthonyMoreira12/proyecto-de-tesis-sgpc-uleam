<template>
  <section
    id="as-autores"
    class="as"
    aria-labelledby="as-autores-title"
    :aria-busy="loadingAutores ? 'true' : 'false'"
    :aria-describedby="props.error ? 'as-autores-error' : undefined"
  >
    <p
      class="as-sr-only as-live"
      aria-live="polite"
      aria-atomic="true"
    >
      {{ liveMessage }}
    </p>

    <!-- =====================================================
         CABECERA
    ====================================================== -->

    <div class="as-head surface-enter surface-enter--1">
      <div class="as-head-left">
        <div class="as-title-wrap">
          <p class="as-kicker">
            Autoría
          </p>

          <h3
            id="as-autores-title"
            class="as-title"
          >
            Autores
            <span
              class="req"
              aria-hidden="true"
            >
              *
            </span>
          </h3>

          <p class="as-subtitle">
            Seleccione los autores de la publicación y defina su orden
            bibliográfico.
          </p>
        </div>
      </div>

      <div class="as-head-right">
        <button
          ref="openPickerButton"
          type="button"
          class="as-btn as-btn-primary"
          :disabled="loadingAutores && !autores.length"
          :aria-busy="loadingAutores ? 'true' : 'false'"
          @click="openPicker()"
        >
          <span v-if="loadingAutores && !showPicker">
            Cargando...
          </span>

          <span v-else>
            {{
              selected.length
                ? "Gestionar autores"
                : "Seleccionar autor(es)"
            }}
          </span>
        </button>
      </div>
    </div>

    <!-- =====================================================
         ERRORES
    ====================================================== -->

    <p
      v-if="props.error"
      id="as-autores-error"
      class="as-alert as-alert-error surface-enter surface-enter--2"
      role="alert"
      aria-live="assertive"
    >
      {{ props.error }}
    </p>

    <div
      v-if="errorAutores"
      class="as-alert as-alert-error as-alert-row surface-enter surface-enter--2"
      role="alert"
    >
      <span>
        {{ errorAutores }}
      </span>

      <button
        type="button"
        class="as-btn as-btn-ghost as-btn-sm"
        :disabled="loadingAutores"
        @click="refreshAutores(true)"
      >
        Reintentar
      </button>
    </div>

    <Transition name="as-confirm">
      <p
        v-if="confirmationMessage"
        class="as-alert as-alert-success surface-enter surface-enter--2"
        role="status"
      >
        {{ confirmationMessage }}
      </p>
    </Transition>

    <!-- =====================================================
         AUTORES SELECCIONADOS
    ====================================================== -->

    <div class="as-body surface-enter surface-enter--2">
      <div
        v-if="!selected.length"
        class="as-empty"
      >
        <div class="as-empty-card">
          <div class="as-empty-title">
            Sin autores agregados
          </div>

          <div class="as-empty-text">
            Seleccione uno o varios autores para incluirlos en la publicación.
          </div>

          <div class="as-empty-actions">
            <button
              type="button"
              class="as-btn as-btn-primary as-btn-sm"
              @click="openPicker()"
            >
              Agregar autores
            </button>
          </div>
        </div>
      </div>

      <div
        v-else
        class="as-selected"
      >
        <div class="as-selected-bar">
          <div class="as-selected-bar__left">
            <span class="as-count">
              {{ selected.length }} autor(es) seleccionado(s)
            </span>

            <span class="as-helper">
              El orden indica la posición bibliográfica de cada autor.
            </span>
          </div>

          <div class="as-selected-bar__right">
            <button
              type="button"
              class="as-btn as-btn-ghost as-btn-sm"
              @click="openPicker()"
            >
              Añadir más
            </button>
          </div>
        </div>

        <!-- =================================================
             ORDEN BIBLIOGRÁFICO
        ================================================== -->

        <div class="as-section">
          <div class="as-section__head">
            <div class="as-section__title-wrap">
              <h4 class="as-section__title">
                Orden bibliográfico
              </h4>

              <p class="as-section__hint">
                Puede arrastrar los autores o utilizar los controles para
                cambiar su posición.
              </p>
            </div>

            <span class="as-section__meta">
              {{ selectedResolved.length }} autor(es)
            </span>
          </div>

          <div
            class="as-list-selected"
            role="list"
            aria-label="Autores seleccionados en orden bibliográfico"
          >
            <div
              v-for="(autor, index) in selectedResolved"
              :key="autorKey(autor, index)"
              class="as-row as-row--draggable"
              role="listitem"
              :class="{
                'as-row--dragging': draggedAuthorIndex === index,
                'as-row--dragover':
                  dragOverAuthorIndex === index &&
                  draggedAuthorIndex !== index,
              }"
              @dragover.prevent="onAuthorDragOver(index, $event)"
              @dragenter.prevent="onAuthorDragEnter(index)"
              @drop.prevent="onAuthorDrop(index, $event)"
            >
              <div class="as-row-main">
                <div class="as-row-topline">
                  <button
                    type="button"
                    class="as-drag-handle"
                    draggable="true"
                    :aria-label="`Arrastrar autor ${
                      autor.nombre_completo || 'Autor'
                    }`"
                    title="Arrastrar para reordenar"
                    @dragstart="onAuthorDragStart(index, $event)"
                    @dragend="onAuthorDragEnd()"
                  >
                    <span aria-hidden="true">
                      ⋮⋮
                    </span>
                  </button>

                  <span class="as-row-index">
                    #{{ autor.orden }}
                  </span>

                  <span class="as-status as-status--soft">
                    Orden bibliográfico {{ autor.orden }}
                  </span>
                </div>

                <div class="as-row-name">
                  {{ autor.nombre_completo || "Autor" }}
                </div>

                <div class="as-row-sub">
                  <span v-if="autor.identificacion">
                    Cédula / DNI: {{ autor.identificacion }}
                  </span>

                  <span v-else>
                    Sin Cédula / DNI
                  </span>

                  <span v-if="autor.correo_resuelto">
                    • {{ autor.correo_resuelto }}
                  </span>

                  <span v-if="autor.institucion">
                    • {{ autor.institucion }}
                  </span>
                </div>

                <div class="as-row-controls">
                  <label
                    class="as-field-inline"
                    :for="`as-order-${autor.autor_id}-${index}`"
                  >
                    <span class="as-field-inline__label">
                      Posición
                    </span>

                    <select
                      :id="`as-order-${autor.autor_id}-${index}`"
                      class="as-control-select as-control-select--order"
                      :value="autor.orden"
                      @change="
                        setAuthorOrder(
                          index,
                          $event.target.value
                        )
                      "
                    >
                      <option
                        v-for="n in authorOrderOptions"
                        :key="`author-order-${autor.autor_id}-${n}`"
                        :value="n"
                      >
                        {{ n }}
                      </option>
                    </select>
                  </label>
                </div>
              </div>

              <div class="as-row-actions">
                <button
                  type="button"
                  class="as-icon"
                  aria-label="Subir autor una posición"
                  title="Subir"
                  :disabled="index === 0"
                  @click="moveAuthorUp(index)"
                >
                  ▲
                </button>

                <button
                  type="button"
                  class="as-icon"
                  aria-label="Bajar autor una posición"
                  title="Bajar"
                  :disabled="index === selectedResolved.length - 1"
                  @click="moveAuthorDown(index)"
                >
                  ▼
                </button>

                <button
                  type="button"
                  class="as-icon as-icon-danger"
                  aria-label="Eliminar autor"
                  title="Eliminar"
                  @click="removeAuthor(index)"
                >
                  ✖
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- =====================================================
         MODAL SELECTOR
    ====================================================== -->

    <Teleport to="body">
      <Transition name="modal-fade">
        <div
          v-if="showPicker"
          class="as-modal-overlay"
          @click.self="closePicker()"
        >
          <div
            ref="pickerDialog"
            class="as-modal as-modal--picker"
            role="dialog"
            aria-modal="true"
            aria-labelledby="as-picker-title"
            aria-describedby="as-picker-sub"
          >
            <div class="as-modal-head">
              <div class="as-modal-head-copy">
                <p class="as-modal-kicker">
                  Selección
                </p>

                <h3
                  id="as-picker-title"
                  class="as-modal-title"
                >
                  Seleccionar autor(es)
                </h3>

                <p
                  id="as-picker-sub"
                  class="as-modal-sub"
                >
                  Busque por nombre, correo, Cédula/DNI, institución, ORCID, SENESCYT, Google Scholar o Scopus.
                </p>
              </div>

              <button
                type="button"
                class="as-icon"
                aria-label="Cerrar selector de autores"
                @click="closePicker()"
              >
                ✖
              </button>
            </div>

            <div class="as-modal-body">
              <div class="as-toolbar">
                <div class="as-search-field">
                  <label
                    class="as-sr-only"
                    for="as-search-input"
                  >
                    Buscar autor
                  </label>

                  <span
                    class="as-search-icon"
                    aria-hidden="true"
                  >
                    ⌕
                  </span>

                  <input
                    id="as-search-input"
                    ref="searchInput"
                    v-model.trim="search"
                    class="as-input as-input-search"
                    type="text"
                    placeholder="Nombre, correo, Cédula/DNI, ORCID, SENESCYT, Scholar o Scopus..."
                    autocomplete="off"
                    inputmode="search"
                  />

                  <button
                    v-if="search"
                    type="button"
                    class="as-search-clear"
                    aria-label="Limpiar búsqueda"
                    @click="clearSearch()"
                  >
                    ✕
                  </button>
                </div>

                <div class="as-toolbar-actions">
                  <span class="as-mini-count">
                    {{ selected.length }} seleccionado(s)
                  </span>

                  <button
                    v-if="search"
                    type="button"
                    class="as-btn as-btn-ghost as-btn-sm"
                    @click="clearSearch()"
                  >
                    Limpiar
                  </button>

                  <button
                    type="button"
                    class="as-btn as-btn-ghost as-btn-sm"
                    :disabled="loadingAutores"
                    @click="refreshAutores(true)"
                  >
                    Actualizar
                  </button>
                </div>
              </div>

              <!-- =============================================
                   ESTADOS DEL CATÁLOGO
              ============================================== -->

              <div
                v-if="loadingAutores && !autores.length"
                class="as-state-card"
              >
                <div class="as-state-card__title">
                  Cargando autores...
                </div>

                <div class="as-state-card__text">
                  Espere un momento mientras se consulta el catálogo.
                </div>
              </div>

              <div
                v-else-if="
                  !loadingAutores &&
                  filteredAutores.length === 0
                "
                class="as-state-card"
              >
                <div class="as-state-card__title">
                  Sin coincidencias
                </div>

                <div class="as-state-card__text">
                  <template v-if="search">
                    No hay resultados para "{{ search }}".
                  </template>

                  <template v-else>
                    No hay autores disponibles en el catálogo.
                  </template>
                </div>
              </div>

              <div
                v-else
                class="as-picker-results"
              >
                <!-- ===========================================
                     FAVORITOS
                ============================================ -->

                <div
                  v-if="favoriteAvailableAutores.length"
                  class="as-picker-group as-picker-group--favorites"
                >
                  <div class="as-picker-group__head">
                    <span class="as-picker-group__title">
                      Favoritos
                    </span>

                    <span class="as-picker-group__count">
                      {{ favoriteAvailableAutores.length }}
                    </span>
                  </div>

                  <div class="as-catalog">
                    <div
                      v-for="a in favoriteAvailableAutores"
                      :key="`fav-${a.id}`"
                      class="as-catalog-item"
                    >
                      <button
                        type="button"
                        class="as-catalog-select"
                        :disabled="isAlreadySelected(a.id)"
                        :aria-label="`Agregar autor ${
                          a.nombre_completo ||
                          `${a.nombres} ${a.apellidos}`
                        }`"
                        title="Agregar autor favorito"
                        @click="selectFromList(a)"
                      >
                        <div class="as-ci-main">
                          <div class="as-ci-name">
                            {{
                              a.nombre_completo ||
                              `${a.nombres} ${a.apellidos}`
                            }}
                          </div>

                          <div class="as-ci-sub">
                            <span v-if="a.identificacion">
                              Cédula / DNI: {{ a.identificacion }}
                            </span>

                            <span v-else>
                              Sin Cédula / DNI
                            </span>

                            <span v-if="a.correo_resuelto">
                              • {{ a.correo_resuelto }}
                            </span>

                            <span v-if="a.institucion">
                              • {{ a.institucion }}
                            </span>
                          </div>

                          <div
                            v-if="matchedAcademicIdentifier(a)"
                            class="as-ci-match"
                          >
                            {{ matchedAcademicIdentifier(a) }}
                          </div>
                        </div>
                      </button>

                      <div class="as-ci-right">
                        <button
                          type="button"
                          class="as-fav-btn is-on"
                          title="Quitar de favoritos"
                          aria-label="Quitar de favoritos"
                          @click.stop.prevent="toggleFavorito(a)"
                        >
                          ★
                        </button>

                        <button
                          type="button"
                          class="as-select-action"
                          :disabled="isAlreadySelected(a.id)"
                          @click="selectFromList(a)"
                        >
                          Seleccionar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ===========================================
                     DISPONIBLES
                ============================================ -->

                <div
                  v-if="nonFavoriteAvailableAutores.length"
                  class="as-picker-group"
                >
                  <div class="as-picker-group__head">
                    <span class="as-picker-group__title">
                      {{
                        search
                          ? "Coincidencias"
                          : "Autores disponibles"
                      }}
                    </span>

                    <span class="as-picker-group__count">
                      {{ nonFavoriteAvailableAutores.length }}
                    </span>
                  </div>

                  <div class="as-catalog">
                    <div
                      v-for="a in nonFavoriteAvailableAutores"
                      :key="a.id"
                      class="as-catalog-item"
                    >
                      <button
                        type="button"
                        class="as-catalog-select"
                        :disabled="isAlreadySelected(a.id)"
                        :aria-label="`Agregar autor ${
                          a.nombre_completo ||
                          `${a.nombres} ${a.apellidos}`
                        }`"
                        title="Agregar autor"
                        @click="selectFromList(a)"
                      >
                        <div class="as-ci-main">
                          <div class="as-ci-name">
                            {{
                              a.nombre_completo ||
                              `${a.nombres} ${a.apellidos}`
                            }}
                          </div>

                          <div class="as-ci-sub">
                            <span v-if="a.identificacion">
                              Cédula / DNI: {{ a.identificacion }}
                            </span>

                            <span v-else>
                              Sin Cédula / DNI
                            </span>

                            <span v-if="a.correo_resuelto">
                              • {{ a.correo_resuelto }}
                            </span>

                            <span v-if="a.institucion">
                              • {{ a.institucion }}
                            </span>
                          </div>

                          <div
                            v-if="matchedAcademicIdentifier(a)"
                            class="as-ci-match"
                          >
                            {{ matchedAcademicIdentifier(a) }}
                          </div>
                        </div>
                      </button>

                      <div class="as-ci-right">
                        <button
                          type="button"
                          class="as-fav-btn"
                          :class="{
                            'is-on': isFavorito(a.id),
                          }"
                          :title="
                            isFavorito(a.id)
                              ? 'Quitar de favoritos'
                              : 'Agregar a favoritos'
                          "
                          :aria-label="
                            isFavorito(a.id)
                              ? 'Quitar de favoritos'
                              : 'Agregar a favoritos'
                          "
                          @click.stop.prevent="toggleFavorito(a)"
                        >
                          ★
                        </button>

                        <button
                          type="button"
                          class="as-select-action"
                          :disabled="isAlreadySelected(a.id)"
                          @click="selectFromList(a)"
                        >
                          Seleccionar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ===========================================
                     YA AGREGADOS
                ============================================ -->

                <div
                  v-if="alreadyAddedAutores.length"
                  class="as-picker-group as-picker-group--selected"
                >
                  <div class="as-picker-group__head">
                    <span class="as-picker-group__title">
                      Ya agregados
                    </span>

                    <span class="as-picker-group__count">
                      {{ alreadyAddedAutores.length }}
                    </span>
                  </div>

                  <div class="as-catalog as-catalog--compact">
                    <div
                      v-for="a in alreadyAddedAutores"
                      :key="`selected-${a.id}`"
                      class="as-catalog-item as-catalog-item--disabled"
                    >
                      <div class="as-catalog-static">
                        <div class="as-ci-main">
                          <div class="as-ci-name">
                            {{
                              a.nombre_completo ||
                              `${a.nombres} ${a.apellidos}`
                            }}
                          </div>

                          <div class="as-ci-sub">
                            <span v-if="a.identificacion">
                              Cédula / DNI: {{ a.identificacion }}
                            </span>

                            <span v-else>
                              Sin Cédula / DNI
                            </span>

                            <span v-if="a.correo_resuelto">
                              • {{ a.correo_resuelto }}
                            </span>

                            <span v-if="a.institucion">
                              • {{ a.institucion }}
                            </span>
                          </div>

                          <div
                            v-if="matchedAcademicIdentifier(a)"
                            class="as-ci-match"
                          >
                            {{ matchedAcademicIdentifier(a) }}
                          </div>
                        </div>
                      </div>

                      <div class="as-ci-right">
                        <button
                          type="button"
                          class="as-fav-btn"
                          :class="{
                            'is-on': isFavorito(a.id),
                          }"
                          :title="
                            isFavorito(a.id)
                              ? 'Quitar de favoritos'
                              : 'Agregar a favoritos'
                          "
                          :aria-label="
                            isFavorito(a.id)
                              ? 'Quitar de favoritos'
                              : 'Agregar a favoritos'
                          "
                          @click.stop.prevent="toggleFavorito(a)"
                        >
                          ★
                        </button>

                        <span class="as-badge as-badge-ok">
                          Agregado
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="as-modal-foot">
              <button
                type="button"
                class="as-btn as-btn-secondary"
                @click="openCreate()"
              >
                Agregar nuevo autor
              </button>

              <button
                type="button"
                class="as-btn"
                @click="closePicker()"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- =====================================================
         MODAL NUEVO AUTOR
    ====================================================== -->

    <Teleport to="body">
      <Transition name="modal-fade">
        <div
          v-if="showCreate"
          class="as-modal-overlay"
          @click.self="closeCreate()"
        >
          <div
            ref="createDialog"
            class="as-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="as-create-title"
            aria-describedby="as-create-sub"
          >
            <div class="as-modal-head">
              <div class="as-modal-head-copy">
                <p class="as-modal-kicker">
                  Registro
                </p>

                <h3
                  id="as-create-title"
                  class="as-modal-title"
                >
                  Agregar nuevo autor
                </h3>

                <p
                  id="as-create-sub"
                  class="as-modal-sub"
                >
                  Complete los datos para registrar un autor externo.
                  Al guardar, se creará y vinculará una cuenta local
                  <b>pendiente</b>. El autor podrá participar en publicaciones
                  aunque todavía no tenga acceso al sistema.
                </p>
              </div>

              <button
                type="button"
                class="as-icon"
                aria-label="Cerrar formulario de autor"
                :disabled="creating"
                @click="closeCreate()"
              >
                ✖
              </button>
            </div>

            <form
              class="as-create-form"
              @submit.prevent="createAutor"
            >
              <div class="as-modal-body">
                <p
                  v-if="createError"
                  class="as-alert as-alert-error"
                  role="alert"
                >
                  {{ createError }}
                </p>

                <!-- ===========================================
                     COINCIDENCIAS DE AUTOR
                ============================================ -->

                <div
                  v-if="duplicateExists && duplicateAutor"
                  class="as-alert"
                  :class="duplicateAlertClass"
                  role="alert"
                >
                  <div class="as-alert-stack">
                    <span>
                      {{ duplicateMessage }}
                      <b>
                        {{ duplicateAutor.nombre_completo }}
                      </b>.
                    </span>

                    <span class="as-alert-sub">
                      {{ duplicateHelperMessage }}
                    </span>

                    <div class="as-inline-actions">
                      <button
                        type="button"
                        class="as-btn as-btn-sm as-btn-secondary"
                        @click="useDuplicateAutor()"
                      >
                        {{ duplicateActionLabel }}
                      </button>
                    </div>
                  </div>
                </div>

                <p
                  v-else-if="checkingDuplicate"
                  class="as-help as-help--muted"
                  aria-live="polite"
                >
                  Verificando si el autor ya existe en la base de datos...
                </p>

                <!-- ===========================================
                     FORMULARIO
                ============================================ -->

                <div class="as-grid">
                  <!-- Cédula / DNI opcional -->

                  <div
                    class="as-field"
                    :class="{
                      'as-field--invalid':
                        !!createFieldErrors.identificacion,
                    }"
                  >
                    <label
                      class="as-field-label"
                      for="nuevo-identificacion"
                    >
                      Cédula / DNI
                      <span class="as-field-optional">
                        (opcional)
                      </span>
                    </label>

                    <input
                      id="nuevo-identificacion"
                      v-model="nuevo.identificacion"
                      class="as-input"
                      type="text"
                      :maxlength="AUTHOR_FIELD_LIMITS.identificacion"
                      placeholder="Documento de identificación"
                      autocomplete="off"
                      :aria-invalid="
                        createFieldErrors.identificacion
                          ? 'true'
                          : 'false'
                      "
                      :aria-describedby="
                        createFieldErrors.identificacion
                          ? 'nuevo-identificacion-error'
                          : 'nuevo-identificacion-help'
                      "
                      @input="normalizeIdentificationInput"
                      @blur="touchCreateField('identificacion')"
                    />

                    <p
                      id="nuevo-identificacion-help"
                      class="as-hint"
                    >
                      Opcional para investigadores externos. Puede registrar una
                      cédula, DNI u otro documento equivalente.
                    </p>

                    <p
                      v-if="createFieldErrors.identificacion"
                      id="nuevo-identificacion-error"
                      class="as-field-error"
                    >
                      {{ createFieldErrors.identificacion }}
                    </p>
                  </div>

                  <!-- Correo -->

                  <div
                    class="as-field"
                    :class="{
                      'as-field--invalid':
                        !!createFieldErrors.correo,
                    }"
                  >
                    <label
                      class="as-field-label"
                      for="nuevo-correo"
                    >
                      Correo
                      <span
                        class="req"
                        aria-hidden="true"
                      >
                        *
                      </span>
                    </label>

                    <input
                      id="nuevo-correo"
                      v-model.trim="nuevo.correo"
                      class="as-input"
                      type="email"
                      required
                      maxlength="150"
                      placeholder="correo@ejemplo.com"
                      autocomplete="off"
                      :aria-invalid="
                        createFieldErrors.correo
                          ? 'true'
                          : 'false'
                      "
                      :aria-describedby="
                        createFieldErrors.correo
                          ? 'nuevo-correo-error'
                          : 'nuevo-correo-help'
                      "
                      @blur="touchCreateField('correo')"
                    />

                    <p
                      id="nuevo-correo-help"
                      class="as-hint"
                    >
                      Se usará para identificar y contactar al autor.
                    </p>

                    <p
                      v-if="createFieldErrors.correo"
                      id="nuevo-correo-error"
                      class="as-field-error"
                    >
                      {{ createFieldErrors.correo }}
                    </p>
                  </div>

                  <!-- Nombres -->

                  <div
                    class="as-field"
                    :class="{
                      'as-field--invalid':
                        !!createFieldErrors.nombres,
                    }"
                  >
                    <label
                      class="as-field-label"
                      for="nuevo-nombres"
                    >
                      Nombres
                      <span
                        class="req"
                        aria-hidden="true"
                      >
                        *
                      </span>
                    </label>

                    <input
                      id="nuevo-nombres"
                      v-model.trim="nuevo.nombres"
                      class="as-input"
                      type="text"
                      required
                      maxlength="100"
                      placeholder="Ej. María"
                      autocomplete="off"
                      :aria-invalid="
                        createFieldErrors.nombres
                          ? 'true'
                          : 'false'
                      "
                      :aria-describedby="
                        createFieldErrors.nombres
                          ? 'nuevo-nombres-error'
                          : undefined
                      "
                      @blur="touchCreateField('nombres')"
                    />

                    <p
                      v-if="createFieldErrors.nombres"
                      id="nuevo-nombres-error"
                      class="as-field-error"
                    >
                      {{ createFieldErrors.nombres }}
                    </p>
                  </div>

                  <!-- Apellidos -->

                  <div
                    class="as-field"
                    :class="{
                      'as-field--invalid':
                        !!createFieldErrors.apellidos,
                    }"
                  >
                    <label
                      class="as-field-label"
                      for="nuevo-apellidos"
                    >
                      Apellidos
                      <span
                        class="req"
                        aria-hidden="true"
                      >
                        *
                      </span>
                    </label>

                    <input
                      id="nuevo-apellidos"
                      v-model.trim="nuevo.apellidos"
                      class="as-input"
                      type="text"
                      required
                      maxlength="100"
                      placeholder="Ej. Pérez"
                      autocomplete="off"
                      :aria-invalid="
                        createFieldErrors.apellidos
                          ? 'true'
                          : 'false'
                      "
                      :aria-describedby="
                        createFieldErrors.apellidos
                          ? 'nuevo-apellidos-error'
                          : undefined
                      "
                      @blur="touchCreateField('apellidos')"
                    />

                    <p
                      v-if="createFieldErrors.apellidos"
                      id="nuevo-apellidos-error"
                      class="as-field-error"
                    >
                      {{ createFieldErrors.apellidos }}
                    </p>
                  </div>

                  <!-- Institución -->

                  <div
                    class="as-field as-field--wide"
                    :class="{
                      'as-field--invalid':
                        !!createFieldErrors.institucion,
                    }"
                  >
                    <label
                      class="as-field-label"
                      for="nuevo-institucion"
                    >
                      Institución
                    </label>

                    <input
                      id="nuevo-institucion"
                      v-model.trim="nuevo.institucion"
                      class="as-input"
                      type="text"
                      maxlength="255"
                      placeholder="Ej. Universidad Laica Eloy Alfaro de Manabí"
                      autocomplete="organization"
                      :aria-invalid="
                        createFieldErrors.institucion
                          ? 'true'
                          : 'false'
                      "
                      :aria-describedby="
                        createFieldErrors.institucion
                          ? 'nuevo-institucion-error'
                          : 'nuevo-institucion-help'
                      "
                      @blur="touchCreateField('institucion')"
                    />

                    <p
                      id="nuevo-institucion-help"
                      class="as-hint"
                    >
                      Puede escribir manualmente la institución o dejarla
                      vacía.
                    </p>

                    <p
                      v-if="createFieldErrors.institucion"
                      id="nuevo-institucion-error"
                      class="as-field-error"
                    >
                      {{ createFieldErrors.institucion }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="as-modal-foot">
                <button
                  type="submit"
                  class="as-btn as-btn-primary"
                  :disabled="createDisabled"
                >
                  <span v-if="creating">
                    Guardando...
                  </span>

                  <span v-else>
                    Guardar y agregar
                  </span>
                </button>

                <button
                  type="button"
                  class="as-btn"
                  :disabled="creating"
                  @click="closeCreate()"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
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

import api from "../../scripts/api/axios";


defineOptions({
  name: "AutoresSelector",
});


/* =========================================================
   PROPS / EMITS
========================================================= */

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },

  error: {
    type: String,
    default: "",
  },
});


const emit = defineEmits([
  "update:modelValue",
]);


/* =========================================================
   ESTADO GENERAL
========================================================= */

const selected = ref([]);
const autores = ref([]);
const remoteSearchAutores = ref([]);
const remoteSearchTerm = ref("");

const loadingAutores = ref(false);
const errorAutores = ref("");

const liveMessage = ref("");
const confirmationMessage = ref("");


/* =========================================================
   MODALES
========================================================= */

const modalState = ref(null);

const returnToPickerAfterCreate =
  ref(false);

const search = ref("");

const searchInput = ref(null);
const pickerDialog = ref(null);
const createDialog = ref(null);
const openPickerButton = ref(null);

const lastFocusedElement = ref(null);


/* =========================================================
   CREACIÓN DE AUTOR
========================================================= */

const creating = ref(false);
const createError = ref("");

const checkingDuplicate = ref(false);

const duplicateResult = ref({
  exists: false,
  match_type: null,
  blocking: false,
  warning_only: false,
  input_incomplete: false,
  message: null,
  autor: null,
});


const createTouched = ref({
  identificacion: false,
  correo: false,
  nombres: false,
  apellidos: false,
  institucion: false,
});


const createFieldErrors = ref({
  identificacion: "",
  correo: "",
  nombres: "",
  apellidos: "",
  institucion: "",
});


const nuevo = ref({
  identificacion: "",
  nombres: "",
  apellidos: "",
  correo: "",
  institucion: "",
});


/* =========================================================
   DRAG & DROP
========================================================= */

const draggedAuthorIndex =
  ref(null);

const dragOverAuthorIndex =
  ref(null);


/* =========================================================
   CONFIGURACIÓN
========================================================= */

const emailRegex =
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


const CATALOG_TTL_MS =
  2 * 60 * 1000;

const AUTHOR_SEARCH_DEBOUNCE_MS = 250;
const AUTHOR_SEARCH_LIMIT = 100;


const AUTHOR_FIELD_LIMITS =
  Object.freeze({
    identificacion: 50,
    nombres: 100,
    apellidos: 100,
    correo: 150,
    institucion: 255,
  });


let refreshReq = 0;
let searchReq = 0;
let duplicateReq = 0;

let searchTimer = null;
let duplicateTimer = null;
let announcementTimer = null;
let confirmationTimer = null;

const lastCatalogLoadedAt =
  ref(0);


/* =========================================================
   MODAL STATE
========================================================= */

const showPicker = computed(
  () =>
    modalState.value ===
    "picker"
);


const showCreate = computed(
  () =>
    modalState.value ===
    "create"
);


/* =========================================================
   NOTIFICACIONES
========================================================= */

const announce = (message) => {
  if (announcementTimer) {
    window.clearTimeout(
      announcementTimer
    );

    announcementTimer =
      null;
  }

  liveMessage.value = "";

  nextTick(() => {
    liveMessage.value =
      message;

    announcementTimer =
      window.setTimeout(
        () => {
          liveMessage.value =
            "";
        },
        1400
      );
  });
};


const showConfirmation = (
  message
) => {
  if (confirmationTimer) {
    window.clearTimeout(
      confirmationTimer
    );

    confirmationTimer =
      null;
  }

  confirmationMessage.value =
    message;

  confirmationTimer =
    window.setTimeout(
      () => {
        confirmationMessage.value =
          "";
      },
      2800
    );
};


const notifyAuthorAction = (
  message
) => {
  announce(message);
  showConfirmation(message);
};


/* =========================================================
   NORMALIZACIÓN BÁSICA
========================================================= */

const normalizeText = (
  value
) =>
  String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(
      /[\u0300-\u036f]/g,
      ""
    )
    .replace(/\s+/g, " ")
    .trim();


const cleanEmail = (
  value
) =>
  String(value ?? "")
    .trim()
    .toLowerCase();


const cleanExternalIdentification = (
  value
) =>
  String(value ?? "")
    .replace(/[\r\n\t]/g, " ")
    .replace(/\s+/g, " ")
    .trim();


const normalizeIdentificationInput =
  () => {
    const current =
      String(
        nuevo.value.identificacion ??
        ""
      )
        .replace(/[\r\n\t]/g, " ")
        .replace(/\s{2,}/g, " ")
        .slice(
          0,
          AUTHOR_FIELD_LIMITS
            .identificacion
        );

    if (
      current !==
      nuevo.value.identificacion
    ) {
      nuevo.value.identificacion =
        current;
    }
  };


/* =========================================================
   FAVORITOS
========================================================= */

const getCurrentUserKey = () => {
  try {
    const rawUser =
      localStorage.getItem(
        "user"
      );

    const parsedUser =
      rawUser
        ? JSON.parse(rawUser)
        : null;

    const userId =
      parsedUser?.id ??
      parsedUser?.user_id ??
      localStorage.getItem(
        "autor_id"
      ) ??
      localStorage.getItem(
        "email"
      ) ??
      "guest";

    return (
      String(userId).trim() ||
      "guest"
    );
  } catch {
    return "guest";
  }
};


const FAV_KEY = computed(
  () =>
    `sgpc-autores-favoritos:${getCurrentUserKey()}`
);


const favoritos =
  ref(new Set());


const normalizeFavId = (
  id
) =>
  String(id ?? "").trim();


const loadFavoritos = () => {
  try {
    const raw =
      localStorage.getItem(
        FAV_KEY.value
      );

    const parsed =
      raw
        ? JSON.parse(raw)
        : [];

    favoritos.value =
      new Set(
        Array.isArray(parsed)
          ? parsed
              .map(
                (id) =>
                  normalizeFavId(
                    id
                  )
              )
              .filter(Boolean)
          : []
      );
  } catch {
    favoritos.value =
      new Set();
  }
};


const saveFavoritos = () => {
  try {
    localStorage.setItem(
      FAV_KEY.value,
      JSON.stringify([
        ...favoritos.value,
      ])
    );
  } catch {
    // No interrumpe el formulario.
  }
};


const isFavorito = (
  autorId
) =>
  favoritos.value.has(
    normalizeFavId(
      autorId
    )
  );


const toggleFavorito = (
  autor
) => {
  const id =
    normalizeFavId(
      autor?.id
    );

  if (!id) {
    return;
  }

  if (
    favoritos.value.has(id)
  ) {
    favoritos.value.delete(
      id
    );
  } else {
    favoritos.value.add(
      id
    );
  }

  favoritos.value =
    new Set(
      favoritos.value
    );

  saveFavoritos();

  announce(
    favoritos.value.has(id)
      ? "Autor agregado a favoritos."
      : "Autor quitado de favoritos."
  );
};


/* =========================================================
   HELPERS DE AUTOR
========================================================= */

const autorKey = (
  autor,
  index
) => {
  const id =
    autor?.autor_id ??
    autor?.id ??
    null;

  return id
    ? `autor-${id}`
    : `tmp-${
        autor?.nombre_completo ||
        "autor"
      }-${index}`;
};


const asArrayResponse = (
  data
) => {
  if (
    Array.isArray(data)
  ) {
    return data;
  }

  if (
    Array.isArray(
      data?.results
    )
  ) {
    return data.results;
  }

  if (
    Array.isArray(
      data?.data
    )
  ) {
    return data.data;
  }

  return [];
};


const compareAutores = (
  a,
  b
) => {
  const apellidosA =
    normalizeText(
      a?.apellidos ||
      ""
    );

  const apellidosB =
    normalizeText(
      b?.apellidos ||
      ""
    );

  if (
    apellidosA !==
    apellidosB
  ) {
    return apellidosA.localeCompare(
      apellidosB,
      "es",
      {
        sensitivity: "base",
      }
    );
  }

  const nombresA =
    normalizeText(
      a?.nombres ||
      ""
    );

  const nombresB =
    normalizeText(
      b?.nombres ||
      ""
    );

  if (
    nombresA !==
    nombresB
  ) {
    return nombresA.localeCompare(
      nombresB,
      "es",
      {
        sensitivity: "base",
      }
    );
  }

  const completoA =
    normalizeText(
      a?.nombre_completo ||
      ""
    );

  const completoB =
    normalizeText(
      b?.nombre_completo ||
      ""
    );

  return completoA.localeCompare(
    completoB,
    "es",
    {
      sensitivity: "base",
    }
  );
};


const dedupeById = (
  items = []
) => {
  const map =
    new Map();

  for (
    const item
    of items
  ) {
    const id =
      Number(
        item?.id
      );

    if (
      !Number.isFinite(id) ||
      id <= 0
    ) {
      continue;
    }

    map.set(
      String(id),
      item
    );
  }

  return [
    ...map.values(),
  ];
};


/* =========================================================
   NORMALIZACIÓN DEL CATÁLOGO
========================================================= */

const normalizeAutores = (
  raw
) => {
  return dedupeById(
    (raw || []).map(
      (a) => {
        const rawId =
          Number(
            a?.id ??
            a?.autor_id
          );

        const nombres =
          String(
            a?.nombres ??
            ""
          ).trim();

        const apellidos =
          String(
            a?.apellidos ??
            ""
          ).trim();

        const correoResuelto =
          cleanEmail(
            a?.correo_resuelto ??
            a?.correo
          );

        const institucion =
          String(
            a?.institucion ??
            ""
          ).trim() ||
          null;

        const nombreCompleto =
          (
            a?.nombre_completo ||
            a?.autor_nombre ||
            `${nombres} ${apellidos}`.trim()
          ).trim();

        const orcid =
          String(
            a?.orcid ??
            ""
          ).trim() || null;

        const registroSenescyt =
          String(
            a?.registro_senescyt ??
            ""
          ).trim() || null;

        const googleScholar =
          String(
            a?.google_scholar ??
            ""
          ).trim() || null;

        const scopusId =
          String(
            a?.scopus_id ??
            ""
          ).trim() || null;

        const searchBlob =
          normalizeText(
            [
              nombreCompleto,
              nombres,
              apellidos,
              a?.identificacion,
              correoResuelto,
              a?.correo,
              institucion,
              orcid,
              registroSenescyt,
              googleScholar,
              scopusId,
            ].join(" ")
          );

        return {
          ...a,

          id: rawId,

          nombres,
          apellidos,

          identificacion:
            String(
              a?.identificacion ??
              ""
            ).trim() ||
            null,

          correo:
            correoResuelto ||
            null,

          correo_resuelto:
            correoResuelto ||
            null,

          institucion,

          orcid,
          registro_senescyt:
            registroSenescyt,
          google_scholar:
            googleScholar,
          scopus_id:
            scopusId,

          nombre_completo:
            nombreCompleto ||
            "Autor",

          search_blob:
            searchBlob,
        };
      }
    )
  ).sort(
    compareAutores
  );
};


/* =========================================================
   NORMALIZACIÓN DE SELECCIONADOS
========================================================= */

const normalizeSelected = (
  arr
) => {
  const base =
    Array.isArray(arr)
      ? [...arr]
      : [];

  const clean =
    base
      .map(
        (
          item,
          originalIndex
        ) => {
          const nestedAutor =
            item?.autor &&
            typeof item.autor ===
              "object"
              ? item.autor
              : null;

          const id =
            Number(
              item?.autor_id ??
              nestedAutor?.id ??
              item?.id
            );

          if (
            !Number.isFinite(id) ||
            id <= 0
          ) {
            return null;
          }

          const rawOrder =
            Number(
              item?.orden
            );

          const nombreCompleto =
            String(
              item?.nombre_completo ||
              item?.autor_nombre ||
              item?.nombre ||
              item?.label ||
              nestedAutor
                ?.nombre_completo ||
              nestedAutor
                ?.autor_nombre ||
              `${
                nestedAutor?.nombres ||
                ""
              } ${
                nestedAutor?.apellidos ||
                ""
              }`.trim() ||
              ""
            ).trim();

          const identificacion =
            String(
              item?.identificacion ??
              nestedAutor
                ?.identificacion ??
              ""
            ).trim() ||
            null;

          const correoResuelto =
            cleanEmail(
              item?.correo_resuelto ??
              item?.correo ??
              nestedAutor
                ?.correo_resuelto ??
              nestedAutor?.correo ??
              ""
            ) ||
            null;

          const institucion =
            String(
              item?.institucion ??
              nestedAutor
                ?.institucion ??
              ""
            ).trim() ||
            null;

          return {
            autor_id:
              id,

            orden:
              (
                Number.isInteger(
                  rawOrder
                ) &&
                rawOrder > 0
              )
                ? rawOrder
                : originalIndex + 1,

            nombre_completo:
              nombreCompleto,

            identificacion,

            correo:
              correoResuelto,

            correo_resuelto:
              correoResuelto,

            institucion,

            _originalIndex:
              originalIndex,
          };
        }
      )
      .filter(Boolean);

  /*
   * Evita autores duplicados sin perder el primer registro
   * recibido para cada Autor.
   */
  const deduped = [];
  const seen = new Set();

  for (
    const item
    of clean
  ) {
    const key =
      String(
        item.autor_id
      );

    if (
      seen.has(key)
    ) {
      continue;
    }

    seen.add(key);
    deduped.push(item);
  }

  /*
   * Orden es exclusivamente bibliográfico.
   * Ante empates o valores heredados inválidos se conserva
   * el orden de entrada y luego se renumera 1..N.
   */
  deduped.sort(
    (a, b) =>
      (
        Number(a.orden) -
        Number(b.orden)
      ) ||
      (
        a._originalIndex -
        b._originalIndex
      )
  );

  return deduped.map(
    (
      item,
      index
    ) => {
      const {
        _originalIndex,
        ...cleanItem
      } = item;

      return {
        ...cleanItem,
        orden:
          index + 1,
      };
    }
  );
};

const emitNormalized = (
  arr
) => {
  const normalized =
    normalizeSelected(
      arr
    );

  selected.value =
    normalized;

  emit(
    "update:modelValue",
    normalized
  );
};


watch(
  () =>
    props.modelValue,

  (value) => {
    selected.value =
      normalizeSelected(
        value
      );
  },

  {
    immediate: true,
  }
);


/* =========================================================
   MAPA DEL CATÁLOGO
========================================================= */

const autoresMap =
  computed(() => {
    const map =
      new Map();

    for (
      const autor
      of autores.value
    ) {
      map.set(
        String(
          autor.id
        ),
        autor
      );
    }

    return map;
  });


const selectedResolved =
  computed(() =>
    selected.value.map(
      (item) => {
        const linked =
          autoresMap.value.get(
            String(
              item.autor_id
            )
          );

        return {
          ...item,

          nombre_completo:
            item.nombre_completo ||
            linked?.nombre_completo ||
            linked?.autor_nombre ||
            "Autor",

          identificacion:
            linked?.identificacion ||
            item?.identificacion ||
            null,

          correo_resuelto:
            linked?.correo_resuelto ||
            linked?.correo ||
            item?.correo_resuelto ||
            item?.correo ||
            null,

          institucion:
            linked?.institucion ||
            item?.institucion ||
            null,
        };
      }
    )
  );


/* =========================================================
   ORDEN BIBLIOGRÁFICO
========================================================= */

const selectedIds =
  computed(
    () =>
      new Set(
        selected.value.map(
          (item) =>
            String(
              item.autor_id
            )
        )
      )
  );


const isAlreadySelected = (
  autorId
) =>
  selectedIds.value.has(
    String(
      autorId
    )
  );


const authorOrderOptions =
  computed(
    () =>
      Array.from(
        {
          length:
            selectedResolved.value
              .length,
        },

        (_, index) =>
          index + 1
      )
  );


const emitOrderedAuthors = (
  items = []
) => {
  emitNormalized(
    items.map(
      (
        item,
        index
      ) => ({
        ...item,

        orden:
          index + 1,
      })
    )
  );
};


/* =========================================================
   CATÁLOGO DE AUTORES
========================================================= */

const shouldRefreshCatalog =
  () => {
    if (
      !autores.value.length
    ) {
      return true;
    }

    if (
      !lastCatalogLoadedAt
        .value
    ) {
      return true;
    }

    return (
      Date.now() -
        lastCatalogLoadedAt.value >
      CATALOG_TTL_MS
    );
  };


const refreshAutores =
  async (
    force = false
  ) => {
    if (
      !force &&
      !shouldRefreshCatalog()
    ) {
      return;
    }

    const reqId =
      ++refreshReq;

    loadingAutores.value =
      true;

    errorAutores.value =
      "";

    try {
      const response =
        await api.get(
          "/selects/autores/"
        );

      if (
        reqId !==
        refreshReq
      ) {
        return;
      }

      autores.value =
        normalizeAutores(
          asArrayResponse(
            response.data
          )
        );

      lastCatalogLoadedAt.value =
        Date.now();
    } catch (error) {
      if (
        reqId !==
        refreshReq
      ) {
        return;
      }

      errorAutores.value =
        "No se pudieron cargar los autores disponibles. Intente nuevamente.";

      console.warn(
        "Error cargando autores:",
        error
      );
    } finally {
      if (
        reqId ===
        refreshReq
      ) {
        loadingAutores.value =
          false;
      }
    }
  };


/* =========================================================
   BÚSQUEDA
========================================================= */

const searchAutoresRemote =
  async (rawTerm) => {
    const query =
      String(
        rawTerm ||
        ""
      ).trim();

    if (!query) {
      remoteSearchAutores.value = [];
      remoteSearchTerm.value = "";
      return;
    }

    const reqId =
      ++searchReq;

    loadingAutores.value = true;
    errorAutores.value = "";

    try {
      const response =
        await api.get(
          "/selects/autores/",
          {
            params: {
              q: query,
              limit:
                AUTHOR_SEARCH_LIMIT,
            },
          }
        );

      if (
        reqId !==
        searchReq
      ) {
        return;
      }

      remoteSearchAutores.value =
        normalizeAutores(
          asArrayResponse(
            response.data
          )
        );

      remoteSearchTerm.value =
        normalizeText(query);
    } catch (error) {
      if (
        reqId !==
        searchReq
      ) {
        return;
      }

      remoteSearchAutores.value = [];
      remoteSearchTerm.value =
        normalizeText(query);

      errorAutores.value =
        "No se pudo completar la búsqueda de autores. Intente nuevamente.";

      console.warn(
        "Error buscando autores:",
        error
      );
    } finally {
      if (
        reqId ===
        searchReq
      ) {
        loadingAutores.value = false;
      }
    }
  };


const scheduleAuthorSearch =
  (value) => {
    if (searchTimer) {
      window.clearTimeout(
        searchTimer
      );

      searchTimer = null;
    }

    const query =
      String(
        value ||
        ""
      ).trim();

    if (!query) {
      searchReq += 1;
      remoteSearchAutores.value = [];
      remoteSearchTerm.value = "";
      errorAutores.value = "";
      return;
    }

    searchTimer =
      window.setTimeout(
        () => {
          searchTimer = null;
          searchAutoresRemote(
            query
          );
        },
        AUTHOR_SEARCH_DEBOUNCE_MS
      );
  };


const filteredAutores =
  computed(() => {
    const term =
      normalizeText(
        search.value
      );

    if (!term) {
      return autores.value;
    }

    /*
     * Mientras responde el backend se conserva un resultado
     * local inmediato. Cuando llega la búsqueda remota se usa
     * el catálogo completo devuelto para esa consulta.
     */
    if (
      remoteSearchTerm.value ===
      term
    ) {
      return remoteSearchAutores.value;
    }

    return autores.value.filter(
      (autor) =>
        autor.search_blob.includes(
          term
        )
    );
  });


const matchedAcademicIdentifier =
  (autor) => {
    const term =
      normalizeText(
        search.value
      );

    if (!term) {
      return "";
    }

    const candidates = [
      [
        "ORCID",
        autor?.orcid,
      ],
      [
        "Registro SENESCYT",
        autor?.registro_senescyt,
      ],
      [
        "Google Scholar",
        autor?.google_scholar,
      ],
      [
        "Scopus ID",
        autor?.scopus_id,
      ],
    ];

    const match =
      candidates.find(
        ([, value]) =>
          value &&
          normalizeText(
            value
          ).includes(term)
      );

    if (!match) {
      return "";
    }

    return `${match[0]}: ${match[1]}`;
  };


const alreadyAddedAutores =
  computed(() =>
    filteredAutores.value.filter(
      (autor) =>
        isAlreadySelected(
          autor.id
        )
    )
  );


const availableAutores =
  computed(() =>
    filteredAutores.value.filter(
      (autor) =>
        !isAlreadySelected(
          autor.id
        )
    )
  );


const favoriteAvailableAutores =
  computed(() =>
    availableAutores.value.filter(
      (autor) =>
        isFavorito(
          autor.id
        )
    )
  );


const nonFavoriteAvailableAutores =
  computed(() =>
    availableAutores.value.filter(
      (autor) =>
        !isFavorito(
          autor.id
        )
    )
  );


const clearSearch =
  async () => {
    search.value = "";

    remoteSearchAutores.value = [];
    remoteSearchTerm.value = "";

    await nextTick();

    searchInput.value?.focus?.();
  };


/* =========================================================
   COINCIDENCIAS Y DUPLICADOS
========================================================= */

const duplicateAutor =
  computed(
    () =>
      duplicateResult.value
        ?.autor ||
      null
  );


const duplicateExists =
  computed(
    () =>
      Boolean(
        duplicateResult.value
          ?.exists
      )
  );


const duplicateMatchType =
  computed(() =>
    String(
      duplicateResult.value
        ?.match_type ||
      ""
    )
      .trim()
      .toLowerCase()
  );


const duplicateBlocking =
  computed(() => {
    const explicitValue =
      duplicateResult.value
        ?.blocking;

    if (
      typeof explicitValue ===
      "boolean"
    ) {
      return explicitValue;
    }

    return [
      "identificacion",
      "correo",
    ].includes(
      duplicateMatchType.value
    );
  });


const duplicateWarningOnly =
  computed(() => {
    const explicitValue =
      duplicateResult.value
        ?.warning_only;

    if (
      typeof explicitValue ===
      "boolean"
    ) {
      return explicitValue;
    }

    return (
      duplicateMatchType.value ===
      "nombre_apellido"
    );
  });


const duplicateAlertClass =
  computed(() =>
    duplicateBlocking.value
      ? "as-alert-error"
      : "as-alert-warning"
  );


const duplicateMessage =
  computed(() => {
    const backendMessage =
      String(
        duplicateResult.value
          ?.message ||
        ""
      ).trim();

    if (backendMessage) {
      return backendMessage;
    }

    if (
      duplicateMatchType.value ===
      "identificacion"
    ) {
      return (
        "Ya existe un autor registrado con esta Cédula / DNI:"
      );
    }

    if (
      duplicateMatchType.value ===
      "correo"
    ) {
      return (
        "Ya existe un autor registrado con este correo:"
      );
    }

    return (
      "Existe un autor con los mismos nombres y apellidos:"
    );
  });


const duplicateHelperMessage =
  computed(() => {
    if (duplicateBlocking.value) {
      return (
        "Debe usar el registro existente para evitar duplicar la misma persona."
      );
    }

    if (duplicateWarningOnly.value) {
      return (
        "Esta coincidencia es solo informativa. Puede usar el registro existente o continuar si se trata de otra persona."
      );
    }

    return (
      "Revise la coincidencia antes de continuar."
    );
  });


const duplicateActionLabel =
  computed(() =>
    duplicateBlocking.value
      ? "Usar autor existente"
      : "Usar esta coincidencia"
  );


const cancelDuplicateCheck =
  () => {
    duplicateReq += 1;

    if (searchTimer) {
      window.clearTimeout(
        searchTimer
      );

      searchTimer = null;
    }

    if (duplicateTimer) {
      window.clearTimeout(
        duplicateTimer
      );

      duplicateTimer =
        null;
    }

    checkingDuplicate.value =
      false;
  };


const resetDuplicateState =
  () => {
    cancelDuplicateCheck();

    duplicateResult.value = {
      exists: false,
      match_type: null,
      blocking: false,
      warning_only: false,
      input_incomplete: false,
      message: null,
      autor: null,
    };
  };


const shouldRunDuplicateCheck =
  () => {
    const identificacion =
      cleanExternalIdentification(
        nuevo.value
          .identificacion
      );

    const correo =
      cleanEmail(
        nuevo.value.correo
      );

    const nombres =
      normalizeText(
        nuevo.value.nombres
      );

    const apellidos =
      normalizeText(
        nuevo.value.apellidos
      );

    return Boolean(
      identificacion ||
      correo ||
      (
        nombres.length >= 2 &&
        apellidos.length >= 2
      )
    );
  };


const runDuplicateCheck =
  async () => {
    if (
      !showCreate.value
    ) {
      return;
    }

    if (
      !shouldRunDuplicateCheck()
    ) {
      resetDuplicateState();

      return;
    }

    const reqId =
      ++duplicateReq;

    checkingDuplicate.value =
      true;

    try {
      const response =
        await api.get(
          "/autores/validar-existencia/",
          {
            params: {
              identificacion:
                cleanExternalIdentification(
                  nuevo.value
                    .identificacion
                ) ||
                undefined,

              correo:
                cleanEmail(
                  nuevo.value
                    .correo
                ) ||
                undefined,

              nombres:
                (
                  nuevo.value
                    .nombres ||
                  ""
                ).trim() ||
                undefined,

              apellidos:
                (
                  nuevo.value
                    .apellidos ||
                  ""
                ).trim() ||
                undefined,
            },
          }
        );

      if (
        reqId !==
        duplicateReq
      ) {
        return;
      }

      const responseData =
        response?.data?.data ||
        response?.data ||
        {};

      duplicateResult.value = {
        exists:
          Boolean(
            responseData
              ?.exists
          ),

        match_type:
          responseData
            ?.match_type ||
          null,

        blocking:
          typeof responseData
            ?.blocking ===
          "boolean"
            ? responseData.blocking
            : [
                "identificacion",
                "correo",
              ].includes(
                String(
                  responseData
                    ?.match_type ||
                  ""
                )
                  .trim()
                  .toLowerCase()
              ),

        warning_only:
          typeof responseData
            ?.warning_only ===
          "boolean"
            ? responseData
                .warning_only
            : String(
                responseData
                  ?.match_type ||
                ""
              )
                .trim()
                .toLowerCase() ===
              "nombre_apellido",

        input_incomplete:
          Boolean(
            responseData
              ?.input_incomplete
          ),

        message:
          responseData
            ?.message ||
          null,

        autor:
          responseData?.autor ||
          null,
      };

      if (
        duplicateResult.value
          .exists
      ) {
        createError.value =
          "";
      }
    } catch (error) {
      if (
        reqId !==
        duplicateReq
      ) {
        return;
      }

      console.warn(
        "Error verificando duplicado de autor:",
        error
      );

      resetDuplicateState();
    } finally {
      if (
        reqId ===
        duplicateReq
      ) {
        checkingDuplicate.value =
          false;
      }
    }
  };


const scheduleDuplicateCheck =
  () => {
    if (duplicateTimer) {
      window.clearTimeout(
        duplicateTimer
      );

      duplicateTimer =
        null;
    }

    duplicateTimer =
      window.setTimeout(
        () => {
          runDuplicateCheck();
        },
        350
      );
  };


/* =========================================================
   VALIDACIÓN DE NUEVO AUTOR
========================================================= */

const resetCreateTouched =
  () => {
    createTouched.value = {
      identificacion: false,
      correo: false,
      nombres: false,
      apellidos: false,
      institucion: false,
    };
  };


const resetCreateErrors =
  () => {
    createFieldErrors.value = {
      identificacion: "",
      correo: "",
      nombres: "",
      apellidos: "",
      institucion: "",
    };
  };


const validateCreateField = (
  field
) => {
  const identificacion =
    cleanExternalIdentification(
      nuevo.value
        .identificacion
    );

  const correo =
    cleanEmail(
      nuevo.value.correo
    );

  const nombres =
    String(
      nuevo.value.nombres ||
      ""
    ).trim();

  const apellidos =
    String(
      nuevo.value.apellidos ||
      ""
    ).trim();

  const institucion =
    String(
      nuevo.value
        .institucion ||
      ""
    ).trim();

  switch (field) {
    case "identificacion":
      if (!identificacion) {
        return "";
      }

      if (
        identificacion.length >
        AUTHOR_FIELD_LIMITS
          .identificacion
      ) {
        return (
          `La Cédula / DNI no puede superar ${
            AUTHOR_FIELD_LIMITS
              .identificacion
          } caracteres.`
        );
      }

      return "";

    case "correo":
      if (!correo) {
        return (
          "El correo es obligatorio."
        );
      }

      if (
        correo.length >
        AUTHOR_FIELD_LIMITS
          .correo
      ) {
        return (
          `El correo no puede superar ${
            AUTHOR_FIELD_LIMITS
              .correo
          } caracteres.`
        );
      }

      if (
        !emailRegex.test(
          correo
        )
      ) {
        return (
          "El correo ingresado no es válido."
        );
      }

      return "";

    case "nombres":
      if (!nombres) {
        return (
          "Los nombres son obligatorios."
        );
      }

      if (
        nombres.length >
        AUTHOR_FIELD_LIMITS
          .nombres
      ) {
        return (
          `Los nombres no pueden superar ${
            AUTHOR_FIELD_LIMITS
              .nombres
          } caracteres.`
        );
      }

      return "";

    case "apellidos":
      if (!apellidos) {
        return (
          "Los apellidos son obligatorios."
        );
      }

      if (
        apellidos.length >
        AUTHOR_FIELD_LIMITS
          .apellidos
      ) {
        return (
          `Los apellidos no pueden superar ${
            AUTHOR_FIELD_LIMITS
              .apellidos
          } caracteres.`
        );
      }

      return "";

    case "institucion":
      if (
        institucion.length >
        AUTHOR_FIELD_LIMITS
          .institucion
      ) {
        return (
          `La institución no puede superar ${
            AUTHOR_FIELD_LIMITS
              .institucion
          } caracteres.`
        );
      }

      return "";

    default:
      return "";
  }
};


const validateTouchedFields =
  () => {
    for (
      const field
      of Object.keys(
        createTouched.value
      )
    ) {
      if (
        createTouched.value[
          field
        ]
      ) {
        createFieldErrors.value[
          field
        ] =
          validateCreateField(
            field
          );
      }
    }
  };


const touchCreateField = (
  field
) => {
  createTouched.value[
    field
  ] = true;

  createFieldErrors.value[
    field
  ] =
    validateCreateField(
      field
    );
};


const validateCreateForm =
  () => {
    createError.value =
      "";

    for (
      const field
      of Object.keys(
        createTouched.value
      )
    ) {
      createTouched.value[
        field
      ] = true;

      createFieldErrors.value[
        field
      ] =
        validateCreateField(
          field
        );
    }

    const hasFieldErrors =
      Object.values(
        createFieldErrors.value
      ).some(Boolean);

    if (
      hasFieldErrors
    ) {
      return false;
    }

    if (
      duplicateBlocking.value
    ) {
      createError.value =
        "La Cédula/DNI o el correo ya pertenecen a un autor registrado. Use el registro existente.";

      return false;
    }

    return true;
  };


/* =========================================================
   MODALES
========================================================= */

const captureFocusOrigin =
  () => {
    if (
      !showPicker.value &&
      !showCreate.value
    ) {
      lastFocusedElement.value =
        document.activeElement;
    }
  };


const openPicker =
  async (
    forceRefresh = false
  ) => {
    captureFocusOrigin();

    modalState.value =
      "picker";

    await nextTick();

    searchInput.value
      ?.focus?.();

    await refreshAutores(
      forceRefresh
    );
  };


const closePicker =
  async () => {
    modalState.value =
      null;

    search.value =
      "";

    remoteSearchAutores.value = [];
    remoteSearchTerm.value = "";
    searchReq += 1;

    clearDragState();

    await nextTick();

    restoreFocus();
  };


const openCreate =
  async () => {
    captureFocusOrigin();

    returnToPickerAfterCreate.value =
      true;

    modalState.value =
      "create";

    createError.value =
      "";

    resetDuplicateState();
    resetCreateErrors();
    resetCreateTouched();

    await nextTick();

    const firstInput =
      createDialog.value
        ?.querySelector(
          "input"
        );

    firstInput
      ?.focus?.();
  };


const resetCreateForm =
  () => {
    nuevo.value = {
      identificacion: "",
      nombres: "",
      apellidos: "",
      correo: "",
      institucion: "",
    };

    createError.value =
      "";

    resetDuplicateState();
    resetCreateTouched();
    resetCreateErrors();
  };


const closeCreate =
  async () => {
    if (
      creating.value
    ) {
      return;
    }

    const goBackToPicker =
      returnToPickerAfterCreate
        .value;

    resetCreateForm();

    modalState.value =
      goBackToPicker
        ? "picker"
        : null;

    await nextTick();

    if (
      goBackToPicker
    ) {
      searchInput.value
        ?.focus?.();
    } else {
      restoreFocus();
    }
  };


const restoreFocus =
  () => {
    const candidate =
      lastFocusedElement.value ||
      openPickerButton.value;

    candidate?.focus?.();
  };


/* =========================================================
   SELECCIÓN
========================================================= */

const selectFromList = (
  autor
) => {
  const id =
    Number(
      autor?.id
    );

  if (
    !Number.isFinite(id) ||
    id <= 0
  ) {
    return;
  }

  const nombreAutor =
    autor?.nombre_completo ||
    "Autor";

  if (
    selected.value.some(
      (item) =>
        Number(
          item.autor_id
        ) === id
    )
  ) {
    notifyAuthorAction(
      `${nombreAutor} ya estaba agregado.`
    );

    return;
  }

  const next = [
    ...selectedResolved.value,

    {
      autor_id:
        id,

      nombre_completo:
        nombreAutor,

      identificacion:
        autor?.identificacion ||
        null,

      correo:
        autor?.correo_resuelto ||
        autor?.correo ||
        null,

      correo_resuelto:
        autor?.correo_resuelto ||
        autor?.correo ||
        null,

      institucion:
        autor?.institucion ||
        null,

      orden:
        selectedResolved.value
          .length + 1,
    },
  ];

  emitOrderedAuthors(
    next
  );

  notifyAuthorAction(
    `Autor agregado: ${nombreAutor}.`
  );
};


/* =========================================================
   GESTIÓN DEL ORDEN
========================================================= */

const removeAuthor = (
  index
) => {
  const next = [
    ...selectedResolved.value,
  ];

  const removed =
    next[index];

  if (!removed) {
    return;
  }

  next.splice(
    index,
    1
  );

  emitOrderedAuthors(
    next
  );

  clearDragState();

  announce(
    `Autor eliminado: ${
      removed?.nombre_completo ||
      "Autor"
    }.`
  );
};


const moveAuthorUp = (
  index
) => {
  if (
    index <= 0
  ) {
    return;
  }

  const next = [
    ...selectedResolved.value,
  ];

  [
    next[index - 1],
    next[index],
  ] = [
    next[index],
    next[index - 1],
  ];

  emitOrderedAuthors(
    next
  );
};


const moveAuthorDown = (
  index
) => {
  if (
    index >=
    selectedResolved.value
      .length - 1
  ) {
    return;
  }

  const next = [
    ...selectedResolved.value,
  ];

  [
    next[index + 1],
    next[index],
  ] = [
    next[index],
    next[index + 1],
  ];

  emitOrderedAuthors(
    next
  );
};


const setAuthorOrder = (
  fromIndex,
  rawValue
) => {
  const targetOrder =
    Number(
      rawValue
    );

  const targetIndex =
    targetOrder - 1;

  if (
    !Number.isInteger(
      targetOrder
    )
  ) {
    return;
  }

  if (
    targetIndex < 0 ||
    targetIndex >=
      selectedResolved.value
        .length
  ) {
    return;
  }

  if (
    fromIndex ===
    targetIndex
  ) {
    return;
  }

  reorderAuthors(
    fromIndex,
    targetIndex
  );
};


/* =========================================================
   DRAG & DROP
========================================================= */

const clearDragState =
  () => {
    draggedAuthorIndex.value =
      null;

    dragOverAuthorIndex.value =
      null;
  };


const reorderAuthors = (
  fromIndex,
  toIndex
) => {
  if (
    fromIndex ===
    toIndex
  ) {
    return;
  }

  if (
    fromIndex == null ||
    toIndex == null
  ) {
    return;
  }

  if (
    fromIndex < 0 ||
    toIndex < 0
  ) {
    return;
  }

  if (
    fromIndex >=
      selectedResolved.value
        .length ||
    toIndex >=
      selectedResolved.value
        .length
  ) {
    return;
  }

  const next = [
    ...selectedResolved.value,
  ];

  const [moved] =
    next.splice(
      fromIndex,
      1
    );

  next.splice(
    toIndex,
    0,
    moved
  );

  emitOrderedAuthors(
    next
  );

  announce(
    "Orden bibliográfico actualizado."
  );
};


const onAuthorDragStart = (
  index,
  event
) => {
  draggedAuthorIndex.value =
    index;

  dragOverAuthorIndex.value =
    index;

  if (
    event?.dataTransfer
  ) {
    event.dataTransfer.effectAllowed =
      "move";

    event.dataTransfer.dropEffect =
      "move";

    event.dataTransfer.setData(
      "text/plain",
      String(index)
    );
  }
};


const onAuthorDragEnter = (
  index
) => {
  if (
    draggedAuthorIndex.value ==
    null
  ) {
    return;
  }

  if (
    draggedAuthorIndex.value ===
    index
  ) {
    return;
  }

  dragOverAuthorIndex.value =
    index;
};


const onAuthorDragOver = (
  index,
  event
) => {
  if (
    draggedAuthorIndex.value ==
    null
  ) {
    return;
  }

  if (
    event?.dataTransfer
  ) {
    event.dataTransfer.dropEffect =
      "move";
  }

  dragOverAuthorIndex.value =
    index;
};


const onAuthorDrop = (
  index
) => {
  if (
    draggedAuthorIndex.value ==
    null
  ) {
    return;
  }

  reorderAuthors(
    draggedAuthorIndex.value,
    index
  );

  clearDragState();
};


const onAuthorDragEnd =
  () => {
    clearDragState();
  };


/* =========================================================
   ERRORES API
========================================================= */

const errorText = (
  value
) => {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "";
  }

  if (
    Array.isArray(value)
  ) {
    return value
      .map(errorText)
      .filter(Boolean)
      .join(" ");
  }

  if (
    typeof value ===
    "object"
  ) {
    return Object.values(
      value
    )
      .map(errorText)
      .filter(Boolean)
      .join(" ");
  }

  return String(
    value
  ).trim();
};


const resolveApiError = (
  data
) => {
  if (!data) {
    return "";
  }

  const source =
    data?.errors &&
    typeof data.errors ===
      "object"
      ? data.errors
      : data;

  const detail =
    errorText(
      source?.detail
    );

  if (detail) {
    return detail;
  }

  const genericError =
    errorText(
      source?.error
    );

  if (genericError) {
    return genericError;
  }

  for (
    const key
    of [
      "identificacion",
      "correo",
      "nombres",
      "apellidos",
      "institucion",
      "usuario",
      "non_field_errors",
    ]
  ) {
    const message =
      errorText(
        source?.[key]
      );

    if (message) {
      return message;
    }
  }

  return errorText(
    source
  );
};


/* =========================================================
   CREAR AUTOR
========================================================= */

const mergeAutor = (
  autor
) => {
  autores.value =
    normalizeAutores([
      autor,
      ...autores.value,
    ]);
};


const createDisabled =
  computed(() => {
    return (
      creating.value ||
      checkingDuplicate.value ||
      duplicateBlocking.value
    );
  });


const useDuplicateAutor =
  async () => {
    if (
      !duplicateAutor.value
    ) {
      return;
    }

    const duplicated =
      normalizeAutores([
        duplicateAutor.value,
      ])[0];

    if (
      !duplicated?.id
    ) {
      return;
    }

    mergeAutor(
      duplicated
    );

    if (
      !isAlreadySelected(
        duplicated.id
      )
    ) {
      selectFromList(
        duplicated
      );
    }

    modalState.value =
      "picker";

    search.value =
      duplicated
        .nombre_completo ||
      "";

    resetCreateForm();

    await nextTick();

    searchInput.value
      ?.focus?.();

    notifyAuthorAction(
      `Se usó el autor existente: ${
        duplicated
          .nombre_completo ||
        "Autor"
      }.`
    );
  };


const createAutor =
  async () => {
    if (
      !validateCreateForm()
    ) {
      return;
    }

    creating.value =
      true;

    createError.value =
      "";

    try {
      /*
       * IMPORTANTE:
       *
       * No enviamos es_externo desde el frontend.
       * El backend es responsable de decidir esa
       * propiedad.
       */
      const payload = {
        identificacion:
          cleanExternalIdentification(
            nuevo.value
              .identificacion
          ) ||
          null,

        nombres:
          (
            nuevo.value.nombres ||
            ""
          ).trim(),

        apellidos:
          (
            nuevo.value.apellidos ||
            ""
          ).trim(),

        correo:
          cleanEmail(
            nuevo.value.correo
          ),

        institucion:
          (
            nuevo.value
              .institucion ||
            ""
          ).trim() ||
          null,
      };

      const response =
        await api.post(
          "/autores/",
          payload
        );

      const responseAutor =
        response?.data?.autor ||
        response?.data?.data ||
        response?.data;

      const inserted =
        normalizeAutores([
          responseAutor,
        ])[0];

      if (
        !inserted?.id
      ) {
        throw new Error(
          "La respuesta del servidor no devolvió un autor válido."
        );
      }

      mergeAutor(
        inserted
      );

      if (
        !isAlreadySelected(
          inserted.id
        )
      ) {
        selectFromList(
          inserted
        );
      }

      modalState.value =
        "picker";

      search.value =
        inserted
          .nombre_completo ||
        "";

      resetCreateForm();

      await nextTick();

      searchInput.value
        ?.focus?.();

      await refreshAutores(
        true
      );

      notifyAuthorAction(
        `Autor externo creado y agregado: ${
          inserted
            .nombre_completo ||
          "Autor"
        }. También quedó vinculado a una cuenta pendiente para una posible activación futura.`
      );
    } catch (error) {
      const data =
        error?.response?.data;

      createError.value =
        resolveApiError(
          data
        ) ||
        "No se pudo crear el autor. Verifique los datos e intente nuevamente.";

      console.warn(
        "Error creando autor:",
        error
      );

      await refreshAutores(
        true
      );
    } finally {
      creating.value =
        false;
    }
  };


/* =========================================================
   FOCO / ACCESIBILIDAD
========================================================= */

const getFocusableElements = (
  root
) => {
  if (!root) {
    return [];
  }

  return [
    ...root.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ),
  ].filter(
    (element) =>
      !element.hasAttribute(
        "disabled"
      ) &&
      element.getAttribute(
        "aria-hidden"
      ) !== "true"
  );
};


const onKey = (
  event
) => {
  if (
    !showPicker.value &&
    !showCreate.value
  ) {
    return;
  }

  /* -------------------------------------------------------
     ESC
  ------------------------------------------------------- */

  if (
    event.key ===
    "Escape"
  ) {
    event.preventDefault();

    if (
      showCreate.value
    ) {
      closeCreate();

      return;
    }

    if (
      showPicker.value
    ) {
      closePicker();
    }

    return;
  }

  /* -------------------------------------------------------
     Focus trap
  ------------------------------------------------------- */

  if (
    event.key ===
    "Tab"
  ) {
    const root =
      showCreate.value
        ? createDialog.value
        : showPicker.value
          ? pickerDialog.value
          : null;

    if (!root) {
      return;
    }

    const focusables =
      getFocusableElements(
        root
      );

    if (
      !focusables.length
    ) {
      return;
    }

    const first =
      focusables[0];

    const last =
      focusables[
        focusables.length - 1
      ];

    const active =
      document.activeElement;

    if (
      event.shiftKey &&
      active === first
    ) {
      event.preventDefault();

      last.focus();
    } else if (
      !event.shiftKey &&
      active === last
    ) {
      event.preventDefault();

      first.focus();
    }
  }
};


/* =========================================================
   WATCHERS
========================================================= */

watch(
  () =>
    search.value,

  (value) => {
    if (
      modalState.value !==
      "picker"
    ) {
      return;
    }

    scheduleAuthorSearch(
      value
    );
  }
);


watch(
  () =>
    modalState.value,

  (value) => {
    document.body
      .classList
      .toggle(
        "as-modal-open",
        Boolean(value)
      );

    if (!value) {
      returnToPickerAfterCreate.value =
        false;

      clearDragState();
    }
  }
);


watch(
  () => [
    nuevo.value
      .identificacion,

    nuevo.value
      .correo,

    nuevo.value
      .nombres,

    nuevo.value
      .apellidos,

    nuevo.value
      .institucion,

    showCreate.value,
  ],

  () => {
    if (
      !showCreate.value
    ) {
      return;
    }

    validateTouchedFields();

    createError.value =
      "";

    scheduleDuplicateCheck();
  }
);


/* =========================================================
   CICLO DE VIDA
========================================================= */

onMounted(
  async () => {
    loadFavoritos();

    window.addEventListener(
      "keydown",
      onKey
    );

    await refreshAutores();
  }
);


onBeforeUnmount(
  () => {
    refreshReq += 1;
    searchReq += 1;
    duplicateReq += 1;

    document.body.classList.remove(
      "as-modal-open"
    );

    window.removeEventListener(
      "keydown",
      onKey
    );

    if (duplicateTimer) {
      window.clearTimeout(
        duplicateTimer
      );

      duplicateTimer =
        null;
    }

    if (announcementTimer) {
      window.clearTimeout(
        announcementTimer
      );

      announcementTimer =
        null;
    }

    if (confirmationTimer) {
      window.clearTimeout(
        confirmationTimer
      );

      confirmationTimer =
        null;
    }
  }
);
</script>

<style scoped src="./autores-selector.css"></style>
