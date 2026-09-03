from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from core.actualizaciones.services.actualizaciones_services import (
    activar_campania,
    finalizar_campania,
)
from core.comunicaciones.services.comunicaciones_services import notificar_campania
from core.models import (
    CampaniaActualizacion,
    CampaniaActualizacionUsuario,
    ComunicacionGlobal,
    Notificacion,
)


User = get_user_model()


class ComunicacionesCampaniaTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin-comunicaciones@example.com",
            nombres="Admin",
            apellidos="Comunicaciones",
            password="ClaveSegura123!",
        )
        self.user_pending = User.objects.create_user(
            email="pendiente@uleam.edu.ec",
            nombres="Usuario",
            apellidos="Pendiente",
            rol="autor",
            auth_source="microsoft",
        )
        self.user_complete = User.objects.create_user(
            email="completo@uleam.edu.ec",
            nombres="Usuario",
            apellidos="Completo",
            rol="autor",
            auth_source="microsoft",
            identificacion="1300000001",
        )

    def _campaign(self, **overrides):
        values = {
            "titulo": "Actualización institucional 2026",
            "descripcion": "Revise y complete la información incorporada en la nueva versión.",
            "tipo": CampaniaActualizacion.TIPO_PERFIL,
            "alcance": CampaniaActualizacion.ALCANCE_TODOS,
            "campos_habilitados": ["identificacion"],
            "solo_incompletos": False,
            "notificar_internamente": True,
            "crear_aviso": True,
            "enviar_correo": False,
            "fecha_fin": timezone.now() + timedelta(days=10),
            "creado_por": self.admin,
        }
        values.update(overrides)
        return CampaniaActualizacion.objects.create(**values)

    def test_activar_crea_comunicacion_y_notificaciones(self):
        campaign = self._campaign()
        activar_campania(campaign, admin_user=self.admin)

        communication = ComunicacionGlobal.objects.get(campania=campaign)
        self.assertTrue(communication.activa)
        self.assertEqual(communication.tipo, ComunicacionGlobal.TIPO_ACTUALIZACION)
        self.assertEqual(communication.ruta_accion, "/informacion-pendiente")

        notifications = Notificacion.objects.filter(
            metadata__campania_id=campaign.pk,
            tipo=Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
        )
        self.assertEqual(notifications.count(), 2)
        self.assertEqual(notifications.filter(visible_en_bandeja=True).count(), 2)
        self.assertEqual(notifications.filter(email_programado=True).count(), 0)

    def test_solo_correo_crea_registro_oculto_para_tracking(self):
        campaign = self._campaign(
            notificar_internamente=False,
            enviar_correo=True,
            crear_aviso=False,
        )
        activar_campania(campaign, admin_user=self.admin)

        notifications = Notificacion.objects.filter(
            metadata__campania_id=campaign.pk,
            tipo=Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
        )
        self.assertEqual(notifications.count(), 2)
        self.assertEqual(notifications.filter(visible_en_bandeja=True).count(), 0)
        self.assertEqual(notifications.filter(email_programado=True).count(), 2)
        self.assertFalse(ComunicacionGlobal.objects.filter(campania=campaign).exists())

    def test_recordatorio_se_envia_solo_a_pendientes(self):
        campaign = self._campaign()
        activar_campania(campaign, admin_user=self.admin)

        participant_complete = CampaniaActualizacionUsuario.objects.get(
            campania=campaign,
            usuario=self.user_complete,
        )
        self.assertEqual(
            participant_complete.estado,
            CampaniaActualizacionUsuario.ESTADO_COMPLETADA,
        )

        result = notificar_campania(
            campaign,
            actor=self.admin,
            recordatorio=True,
            solo_pendientes=True,
        )

        self.assertEqual(result["destinatarios"], 1)
        reminders = Notificacion.objects.filter(
            metadata__campania_id=campaign.pk,
            tipo=Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
        )
        self.assertEqual(reminders.count(), 1)
        self.assertEqual(reminders.first().destinatario_id, self.user_pending.pk)

    def test_finalizar_desactiva_comunicacion(self):
        campaign = self._campaign()
        activar_campania(campaign, admin_user=self.admin)
        finalizar_campania(campaign, admin_user=self.admin)

        communication = ComunicacionGlobal.objects.get(campania=campaign)
        self.assertFalse(communication.activa)
        self.assertIsNotNone(communication.desactivada_at)
    def test_correo_programado_se_envia_despues_del_commit(self):
        campaign = self._campaign(
            notificar_internamente=False,
            enviar_correo=True,
            crear_aviso=False,
        )
        with self.captureOnCommitCallbacks(execute=True):
            activar_campania(campaign, admin_user=self.admin)

        notifications = Notificacion.objects.filter(
            metadata__campania_id=campaign.pk,
            tipo=Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
        )
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(notifications.filter(email_enviado=True).count(), 2)
        self.assertEqual(notifications.exclude(email_error__isnull=True).count(), 0)

