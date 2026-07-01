import { describe, it, expect } from 'vitest';
import { normalizeSpaces, normalizePersonName } from './textFormat';

describe('Utilidades de Formato de Texto (textFormat.js)', () => {

  describe('normalizeSpaces', () => {
    it('debe eliminar espacios al inicio y al final', () => {
      expect(normalizeSpaces('  Hola  ')).toBe('Hola');
    });

    it('debe reducir múltiples espacios intermedios a uno solo', () => {
      expect(normalizeSpaces('Anthony    Joel    Moreira')).toBe('Anthony Joel Moreira');
    });

    it('debe devolver un string vacío si se pasa null o undefined', () => {
      expect(normalizeSpaces(null)).toBe('');
      expect(normalizeSpaces(undefined)).toBe('');
    });
  });

  describe('normalizePersonName', () => {
    it('debe capitalizar correctamente nombres normales', () => {
      expect(normalizePersonName('ANTHONY JOEL MOREIRA')).toBe('Anthony Joel Moreira');
      expect(normalizePersonName('anthony joel moreira')).toBe('Anthony Joel Moreira');
    });

    it('debe respetar y mantener en minúsculas las partículas de nombres (de, del, la, von)', () => {
      expect(normalizePersonName('LUIS MIGUEL DE LA CRUZ')).toBe('Luis Miguel de la Cruz');
      expect(normalizePersonName('MARIA DEL CARMEN')).toBe('Maria del Carmen');
    });

    it('debe capitalizar correctamente nombres con guiones', () => {
      expect(normalizePersonName('MARIA-JOSE PEREZ')).toBe('Maria-Jose Perez');
    });

    it('debe manejar textos vacíos o nulos', () => {
      expect(normalizePersonName('')).toBe('');
      expect(normalizePersonName(null)).toBe('');
    });
  });
});