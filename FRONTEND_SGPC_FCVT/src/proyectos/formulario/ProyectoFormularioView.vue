<template>
  <main class="pf-page">
    <section class="pf-shell">
      <header class="pf-hero page-stage page-hero">
        <div class="pf-hero__copy">
          <p class="pf-kicker">Proyectos</p>

          <h1 class="pf-title">
            {{ isEditMode ? "Editar proyecto" : "Nuevo proyecto" }}
          </h1>

          <p class="pf-subtitle">
            Registre el proyecto, su facultad, carrera, periodo académico y PDF de respaldo.
            Los profesores pueden vincularse después.
          </p>
        </div>

        <div class="pf-hero__meta" aria-label="Resumen">
          <span class="pf-pill">
            Estado: <strong>{{ estadoResumen }}</strong>
          </span>

          <span class="pf-pill">
            Periodo: <strong>{{ periodoResumen }}</strong>
          </span>

          <span class="pf-pill">
            Profesores: <strong>{{ profesoresResumen }}</strong>
          </span>
        </div>
      </header>

      <form
        class="pf-form pf-form--with-aside"
        enctype="multipart/form-data"
        @submit.prevent="guardarProyecto"
      >
        <main class="pf-main page-stage page-main">
          <section v-if="loadingProyecto" class="pf-card pf-state-card">
            <p class="pf-state-text">Cargando proyecto...</p>
          </section>

          <section
            v-else-if="loadProyectoError"
            class="pf-card pf-state-card pf-state-card--error"
            role="alert"
          >
            <h2 class="pf-state-title">No se pudo cargar</h2>
            <p class="pf-state-text">{{ loadProyectoError }}</p>

            <div class="pf-state-actions">
              <button
                type="button"
                class="pf-btn pf-btn--ghost"
                @click="volverListado"
              >
                Volver
              </button>

              <button
                type="button"
                class="pf-btn pf-btn--primary"
                @click="cargarProyecto"
              >
                Reintentar
              </button>
            </div>
          </section>

          <template v-else>
            <section
              id="pf-datos"
              class="pf-card"
              aria-labelledby="pf-datos-title"
            >
              <div class="pf-card__head">
                <div>
                  <p class="pf-section-kicker">Datos</p>

                  <h2 id="pf-datos-title" class="pf-card__title">
                    Información principal
                  </h2>
                </div>

                <p class="pf-card__desc">
                  Nombre, estado y descripción del proyecto.
                </p>
              </div>

              <div class="pf-grid">
                <div class="pf-field pf-col-8">
                  <label for="proyecto-nombre">
                    Nombre del proyecto
                    <span class="pf-req">*</span>
                  </label>

                  <input
                    id="proyecto-nombre"
                    ref="firstField"
                    v-model.trim="form.nombre"
                    type="text"
                    maxlength="255"
                    placeholder="Nombre oficial"
                    :disabled="saving"
                    :aria-invalid="showNombreError ? 'true' : 'false'"
                  />

                  <p v-if="showNombreError" class="pf-error" role="alert">
                    El nombre es obligatorio.
                  </p>
                </div>

                <div class="pf-field pf-col-4">
                  <label for="proyecto-estado">
                    Estado
                    <span class="pf-req">*</span>
                  </label>

                  <select
                    id="proyecto-estado"
                    v-model="form.estado"
                    class="pf-select"
                    :disabled="saving"
                  >
                    <option
                      v-for="opcion in estadoOptions"
                      :key="opcion.value"
                      :value="opcion.value"
                    >
                      {{ opcion.label }}
                    </option>
                  </select>

                  <p class="pf-help">
                    Para cerrar debe existir un investigador principal.
                  </p>
                </div>

                <div class="pf-field pf-col-12">
                  <label for="proyecto-descripcion">Descripción</label>

                  <textarea
                    id="proyecto-descripcion"
                    v-model.trim="form.descripcion"
                    rows="4"
                    maxlength="1200"
                    placeholder="Descripción breve"
                    :disabled="saving"
                  ></textarea>

                  <div class="pf-field-meta">
                    <span>{{ descripcionLength }}/1200</span>
                  </div>
                </div>
              </div>
            </section>

            <section
              id="pf-periodo"
              class="pf-card"
              aria-labelledby="pf-periodo-title"
            >
              <div class="pf-card__head">
                <div>
                  <p class="pf-section-kicker">Periodo</p>

                  <h2 id="pf-periodo-title" class="pf-card__title">
                    Periodo académico
                  </h2>
                </div>

                <p class="pf-card__desc">
                  Escriba el año y el periodo. Cada año tiene solo dos periodos: 1 y 2.
                </p>
              </div>

              <div class="pf-grid">
                <div class="pf-field pf-col-4">
                  <label for="proyecto-periodo-inicio">
                    Periodo de inicio
                    <span class="pf-req">*</span>
                  </label>

                  <input
                    id="proyecto-periodo-inicio"
                    v-model.trim="form.periodo_inicio"
                    type="text"
                    inputmode="numeric"
                    maxlength="6"
                    pattern="\\d{4}-[12]"
                    placeholder="Ej. 2026-1"
                    :disabled="saving"
                    :aria-invalid="showPeriodoInicioError ? 'true' : 'false'"
                    @input="normalizarPeriodoInput('periodo_inicio')"
                  />

                  <p class="pf-help">
                    Formato permitido: 2026-1 o 2026-2.
                  </p>

                  <p v-if="showPeriodoInicioError" class="pf-error" role="alert">
                    Ingrese un periodo válido. Ejemplo: 2026-1.
                  </p>
                </div>

                <div class="pf-field pf-col-4">
                  <label for="proyecto-periodo-fin">
                    Periodo final
                  </label>

                  <input
                    id="proyecto-periodo-fin"
                    v-model.trim="form.periodo_fin"
                    type="text"
                    inputmode="numeric"
                    maxlength="6"
                    pattern="\\d{4}-[12]"
                    placeholder="Ej. 2026-2"
                    :disabled="saving"
                    :aria-invalid="showPeriodoFinError ? 'true' : 'false'"
                    @input="normalizarPeriodoInput('periodo_fin')"
                  />

                  <p class="pf-help">
                    Opcional. Use el mismo formato.
                  </p>

                  <p v-if="showPeriodoFinError" class="pf-error" role="alert">
                    El periodo final debe ser válido y no puede ser menor al periodo inicial.
                  </p>
                </div>

                <div class="pf-period-preview pf-col-4">
                  <span>Periodo</span>
                  <strong>{{ periodoResumen }}</strong>
                </div>

                <div class="pf-field pf-col-4">
                  <label for="proyecto-fecha-inicio">Fecha de inicio</label>

                  <input
                    id="proyecto-fecha-inicio"
                    v-model="form.fecha_inicio"
                    type="date"
                    :disabled="saving"
                  />
                </div>

                <div class="pf-field pf-col-4">
                  <label for="proyecto-fecha-fin-planificada">
                    Fecha fin planificada
                  </label>

                  <input
                    id="proyecto-fecha-fin-planificada"
                    v-model="form.fecha_fin_planificada"
                    type="date"
                    :disabled="saving"
                  />
                </div>

                <div class="pf-field pf-col-4">
                  <label for="proyecto-fecha-fin-prorrogada">
                    Fecha prorrogada
                  </label>

                  <input
                    id="proyecto-fecha-fin-prorrogada"
                    v-model="form.fecha_fin_prorrogada"
                    type="date"
                    :disabled="saving"
                  />
                </div>

                <div class="pf-field pf-col-4">
                  <label for="proyecto-fecha-cierre">Fecha de cierre</label>

                  <input
                    id="proyecto-fecha-cierre"
                    v-model="form.fecha_cierre"
                    type="date"
                    :disabled="saving || form.estado !== 'cierre'"
                  />
                </div>
              </div>
            </section>

            <section
              id="pf-carrera"
              class="pf-card"
              aria-labelledby="pf-carrera-title"
            >
              <div class="pf-card__head">
                <div>
                  <p class="pf-section-kicker">Asignación</p>

                  <h2 id="pf-carrera-title" class="pf-card__title">
                    Facultad y carrera
                  </h2>
                </div>

                <p class="pf-card__desc">
                  Primero seleccione una facultad. Luego podrá escoger la carrera correspondiente.
                </p>
              </div>

              <div class="pf-grid">
                <div class="pf-field pf-col-4">
                  <label for="proyecto-facultad">
                    Facultad
                    <span class="pf-req">*</span>
                  </label>

                  <select
                    id="proyecto-facultad"
                    v-model="form.facultad"
                    class="pf-select"
                    :disabled="saving || loadingFacultades"
                    :aria-invalid="showFacultadError ? 'true' : 'false'"
                    @change="handleFacultadChange"
                  >
                    <option value="" disabled>
                      {{
                        loadingFacultades
                          ? "Cargando..."
                          : "Seleccione una facultad"
                      }}
                    </option>

                    <option
                      v-for="facultad in facultades"
                      :key="facultad.id"
                      :value="facultad.id"
                    >
                      {{ facultad.nombre }}
                    </option>
                  </select>

                  <p v-if="showFacultadError" class="pf-error" role="alert">
                    Seleccione una facultad.
                  </p>

                  <p v-if="errorFacultades" class="pf-error" role="alert">
                    {{ errorFacultades }}
                  </p>
                </div>

                <div class="pf-field pf-col-8">
                  <label for="proyecto-carrera">
                    Carrera
                    <span class="pf-req">*</span>
                  </label>

                  <div
                    ref="carreraRoot"
                    class="pf-combo"
                    :class="{
                      'is-open': carreraDropdownOpen,
                      'is-invalid': showCarreraError,
                      'is-disabled': !form.facultad || saving || loadingCarreras
                    }"
                  >
                    <div class="pf-combo__control">
                      <input
                        id="proyecto-carrera"
                        ref="carreraInput"
                        v-model="carreraQuery"
                        type="text"
                        role="combobox"
                        aria-autocomplete="list"
                        aria-haspopup="listbox"
                        :aria-expanded="carreraDropdownOpen ? 'true' : 'false'"
                        :aria-invalid="showCarreraError ? 'true' : 'false'"
                        :aria-busy="loadingCarreras ? 'true' : 'false'"
                        :placeholder="carreraPlaceholder"
                        autocomplete="off"
                        :disabled="!form.facultad || saving || loadingCarreras"
                        @focus="abrirCarreraDropdown"
                        @input="handleCarreraInput"
                        @keydown.down.prevent="moverCarrera(1)"
                        @keydown.up.prevent="moverCarrera(-1)"
                        @keydown.enter.prevent="seleccionarCarreraActiva"
                        @keydown.esc.prevent="cerrarCarreraDropdown"
                        @keydown.tab="cerrarCarreraDropdown"
                      />

                      <button
                        type="button"
                        class="pf-combo__button"
                        :disabled="!form.facultad || saving || loadingCarreras"
                        aria-label="Abrir carreras"
                        @click="toggleCarreraDropdown"
                      >
                        ⌄
                      </button>
                    </div>

                    <div v-if="carreraSeleccionada" class="pf-selected-box">
                      <div>
                        <strong>{{ carreraSeleccionada.nombre }}</strong>
                        <span>{{ facultadSeleccionada?.nombre || "Facultad seleccionada" }}</span>
                      </div>

                      <button
                        type="button"
                        class="pf-link-btn"
                        :disabled="saving"
                        @click="limpiarCarrera"
                      >
                        Cambiar
                      </button>
                    </div>

                    <div class="pf-combo__meta">
                      <span v-if="loadingCarreras" class="pf-mini-pill">
                        Cargando...
                      </span>

                      <span v-else class="pf-mini-pill">
                        {{ carrerasVisibles.length }} resultado{{
                          carrerasVisibles.length === 1 ? "" : "s"
                        }}
                      </span>

                      <button
                        v-if="errorCarreras"
                        type="button"
                        class="pf-link-btn"
                        :disabled="saving || loadingCarreras"
                        @click="cargarCarrerasPorFacultad(form.facultad)"
                      >
                        Reintentar
                      </button>
                    </div>

                    <transition name="dropdown-fade">
                      <div
                        v-if="carreraDropdownOpen"
                        class="pf-dropdown"
                        role="listbox"
                        aria-label="Carreras disponibles"
                      >
                        <div
                          v-if="!form.facultad"
                          class="pf-dropdown-state"
                        >
                          Seleccione una facultad para ver sus carreras.
                        </div>

                        <div
                          v-else-if="errorCarreras && !carrerasVisibles.length"
                          class="pf-dropdown-state pf-dropdown-state--error"
                          role="alert"
                        >
                          No se pudieron cargar las carreras.
                        </div>

                        <div
                          v-else-if="loadingCarreras"
                          class="pf-dropdown-state"
                        >
                          Cargando carreras...
                        </div>

                        <div
                          v-else-if="carrerasVisibles.length === 0"
                          class="pf-dropdown-state"
                        >
                          No hay coincidencias para “{{ carreraQuery }}”.
                        </div>

                        <template v-else>
                          <button
                            v-for="(carrera, index) in carrerasVisibles"
                            :key="carrera.id"
                            type="button"
                            class="pf-option"
                            :class="{
                              'is-active': index === carreraActiveIndex,
                              'is-selected': normalizeId(carrera.id) === normalizeId(form.carrera)
                            }"
                            role="option"
                            :aria-selected="
                              normalizeId(carrera.id) === normalizeId(form.carrera)
                                ? 'true'
                                : 'false'
                            "
                            @mousemove="carreraActiveIndex = index"
                            @mousedown.prevent="seleccionarCarrera(carrera)"
                          >
                            <span>
                              <strong>{{ carrera.nombre }}</strong>
                            </span>
                          </button>
                        </template>
                      </div>
                    </transition>
                  </div>

                  <p v-if="showCarreraError" class="pf-error" role="alert">
                    Seleccione una carrera válida.
                  </p>
                </div>
              </div>
            </section>

            <section
              id="pf-profesores"
              class="pf-card"
              aria-labelledby="pf-profesores-title"
            >
              <div class="pf-card__head">
                <div>
                  <p class="pf-section-kicker">Profesores</p>

                  <h2 id="pf-profesores-title" class="pf-card__title">
                    Equipo investigador
                  </h2>
                </div>

                <p class="pf-card__desc">
                  Puede completarlo después.
                </p>
              </div>

              <div class="pf-authors-layout">
                <div ref="autorRoot" class="pf-author-search">
                  <label for="proyecto-autor">
                    Buscar profesor
                  </label>

                  <div
                    class="pf-author-search__bar"
                    :class="{ 'is-open': autorDropdownOpen }"
                  >
                    <input
                      id="proyecto-autor"
                      ref="autorInput"
                      v-model="autorQuery"
                      type="text"
                      placeholder="Mínimo 2 caracteres"
                      autocomplete="off"
                      :disabled="saving"
                      @focus="handleAutorFocus"
                      @input="handleAutorInput"
                      @keydown.down.prevent="moverAutor(1)"
                      @keydown.up.prevent="moverAutor(-1)"
                      @keydown.enter.prevent="seleccionarAutorActivo"
                      @keydown.esc.prevent="cerrarAutorDropdown"
                      @keydown.tab="cerrarAutorDropdown"
                    />

                    <button
                      type="button"
                      class="pf-btn-inline"
                      :disabled="saving || autorQuery.trim().length < 2"
                      @click="buscarAutores"
                    >
                      Buscar
                    </button>
                  </div>

                  <div class="pf-combo__meta">
                    <span v-if="loadingAutores" class="pf-mini-pill">
                      Buscando...
                    </span>

                    <span v-else class="pf-mini-pill">
                      {{ autoresVisibles.length }} resultado{{
                        autoresVisibles.length === 1 ? "" : "s"
                      }}
                    </span>

                    <button
                      v-if="errorAutores"
                      type="button"
                      class="pf-link-btn"
                      :disabled="saving || loadingAutores"
                      @click="buscarAutores"
                    >
                      Reintentar
                    </button>
                  </div>

                  <transition name="dropdown-fade">
                    <div
                      v-if="autorDropdownOpen"
                      class="pf-dropdown pf-dropdown--authors"
                      role="listbox"
                      aria-label="Profesores disponibles"
                    >
                      <div
                        v-if="autorQuery.trim().length < 2"
                        class="pf-dropdown-state"
                      >
                        Escriba al menos 2 caracteres.
                      </div>

                      <div
                        v-else-if="loadingAutores"
                        class="pf-dropdown-state"
                      >
                        Buscando profesores...
                      </div>

                      <div
                        v-else-if="errorAutores && !autoresVisibles.length"
                        class="pf-dropdown-state pf-dropdown-state--error"
                        role="alert"
                      >
                        No se pudieron cargar los profesores.
                      </div>

                      <div
                        v-else-if="autoresVisibles.length === 0"
                        class="pf-dropdown-state"
                      >
                        No hay coincidencias para “{{ autorQuery }}”.
                      </div>

                      <template v-else>
                        <button
                          v-for="(autor, index) in autoresVisibles"
                          :key="autor.id"
                          type="button"
                          class="pf-option"
                          :class="{ 'is-active': index === autorActiveIndex }"
                          role="option"
                          :aria-selected="index === autorActiveIndex ? 'true' : 'false'"
                          @mousemove="autorActiveIndex = index"
                          @mousedown.prevent="agregarAutor(autor)"
                        >
                          <span>
                            <strong>{{ autor.nombre_completo }}</strong>
                            <small>{{ autor.correo || "Sin correo registrado" }}</small>
                          </span>

                          <em>{{ autor.es_externo ? "Externo" : "Interno" }}</em>
                        </button>
                      </template>
                    </div>
                  </transition>
                </div>

                <div class="pf-authors-selected">
                  <div class="pf-authors-selected__head">
                    <h3>Seleccionados</h3>
                    <span>{{ profesoresResumen }}</span>
                  </div>

                  <div
                    v-if="autoresSeleccionados.length === 0"
                    class="pf-empty-box"
                    :class="{ 'is-invalid': showAutoresError }"
                  >
                    Equipo pendiente. Puede guardar y completarlo después.
                  </div>

                  <div v-else class="pf-author-list">
                    <article
                      v-for="(autor, index) in autoresSeleccionados"
                      :key="autor.id"
                      class="pf-author-card"
                    >
                      <div class="pf-author-card__identity">
                        <strong>{{ autor.nombre_completo }}</strong>
                        <span>{{ autor.correo || "Sin correo registrado" }}</span>
                      </div>

                      <div class="pf-author-card__controls">
                        <label :for="`autor-rol-${autor.id}`">
                          Rol
                        </label>

                        <select
                          :id="`autor-rol-${autor.id}`"
                          v-model="autor.rol"
                          class="pf-select"
                          :disabled="saving"
                        >
                          <option
                            v-for="opcion in autorRolOptions"
                            :key="opcion.value"
                            :value="opcion.value"
                          >
                            {{ opcion.label }}
                          </option>
                        </select>
                      </div>

                      <div class="pf-author-card__footer">
                        <span>Orden {{ index + 1 }}</span>

                        <div class="pf-author-card__actions">
                          <button
                            type="button"
                            class="pf-icon-btn"
                            title="Subir"
                            aria-label="Subir profesor"
                            :disabled="saving || index === 0"
                            @click="moverAutorSeleccionado(index, -1)"
                          >
                            ↑
                          </button>

                          <button
                            type="button"
                            class="pf-icon-btn"
                            title="Bajar"
                            aria-label="Bajar profesor"
                            :disabled="saving || index === autoresSeleccionados.length - 1"
                            @click="moverAutorSeleccionado(index, 1)"
                          >
                            ↓
                          </button>

                          <button
                            type="button"
                            class="pf-icon-btn pf-icon-btn--danger"
                            title="Quitar"
                            aria-label="Quitar profesor"
                            :disabled="saving"
                            @click="quitarAutor(autor.id)"
                          >
                            ✕
                          </button>
                        </div>
                      </div>
                    </article>
                  </div>

                  <p v-if="showAutoresError" class="pf-error" role="alert">
                    Para cerrar debe existir un investigador principal.
                  </p>
                </div>
              </div>
            </section>

            <section
              id="pf-documento"
              class="pf-card"
              aria-labelledby="pf-documento-title"
            >
              <div class="pf-card__head">
                <div>
                  <p class="pf-section-kicker">PDF</p>

                  <h2 id="pf-documento-title" class="pf-card__title">
                    Documento del proyecto
                  </h2>
                </div>

                <p class="pf-card__desc">
                  PDF opcional. Máximo 5 MB.
                </p>
              </div>

              <div
                class="pf-upload"
                :class="{ 'is-dragover': pdfDragOver }"
                @dragenter.prevent="pdfDragOver = true"
                @dragover.prevent="handlePdfDragOver"
                @dragleave.prevent="handlePdfDragLeave"
                @drop.prevent="handlePdfDrop"
              >
                <div class="pf-upload__head">
                  <h3>Agregar PDF</h3>

                  <div class="pf-upload__chips">
                    <span>PDF</span>
                    <span>1 archivo</span>
                    <span>≤ 5 MB</span>
                  </div>
                </div>

                <label class="pf-upload__trigger" for="proyecto-pdf">
                  <input
                    id="proyecto-pdf"
                    ref="fileInput"
                    class="pf-upload__native"
                    type="file"
                    accept="application/pdf,.pdf"
                    :disabled="saving"
                    @change="handlePdfChange"
                  />

                  <span class="pf-upload__icon" aria-hidden="true">
                    PDF
                  </span>

                  <span class="pf-upload__copy">
                    <strong>Seleccionar PDF</strong>
                    <small>También puede arrastrar y soltar el archivo</small>
                  </span>
                </label>

                <p class="pf-upload__hint">
                  Formato permitido: PDF. Máximo 5 MB.
                </p>

                <article
                  v-if="form.archivo_pdf || archivoPdfActualUrl"
                  class="pf-file-chip"
                >
                  <div class="pf-file-chip__top">
                    <div class="pf-file-chip__main">
                      <span class="pf-file-chip__icon" aria-hidden="true">
                        PDF
                      </span>

                      <div class="pf-file-chip__body">
                        <strong>{{ pdfLabel }}</strong>

                        <span>
                          {{
                            form.archivo_pdf
                              ? prettyBytes(form.archivo_pdf.size)
                              : "Archivo registrado"
                          }}
                        </span>
                      </div>
                    </div>

                    <div class="pf-file-chip__actions">
                      <a
                        v-if="archivoPdfActualUrl && !form.archivo_pdf"
                        class="pf-link-btn pf-link-btn--anchor"
                        :href="archivoPdfActualUrl"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Ver PDF
                      </a>

                      <button
                        v-if="form.archivo_pdf"
                        type="button"
                        class="pf-file-chip__remove"
                        :disabled="saving"
                        @click="limpiarPdf"
                      >
                        Quitar
                      </button>
                    </div>
                  </div>

                  <div class="pf-file-chip__form">
                    <label for="proyecto-pdf-nombre">
                      Nombre personalizado
                    </label>

                    <input
                      id="proyecto-pdf-nombre"
                      v-model.trim="form.archivo_pdf_nombre"
                      type="text"
                      maxlength="150"
                      placeholder="Ej. Resolución del proyecto / Documento principal"
                      :disabled="saving"
                    />

                    <p>
                      Este nombre se enviará como referencia del documento.
                    </p>
                  </div>
                </article>

                <p v-if="pdfError" class="pf-error" role="alert">
                  {{ pdfError }}
                </p>
              </div>
            </section>
          </template>
        </main>

        <aside class="pf-aside page-stage page-aside" aria-label="Resumen">
          <section class="pf-summary">
            <div class="pf-summary__head">
              <p class="pf-section-kicker">Resumen</p>
              <h2 class="pf-summary__title">Registro</h2>
            </div>

            <div class="pf-progress">
              <div class="pf-progress__bar" aria-hidden="true">
                <span :style="{ width: `${completionPercent}%` }"></span>
              </div>

              <strong>{{ completionPercent }}%</strong>
            </div>

            <div class="pf-summary-list">
              <a
                href="#pf-datos"
                class="pf-summary-item"
                :class="{ 'is-complete': Boolean(form.nombre) }"
              >
                <span class="pf-summary-dot" aria-hidden="true"></span>

                <span>
                  <strong>Datos</strong>
                  <small>{{ form.nombre ? "Listo" : "Pendiente" }}</small>
                </span>
              </a>

              <a
                href="#pf-periodo"
                class="pf-summary-item"
                :class="{ 'is-complete': isValidPeriodo(form.periodo_inicio) }"
              >
                <span class="pf-summary-dot" aria-hidden="true"></span>

                <span>
                  <strong>Periodo</strong>
                  <small>{{ periodoResumen }}</small>
                </span>
              </a>

              <a
                href="#pf-carrera"
                class="pf-summary-item"
                :class="{ 'is-complete': Boolean(form.facultad && carreraSeleccionada) }"
              >
                <span class="pf-summary-dot" aria-hidden="true"></span>

                <span>
                  <strong>Asignación</strong>
                  <small>
                    {{ carreraSeleccionada?.nombre || facultadSeleccionada?.nombre || "Pendiente" }}
                  </small>
                </span>
              </a>

              <a
                href="#pf-profesores"
                class="pf-summary-item"
                :class="{ 'is-complete': !isEstadoCierre || hasPrincipalAutor }"
              >
                <span class="pf-summary-dot" aria-hidden="true"></span>

                <span>
                  <strong>Profesores</strong>
                  <small>{{ profesoresResumen }}</small>
                </span>
              </a>

              <a
                href="#pf-documento"
                class="pf-summary-item"
                :class="{ 'is-complete': Boolean(form.archivo_pdf || archivoPdfActualUrl) }"
              >
                <span class="pf-summary-dot" aria-hidden="true"></span>

                <span>
                  <strong>PDF</strong>
                  <small>
                    {{ form.archivo_pdf || archivoPdfActualUrl ? "Cargado" : "Opcional" }}
                  </small>
                </span>
              </a>
            </div>
          </section>

          <section class="pf-aside-card">
            <h3>Acciones</h3>

            <p>
              Complete los campos obligatorios. El PDF y los profesores pueden
              agregarse después.
            </p>

            <div v-if="saveError" class="pf-save-error" role="alert">
              {{ saveError }}
            </div>

            <div v-if="feedbackMessage" class="pf-save-ok" role="status">
              {{ feedbackMessage }}
            </div>

            <div class="pf-aside-actions">
              <button
                type="button"
                class="pf-btn pf-btn--ghost"
                :disabled="saving"
                @click="volverListado"
              >
                Cancelar
              </button>

              <button
                type="submit"
                class="pf-btn pf-btn--primary"
                :disabled="saving || loadingProyecto"
              >
                {{ saving ? "Guardando..." : "Guardar proyecto" }}
              </button>
            </div>
          </section>
        </aside>
      </form>
    </section>
  </main>
</template>

<script setup>
import {
  ref,
  computed,
  watch,
  onMounted,
  onBeforeUnmount,
  nextTick,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../../scripts/api/axios";

/* ============================================================
   ROUTER
============================================================ */
const route = useRoute();
const router = useRouter();

const isEditMode = computed(() => Boolean(route.params.id));
const proyectoId = computed(() => route.params.id);

/* ============================================================
   DOM REFS
============================================================ */
const firstField = ref(null);
const carreraRoot = ref(null);
const carreraInput = ref(null);
const autorRoot = ref(null);
const autorInput = ref(null);
const fileInput = ref(null);

/* ============================================================
   CONSTANTES
============================================================ */
const CURRENT_YEAR = new Date().getFullYear();
const MIN_YEAR = 2000;
const MAX_PDF_BYTES = 5 * 1024 * 1024;

const estadoOptions = [
  { value: "nuevo", label: "Nuevo" },
  { value: "arrastre", label: "Arrastre" },
  { value: "cierre", label: "Cierre" },
];

const autorRolOptions = [
  { value: "principal", label: "Investigador principal" },
  { value: "coinvestigador", label: "Coinvestigador" },
  { value: "colaborador", label: "Colaborador" },
];

/* ============================================================
   FORMULARIO
============================================================ */
const form = ref({
  nombre: "",
  descripcion: "",
  estado: "nuevo",
  facultad: "",
  carrera: "",
  periodo_inicio: `${CURRENT_YEAR}-1`,
  periodo_fin: "",
  fecha_inicio: "",
  fecha_fin_planificada: "",
  fecha_fin_prorrogada: "",
  fecha_cierre: "",
  archivo_pdf: null,
  archivo_pdf_nombre: "",
});

const loadingProyecto = ref(false);
const loadProyectoError = ref("");
const saving = ref(false);
const saveError = ref("");
const feedbackMessage = ref("");
const triedSubmit = ref(false);

/* ============================================================
   FACULTADES / CARRERAS
============================================================ */
const facultades = ref([]);
const loadingFacultades = ref(false);
const errorFacultades = ref("");

const carreras = ref([]);
const loadingCarreras = ref(false);
const errorCarreras = ref("");
const carreraQuery = ref("");
const carreraDropdownOpen = ref(false);
const carreraActiveIndex = ref(0);

/* ============================================================
   AUTORES
============================================================ */
const autores = ref([]);
const autoresSeleccionados = ref([]);
const loadingAutores = ref(false);
const errorAutores = ref("");
const autorQuery = ref("");
const autorDropdownOpen = ref(false);
const autorActiveIndex = ref(0);
let autorSearchTimer = null;
let autorAbortController = null;

/* ============================================================
   PDF
============================================================ */
const pdfError = ref("");
const archivoPdfActualUrl = ref("");
const pdfDragOver = ref(false);

/* ============================================================
   HELPERS
============================================================ */
function normalizeId(value) {
  return value == null ? "" : String(value);
}

function normalizeText(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^\p{L}\p{N}\s@._-]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function toApiId(value) {
  const id = normalizeId(value);
  return /^\d+$/.test(id) ? Number(id) : id;
}

function normalizeDate(value) {
  if (!value) return "";
  return String(value).slice(0, 10);
}

function prettyBytes(bytes) {
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
}

function prettyError(value) {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(prettyError).join(", ");

  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, val]) => `${key}: ${prettyError(val)}`)
      .join(" | ");
  }

  return String(value);
}

function appendIfValue(formData, key, value) {
  if (value === undefined || value === null || value === "") return;
  formData.append(key, value);
}

function getYearFromPeriod(periodo) {
  const match = String(periodo || "").match(/^(\d{4})-[12]$/);
  return match ? match[1] : "";
}

function parsePeriodIndex(periodo) {
  const match = String(periodo || "").match(/^(\d{4})-([12])$/);

  if (!match) return null;

  const year = Number(match[1]);
  const half = Number(match[2]);

  if (!Number.isInteger(year) || ![1, 2].includes(half)) return null;

  return year * 2 + half;
}

function buildPeriodFromYear(year, suffix = 1) {
  const parsed = Number(year);

  if (!Number.isInteger(parsed) || parsed < MIN_YEAR) {
    return "";
  }

  const safeSuffix = suffix === 2 ? 2 : 1;
  return `${parsed}-${safeSuffix}`;
}

function isValidPeriodo(value) {
  return /^\d{4}-[12]$/.test(String(value || "").trim());
}

function normalizarPeriodoInput(field) {
  const digits = String(form.value[field] || "")
    .replace(/\D/g, "")
    .slice(0, 5);

  if (!digits) {
    form.value[field] = "";
    return;
  }

  if (digits.length <= 4) {
    form.value[field] = digits;
    return;
  }

  form.value[field] = `${digits.slice(0, 4)}-${digits.slice(4, 5)}`;
}

function isPdfFile(file) {
  if (!file) return false;

  const name = String(file.name || "").toLowerCase();
  return file.type === "application/pdf" || name.endsWith(".pdf");
}

function extractArray(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
}

/* ============================================================
   PERIODOS
============================================================ */
const periodoInicioIndex = computed(() =>
  parsePeriodIndex(form.value.periodo_inicio)
);

const periodoFinIndex = computed(() =>
  parsePeriodIndex(form.value.periodo_fin)
);

function syncAniosDesdePeriodos() {
  const inicio = getYearFromPeriod(form.value.periodo_inicio);
  const fin = getYearFromPeriod(form.value.periodo_fin);

  return {
    anio_inicio: inicio,
    anio_fin: fin,
  };
}

/* ============================================================
   COMPUTEDS
============================================================ */
const isEstadoCierre = computed(() => form.value.estado === "cierre");

const hasPrincipalAutor = computed(() => {
  return autoresSeleccionados.value.some(
    (autor) => String(autor.rol || "").trim().toLowerCase() === "principal"
  );
});

const profesoresResumen = computed(() => {
  const total = autoresSeleccionados.value.length;

  if (total > 0) {
    return `${total} vinculado${total === 1 ? "" : "s"}`;
  }

  return isEstadoCierre.value ? "Requerido" : "Opcional";
});

const estadoResumen = computed(() => {
  return (
    estadoOptions.find((item) => item.value === form.value.estado)?.label ||
    "Nuevo"
  );
});

const periodoResumen = computed(() => {
  const inicio = form.value.periodo_inicio;
  const fin = form.value.periodo_fin;

  if (inicio && fin) return `${inicio} · ${fin}`;
  if (inicio) return `Desde ${inicio}`;

  return "Sin definir";
});

const descripcionLength = computed(() => {
  return String(form.value.descripcion || "").length;
});

const pdfLabel = computed(() => {
  if (form.value.archivo_pdf) {
    return form.value.archivo_pdf.name;
  }

  if (archivoPdfActualUrl.value) {
    return form.value.archivo_pdf_nombre || "PDF registrado";
  }

  return "Sin PDF";
});

const facultadSeleccionada = computed(() => {
  return (
    facultades.value.find(
      (item) => normalizeId(item.id) === normalizeId(form.value.facultad)
    ) || null
  );
});

const carreraSeleccionada = computed(() => {
  return (
    carreras.value.find(
      (item) => normalizeId(item.id) === normalizeId(form.value.carrera)
    ) || null
  );
});

const carreraPlaceholder = computed(() => {
  if (!form.value.facultad) return "Seleccione primero una facultad";
  if (loadingCarreras.value) return "Cargando carreras...";
  return "Buscar carrera";
});

const showNombreError = computed(() => {
  return triedSubmit.value && !String(form.value.nombre || "").trim();
});

const showFacultadError = computed(() => {
  return triedSubmit.value && !form.value.facultad;
});

const showCarreraError = computed(() => {
  return triedSubmit.value && !form.value.carrera;
});

const showPeriodoInicioError = computed(() => {
  return triedSubmit.value && !isValidPeriodo(form.value.periodo_inicio);
});

const showPeriodoFinError = computed(() => {
  if (!triedSubmit.value) return false;
  if (!form.value.periodo_fin) return false;

  if (!isValidPeriodo(form.value.periodo_fin)) return true;
  if (!isValidPeriodo(form.value.periodo_inicio)) return false;

  return periodoFinIndex.value < periodoInicioIndex.value;
});

const showAutoresError = computed(() => {
  return triedSubmit.value && isEstadoCierre.value && !hasPrincipalAutor.value;
});

const completionPercent = computed(() => {
  const checks = [
    Boolean(String(form.value.nombre || "").trim()),
    isValidPeriodo(form.value.periodo_inicio),
    Boolean(form.value.facultad),
    Boolean(carreraSeleccionada.value),
    !isEstadoCierre.value || hasPrincipalAutor.value,
  ];

  const complete = checks.filter(Boolean).length;

  return Math.round((complete / checks.length) * 100);
});

/* ============================================================
   WATCHERS
============================================================ */
watch(
  () => form.value.estado,
  (estado) => {
    if (estado === "cierre" && !form.value.fecha_cierre) {
      form.value.fecha_cierre = new Date().toISOString().slice(0, 10);
    }

    if (estado !== "cierre") {
      form.value.fecha_cierre = "";
    }
  }
);

/* ============================================================
   HIDRATACIÓN
============================================================ */
function resetForm() {
  form.value = {
    nombre: "",
    descripcion: "",
    estado: "nuevo",
    facultad: "",
    carrera: "",
    periodo_inicio: `${CURRENT_YEAR}-1`,
    periodo_fin: "",
    fecha_inicio: "",
    fecha_fin_planificada: "",
    fecha_fin_prorrogada: "",
    fecha_cierre: "",
    archivo_pdf: null,
    archivo_pdf_nombre: "",
  };

  carreras.value = [];
  carreraQuery.value = "";
  autoresSeleccionados.value = [];
  archivoPdfActualUrl.value = "";
  pdfError.value = "";
  saveError.value = "";
  feedbackMessage.value = "";
  triedSubmit.value = false;
  pdfDragOver.value = false;

  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

function resolveFacultadIdFromData(data) {
  const direct =
    data?.facultad_id ||
    data?.facultad?.id ||
    data?.carrera_facultad_id ||
    data?.facultad;

  if (direct && /^\d+$/.test(String(direct))) {
    return normalizeId(direct);
  }

  const nombre = String(
    data?.facultad_nombre ||
      data?.facultad?.nombre ||
      data?.facultad ||
      ""
  ).trim();

  if (!nombre) return "";

  const match = facultades.value.find(
    (item) => normalizeText(item.nombre) === normalizeText(nombre)
  );

  return match ? normalizeId(match.id) : "";
}

function buildAutoresFromProyecto(data) {
  const source = Array.isArray(data?.autores)
    ? data.autores
    : Array.isArray(data?.autores_resumen)
      ? data.autores_resumen
      : [];

  return source
    .map((item, index) => {
      const id = item.id || item.autor_id || item.autor;

      if (!id) return null;

      const nombres = item.nombres || "";
      const apellidos = item.apellidos || "";

      const nombre =
        item.nombre_completo ||
        item.nombre ||
        `${nombres} ${apellidos}`.trim() ||
        `Autor #${id}`;

      return {
        id: normalizeId(id),
        nombres,
        apellidos,
        nombre_completo: nombre,
        correo: item.correo || item.email || "",
        es_externo: Boolean(item.es_externo),
        rol: item.rol || "principal",
        orden: Number(item.orden || index + 1),
      };
    })
    .filter(Boolean)
    .sort((a, b) => Number(a.orden || 0) - Number(b.orden || 0));
}

function hydrateForm(data) {
  const anioInicio = data.anio_inicio || CURRENT_YEAR;
  const anioFin = data.anio_fin || "";
  const facultadId = resolveFacultadIdFromData(data);

  form.value = {
    nombre: data.nombre || "",
    descripcion: data.descripcion || "",
    estado: data.estado || "nuevo",
    facultad: facultadId,
    carrera: normalizeId(data.carrera_id || data.carrera || ""),
    periodo_inicio:
      data.periodo_inicio ||
      data.periodo_academico_inicio ||
      buildPeriodFromYear(anioInicio, 1),
    periodo_fin:
      data.periodo_fin ||
      data.periodo_academico_fin ||
      (anioFin ? buildPeriodFromYear(anioFin, 2) : ""),
    fecha_inicio: normalizeDate(data.fecha_inicio),
    fecha_fin_planificada: normalizeDate(data.fecha_fin_planificada),
    fecha_fin_prorrogada: normalizeDate(data.fecha_fin_prorrogada),
    fecha_cierre: normalizeDate(data.fecha_cierre),
    archivo_pdf: null,
    archivo_pdf_nombre:
      data.archivo_pdf_nombre ||
      data.nombre_archivo_pdf ||
      data.pdf_nombre ||
      "",
  };

  autoresSeleccionados.value = buildAutoresFromProyecto(data);
  archivoPdfActualUrl.value = data.archivo_pdf_url || data.archivo_pdf || "";
  pdfError.value = "";
  saveError.value = "";
  triedSubmit.value = false;

  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

async function cargarProyecto() {
  if (!isEditMode.value) {
    resetForm();

    nextTick(() => {
      firstField.value?.focus();
    });

    return;
  }

  loadingProyecto.value = true;
  loadProyectoError.value = "";

  try {
    const res = await api.get(`/proyectos/${proyectoId.value}/`);
    hydrateForm(res.data || {});

    if (form.value.facultad) {
      await cargarCarrerasPorFacultad(form.value.facultad);
      syncCarreraQueryFromSelection();
    }
  } catch (error) {
    console.error("Error cargando proyecto:", error);
    loadProyectoError.value =
      error?.response?.data
        ? prettyError(error.response.data)
        : "No se pudo obtener la información del proyecto.";
  } finally {
    loadingProyecto.value = false;
  }
}

/* ============================================================
   FACULTADES
============================================================ */
function normalizeFacultad(item) {
  return {
    id: normalizeId(item?.id),
    nombre: String(item?.nombre || item?.label || "").trim(),
  };
}

function sortFacultades(list) {
  return [...list].sort((a, b) =>
    String(a?.nombre || "").localeCompare(String(b?.nombre || ""), "es", {
      sensitivity: "base",
    })
  );
}

async function cargarFacultades() {
  loadingFacultades.value = true;
  errorFacultades.value = "";

  try {
    const res = await api.get("/selects/facultades/");
    facultades.value = sortFacultades(
      extractArray(res.data).map(normalizeFacultad).filter((item) => item.id)
    );

    if (!facultades.value.length) {
      errorFacultades.value = "No hay facultades disponibles.";
    }
  } catch (error) {
    console.error("Error cargando facultades:", error);
    facultades.value = [];
    errorFacultades.value = "No se pudieron cargar las facultades.";
  } finally {
    loadingFacultades.value = false;
  }
}

async function handleFacultadChange() {
  form.value.carrera = "";
  carreraQuery.value = "";
  carreras.value = [];
  cerrarCarreraDropdown();

  if (!form.value.facultad) return;

  await cargarCarrerasPorFacultad(form.value.facultad);

  await nextTick();
  abrirCarreraDropdown();
  carreraInput.value?.focus?.();
}

/* ============================================================
   CARRERAS
============================================================ */
function normalizeCarrera(item, facultad = "") {
  return {
    id: normalizeId(item?.id),
    nombre: item?.nombre || item?.label || "",
    facultad: item?.facultad || item?.facultad_nombre || facultad || "",
  };
}

function sortCarreras(list) {
  return [...list].sort((a, b) =>
    String(a?.nombre || "").localeCompare(String(b?.nombre || ""), "es", {
      sensitivity: "base",
    })
  );
}

async function cargarCarrerasPorFacultad(facultadId) {
  if (!facultadId) {
    carreras.value = [];
    return;
  }

  loadingCarreras.value = true;
  errorCarreras.value = "";

  try {
    const facultadNombre =
      facultades.value.find((item) => normalizeId(item.id) === normalizeId(facultadId))
        ?.nombre || "";

    const res = await api.get(`/selects/carreras/${facultadId}/`);
    const source = extractArray(res.data);

    carreras.value = sortCarreras(
      source
        .map((item) => normalizeCarrera(item, facultadNombre))
        .filter((item) => item.id)
    );

    if (!carreras.value.length) {
      errorCarreras.value = "No hay carreras disponibles para esta facultad.";
    }
  } catch (error) {
    console.error("Error cargando carreras:", error);
    carreras.value = [];
    errorCarreras.value = "No se pudieron cargar las carreras de la facultad.";
  } finally {
    loadingCarreras.value = false;
  }
}

function buildCarreraScore(carrera, query) {
  if (!query) return 1;

  const nombre = normalizeText(carrera?.nombre);
  const tokens = query.split(" ").filter(Boolean);

  let score = 0;

  if (nombre.startsWith(query)) score += 12;
  if (nombre.includes(query)) score += 7;

  for (const token of tokens) {
    if (nombre.startsWith(token)) score += 3;
    else if (nombre.includes(token)) score += 2;
  }

  return score;
}

const carrerasVisibles = computed(() => {
  const query = normalizeText(carreraQuery.value);

  if (!form.value.facultad) return [];

  if (!query) {
    return sortCarreras(carreras.value).slice(0, 80);
  }

  return carreras.value
    .map((carrera) => ({
      carrera,
      score: buildCarreraScore(carrera, query),
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;

      return String(a.carrera.nombre || "").localeCompare(
        String(b.carrera.nombre || ""),
        "es",
        { sensitivity: "base" }
      );
    })
    .slice(0, 80)
    .map((item) => item.carrera);
});

function abrirCarreraDropdown() {
  if (!form.value.facultad || loadingCarreras.value) return;

  cerrarAutorDropdown();
  carreraDropdownOpen.value = true;
  carreraActiveIndex.value = 0;
}

function cerrarCarreraDropdown() {
  carreraDropdownOpen.value = false;
}

function toggleCarreraDropdown() {
  if (!form.value.facultad || loadingCarreras.value) return;

  if (carreraDropdownOpen.value) {
    cerrarCarreraDropdown();
  } else {
    abrirCarreraDropdown();
  }

  nextTick(() => carreraInput.value?.focus());
}

function handleCarreraInput() {
  form.value.carrera = "";
  carreraDropdownOpen.value = true;
  carreraActiveIndex.value = 0;
}

function moverCarrera(direction) {
  if (!carreraDropdownOpen.value) {
    abrirCarreraDropdown();
  }

  const max = carrerasVisibles.value.length - 1;

  if (max < 0) return;

  const next = carreraActiveIndex.value + direction;

  if (next < 0) carreraActiveIndex.value = 0;
  else if (next > max) carreraActiveIndex.value = max;
  else carreraActiveIndex.value = next;
}

function seleccionarCarreraActiva() {
  const carrera = carrerasVisibles.value[carreraActiveIndex.value];

  if (carrera) {
    seleccionarCarrera(carrera);
  }
}

function seleccionarCarrera(carrera) {
  form.value.carrera = normalizeId(carrera.id);
  carreraQuery.value = carrera.nombre;
  cerrarCarreraDropdown();
}

function limpiarCarrera() {
  form.value.carrera = "";
  carreraQuery.value = "";
  abrirCarreraDropdown();

  nextTick(() => carreraInput.value?.focus());
}

function syncCarreraQueryFromSelection() {
  if (!form.value.carrera) {
    carreraQuery.value = "";
    return;
  }

  const carrera = carreras.value.find(
    (item) => normalizeId(item.id) === normalizeId(form.value.carrera)
  );

  carreraQuery.value = carrera ? carrera.nombre : carreraQuery.value;
}

watch(carrerasVisibles, (list) => {
  if (!list.length) {
    carreraActiveIndex.value = 0;
    return;
  }

  if (carreraActiveIndex.value > list.length - 1) {
    carreraActiveIndex.value = 0;
  }
});

/* ============================================================
   AUTORES
============================================================ */
function normalizeAutor(item) {
  const id = item?.id || item?.autor_id || item?.value;
  const nombres = item?.nombres || "";
  const apellidos = item?.apellidos || "";

  const nombre =
    item?.nombre_completo ||
    item?.nombre ||
    item?.label ||
    `${nombres} ${apellidos}`.trim();

  return {
    id: normalizeId(id),
    nombres,
    apellidos,
    nombre_completo: String(nombre || "").trim() || `Autor #${id}`,
    correo: item?.correo || item?.email || "",
    es_externo: Boolean(item?.es_externo),
  };
}

function sortAutores(list) {
  return [...list].sort((a, b) =>
    String(a?.nombre_completo || "").localeCompare(
      String(b?.nombre_completo || ""),
      "es",
      { sensitivity: "base" }
    )
  );
}

function buildAutorScore(autor, query) {
  if (!query) return 1;

  const nombre = normalizeText(autor?.nombre_completo);
  const correo = normalizeText(autor?.correo);
  const full = `${nombre} ${correo}`.trim();
  const tokens = query.split(" ").filter(Boolean);

  let score = 0;

  if (nombre.startsWith(query)) score += 12;
  if (nombre.includes(query)) score += 7;
  if (correo.includes(query)) score += 4;
  if (full.includes(query)) score += 5;

  for (const token of tokens) {
    if (nombre.startsWith(token)) score += 3;
    else if (nombre.includes(token)) score += 2;

    if (correo.includes(token)) score += 1;
  }

  return score;
}

const autoresVisibles = computed(() => {
  const selectedIds = new Set(
    autoresSeleccionados.value.map((item) => normalizeId(item.id))
  );

  const available = autores.value.filter(
    (item) => !selectedIds.has(normalizeId(item.id))
  );

  const query = normalizeText(autorQuery.value);

  return available
    .map((autor) => ({
      autor,
      score: buildAutorScore(autor, query),
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;

      return String(a.autor.nombre_completo || "").localeCompare(
        String(b.autor.nombre_completo || ""),
        "es",
        { sensitivity: "base" }
      );
    })
    .slice(0, 60)
    .map((item) => item.autor);
});

function handleAutorFocus() {
  cerrarCarreraDropdown();
  autorDropdownOpen.value = true;
}

function handleAutorInput() {
  errorAutores.value = "";
  autorDropdownOpen.value = true;
  autorActiveIndex.value = 0;

  clearTimeout(autorSearchTimer);

  if (autorQuery.value.trim().length < 2) {
    autores.value = [];
    return;
  }

  autorSearchTimer = setTimeout(() => {
    buscarAutores();
  }, 280);
}

async function buscarAutores() {
  const query = autorQuery.value.trim();

  if (query.length < 2) {
    autores.value = [];
    autorDropdownOpen.value = true;
    return;
  }

  autorAbortController?.abort?.();

  const controller = new AbortController();
  autorAbortController = controller;

  loadingAutores.value = true;
  errorAutores.value = "";
  autorDropdownOpen.value = true;

  try {
    const res = await api.get("/selects/autores/", {
      params: { q: query },
      signal: controller.signal,
    });

    if (autorAbortController !== controller) return;

    const source = extractArray(res.data);
    const normalized = source.map(normalizeAutor).filter((item) => item.id);

    autores.value = sortAutores(normalized);
  } catch (error) {
    if (error?.name === "CanceledError" || error?.code === "ERR_CANCELED") {
      return;
    }

    console.error("Error buscando autores:", error);
    autores.value = [];
    errorAutores.value = "No se pudieron cargar los profesores.";
  } finally {
    if (autorAbortController === controller) {
      loadingAutores.value = false;
    }
  }
}

function cerrarAutorDropdown() {
  autorDropdownOpen.value = false;
}

function moverAutor(direction) {
  if (!autorDropdownOpen.value) {
    autorDropdownOpen.value = true;
  }

  const max = autoresVisibles.value.length - 1;

  if (max < 0) return;

  const next = autorActiveIndex.value + direction;

  if (next < 0) autorActiveIndex.value = 0;
  else if (next > max) autorActiveIndex.value = max;
  else autorActiveIndex.value = next;
}

function seleccionarAutorActivo() {
  const autor = autoresVisibles.value[autorActiveIndex.value];

  if (autor) {
    agregarAutor(autor);
  }
}

function agregarAutor(autor) {
  const id = normalizeId(autor?.id);

  if (!id) return;

  const exists = autoresSeleccionados.value.some(
    (item) => normalizeId(item.id) === id
  );

  if (exists) return;

  autoresSeleccionados.value.push({
    ...autor,
    id,
    rol: autoresSeleccionados.value.length === 0 ? "principal" : "coinvestigador",
    orden: autoresSeleccionados.value.length + 1,
  });

  autorQuery.value = "";
  autores.value = [];
  autorDropdownOpen.value = false;
  feedbackMessage.value = "Profesor agregado.";
}

function quitarAutor(id) {
  const normalized = normalizeId(id);

  autoresSeleccionados.value = autoresSeleccionados.value
    .filter((item) => normalizeId(item.id) !== normalized)
    .map((item, index) => ({
      ...item,
      orden: index + 1,
    }));
}

function moverAutorSeleccionado(index, direction) {
  const nextIndex = index + direction;

  if (nextIndex < 0 || nextIndex >= autoresSeleccionados.value.length) return;

  const list = [...autoresSeleccionados.value];
  const temp = list[index];

  list[index] = list[nextIndex];
  list[nextIndex] = temp;

  autoresSeleccionados.value = list.map((item, itemIndex) => ({
    ...item,
    orden: itemIndex + 1,
  }));
}

watch(autoresVisibles, (list) => {
  if (!list.length) {
    autorActiveIndex.value = 0;
    return;
  }

  if (autorActiveIndex.value > list.length - 1) {
    autorActiveIndex.value = 0;
  }
});

/* ============================================================
   PDF
============================================================ */
function setPdfFile(file) {
  pdfError.value = "";

  if (!file) {
    form.value.archivo_pdf = null;
    return;
  }

  if (!isPdfFile(file)) {
    pdfError.value = "Solo se permiten archivos PDF.";
    form.value.archivo_pdf = null;

    if (fileInput.value) {
      fileInput.value.value = "";
    }

    return;
  }

  if (file.size > MAX_PDF_BYTES) {
    pdfError.value = "El PDF supera el tamaño máximo de 5 MB.";
    form.value.archivo_pdf = null;

    if (fileInput.value) {
      fileInput.value.value = "";
    }

    return;
  }

  form.value.archivo_pdf = file;

  if (!form.value.archivo_pdf_nombre) {
    form.value.archivo_pdf_nombre = file.name.replace(/\.pdf$/i, "");
  }
}

function handlePdfChange(event) {
  const file = event.target.files?.[0] || null;
  setPdfFile(file);
}

function handlePdfDragOver(event) {
  pdfDragOver.value = true;

  if (event?.dataTransfer) {
    event.dataTransfer.dropEffect = "copy";
  }
}

function handlePdfDragLeave(event) {
  const current = event.currentTarget;
  const related = event.relatedTarget;

  if (current && related && current.contains?.(related)) return;

  pdfDragOver.value = false;
}

function handlePdfDrop(event) {
  pdfDragOver.value = false;

  const file = Array.from(event?.dataTransfer?.files || [])[0] || null;
  setPdfFile(file);
}

function limpiarPdf() {
  form.value.archivo_pdf = null;
  form.value.archivo_pdf_nombre = "";
  pdfError.value = "";

  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

/* ============================================================
   PAYLOAD
============================================================ */
function buildAutoresPayload() {
  return autoresSeleccionados.value.map((autor, index) => ({
    autor_id: toApiId(autor.id),
    rol: autor.rol || (index === 0 ? "principal" : "coinvestigador"),
    orden: index + 1,
  }));
}

function buildPayload() {
  const formData = new FormData();
  const periodYears = syncAniosDesdePeriodos();

  formData.append("nombre", String(form.value.nombre || "").trim());
  formData.append("descripcion", String(form.value.descripcion || "").trim());
  formData.append("estado", form.value.estado || "nuevo");
  formData.append("carrera", toApiId(form.value.carrera));

  appendIfValue(formData, "fecha_inicio", form.value.fecha_inicio);
  appendIfValue(formData, "fecha_fin_planificada", form.value.fecha_fin_planificada);
  appendIfValue(formData, "fecha_fin_prorrogada", form.value.fecha_fin_prorrogada);
  appendIfValue(formData, "fecha_cierre", form.value.fecha_cierre);

  appendIfValue(formData, "anio_inicio", periodYears.anio_inicio);
  appendIfValue(formData, "anio_fin", periodYears.anio_fin);

  formData.append("periodo_inicio", form.value.periodo_inicio);
  appendIfValue(formData, "periodo_fin", form.value.periodo_fin);

  formData.append("autores_data", JSON.stringify(buildAutoresPayload()));

  if (form.value.archivo_pdf) {
    formData.append("archivo_pdf", form.value.archivo_pdf);
  }

  appendIfValue(
    formData,
    "archivo_pdf_nombre",
    String(form.value.archivo_pdf_nombre || "").trim()
  );

  return formData;
}

/* ============================================================
   VALIDACIÓN / GUARDADO
============================================================ */
function validateBeforeSave() {
  triedSubmit.value = true;
  saveError.value = "";
  feedbackMessage.value = "";

  if (!String(form.value.nombre || "").trim()) {
    saveError.value = "El nombre del proyecto es obligatorio.";
    nextTick(() => firstField.value?.focus());
    return false;
  }

  if (!form.value.facultad) {
    saveError.value = "Seleccione una facultad.";
    return false;
  }

  if (!form.value.carrera) {
    saveError.value = "Seleccione una carrera.";
    abrirCarreraDropdown();
    nextTick(() => carreraInput.value?.focus());
    return false;
  }

  if (!isValidPeriodo(form.value.periodo_inicio)) {
    saveError.value = "Ingrese un periodo de inicio válido. Ejemplo: 2026-1.";
    return false;
  }

  if (form.value.periodo_fin && !isValidPeriodo(form.value.periodo_fin)) {
    saveError.value = "Ingrese un periodo final válido. Ejemplo: 2026-2.";
    return false;
  }

  if (
    form.value.periodo_inicio &&
    form.value.periodo_fin &&
    periodoFinIndex.value < periodoInicioIndex.value
  ) {
    saveError.value = "El periodo final no puede ser menor al periodo inicial.";
    return false;
  }

  if (form.value.fecha_inicio && form.value.fecha_fin_planificada) {
    if (form.value.fecha_fin_planificada < form.value.fecha_inicio) {
      saveError.value =
        "La fecha fin planificada no puede ser menor a la fecha de inicio.";
      return false;
    }
  }

  if (form.value.fecha_inicio && form.value.fecha_fin_prorrogada) {
    if (form.value.fecha_fin_prorrogada < form.value.fecha_inicio) {
      saveError.value =
        "La fecha prorrogada no puede ser menor a la fecha de inicio.";
      return false;
    }
  }

  if (form.value.fecha_fin_planificada && form.value.fecha_fin_prorrogada) {
    if (form.value.fecha_fin_prorrogada < form.value.fecha_fin_planificada) {
      saveError.value =
        "La fecha prorrogada no puede ser menor a la fecha planificada.";
      return false;
    }
  }

  if (isEstadoCierre.value && !hasPrincipalAutor.value) {
    saveError.value =
      "Para cerrar el proyecto debe existir un investigador principal.";
    nextTick(() => autorInput.value?.focus());
    return false;
  }

  if (pdfError.value) {
    saveError.value = pdfError.value;
    return false;
  }

  return true;
}

async function guardarProyecto() {
  if (!validateBeforeSave()) return;

  saving.value = true;
  saveError.value = "";
  feedbackMessage.value = "";

  try {
    const payload = buildPayload();

    if (isEditMode.value) {
      await api.patch(`/proyectos/${proyectoId.value}/`, payload);
    } else {
      await api.post("/proyectos/", payload);
    }

    router.push({
      name: "ProyectosListado",
      query: { guardado: "1" },
    });
  } catch (error) {
    console.error("Error guardando proyecto:", error);

    saveError.value =
      error?.response?.data
        ? prettyError(error.response.data)
        : "No se pudo guardar el proyecto.";
  } finally {
    saving.value = false;
  }
}

/* ============================================================
   NAVEGACIÓN
============================================================ */
function volverListado() {
  if (saving.value) return;

  router.push({ name: "ProyectosListado" });
}

function scrollToHashTarget() {
  const hash = route.hash;

  if (!hash) return;

  nextTick(() => {
    const target = document.querySelector(hash);

    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }

    if (hash === "#pf-profesores") {
      autorInput.value?.focus();
    }
  });
}

/* ============================================================
   EVENTOS GLOBALES
============================================================ */
function handleDocumentClick(event) {
  if (
    carreraDropdownOpen.value &&
    carreraRoot.value &&
    !carreraRoot.value.contains(event.target)
  ) {
    cerrarCarreraDropdown();
  }

  if (
    autorDropdownOpen.value &&
    autorRoot.value &&
    !autorRoot.value.contains(event.target)
  ) {
    cerrarAutorDropdown();
  }
}

function handleDocumentKeydown(event) {
  if (event.key !== "Escape") return;

  if (carreraDropdownOpen.value) {
    cerrarCarreraDropdown();
    return;
  }

  if (autorDropdownOpen.value) {
    cerrarAutorDropdown();
  }
}

/* ============================================================
   CICLO DE VIDA
============================================================ */
onMounted(async () => {
  document.addEventListener("mousedown", handleDocumentClick);
  document.addEventListener("keydown", handleDocumentKeydown);

  await cargarFacultades();
  await cargarProyecto();

  if (route.hash) {
    scrollToHashTarget();
    return;
  }

  nextTick(() => {
    firstField.value?.focus();
  });
});

onBeforeUnmount(() => {
  clearTimeout(autorSearchTimer);
  autorAbortController?.abort?.();

  document.removeEventListener("mousedown", handleDocumentClick);
  document.removeEventListener("keydown", handleDocumentKeydown);
});
</script>

<style src="./proyecto-formulario.css" lang="css"></style>
