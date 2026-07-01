"""
Signal para sincronizar Autor cuando se guarda un Usuario.
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.auth.services.auth_author_sync_services import asegurar_autor_para_usuario

User = get_user_model()


@receiver(post_save, sender=User)
def sync_autor(sender, instance, created, **kwargs):
    asegurar_autor_para_usuario(instance)