"""
Ajuste final de la matriz académica SGPC-ULEAM.

Cambios acordados:
1. Restaurar la denominación:
   "Facultad de Educación Turismo y Humanidades"
   -> "Facultad de Educación y Turismo"

2. Campus Flavio Alfaro:
   - activar Software
   - activar Educación Inicial
   - conservar Educación Básica

3. Campus Jama:
   - desactivar Gastronomía como CarreraSede de Facultad
     (se conserva el registro Carrera y la relación histórica).

Por seguridad:
- El modo por defecto es VISTA PREVIA.
- Para aplicar:
    SGPC_APLICAR_AJUSTE_MATRIZ=1
- Los cambios se ejecutan dentro de transaction.atomic().
- Es idempotente: puede volver a ejecutarse sin duplicar relaciones.
"""

import os

from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Carrera, CarreraSede, Facultad, Sede


APLICAR = os.getenv(
    "SGPC_APLICAR_AJUSTE_MATRIZ",
    "",
).strip() == "1"

NOMBRE_EDUCACION_ACTUAL = (
    "Facultad de Educación Turismo y Humanidades"
)
NOMBRE_EDUCACION_CORRECTO = (
    "Facultad de Educación y Turismo"
)

NOMBRE_FCVT = (
    "Facultad de Ciencias de la Vida y Tecnologías"
)

SEDE_FLAVIO = "fla"
SEDE_JAMA = "jam"


def titulo(texto):
    print()
    print("=" * 88)
    print(texto)
    print("=" * 88)


def obtener_unico(modelo, **filtros):
    qs = modelo.objects.filter(**filtros)

    cantidad = qs.count()

    if cantidad != 1:
        raise RuntimeError(
            f"Se esperaba exactamente 1 {modelo.__name__} "
            f"para {filtros}, pero se encontraron {cantidad}."
        )

    return qs.first()


def resolver_facultad_educacion():
    antigua = Facultad.objects.filter(
        nombre=NOMBRE_EDUCACION_ACTUAL
    ).first()

    correcta = Facultad.objects.filter(
        nombre=NOMBRE_EDUCACION_CORRECTO
    ).first()

    if antigua and correcta and antigua.pk != correcta.pk:
        raise RuntimeError(
            "Existen simultáneamente las dos denominaciones de "
            "la Facultad de Educación en registros distintos. "
            "No se aplicarán cambios automáticamente."
        )

    facultad = correcta or antigua

    if facultad is None:
        raise RuntimeError(
            "No se encontró la Facultad de Educación esperada."
        )

    return facultad


def obtener_carrera(nombre, facultad):
    return obtener_unico(
        Carrera,
        nombre=nombre,
        facultad=facultad,
    )


def estado_relacion(sede, carrera):
    relacion = CarreraSede.objects.filter(
        sede=sede,
        carrera=carrera,
    ).first()

    if relacion is None:
        return "NO EXISTE"

    return (
        "ACTIVA"
        if relacion.activa
        else "INACTIVA"
    )


def imprimir_relaciones_sede(sede):
    relaciones = (
        CarreraSede.objects
        .filter(
            sede=sede,
            activa=True,
        )
        .select_related(
            "carrera",
            "carrera__facultad",
        )
        .order_by(
            "carrera__facultad__nombre",
            "carrera__nombre",
        )
    )

    print(
        f"{sede.codigo} | {sede.nombre} | "
        f"{relaciones.count()} carrera(s) activa(s)"
    )

    for relacion in relaciones:
        print(
            "  - "
            f"{relacion.carrera.facultad.nombre} | "
            f"{relacion.carrera.nombre}"
        )


def preparar_contexto():
    facultad_educacion = resolver_facultad_educacion()

    facultad_fcvt = obtener_unico(
        Facultad,
        nombre=NOMBRE_FCVT,
    )

    flavio = obtener_unico(
        Sede,
        codigo=SEDE_FLAVIO,
    )

    jama = obtener_unico(
        Sede,
        codigo=SEDE_JAMA,
    )

    educacion_basica = obtener_carrera(
        "Educación Básica",
        facultad_educacion,
    )

    educacion_inicial = obtener_carrera(
        "Educación Inicial",
        facultad_educacion,
    )

    software = obtener_carrera(
        "Software",
        facultad_fcvt,
    )

    gastronomia = obtener_carrera(
        "Gastronomía",
        facultad_educacion,
    )

    return {
        "facultad_educacion": facultad_educacion,
        "facultad_fcvt": facultad_fcvt,
        "flavio": flavio,
        "jama": jama,
        "educacion_basica": educacion_basica,
        "educacion_inicial": educacion_inicial,
        "software": software,
        "gastronomia": gastronomia,
    }


def vista_previa(ctx):
    titulo("SGPC-ULEAM | AJUSTE FINAL MATRIZ ACADÉMICA")

    print(
        "MODO:",
        "APLICAR CAMBIOS"
        if APLICAR
        else "VISTA PREVIA / SIN ESCRITURA",
    )

    print()
    print("ESTADO ACTUAL")
    print(
        "- Facultades:",
        Facultad.objects.count(),
    )
    print(
        "- Carreras:",
        Carrera.objects.count(),
    )
    print(
        "- Sedes:",
        Sede.objects.count(),
    )
    print(
        "- CarreraSede total:",
        CarreraSede.objects.count(),
    )
    print(
        "- CarreraSede activas:",
        CarreraSede.objects.filter(
            activa=True
        ).count(),
    )

    print()
    print("CAMBIOS ACORDADOS")

    facultad = ctx["facultad_educacion"]

    if facultad.nombre == NOMBRE_EDUCACION_ACTUAL:
        print(
            "1. RENOMBRAR FACULTAD:"
        )
        print(
            f"   {NOMBRE_EDUCACION_ACTUAL}"
        )
        print(
            f"   -> {NOMBRE_EDUCACION_CORRECTO}"
        )
    else:
        print(
            "1. Facultad de Educación ya tiene "
            "la denominación acordada."
        )

    print()
    print(
        "2. FLAVIO ALFARO | Educación Básica:",
        estado_relacion(
            ctx["flavio"],
            ctx["educacion_basica"],
        ),
    )
    print(
        "   FLAVIO ALFARO | Educación Inicial:",
        estado_relacion(
            ctx["flavio"],
            ctx["educacion_inicial"],
        ),
        "-> DEBE QUEDAR ACTIVA",
    )
    print(
        "   FLAVIO ALFARO | Software:",
        estado_relacion(
            ctx["flavio"],
            ctx["software"],
        ),
        "-> DEBE QUEDAR ACTIVA",
    )

    print()
    print(
        "3. JAMA | Gastronomía:",
        estado_relacion(
            ctx["jama"],
            ctx["gastronomia"],
        ),
        "-> DEBE QUEDAR INACTIVA",
    )


def aplicar_ajuste(ctx):
    with transaction.atomic():
        facultad = ctx["facultad_educacion"]

        if facultad.nombre != NOMBRE_EDUCACION_CORRECTO:
            facultad.nombre = NOMBRE_EDUCACION_CORRECTO
            facultad.save(
                update_fields=["nombre"]
            )

        CarreraSede.objects.update_or_create(
            sede=ctx["flavio"],
            carrera=ctx["educacion_inicial"],
            defaults={
                "activa": True,
            },
        )

        CarreraSede.objects.update_or_create(
            sede=ctx["flavio"],
            carrera=ctx["software"],
            defaults={
                "activa": True,
            },
        )

        relacion_jama_gastronomia = (
            CarreraSede.objects.filter(
                sede=ctx["jama"],
                carrera=ctx["gastronomia"],
            ).first()
        )

        if (
            relacion_jama_gastronomia
            and relacion_jama_gastronomia.activa
        ):
            relacion_jama_gastronomia.activa = False
            relacion_jama_gastronomia.save(
                update_fields=["activa"]
            )

        # ----------------------------------------------------
        # VALIDACIONES POSTERIORES DENTRO DE LA TRANSACCIÓN
        # ----------------------------------------------------

        if Facultad.objects.filter(
            nombre=NOMBRE_EDUCACION_ACTUAL
        ).exists():
            raise ValidationError(
                "La denominación anterior de la Facultad "
                "de Educación todavía existe."
            )

        facultad_final = obtener_unico(
            Facultad,
            nombre=NOMBRE_EDUCACION_CORRECTO,
        )

        educacion_basica_final = obtener_carrera(
            "Educación Básica",
            facultad_final,
        )

        educacion_inicial_final = obtener_carrera(
            "Educación Inicial",
            facultad_final,
        )

        software_final = obtener_carrera(
            "Software",
            ctx["facultad_fcvt"],
        )

        gastronomia_final = obtener_carrera(
            "Gastronomía",
            facultad_final,
        )

        esperadas_flavio = {
            educacion_basica_final.id,
            educacion_inicial_final.id,
            software_final.id,
        }

        activas_flavio = set(
            CarreraSede.objects.filter(
                sede=ctx["flavio"],
                activa=True,
            ).values_list(
                "carrera_id",
                flat=True,
            )
        )

        if activas_flavio != esperadas_flavio:
            raise ValidationError(
                "Flavio Alfaro no quedó exactamente con "
                "Educación Básica, Educación Inicial y Software."
            )

        if CarreraSede.objects.filter(
            sede=ctx["jama"],
            carrera=gastronomia_final,
            activa=True,
        ).exists():
            raise ValidationError(
                "Jama todavía conserva Gastronomía como "
                "CarreraSede activa."
            )

        activas_globales = (
            CarreraSede.objects.filter(
                activa=True
            ).count()
        )

        if activas_globales != 138:
            raise ValidationError(
                "El total esperado es 138 relaciones "
                f"CarreraSede activas, pero quedaron "
                f"{activas_globales}."
            )


def resumen_final():
    titulo("ESTADO FINAL")

    print(
        "- Facultades:",
        Facultad.objects.count(),
    )
    print(
        "- Carreras:",
        Carrera.objects.count(),
    )
    print(
        "- Sedes:",
        Sede.objects.count(),
    )
    print(
        "- CarreraSede total:",
        CarreraSede.objects.count(),
    )
    print(
        "- CarreraSede activas:",
        CarreraSede.objects.filter(
            activa=True
        ).count(),
    )

    print()
    print(
        "FACULTAD DE EDUCACIÓN:",
        Facultad.objects.get(
            nombre=NOMBRE_EDUCACION_CORRECTO
        ).nombre,
    )

    print()
    print("FLAVIO ALFARO")
    imprimir_relaciones_sede(
        Sede.objects.get(
            codigo=SEDE_FLAVIO
        )
    )

    print()
    print("JAMA")
    imprimir_relaciones_sede(
        Sede.objects.get(
            codigo=SEDE_JAMA
        )
    )


ctx = preparar_contexto()
vista_previa(ctx)

if not APLICAR:
    print()
    print(
        "VISTA PREVIA COMPLETADA. "
        "LA BASE DE DATOS NO FUE MODIFICADA."
    )
    print(
        "Para aplicar, establezca "
        "SGPC_APLICAR_AJUSTE_MATRIZ=1."
    )
else:
    aplicar_ajuste(ctx)
    resumen_final()

    print()
    print(
        "AJUSTE FINAL APLICADO CORRECTAMENTE."
    )
