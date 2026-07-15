<template>
  <section
    class="as"
    id="as-autores"
    aria-labelledby="as-autores-title"
    :aria-busy="loadingAutores ? 'true' : 'false'"
    :aria-describedby="props.error ? 'as-autores-error' : undefined"
  >
    <p class="as-sr-only as-live" aria-live="polite" aria-atomic="true">
      {{ liveMessage }}
    </p>

    <div class="as-head surface-enter surface-enter--1">
      <div class="as-head-left">
        <div class="as-title-wrap">
          <p class="as-kicker">Autoría</p>

          <h3 id="as-autores-title" class="as-title">
            Autores <span class="req" aria-hidden="true">*</span>
          </h3>

          <p class="as-subtitle">
            Seleccione un autor principal, agregue coautores y ordénelos libremente.
          </p>
        </div>
      </div>

      <div class="as-head-right">
        <button
          ref="openPickerButton"
          type="button"
          class="as-btn as-btn-primary"
          @click="openPicker()"
          :disabled="loadingAutores && !autores.length"
          :aria-busy="loadingAutores ? 'true' : 'false'"
        >
          <span v-if="loadingAutores && !showPicker">Cargando...</span>
          <span v-else>{{ selected.length ? "Gestionar autores" : "Seleccionar autor(es)" }}</span>
        </button>
      </div>
    </div>

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
      <span>{{ errorAutores }}</span>

      <button
        type="button"
        class="as-btn as-btn-ghost as-btn-sm"
        @click="refreshAutores(true)"
        :disabled="loadingAutores"
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

    <div class="as-body surface-enter surface-enter--2">
      <div v-if="!selected.length" class="as-empty">
        <div class="as-empty-card">
          <div class="as-empty-title">Sin autores agregados</div>

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

      <div v-else class="as-selected">
        <div class="as-selected-bar">
          <div class="as-selected-bar__left">
            <span class="as-count">
              {{ selected.length }} autor(es) seleccionado(s)
            </span>

            <span class="as-helper">
              Debe existir un único autor principal. Los coautores pueden ordenarse libremente.
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

        <div class="as-section">
          <div class="as-section__head">
            <h4 class="as-section__title">Autor principal</h4>
            <span class="as-section__meta">Orden 1</span>
          </div>

          <div v-if="principalAutor" class="as-row as-row--principal">
            <div class="as-row-main">
              <div class="as-row-topline">
                <span class="as-status as-status--primary">Autor principal</span>
              </div>

              <div class="as-row-name">
                {{ principalAutor.nombre_completo || "Autor" }}
              </div>

              <div class="as-row-sub">
                <span v-if="principalAutor.identificacion">
                  CI: {{ principalAutor.identificacion }}
                </span>
                <span v-else>Sin identificación</span>

                <span v-if="principalAutor.correo_resuelto">
                  • {{ principalAutor.correo_resuelto }}
                </span>

                <span v-if="principalAutor.institucion">
                  • {{ principalAutor.institucion }}
                </span>
              </div>

              <div class="as-row-controls">
                <label class="as-field-inline" for="as-principal-select">
                  <span class="as-field-inline__label">Cambiar principal</span>

                  <select
                    id="as-principal-select"
                    class="as-control-select as-control-select--role"
                    :value="principalAutor.autor_id"
                    @change="setPrincipalById($event.target.value)"
                  >
                    <option
                      v-for="autor in selectedResolved"
                      :key="`principal-opt-${autor.autor_id}`"
                      :value="autor.autor_id"
                    >
                      {{ autor.nombre_completo || "Autor" }}
                    </option>
                  </select>
                </label>
              </div>
            </div>

            <div class="as-row-actions">
              <button
                type="button"
                class="as-icon as-icon-danger"
                aria-label="Eliminar autor principal"
                title="Eliminar autor principal"
                @click="removePrincipal()"
              >
                ✖
              </button>
            </div>
          </div>

          <p v-else class="as-alert as-alert-error as-alert-inline" role="alert">
            Debe existir un autor principal.
          </p>
        </div>

        <div class="as-section">
          <div class="as-section__head">
            <div class="as-section__title-wrap">
              <h4 class="as-section__title">Coautores</h4>
              <p class="as-section__hint">
                Puede arrastrarlos para cambiar el orden.
              </p>
            </div>

            <span class="as-section__meta">
              {{ coautores.length }} coautor(es)
            </span>
          </div>

          <div v-if="!coautores.length" class="as-subempty">
            No hay coautores agregados.
          </div>

          <div
            v-else
            class="as-list-selected"
            role="list"
            aria-label="Coautores seleccionados"
          >
            <div
              class="as-row as-row--draggable"
              v-for="(autor, index) in coautores"
              :key="autorKey(autor, index)"
              role="listitem"
              :class="{
                'as-row--dragging': draggedCoautorIndex === index,
                'as-row--dragover': dragOverCoautorIndex === index && draggedCoautorIndex !== index
              }"
              @dragover.prevent="onCoautorDragOver(index, $event)"
              @dragenter.prevent="onCoautorDragEnter(index)"
              @drop.prevent="onCoautorDrop(index, $event)"
            >
              <div class="as-row-main">
                <div class="as-row-topline">
                  <button
                    type="button"
                    class="as-drag-handle"
                    draggable="true"
                    :aria-label="`Arrastrar coautor ${autor.nombre_completo || 'Autor'}`"
                    title="Arrastrar para reordenar"
                    @dragstart="onCoautorDragStart(index, $event)"
                    @dragend="onCoautorDragEnd()"
                  >
                    <span aria-hidden="true">⋮⋮</span>
                  </button>

                  <span class="as-row-index">#{{ index + 2 }}</span>
                  <span class="as-status as-status--soft">Coautor</span>
                </div>

                <div class="as-row-name">
                  {{ autor.nombre_completo || "Autor" }}
                </div>

                <div class="as-row-sub">
                  <span v-if="autor.identificacion">CI: {{ autor.identificacion }}</span>
                  <span v-else>Sin identificación</span>

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
                    <span class="as-field-inline__label">Orden</span>

                    <select
                      :id="`as-order-${autor.autor_id}-${index}`"
                      class="as-control-select as-control-select--order"
                      :value="index + 2"
                      @change="setCoautorOrden(index, $event.target.value)"
                    >
                      <option
                        v-for="n in coautorOrdenOptions"
                        :key="`coorden-${autor.autor_id}-${n}`"
                        :value="n"
                      >
                        {{ n }}
                      </option>
                    </select>
                  </label>

                  <button
                    type="button"
                    class="as-btn as-btn-ghost as-btn-sm"
                    @click="makePrincipal(autor.autor_id)"
                  >
                    Hacer principal
                  </button>
                </div>
              </div>

              <div class="as-row-actions">
                <button
                  type="button"
                  class="as-icon"
                  aria-label="Subir coautor una posición"
                  title="Subir"
                  @click="moveCoautorUp(index)"
                  :disabled="index === 0"
                >
                  ▲
                </button>

                <button
                  type="button"
                  class="as-icon"
                  aria-label="Bajar coautor una posición"
                  title="Bajar"
                  @click="moveCoautorDown(index)"
                  :disabled="index === coautores.length - 1"
                >
                  ▼
                </button>

                <button
                  type="button"
                  class="as-icon as-icon-danger"
                  aria-label="Eliminar coautor"
                  title="Eliminar"
                  @click="removeCoautor(index)"
                >
                  ✖
                </button>
              </div>
            </div>
          </div>
        </div>

        <p
          v-if="selected.length && principalCount !== 1"
          class="as-alert as-alert-error as-alert-inline"
          role="alert"
        >
          Debe existir exactamente un autor principal.
        </p>
      </div>
    </div>

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
                <p class="as-modal-kicker">Selección</p>

                <h3 id="as-picker-title" class="as-modal-title">
                  Seleccionar autor(es)
                </h3>

                <p id="as-picker-sub" class="as-modal-sub">
                  Busque por nombre, correo, identificación o institución.
                </p>
              </div>

              <button
                type="button"
                class="as-icon"
                @click="closePicker()"
                aria-label="Cerrar selector de autores"
              >
                ✖
              </button>
            </div>

            <div class="as-modal-body">
              <div class="as-toolbar">
                <div class="as-search-field">
                  <label class="as-sr-only" for="as-search-input">
                    Buscar autor
                  </label>

                  <span class="as-search-icon" aria-hidden="true">⌕</span>

                  <input
                    id="as-search-input"
                    ref="searchInput"
                    class="as-input as-input-search"
                    type="text"
                    v-model.trim="search"
                    placeholder="Buscar por nombre, correo, identificación o institución..."
                    autocomplete="off"
                    inputmode="search"
                  />

                  <button
                    v-if="search"
                    type="button"
                    class="as-search-clear"
                    @click="clearSearch()"
                    aria-label="Limpiar búsqueda"
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
                    @click="refreshAutores(true)"
                    :disabled="loadingAutores"
                  >
                    Actualizar
                  </button>
                </div>
              </div>

              <div v-if="loadingAutores && !autores.length" class="as-state-card">
                <div class="as-state-card__title">Cargando autores...</div>
                <div class="as-state-card__text">
                  Espere un momento mientras se consulta el catálogo.
                </div>
              </div>

              <div
                v-else-if="!loadingAutores && filteredAutores.length === 0"
                class="as-state-card"
              >
                <div class="as-state-card__title">Sin coincidencias</div>

                <div class="as-state-card__text">
                  <template v-if="search">
                    No hay resultados para "{{ search }}".
                  </template>

                  <template v-else>
                    No hay autores disponibles en el catálogo.
                  </template>
                </div>
              </div>

              <div v-else class="as-picker-results">
                <div
                  v-if="favoriteAvailableAutores.length"
                  class="as-picker-group as-picker-group--favorites"
                >
                  <div class="as-picker-group__head">
                    <span class="as-picker-group__title">Favoritos</span>
                    <span class="as-picker-group__count">
                      {{ favoriteAvailableAutores.length }}
                    </span>
                  </div>

                  <div class="as-catalog">
                    <div
                      class="as-catalog-item"
                      v-for="a in favoriteAvailableAutores"
                      :key="`fav-${a.id}`"
                    >
                      <button
                        type="button"
                        class="as-catalog-select"
                        @click="selectFromList(a)"
                        :disabled="isAlreadySelected(a.id)"
                        :aria-label="`Agregar autor ${a.nombre_completo || `${a.nombres} ${a.apellidos}`}`"
                        title="Agregar autor favorito"
                      >
                        <div class="as-ci-main">
                          <div class="as-ci-name">
                            {{ a.nombre_completo || `${a.nombres} ${a.apellidos}` }}
                          </div>

                          <div class="as-ci-sub">
                            <span v-if="a.identificacion">CI: {{ a.identificacion }}</span>
                            <span v-else>Sin identificación</span>
                            <span v-if="a.correo_resuelto"> • {{ a.correo_resuelto }}</span>
                            <span v-if="a.institucion"> • {{ a.institucion }}</span>
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
                          @click="selectFromList(a)"
                          :disabled="isAlreadySelected(a.id)"
                        >
                          Seleccionar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="nonFavoriteAvailableAutores.length" class="as-picker-group">
                  <div class="as-picker-group__head">
                    <span class="as-picker-group__title">
                      {{ search ? "Coincidencias" : "Autores disponibles" }}
                    </span>

                    <span class="as-picker-group__count">
                      {{ nonFavoriteAvailableAutores.length }}
                    </span>
                  </div>

                  <div class="as-catalog">
                    <div
                      class="as-catalog-item"
                      v-for="a in nonFavoriteAvailableAutores"
                      :key="a.id"
                    >
                      <button
                        type="button"
                        class="as-catalog-select"
                        @click="selectFromList(a)"
                        :disabled="isAlreadySelected(a.id)"
                        :aria-label="`Agregar autor ${a.nombre_completo || `${a.nombres} ${a.apellidos}`}`"
                        title="Agregar autor"
                      >
                        <div class="as-ci-main">
                          <div class="as-ci-name">
                            {{ a.nombre_completo || `${a.nombres} ${a.apellidos}` }}
                          </div>

                          <div class="as-ci-sub">
                            <span v-if="a.identificacion">CI: {{ a.identificacion }}</span>
                            <span v-else>Sin identificación</span>
                            <span v-if="a.correo_resuelto"> • {{ a.correo_resuelto }}</span>
                            <span v-if="a.institucion"> • {{ a.institucion }}</span>
                          </div>
                        </div>
                      </button>

                      <div class="as-ci-right">
                        <button
                          type="button"
                          class="as-fav-btn"
                          :class="{ 'is-on': isFavorito(a.id) }"
                          :title="isFavorito(a.id) ? 'Quitar de favoritos' : 'Agregar a favoritos'"
                          :aria-label="isFavorito(a.id) ? 'Quitar de favoritos' : 'Agregar a favoritos'"
                          @click.stop.prevent="toggleFavorito(a)"
                        >
                          ★
                        </button>

                        <button
                          type="button"
                          class="as-select-action"
                          @click="selectFromList(a)"
                          :disabled="isAlreadySelected(a.id)"
                        >
                          Seleccionar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div
                  v-if="alreadyAddedAutores.length"
                  class="as-picker-group as-picker-group--selected"
                >
                  <div class="as-picker-group__head">
                    <span class="as-picker-group__title">Ya agregados</span>
                    <span class="as-picker-group__count">
                      {{ alreadyAddedAutores.length }}
                    </span>
                  </div>

                  <div class="as-catalog as-catalog--compact">
                    <div
                      class="as-catalog-item as-catalog-item--disabled"
                      v-for="a in alreadyAddedAutores"
                      :key="`selected-${a.id}`"
                    >
                      <div class="as-catalog-static">
                        <div class="as-ci-main">
                          <div class="as-ci-name">
                            {{ a.nombre_completo || `${a.nombres} ${a.apellidos}` }}
                          </div>

                          <div class="as-ci-sub">
                            <span v-if="a.identificacion">CI: {{ a.identificacion }}</span>
                            <span v-else>Sin identificación</span>
                            <span v-if="a.correo_resuelto"> • {{ a.correo_resuelto }}</span>
                            <span v-if="a.institucion"> • {{ a.institucion }}</span>
                          </div>
                        </div>
                      </div>

                      <div class="as-ci-right">
                        <button
                          type="button"
                          class="as-fav-btn"
                          :class="{ 'is-on': isFavorito(a.id) }"
                          :title="isFavorito(a.id) ? 'Quitar de favoritos' : 'Agregar a favoritos'"
                          :aria-label="isFavorito(a.id) ? 'Quitar de favoritos' : 'Agregar a favoritos'"
                          @click.stop.prevent="toggleFavorito(a)"
                        >
                          ★
                        </button>

                        <span class="as-badge as-badge-ok">Agregado</span>
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
                <p class="as-modal-kicker">Registro</p>

                <h3 id="as-create-title" class="as-modal-title">
                  Agregar nuevo autor
                </h3>

                <p id="as-create-sub" class="as-modal-sub">
                  Complete los datos para registrar un autor externo.
                  Al guardar, también se registrará como <b>pendiente</b> en el sistema.
                </p>
              </div>

              <button
                type="button"
                class="as-icon"
                @click="closeCreate()"
                aria-label="Cerrar formulario de autor"
                :disabled="creating"
              >
                ✖
              </button>
            </div>

            <form class="as-create-form" @submit.prevent="createAutor">
              <div class="as-modal-body">
                <p v-if="createError" class="as-alert as-alert-error" role="alert">
                  {{ createError }}
                </p>

                <div
                  v-if="duplicateExists && duplicateAutor"
                  class="as-alert as-alert-warning"
                  role="alert"
                >
                  <div class="as-alert-stack">
                    <span>
                      Ya existe un autor registrado con esos datos:
                      <b>{{ duplicateAutor.nombre_completo }}</b>.
                    </span>

                    <span class="as-alert-sub">
                      Use el registro existente para evitar duplicados.
                    </span>

                    <div class="as-inline-actions">
                      <button
                        type="button"
                        class="as-btn as-btn-sm as-btn-secondary"
                        @click="useDuplicateAutor()"
                      >
                        Usar autor existente
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

                <div class="as-grid">
                  <div
                    class="as-field"
                    :class="{ 'as-field--invalid': !!createFieldErrors.identificacion }"
                  >
                    <label class="as-field-label" for="nuevo-identificacion">
                      Identificación <span class="req" aria-hidden="true">*</span>
                    </label>

                    <input
                      id="nuevo-identificacion"
                      class="as-input"
                      v-model.trim="nuevo.identificacion"
                      required
                      maxlength="10"
                      pattern="[0-9]{10}"
                      placeholder="Ej. 1312345678"
                      inputmode="numeric"
                      autocomplete="off"
                      :aria-invalid="createFieldErrors.identificacion ? 'true' : 'false'"
                      :aria-describedby="
                        createFieldErrors.identificacion
                          ? 'nuevo-identificacion-error'
                          : 'nuevo-identificacion-help'
                      "
                      @blur="touchCreateField('identificacion')"
                    />

                    <p id="nuevo-identificacion-help" class="as-hint">
                      Ingrese una identificación de 10 dígitos.
                    </p>

                    <p
                      v-if="createFieldErrors.identificacion"
                      id="nuevo-identificacion-error"
                      class="as-field-error"
                    >
                      {{ createFieldErrors.identificacion }}
                    </p>
                  </div>

                  <div
                    class="as-field"
                    :class="{ 'as-field--invalid': !!createFieldErrors.correo }"
                  >
                    <label class="as-field-label" for="nuevo-correo">
                      Correo <span class="req" aria-hidden="true">*</span>
                    </label>

                    <input
                      id="nuevo-correo"
                      class="as-input"
                      type="email"
                      v-model.trim="nuevo.correo"
                      required
                      placeholder="correo@ejemplo.com"
                      autocomplete="off"
                      :aria-invalid="createFieldErrors.correo ? 'true' : 'false'"
                      :aria-describedby="
                        createFieldErrors.correo
                          ? 'nuevo-correo-error'
                          : 'nuevo-correo-help'
                      "
                      @blur="touchCreateField('correo')"
                    />

                    <p id="nuevo-correo-help" class="as-hint">
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

                  <div
                    class="as-field"
                    :class="{ 'as-field--invalid': !!createFieldErrors.nombres }"
                  >
                    <label class="as-field-label" for="nuevo-nombres">
                      Nombres <span class="req" aria-hidden="true">*</span>
                    </label>

                    <input
                      id="nuevo-nombres"
                      class="as-input"
                      v-model.trim="nuevo.nombres"
                      required
                      placeholder="Ej. María"
                      autocomplete="off"
                      :aria-invalid="createFieldErrors.nombres ? 'true' : 'false'"
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

                  <div
                    class="as-field"
                    :class="{ 'as-field--invalid': !!createFieldErrors.apellidos }"
                  >
                    <label class="as-field-label" for="nuevo-apellidos">
                      Apellidos <span class="req" aria-hidden="true">*</span>
                    </label>

                    <input
                      id="nuevo-apellidos"
                      class="as-input"
                      v-model.trim="nuevo.apellidos"
                      required
                      placeholder="Ej. Pérez"
                      autocomplete="off"
                      :aria-invalid="createFieldErrors.apellidos ? 'true' : 'false'"
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

                  <div
                    class="as-field as-field--wide"
                    :class="{ 'as-field--invalid': !!createFieldErrors.institucion }"
                  >
                    <label class="as-field-label" for="nuevo-institucion">
                      Institución
                    </label>

                    <input
                      id="nuevo-institucion"
                      class="as-input"
                      v-model.trim="nuevo.institucion"
                      maxlength="255"
                      placeholder="Ej. Universidad Laica Eloy Alfaro de Manabí"
                      autocomplete="organization"
                      :aria-invalid="createFieldErrors.institucion ? 'true' : 'false'"
                      :aria-describedby="
                        createFieldErrors.institucion
                          ? 'nuevo-institucion-error'
                          : 'nuevo-institucion-help'
                      "
                      @blur="touchCreateField('institucion')"
                    />

                    <p id="nuevo-institucion-help" class="as-hint">
                      Puede escribir manualmente la institución o dejarla vacía.
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
                  <span v-if="creating">Guardando...</span>
                  <span v-else>Guardar y agregar</span>
                </button>

                <button
                  type="button"
                  class="as-btn"
                  @click="closeCreate()"
                  :disabled="creating"
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

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  error: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue"]);

const selected = ref([]);
const autores = ref([]);
const loadingAutores = ref(false);
const errorAutores = ref("");
const liveMessage = ref("");
const confirmationMessage = ref("");

const modalState = ref(null);
const returnToPickerAfterCreate = ref(false);

const search = ref("");
const searchInput = ref(null);
const pickerDialog = ref(null);
const createDialog = ref(null);
const openPickerButton = ref(null);
const lastFocusedElement = ref(null);

const creating = ref(false);
const createError = ref("");
const checkingDuplicate = ref(false);
const duplicateResult = ref({
  exists: false,
  match_type: null,
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

const draggedCoautorIndex = ref(null);
const dragOverCoautorIndex = ref(null);

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CATALOG_TTL_MS = 2 * 60 * 1000;

let refreshReq = 0;
let duplicateReq = 0;
let duplicateTimer = null;
let announcementTimer = null;
let confirmationTimer = null;

const lastCatalogLoadedAt = ref(0);

const showPicker = computed(() => modalState.value === "picker");
const showCreate = computed(() => modalState.value === "create");

const announce = (message) => {
  if (announcementTimer) {
    window.clearTimeout(announcementTimer);
    announcementTimer = null;
  }

  liveMessage.value = "";

  nextTick(() => {
    liveMessage.value = message;

    announcementTimer = window.setTimeout(() => {
      liveMessage.value = "";
    }, 1400);
  });
};

const showConfirmation = (message) => {
  if (confirmationTimer) {
    window.clearTimeout(confirmationTimer);
    confirmationTimer = null;
  }

  confirmationMessage.value = message;

  confirmationTimer = window.setTimeout(() => {
    confirmationMessage.value = "";
  }, 2800);
};

const notifyAuthorAction = (message) => {
  announce(message);
  showConfirmation(message);
};

const normalizeText = (value) =>
  String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim();

const cleanEmail = (value) => String(value ?? "").trim().toLowerCase();
const digitsOnly = (value) => String(value ?? "").replace(/\D/g, "");

const getCurrentUserKey = () => {
  try {
    const rawUser = localStorage.getItem("user");
    const parsedUser = rawUser ? JSON.parse(rawUser) : null;

    const userId =
      parsedUser?.id ??
      parsedUser?.user_id ??
      localStorage.getItem("autor_id") ??
      localStorage.getItem("email") ??
      "guest";

    return String(userId).trim() || "guest";
  } catch {
    return "guest";
  }
};

const FAV_KEY = computed(() => `sgpc-autores-favoritos:${getCurrentUserKey()}`);
const favoritos = ref(new Set());

const normalizeFavId = (id) => String(id ?? "").trim();

const autorKey = (autor, index) => {
  const id = autor?.autor_id ?? autor?.id ?? null;
  return id ? `autor-${id}` : `tmp-${autor?.nombre_completo || "autor"}-${index}`;
};

const asArrayResponse = (data) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
};

const compareAutores = (a, b) => {
  const apellidosA = normalizeText(a?.apellidos || "");
  const apellidosB = normalizeText(b?.apellidos || "");

  if (apellidosA !== apellidosB) {
    return apellidosA.localeCompare(apellidosB, "es", { sensitivity: "base" });
  }

  const nombresA = normalizeText(a?.nombres || "");
  const nombresB = normalizeText(b?.nombres || "");

  if (nombresA !== nombresB) {
    return nombresA.localeCompare(nombresB, "es", { sensitivity: "base" });
  }

  const completoA = normalizeText(a?.nombre_completo || "");
  const completoB = normalizeText(b?.nombre_completo || "");

  return completoA.localeCompare(completoB, "es", { sensitivity: "base" });
};

const dedupeById = (items = []) => {
  const map = new Map();

  for (const item of items) {
    const id = Number(item?.id);
    if (!Number.isFinite(id) || id <= 0) continue;
    map.set(String(id), item);
  }

  return [...map.values()];
};

const normalizeAutores = (raw) => {
  return dedupeById(
    (raw || []).map((a) => {
      const rawId = Number(a?.id ?? a?.autor_id);
      const nombres = String(a?.nombres ?? "").trim();
      const apellidos = String(a?.apellidos ?? "").trim();
      const correoResuelto = cleanEmail(a?.correo_resuelto ?? a?.correo);
      const institucion = String(a?.institucion ?? "").trim() || null;

      const nombreCompleto = (
        a?.nombre_completo ||
        a?.autor_nombre ||
        `${nombres} ${apellidos}`.trim()
      ).trim();

      const searchBlob = normalizeText(
        [
          nombreCompleto,
          nombres,
          apellidos,
          a?.identificacion,
          correoResuelto,
          a?.correo,
          institucion,
        ].join(" ")
      );

      return {
        ...a,
        id: rawId,
        nombres,
        apellidos,
        identificacion: String(a?.identificacion ?? "").trim() || null,
        correo: correoResuelto || null,
        correo_resuelto: correoResuelto || null,
        institucion,
        nombre_completo: nombreCompleto || "Autor",
        search_blob: searchBlob,
      };
    })
  ).sort(compareAutores);
};

const normalizeSelected = (arr) => {
  const base = Array.isArray(arr) ? [...arr] : [];

  const clean = base
    .map((item) => {
      const nestedAutor =
        item?.autor && typeof item.autor === "object"
          ? item.autor
          : null;

      const id = Number(
        item?.autor_id ??
        nestedAutor?.id ??
        item?.id
      );

      if (!Number.isFinite(id) || id <= 0) return null;

      const nombreCompleto = String(
        item?.nombre_completo ||
        item?.autor_nombre ||
        item?.nombre ||
        item?.label ||
        nestedAutor?.nombre_completo ||
        nestedAutor?.autor_nombre ||
        `${nestedAutor?.nombres || ""} ${nestedAutor?.apellidos || ""}`.trim() ||
        ""
      ).trim();

      return {
        autor_id: id,
        orden: Number(item?.orden) || 9999,
        rol_autoria:
          item?.rol_autoria === "principal"
            ? "principal"
            : "coautor",
        nombre_completo: nombreCompleto,
      };
    })
    .filter(Boolean);

  const deduped = [];
  const seen = new Set();

  for (const item of clean) {
    const key = String(item.autor_id);
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(item);
  }

  const principal =
    deduped.find((x) => x.rol_autoria === "principal") ||
    deduped[0] ||
    null;

  const coautoresList = deduped
    .filter((x) => x.autor_id !== principal?.autor_id)
    .sort((a, b) => (a.orden || 9999) - (b.orden || 9999))
    .map((item, index) => ({
      ...item,
      rol_autoria: "coautor",
      orden: index + 2,
    }));

  const normalized = [];

  if (principal) {
    normalized.push({
      ...principal,
      rol_autoria: "principal",
      orden: 1,
    });
  }

  normalized.push(...coautoresList);
  return normalized;
};

const emitNormalized = (arr) => {
  const normalized = normalizeSelected(arr);
  selected.value = normalized;
  emit("update:modelValue", normalized);
};

watch(
  () => props.modelValue,
  (value) => {
    selected.value = normalizeSelected(value);
  },
  { immediate: true }
);

const autoresMap = computed(() => {
  const map = new Map();

  for (const a of autores.value) {
    map.set(String(a.id), a);
  }

  return map;
});

const selectedResolved = computed(() =>
  selected.value.map((item) => {
    const linked = autoresMap.value.get(String(item.autor_id));

    return {
      ...item,
      nombre_completo:
        item.nombre_completo ||
        linked?.nombre_completo ||
        linked?.autor_nombre ||
        "Autor",
      identificacion: linked?.identificacion || null,
      correo_resuelto: linked?.correo_resuelto || linked?.correo || null,
      institucion: linked?.institucion || null,
    };
  })
);

const principalAutor = computed(
  () =>
    selectedResolved.value.find((item) => item.rol_autoria === "principal") ||
    null
);

const coautores = computed(() =>
  selectedResolved.value.filter((item) => item.rol_autoria === "coautor")
);

const principalCount = computed(
  () => selected.value.filter((item) => item.rol_autoria === "principal").length
);

const selectedIds = computed(
  () => new Set(selected.value.map((x) => String(x.autor_id)))
);

const isAlreadySelected = (autorId) => selectedIds.value.has(String(autorId));

const coautorOrdenOptions = computed(() =>
  Array.from({ length: coautores.value.length }, (_, i) => i + 2)
);

const buildNormalizedFromParts = (principal, coautoresList = []) => {
  const next = [];

  if (principal) {
    next.push({
      ...principal,
      rol_autoria: "principal",
      orden: 1,
    });
  }

  coautoresList.forEach((item, index) => {
    next.push({
      ...item,
      rol_autoria: "coautor",
      orden: index + 2,
    });
  });

  emitNormalized(next);
};

const loadFavoritos = () => {
  try {
    const raw = localStorage.getItem(FAV_KEY.value);
    const parsed = raw ? JSON.parse(raw) : [];

    favoritos.value = new Set(
      Array.isArray(parsed)
        ? parsed.map((id) => normalizeFavId(id)).filter(Boolean)
        : []
    );
  } catch {
    favoritos.value = new Set();
  }
};

const saveFavoritos = () => {
  try {
    localStorage.setItem(FAV_KEY.value, JSON.stringify([...favoritos.value]));
  } catch {
    // noop
  }
};

const isFavorito = (autorId) => favoritos.value.has(normalizeFavId(autorId));

const toggleFavorito = (autor) => {
  const id = normalizeFavId(autor?.id);
  if (!id) return;

  if (favoritos.value.has(id)) {
    favoritos.value.delete(id);
  } else {
    favoritos.value.add(id);
  }

  favoritos.value = new Set(favoritos.value);
  saveFavoritos();

  announce(
    favoritos.value.has(id)
      ? "Autor agregado a favoritos."
      : "Autor quitado de favoritos."
  );
};

const shouldRefreshCatalog = () => {
  if (!autores.value.length) return true;
  if (!lastCatalogLoadedAt.value) return true;
  return Date.now() - lastCatalogLoadedAt.value > CATALOG_TTL_MS;
};

const refreshAutores = async (force = false) => {
  if (!force && !shouldRefreshCatalog()) return;

  const reqId = ++refreshReq;
  loadingAutores.value = true;
  errorAutores.value = "";

  try {
    const res = await api.get("/selects/autores/");
    if (reqId !== refreshReq) return;

    autores.value = normalizeAutores(asArrayResponse(res.data));
    lastCatalogLoadedAt.value = Date.now();
  } catch (e) {
    if (reqId !== refreshReq) return;

    errorAutores.value =
      "No se pudieron cargar los autores disponibles. Intente nuevamente.";
    console.warn("Error cargando autores:", e);
  } finally {
    if (reqId === refreshReq) {
      loadingAutores.value = false;
    }
  }
};

const filteredAutores = computed(() => {
  const t = normalizeText(search.value);
  if (!t) return autores.value;
  return autores.value.filter((a) => a.search_blob.includes(t));
});

const alreadyAddedAutores = computed(() =>
  filteredAutores.value.filter((a) => isAlreadySelected(a.id))
);

const availableAutores = computed(() =>
  filteredAutores.value.filter((a) => !isAlreadySelected(a.id))
);

const favoriteAvailableAutores = computed(() =>
  availableAutores.value.filter((a) => isFavorito(a.id))
);

const nonFavoriteAvailableAutores = computed(() =>
  availableAutores.value.filter((a) => !isFavorito(a.id))
);

const clearSearch = async () => {
  search.value = "";
  await nextTick();
  searchInput.value?.focus?.();
};

const duplicateAutor = computed(() => duplicateResult.value?.autor || null);
const duplicateExists = computed(() => !!duplicateResult.value?.exists);

const cancelDuplicateCheck = () => {
  duplicateReq += 1;

  if (duplicateTimer) {
    window.clearTimeout(duplicateTimer);
    duplicateTimer = null;
  }

  checkingDuplicate.value = false;
};

const resetDuplicateState = () => {
  cancelDuplicateCheck();

  duplicateResult.value = {
    exists: false,
    match_type: null,
    autor: null,
  };
};

const resetCreateTouched = () => {
  createTouched.value = {
    identificacion: false,
    correo: false,
    nombres: false,
    apellidos: false,
    institucion: false,
  };
};

const resetCreateErrors = () => {
  createFieldErrors.value = {
    identificacion: "",
    correo: "",
    nombres: "",
    apellidos: "",
    institucion: "",
  };
};

const validateCreateField = (field) => {
  const identificacion = digitsOnly(nuevo.value.identificacion);
  const correo = cleanEmail(nuevo.value.correo);

  switch (field) {
    case "identificacion":
      if (!identificacion) return "La identificación es obligatoria.";
      if (identificacion.length !== 10) {
        return "La identificación debe contener exactamente 10 dígitos.";
      }
      return "";

    case "correo":
      if (!correo) return "El correo es obligatorio.";
      if (!emailRegex.test(correo)) return "El correo ingresado no es válido.";
      return "";

    case "nombres":
      if (!(nuevo.value.nombres || "").trim()) return "Los nombres son obligatorios.";
      return "";

    case "apellidos":
      if (!(nuevo.value.apellidos || "").trim()) return "Los apellidos son obligatorios.";
      return "";

    case "institucion": {
      const institucion = String(nuevo.value.institucion || "").trim();

      if (institucion.length > 255) {
        return "La institución no puede superar 255 caracteres.";
      }

      return "";
    }

    default:
      return "";
  }
};

const validateTouchedFields = () => {
  for (const field of Object.keys(createTouched.value)) {
    if (createTouched.value[field]) {
      createFieldErrors.value[field] = validateCreateField(field);
    }
  }
};

const touchCreateField = (field) => {
  createTouched.value[field] = true;
  createFieldErrors.value[field] = validateCreateField(field);
};

const validateCreateForm = () => {
  createError.value = "";

  for (const field of Object.keys(createTouched.value)) {
    createTouched.value[field] = true;
    createFieldErrors.value[field] = validateCreateField(field);
  }

  const hasFieldErrors = Object.values(createFieldErrors.value).some(Boolean);
  if (hasFieldErrors) return false;

  if (duplicateExists.value) {
    createError.value =
      "Ese autor ya existe en la base de datos. Use el registro existente.";
    return false;
  }

  return true;
};

const shouldRunDuplicateCheck = () => {
  const identificacion = digitsOnly(nuevo.value.identificacion);
  const correo = cleanEmail(nuevo.value.correo);
  const nombres = normalizeText(nuevo.value.nombres);
  const apellidos = normalizeText(nuevo.value.apellidos);

  return Boolean(
    identificacion ||
    correo ||
    (nombres.length >= 2 && apellidos.length >= 2)
  );
};

const runDuplicateCheck = async () => {
  if (!showCreate.value) return;

  if (!shouldRunDuplicateCheck()) {
    resetDuplicateState();
    return;
  }

  const reqId = ++duplicateReq;
  checkingDuplicate.value = true;

  try {
    const res = await api.get("/autores/validar-existencia/", {
      params: {
        identificacion: digitsOnly(nuevo.value.identificacion) || undefined,
        correo: cleanEmail(nuevo.value.correo) || undefined,
        nombres: (nuevo.value.nombres || "").trim() || undefined,
        apellidos: (nuevo.value.apellidos || "").trim() || undefined,
      },
    });

    if (reqId !== duplicateReq) return;

    const responseData = res?.data?.data || res?.data || {};

    duplicateResult.value = {
      exists: !!responseData?.exists,
      match_type: responseData?.match_type || null,
      autor: responseData?.autor || null,
    };

    if (duplicateResult.value.exists) {
      createError.value = "";
    }
  } catch (e) {
    if (reqId !== duplicateReq) return;
    console.warn("Error verificando duplicado de autor:", e);
    resetDuplicateState();
  } finally {
    if (reqId === duplicateReq) {
      checkingDuplicate.value = false;
    }
  }
};

const scheduleDuplicateCheck = () => {
  if (duplicateTimer) {
    window.clearTimeout(duplicateTimer);
    duplicateTimer = null;
  }

  duplicateTimer = window.setTimeout(() => {
    runDuplicateCheck();
  }, 350);
};

const captureFocusOrigin = () => {
  if (!showPicker.value && !showCreate.value) {
    lastFocusedElement.value = document.activeElement;
  }
};

const openPicker = async (forceRefresh = false) => {
  captureFocusOrigin();
  modalState.value = "picker";

  await nextTick();
  searchInput.value?.focus?.();

  await refreshAutores(forceRefresh);
};

const closePicker = async () => {
  modalState.value = null;
  search.value = "";
  clearDragState();

  await nextTick();
  restoreFocus();
};

const openCreate = async () => {
  captureFocusOrigin();
  returnToPickerAfterCreate.value = true;
  modalState.value = "create";
  createError.value = "";
  resetDuplicateState();
  resetCreateErrors();
  resetCreateTouched();

  await nextTick();

  const firstInput = createDialog.value?.querySelector("input");
  firstInput?.focus?.();
};

const resetCreateForm = () => {
  nuevo.value = {
    identificacion: "",
    nombres: "",
    apellidos: "",
    correo: "",
    institucion: "",
  };

  createError.value = "";
  resetDuplicateState();
  resetCreateTouched();
  resetCreateErrors();
};

const closeCreate = async () => {
  if (creating.value) return;

  const goBackToPicker = returnToPickerAfterCreate.value;

  resetCreateForm();
  modalState.value = goBackToPicker ? "picker" : null;

  await nextTick();

  if (goBackToPicker) {
    searchInput.value?.focus?.();
  } else {
    restoreFocus();
  }
};

const restoreFocus = () => {
  const candidate = lastFocusedElement.value || openPickerButton.value;
  candidate?.focus?.();
};

const selectFromList = (a) => {
  const id = Number(a?.id);

  if (!Number.isFinite(id) || id <= 0) return;

  const nombreAutor = a?.nombre_completo || "Autor";

  if (selected.value.some((item) => Number(item.autor_id) === id)) {
    notifyAuthorAction(`${nombreAutor} ya estaba agregado.`);
    return;
  }

  const next = [...selectedResolved.value];

  if (!next.length) {
    next.push({
      autor_id: id,
      nombre_completo: nombreAutor,
      rol_autoria: "principal",
      orden: 1,
    });

    emitNormalized(next);
    notifyAuthorAction(`Autor principal agregado: ${nombreAutor}.`);
    return;
  }

  next.push({
    autor_id: id,
    nombre_completo: nombreAutor,
    rol_autoria: "coautor",
    orden: next.length + 1,
  });

  emitNormalized(next);
  notifyAuthorAction(`Autor agregado: ${nombreAutor}.`);
};

const makePrincipal = (autorId) => {
  const all = [...selectedResolved.value];

  const nuevoPrincipal = all.find(
    (item) => Number(item.autor_id) === Number(autorId)
  );

  if (!nuevoPrincipal) return;

  const nextCoautores = all.filter(
    (item) => Number(item.autor_id) !== Number(autorId)
  );

  buildNormalizedFromParts(nuevoPrincipal, nextCoautores);
  announce(`${nuevoPrincipal.nombre_completo || "Autor"} ahora es el autor principal.`);
};

const setPrincipalById = (autorId) => {
  makePrincipal(Number(autorId));
};

const removePrincipal = () => {
  if (!principalAutor.value) return;

  const removedName = principalAutor.value.nombre_completo || "Autor";

  const restantes = selectedResolved.value.filter(
    (item) => Number(item.autor_id) !== Number(principalAutor.value.autor_id)
  );

  const nuevoPrincipal = restantes.length ? restantes[0] : null;
  const nextCoautores = restantes.slice(1);

  buildNormalizedFromParts(nuevoPrincipal, nextCoautores);
  announce(`Autor eliminado: ${removedName}.`);
};

const removeCoautor = (index) => {
  const principal = principalAutor.value ? { ...principalAutor.value } : null;
  const nextCoautores = [...coautores.value];
  const removed = nextCoautores[index];

  nextCoautores.splice(index, 1);
  buildNormalizedFromParts(principal, nextCoautores);

  clearDragState();
  announce(`Coautor eliminado: ${removed?.nombre_completo || "Autor"}.`);
};

const moveCoautorUp = (index) => {
  if (index <= 0) return;

  const principal = principalAutor.value ? { ...principalAutor.value } : null;
  const nextCoautores = [...coautores.value];

  [nextCoautores[index - 1], nextCoautores[index]] = [
    nextCoautores[index],
    nextCoautores[index - 1],
  ];

  buildNormalizedFromParts(principal, nextCoautores);
};

const moveCoautorDown = (index) => {
  if (index >= coautores.value.length - 1) return;

  const principal = principalAutor.value ? { ...principalAutor.value } : null;
  const nextCoautores = [...coautores.value];

  [nextCoautores[index + 1], nextCoautores[index]] = [
    nextCoautores[index],
    nextCoautores[index + 1],
  ];

  buildNormalizedFromParts(principal, nextCoautores);
};

const setCoautorOrden = (fromIndex, rawValue) => {
  const targetOrder = Number(rawValue);
  const targetIndex = targetOrder - 2;

  if (!Number.isInteger(targetOrder)) return;
  if (targetIndex < 0 || targetIndex >= coautores.value.length) return;
  if (fromIndex === targetIndex) return;

  const principal = principalAutor.value ? { ...principalAutor.value } : null;
  const nextCoautores = [...coautores.value];

  const [moved] = nextCoautores.splice(fromIndex, 1);
  nextCoautores.splice(targetIndex, 0, moved);

  buildNormalizedFromParts(principal, nextCoautores);
};

const clearDragState = () => {
  draggedCoautorIndex.value = null;
  dragOverCoautorIndex.value = null;
};

const reorderCoautores = (fromIndex, toIndex) => {
  if (fromIndex === toIndex) return;
  if (fromIndex == null || toIndex == null) return;
  if (fromIndex < 0 || toIndex < 0) return;
  if (fromIndex >= coautores.value.length || toIndex >= coautores.value.length) return;

  const principal = principalAutor.value ? { ...principalAutor.value } : null;
  const nextCoautores = [...coautores.value];

  const [moved] = nextCoautores.splice(fromIndex, 1);
  nextCoautores.splice(toIndex, 0, moved);

  buildNormalizedFromParts(principal, nextCoautores);
  announce("Orden de coautores actualizado.");
};

const onCoautorDragStart = (index, event) => {
  draggedCoautorIndex.value = index;
  dragOverCoautorIndex.value = index;

  if (event?.dataTransfer) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.dropEffect = "move";
    event.dataTransfer.setData("text/plain", String(index));
  }
};

const onCoautorDragEnter = (index) => {
  if (draggedCoautorIndex.value == null) return;
  if (draggedCoautorIndex.value === index) return;
  dragOverCoautorIndex.value = index;
};

const onCoautorDragOver = (index, event) => {
  if (draggedCoautorIndex.value == null) return;

  if (event?.dataTransfer) {
    event.dataTransfer.dropEffect = "move";
  }

  dragOverCoautorIndex.value = index;
};

const onCoautorDrop = (index) => {
  if (draggedCoautorIndex.value == null) return;

  reorderCoautores(draggedCoautorIndex.value, index);
  clearDragState();
};

const onCoautorDragEnd = () => {
  clearDragState();
};

const resolveApiError = (data) => {
  if (!data) return "";
  if (typeof data?.detail === "string") return data.detail;
  if (typeof data?.error === "string") return data.error;

  for (const key of [
    "identificacion",
    "correo",
    "nombres",
    "apellidos",
    "institucion",
    "usuario",
    "es_externo",
    "non_field_errors",
  ]) {
    const value = data?.[key];

    if (Array.isArray(value) && value[0]) return value[0];
    if (typeof value === "string" && value) return value;
  }

  return "";
};

const mergeAutor = (autor) => {
  const merged = normalizeAutores([autor, ...autores.value]);
  autores.value = merged;
};

const createDisabled = computed(() => {
  return (
    creating.value ||
    checkingDuplicate.value ||
    duplicateExists.value
  );
});

const useDuplicateAutor = async () => {
  if (!duplicateAutor.value) return;

  const duplicated = normalizeAutores([duplicateAutor.value])[0];
  if (!duplicated?.id) return;

  mergeAutor(duplicated);

  if (!isAlreadySelected(duplicated.id)) {
    selectFromList(duplicated);
  }

  modalState.value = "picker";
  search.value = duplicated.nombre_completo || "";
  resetCreateForm();

  await nextTick();
  searchInput.value?.focus?.();

  notifyAuthorAction(`Se usó el autor existente: ${duplicated.nombre_completo || "Autor"}.`);
};

const createAutor = async () => {
  if (!validateCreateForm()) return;

  creating.value = true;
  createError.value = "";

  try {
    const payload = {
      identificacion: digitsOnly(nuevo.value.identificacion),
      nombres: (nuevo.value.nombres || "").trim(),
      apellidos: (nuevo.value.apellidos || "").trim(),
      correo: cleanEmail(nuevo.value.correo),
      institucion: (nuevo.value.institucion || "").trim() || null,
      es_externo: true,
    };

    const res = await api.post("/autores/", payload);
    const responseAutor =
      res?.data?.autor ||
      res?.data?.data ||
      res?.data;

    const inserted = normalizeAutores([responseAutor])[0];

    if (!inserted?.id) {
      throw new Error("La respuesta del servidor no devolvió un autor válido.");
    }

    mergeAutor(inserted);

    if (!isAlreadySelected(inserted.id)) {
      selectFromList(inserted);
    }

    modalState.value = "picker";
    search.value = inserted.nombre_completo || "";
    resetCreateForm();

    await nextTick();
    searchInput.value?.focus?.();

    await refreshAutores(true);

    notifyAuthorAction(`Autor creado y agregado: ${inserted.nombre_completo || "Autor"}.`);
  } catch (e) {
    const data = e?.response?.data;

    createError.value =
      resolveApiError(data) ||
      "No se pudo crear el autor. Verifique los datos e intente nuevamente.";

    console.warn("Error creando autor:", e);
    await refreshAutores(true);
  } finally {
    creating.value = false;
  }
};

const getFocusableElements = (root) => {
  if (!root) return [];

  return [
    ...root.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ),
  ].filter(
    (el) =>
      !el.hasAttribute("disabled") &&
      el.getAttribute("aria-hidden") !== "true"
  );
};

const onKey = (e) => {
  if (!showPicker.value && !showCreate.value) return;

  if (e.key === "Escape") {
    e.preventDefault();

    if (showCreate.value) {
      closeCreate();
      return;
    }

    if (showPicker.value) {
      closePicker();
    }

    return;
  }

  if (e.key === "Tab") {
    const root = showCreate.value
      ? createDialog.value
      : showPicker.value
        ? pickerDialog.value
        : null;

    if (!root) return;

    const focusables = getFocusableElements(root);
    if (!focusables.length) return;

    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement;

    if (e.shiftKey && active === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault();
      first.focus();
    }
  }
};

watch(
  () => modalState.value,
  (value) => {
    document.body.classList.toggle("as-modal-open", !!value);

    if (!value) {
      returnToPickerAfterCreate.value = false;
      clearDragState();
    }
  }
);

watch(
  () => [
    nuevo.value.identificacion,
    nuevo.value.correo,
    nuevo.value.nombres,
    nuevo.value.apellidos,
    nuevo.value.institucion,
    showCreate.value,
  ],
  () => {
    if (!showCreate.value) return;

    validateTouchedFields();
    createError.value = "";
    scheduleDuplicateCheck();
  }
);

onMounted(async () => {
  loadFavoritos();
  window.addEventListener("keydown", onKey);
  await refreshAutores();
});

onBeforeUnmount(() => {
  refreshReq += 1;
  duplicateReq += 1;

  document.body.classList.remove("as-modal-open");
  window.removeEventListener("keydown", onKey);

  if (duplicateTimer) {
    window.clearTimeout(duplicateTimer);
    duplicateTimer = null;
  }

  if (announcementTimer) {
    window.clearTimeout(announcementTimer);
    announcementTimer = null;
  }

  if (confirmationTimer) {
    window.clearTimeout(confirmationTimer);
    confirmationTimer = null;
  }
});
</script>

<style scoped src="./autores-selector.css"></style>