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
            Registre el proyecto, su facultad, carrera, años de ejecución y PDF de respaldo.
            El equipo investigador puede completarse después mientras el proyecto no esté cerrado.
          </p>
        </div>

        <div class="pf-hero__meta" aria-label="Resumen">
          <span class="pf-pill">
            Estado: <strong>{{ estadoResumen }}</strong>
          </span>

          <span class="pf-pill">
            Vigencia: <strong>{{ periodoResumen }}</strong>
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
                    disabled
                    aria-describedby="proyecto-estado-help"
                  >
                    <option
                      v-for="opcion in estadoOptions"
                      :key="opcion.value"
                      :value="opcion.value"
                    >
                      {{ opcion.label }}
                    </option>
                  </select>

                  <p id="proyecto-estado-help" class="pf-help">
                    El estado se cambia desde el listado de proyectos.
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
                  <p class="pf-section-kicker">Vigencia</p>

                  <h2 id="pf-periodo-title" class="pf-card__title">
                    Años y fechas del proyecto
                  </h2>
                </div>

                <p class="pf-card__desc">
                  Los años deben coincidir con las fechas registradas cuando estas se informen.
                </p>
              </div>

              <div class="pf-grid">
                <div class="pf-field pf-col-4">
                  <label for="proyecto-periodo-inicio">
                    Año de inicio
                    <span class="pf-req">*</span>
                  </label>

                  <input
                    id="proyecto-periodo-inicio"
                    v-model="form.anio_inicio"
                    type="number"
                    inputmode="numeric"
                    :min="MIN_YEAR"
                    :max="MAX_YEAR"
                    step="1"
                    :placeholder="String(CURRENT_YEAR)"
                    :disabled="saving"
                    :aria-invalid="showAnioInicioError ? 'true' : 'false'"
                    @input="normalizarAnioInput('anio_inicio')"
                  />

                  <p class="pf-help">
                    Rango permitido: {{ MIN_YEAR }}–{{ MAX_YEAR }}.
                  </p>

                  <p v-if="showAnioInicioError" class="pf-error" role="alert">
                    Ingrese un año de inicio válido.
                  </p>
                </div>

                <div class="pf-field pf-col-4">
                  <label for="proyecto-periodo-fin">
                    Año de finalización
                  </label>

                  <input
                    id="proyecto-periodo-fin"
                    v-model="form.anio_fin"
                    type="number"
                    inputmode="numeric"
                    :min="MIN_YEAR"
                    :max="MAX_YEAR"
                    step="1"
                    placeholder="Opcional"
                    :disabled="
                      saving ||
                      Boolean(form.fecha_fin_prorrogada) ||
                      form.estado === 'cierre'
                    "
                    :aria-invalid="showAnioFinError ? 'true' : 'false'"
                    @input="normalizarAnioInput('anio_fin')"
                  />

                  <p class="pf-help">
                    Se bloquea cuando existe una prórroga o el proyecto está cerrado.
                  </p>

                  <p v-if="showAnioFinError" class="pf-error" role="alert">
                    El año final debe ser válido y no puede ser menor al año de inicio.
                  </p>
                </div>

                <div class="pf-period-preview pf-col-4">
                  <span>Vigencia</span>
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
                    disabled
                  />

                  <p class="pf-help">
                    La prórroga se administra desde el listado.
                  </p>
                </div>

                <div class="pf-field pf-col-4">
                  <label for="proyecto-fecha-cierre">Fecha de cierre</label>

                  <input
                    id="proyecto-fecha-cierre"
                    v-model="form.fecha_cierre"
                    type="date"
                    disabled
                  />

                  <p class="pf-help">
                    Se establece automáticamente al cerrar el proyecto.
                  </p>
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
                          :disabled="saving || index === 0"
                          @change="normalizarEquipoInvestigador"
                        >
                          <option
                            v-for="opcion in autorRolOptionsForIndex(index)"
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
                  v-if="
                    form.archivo_pdf ||
                    (archivoPdfActualUrl && !eliminarPdfActual)
                  "
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
                        @click="limpiarPdfNuevo"
                      >
                        Quitar
                      </button>

                      <button
                        v-else-if="archivoPdfActualUrl"
                        type="button"
                        class="pf-file-chip__remove"
                        :disabled="saving"
                        @click="marcarEliminarPdfActual"
                      >
                        Eliminar
                      </button>
                    </div>
                  </div>
                </article>

                <div
                  v-if="eliminarPdfActual && !form.archivo_pdf"
                  class="pf-save-error"
                  role="status"
                >
                  El PDF almacenado se eliminará al guardar.

                  <button
                    type="button"
                    class="pf-link-btn"
                    :disabled="saving"
                    @click="deshacerEliminarPdfActual"
                  >
                    Deshacer
                  </button>
                </div>

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
                :class="{ 'is-complete': isValidProjectYear(form.anio_inicio) }"
              >
                <span class="pf-summary-dot" aria-hidden="true"></span>

                <span>
                  <strong>Vigencia</strong>
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
                :class="{
                  'is-complete': Boolean(
                    form.archivo_pdf ||
                    (archivoPdfActualUrl && !eliminarPdfActual)
                  )
                }"
              >
                <span class="pf-summary-dot" aria-hidden="true"></span>

                <span>
                  <strong>PDF</strong>
                  <small>
                    {{
                      form.archivo_pdf ||
                      (archivoPdfActualUrl && !eliminarPdfActual)
                        ? "Cargado"
                        : "Opcional"
                    }}
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
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";

import {
  onBeforeRouteLeave,
  useRoute,
  useRouter,
} from "vue-router";

import {
  actualizarProyecto,
  buscarAutoresProyecto,
  consultarCarrerasProyecto,
  consultarFacultadesProyecto,
  crearProyecto,
  getProyectoApiErrorMessage,
  obtenerProyecto,
} from "../../scripts/api/proyectosApi";


/* ============================================================
   ROUTER
============================================================ */

const route =
  useRoute();

const router =
  useRouter();

const isEditMode =
  computed(
    () => Boolean(
      route.params.id
    )
  );

const proyectoId =
  computed(
    () => route.params.id
  );


/* ============================================================
   DOM REFS
============================================================ */

const firstField =
  ref(null);

const carreraRoot =
  ref(null);

const carreraInput =
  ref(null);

const autorRoot =
  ref(null);

const autorInput =
  ref(null);

const fileInput =
  ref(null);


/* ============================================================
   CONSTANTES
============================================================ */

const CURRENT_YEAR =
  new Date().getFullYear();

const MIN_YEAR = 1900;

const MAX_PROJECT_FUTURE_YEARS = 50;

const MAX_YEAR = (
  CURRENT_YEAR
  + MAX_PROJECT_FUTURE_YEARS
);

const MAX_PDF_BYTES =
  5 * 1024 * 1024;

const UNSAVED_MESSAGE = (
  "Existen cambios sin guardar. "
  + "¿Desea salir y descartarlos?"
);

const estadoOptions = [
  {
    value: "nuevo",
    label: "Nuevo",
  },
  {
    value: "arrastre",
    label: "Arrastre",
  },
  {
    value: "cierre",
    label: "Cierre",
  },
];

const autorRolOptions = [
  {
    value: "principal",
    label: "Investigador principal",
  },
  {
    value: "coinvestigador",
    label: "Coinvestigador",
  },
  {
    value: "colaborador",
    label: "Colaborador",
  },
];


/* ============================================================
   FORMULARIO
============================================================ */

function emptyForm() {
  return {
    nombre: "",
    descripcion: "",
    estado: "nuevo",
    facultad: "",
    carrera: "",
    anio_inicio:
      String(
        CURRENT_YEAR
      ),
    anio_fin: "",
    fecha_inicio: "",
    fecha_fin_planificada: "",
    fecha_fin_prorrogada: "",
    fecha_cierre: "",
    archivo_pdf: null,
  };
}

const form =
  ref(
    emptyForm()
  );

const loadingProyecto =
  ref(false);

const loadProyectoError =
  ref("");

const saving =
  ref(false);

const saveError =
  ref("");

const feedbackMessage =
  ref("");

const triedSubmit =
  ref(false);


/* ============================================================
   FACULTADES / CARRERAS
============================================================ */

const facultades =
  ref([]);

const loadingFacultades =
  ref(false);

const errorFacultades =
  ref("");

const carreras =
  ref([]);

const loadingCarreras =
  ref(false);

const errorCarreras =
  ref("");

const carreraQuery =
  ref("");

const carreraDropdownOpen =
  ref(false);

const carreraActiveIndex =
  ref(0);


/* ============================================================
   AUTORES
============================================================ */

const autores =
  ref([]);

const autoresSeleccionados =
  ref([]);

const loadingAutores =
  ref(false);

const errorAutores =
  ref("");

const autorQuery =
  ref("");

const autorDropdownOpen =
  ref(false);

const autorActiveIndex =
  ref(0);


/* ============================================================
   PDF
============================================================ */

const pdfError =
  ref("");

const archivoPdfActualUrl =
  ref("");

const eliminarPdfActual =
  ref(false);

const pdfDragOver =
  ref(false);


/* ============================================================
   CONTROL INTERNO
============================================================ */

let autorSearchTimer = null;
let autorAbortController = null;
let projectAbortController = null;
let facultiesAbortController = null;
let careersAbortController = null;

const initialSnapshot =
  ref("");

const allowNavigation =
  ref(false);

const hydrating =
  ref(false);


/* ============================================================
   HELPERS GENERALES
============================================================ */

function normalizeId(
  value
) {
  return value == null
    ? ""
    : String(value);
}


function normalizeText(
  value
) {
  return String(
    value || ""
  )
    .toLowerCase()
    .normalize("NFD")
    .replace(
      /[\u0300-\u036f]/g,
      ""
    )
    .replace(
      /[^\p{L}\p{N}\s@._-]/gu,
      " "
    )
    .replace(
      /\s+/g,
      " "
    )
    .trim();
}


function toApiId(
  value
) {
  const id =
    normalizeId(
      value
    );

  return /^\d+$/.test(
    id
  )
    ? Number(id)
    : id;
}


function normalizeDate(
  value
) {
  if (
    !value
  ) {
    return "";
  }

  return String(
    value
  ).slice(
    0,
    10
  );
}


function dateYear(
  value
) {
  const normalized =
    normalizeDate(
      value
    );

  if (
    !normalized
  ) {
    return "";
  }

  const match =
    normalized.match(
      /^(\d{4})-/
    );

  return match
    ? match[1]
    : "";
}


function prettyBytes(
  bytes
) {
  const size =
    Number(
      bytes || 0
    );

  if (
    size <= 0
  ) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ];

  let value =
    size;

  let index = 0;

  while (
    value >= 1024
    && index < units.length - 1
  ) {
    value /= 1024;
    index += 1;
  }

  return (
    `${value.toFixed(
      index === 0
        ? 0
        : 2
    )} ${units[index]}`
  );
}


function extractArray(
  payload
) {
  if (
    Array.isArray(
      payload
    )
  ) {
    return payload;
  }

  if (
    Array.isArray(
      payload?.results
    )
  ) {
    return payload.results;
  }

  return [];
}


function isValidProjectYear(
  value,
  {
    allowBlank = false,
  } = {}
) {
  const text =
    String(
      value ?? ""
    ).trim();

  if (
    !text
  ) {
    return allowBlank;
  }

  if (
    !/^\d{4}$/.test(
      text
    )
  ) {
    return false;
  }

  const year =
    Number(text);

  return (
    Number.isInteger(
      year
    )
    && year >= MIN_YEAR
    && year <= MAX_YEAR
  );
}


function normalizarAnioInput(
  field
) {
  const digits =
    String(
      form.value[
        field
      ] ?? ""
    )
      .replace(
        /\D/g,
        ""
      )
      .slice(
        0,
        4
      );

  form.value[
    field
  ] = digits;
}


function isPdfFile(
  file
) {
  if (
    !file
  ) {
    return false;
  }

  const name =
    String(
      file.name || ""
    ).toLowerCase();

  return (
    file.type
    === "application/pdf"
    || name.endsWith(
      ".pdf"
    )
  );
}


/* ============================================================
   EQUIPO INVESTIGADOR
============================================================ */

function autorRolOptionsForIndex(
  index
) {
  if (
    index === 0
  ) {
    return autorRolOptions.filter(
      (option) => (
        option.value
        === "principal"
      )
    );
  }

  return autorRolOptions.filter(
    (option) => (
      option.value
      !== "principal"
    )
  );
}


function normalizarEquipoInvestigador() {
  autoresSeleccionados.value =
    autoresSeleccionados.value.map(
      (
        autor,
        index
      ) => {
        let role =
          String(
            autor?.rol || ""
          )
            .trim()
            .toLowerCase();

        if (
          index === 0
        ) {
          role =
            "principal";
        } else if (
          ![
            "coinvestigador",
            "colaborador",
          ].includes(
            role
          )
        ) {
          role =
            "coinvestigador";
        }

        return {
          ...autor,
          rol:
            role,
          orden:
            index + 1,
        };
      }
    );
}


function buildAutoresPayload() {
  normalizarEquipoInvestigador();

  return autoresSeleccionados.value.map(
    (
      autor,
      index
    ) => ({
      autor_id:
        toApiId(
          autor.id
        ),

      rol: (
        index === 0
          ? "principal"
          : autor.rol
      ),

      orden:
        index + 1,
    })
  );
}


function autoresSignature(
  authors = autoresSeleccionados.value
) {
  return JSON.stringify(
    authors.map(
      (
        author,
        index
      ) => ({
        autor_id:
          normalizeId(
            author.id
          ),

        rol: (
          index === 0
            ? "principal"
            : (
              author.rol
              || "coinvestigador"
            )
        ),

        orden:
          index + 1,
      })
    )
  );
}


/* ============================================================
   CAMBIOS SIN GUARDAR
============================================================ */

function fileSnapshot(
  file
) {
  if (
    !file
  ) {
    return null;
  }

  return {
    name:
      file.name || "",

    size:
      Number(
        file.size || 0
      ),

    lastModified:
      Number(
        file.lastModified || 0
      ),
  };
}


function buildSnapshot() {
  return JSON.stringify({
    nombre:
      String(
        form.value.nombre || ""
      ).trim(),

    descripcion:
      String(
        form.value.descripcion || ""
      ).trim(),

    estado:
      form.value.estado,

    facultad:
      normalizeId(
        form.value.facultad
      ),

    carrera:
      normalizeId(
        form.value.carrera
      ),

    anio_inicio:
      String(
        form.value.anio_inicio || ""
      ),

    anio_fin:
      String(
        form.value.anio_fin || ""
      ),

    fecha_inicio:
      form.value.fecha_inicio || "",

    fecha_fin_planificada:
      form.value.fecha_fin_planificada || "",

    fecha_fin_prorrogada:
      form.value.fecha_fin_prorrogada || "",

    fecha_cierre:
      form.value.fecha_cierre || "",

    autores:
      autoresSignature(),

    archivo_pdf:
      fileSnapshot(
        form.value.archivo_pdf
      ),

    eliminar_pdf:
      Boolean(
        eliminarPdfActual.value
      ),

    archivo_actual:
      archivoPdfActualUrl.value || "",
  });
}


function captureInitialSnapshot() {
  initialSnapshot.value =
    buildSnapshot();
}


const hasUnsavedChanges =
  computed(
    () => (
      Boolean(
        initialSnapshot.value
      )
      && buildSnapshot()
      !== initialSnapshot.value
    )
  );


function confirmDiscardChanges() {
  if (
    !hasUnsavedChanges.value
  ) {
    return true;
  }

  return window.confirm(
    UNSAVED_MESSAGE
  );
}


/* ============================================================
   COMPUTEDS
============================================================ */

const isEstadoCierre =
  computed(
    () => (
      form.value.estado
      === "cierre"
    )
  );


const hasPrincipalAutor =
  computed(
    () => {
      const principals =
        autoresSeleccionados.value.filter(
          (
            autor,
            index
          ) => (
            index === 0
            && autor.rol
            === "principal"
          )
        );

      return (
        autoresSeleccionados.value.length > 0
        && principals.length === 1
      );
    }
  );


const profesoresResumen =
  computed(
    () => {
      const total =
        autoresSeleccionados.value.length;

      if (
        total > 0
      ) {
        return (
          `${total} vinculado`
          + `${total === 1 ? "" : "s"}`
        );
      }

      return isEstadoCierre.value
        ? "Requerido"
        : "Opcional";
    }
  );


const estadoResumen =
  computed(
    () => (
      estadoOptions.find(
        (item) => (
          item.value
          === form.value.estado
        )
      )?.label
      || "Nuevo"
    )
  );


const periodoResumen =
  computed(
    () => {
      const start =
        String(
          form.value.anio_inicio || ""
        );

      const end =
        String(
          form.value.anio_fin || ""
        );

      if (
        start
        && end
      ) {
        return `${start}–${end}`;
      }

      if (
        start
      ) {
        return `Desde ${start}`;
      }

      if (
        end
      ) {
        return `Hasta ${end}`;
      }

      return "Sin definir";
    }
  );


const descripcionLength =
  computed(
    () => (
      String(
        form.value.descripcion || ""
      ).length
    )
  );


const pdfLabel =
  computed(
    () => {
      if (
        form.value.archivo_pdf
      ) {
        return (
          form.value
            .archivo_pdf
            .name
        );
      }

      if (
        archivoPdfActualUrl.value
        && !eliminarPdfActual.value
      ) {
        const cleanUrl =
          String(
            archivoPdfActualUrl.value
          )
            .split("?")[0]
            .split("#")[0];

        const name =
          cleanUrl
            .split("/")
            .pop();

        return (
          decodeURIComponent(
            name || ""
          )
          || "PDF registrado"
        );
      }

      return "Sin PDF";
    }
  );


const facultadSeleccionada =
  computed(
    () => (
      facultades.value.find(
        (item) => (
          normalizeId(
            item.id
          )
          === normalizeId(
            form.value.facultad
          )
        )
      )
      || null
    )
  );


const carreraSeleccionada =
  computed(
    () => (
      carreras.value.find(
        (item) => (
          normalizeId(
            item.id
          )
          === normalizeId(
            form.value.carrera
          )
        )
      )
      || null
    )
  );


const carreraPlaceholder =
  computed(
    () => {
      if (
        !form.value.facultad
      ) {
        return (
          "Seleccione primero "
          + "una facultad"
        );
      }

      if (
        loadingCarreras.value
      ) {
        return "Cargando carreras...";
      }

      return "Buscar carrera";
    }
  );


const showNombreError =
  computed(
    () => (
      triedSubmit.value
      && !String(
        form.value.nombre || ""
      ).trim()
    )
  );


const showFacultadError =
  computed(
    () => (
      triedSubmit.value
      && !form.value.facultad
    )
  );


const showCarreraError =
  computed(
    () => (
      triedSubmit.value
      && !form.value.carrera
    )
  );


const showAnioInicioError =
  computed(
    () => (
      triedSubmit.value
      && !isValidProjectYear(
        form.value.anio_inicio
      )
    )
  );


const showAnioFinError =
  computed(
    () => {
      if (
        !triedSubmit.value
      ) {
        return false;
      }

      if (
        !String(
          form.value.anio_fin || ""
        ).trim()
      ) {
        return false;
      }

      if (
        !isValidProjectYear(
          form.value.anio_fin
        )
      ) {
        return true;
      }

      if (
        !isValidProjectYear(
          form.value.anio_inicio
        )
      ) {
        return false;
      }

      return (
        Number(
          form.value.anio_fin
        )
        < Number(
          form.value.anio_inicio
        )
      );
    }
  );


const showAutoresError =
  computed(
    () => (
      triedSubmit.value
      && isEstadoCierre.value
      && !hasPrincipalAutor.value
    )
  );


const completionPercent =
  computed(
    () => {
      const checks = [
        Boolean(
          String(
            form.value.nombre || ""
          ).trim()
        ),

        isValidProjectYear(
          form.value.anio_inicio
        ),

        Boolean(
          form.value.facultad
        ),

        Boolean(
          carreraSeleccionada.value
        ),

        (
          !isEstadoCierre.value
          || hasPrincipalAutor.value
        ),
      ];

      const complete =
        checks.filter(
          Boolean
        ).length;

      return Math.round(
        (
          complete
          / checks.length
        ) * 100
      );
    }
  );


/* ============================================================
   HIDRATACIÓN
============================================================ */

function resetForm() {
  hydrating.value =
    true;

  form.value =
    emptyForm();

  carreras.value = [];
  carreraQuery.value = "";
  autoresSeleccionados.value = [];
  archivoPdfActualUrl.value = "";
  eliminarPdfActual.value = false;
  pdfError.value = "";
  saveError.value = "";
  feedbackMessage.value = "";
  triedSubmit.value = false;
  pdfDragOver.value = false;

  if (
    fileInput.value
  ) {
    fileInput.value.value =
      "";
  }

  nextTick(
    () => {
      captureInitialSnapshot();
      hydrating.value = false;
    }
  );
}


function resolveFacultadIdFromData(
  data
) {
  const direct = (
    data?.facultad_id
    || data?.facultad?.id
    || data?.carrera_facultad_id
    || data?.facultad
  );

  if (
    direct
    && /^\d+$/.test(
      String(direct)
    )
  ) {
    return normalizeId(
      direct
    );
  }

  const name =
    String(
      data?.facultad_nombre
      || data?.facultad?.nombre
      || data?.facultad
      || ""
    ).trim();

  if (
    !name
  ) {
    return "";
  }

  const match =
    facultades.value.find(
      (item) => (
        normalizeText(
          item.nombre
        )
        === normalizeText(
          name
        )
      )
    );

  return match
    ? normalizeId(
        match.id
      )
    : "";
}


function buildAutoresFromProyecto(
  data
) {
  const source = (
    Array.isArray(
      data?.autores
    )
      ? data.autores
      : (
        Array.isArray(
          data?.autores_resumen
        )
          ? data.autores_resumen
          : []
      )
  );

  const normalized =
    source
      .map(
        (
          item,
          index
        ) => {
          const id = (
            item.id
            || item.autor_id
            || item.autor
          );

          if (
            !id
          ) {
            return null;
          }

          const names =
            item.nombres || "";

          const surnames =
            item.apellidos || "";

          const fullName = (
            item.nombre_completo
            || item.nombre
            || `${names} ${surnames}`.trim()
            || `Autor #${id}`
          );

          return {
            id:
              normalizeId(
                id
              ),

            nombres:
              names,

            apellidos:
              surnames,

            nombre_completo:
              fullName,

            correo:
              item.correo
              || item.email
              || "",

            es_externo:
              Boolean(
                item.es_externo
              ),

            rol:
              item.rol
              || (
                index === 0
                  ? "principal"
                  : "coinvestigador"
              ),

            orden:
              Number(
                item.orden
                || index + 1
              ),
          };
        }
      )
      .filter(
        Boolean
      )
      .sort(
        (
          first,
          second
        ) => (
          Number(
            first.orden || 0
          )
          - Number(
            second.orden || 0
          )
        )
      );

  autoresSeleccionados.value =
    normalized;

  normalizarEquipoInvestigador();

  return autoresSeleccionados.value;
}


function hydrateForm(
  data
) {
  hydrating.value =
    true;

  const facultyId =
    resolveFacultadIdFromData(
      data
    );

  form.value = {
    nombre:
      data.nombre || "",

    descripcion:
      data.descripcion || "",

    estado:
      data.estado || "nuevo",

    facultad:
      facultyId,

    carrera:
      normalizeId(
        data.carrera_id
        || data.carrera
        || ""
      ),

    anio_inicio:
      String(
        data.anio_inicio
        || CURRENT_YEAR
      ),

    anio_fin:
      data.anio_fin == null
        ? ""
        : String(
            data.anio_fin
          ),

    fecha_inicio:
      normalizeDate(
        data.fecha_inicio
      ),

    fecha_fin_planificada:
      normalizeDate(
        data.fecha_fin_planificada
      ),

    fecha_fin_prorrogada:
      normalizeDate(
        data.fecha_fin_prorrogada
      ),

    fecha_cierre:
      normalizeDate(
        data.fecha_cierre
      ),

    archivo_pdf:
      null,
  };

  buildAutoresFromProyecto(
    data
  );

  archivoPdfActualUrl.value = (
    data.archivo_pdf_url
    || data.archivo_pdf
    || ""
  );

  eliminarPdfActual.value =
    false;

  pdfError.value =
    "";

  saveError.value =
    "";

  triedSubmit.value =
    false;

  if (
    fileInput.value
  ) {
    fileInput.value.value =
      "";
  }
}


async function cargarProyecto() {
  projectAbortController?.abort?.();

  if (
    !isEditMode.value
  ) {
    resetForm();

    nextTick(
      () => {
        firstField.value
          ?.focus?.();
      }
    );

    return;
  }

  const controller =
    new AbortController();

  projectAbortController =
    controller;

  loadingProyecto.value =
    true;

  loadProyectoError.value =
    "";

  try {
    const data =
      await obtenerProyecto(
        proyectoId.value,
        {
          signal:
            controller.signal,
        }
      );

    if (
      projectAbortController
      !== controller
    ) {
      return;
    }

    hydrateForm(
      data || {}
    );

    if (
      form.value.facultad
    ) {
      await cargarCarrerasPorFacultad(
        form.value.facultad
      );

      syncCarreraQueryFromSelection();
    }

    await nextTick();

    captureInitialSnapshot();
    hydrating.value = false;
  } catch (
    error
  ) {
    if (
      error?.code
      === "ERR_CANCELED"
    ) {
      return;
    }

    console.error(
      "Error cargando proyecto:",
      error
    );

    loadProyectoError.value =
      getProyectoApiErrorMessage(
        error,
        (
          "No se pudo obtener la "
          + "información del proyecto."
        )
      );

    hydrating.value =
      false;
  } finally {
    if (
      projectAbortController
      === controller
    ) {
      loadingProyecto.value =
        false;
    }
  }
}


/* ============================================================
   FACULTADES
============================================================ */

function normalizeFacultad(
  item
) {
  return {
    id:
      normalizeId(
        item?.id
      ),

    nombre:
      String(
        item?.nombre
        || item?.label
        || ""
      ).trim(),
  };
}


function sortFacultades(
  list
) {
  return [
    ...list,
  ].sort(
    (
      first,
      second
    ) => (
      String(
        first?.nombre || ""
      ).localeCompare(
        String(
          second?.nombre || ""
        ),
        "es",
        {
          sensitivity:
            "base",
        }
      )
    )
  );
}


async function cargarFacultades() {
  facultiesAbortController
    ?.abort?.();

  const controller =
    new AbortController();

  facultiesAbortController =
    controller;

  loadingFacultades.value =
    true;

  errorFacultades.value =
    "";

  try {
    const payload =
      await consultarFacultadesProyecto({
        signal:
          controller.signal,
      });

    if (
      facultiesAbortController
      !== controller
    ) {
      return;
    }

    facultades.value =
      sortFacultades(
        extractArray(
          payload
        )
          .map(
            normalizeFacultad
          )
          .filter(
            (item) => (
              item.id
              && item.nombre
            )
          )
      );

    if (
      !facultades.value.length
    ) {
      errorFacultades.value =
        "No hay facultades disponibles.";
    }
  } catch (
    error
  ) {
    if (
      error?.code
      === "ERR_CANCELED"
    ) {
      return;
    }

    console.error(
      "Error cargando facultades:",
      error
    );

    facultades.value = [];

    errorFacultades.value =
      getProyectoApiErrorMessage(
        error,
        (
          "No se pudieron cargar "
          + "las facultades."
        )
      );
  } finally {
    if (
      facultiesAbortController
      === controller
    ) {
      loadingFacultades.value =
        false;
    }
  }
}


async function handleFacultadChange() {
  form.value.carrera =
    "";

  carreraQuery.value =
    "";

  carreras.value =
    [];

  cerrarCarreraDropdown();

  if (
    !form.value.facultad
  ) {
    return;
  }

  await cargarCarrerasPorFacultad(
    form.value.facultad
  );

  await nextTick();

  abrirCarreraDropdown();

  carreraInput.value
    ?.focus?.();
}


/* ============================================================
   CARRERAS
============================================================ */

function normalizeCarrera(
  item,
  faculty = ""
) {
  return {
    id:
      normalizeId(
        item?.id
      ),

    nombre:
      item?.nombre
      || item?.label
      || "",

    facultad:
      item?.facultad
      || item?.facultad_nombre
      || faculty
      || "",
  };
}


function sortCarreras(
  list
) {
  return [
    ...list,
  ].sort(
    (
      first,
      second
    ) => (
      String(
        first?.nombre || ""
      ).localeCompare(
        String(
          second?.nombre || ""
        ),
        "es",
        {
          sensitivity:
            "base",
        }
      )
    )
  );
}


async function cargarCarrerasPorFacultad(
  facultadId
) {
  careersAbortController
    ?.abort?.();

  if (
    !facultadId
  ) {
    carreras.value = [];
    return;
  }

  const controller =
    new AbortController();

  careersAbortController =
    controller;

  loadingCarreras.value =
    true;

  errorCarreras.value =
    "";

  try {
    const facultyName = (
      facultades.value.find(
        (item) => (
          normalizeId(
            item.id
          )
          === normalizeId(
            facultadId
          )
        )
      )?.nombre
      || ""
    );

    const payload =
      await consultarCarrerasProyecto(
        facultadId,
        {
          signal:
            controller.signal,
        }
      );

    if (
      careersAbortController
      !== controller
    ) {
      return;
    }

    carreras.value =
      sortCarreras(
        extractArray(
          payload
        )
          .map(
            (item) => (
              normalizeCarrera(
                item,
                facultyName
              )
            )
          )
          .filter(
            (item) => (
              item.id
              && item.nombre
            )
          )
      );

    if (
      !carreras.value.length
    ) {
      errorCarreras.value = (
        "No hay carreras disponibles "
        + "para esta facultad."
      );
    }
  } catch (
    error
  ) {
    if (
      error?.code
      === "ERR_CANCELED"
    ) {
      return;
    }

    console.error(
      "Error cargando carreras:",
      error
    );

    carreras.value = [];

    errorCarreras.value =
      getProyectoApiErrorMessage(
        error,
        (
          "No se pudieron cargar las "
          + "carreras de la facultad."
        )
      );
  } finally {
    if (
      careersAbortController
      === controller
    ) {
      loadingCarreras.value =
        false;
    }
  }
}


function buildCarreraScore(
  career,
  query
) {
  if (
    !query
  ) {
    return 1;
  }

  const name =
    normalizeText(
      career?.nombre
    );

  const tokens =
    query
      .split(" ")
      .filter(
        Boolean
      );

  let score = 0;

  if (
    name.startsWith(
      query
    )
  ) {
    score += 12;
  }

  if (
    name.includes(
      query
    )
  ) {
    score += 7;
  }

  tokens.forEach(
    (token) => {
      if (
        name.startsWith(
          token
        )
      ) {
        score += 3;
      } else if (
        name.includes(
          token
        )
      ) {
        score += 2;
      }
    }
  );

  return score;
}


const carrerasVisibles =
  computed(
    () => {
      const query =
        normalizeText(
          carreraQuery.value
        );

      if (
        !form.value.facultad
      ) {
        return [];
      }

      if (
        !query
      ) {
        return sortCarreras(
          carreras.value
        ).slice(
          0,
          80
        );
      }

      return carreras.value
        .map(
          (career) => ({
            career,
            score:
              buildCarreraScore(
                career,
                query
              ),
          })
        )
        .filter(
          (item) => (
            item.score > 0
          )
        )
        .sort(
          (
            first,
            second
          ) => {
            if (
              second.score
              !== first.score
            ) {
              return (
                second.score
                - first.score
              );
            }

            return String(
              first
                .career
                .nombre || ""
            ).localeCompare(
              String(
                second
                  .career
                  .nombre || ""
              ),
              "es",
              {
                sensitivity:
                  "base",
              }
            );
          }
        )
        .slice(
          0,
          80
        )
        .map(
          (item) => (
            item.career
          )
        );
    }
  );


function abrirCarreraDropdown() {
  if (
    !form.value.facultad
    || loadingCarreras.value
  ) {
    return;
  }

  cerrarAutorDropdown();

  carreraDropdownOpen.value =
    true;

  carreraActiveIndex.value =
    0;
}


function cerrarCarreraDropdown() {
  carreraDropdownOpen.value =
    false;
}


function toggleCarreraDropdown() {
  if (
    !form.value.facultad
    || loadingCarreras.value
  ) {
    return;
  }

  if (
    carreraDropdownOpen.value
  ) {
    cerrarCarreraDropdown();
  } else {
    abrirCarreraDropdown();
  }

  nextTick(
    () => (
      carreraInput.value
        ?.focus?.()
    )
  );
}


function handleCarreraInput() {
  form.value.carrera =
    "";

  carreraDropdownOpen.value =
    true;

  carreraActiveIndex.value =
    0;
}


function moverCarrera(
  direction
) {
  if (
    !carreraDropdownOpen.value
  ) {
    abrirCarreraDropdown();
  }

  const maximum =
    carrerasVisibles.value.length
    - 1;

  if (
    maximum < 0
  ) {
    return;
  }

  const next = (
    carreraActiveIndex.value
    + direction
  );

  carreraActiveIndex.value =
    Math.min(
      maximum,
      Math.max(
        0,
        next
      )
    );
}


function seleccionarCarreraActiva() {
  const career =
    carrerasVisibles.value[
      carreraActiveIndex.value
    ];

  if (
    career
  ) {
    seleccionarCarrera(
      career
    );
  }
}


function seleccionarCarrera(
  career
) {
  form.value.carrera =
    normalizeId(
      career.id
    );

  carreraQuery.value =
    career.nombre;

  cerrarCarreraDropdown();
}


function limpiarCarrera() {
  form.value.carrera =
    "";

  carreraQuery.value =
    "";

  abrirCarreraDropdown();

  nextTick(
    () => (
      carreraInput.value
        ?.focus?.()
    )
  );
}


function syncCarreraQueryFromSelection() {
  if (
    !form.value.carrera
  ) {
    carreraQuery.value =
      "";

    return;
  }

  const career =
    carreras.value.find(
      (item) => (
        normalizeId(
          item.id
        )
        === normalizeId(
          form.value.carrera
        )
      )
    );

  if (
    career
  ) {
    carreraQuery.value =
      career.nombre;
  }
}


/* ============================================================
   AUTORES
============================================================ */

function normalizeAutor(
  item
) {
  const id = (
    item?.id
    || item?.autor_id
    || item?.value
  );

  const names =
    item?.nombres || "";

  const surnames =
    item?.apellidos || "";

  const name = (
    item?.nombre_completo
    || item?.nombre
    || item?.label
    || `${names} ${surnames}`.trim()
  );

  return {
    id:
      normalizeId(
        id
      ),

    nombres:
      names,

    apellidos:
      surnames,

    nombre_completo: (
      String(
        name || ""
      ).trim()
      || `Autor #${id}`
    ),

    correo:
      item?.correo
      || item?.email
      || "",

    es_externo:
      Boolean(
        item?.es_externo
      ),
  };
}


function sortAutores(
  list
) {
  return [
    ...list,
  ].sort(
    (
      first,
      second
    ) => (
      String(
        first?.nombre_completo
        || ""
      ).localeCompare(
        String(
          second?.nombre_completo
          || ""
        ),
        "es",
        {
          sensitivity:
            "base",
        }
      )
    )
  );
}


function buildAutorScore(
  author,
  query
) {
  if (
    !query
  ) {
    return 1;
  }

  const name =
    normalizeText(
      author?.nombre_completo
    );

  const email =
    normalizeText(
      author?.correo
    );

  const full =
    `${name} ${email}`.trim();

  const tokens =
    query
      .split(" ")
      .filter(
        Boolean
      );

  let score = 0;

  if (
    name.startsWith(
      query
    )
  ) {
    score += 12;
  }

  if (
    name.includes(
      query
    )
  ) {
    score += 7;
  }

  if (
    email.includes(
      query
    )
  ) {
    score += 4;
  }

  if (
    full.includes(
      query
    )
  ) {
    score += 5;
  }

  tokens.forEach(
    (token) => {
      if (
        name.startsWith(
          token
        )
      ) {
        score += 3;
      } else if (
        name.includes(
          token
        )
      ) {
        score += 2;
      }

      if (
        email.includes(
          token
        )
      ) {
        score += 1;
      }
    }
  );

  return score;
}


const autoresVisibles =
  computed(
    () => {
      const selectedIds =
        new Set(
          autoresSeleccionados.value.map(
            (item) => (
              normalizeId(
                item.id
              )
            )
          )
        );

      const available =
        autores.value.filter(
          (item) => (
            !selectedIds.has(
              normalizeId(
                item.id
              )
            )
          )
        );

      const query =
        normalizeText(
          autorQuery.value
        );

      return available
        .map(
          (author) => ({
            author,
            score:
              buildAutorScore(
                author,
                query
              ),
          })
        )
        .filter(
          (item) => (
            item.score > 0
          )
        )
        .sort(
          (
            first,
            second
          ) => {
            if (
              second.score
              !== first.score
            ) {
              return (
                second.score
                - first.score
              );
            }

            return String(
              first
                .author
                .nombre_completo
                || ""
            ).localeCompare(
              String(
                second
                  .author
                  .nombre_completo
                  || ""
              ),
              "es",
              {
                sensitivity:
                  "base",
              }
            );
          }
        )
        .slice(
          0,
          60
        )
        .map(
          (item) => (
            item.author
          )
        );
    }
  );


function handleAutorFocus() {
  cerrarCarreraDropdown();

  autorDropdownOpen.value =
    true;
}


function handleAutorInput() {
  errorAutores.value =
    "";

  autorDropdownOpen.value =
    true;

  autorActiveIndex.value =
    0;

  clearTimeout(
    autorSearchTimer
  );

  if (
    autorQuery.value
      .trim()
      .length < 2
  ) {
    autores.value = [];
    autorAbortController
      ?.abort?.();

    return;
  }

  autorSearchTimer =
    setTimeout(
      () => {
        buscarAutores();
      },
      280
    );
}


async function buscarAutores() {
  const query =
    autorQuery.value.trim();

  if (
    query.length < 2
  ) {
    autores.value = [];

    autorDropdownOpen.value =
      true;

    return;
  }

  autorAbortController
    ?.abort?.();

  const controller =
    new AbortController();

  autorAbortController =
    controller;

  loadingAutores.value =
    true;

  errorAutores.value =
    "";

  autorDropdownOpen.value =
    true;

  try {
    const payload =
      await buscarAutoresProyecto(
        {
          q:
            query,
        },
        {
          signal:
            controller.signal,
        }
      );

    if (
      autorAbortController
      !== controller
    ) {
      return;
    }

    autores.value =
      sortAutores(
        extractArray(
          payload
        )
          .map(
            normalizeAutor
          )
          .filter(
            (item) => (
              item.id
            )
          )
      );
  } catch (
    error
  ) {
    if (
      error?.code
      === "ERR_CANCELED"
    ) {
      return;
    }

    console.error(
      "Error buscando autores:",
      error
    );

    autores.value = [];

    errorAutores.value =
      getProyectoApiErrorMessage(
        error,
        (
          "No se pudieron cargar "
          + "los profesores."
        )
      );
  } finally {
    if (
      autorAbortController
      === controller
    ) {
      loadingAutores.value =
        false;
    }
  }
}


function cerrarAutorDropdown() {
  autorDropdownOpen.value =
    false;
}


function moverAutor(
  direction
) {
  if (
    !autorDropdownOpen.value
  ) {
    autorDropdownOpen.value =
      true;
  }

  const maximum =
    autoresVisibles.value.length
    - 1;

  if (
    maximum < 0
  ) {
    return;
  }

  const next = (
    autorActiveIndex.value
    + direction
  );

  autorActiveIndex.value =
    Math.min(
      maximum,
      Math.max(
        0,
        next
      )
    );
}


function seleccionarAutorActivo() {
  const author =
    autoresVisibles.value[
      autorActiveIndex.value
    ];

  if (
    author
  ) {
    agregarAutor(
      author
    );
  }
}


function agregarAutor(
  author
) {
  const id =
    normalizeId(
      author?.id
    );

  if (
    !id
  ) {
    return;
  }

  const exists =
    autoresSeleccionados.value.some(
      (item) => (
        normalizeId(
          item.id
        )
        === id
      )
    );

  if (
    exists
  ) {
    return;
  }

  autoresSeleccionados.value.push({
    ...author,
    id,
    rol: (
      autoresSeleccionados.value.length
      === 0
        ? "principal"
        : "coinvestigador"
    ),
    orden:
      autoresSeleccionados.value.length
      + 1,
  });

  normalizarEquipoInvestigador();

  autorQuery.value =
    "";

  autores.value =
    [];

  autorDropdownOpen.value =
    false;

  feedbackMessage.value =
    "Profesor agregado.";
}


function quitarAutor(
  id
) {
  const normalizedId =
    normalizeId(
      id
    );

  autoresSeleccionados.value =
    autoresSeleccionados.value.filter(
      (item) => (
        normalizeId(
          item.id
        )
        !== normalizedId
      )
    );

  normalizarEquipoInvestigador();
}


function moverAutorSeleccionado(
  index,
  direction
) {
  const nextIndex =
    index + direction;

  if (
    nextIndex < 0
    || nextIndex
    >= autoresSeleccionados
      .value
      .length
  ) {
    return;
  }

  const list = [
    ...autoresSeleccionados.value,
  ];

  [
    list[index],
    list[nextIndex],
  ] = [
    list[nextIndex],
    list[index],
  ];

  autoresSeleccionados.value =
    list;

  normalizarEquipoInvestigador();
}


/* ============================================================
   PDF
============================================================ */

function setPdfFile(
  file
) {
  pdfError.value =
    "";

  if (
    !file
  ) {
    form.value.archivo_pdf =
      null;

    return;
  }

  if (
    !isPdfFile(
      file
    )
  ) {
    pdfError.value =
      "Solo se permiten archivos PDF.";

    form.value.archivo_pdf =
      null;

    if (
      fileInput.value
    ) {
      fileInput.value.value =
        "";
    }

    return;
  }

  if (
    file.size
    > MAX_PDF_BYTES
  ) {
    pdfError.value = (
      "El PDF supera el tamaño "
      + "máximo de 5 MB."
    );

    form.value.archivo_pdf =
      null;

    if (
      fileInput.value
    ) {
      fileInput.value.value =
        "";
    }

    return;
  }

  form.value.archivo_pdf =
    file;

  eliminarPdfActual.value =
    false;
}


function handlePdfChange(
  event
) {
  const file = (
    event.target
      .files?.[0]
    || null
  );

  setPdfFile(
    file
  );
}


function handlePdfDragOver(
  event
) {
  pdfDragOver.value =
    true;

  if (
    event?.dataTransfer
  ) {
    event.dataTransfer
      .dropEffect = "copy";
  }
}


function handlePdfDragLeave(
  event
) {
  const current =
    event.currentTarget;

  const related =
    event.relatedTarget;

  if (
    current
    && related
    && current.contains?.(
      related
    )
  ) {
    return;
  }

  pdfDragOver.value =
    false;
}


function handlePdfDrop(
  event
) {
  pdfDragOver.value =
    false;

  const file = (
    Array.from(
      event?.dataTransfer?.files
      || []
    )[0]
    || null
  );

  setPdfFile(
    file
  );
}


function limpiarPdfNuevo() {
  form.value.archivo_pdf =
    null;

  pdfError.value =
    "";

  if (
    fileInput.value
  ) {
    fileInput.value.value =
      "";
  }
}


function marcarEliminarPdfActual() {
  form.value.archivo_pdf =
    null;

  eliminarPdfActual.value =
    true;

  pdfError.value =
    "";

  if (
    fileInput.value
  ) {
    fileInput.value.value =
      "";
  }
}


function deshacerEliminarPdfActual() {
  eliminarPdfActual.value =
    false;
}


/* ============================================================
   PAYLOAD
============================================================ */

function appendFormValue(
  formData,
  key,
  value
) {
  formData.append(
    key,
    value == null
      ? ""
      : String(value)
  );
}


function teamChanged() {
  const initial = (
    initialSnapshot.value
      ? JSON.parse(
          initialSnapshot.value
        ).autores
      : "[]"
  );

  return (
    autoresSignature()
    !== initial
  );
}


function buildPayload() {
  const payload =
    new FormData();

  appendFormValue(
    payload,
    "nombre",
    String(
      form.value.nombre || ""
    ).trim()
  );

  appendFormValue(
    payload,
    "descripcion",
    String(
      form.value.descripcion || ""
    ).trim()
  );

  appendFormValue(
    payload,
    "carrera",
    toApiId(
      form.value.carrera
    )
  );

  appendFormValue(
    payload,
    "fecha_inicio",
    form.value.fecha_inicio
  );

  appendFormValue(
    payload,
    "fecha_fin_planificada",
    form.value
      .fecha_fin_planificada
  );

  appendFormValue(
    payload,
    "anio_inicio",
    form.value.anio_inicio
  );

  appendFormValue(
    payload,
    "anio_fin",
    form.value.anio_fin
  );

  if (
    !isEditMode.value
  ) {
    appendFormValue(
      payload,
      "estado",
      "nuevo"
    );
  }

  if (
    !isEditMode.value
    || teamChanged()
  ) {
    appendFormValue(
      payload,
      "autores_data",
      JSON.stringify(
        buildAutoresPayload()
      )
    );
  }

  if (
    form.value.archivo_pdf
  ) {
    payload.append(
      "archivo_pdf",
      form.value.archivo_pdf
    );
  } else if (
    eliminarPdfActual.value
  ) {
    appendFormValue(
      payload,
      "eliminar_archivo_pdf",
      "true"
    );
  }

  return payload;
}


/* ============================================================
   VALIDACIÓN
============================================================ */

function validateBeforeSave() {
  triedSubmit.value =
    true;

  saveError.value =
    "";

  feedbackMessage.value =
    "";

  if (
    !String(
      form.value.nombre || ""
    ).trim()
  ) {
    saveError.value =
      "El nombre del proyecto es obligatorio.";

    nextTick(
      () => (
        firstField.value
          ?.focus?.()
      )
    );

    return false;
  }

  if (
    !form.value.facultad
  ) {
    saveError.value =
      "Seleccione una facultad.";

    return false;
  }

  if (
    !form.value.carrera
  ) {
    saveError.value =
      "Seleccione una carrera.";

    abrirCarreraDropdown();

    nextTick(
      () => (
        carreraInput.value
          ?.focus?.()
      )
    );

    return false;
  }

  if (
    !isValidProjectYear(
      form.value.anio_inicio
    )
  ) {
    saveError.value = (
      "Ingrese un año de inicio "
      + `entre ${MIN_YEAR} y ${MAX_YEAR}.`
    );

    return false;
  }

  if (
    form.value.anio_fin
    && !isValidProjectYear(
      form.value.anio_fin
    )
  ) {
    saveError.value = (
      "Ingrese un año final "
      + `entre ${MIN_YEAR} y ${MAX_YEAR}.`
    );

    return false;
  }

  if (
    form.value.anio_fin
    && Number(
      form.value.anio_fin
    )
    < Number(
      form.value.anio_inicio
    )
  ) {
    saveError.value = (
      "El año final no puede ser "
      + "menor al año de inicio."
    );

    return false;
  }

  const startDateYear =
    dateYear(
      form.value.fecha_inicio
    );

  if (
    startDateYear
    && startDateYear
    !== String(
      form.value.anio_inicio
    )
  ) {
    saveError.value = (
      "El año de inicio debe coincidir "
      + "con la fecha de inicio."
    );

    return false;
  }

  const plannedEndYear =
    dateYear(
      form.value
        .fecha_fin_planificada
    );

  if (
    plannedEndYear
    && !form.value
      .fecha_fin_prorrogada
    && form.value.estado
      !== "cierre"
    && plannedEndYear
    !== String(
      form.value.anio_fin || ""
    )
  ) {
    saveError.value = (
      "El año final debe coincidir con "
      + "la fecha fin planificada."
    );

    return false;
  }

  if (
    form.value.fecha_inicio
    && form.value
      .fecha_fin_planificada
    && form.value
      .fecha_fin_planificada
      < form.value.fecha_inicio
  ) {
    saveError.value = (
      "La fecha fin planificada no "
      + "puede ser menor a la fecha "
      + "de inicio."
    );

    return false;
  }

  normalizarEquipoInvestigador();

  if (
    autoresSeleccionados
      .value
      .length > 0
    && !hasPrincipalAutor.value
  ) {
    saveError.value = (
      "El primer integrante debe ser "
      + "el único investigador principal."
    );

    nextTick(
      () => (
        autorInput.value
          ?.focus?.()
      )
    );

    return false;
  }

  if (
    isEstadoCierre.value
    && !hasPrincipalAutor.value
  ) {
    saveError.value = (
      "Un proyecto cerrado debe "
      + "conservar un investigador "
      + "principal en el orden 1."
    );

    nextTick(
      () => (
        autorInput.value
          ?.focus?.()
      )
    );

    return false;
  }

  if (
    pdfError.value
  ) {
    saveError.value =
      pdfError.value;

    return false;
  }

  return true;
}


/* ============================================================
   GUARDADO
============================================================ */

async function guardarProyecto() {
  if (
    !validateBeforeSave()
  ) {
    return;
  }

  saving.value =
    true;

  saveError.value =
    "";

  feedbackMessage.value =
    "";

  try {
    const payload =
      buildPayload();

    if (
      isEditMode.value
    ) {
      await actualizarProyecto(
        proyectoId.value,
        payload
      );
    } else {
      await crearProyecto(
        payload
      );
    }

    allowNavigation.value =
      true;

    captureInitialSnapshot();

    await router.push({
      name:
        "ProyectosListado",

      query: {
        guardado:
          "1",
      },
    });
  } catch (
    error
  ) {
    console.error(
      "Error guardando proyecto:",
      error
    );

    saveError.value =
      getProyectoApiErrorMessage(
        error,
        (
          "No se pudo guardar "
          + "el proyecto."
        )
      );
  } finally {
    saving.value =
      false;
  }
}


/* ============================================================
   NAVEGACIÓN
============================================================ */

async function volverListado() {
  if (
    saving.value
  ) {
    return;
  }

  if (
    !confirmDiscardChanges()
  ) {
    return;
  }

  allowNavigation.value =
    true;

  await router.push({
    name:
      "ProyectosListado",
  });
}


function scrollToHashTarget() {
  const hash =
    route.hash;

  if (
    !hash
  ) {
    return;
  }

  nextTick(
    () => {
      const target =
        document.querySelector(
          hash
        );

      if (
        target
      ) {
        target.scrollIntoView({
          behavior:
            "smooth",

          block:
            "start",
        });
      }

      if (
        hash
        === "#pf-profesores"
      ) {
        autorInput.value
          ?.focus?.();
      }
    }
  );
}


/* ============================================================
   EVENTOS
============================================================ */

function handleDocumentClick(
  event
) {
  if (
    carreraDropdownOpen.value
    && carreraRoot.value
    && !carreraRoot.value.contains(
      event.target
    )
  ) {
    cerrarCarreraDropdown();
  }

  if (
    autorDropdownOpen.value
    && autorRoot.value
    && !autorRoot.value.contains(
      event.target
    )
  ) {
    cerrarAutorDropdown();
  }
}


function handleDocumentKeydown(
  event
) {
  if (
    event.key
    !== "Escape"
  ) {
    return;
  }

  if (
    carreraDropdownOpen.value
  ) {
    cerrarCarreraDropdown();
    return;
  }

  if (
    autorDropdownOpen.value
  ) {
    cerrarAutorDropdown();
  }
}


function handleBeforeUnload(
  event
) {
  if (
    saving.value
    || allowNavigation.value
    || !hasUnsavedChanges.value
  ) {
    return;
  }

  event.preventDefault();
  event.returnValue =
    "";
}


/* ============================================================
   WATCHERS
============================================================ */

watch(
  () => form.value.fecha_inicio,
  (
    value
  ) => {
    if (
      hydrating.value
    ) {
      return;
    }

    const year =
      dateYear(
        value
      );

    if (
      year
    ) {
      form.value.anio_inicio =
        year;
    }
  }
);


watch(
  () => form.value.fecha_fin_planificada,
  (
    value
  ) => {
    if (
      hydrating.value
      || form.value
        .fecha_fin_prorrogada
      || form.value.estado
        === "cierre"
    ) {
      return;
    }

    const year =
      dateYear(
        value
      );

    if (
      year
    ) {
      form.value.anio_fin =
        year;
    }
  }
);


watch(
  carrerasVisibles,
  (
    list
  ) => {
    if (
      !list.length
    ) {
      carreraActiveIndex.value =
        0;

      return;
    }

    if (
      carreraActiveIndex.value
      > list.length - 1
    ) {
      carreraActiveIndex.value =
        0;
    }
  }
);


watch(
  autoresVisibles,
  (
    list
  ) => {
    if (
      !list.length
    ) {
      autorActiveIndex.value =
        0;

      return;
    }

    if (
      autorActiveIndex.value
      > list.length - 1
    ) {
      autorActiveIndex.value =
        0;
    }
  }
);


/* ============================================================
   GUARD DE RUTA
============================================================ */

onBeforeRouteLeave(
  () => {
    if (
      saving.value
      || allowNavigation.value
      || !hasUnsavedChanges.value
    ) {
      return true;
    }

    return confirmDiscardChanges();
  }
);


/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(
  async () => {
    document.addEventListener(
      "mousedown",
      handleDocumentClick
    );

    document.addEventListener(
      "keydown",
      handleDocumentKeydown
    );

    window.addEventListener(
      "beforeunload",
      handleBeforeUnload
    );

    await cargarFacultades();
    await cargarProyecto();

    if (
      route.hash
    ) {
      scrollToHashTarget();
      return;
    }

    nextTick(
      () => {
        firstField.value
          ?.focus?.();
      }
    );
  }
);


onBeforeUnmount(
  () => {
    clearTimeout(
      autorSearchTimer
    );

    autorAbortController
      ?.abort?.();

    projectAbortController
      ?.abort?.();

    facultiesAbortController
      ?.abort?.();

    careersAbortController
      ?.abort?.();

    document.removeEventListener(
      "mousedown",
      handleDocumentClick
    );

    document.removeEventListener(
      "keydown",
      handleDocumentKeydown
    );

    window.removeEventListener(
      "beforeunload",
      handleBeforeUnload
    );
  }
);
</script>

<style src="./proyecto-formulario.css" lang="css"></style>
