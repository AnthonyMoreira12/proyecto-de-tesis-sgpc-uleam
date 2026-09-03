from datetime import timedelta

from django.db import migrations


DEFAULT_PROFILE_EDIT_HOURS = 48


def corregir_plazo_anterior(apps, schema_editor):
    """Corrige solicitudes creadas con fecha_registro como plazo anterior.

    La implementación inicial guardaba ``fecha_registro`` cuando el usuario
    no tenía ``profile_edit_until`` explícito. El plazo real del periodo
    inicial es ``fecha_registro + 48 horas``.

    La migración es conservadora: solo modifica registros cuyo
    ``plazo_anterior`` está vacío o coincide exactamente con
    ``fecha_registro``. No toca solicitudes que ya tengan un plazo explícito
    distinto.
    """

    SolicitudExtensionPerfil = apps.get_model(
        "core",
        "SolicitudExtensionPerfil",
    )

    queryset = (
        SolicitudExtensionPerfil.objects
        .select_related("usuario")
        .all()
    )

    for solicitud in queryset.iterator():
        usuario = getattr(solicitud, "usuario", None)
        if usuario is None:
            continue

        fecha_registro = getattr(
            usuario,
            "fecha_registro",
            None,
        )
        profile_edit_until = getattr(
            usuario,
            "profile_edit_until",
            None,
        )

        if profile_edit_until is not None:
            expected_deadline = profile_edit_until
        elif fecha_registro is not None:
            expected_deadline = (
                fecha_registro
                + timedelta(hours=DEFAULT_PROFILE_EDIT_HOURS)
            )
        else:
            expected_deadline = None

        if expected_deadline is None:
            continue

        current_deadline = solicitud.plazo_anterior

        should_update = (
            current_deadline is None
            or (
                profile_edit_until is None
                and fecha_registro is not None
                and current_deadline == fecha_registro
            )
        )

        if should_update:
            (
                SolicitudExtensionPerfil.objects
                .filter(pk=solicitud.pk)
                .update(plazo_anterior=expected_deadline)
            )


def reverse_noop(apps, schema_editor):
    # No se restaura el valor incorrecto anterior.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_solicitud_extension_horas_aprobadas"),
    ]

    operations = [
        migrations.RunPython(
            corregir_plazo_anterior,
            reverse_noop,
        ),
    ]
