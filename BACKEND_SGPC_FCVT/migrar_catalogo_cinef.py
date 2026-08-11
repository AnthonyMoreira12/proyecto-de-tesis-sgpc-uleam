from django.db import transaction
from django.db.models import Q

from core.models import (
    AreaConocimiento,
    Publicacion,
    Subarea,
)


# ============================================================
# CATÁLOGO CINE-F 2013
# ÁREAS AMPLIAS
# ============================================================

AREAS_CINEF = [
    (
        "00",
        "Programas y certificaciones genéricos",
    ),
    (
        "01",
        "Educación",
    ),
    (
        "02",
        "Artes y humanidades",
    ),
    (
        "03",
        "Ciencias sociales, periodismo e información",
    ),
    (
        "04",
        "Administración de empresas y derecho",
    ),
    (
        "05",
        "Ciencias naturales, matemáticas y estadística",
    ),
    (
        "06",
        "Tecnologías de la información y la comunicación (TIC)",
    ),
    (
        "07",
        "Ingeniería, industria y construcción",
    ),
    (
        "08",
        "Agricultura, silvicultura, pesca y veterinaria",
    ),
    (
        "09",
        "Salud y bienestar",
    ),
    (
        "10",
        "Servicios",
    ),
]


# ============================================================
# CATÁLOGO CINE-F 2013
# SUBÁREAS
# ============================================================

SUBAREAS_CINEF = [
    # --------------------------------------------------------
    # 00 - Programas y certificaciones genéricos
    # --------------------------------------------------------
    (
        "001",
        "Programas y certificaciones básicos",
        "00",
    ),
    (
        "002",
        "Alfabetización y aritmética",
        "00",
    ),
    (
        "003",
        "Competencias personales y desarrollo",
        "00",
    ),

    # --------------------------------------------------------
    # 01 - Educación
    # --------------------------------------------------------
    (
        "011",
        "Educación",
        "01",
    ),

    # --------------------------------------------------------
    # 02 - Artes y humanidades
    # --------------------------------------------------------
    (
        "021",
        "Artes",
        "02",
    ),
    (
        "022",
        "Humanidades (excepto idiomas)",
        "02",
    ),
    (
        "023",
        "Idiomas",
        "02",
    ),

    # --------------------------------------------------------
    # 03 - Ciencias sociales, periodismo e información
    # --------------------------------------------------------
    (
        "031",
        "Ciencias sociales y del comportamiento",
        "03",
    ),
    (
        "032",
        "Periodismo e información",
        "03",
    ),

    # --------------------------------------------------------
    # 04 - Administración de empresas y derecho
    # --------------------------------------------------------
    (
        "041",
        "Educación comercial y administración",
        "04",
    ),
    (
        "042",
        "Derecho",
        "04",
    ),

    # --------------------------------------------------------
    # 05 - Ciencias naturales, matemáticas y estadística
    # --------------------------------------------------------
    (
        "051",
        "Ciencias biológicas y afines",
        "05",
    ),
    (
        "052",
        "Medio ambiente",
        "05",
    ),
    (
        "053",
        "Ciencias físicas",
        "05",
    ),
    (
        "054",
        "Matemáticas y estadística",
        "05",
    ),

    # --------------------------------------------------------
    # 06 - TIC
    # --------------------------------------------------------
    (
        "061",
        "Tecnologías de la información y la comunicación (TIC)",
        "06",
    ),

    # --------------------------------------------------------
    # 07 - Ingeniería, industria y construcción
    # --------------------------------------------------------
    (
        "071",
        "Ingeniería y profesiones afines",
        "07",
    ),
    (
        "072",
        "Industria y producción",
        "07",
    ),
    (
        "073",
        "Arquitectura y construcción",
        "07",
    ),

    # --------------------------------------------------------
    # 08 - Agricultura, silvicultura, pesca y veterinaria
    # --------------------------------------------------------
    (
        "081",
        "Agricultura",
        "08",
    ),
    (
        "082",
        "Silvicultura",
        "08",
    ),
    (
        "083",
        "Pesca",
        "08",
    ),
    (
        "084",
        "Veterinaria",
        "08",
    ),

    # --------------------------------------------------------
    # 09 - Salud y bienestar
    # --------------------------------------------------------
    (
        "091",
        "Salud",
        "09",
    ),
    (
        "092",
        "Bienestar",
        "09",
    ),

    # --------------------------------------------------------
    # 10 - Servicios
    # --------------------------------------------------------
    (
        "101",
        "Servicios personales",
        "10",
    ),
    (
        "102",
        "Servicios de higiene y salud ocupacional",
        "10",
    ),
    (
        "103",
        "Servicios de seguridad",
        "10",
    ),
    (
        "104",
        "Servicios de transporte",
        "10",
    ),
]


# ============================================================
# IDENTIFICADORES DEL CATÁLOGO ANTERIOR
# ============================================================

AREA_MEDICA_ANTIGUA_ID = 3

SUBAREAS_MEDICAS_ANTIGUAS = {
    19,  # Medicina básica
    21,  # Ciencias de la salud
}


# ============================================================
# MIGRACIÓN
# ============================================================

print()
print(
    "============================================================"
)
print(
    " MIGRACIÓN DEL CATÁLOGO DE CONOCIMIENTO A CINE-F 2013"
)
print(
    "============================================================"
)
print()


with transaction.atomic():

    # ========================================================
    # 1. IDENTIFICAR CATÁLOGO ANTIGUO
    # ========================================================

    old_area_ids = list(
        AreaConocimiento.objects
        .filter(
            codigo__isnull=True
        )
        .values_list(
            "id",
            flat=True,
        )
    )

    old_subarea_ids = list(
        Subarea.objects
        .filter(
            codigo__isnull=True
        )
        .values_list(
            "id",
            flat=True,
        )
    )

    print(
        f"Áreas antiguas encontradas: "
        f"{len(old_area_ids)}"
    )

    print(
        f"Subáreas antiguas encontradas: "
        f"{len(old_subarea_ids)}"
    )

    # ========================================================
    # 2. VALIDAR PUBLICACIONES ANTIGUAS
    # ========================================================

    publicaciones_area_medica = (
        Publicacion.objects
        .filter(
            area_id=AREA_MEDICA_ANTIGUA_ID
        )
    )

    cantidad_medicas = (
        publicaciones_area_medica.count()
    )

    print(
        f"Publicaciones en área médica antigua: "
        f"{cantidad_medicas}"
    )

    publicaciones_no_mapeables = (
        publicaciones_area_medica
        .exclude(
            subarea_id__in=(
                SUBAREAS_MEDICAS_ANTIGUAS
            )
        )
    )

    if publicaciones_no_mapeables.exists():
        ids = list(
            publicaciones_no_mapeables
            .values_list(
                "id",
                flat=True,
            )
        )

        raise RuntimeError(
            "Se encontraron publicaciones del área "
            "médica que no pueden reasignarse "
            "automáticamente. IDs: "
            f"{ids}"
        )

    # ========================================================
    # 3. CREAR ÁREAS CINE-F
    # ========================================================

    areas_por_codigo = {}

    print()
    print("Creando áreas CINE-F...")

    for codigo, nombre in AREAS_CINEF:

        area, creada = (
            AreaConocimiento.objects
            .update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                },
            )
        )

        areas_por_codigo[
            codigo
        ] = area

        estado = (
            "CREADA"
            if creada
            else "ACTUALIZADA"
        )

        print(
            f"  {codigo} | {nombre} | {estado}"
        )

    # ========================================================
    # 4. CREAR SUBÁREAS CINE-F
    # ========================================================

    subareas_por_codigo = {}

    print()
    print("Creando subáreas CINE-F...")

    for (
        codigo,
        nombre,
        area_codigo,
    ) in SUBAREAS_CINEF:

        area = areas_por_codigo[
            area_codigo
        ]

        subarea, creada = (
            Subarea.objects
            .update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "area": area,
                },
            )
        )

        subareas_por_codigo[
            codigo
        ] = subarea

        estado = (
            "CREADA"
            if creada
            else "ACTUALIZADA"
        )

        print(
            f"  {codigo} | {nombre} | {estado}"
        )

    # ========================================================
    # 5. OBTENER DESTINO DE LAS PUBLICACIONES MÉDICAS
    # ========================================================

    nueva_area_salud = (
        areas_por_codigo[
            "09"
        ]
    )

    nueva_subarea_salud = (
        subareas_por_codigo[
            "091"
        ]
    )

    # ========================================================
    # 6. REASIGNAR LAS PUBLICACIONES EXISTENTES
    # ========================================================

    print()
    print(
        "Reasignando publicaciones existentes..."
    )

    actualizadas = (
        publicaciones_area_medica
        .update(
            area=nueva_area_salud,
            subarea=nueva_subarea_salud,
        )
    )

    print(
        f"Publicaciones reasignadas a "
        f"09 / 091: {actualizadas}"
    )

    # ========================================================
    # 7. VERIFICAR QUE NO EXISTAN REFERENCIAS AL CATÁLOGO
    #    ANTIGUO
    # ========================================================

    publicaciones_antiguas_restantes = (
        Publicacion.objects
        .filter(
            Q(
                area_id__in=old_area_ids
            )
            | Q(
                subarea_id__in=old_subarea_ids
            )
        )
        .count()
    )

    if publicaciones_antiguas_restantes:
        raise RuntimeError(
            "Todavía existen publicaciones asociadas "
            "al catálogo anterior. "
            "La operación fue cancelada."
        )

    # ========================================================
    # 8. ELIMINAR SUBÁREAS ANTIGUAS
    # ========================================================

    print()
    print(
        "Eliminando subáreas del catálogo anterior..."
    )

    subareas_eliminadas = (
        Subarea.objects
        .filter(
            id__in=old_subarea_ids
        )
        .delete()
    )

    print(
        f"Resultado eliminación de subáreas: "
        f"{subareas_eliminadas}"
    )

    # ========================================================
    # 9. ELIMINAR ÁREAS ANTIGUAS
    # ========================================================

    print(
        "Eliminando áreas del catálogo anterior..."
    )

    areas_eliminadas = (
        AreaConocimiento.objects
        .filter(
            id__in=old_area_ids
        )
        .delete()
    )

    print(
        f"Resultado eliminación de áreas: "
        f"{areas_eliminadas}"
    )

    # ========================================================
    # 10. VALIDACIÓN FINAL
    # ========================================================

    total_areas = (
        AreaConocimiento.objects.count()
    )

    total_subareas = (
        Subarea.objects.count()
    )

    areas_sin_codigo = (
        AreaConocimiento.objects
        .filter(
            codigo__isnull=True
        )
        .count()
    )

    subareas_sin_codigo = (
        Subarea.objects
        .filter(
            codigo__isnull=True
        )
        .count()
    )

    if total_areas != 11:
        raise RuntimeError(
            "El catálogo final debe contener "
            f"11 áreas. Se encontraron {total_areas}."
        )

    if total_subareas != 29:
        raise RuntimeError(
            "El catálogo final debe contener "
            f"29 subáreas. Se encontraron "
            f"{total_subareas}."
        )

    if areas_sin_codigo:
        raise RuntimeError(
            "Existen áreas sin código después "
            "de la migración."
        )

    if subareas_sin_codigo:
        raise RuntimeError(
            "Existen subáreas sin código después "
            "de la migración."
        )

    print()
    print(
        "============================================================"
    )
    print(
        " MIGRACIÓN COMPLETADA CORRECTAMENTE"
    )
    print(
        "============================================================"
    )

    print(
        f"Áreas finales: {total_areas}"
    )

    print(
        f"Subáreas finales: {total_subareas}"
    )

    print(
        f"Publicaciones migradas: "
        f"{actualizadas}"
    )

    print()