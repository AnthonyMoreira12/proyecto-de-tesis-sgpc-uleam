from django.contrib.auth import get_user_model
from django.test import TestCase

from core.migracion_produccion.services.migracion_produccion_services import (
    comparar_snapshots_produccion,
    diagnostico_actualizacion_produccion,
    normalizar_actualizacion_produccion,
    snapshot_metricas_produccion,
)
from core.models import (
    Carrera,
    CarreraSede,
    Facultad,
    Proyecto,
    Publicacion,
    Sede,
    TipoPublicacion,
)


User = get_user_model()


class PreparacionProduccionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin-migracion@example.com",
            nombres="Admin",
            apellidos="Migracion",
            password="ClaveSegura123!",
        )
        self.facultad = Facultad.objects.create(nombre="Facultad Migracion", siglas="FM")
        self.carrera = Carrera.objects.create(nombre="Carrera Migracion", facultad=self.facultad)
        self.sede = Sede.objects.create(nombre="Matriz Manta Migracion", codigo="matriz-migracion")
        CarreraSede.objects.create(sede=self.sede, carrera=self.carrera, activa=True)
        self.user = User.objects.create_user(
            email="historico@uleam.edu.ec",
            nombres="Usuario",
            apellidos="Historico",
            identificacion="1300000001",
            carrera=self.carrera,
            rol="autor",
            auth_source="microsoft",
        )
        self.tipo = TipoPublicacion.objects.create(
            nombre="Libro migracion",
            codigo="libro-migracion",
            categoria="libro",
            orden=99,
        )
        self.proyecto = Proyecto.objects.create(
            nombre="Proyecto historico",
            sede=self.sede,
            carrera=self.carrera,
            creado_por=self.admin,
            estado="nuevo",
        )
        self.publicacion = Publicacion.objects.create(
            tipo=self.tipo,
            usuario_creador=self.user,
            sede=self.sede,
            carrera=self.carrera,
            proyecto=self.proyecto,
            anio_publicacion=2025,
            estado=Publicacion.ESTADO_APROBADA,
        )
        Proyecto.objects.filter(pk=self.proyecto.pk).update(sede=None)
        Publicacion.objects.filter(pk=self.publicacion.pk).update(sede=None)
        User.objects.filter(pk=self.user.pk).update(sede=None, perfil_completo=False)
        self.user.refresh_from_db()
        self.proyecto.refresh_from_db()
        self.publicacion.refresh_from_db()

    def test_diagnostico_identifica_nulos_sin_modificarlos(self):
        diag = diagnostico_actualizacion_produccion()
        self.assertGreaterEqual(diag["usuarios"]["sin_sede"], 1)
        self.assertGreaterEqual(diag["publicaciones"]["sin_sede"], 1)
        self.assertGreaterEqual(diag["proyectos"]["sin_sede"], 1)
        self.assertTrue(diag["catalogos"]["carreras_sedes_activas"] >= 1)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.sede_id)

    def test_dry_run_propone_sede_predeterminada_sin_escribir(self):
        result = normalizar_actualizacion_produccion(
            dry_run=True,
            default_sede_id=self.sede.pk,
            usar_sede_predeterminada=True,
        )
        self.assertEqual(result["resumen"]["usuarios_sede"], 1)
        self.assertEqual(result["resumen"]["proyectos_sede"], 1)
        self.assertEqual(result["resumen"]["publicaciones_sede"], 1)
        self.user.refresh_from_db()
        self.proyecto.refresh_from_db()
        self.publicacion.refresh_from_db()
        self.assertIsNone(self.user.sede_id)
        self.assertIsNone(self.proyecto.sede_id)
        self.assertIsNone(self.publicacion.sede_id)

    def test_aplicar_normaliza_y_preserva_conteos_criticos(self):
        before = snapshot_metricas_produccion()
        result = normalizar_actualizacion_produccion(
            dry_run=False,
            default_sede_id=self.sede.pk,
            usar_sede_predeterminada=True,
        )
        self.user.refresh_from_db()
        self.proyecto.refresh_from_db()
        self.publicacion.refresh_from_db()
        self.assertEqual(self.user.sede_id, self.sede.pk)
        self.assertEqual(self.proyecto.sede_id, self.sede.pk)
        self.assertEqual(self.publicacion.sede_id, self.sede.pk)
        self.assertTrue(self.user.perfil_completo)
        comparison = comparar_snapshots_produccion(before)
        self.assertEqual(comparison["estado"], "OK")
        self.assertFalse(comparison["perdida_detectada"])
        self.assertEqual(result["comparacion"]["estado"], "OK")

    def test_publicacion_infiere_sede_desde_usuario_sin_default(self):
        User.objects.filter(pk=self.user.pk).update(sede=self.sede, perfil_completo=True)
        result = normalizar_actualizacion_produccion(dry_run=False)
        self.publicacion.refresh_from_db()
        self.assertEqual(self.publicacion.sede_id, self.sede.pk)
        change = next(item for item in result["cambios"]["publicaciones_sede"] if item["id"] == self.publicacion.pk)
        self.assertEqual(change["fuente"], "usuario_creador")

from rest_framework.test import APIClient


class PreparacionProduccionApiTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin-api-migracion@example.com",
            nombres="Admin",
            apellidos="API",
            password="ClaveSegura123!",
        )
        self.normal = User.objects.create_user(
            email="usuario-api@example.com",
            nombres="Usuario",
            apellidos="API",
            password="ClaveSegura123!",
        )
        self.client = APIClient()

    def test_diagnostico_es_solo_administrativo(self):
        self.client.force_authenticate(self.normal)
        response = self.client.get("/api/admin/preparacion-produccion/diagnostico/")
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/admin/preparacion-produccion/diagnostico/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("snapshot", response.data)

    def test_aplicacion_real_exige_confirmacion_explicita(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/admin/preparacion-produccion/normalizar/",
            {"dry_run": False},
            format="json",
        )
        self.assertEqual(response.status_code, 409)
