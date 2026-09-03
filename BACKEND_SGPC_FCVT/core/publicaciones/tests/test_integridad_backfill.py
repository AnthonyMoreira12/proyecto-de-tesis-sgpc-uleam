from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Carrera, CarreraSede, Facultad, Publicacion, Sede, TipoPublicacion
from core.publicaciones.services.publicaciones_integridad_backfill_services import (
    backfill_integridad_documental,
)

User = get_user_model()


class IntegridadPdfBackfillTests(TestCase):
    def test_completa_metadata_sin_full_clean_historico(self):
        user = User.objects.create_user(
            email="pdf-backfill@uleam.edu.ec",
            nombres="PDF",
            apellidos="Historico",
        )
        facultad = Facultad.objects.create(nombre="Facultad PDF")
        carrera = Carrera.objects.create(nombre="Carrera PDF", facultad=facultad)
        sede = Sede.objects.create(nombre="Sede PDF", codigo="sede-pdf")
        CarreraSede.objects.create(sede=sede, carrera=carrera, activa=True)
        tipo = TipoPublicacion.objects.create(
            nombre="Libro PDF",
            codigo="libro-pdf",
            categoria="libro",
            orden=9,
        )
        pdf = SimpleUploadedFile(
            "documento_historico.pdf",
            b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF",
            content_type="application/pdf",
        )
        pub = Publicacion.objects.create(
            tipo=tipo,
            usuario_creador=user,
            sede=sede,
            carrera=carrera,
            anio_publicacion=2025,
            archivo_pdf=pdf,
        )
        # Simula la fila previa a 0019 y, además, deja sede NULL para demostrar
        # que el backfill no intenta validar de nuevo el registro completo.
        Publicacion.objects.filter(pk=pub.pk).update(
            sede=None,
            archivo_pdf_nombre_original=None,
            archivo_pdf_tamano_bytes=None,
            archivo_pdf_sha256=None,
        )

        result = backfill_integridad_documental(publication_id=pub.pk)
        self.assertEqual(result["publicaciones_actualizadas"], 1)
        self.assertEqual(result["errores_total"], 0)
        pub.refresh_from_db()
        self.assertIsNone(pub.sede_id)
        self.assertTrue(pub.archivo_pdf_nombre_original)
        self.assertGreater(pub.archivo_pdf_tamano_bytes, 0)
        self.assertEqual(len(pub.archivo_pdf_sha256), 64)
