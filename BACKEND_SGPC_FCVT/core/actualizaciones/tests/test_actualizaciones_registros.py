from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.actualizaciones.services.actualizaciones_services import activar_campania
from core.models import (
    AuditoriaSistema,
    Autor,
    CampaniaActualizacion,
    CampaniaActualizacionUsuario,
    Carrera,
    CarreraSede,
    Facultad,
    Libro,
    Proyecto,
    ProyectoAutor,
    Publicacion,
    Sede,
    TipoPublicacion,
)


User = get_user_model()


class CampaniaRegistrosApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin-registros@example.com",
            nombres="Admin",
            apellidos="Registros",
            password="ClaveSegura123!",
        )
        self.user = User.objects.create_user(
            email="docente-registros@uleam.edu.ec",
            nombres="Docente",
            apellidos="Registros",
            rol="autor",
            auth_source="microsoft",
        )
        self.other = User.objects.create_user(
            email="otro-registros@uleam.edu.ec",
            nombres="Otro",
            apellidos="Docente",
            rol="autor",
            auth_source="microsoft",
        )

        self.facultad = Facultad.objects.create(
            nombre="Facultad Registros",
            siglas="FR",
        )
        self.carrera = Carrera.objects.create(
            nombre="Tecnologías de la Información Registros",
            facultad=self.facultad,
        )
        self.sede = Sede.objects.create(
            nombre="Matriz Manta Registros",
            codigo="matriz-registros",
        )
        CarreraSede.objects.create(
            sede=self.sede,
            carrera=self.carrera,
            activa=True,
        )

        self.tipo_libro = TipoPublicacion.objects.create(
            nombre="Libro de prueba de campaña",
            codigo="libro",
            categoria="libro",
            orden=1,
        )

        self.publicacion = Publicacion.objects.create(
            tipo=self.tipo_libro,
            usuario_creador=self.user,
            carrera=self.carrera,
            sede=self.sede,
            estado=Publicacion.ESTADO_APROBADA,
            anio_publicacion=2025,
            origen_tipo="ninguno",
        )
        # Simula un registro histórico anterior a la incorporación de Sede.
        Publicacion.objects.filter(pk=self.publicacion.pk).update(sede=None)
        self.publicacion.refresh_from_db()
        Libro.objects.create(
            publicacion=self.publicacion,
            nombre_libro="Libro válido",
            codigo_isbn="978-9978-00-000-1",
            editorial_compilador="Editorial ULEAM",
            revisor_par_arbitraje="si",
            link_libro="https://example.com/libro",
        )

        self.autor = Autor.objects.create(
            usuario=self.user,
            nombres=self.user.nombres,
            apellidos=self.user.apellidos,
            correo=self.user.email,
        )
        self.other_autor = Autor.objects.create(
            usuario=self.other,
            nombres=self.other.nombres,
            apellidos=self.other.apellidos,
            correo=self.other.email,
        )

        self.proyecto = Proyecto.objects.create(
            nombre="Proyecto histórico campaña",
            descripcion="",
            sede=None,
            carrera=self.carrera,
            creado_por=self.admin,
            estado="cierre",
        )
        ProyectoAutor.objects.create(
            proyecto=self.proyecto,
            autor=self.autor,
            rol="principal",
            orden=1,
        )

    def _activate_publication_campaign(self):
        campaign = CampaniaActualizacion.objects.create(
            titulo="Completar sede de publicaciones",
            tipo=CampaniaActualizacion.TIPO_PUBLICACION,
            alcance=CampaniaActualizacion.ALCANCE_TODOS,
            campos_habilitados=["sede"],
            creado_por=self.admin,
        )
        activar_campania(campaign, admin_user=self.admin)
        return campaign

    def _activate_project_campaign(self):
        campaign = CampaniaActualizacion.objects.create(
            titulo="Completar sede de proyectos",
            tipo=CampaniaActualizacion.TIPO_PROYECTO,
            alcance=CampaniaActualizacion.ALCANCE_TODOS,
            campos_habilitados=["sede"],
            creado_por=self.admin,
        )
        activar_campania(campaign, admin_user=self.admin)
        return campaign

    def test_publicacion_aprobada_puede_completar_sede_por_campania(self):
        campaign = self._activate_publication_campaign()
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            f"/api/publicaciones/{self.publicacion.pk}/",
            {"sede": self.sede.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.publicacion.refresh_from_db()
        self.assertEqual(self.publicacion.sede_id, self.sede.pk)
        self.assertTrue(
            AuditoriaSistema.objects.filter(
                actor=self.user,
                modulo="publicaciones",
                accion="actualizar",
                entidad_id=str(self.publicacion.pk),
                contexto__origen="actualizacion_global",
            ).exists()
        )
        participant = CampaniaActualizacionUsuario.objects.get(
            campania=campaign,
            usuario=self.user,
        )
        self.assertEqual(
            participant.estado,
            CampaniaActualizacionUsuario.ESTADO_COMPLETADA,
        )

    def test_publicacion_aprobada_rechaza_campo_sensible_no_habilitado(self):
        self._activate_publication_campaign()
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            f"/api/publicaciones/{self.publicacion.pk}/",
            {"nombre_libro": "Intento de cambio sensible"},
            format="json",
        )

        self.assertEqual(response.status_code, 403, response.data)
        self.publicacion.libro.refresh_from_db()
        self.assertEqual(self.publicacion.libro.nombre_libro, "Libro válido")

    def test_otro_usuario_no_puede_usar_campania_sobre_publicacion_ajena(self):
        self._activate_publication_campaign()
        self.client.force_authenticate(self.other)

        response = self.client.patch(
            f"/api/publicaciones/{self.publicacion.pk}/",
            {"sede": self.sede.pk},
            format="json",
        )

        self.assertIn(response.status_code, {403, 404})
        self.publicacion.refresh_from_db()
        self.assertIsNone(self.publicacion.sede_id)

    def test_proyecto_historico_participante_puede_completar_sede(self):
        campaign = self._activate_project_campaign()
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            f"/api/proyectos/{self.proyecto.pk}/",
            {"sede": self.sede.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.sede_id, self.sede.pk)
        self.assertTrue(
            AuditoriaSistema.objects.filter(
                actor=self.user,
                modulo="proyectos",
                accion="actualizar",
                entidad_id=str(self.proyecto.pk),
                contexto__origen="actualizacion_global",
            ).exists()
        )
        participant = CampaniaActualizacionUsuario.objects.get(
            campania=campaign,
            usuario=self.user,
        )
        self.assertEqual(
            participant.estado,
            CampaniaActualizacionUsuario.ESTADO_COMPLETADA,
        )


    def test_detalle_publicacion_expone_campos_de_campania(self):
        campaign = self._activate_publication_campaign()
        self.client.force_authenticate(self.user)

        response = self.client.get(
            f"/api/publicaciones/{self.publicacion.pk}/",
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(response.data["puede_editar"])
        self.assertTrue(response.data["edicion_por_campania"])
        self.assertEqual(response.data["campos_editables_campania"], ["sede"])
        self.assertEqual(response.data["campos_pendientes_campania"], ["sede"])
        self.assertEqual(response.data["campanias_actualizacion_ids"], [campaign.pk])

    def test_proyecto_participante_rechaza_campo_no_habilitado(self):
        self._activate_project_campaign()
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            f"/api/proyectos/{self.proyecto.pk}/",
            {"nombre": "Intento de renombrar proyecto"},
            format="json",
        )

        self.assertEqual(response.status_code, 403, response.data)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.nombre, "Proyecto histórico campaña")

    def test_usuario_no_participante_no_puede_editar_proyecto_por_campania(self):
        self._activate_project_campaign()
        self.client.force_authenticate(self.other)

        response = self.client.patch(
            f"/api/proyectos/{self.proyecto.pk}/",
            {"sede": self.sede.pk},
            format="json",
        )

        self.assertIn(response.status_code, {403, 404})
        self.proyecto.refresh_from_db()
        self.assertIsNone(self.proyecto.sede_id)
