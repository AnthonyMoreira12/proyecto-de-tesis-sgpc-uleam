import { defineStore } from "pinia";
import api from "../api/axios";

const emptyResultados = () => ({
  usuarios: [],
  autores: [],
  proyectos: [],
  publicaciones: [],
});

const toStr = (value) => String(value ?? "").trim();

export const useSearchStore = defineStore("search", {
  state: () => ({
    query: "",
    resultados: emptyResultados(),
    loading: false,
    error: null,

    _t: null,
    _reqId: 0,
    _abort: null,

    suspendBackend: false,
  }),

  getters: {
    resultadosEncontrados(state) {
      const r = state.resultados;
      return Boolean(
        r.usuarios.length ||
          r.autores.length ||
          r.proyectos.length ||
          r.publicaciones.length
      );
    },

    total(state) {
      const r = state.resultados;
      return (
        r.usuarios.length +
        r.autores.length +
        r.proyectos.length +
        r.publicaciones.length
      );
    },
  },

  actions: {
    _cancelRequest() {
      if (this._t) clearTimeout(this._t);
      this._t = null;

      if (this._abort) this._abort.abort();
      this._abort = null;

      this._reqId += 1;
      this.loading = false;
    },

    setQuery(q) {
      this.query = toStr(q);
    },

    setResultados(res) {
      this.resultados = {
        usuarios: Array.isArray(res?.usuarios) ? res.usuarios : [],
        autores: Array.isArray(res?.autores) ? res.autores : [],
        proyectos: Array.isArray(res?.proyectos) ? res.proyectos : [],
        publicaciones: Array.isArray(res?.publicaciones) ? res.publicaciones : [],
      };
    },

    clearResultados() {
      this._cancelRequest();
      this.resultados = emptyResultados();
      this.loading = false;
      this.error = null;
    },

    clear() {
      this.clearResultados();
      this.query = "";
    },

    async _searchNow(query) {
      const q = toStr(query);
      this.query = q;

      if (!q) {
        this.clearResultados();
        return emptyResultados();
      }

      if (this.suspendBackend) {
        this.resultados = emptyResultados();
        this.loading = false;
        this.error = null;
        return emptyResultados();
      }

      this._cancelRequest();
      const myReqId = this._reqId;
      this._abort = new AbortController();
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get("/busqueda/", {
          params: { q },
          signal: this._abort.signal,
        });

        if (myReqId !== this._reqId) return emptyResultados();

        const data = response?.data ?? response ?? {};
        const normalized = {
          usuarios: Array.isArray(data?.usuarios) ? data.usuarios : [],
          autores: Array.isArray(data?.autores) ? data.autores : [],
          proyectos: Array.isArray(data?.proyectos) ? data.proyectos : [],
          publicaciones: Array.isArray(data?.publicaciones) ? data.publicaciones : [],
        };

        this.resultados = normalized;
        return normalized;
      } catch (e) {
        if (e?.code === "ERR_CANCELED") return emptyResultados();

        this.resultados = emptyResultados();
        this.error = "No se pudo completar la búsqueda general.";
        throw e;
      } finally {
        if (myReqId === this._reqId) {
          this.loading = false;
        }
      }
    },

    async search(q, { debounce = 250, min = 2 } = {}) {
      const query = toStr(q);
      this.query = query;

      if (this._t) clearTimeout(this._t);

      if (query.length < min) {
        this.clearResultados();
        return emptyResultados();
      }

      return new Promise((resolve, reject) => {
        this._t = setTimeout(async () => {
          try {
            const data = await this._searchNow(query);
            resolve(data);
          } catch (e) {
            reject(e);
          }
        }, debounce);
      });
    },

    setSuspendBackend(value) {
      this.suspendBackend = !!value;

      if (this.suspendBackend) {
        this.clearResultados();
      }
    },
  },
});