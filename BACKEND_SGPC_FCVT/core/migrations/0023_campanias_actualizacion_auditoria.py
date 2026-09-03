from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_corregir_plazo_anterior_extension_perfil"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditoriaSistema",
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
                ("accion", models.CharField(db_index=True, max_length=60)),
                ("modulo", models.CharField(db_index=True, max_length=80)),
                ("entidad_tipo", models.CharField(blank=True, default="", max_length=100)),
                (
                    "entidad_id",
                    models.CharField(blank=True, db_index=True, default="", max_length=80),
                ),
                ("descripcion", models.TextField(blank=True, default="")),
                ("datos_anteriores", models.JSONField(blank=True, default=dict)),
                ("datos_nuevos", models.JSONField(blank=True, default=dict)),
                ("contexto", models.JSONField(blank=True, default=dict)),
                ("ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, default="", max_length=500)),
                ("ruta", models.CharField(blank=True, default="", max_length=500)),
                ("metodo_http", models.CharField(blank=True, default="", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="eventos_auditoria",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "auditoria_sistema",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="CampaniaActualizacion",
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
                ("descripcion", models.TextField(blank=True, default="")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("perfil", "Perfil"),
                            ("publicacion", "Publicaciones"),
                            ("proyecto", "Proyectos"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("borrador", "Borrador"),
                            ("activa", "Activa"),
                            ("finalizada", "Finalizada"),
                            ("cancelada", "Cancelada"),
                        ],
                        db_index=True,
                        default="borrador",
                        max_length=20,
                    ),
                ),
                (
                    "alcance",
                    models.CharField(
                        choices=[
                            ("todos", "Todos los usuarios"),
                            ("sede", "Por sede"),
                            ("facultad", "Por facultad"),
                            ("carrera", "Por carrera"),
                            ("usuarios", "Usuarios específicos"),
                        ],
                        db_index=True,
                        default="todos",
                        max_length=20,
                    ),
                ),
                ("fecha_inicio", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("fecha_fin", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("solo_incompletos", models.BooleanField(default=True)),
                ("campos_habilitados", models.JSONField(default=list)),
                ("filtros_destinatarios", models.JSONField(blank=True, default=dict)),
                ("notificar_internamente", models.BooleanField(default=True)),
                ("crear_aviso", models.BooleanField(default=True)),
                ("enviar_correo", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("activada_at", models.DateTimeField(blank=True, null=True)),
                ("finalizada_at", models.DateTimeField(blank=True, null=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="campanias_actualizacion_creadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "campanias_actualizacion",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="CampaniaActualizacionUsuario",
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
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente"),
                            ("en_progreso", "En progreso"),
                            ("completada", "Completada"),
                            ("omitida", "Omitida"),
                        ],
                        db_index=True,
                        default="pendiente",
                        max_length=20,
                    ),
                ),
                ("campos_pendientes", models.JSONField(blank=True, default=list)),
                ("resumen_pendientes", models.JSONField(blank=True, default=dict)),
                ("asignada_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("iniciada_at", models.DateTimeField(blank=True, null=True)),
                ("completada_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "campania",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="participantes",
                        to="core.campaniaactualizacion",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="campanias_actualizacion",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "campanias_actualizacion_usuarios",
                "ordering": ["campania_id", "usuario_id"],
            },
        ),
        migrations.AddIndex(
            model_name="auditoriasistema",
            index=models.Index(
                fields=["modulo", "accion", "created_at"],
                name="audit_mod_acc_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="auditoriasistema",
            index=models.Index(
                fields=["actor", "created_at"],
                name="audit_actor_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="auditoriasistema",
            index=models.Index(
                fields=["entidad_tipo", "entidad_id"],
                name="audit_entidad_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="campaniaactualizacion",
            index=models.Index(
                fields=["estado", "tipo"],
                name="camp_act_estado_tipo_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="campaniaactualizacion",
            index=models.Index(
                fields=["fecha_inicio", "fecha_fin"],
                name="camp_act_fechas_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="campaniaactualizacionusuario",
            index=models.Index(
                fields=["campania", "estado"],
                name="camp_user_camp_estado_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="campaniaactualizacionusuario",
            index=models.Index(
                fields=["usuario", "estado"],
                name="camp_user_usr_estado_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="campaniaactualizacionusuario",
            constraint=models.UniqueConstraint(
                fields=("campania", "usuario"),
                name="uniq_campania_actualizacion_usuario",
            ),
        ),
    ]
