import pytest
from pytest_archon import archrule

def test_models_should_not_import_views_or_serializers():
    """
    Garantiza que la capa de datos/dominio (Modelos) sea independiente.
    Los modelos jamás deben importar Vistas (presentación) ni 
    Serializadores (transferencia de datos).
    """
    (
        archrule("Aislamiento de Modelos")
        .match("core.models*")
        .should_not_import("core.*.views*")
        .should_not_import("core.*.serializers*")
        .check("core")
    )

def test_serializers_should_not_import_views():
    """
    Evita dependencias circulares y mezcla de responsabilidades: 
    Los DTOs/Serializers no deben importar controladores/vistas.
    """
    (
        archrule("Aislamiento de DTOs")
        .match("core.*.serializers*")
        .should_not_import("core.*.views*")
        .check("core")
    )