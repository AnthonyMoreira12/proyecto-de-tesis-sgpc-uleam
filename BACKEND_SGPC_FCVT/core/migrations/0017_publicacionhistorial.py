from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0016_publicacionrevision",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicacionHistorial",
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
                    "actor_nombre",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "actor_email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                    ),
                ),
                (
                    "evento",
                    models.CharField(
                        choices=[
                            (
                                "creada",
                                "Publicación creada",
                            ),
                            (
                                "editada",
                                "Publicación editada",
                            ),
                            (
                                "enviada_revision",
                                "Enviada a revisión",
                            ),
                            (
                                "observada",
                                "Publicación observada",
                            ),
                            (
                                "aprobada",
                                "Publicación aprobada",
                            ),
                            (
                                "rechazada",
                                "Publicación rechazada",
                            ),
                            (
                                "reenviada_revision",
                                "Reenviada a revisión",
                            ),
                        ],
                        db_index=True,
                        max_length=30,
                    ),
                ),
                (
                    "estado_anterior",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("borrador", "Borrador"),
                            ("en_revision", "En revisión"),
                            ("observada", "Observada"),
                            ("aprobada", "Aprobada"),
                            ("rechazada", "Rechazada"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "estado_resultante",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("borrador", "Borrador"),
                            ("en_revision", "En revisión"),
                            ("observada", "Observada"),
                            ("aprobada", "Aprobada"),
                            ("rechazada", "Rechazada"),
                        ],
                        max_length=20,
                        null=True,
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
                    "detalle",
                    models.JSONField(
                        blank=True,
                        default=dict,
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
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="historial_publicaciones_realizado",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "publicacion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historial",
                        to="core.publicacion",
                    ),
                ),
            ],
            options={
                "db_table": "publicaciones_historial",
                "ordering": [
                    "-created_at",
                    "-id",
                ],
            },
        ),
        migrations.AddIndex(
            model_name="publicacionhistorial",
            index=models.Index(
                fields=[
                    "publicacion",
                    "created_at",
                ],
                name="pubhist_pub_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="publicacionhistorial",
            index=models.Index(
                fields=[
                    "evento",
                    "created_at",
                ],
                name="pubhist_evt_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="publicacionhistorial",
            index=models.Index(
                fields=[
                    "actor",
                    "created_at",
                ],
                name="pubhist_act_fecha_idx",
            ),
        ),
    ]