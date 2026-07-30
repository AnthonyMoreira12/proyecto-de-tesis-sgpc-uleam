"""
Signal para sincronizar Usuario con Autor.

La sincronización se ejecuta después de confirmar la transacción
que creó o modificó al usuario.

Solo se programa cuando cambian campos que afectan directamente
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

AUTHOR_SYNC_FIELDS = frozenset(
    {
        "nombres",
        "apellidos",
        "email",
        "identificacion",
        "rol",
        "auth_source",
    }
)


# ============================================================
# SINCRONIZACIÓN DIFERIDA
# ============================================================

def _sync_author_after_commit(
    user_id,
):
    """
    Sincroniza el Autor después de confirmar la transacción.

    Se recupera únicamente la clave primaria porque el servicio
    asegurar_autor_para_usuario() vuelve a consultar y bloquear
    la fila completa del Usuario.
    """
    if not user_id:
        return

    try:
        user = (
            User.objects
            .only("pk")
            .filter(pk=user_id)
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
                "al Usuario %s después de confirmar la "
                "transacción."
            ),
            user_id,
        )

    except Exception:
        """
        El signal es un mecanismo auxiliar.

        Un error inesperado no debe revertir una operación del
        Usuario que ya fue confirmada en la base de datos.
        """
        logger.exception(
            (
                "Se produjo un error inesperado al "
                "sincronizar el Autor del Usuario %s."
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

    La operación se omite cuando:

    - El registro se carga desde fixtures con raw=True.
    - El Usuario todavía no tiene clave primaria.
    - update_fields está vacío.
    - La actualización no afectó ningún campo del Autor.
    """
    del sender
    del kwargs

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
            if field_name
        }

        if not updated_field_names:
            return

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