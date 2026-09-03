from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0017_publicacionhistorial",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Notificacion",
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
                    "tipo",
                    models.CharField(
                        choices=[
                            (
                                "publicacion_enviada",
                                "Publicación enviada",
                            ),
                            (
                                "publicacion_observada",
                                "Publicación observada",
                            ),
                            (
                                "publicacion_aprobada",
                                "Publicación aprobada",
                            ),
                            (
                                "publicacion_rechazada",
                                "Publicación rechazada",
                            ),
                            (
                                "nueva_publicacion_revision",
                                "Nueva publicación para revisar",
                            ),
                            (
                                "publicacion_reenviada",
                                "Publicación corregida y reenviada",
                            ),
                        ],
                        db_index=True,
                        max_length=40,
                    ),
                ),
                (
                    "titulo",
                    models.CharField(
                        max_length=200,
                    ),
                ),
                (
                    "mensaje",
                    models.TextField(),
                ),
                (
                    "leida",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                    ),
                ),
                (
                    "leida_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        default=dict,
                    ),
                ),
                (
                    "email_programado",
                    models.BooleanField(
                        default=False,
                    ),
                ),
                (
                    "email_enviado",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                    ),
                ),
                (
                    "email_intentado_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "email_error",
                    models.TextField(
                        blank=True,
                        null=True,
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
                    "destinatario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notificaciones",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "publicacion",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notificaciones",
                        to="core.publicacion",
                    ),
                ),
            ],
            options={
                "db_table": "notificaciones",
                "ordering": [
                    "-created_at",
                    "-id",
                ],
            },
        ),
        migrations.AddIndex(
            model_name="notificacion",
            index=models.Index(
                fields=[
                    "destinatario",
                    "leida",
                    "created_at",
                ],
                name="notif_dest_leida_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="notificacion",
            index=models.Index(
                fields=[
                    "tipo",
                    "created_at",
                ],
                name="notif_tipo_fecha_idx",
            ),
        ),
    ]