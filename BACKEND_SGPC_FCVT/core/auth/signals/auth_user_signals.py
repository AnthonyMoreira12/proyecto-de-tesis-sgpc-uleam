"""
Signal para sincronizar Usuario con Autor.

La sincronización se programa después de confirmar la
transacción que modificó al usuario. Solo se ejecuta cuando se
crea un usuario o cuando cambia un campo que afecta directamente
al registro Autor.
"""

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import (
    DatabaseError,
    IntegrityError,
    transaction,
)
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.auth.services.auth_author_sync_services import (
    asegurar_autor_para_usuario,
)


logger = logging.getLogger(__name__)

User = get_user_model()


# ============================================================
# CAMPOS QUE AFECTAN AL AUTOR
# ============================================================

AUTHOR_SYNC_FIELDS = {
    "nombres",
    "apellidos",
    "email",
    "identificacion",
    "rol",
    "auth_source",
}


# ============================================================
# SINCRONIZACIÓN DIFERIDA
# ============================================================

def _sync_author_after_commit(user_id):
    """
    Ejecuta la sincronización después de confirmar la
    transacción que guardó al usuario.

    El callback vuelve a consultar al usuario para trabajar con
    los datos definitivamente almacenados en la base de datos.
    """
    try:
        user = (
            User.objects
            .select_related(
                "carrera",
                "carrera__facultad",
            )
            .filter(
                pk=user_id
            )
            .first()
        )

        if user is None:
            return

        asegurar_autor_para_usuario(
            user
        )

    except (
        ValidationError,
        IntegrityError,
        DatabaseError,
    ):
        logger.exception(
            (
                "No se pudo sincronizar el Autor asociado "
                "al Usuario %s."
            ),
            user_id,
        )

    except Exception:
        # El signal es un mecanismo auxiliar. Un error inesperado
        # no debe revertir una operación del usuario que ya fue
        # confirmada en la base de datos.
        logger.exception(
            (
                "Se produjo un error inesperado al sincronizar "
                "el Autor del Usuario %s."
            ),
            user_id,
        )


# ============================================================
# SIGNAL
# ============================================================

@receiver(
    post_save,
    sender=User,
    dispatch_uid=(
        "core.auth.signals."
        "sync_autor_after_user_save"
    ),
)
def sync_autor(
    sender,
    instance,
    created,
    raw=False,
    using=None,
    update_fields=None,
    **kwargs,
):
    """
    Programa la sincronización del Autor cuando corresponde.

    Se omite cuando:

    - El registro se carga desde fixtures con raw=True.
    - El usuario todavía no tiene clave primaria.
    - La actualización no modificó ningún campo relevante para
      el Autor.
    """
    if raw:
        return

    user_id = getattr(
        instance,
        "pk",
        None,
    )

    if not user_id:
        return

    if (
        not created
        and update_fields is not None
    ):
        updated_field_names = {
            str(field_name)
            for field_name in update_fields
        }

        if not (
            updated_field_names
            & AUTHOR_SYNC_FIELDS
        ):
            return

    transaction.on_commit(
        lambda current_user_id=user_id: (
            _sync_author_after_commit(
                current_user_id
            )
        ),
        using=using,
    )