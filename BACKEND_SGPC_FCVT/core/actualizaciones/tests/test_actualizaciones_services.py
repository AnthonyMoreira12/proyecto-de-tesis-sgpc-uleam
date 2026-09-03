from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.auth.services.auth_profile_services import (
    ProfileEditServiceError,
    ensure_profile_edit_allowed,
)
from core.actualizaciones.services.actualizaciones_services import (
    activar_campania,
    progreso_campania,
    recalcular_participante,
    usuario_puede_editar_campo_por_campania,
)
from core.models import (
    AuditoriaSistema,
    CampaniaActualizacion,
    CampaniaActualizacionUsuario,
    Carrera,
    CarreraSede,
    Facultad,
    Sede,
)


User = get_user_model()


class CampaniaPerfilServicesTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            nombres="Admin",
            apellidos="SGPC",
            password="ClaveSegura123!",
        )
        self.facultad = Facultad.objects.create(nombre="Facultad de Prueba", siglas="FP")
        self.carrera = Carrera.objects.create(nombre="Tecnologías de la Información", facultad=self.facultad)
        self.sede = Sede.objects.create(nombre="Matriz Manta", codigo="matriz-manta")
        CarreraSede.objects.create(sede=self.sede, carrera=self.carrera, activa=True)
        self.user = User.objects.create_user(
            email="docente@uleam.edu.ec",
            nombres="Docente",
            apellidos="Prueba",
            rol="autor",
            auth_source="microsoft",
        )

    def test_activar_campania_asigna_usuario_incompleto_y_registra_auditoria(self):
        campaign = CampaniaActualizacion.objects.create(
            titulo="Actualización académica 2026",
            descripcion="Completar datos incorporados en la nueva versión.",
            tipo=CampaniaActualizacion.TIPO_PERFIL,
            alcance=CampaniaActualizacion.ALCANCE_TODOS,
            campos_habilitados=["identificacion", "sede", "carrera"],
            creado_por=self.admin,
        )

        activated = activar_campania(campaign, admin_user=self.admin)

        participant = CampaniaActualizacionUsuario.objects.get(
            campania=activated,
            usuario=self.user,
        )
        self.assertEqual(activated.estado, CampaniaActualizacion.ESTADO_ACTIVA)
        self.assertEqual(participant.estado, CampaniaActualizacionUsuario.ESTADO_PENDIENTE)
        self.assertEqual(
            set(participant.campos_pendientes),
            {"identificacion", "sede", "carrera"},
        )
        self.assertTrue(
            AuditoriaSistema.objects.filter(
                modulo="actualizaciones",
                accion="activar",
                entidad_id=str(campaign.pk),
            ).exists()
        )
        self.assertIsNotNone(
            usuario_puede_editar_campo_por_campania(
                self.user,
                tipo=CampaniaActualizacion.TIPO_PERFIL,
                campo="sede",
            )
        )

    def test_recalcular_marca_completada_al_llenar_datos(self):
        campaign = CampaniaActualizacion.objects.create(
            titulo="Actualización académica 2026",
            tipo=CampaniaActualizacion.TIPO_PERFIL,
            alcance=CampaniaActualizacion.ALCANCE_TODOS,
            campos_habilitados=["identificacion", "sede", "carrera"],
            creado_por=self.admin,
        )
        activar_campania(campaign, admin_user=self.admin)
        participant = CampaniaActualizacionUsuario.objects.get(campania=campaign, usuario=self.user)

        User.objects.filter(pk=self.user.pk).update(
            identificacion="1300000001",
            sede=self.sede,
            carrera=self.carrera,
        )
        participant.usuario.refresh_from_db()
        recalcular_participante(participant)

        self.assertEqual(participant.estado, CampaniaActualizacionUsuario.ESTADO_COMPLETADA)
        self.assertEqual(participant.campos_pendientes, [])
        self.assertIsNotNone(participant.completada_at)
        self.assertEqual(progreso_campania(campaign)["porcentaje"], 100.0)

    def test_campania_permite_editar_perfil_aunque_plazo_individual_haya_vencido(self):
        User.objects.filter(pk=self.user.pk).update(
            profile_edit_until=timezone.now() - timedelta(hours=1)
        )
        self.user.refresh_from_db()
        campaign = CampaniaActualizacion.objects.create(
            titulo="Completar sede",
            tipo=CampaniaActualizacion.TIPO_PERFIL,
            alcance=CampaniaActualizacion.ALCANCE_TODOS,
            campos_habilitados=["sede", "carrera"],
            creado_por=self.admin,
        )
        activar_campania(campaign, admin_user=self.admin)

        permission = ensure_profile_edit_allowed(
            self.user,
            requested_fields=["sede_set", "carrera_set", "facultad_set"],
        )
        self.assertTrue(permission["via_campaign"])
        self.assertEqual(permission["campaign_ids"], [campaign.pk])

        with self.assertRaises(ProfileEditServiceError):
            ensure_profile_edit_allowed(
                self.user,
                requested_fields=["nombres"],
            )

    def test_campania_vencida_no_es_vigente(self):
        campaign = CampaniaActualizacion(
            titulo="Campaña",
            tipo=CampaniaActualizacion.TIPO_PERFIL,
            estado=CampaniaActualizacion.ESTADO_FINALIZADA,
            campos_habilitados=["sede"],
            creado_por=self.admin,
            fecha_fin=timezone.now(),
        )
        self.assertFalse(campaign.esta_vigente)
