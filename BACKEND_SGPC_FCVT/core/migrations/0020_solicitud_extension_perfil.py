from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_integridad_documental_pdf"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificacion",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("publicacion_enviada", "Publicación enviada"),
                    ("publicacion_observada", "Publicación observada"),
                    ("publicacion_aprobada", "Publicación aprobada"),
                    ("publicacion_rechazada", "Publicación rechazada"),
                    (
                        "nueva_publicacion_revision",
                        "Nueva publicación para revisar",
                    ),
                    (
                        "publicacion_reenviada",
                        "Publicación corregida y reenviada",
                    ),
                    (
                        "solicitud_extension_perfil",
                        "Solicitud de extensión de perfil",
                    ),
                    (
                        "extension_perfil_aprobada",
                        "Extensión de perfil aprobada",
                    ),
                    (
                        "extension_perfil_rechazada",
                        "Extensión de perfil rechazada",
                    ),
                ],
                db_index=True,
                max_length=40,
            ),
        ),
        migrations.CreateModel(
            name="SolicitudExtensionPerfil",
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
                    "horas_solicitadas",
                    models.PositiveSmallIntegerField(),
                ),
                ("motivo", models.TextField()),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("aprobada", "Aprobada"),
                            ("rechazada", "Rechazada"),
                        ],
                        db_index=True,
                        default="pendiente",
                        max_length=16,
                    ),
                ),
                (
                    "plazo_anterior",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "nuevo_plazo",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "solicitada_at",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                (
                    "resuelta_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "motivo_resolucion",
                    models.TextField(blank=True, default=""),
                ),
                (
                    "ip_solicitud",
                    models.GenericIPAddressField(blank=True, null=True),
                ),
                (
                    "resuelta_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="solicitudes_extension_perfil_resueltas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitudes_extension_perfil",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "solicitudes_extension_perfil",
                "ordering": ["-solicitada_at", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="solicitudextensionperfil",
            index=models.Index(
                fields=["estado", "solicitada_at"],
                name="sol_ext_estado_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="solicitudextensionperfil",
            index=models.Index(
                fields=["usuario", "solicitada_at"],
                name="sol_ext_usuario_fecha_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="solicitudextensionperfil",
            constraint=models.UniqueConstraint(
                condition=models.Q(estado="pendiente"),
                fields=("usuario",),
                name="uniq_sol_ext_pendiente_usuario",
            ),
        ),
        migrations.AddConstraint(
            model_name="solicitudextensionperfil",
            constraint=models.CheckConstraint(
                check=models.Q(horas_solicitadas__gt=0),
                name="sol_ext_horas_mayor_cero",
            ),
        ),
    ]
