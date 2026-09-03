from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0018_notificacion",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="publicacion",
            name="archivo_pdf_nombre_original",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="publicacion",
            name="archivo_pdf_tamano_bytes",
            field=models.PositiveBigIntegerField(
                blank=True,
                editable=False,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="publicacion",
            name="archivo_pdf_sha256",
            field=models.CharField(
                blank=True,
                db_index=True,
                editable=False,
                max_length=64,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="publicacionarchivo",
            name="nombre_original",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="publicacionarchivo",
            name="tamano_bytes",
            field=models.PositiveBigIntegerField(
                blank=True,
                editable=False,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="publicacionarchivo",
            name="sha256",
            field=models.CharField(
                blank=True,
                db_index=True,
                editable=False,
                max_length=64,
                null=True,
            ),
        ),
    ]