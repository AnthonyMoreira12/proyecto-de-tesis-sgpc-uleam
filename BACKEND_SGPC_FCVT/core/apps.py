from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Registra únicamente signals de auditoría de modelos de negocio.
        from core.auditoria import signals  # noqa: F401
