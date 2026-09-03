from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0015_publicacion_estado",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicacionRevision",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "decision",
                    models.CharField(
                        choices=[
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
                        max_length=20,
                    ),
                ),
                (
                    "comentario",
                    models.TextField(
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "estado_anterior",
                    models.CharField(
                        choices=[
                            ("borrador", "Borrador"),
                            ("en_revision", "En revisión"),
                            ("observada", "Observada"),
                            ("aprobada", "Aprobada"),
                            ("rechazada", "Rechazada"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "estado_resultante",
                    models.CharField(
                        choices=[
                            ("borrador", "Borrador"),
                            ("en_revision", "En revisión"),
                            ("observada", "Observada"),
                            ("aprobada", "Aprobada"),
                            ("rechazada", "Rechazada"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                    ),
                ),
                (
                    "publicacion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="revisiones",
                        to="core.publicacion",
                    ),
                ),
                (
                    "revisor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="revisiones_publicaciones_realizadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "publicaciones_revisiones",
                "ordering": [
                    "-created_at",
                    "-id",
                ],
            },
        ),
        migrations.AddIndex(
            model_name="publicacionrevision",
            index=models.Index(
                fields=[
                    "publicacion",
                    "created_at",
                ],
                name="pubrev_pub_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="publicacionrevision",
            index=models.Index(
                fields=[
                    "decision",
                    "created_at",
                ],
                name="pubrev_dec_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="publicacionrevision",
            index=models.Index(
                fields=[
                    "revisor",
                    "created_at",
                ],
                name="pubrev_rev_fecha_idx",
            ),
        ),
    ]