from django.test import TestCase

from core.models import Ciudad, Pais
from core.publicaciones.serializers.create.publicaciones_ponencia_create_serializers import (
    _resolve_city_for_create,
)


class PonenciaCiudadManualTests(TestCase):

    def test_ciudad_manual_crea_registro_en_pais(self):
        pais = Pais.objects.create(
            nombre="Ecuador",
            iso2="EC",
            iso3="ECU",
        )

        ciudad = _resolve_city_for_create(
            pais=pais,
            ciudad_manual="  Loja  ",
        )

        self.assertEqual(
            ciudad.nombre,
            "Loja",
        )

        self.assertEqual(
            ciudad.pais_id,
            pais.id,
        )

        self.assertEqual(
            Ciudad.objects.filter(
                pais=pais,
                nombre="Loja",
            ).count(),
            1,
        )

    def test_ciudad_manual_reutiliza_existente_sin_importar_mayusculas(self):
        pais = Pais.objects.create(
            nombre="Colombia",
            iso2="CO",
            iso3="COL",
        )

        existente = Ciudad.objects.create(
            pais=pais,
            nombre="Bogotá",
        )

        resuelta = _resolve_city_for_create(
            pais=pais,
            ciudad_manual=" bogotá ",
        )

        self.assertEqual(
            resuelta.id,
            existente.id,
        )

        self.assertEqual(
            Ciudad.objects.filter(
                pais=pais,
            ).count(),
            1,
        )

    def test_ciudad_seleccionada_tiene_prioridad_sobre_texto_manual(self):
        pais = Pais.objects.create(
            nombre="Perú",
            iso2="PE",
            iso3="PER",
        )

        existente = Ciudad.objects.create(
            pais=pais,
            nombre="Lima",
        )

        resuelta = _resolve_city_for_create(
            pais=pais,
            ciudad=existente,
            ciudad_manual="Cusco",
        )

        self.assertEqual(
            resuelta.id,
            existente.id,
        )

        self.assertFalse(
            Ciudad.objects.filter(
                pais=pais,
                nombre="Cusco",
            ).exists()
        )