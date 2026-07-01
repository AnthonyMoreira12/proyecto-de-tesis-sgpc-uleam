import json
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Publicacion, Facultad, Carrera, TipoPublicacion
from core.publicaciones.serializers.base.publicaciones_archivos_serializers import (
    PublicacionArchivoCreateSerializer
)

User = get_user_model()

class PublicacionArchivoSecurityTestCase(TestCase):
    def setUp(self):
        self.facultad = Facultad.objects.create(nombre="Facultad de Prueba")
        self.carrera = Carrera.objects.create(nombre="Carrera de Prueba", facultad=self.facultad)
        
        self.tipo_pub = TipoPublicacion.objects.create(
            nombre="Artículo de Prueba", 
            codigo="art-test", 
            categoria="articulo"
        )
        
        self.user = User.objects.create_user(
            nombres="Carlos",
            apellidos="Velez",
            email="testuser@uleam.edu.ec",
            password="password123",
            identificacion="1316718111"
        )
        
        # CORRECCIÓN: Se elimina el envío de 'facultad' porque ya fue removido del modelo
        self.publicacion = Publicacion.objects.create(
            usuario_creador=self.user,
            carrera=self.carrera,
            tipo=self.tipo_pub
        )

    # CORRECCIÓN: Usamos @patch para simular la lectura de bytes sin depender de Windows
    @patch('core.publicaciones.utils.publicaciones_archivos_utils.magic.from_buffer')
    def test_upload_valid_pdf_success(self, mock_magic):
        """
        Prueba que un archivo con extensión .pdf y contenido estructurado
        como un PDF legítimo sea aceptado.
        """
        # Le decimos al mock: "Finge que el archivo que leíste es un PDF"
        mock_magic.return_value = "application/pdf"

        contenido_pdf_real = b"%PDF-1.5\n% \n1 0 obj\n<< /Type /Catalog ... >>"
        archivo_valido = SimpleUploadedFile(
            name="tesis_valida.pdf",
            content=contenido_pdf_real,
            content_type="application/pdf"
        )

        data = {
            "publicacion": self.publicacion.id,
            "nombre": "Documento de Tesis Legítimo",
            "archivo": archivo_valido,
            "orden": 1
        }

        serializer = PublicacionArchivoCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        archivo_objeto = serializer.save()
        self.assertEqual(archivo_objeto.nombre, "Documento de Tesis Legítimo")

    # CORRECCIÓN: Usamos @patch para simular la detección de un archivo falso
    @patch('core.publicaciones.utils.publicaciones_archivos_utils.magic.from_buffer')
    def test_upload_spoofed_pdf_fails(self, mock_magic):
        """
        Prueba de Seguridad (Anti-Spoofing): Un archivo que simula ser un PDF
        por su extensión pero contiene código debe ser rechazado.
        """
        # Le decimos al mock: "Finge que el archivo que leíste es HTML puro, no un PDF"
        mock_magic.return_value = "text/html"

        contenido_falso = b"<html><body><h1>Malicious Script</h1></body></html>"
        archivo_falso = SimpleUploadedFile(
            name="ataque_disfrazado.pdf",
            content=contenido_falso,
            content_type="application/pdf"
        )

        data = {
            "publicacion": self.publicacion.id,
            "nombre": "Archivo Peligroso",
            "archivo": archivo_falso,
            "orden": 2
        }

        serializer = PublicacionArchivoCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("archivo", serializer.errors)
        self.assertEqual(
            serializer.errors["archivo"][0],
            "El archivo adjunto no es un PDF válido (Firma MIME incorrecta)."
        )