"""
Prevalidación integral de publicaciones.

El servicio no crea ni modifica registros. Resuelve los identificadores
institucionales recibidos, valida el PDF si está presente, comprueba la
integridad académica y ejecuta la detección de duplicados.
"""

from rest_framework.exceptions import ValidationError

from core.models import (
    AreaConocimiento,
    Carrera,
    Ciudad,
    Facultad,
    Pais,
    Proyecto,
    Sede,
    Subarea,
)
from core.models.publicaciones.base import MAX_PUBLICACION_PDF_BYTES
from core.publicaciones.services.publicaciones_duplicados_services import (
    analizar_duplicados_candidato,
)
from core.publicaciones.services.publicaciones_integridad_services import (
    validar_integridad_publicacion,
)
from core.publicaciones.utils.publicaciones_permissions_utils import (
    is_admin_user,
)
from core.publicaciones.utils.publicaciones_validation_response_utils import (
    construir_respuesta_validacion,
    crear_problema_validacion,
    problemas_desde_duplicados,
    problemas_desde_validation_error,
)
from core.utils.files import validate_pdf_file


def _text(value):
    return str(value or "").strip()


def _truthy(value):
    return _text(value).lower() in {
        "1",
        "true",
        "si",
        "sí",
        "yes",
    }


def _first(data, *keys):
    for key in keys:
        if hasattr(data, "get"):
            value = data.get(key)
        else:
            value = None

        if value not in (None, ""):
            return value

    return None


def _resolve_fk(
    data,
    *,
    keys,
    model,
    field,
    queryset=None,
):
    raw = _first(data, *keys)

    if raw in (None, ""):
        return None, []

    try:
        object_id = int(raw)
    except (TypeError, ValueError, OverflowError):
        return None, [
            crear_problema_validacion(
                codigo=f"integridad.{field}.id_invalido",
                campo=field,
                mensaje=(
                    f"El identificador enviado para {field} "
                    "no es válido."
                ),
                origen="integridad",
            )
        ]

    if object_id <= 0:
        return None, [
            crear_problema_validacion(
                codigo=f"integridad.{field}.id_invalido",
                campo=field,
                mensaje=(
                    f"El identificador enviado para {field} "
                    "no es válido."
                ),
                origen="integridad",
            )
        ]

    qs = queryset if queryset is not None else model.objects.all()
    obj = qs.filter(pk=object_id).first()

    if obj is None:
        return None, [
            crear_problema_validacion(
                codigo=f"integridad.{field}.no_encontrado",
                campo=field,
                mensaje=(
                    f"No existe un registro válido para {field} "
                    f"con identificador {object_id}."
                ),
                origen="integridad",
            )
        ]

    return obj, []


def prevalidar_publicacion(
    data,
    *,
    actor,
    uploaded_file=None,
):
    blocking = []
    warnings = []

    site, issues = _resolve_fk(
        data,
        keys=("sede", "sede_id"),
        model=Sede,
        field="sede",
    )
    blocking.extend(issues)

    career, issues = _resolve_fk(
        data,
        keys=("carrera", "carrera_id"),
        model=Carrera,
        field="carrera",
        queryset=Carrera.objects.select_related("facultad"),
    )
    blocking.extend(issues)

    faculty, issues = _resolve_fk(
        data,
        keys=("facultad", "facultad_id"),
        model=Facultad,
        field="facultad",
    )
    blocking.extend(issues)

    project, issues = _resolve_fk(
        data,
        keys=("proyecto", "proyecto_id"),
        model=Proyecto,
        field="proyecto",
        queryset=Proyecto.objects.select_related("sede", "carrera"),
    )
    blocking.extend(issues)

    area, issues = _resolve_fk(
        data,
        keys=("area", "area_id"),
        model=AreaConocimiento,
        field="area",
    )
    blocking.extend(issues)

    subarea, issues = _resolve_fk(
        data,
        keys=("subarea", "subarea_id"),
        model=Subarea,
        field="subarea",
        queryset=Subarea.objects.select_related("area"),
    )
    blocking.extend(issues)

    country, issues = _resolve_fk(
        data,
        keys=("pais", "pais_id"),
        model=Pais,
        field="pais",
    )
    blocking.extend(issues)

    city, issues = _resolve_fk(
        data,
        keys=("ciudad", "ciudad_id"),
        model=Ciudad,
        field="ciudad",
        queryset=Ciudad.objects.select_related("pais"),
    )
    blocking.extend(issues)

    checks = {
        "documento": {
            "ejecutada": uploaded_file not in (None, ""),
            "valida": True,
        },
        "integridad": {
            "ejecutada": True,
            "valida": True,
        },
        "duplicados": {
            "ejecutada": True,
            "valida": True,
        },
    }

    # --------------------------------------------------------
    # DOCUMENTO
    # --------------------------------------------------------
    if uploaded_file not in (None, ""):
        try:
            validate_pdf_file(
                uploaded_file,
                max_bytes=MAX_PUBLICACION_PDF_BYTES,
                field_name="archivo_pdf",
                label="El archivo PDF",
            )
        except ValidationError as exc:
            checks["documento"]["valida"] = False
            blocking.extend(
                problemas_desde_validation_error(
                    exc.detail,
                    origen="documento",
                    prefijo="documento",
                )
            )

    # --------------------------------------------------------
    # INTEGRIDAD
    # --------------------------------------------------------
    can_run_integrity = not any(
        issue.get("origen") == "integridad"
        and issue.get("codigo", "").endswith(
            ("id_invalido", "no_encontrado")
        )
        for issue in blocking
    )

    if can_run_integrity:
        try:
            validar_integridad_publicacion(
                usuario=actor,
                sede=site,
                carrera=career,
                facultad=faculty,
                proyecto=project,
                area=area,
                subarea=subarea,
                pais=country,
                ciudad=city,
                anio_publicacion=_first(
                    data,
                    "anio_publicacion",
                    "anio",
                ),
                mes_publicacion=_first(
                    data,
                    "mes_publicacion",
                    "mes",
                ),
                registrado_por_admin=(
                    is_admin_user(actor)
                    and _truthy(
                        _first(
                            data,
                            "registrado_por_admin",
                        )
                    )
                ),
                require_sede=True,
                require_carrera=True,
                require_periodo=True,
            )
        except ValidationError as exc:
            checks["integridad"]["valida"] = False
            blocking.extend(
                problemas_desde_validation_error(
                    exc.detail,
                    origen="integridad",
                    prefijo="integridad",
                )
            )
    else:
        checks["integridad"]["valida"] = False

    # --------------------------------------------------------
    # DUPLICADOS
    # --------------------------------------------------------
    duplicate_result = None

    try:
        duplicate_result = analizar_duplicados_candidato(
            data,
            uploaded_file=uploaded_file,
            exclude_publication_id=(
                _first(
                    data,
                    "excluir_publicacion_id",
                    "publicacion_id",
                )
            ),
        )

        duplicate_blocking, duplicate_warnings = (
            problemas_desde_duplicados(
                duplicate_result
            )
        )

        blocking.extend(duplicate_blocking)
        warnings.extend(duplicate_warnings)

        checks["duplicados"].update(
            {
                "valida": not bool(duplicate_blocking),
                "tiene_bloqueantes": bool(duplicate_blocking),
                "tiene_advertencias": bool(duplicate_warnings),
                "criterios": duplicate_result.get("criterios", {}),
            }
        )

    except ValidationError as exc:
        checks["duplicados"]["valida"] = False
        blocking.extend(
            problemas_desde_validation_error(
                exc.detail,
                origen="duplicados",
                prefijo="duplicados",
            )
        )

    return construir_respuesta_validacion(
        bloqueantes=blocking,
        advertencias=warnings,
        validaciones=checks,
        extras={
            "coincidencias": {
                "bloqueantes": (
                    duplicate_result.get("bloqueantes", [])
                    if duplicate_result
                    else []
                ),
                "advertencias": (
                    duplicate_result.get("advertencias", [])
                    if duplicate_result
                    else []
                ),
            },
        },
    )