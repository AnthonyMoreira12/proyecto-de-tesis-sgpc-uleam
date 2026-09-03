"""
Validaciones transversales de integridad institucional y académica.

Este servicio concentra las reglas comunes que deben cumplirse
independientemente del tipo de publicación:

    Sede -> CarreraSede activa -> Carrera -> Facultad
    Proyecto -> Sede / Carrera
    Área -> Subárea
    País -> Ciudad
    Año / Mes
    Usuario creador -> Sede, cuando no es registro administrativo

Los serializers pueden conservar validaciones tempranas para devolver
errores cerca del formulario, pero esta capa actúa como respaldo común
para creación y actualización.
"""

from rest_framework.exceptions import ValidationError


MIN_PUBLICATION_YEAR = 1900
MAX_PUBLICATION_YEAR = 2100


def _pk(value):
    if value is None:
        return None

    return getattr(
        value,
        "pk",
        getattr(
            value,
            "id",
            None,
        ),
    )


def _normalize_year(value):
    if value in (
        None,
        "",
    ):
        raise ValidationError(
            {
                "anio_publicacion": [
                    "El año de publicación es obligatorio."
                ]
            }
        )

    try:
        value = int(value)
    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise ValidationError(
            {
                "anio_publicacion": [
                    "El año de publicación debe ser numérico."
                ]
            }
        ) from exc

    if value < MIN_PUBLICATION_YEAR:
        raise ValidationError(
            {
                "anio_publicacion": [
                    "El año de publicación debe ser mayor "
                    f"o igual a {MIN_PUBLICATION_YEAR}."
                ]
            }
        )

    if value > MAX_PUBLICATION_YEAR:
        raise ValidationError(
            {
                "anio_publicacion": [
                    "El año de publicación no puede ser mayor "
                    f"a {MAX_PUBLICATION_YEAR}."
                ]
            }
        )

    return value


def _normalize_month(value):
    if value in (
        None,
        "",
    ):
        return None

    try:
        value = int(value)
    except (
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise ValidationError(
            {
                "mes_publicacion": [
                    "El mes de publicación debe ser numérico."
                ]
            }
        ) from exc

    if not 1 <= value <= 12:
        raise ValidationError(
            {
                "mes_publicacion": [
                    "El mes de publicación debe estar "
                    "entre 1 y 12."
                ]
            }
        )

    return value


def validar_integridad_publicacion(
    *,
    usuario=None,
    sede=None,
    carrera=None,
    facultad=None,
    proyecto=None,
    area=None,
    subarea=None,
    pais=None,
    ciudad=None,
    anio_publicacion=None,
    mes_publicacion=None,
    registrado_por_admin=False,
    require_sede=True,
    require_carrera=True,
    require_periodo=True,
):
    """
    Valida y normaliza la clasificación general de una publicación.

    ``require_sede=False`` se utiliza únicamente al editar registros
    históricos que aún pueden conservar ``sede = NULL``. No relaja
    ninguna relación cuando la sede sí existe.
    """

    errors = {}

    # ========================================================
    # SEDE
    # ========================================================

    if sede is None and usuario is not None:
        sede = getattr(
            usuario,
            "sede",
            None,
        )

    if (
        sede is None
        and proyecto is not None
        and getattr(
            proyecto,
            "sede_id",
            None,
        )
    ):
        sede = getattr(
            proyecto,
            "sede",
            None,
        )

    if require_sede and sede is None:
        errors["sede"] = [
            "La sede es obligatoria para registrar "
            "una nueva publicación."
        ]

    if (
        sede is not None
        and not getattr(
            sede,
            "activa",
            False,
        )
    ):
        errors["sede"] = [
            "La sede seleccionada no está activa."
        ]

    # ========================================================
    # CARRERA -> FACULTAD / SEDE
    # ========================================================

    if require_carrera and carrera is None:
        errors["carrera"] = [
            "La carrera es obligatoria."
        ]

    if (
        carrera is not None
        and facultad is not None
        and getattr(
            carrera,
            "facultad_id",
            None,
        )
        != _pk(facultad)
    ):
        errors["carrera"] = [
            "La carrera seleccionada no pertenece "
            "a la facultad indicada."
        ]

    if (
        sede is not None
        and carrera is not None
    ):
        relation_exists = (
            carrera.sedes_carrera
            .filter(
                sede_id=_pk(sede),
                activa=True,
                sede__activa=True,
            )
            .exists()
        )

        if not relation_exists:
            errors["carrera"] = [
                "La carrera seleccionada no está "
                "habilitada en la sede indicada."
            ]

    # ========================================================
    # USUARIO CREADOR -> SEDE
    # ========================================================

    user_site_id = (
        getattr(
            usuario,
            "sede_id",
            None,
        )
        if usuario is not None
        else None
    )

    if (
        user_site_id
        and sede is not None
        and not registrado_por_admin
        and user_site_id != _pk(sede)
    ):
        errors["sede"] = [
            "La sede de la publicación debe corresponder "
            "con la sede asignada al usuario institucional."
        ]

    # ========================================================
    # PROYECTO -> CARRERA / SEDE
    # ========================================================

    if (
        proyecto is not None
        and carrera is not None
        and getattr(
            proyecto,
            "carrera_id",
            None,
        )
        != _pk(carrera)
    ):
        errors["proyecto"] = [
            "El proyecto seleccionado no pertenece "
            "a la carrera indicada."
        ]

    project_site_id = (
        getattr(
            proyecto,
            "sede_id",
            None,
        )
        if proyecto is not None
        else None
    )

    # Los proyectos históricos pueden conservar sede NULL.
    if (
        proyecto is not None
        and project_site_id
        and sede is not None
        and project_site_id != _pk(sede)
    ):
        errors["proyecto"] = [
            "El proyecto seleccionado pertenece "
            "a una sede diferente de la publicación."
        ]

    if (
        proyecto is not None
        and project_site_id
        and getattr(
            proyecto,
            "carrera_id",
            None,
        )
    ):
        project_career = getattr(
            proyecto,
            "carrera",
            None,
        )

        if (
            project_career is not None
            and not project_career.sedes_carrera.filter(
                sede_id=project_site_id,
                activa=True,
                sede__activa=True,
            ).exists()
        ):
            errors["proyecto"] = [
                "La clasificación institucional del proyecto "
                "no corresponde a una relación Sede-Carrera activa."
            ]

    # ========================================================
    # ÁREA -> SUBÁREA
    # ========================================================

    if (
        subarea is not None
        and area is None
    ):
        area = getattr(
            subarea,
            "area",
            None,
        )

    if (
        area is not None
        and subarea is not None
        and getattr(
            subarea,
            "area_id",
            None,
        )
        != _pk(area)
    ):
        errors["subarea"] = [
            "La subárea seleccionada no pertenece "
            "al área indicada."
        ]

    # ========================================================
    # PAÍS -> CIUDAD
    # ========================================================

    if (
        ciudad is not None
        and pais is None
    ):
        errors["pais"] = [
            "Debe seleccionar un país cuando "
            "seleccione una ciudad."
        ]

    if (
        pais is not None
        and ciudad is not None
        and getattr(
            ciudad,
            "pais_id",
            None,
        )
        != _pk(pais)
    ):
        errors["ciudad"] = [
            "La ciudad seleccionada no pertenece "
            "al país indicado."
        ]

    # ========================================================
    # PERÍODO
    # ========================================================

    normalized_year = (
        _normalize_year(
            anio_publicacion
        )
        if require_periodo
        else anio_publicacion
    )

    normalized_month = (
        _normalize_month(
            mes_publicacion
        )
        if require_periodo
        else mes_publicacion
    )

    if errors:
        raise ValidationError(errors)

    return {
        "sede": sede,
        "carrera": carrera,
        "facultad": facultad,
        "proyecto": proyecto,
        "area": area,
        "subarea": subarea,
        "pais": pais,
        "ciudad": ciudad,
        "anio_publicacion": normalized_year,
        "mes_publicacion": normalized_month,
    }
