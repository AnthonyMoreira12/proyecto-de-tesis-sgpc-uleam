from django.contrib.auth import get_user_model
from django.test import TestCase

from core.auditoria.services.auditoria_services import registrar_evento_auditoria
from core.models import AuditoriaSistema


User = get_user_model()


class AuditoriaTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="audit-admin@example.com",
            nombres="Audit",
            apellidos="Admin",
            password="ClaveSegura123!",
        )

    def test_evento_es_inmutable_por_modelo(self):
        event = registrar_evento_auditoria(
            actor=self.admin,
            accion="crear",
            modulo="pruebas",
            entidad_tipo="Objeto",
            entidad_id=10,
            datos_nuevos={"estado": "nuevo"},
        )
        event.descripcion = "Intento de cambio"
        with self.assertRaises(ValueError):
            event.save()
        with self.assertRaises(ValueError):
            event.delete()

        stored = AuditoriaSistema.objects.get(pk=event.pk)
        self.assertEqual(stored.datos_nuevos, {"estado": "nuevo"})
