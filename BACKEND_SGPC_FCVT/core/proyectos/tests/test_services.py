from django.test import TestCase
from rest_framework.exceptions import ValidationError

from core.models import Proyecto
from core.proyectos.services.proyectos_proyecto_services import resolver_estado_destino


class ProyectoStateMachineTests(TestCase):
    def setUp(self):
        # Configuramos un proyecto en memoria antes de cada prueba.
        # No usamos .save() porque no necesitamos la base de datos para probar esta lógica.
        self.proyecto = Proyecto(estado="nuevo")

    def test_transicion_automatica_nuevo_a_arrastre(self):
        """
        Si un proyecto está en 'nuevo' y no se envía un estado específico,
        el sistema debe pasarlo automáticamente a 'arrastre'.
        """
        nuevo_estado = resolver_estado_destino(self.proyecto, estado_solicitado="")
        self.assertEqual(nuevo_estado, "arrastre")

    def test_transicion_automatica_arrastre_a_cierre(self):
        """
        Si un proyecto está en 'arrastre' y no se envía un estado específico,
        el sistema debe pasarlo automáticamente a 'cierre'.
        """
        self.proyecto.estado = "arrastre"
        nuevo_estado = resolver_estado_destino(self.proyecto, estado_solicitado="")
        self.assertEqual(nuevo_estado, "cierre")

    def test_transicion_manual_valida(self):
        """
        El usuario administrador puede forzar el paso a un estado válido,
        como pasar de 'nuevo' a 'cierre' directamente.
        """
        nuevo_estado = resolver_estado_destino(self.proyecto, estado_solicitado="cierre")
        self.assertEqual(nuevo_estado, "cierre")

    def test_transicion_invalida_lanza_error(self):
        """
        Si el frontend o un usuario malintencionado intenta enviar un estado
        que no existe, el servicio debe bloquearlo lanzando un ValidationError.
        """
        with self.assertRaises(ValidationError):
            resolver_estado_destino(self.proyecto, estado_solicitado="estado_inventado")

    def test_mapa_de_estados_heredados(self):
        """
        Verifica que el mapa de soporte para versiones antiguas funcione.
        Enviar '1' o 'true' debe interpretarse como 'arrastre'.
        """
        nuevo_estado = resolver_estado_destino(self.proyecto, estado_solicitado="true")
        self.assertEqual(nuevo_estado, "arrastre")