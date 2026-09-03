from django.core.management.base import BaseCommand, CommandError

from core.actualizaciones.services.actualizaciones_recordatorios_services import (
    RECORDATORIO_INTERVALO_DIAS,
    procesar_recordatorios_periodicos_actualizacion,
)


class Command(BaseCommand):
    help = (
        "Genera recordatorios internos para usuarios con información pendiente "
        "en campañas de actualización vigentes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dias",
            type=int,
            default=RECORDATORIO_INTERVALO_DIAS,
            help=(
                "Intervalo mínimo entre avisos para una misma participación. "
                f"Predeterminado: {RECORDATORIO_INTERVALO_DIAS} días."
            ),
        )

    def handle(self, *args, **options):
        dias = int(options.get("dias") or RECORDATORIO_INTERVALO_DIAS)
        if dias < 1:
            raise CommandError("--dias debe ser un entero mayor o igual a 1.")

        result = procesar_recordatorios_periodicos_actualizacion(
            intervalo_dias=dias,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Recordatorios de actualización procesados correctamente."
            )
        )
        self.stdout.write("Usuarios procesados: " f"{result['usuarios_procesados']}")
        self.stdout.write("Usuarios con pendientes: " f"{result['usuarios_con_pendientes']}")
        self.stdout.write("Notificaciones creadas: " f"{result['notificaciones_creadas']}")
        self.stdout.write("Recordatorios creados: " f"{result['recordatorios_creados']}")
