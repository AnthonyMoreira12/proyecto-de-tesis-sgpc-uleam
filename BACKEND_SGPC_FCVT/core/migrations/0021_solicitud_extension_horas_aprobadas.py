from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_solicitud_extension_perfil"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitudextensionperfil",
            name="horas_aprobadas",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
            ),
        ),
    ]
