from django.db import migrations, models


def aprobar_publicaciones_historicas(apps, schema_editor):
    """
    Conserva la visibilidad y el significado de los registros existentes.

    Antes de incorporar el flujo de revisión, las publicaciones almacenadas
    en el SGPC ya se trataban como registros institucionales válidos. Por eso,
    únicamente durante esta migración, los registros históricos pasan a
    estado "aprobada".

    Las publicaciones creadas después de la migración utilizarán el valor
    por defecto definitivo del modelo: "borrador".
    """
    Publicacion = apps.get_model("core", "Publicacion")

    Publicacion.objects.filter(
        estado="borrador",
    ).update(
        estado="aprobada",
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0014_carrerasede_sede_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="publicacion",
            name="estado",
            field=models.CharField(
                choices=[
                    (
                        "borrador",
                        "Borrador",
                    ),
                    (
                        "en_revision",
                        "En revisión",
                    ),
                    (
                        "observada",
                        "Observada",
                    ),
                    (
                        "aprobada",
                        "Aprobada",
                    ),
                    (
                        "rechazada",
                        "Rechazada",
                    ),
                ],
                db_index=True,
                default="borrador",
                max_length=20,
            ),
        ),
        migrations.RunPython(
            aprobar_publicaciones_historicas,
            migrations.RunPython.noop,
        ),
        migrations.AddIndex(
            model_name="publicacion",
            index=models.Index(
                fields=[
                    "estado",
                    "anio_publicacion",
                ],
                name="pub_estado_anio_idx",
            ),
        ),
    ]