import json

from django.core.management.base import BaseCommand, CommandError

from core.migracion_produccion.services.migracion_produccion_services import (
    comparar_snapshots_produccion,
    diagnostico_actualizacion_produccion,
    normalizar_actualizacion_produccion,
)
from core.models import Sede


class Command(BaseCommand):
    help = "Diagnostica/simula/aplica la normalización segura de datos históricos antes de actualizar SGPC."

    def add_arguments(self, parser):
        parser.add_argument("--diagnostico", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--aplicar", action="store_true")
        parser.add_argument("--sede-id", type=int)
        parser.add_argument("--sede-codigo")
        parser.add_argument("--usar-sede-predeterminada", action="store_true")
        parser.add_argument("--confirmar")
        parser.add_argument("--output")
        parser.add_argument("--comparar-con", help="Archivo JSON de un diagnóstico/snapshot anterior.")

    def handle(self, *args, **options):
        compare_file = str(options.get("comparar_con") or "").strip()
        if compare_file:
            try:
                with open(compare_file, "r", encoding="utf-8") as fh:
                    previous = json.load(fh)
            except (OSError, ValueError) as exc:
                raise CommandError(f"No fue posible leer --comparar-con: {exc}") from exc
            before = previous.get("snapshot", previous.get("snapshot_antes", previous))
            result = comparar_snapshots_produccion(before)
            text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
            self.stdout.write(text)
            output = str(options.get("output") or "").strip()
            if output:
                with open(output, "w", encoding="utf-8") as fh:
                    fh.write(text + "\n")
            return

        apply_changes = bool(options["aplicar"])
        dry_run = bool(options["dry_run"])
        diagnostic_only = bool(options["diagnostico"] or (not apply_changes and not dry_run))

        sede_id = options.get("sede_id")
        sede_codigo = str(options.get("sede_codigo") or "").strip()
        if sede_codigo:
            sede = Sede.objects.filter(codigo=sede_codigo, activa=True).first()
            if not sede:
                raise CommandError(f"No existe una sede activa con código '{sede_codigo}'.")
            if sede_id and sede.pk != sede_id:
                raise CommandError("--sede-id y --sede-codigo apuntan a sedes diferentes.")
            sede_id = sede.pk

        if options["usar_sede_predeterminada"] and not sede_id:
            raise CommandError("Debe indicar --sede-id o --sede-codigo al usar sede predeterminada.")

        if apply_changes and options.get("confirmar") != "NORMALIZAR_PRODUCCION":
            raise CommandError(
                "La ejecución real requiere --confirmar NORMALIZAR_PRODUCCION. Ejecute primero --dry-run."
            )

        if diagnostic_only:
            result = diagnostico_actualizacion_produccion()
        else:
            result = normalizar_actualizacion_produccion(
                dry_run=not apply_changes,
                default_sede_id=sede_id,
                usar_sede_predeterminada=bool(options["usar_sede_predeterminada"]),
                recalcular_perfiles=True,
            )

        text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        self.stdout.write(text)
        output = str(options.get("output") or "").strip()
        if output:
            with open(output, "w", encoding="utf-8") as fh:
                fh.write(text)
                fh.write("\n")
            self.stdout.write(self.style.SUCCESS(f"Resultado guardado en {output}"))
