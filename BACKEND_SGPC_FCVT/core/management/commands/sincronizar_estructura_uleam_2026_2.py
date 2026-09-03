"""
Sincronización NO DESTRUCTIVA de la estructura académica ULEAM 2026-2.

Objetivo
========
Corregir los vacíos detectados en el catálogo Sede -> CarreraSede -> Carrera ->
Facultad del SGPC sin eliminar publicaciones, usuarios, proyectos ni relaciones
históricas.

El modelo actual del SGPC obliga a que toda Carrera pertenezca a una Facultad.
ULEAM, sin embargo, posee la Unidad Académica de Formación Técnica y
Tecnológica, Educación Virtual y otras modalidades de estudio. Para mantener
compatibilidad con el esquema existente, esta unidad se registra en la tabla
/modelo Facultad como una "unidad académica" adicional. No se renombra el
modelo ni se requiere migración de esquema.

Fuentes institucionales verificadas para 2026-2:
- https://admision.uleam.edu.ec/oferta-academica-2026-2/
- https://carreras.uleam.edu.ec/unitev/electromecanica/
- Resolución OCS-SO-001-003-2025 sobre Electromecánica y Energías Renovables.

Uso
===
Vista previa (NO modifica la base):
    python manage.py sincronizar_estructura_uleam_2026_2

Aplicar cambios:
    python manage.py sincronizar_estructura_uleam_2026_2 --apply --confirmar SINCRONIZAR_ESTRUCTURA_2026_2

El comando es idempotente: puede ejecutarse más de una vez sin duplicar
CarreraSede. Nunca mueve una Carrera histórica de Facultad.
"""

from __future__ import annotations

import unicodedata
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Carrera, CarreraSede, Facultad, Sede


UNIDAD_TECNICA_NOMBRE = (
    "Unidad Académica de Formación Técnica y Tecnológica, "
    "Educación Virtual y otras modalidades de estudio"
)
UNIDAD_TECNICA_SIGLAS = "UAFTT"


# ---------------------------------------------------------------------------
# Programas que la estructura vigente del SGPC no podía representar de forma
# correcta porque no pertenecen a una de las facultades históricas cargadas.
#
# Los códigos de sede son los que ya existen en el SGPC:
# man, cho, suc, elc, ped, pic, fla, sdo, tos, sta, jun, sis, plo, jam.
# ---------------------------------------------------------------------------
PROGRAMAS_UNIDAD_ACADEMICA = {
    "Electromecánica": {
        "sedes": ("cho", "elc", "fla", "sta", "jam"),
        "aliases": (
            "Electromecánica",
            "Electromecanica",
            "Tecnología Superior en Electromecánica",
            "Tecnologia Superior en Electromecanica",
        ),
    },
    "Electromecánica y Energías Renovables": {
        "sedes": ("elc", "ped", "tos"),
        "aliases": (
            "Electromecánica y Energías Renovables",
            "Electromecánica y Energía Renovables",
            "Electromecanica y Energias Renovables",
            "Electromecanica y Energia Renovables",
            "Ingeniería en Electromecánica y Energías Renovables",
            "Ingenieria en Electromecanica y Energias Renovables",
        ),
    },
    "Gastronomía": {
        "sedes": ("man", "tos", "plo", "jam"),
        "aliases": (
            "Gastronomía",
            "Gastronomia",
        ),
    },
    "Tecnología Superior en Riego y Producción Agrícola": {
        "sedes": ("tos",),
        "aliases": (
            "Tecnología Superior en Riego y Producción Agrícola",
            "Tecnologia Superior en Riego y Produccion Agricola",
            "Riego y Producción Agrícola",
            "Riego y Produccion Agricola",
        ),
    },
    "Explotación y Mantenimiento de Equipos Biomédicos": {
        "sedes": ("tos",),
        "aliases": (
            "Explotación y Mantenimiento de Equipos Biomédicos",
            "Explotacion y Mantenimiento de Equipos Biomedicos",
        ),
    },
    "Comunicación para Televisión, Relaciones Públicas y Protocolo": {
        "sedes": ("man",),
        "aliases": (
            "Comunicación para Televisión, Relaciones Públicas y Protocolo",
            "Comunicación para Televisión, Relaciones Publicas y Protocolo",
            "Comunicacion para Television, Relaciones Publicas y Protocolo",
        ),
    },
}


# Relaciones de grado ya presentes en la BD del usuario se conservan. Esta
# lista solo asegura las incorporaciones actuales que faltaban en la matriz.
SEDES_REQUERIDAS = {
    codigo
    for datos in PROGRAMAS_UNIDAD_ACADEMICA.values()
    for codigo in datos["sedes"]
}


def _normalizar(valor: str | None) -> str:
    """Normaliza texto para comparar nombres sin depender de tildes/caso."""
    texto = (valor or "").strip().casefold()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.split())


def _buscar_carreras_por_aliases(aliases):
    aliases_norm = {_normalizar(alias) for alias in aliases}
    return [
        carrera
        for carrera in Carrera.objects.select_related("facultad").all()
        if _normalizar(carrera.nombre) in aliases_norm
    ]


class Command(BaseCommand):
    help = (
        "Sincroniza de forma no destructiva la estructura académica ULEAM "
        "2026-2 que falta en Carrera/CarreraSede."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help=(
                "Aplica la sincronización. Sin esta opción solo se muestra "
                "una vista previa y NO se modifica la base de datos."
            ),
        )
        parser.add_argument(
            "--confirmar",
            default="",
            help=(
                "Confirmación obligatoria para aplicar cambios: "
                "SINCRONIZAR_ESTRUCTURA_2026_2"
            ),
        )

    def handle(self, *args, **options):
        aplicar = bool(options["apply"])
        confirmar = str(options.get("confirmar") or "").strip()

        if aplicar and confirmar != "SINCRONIZAR_ESTRUCTURA_2026_2":
            raise CommandError(
                "La ejecución real requiere --confirmar "
                "SINCRONIZAR_ESTRUCTURA_2026_2. Ejecute primero la vista previa."
            )

        self.stdout.write("=" * 92)
        self.stdout.write("SGPC ULEAM - SINCRONIZACIÓN ESTRUCTURA ACADÉMICA 2026-2")
        self.stdout.write("=" * 92)
        self.stdout.write(
            self.style.WARNING(
                "MODO APLICACIÓN" if aplicar else "MODO VISTA PREVIA - NO MODIFICA LA BD"
            )
        )

        sedes = self._validar_sedes()
        self._mostrar_estado_inicial()

        if not aplicar:
            self._mostrar_plan(sedes)
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Vista previa completada. Para aplicar: "
                    "python manage.py sincronizar_estructura_uleam_2026_2 --apply --confirmar SINCRONIZAR_ESTRUCTURA_2026_2"
                )
            )
            return

        with transaction.atomic():
            resumen = self._aplicar(sedes)

        self._mostrar_resumen(resumen)
        self._mostrar_estado_final()

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------

    def _validar_sedes(self):
        sedes = {
            sede.codigo: sede
            for sede in Sede.objects.filter(codigo__in=SEDES_REQUERIDAS)
        }

        faltantes = sorted(SEDES_REQUERIDAS - set(sedes))
        if faltantes:
            raise CommandError(
                "No se puede sincronizar porque faltan estas sedes en la BD: "
                + ", ".join(faltantes)
            )

        inactivas = sorted(
            codigo for codigo, sede in sedes.items() if not sede.activa
        )
        if inactivas:
            raise CommandError(
                "Las siguientes sedes existen pero están inactivas: "
                + ", ".join(inactivas)
            )

        return sedes

    # ------------------------------------------------------------------
    # Vista previa
    # ------------------------------------------------------------------

    def _mostrar_estado_inicial(self):
        self.stdout.write("")
        self.stdout.write("ESTADO ACTUAL")
        self.stdout.write(f"- Sedes: {Sede.objects.count()}")
        self.stdout.write(f"- Sedes activas: {Sede.objects.filter(activa=True).count()}")
        self.stdout.write(f"- Unidades/Facultades: {Facultad.objects.count()}")
        self.stdout.write(f"- Carreras: {Carrera.objects.count()}")
        self.stdout.write(f"- CarreraSede: {CarreraSede.objects.count()}")
        self.stdout.write(
            f"- CarreraSede activas: {CarreraSede.objects.filter(activa=True).count()}"
        )

    def _mostrar_plan(self, sedes):
        unidad = Facultad.objects.filter(nombre=UNIDAD_TECNICA_NOMBRE).first()

        self.stdout.write("")
        self.stdout.write("CAMBIOS PROPUESTOS")

        if unidad:
            self.stdout.write(
                f"- Unidad académica ya existe: ID {unidad.id} - {unidad.nombre}"
            )
        else:
            self.stdout.write(
                f"- CREAR unidad académica: {UNIDAD_TECNICA_NOMBRE}"
            )

        for nombre, datos in PROGRAMAS_UNIDAD_ACADEMICA.items():
            carreras = _buscar_carreras_por_aliases(datos["aliases"])
            carrera_unidad = None
            if unidad:
                carrera_unidad = next(
                    (c for c in carreras if c.facultad_id == unidad.id),
                    None,
                )

            if carrera_unidad:
                self.stdout.write(
                    f"- REUTILIZAR carrera ID {carrera_unidad.id}: {nombre}"
                )
            elif carreras:
                historicas = ", ".join(
                    f"ID {c.id} ({c.facultad.nombre})" for c in carreras
                )
                self.stdout.write(
                    f"- CONSERVAR carrera(s) histórica(s): {historicas}"
                )
                self.stdout.write(
                    f"- CREAR carrera actual en la unidad académica: {nombre}"
                )
            else:
                self.stdout.write(f"- CREAR carrera: {nombre}")

            for codigo in datos["sedes"]:
                sede = sedes[codigo]
                self.stdout.write(
                    f"    ASEGURAR {codigo} - {sede.nombre} -> {nombre}"
                )

        self.stdout.write("")
        self.stdout.write(
            "IMPORTANTE: no se eliminarán ni desactivarán las relaciones históricas."
        )

    # ------------------------------------------------------------------
    # Aplicación
    # ------------------------------------------------------------------

    def _obtener_o_crear_unidad(self, resumen):
        unidad, creada = Facultad.objects.get_or_create(
            nombre=UNIDAD_TECNICA_NOMBRE,
            defaults={
                "siglas": None,
                "descripcion": (
                    "Unidad académica ULEAM incorporada al catálogo SGPC para "
                    "representar carreras técnicas, tecnológicas y otras ofertas "
                    "que no pertenecen a una facultad histórica del esquema."
                ),
            },
        )

        if creada:
            resumen["unidades_creadas"].append(unidad.nombre)

        # Asignar siglas solo si el modelo dispone del campo y no existe colisión.
        if hasattr(unidad, "siglas") and not unidad.siglas:
            existe_sigla = Facultad.objects.exclude(pk=unidad.pk).filter(
                siglas__iexact=UNIDAD_TECNICA_SIGLAS
            ).exists()
            if not existe_sigla:
                unidad.siglas = UNIDAD_TECNICA_SIGLAS
                unidad.save(update_fields=["siglas"])

        return unidad

    def _resolver_carrera(self, unidad, nombre, datos, resumen):
        carreras = _buscar_carreras_por_aliases(datos["aliases"])

        # 1. Ya existe una coincidencia dentro de la unidad correcta.
        dentro_unidad = [c for c in carreras if c.facultad_id == unidad.id]
        if dentro_unidad:
            carrera = dentro_unidad[0]
            if carrera.nombre != nombre:
                # Canoniza el nombre solo si no produce una colisión.
                colision = Carrera.objects.filter(
                    facultad=unidad,
                    nombre=nombre,
                ).exclude(pk=carrera.pk).exists()
                if not colision:
                    anterior = carrera.nombre
                    carrera.nombre = nombre
                    carrera.save(update_fields=["nombre"])
                    resumen["carreras_renombradas"].append(
                        f"{anterior} -> {nombre}"
                    )
            return carrera

        # 2. Nunca se mueve una Carrera histórica de Facultad.
        #    La Facultad forma parte del significado histórico de los registros
        #    que ya apuntan a esa Carrera. Si existe una coincidencia en otra
        #    Facultad, se conserva intacta y se crea/reutiliza una Carrera
        #    separada dentro de la unidad académica vigente.
        if carreras:
            for historica in carreras:
                resumen["carreras_historicas_conservadas"].append(
                    f"ID {historica.id}: {historica.nombre} | "
                    f"{historica.facultad.nombre}"
                )

        carrera, creada = Carrera.objects.get_or_create(
            facultad=unidad,
            nombre=nombre,
        )
        if creada:
            resumen["carreras_creadas"].append(
                f"ID {carrera.id}: {carrera.nombre}"
            )
        return carrera

    def _asegurar_relacion(self, sede, carrera, resumen):
        relacion, creada = CarreraSede.objects.get_or_create(
            sede=sede,
            carrera=carrera,
            defaults={"activa": True},
        )

        if creada:
            resumen["relaciones_creadas"].append(
                f"{sede.codigo} | {sede.nombre} -> {carrera.nombre}"
            )
            return

        if not relacion.activa:
            relacion.activa = True
            relacion.save(update_fields=["activa"])
            resumen["relaciones_reactivadas"].append(
                f"{sede.codigo} | {sede.nombre} -> {carrera.nombre}"
            )
        else:
            resumen["relaciones_existentes"].append(
                f"{sede.codigo} | {sede.nombre} -> {carrera.nombre}"
            )

    def _aplicar(self, sedes):
        resumen = defaultdict(list)
        unidad = self._obtener_o_crear_unidad(resumen)

        for nombre, datos in PROGRAMAS_UNIDAD_ACADEMICA.items():
            carrera = self._resolver_carrera(
                unidad=unidad,
                nombre=nombre,
                datos=datos,
                resumen=resumen,
            )

            for codigo in datos["sedes"]:
                self._asegurar_relacion(
                    sede=sedes[codigo],
                    carrera=carrera,
                    resumen=resumen,
                )

        return resumen

    # ------------------------------------------------------------------
    # Reporte final
    # ------------------------------------------------------------------

    def _mostrar_resumen(self, resumen):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("SINCRONIZACIÓN APLICADA"))

        secciones = (
            ("Unidades creadas", "unidades_creadas"),
            ("Carreras creadas", "carreras_creadas"),
            ("Carreras históricas conservadas", "carreras_historicas_conservadas"),
            ("Carreras renombradas", "carreras_renombradas"),
            ("Relaciones creadas", "relaciones_creadas"),
            ("Relaciones reactivadas", "relaciones_reactivadas"),
            ("Relaciones ya existentes", "relaciones_existentes"),
        )

        for titulo, clave in secciones:
            elementos = resumen.get(clave, [])
            self.stdout.write(f"\n{titulo}: {len(elementos)}")
            for elemento in elementos:
                self.stdout.write(f"  - {elemento}")

    def _mostrar_estado_final(self):
        self.stdout.write("")
        self.stdout.write("ESTADO FINAL")
        self.stdout.write(f"- Unidades/Facultades: {Facultad.objects.count()}")
        self.stdout.write(f"- Carreras: {Carrera.objects.count()}")
        self.stdout.write(f"- CarreraSede: {CarreraSede.objects.count()}")
        self.stdout.write(
            f"- CarreraSede activas: {CarreraSede.objects.filter(activa=True).count()}"
        )

        self.stdout.write("\nRESUMEN DE LAS SEDES CORREGIDAS")
        for codigo in sorted(SEDES_REQUERIDAS):
            sede = Sede.objects.get(codigo=codigo)
            cantidad = CarreraSede.objects.filter(
                sede=sede,
                activa=True,
            ).count()
            self.stdout.write(
                f"  {codigo} - {sede.nombre}: {cantidad} carreras activas"
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "No se eliminaron publicaciones, usuarios, proyectos ni "
                "relaciones CarreraSede históricas."
            )
        )
