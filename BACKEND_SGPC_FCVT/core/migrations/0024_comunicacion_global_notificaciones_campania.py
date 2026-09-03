from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_campanias_actualizacion_auditoria"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="notificacion",
            name="visible_en_bandeja",
            field=models.BooleanField(
                db_index=True,
                default=True,
                help_text=(
                    "Permite conservar el registro de envío de correo sin mostrar "
                    "una notificación interna cuando la campaña solo usa email."
                ),
            ),
        ),
        migrations.AlterField(
            model_name="notificacion",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("publicacion_enviada", "Publicación enviada"),
                    ("publicacion_observada", "Publicación observada"),
                    ("publicacion_aprobada", "Publicación aprobada"),
                    ("publicacion_rechazada", "Publicación rechazada"),
                    ("nueva_publicacion_revision", "Nueva publicación para revisar"),
                    ("publicacion_reenviada", "Publicación corregida y reenviada"),
                    ("solicitud_extension_perfil", "Solicitud de extensión de perfil"),
                    ("extension_perfil_aprobada", "Extensión de perfil aprobada"),
                    ("extension_perfil_rechazada", "Extensión de perfil rechazada"),
                    ("campania_actualizacion", "Actualización de información requerida"),
                    ("recordatorio_actualizacion", "Recordatorio de actualización"),
                ],
                db_index=True,
                max_length=40,
            ),
        ),
        migrations.CreateModel(
            name="ComunicacionGlobal",
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
                ("titulo", models.CharField(max_length=200)),
                ("mensaje", models.TextField()),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("informacion", "Información"),
                            ("actualizacion", "Actualización del sistema"),
                            ("importante", "Importante"),
                            ("mantenimiento", "Mantenimiento"),
                        ],
                        db_index=True,
                        default="informacion",
                        max_length=24,
                    ),
                ),
                ("etiqueta_accion", models.CharField(blank=True, default="", max_length=80)),
                ("ruta_accion", models.CharField(blank=True, default="", max_length=255)),
                ("fecha_inicio", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("fecha_fin", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("activa", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("desactivada_at", models.DateTimeField(blank=True, null=True)),
                (
                    "campania",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comunicacion_global",
                        to="core.campaniaactualizacion",
                    ),
                ),
                (
                    "creado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="comunicaciones_globales_creadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "comunicaciones_globales",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="comunicacionglobal",
            index=models.Index(
                fields=["activa", "fecha_inicio", "fecha_fin"],
                name="com_global_vigencia_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="comunicacionglobal",
            index=models.Index(
                fields=["tipo", "created_at"],
                name="com_global_tipo_fecha_idx",
            ),
        ),
    ]
