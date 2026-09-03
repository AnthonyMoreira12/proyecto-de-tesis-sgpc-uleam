from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from core.actualizaciones.services.actualizaciones_recordatorios_services import (
    sincronizar_avisos_actualizacion_usuario,
)
from core.actualizaciones.services.actualizaciones_services import activar_campania
from core.actualizaciones.views.actualizaciones_viewsets import MisActualizacionesViewSet
from core.models import (
    CampaniaActualizacion,
    CampaniaActualizacionUsuario,
    Notificacion,
)


User = get_user_model()


class ActualizacionesRecordatoriosTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin-recordatorios@example.com",
            nombres="Admin",
            apellidos="Recordatorios",
            password="ClaveSegura123!",
        )
        self.user = User.objects.create_user(
            email="docente-recordatorios@uleam.edu.ec",
            nombres="Docente",
            apellidos="Recordatorios",
            rol="autor",
            auth_source="microsoft",
        )

    def _activate_campaign(self, **overrides):
        payload = {
            "titulo": "Completar identificación",
            "tipo": CampaniaActualizacion.TIPO_PERFIL,
            "alcance": CampaniaActualizacion.ALCANCE_TODOS,
            "campos_habilitados": ["identificacion"],
            "creado_por": self.admin,
        }
        payload.update(overrides)
        campaign = CampaniaActualizacion.objects.create(**payload)
        activar_campania(campaign, admin_user=self.admin)
        return campaign

    def _participant(self, campaign):
        return CampaniaActualizacionUsuario.objects.get(
            campania=campaign,
            usuario=self.user,
        )

    def _update_notifications(self, campaign):
        participant = self._participant(campaign)
        return Notificacion.objects.filter(
            destinatario=self.user,
            tipo__in=[
                Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
                Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
            ],
            metadata__campania_id=campaign.pk,
            metadata__participante_id=participant.pk,
        )


    def test_estado_aviso_action_returns_modal_summary(self):
        self._activate_campaign()
        factory = APIRequestFactory()
        request = factory.post(
            "/api/mis-actualizaciones/estado-aviso/",
            {},
            format="json",
        )
        force_authenticate(request, user=self.user)
        view = MisActualizacionesViewSet.as_view({"post": "estado_aviso"})

        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["requiere_actualizacion"])
        self.assertEqual(response.data["total_campos_pendientes"], 1)

    def test_sync_reports_pending_data_and_keeps_notification_visible(self):
        campaign = self._activate_campaign()

        result = sincronizar_avisos_actualizacion_usuario(self.user)

        self.assertTrue(result["requiere_actualizacion"])
        self.assertEqual(result["total_campanias"], 1)
        self.assertEqual(result["total_campos_pendientes"], 1)
        self.assertEqual(result["por_tipo"]["perfil"]["campos"], 1)
        self.assertTrue(
            self._update_notifications(campaign).filter(
                visible_en_bandeja=True,
                leida=False,
            ).exists()
        )

    def test_sync_creates_visible_notification_even_if_campaign_disabled_internal_notice(self):
        campaign = self._activate_campaign(
            notificar_internamente=False,
            enviar_correo=False,
        )

        self.assertFalse(
            self._update_notifications(campaign).filter(
                visible_en_bandeja=True,
            ).exists()
        )

        result = sincronizar_avisos_actualizacion_usuario(self.user)

        self.assertEqual(result["notificaciones_creadas"], 1)
        self.assertTrue(
            self._update_notifications(campaign).filter(
                tipo=Notificacion.TIPO_CAMPANIA_ACTUALIZACION,
                visible_en_bandeja=True,
            ).exists()
        )

    def test_reminder_is_created_only_after_three_days(self):
        campaign = self._activate_campaign()
        notifications = self._update_notifications(campaign)

        first = sincronizar_avisos_actualizacion_usuario(self.user)
        self.assertEqual(first["recordatorios_creados"], 0)

        notifications.update(
            created_at=timezone.now() - timedelta(days=3, minutes=1)
        )

        result = sincronizar_avisos_actualizacion_usuario(self.user)
        self.assertEqual(result["recordatorios_creados"], 1)
        self.assertEqual(
            notifications.filter(
                tipo=Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
            ).count(),
            1,
        )

        repeated = sincronizar_avisos_actualizacion_usuario(self.user)
        self.assertEqual(repeated["recordatorios_creados"], 0)
        self.assertEqual(
            notifications.filter(
                tipo=Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
            ).count(),
            1,
        )

    def test_completing_required_data_stops_reminders_and_closes_unread_notice(self):
        campaign = self._activate_campaign()
        notifications = self._update_notifications(campaign)

        notifications.update(
            created_at=timezone.now() - timedelta(days=4)
        )
        sincronizar_avisos_actualizacion_usuario(self.user)

        self.assertTrue(
            notifications.filter(leida=False).exists()
        )

        User.objects.filter(pk=self.user.pk).update(
            identificacion="1300000001"
        )
        self.user.refresh_from_db()

        result = sincronizar_avisos_actualizacion_usuario(self.user)

        self.assertFalse(result["requiere_actualizacion"])
        participant = self._participant(campaign)
        self.assertEqual(
            participant.estado,
            CampaniaActualizacionUsuario.ESTADO_COMPLETADA,
        )
        self.assertFalse(
            notifications.filter(leida=False).exists()
        )

        reminder_count = notifications.filter(
            tipo=Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
        ).count()
        next_result = sincronizar_avisos_actualizacion_usuario(self.user)
        self.assertEqual(next_result["recordatorios_creados"], 0)
        self.assertEqual(
            notifications.filter(
                tipo=Notificacion.TIPO_RECORDATORIO_ACTUALIZACION,
            ).count(),
            reminder_count,
        )
