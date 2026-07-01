import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import Carrera, TipoPublicacion, Publicacion

User = get_user_model()

@pytest.fixture
def api_client():
    """Fixture para inicializar el cliente de pruebas de la API."""
    return APIClient()

@pytest.fixture
def usuario_autor_autenticado(api_client):
    """Fixture para crear y autenticar un usuario con rol de autor."""
    user = User.objects.create_user(
        email="anthony.test@live.uleam.edu.ec",
        nombres="Anthony Test",
        apellidos="Moreira Test",
        rol="autor",
        password="password_seguro_123"
    )
    api_client.force_authenticate(user=user)
    return user

@pytest.mark.django_db
def test_listar_publicaciones_autenticado(api_client, usuario_autor_autenticado):
    """Prueba que un usuario autenticado pueda consultar el listado de producción científica."""
    # Cambia '/api/publicaciones/' por la ruta real de tu router de URLs
    response = api_client.get('/api/publicaciones/')
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list) or "results" in response.data

@pytest.mark.django_db
def test_crear_publicacion_anonimo_retorna_401(api_client):
    """Garantiza la seguridad del backend: un usuario no autenticado no puede registrar datos."""
    datos_invalidos = {
        "nombre_articulo": "Ataque de inyección de datos anonimos",
        "codigo_issn": "1234-5678"
    }
    response = api_client.post('/api/publicaciones/', data=datos_invalidos, format='json')
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED