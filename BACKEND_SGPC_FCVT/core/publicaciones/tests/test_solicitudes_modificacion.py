from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import (
    AuditoriaSistema,
    Autor,
    Carrera,
    CarreraSede,
    Facultad,
    Libro,
    Notificacion,
    Publicacion,
    PublicacionAutor,
    Sede,
    SolicitudModificacionPublicacion,
    TipoPublicacion,
)

User = get_user_model()


class SolicitudModificacionPublicacionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin-solmod@example.com",
            nombres="Admin",
            apellidos="Solicitudes",
            password="Clave123!",
        )
        self.user = User.objects.create_user(
            email="docente-solmod@uleam.edu.ec",
            nombres="Docente",
            apellidos="Solicitudes",
            rol="autor",
            auth_source="microsoft",
        )
        self.facultad = Facultad.objects.create(nombre="Facultad Solicitudes", siglas="FS")
        self.carrera = Carrera.objects.create(nombre="Carrera Solicitudes", facultad=self.facultad)
        self.sede = Sede.objects.create(nombre="Matriz Solicitudes", codigo="mat-solmod")
        CarreraSede.objects.create(sede=self.sede, carrera=self.carrera, activa=True)
        self.user.sede = self.sede
        self.user.carrera = self.carrera
        self.user.identificacion = "1300000001"
        self.user.save()

        self.tipo = TipoPublicacion.objects.create(
            nombre="Libro solicitud",
            codigo="libro",
            categoria="libro",
            orden=1,
        )
        self.publicacion = Publicacion.objects.create(
            tipo=self.tipo,
            usuario_creador=self.user,
            sede=self.sede,
            carrera=self.carrera,
            estado=Publicacion.ESTADO_APROBADA,
            anio_publicacion=2025,
            origen_tipo="ninguno",
        )
        self.libro = Libro.objects.create(
            publicacion=self.publicacion,
            nombre_libro="Libro original",
            codigo_isbn="978-9978-00-000-1",
            editorial_compilador="Editorial ULEAM",
            revisor_par_arbitraje="si",
            link_libro="https://example.com/libro-original",
        )
        autor = Autor.objects.create(
            usuario=self.user,
            nombres=self.user.nombres,
            apellidos=self.user.apellidos,
            correo=self.user.email,
        )
        PublicacionAutor.objects.create(publicacion=self.publicacion, autor=autor, orden=1)

    def _crear_solicitud(self, nombre="Libro corregido"):
        self.client.force_authenticate(self.user)
        return self.client.post(
            "/api/solicitudes-modificacion-publicaciones/",
            {
                "publicacion": self.publicacion.pk,
                "motivo": "Corregir el título bibliográfico validado.",
                "cambios_solicitados": {"nombre_libro": nombre},
            },
            format="json",
        )

    def test_crear_y_aprobar_solicitud_aplica_cambio(self):
        response = self._crear_solicitud()
        self.assertEqual(response.status_code, 201, response.data)
        solicitud_id = response.data["id"]
        self.assertTrue(
            Notificacion.objects.filter(
                destinatario=self.admin,
                tipo=Notificacion.TIPO_SOLICITUD_MODIFICACION_PUBLICACION,
            ).exists()
        )

        self.client.force_authenticate(self.admin)
        approve = self.client.post(
            f"/api/admin/solicitudes-modificacion-publicaciones/{solicitud_id}/aprobar/",
            {"comentario": "Documento de respaldo revisado."},
            format="json",
        )
        self.assertEqual(approve.status_code, 200, approve.data)

        self.libro.refresh_from_db()
        self.assertEqual(self.libro.nombre_libro, "Libro corregido")
        solicitud = SolicitudModificacionPublicacion.objects.get(pk=solicitud_id)
        self.assertEqual(solicitud.estado, SolicitudModificacionPublicacion.ESTADO_APROBADA)
        self.assertIsNotNone(solicitud.aplicado_at)
        self.assertTrue(
            Notificacion.objects.filter(
                destinatario=self.user,
                tipo=Notificacion.TIPO_MODIFICACION_PUBLICACION_APROBADA,
            ).exists()
        )
        self.assertTrue(
            AuditoriaSistema.objects.filter(
                modulo="publicaciones",
                accion="aprobar",
                entidad_tipo="SolicitudModificacionPublicacion",
                entidad_id=str(solicitud_id),
            ).exists()
        )

    def test_rechazo_no_modifica_publicacion(self):
        response = self._crear_solicitud("No debe aplicarse")
        self.client.force_authenticate(self.admin)
        reject = self.client.post(
            f"/api/admin/solicitudes-modificacion-publicaciones/{response.data['id']}/rechazar/",
            {"comentario": "El respaldo no justifica el cambio."},
            format="json",
        )
        self.assertEqual(reject.status_code, 200, reject.data)
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.nombre_libro, "Libro original")

    def test_aprobacion_detecta_publicacion_modificada_despues(self):
        response = self._crear_solicitud("Cambio obsoleto")
        Publicacion.objects.filter(pk=self.publicacion.pk).update(updated_at=timezone.now())
        self.client.force_authenticate(self.admin)
        approve = self.client.post(
            f"/api/admin/solicitudes-modificacion-publicaciones/{response.data['id']}/aprobar/",
            {},
            format="json",
        )
        self.assertEqual(approve.status_code, 409, approve.data)
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.nombre_libro, "Libro original")
