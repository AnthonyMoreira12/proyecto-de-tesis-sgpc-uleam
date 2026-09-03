"""
Utilidades para respuestas homogéneas de validación.

La interfaz recibe siempre problemas con la misma estructura:

    codigo
    nivel
    campo
    mensaje
    origen
    metadata

Los errores bloqueantes impiden continuar. Las advertencias informan
una posible inconsistencia que requiere revisión humana.
"""

from rest_framework.exceptions import ErrorDetail


NIVEL_BLOQUEANTE = "bloqueante"
NIVEL_ADVERTENCIA = "advertencia"


def _text(value):
    return str(value or "").strip()


def crear_problema_validacion(
    *,
    codigo,
    mensaje,
    nivel=NIVEL_BLOQUEANTE,
    campo=None,
    origen="validacion",
    metadata=None,
):
    return {
        "codigo": _text(codigo) or "validacion.invalid",
        "nivel": (
            NIVEL_ADVERTENCIA
            if nivel == NIVEL_ADVERTENCIA
            else NIVEL_BLOQUEANTE
        ),
        "campo": _text(campo) or None,
        "mensaje": _text(mensaje),
        "origen": _text(origen) or "validacion",
        "metadata": metadata if isinstance(metadata, dict) else {},
    }


def _detail_code(value):
    if isinstance(value, ErrorDetail):
        return _text(getattr(value, "code", "")) or "invalid"

    return "invalid"


def _flatten_detail(
    value,
    *,
    origin,
    field=None,
    prefix="validacion",
):
    issues = []

    if isinstance(value, dict):
        for key, nested in value.items():
            next_field = _text(key) or field
            issues.extend(
                _flatten_detail(
                    nested,
                    origin=origin,
                    field=next_field,
                    prefix=prefix,
                )
            )
        return issues

    if isinstance(value, (list, tuple)):
        for nested in value:
            issues.extend(
                _flatten_detail(
                    nested,
                    origin=origin,
                    field=field,
                    prefix=prefix,
                )
            )
        return issues

    code = _detail_code(value)
    field_code = _text(field) or "general"

    issues.append(
        crear_problema_validacion(
            codigo=f"{prefix}.{field_code}.{code}",
            campo=field,
            mensaje=_text(value),
            nivel=NIVEL_BLOQUEANTE,
            origen=origin,
        )
    )

    return issues


def problemas_desde_validation_error(
    detail,
    *,
    origen,
    prefijo=None,
):
    """Convierte ``ValidationError.detail`` en una lista estable."""

    return _flatten_detail(
        detail,
        origin=origen,
        prefix=_text(prefijo) or _text(origen) or "validacion",
    )


def problemas_desde_duplicados(result):
    blocking = []
    warnings = []

    for match in result.get("bloqueantes", []) or []:
        criteria = list(match.get("criterios", []) or [])
        reasons = list(match.get("motivos", []) or [])
        criterion = criteria[0] if criteria else "coincidencia_fuerte"
        message = (
            reasons[0]
            if reasons
            else "Se detectó una coincidencia fuerte."
        )

        blocking.append(
            crear_problema_validacion(
                codigo=f"duplicados.{criterion}",
                campo=None,
                mensaje=message,
                nivel=NIVEL_BLOQUEANTE,
                origen="duplicados",
                metadata={"coincidencia": match},
            )
        )

    for match in result.get("advertencias", []) or []:
        criteria = list(match.get("criterios", []) or [])
        reasons = list(match.get("motivos", []) or [])
        criterion = criteria[0] if criteria else "posible_coincidencia"
        message = (
            reasons[0]
            if reasons
            else "Se detectó una posible coincidencia."
        )

        warnings.append(
            crear_problema_validacion(
                codigo=f"duplicados.{criterion}",
                campo=None,
                mensaje=message,
                nivel=NIVEL_ADVERTENCIA,
                origen="duplicados",
                metadata={"coincidencia": match},
            )
        )

    return blocking, warnings


def construir_respuesta_validacion(
    *,
    bloqueantes=None,
    advertencias=None,
    validaciones=None,
    extras=None,
):
    blocking = list(bloqueantes or [])
    warnings = list(advertencias or [])
    can_continue = not blocking

    payload = {
        "ok": True,
        "valido": can_continue,
        "puede_continuar": can_continue,
        "resumen": {
            "bloqueantes": len(blocking),
            "advertencias": len(warnings),
        },
        "bloqueantes": blocking,
        "advertencias": warnings,
        "validaciones": (
            validaciones
            if isinstance(validaciones, dict)
            else {}
        ),
    }

    if isinstance(extras, dict):
        payload.update(extras)

    return payload