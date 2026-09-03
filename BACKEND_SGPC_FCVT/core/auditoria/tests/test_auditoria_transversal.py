from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from core.auditoria.context import reset_current_request, set_current_request
from core.models import AuditoriaSistema, Sede

User = get_user_model()


class AuditoriaTransversalTests(TestCase):
    def test_actualizacion_modelo_registra_actor_y_diff(self):
        admin = User.objects.create_superuser(
            email="audit-transversal@example.com",
            nombres="Admin",
            apellidos="Audit",
            password="Secreto123!",
        )
        sede = Sede.objects.create(nombre="Sede Uno", codigo="sede-uno")
        request = RequestFactory().patch("/api/admin/sedes/1/")
        request.user = admin
        token = set_current_request(request)
        try:
            sede.nombre = "Sede Dos"
            sede.save()
        finally:
            reset_current_request(token)

        event = AuditoriaSistema.objects.filter(
            modulo="estructura_academica",
            entidad_tipo="Sede",
            entidad_id=str(sede.pk),
            accion="actualizar",
        ).latest("id")
        self.assertEqual(event.actor_id, admin.pk)
        self.assertEqual(event.datos_anteriores.get("nombre"), "Sede Uno")
        self.assertEqual(event.datos_nuevos.get("nombre"), "Sede Dos")
        self.assertEqual(event.metodo_http, "PATCH")
        self.assertNotIn("password", event.datos_nuevos)
