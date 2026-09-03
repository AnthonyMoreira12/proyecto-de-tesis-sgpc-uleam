from django.core.management.base import BaseCommand, CommandError

from core.publicaciones.services.publicaciones_integridad_backfill_services import (
    backfill_integridad_documental,
    diagnostico_integridad_documental,
)


class Command(BaseCommand):
    help = "Completa nombre/tamaño/SHA-256 de PDF históricos sin alterar datos científicos."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--publication-id", type=int, default=None)
        parser.add_argument("--diagnostico", action="store_true")

    def handle(self, *args, **options):
        if options["diagnostico"]:
            data = diagnostico_integridad_documental()
            for key, value in data.items():
                self.stdout.write(f"{key}: {value}")
            return

        if options["limit"] is not None and options["limit"] < 1:
            raise CommandError("--limit debe ser mayor que cero.")

        result = backfill_integridad_documental(
            dry_run=options["dry_run"],
            limit=options["limit"],
            publication_id=options["publication_id"],
        )
        for key in (
            "dry_run",
            "publicaciones_revisadas",
            "publicaciones_actualizadas",
            "adjuntos_revisados",
            "adjuntos_actualizados",
            "errores_total",
        ):
            self.stdout.write(f"{key}: {result[key]}")
        for error in result["errores"][:50]:
            self.stderr.write(str(error))
