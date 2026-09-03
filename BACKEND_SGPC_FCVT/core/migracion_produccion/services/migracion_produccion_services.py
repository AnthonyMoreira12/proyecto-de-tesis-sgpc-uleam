"""Diagnóstico y normalización segura para actualizar una BD histórica del SGPC.

Reglas de seguridad:
- Nunca elimina registros.
- Nunca cambia carrera, autoría, tipo, estado ni contenido científico.
- No inventa relaciones CarreraSede.
- Una sede predeterminada solo se usa si el administrador la solicita y la
  relación CarreraSede correspondiente ya existe y está activa.
- Las inferencias automáticas requieren una fuente consistente ya existente.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from django.db import transaction
from django.utils import timezone

from core.publicaciones.services.publicaciones_integridad_backfill_services import (
    diagnostico_integridad_documental,
)

from core.models import (
    Autor,
    CarreraSede,
    Proyecto,
    Publicacion,
    Sede,
    Usuario,
)


CRITICAL_COUNT_KEYS = (
    "usuarios",
    "autores",
    "publicaciones",
    "proyectos",
)


def _relation_active(*, sede_id: int | None, carrera_id: int | None) -> bool:
    if not sede_id or not carrera_id:
        return False
    return CarreraSede.objects.filter(
        sede_id=sede_id,
        carrera_id=carrera_id,
        activa=True,
        sede__activa=True,
    ).exists()


def _sample_ids(queryset, limit: int = 20) -> list[int]:
    return list(queryset.order_by("pk").values_list("pk", flat=True)[: max(1, limit)])


def snapshot_metricas_produccion() -> dict[str, Any]:
    """Snapshot pequeño y serializable para comprobar que no se pierdan datos."""
    return {
        "capturado_en": timezone.now().isoformat(),
        "usuarios": Usuario.objects.count(),
        "autores": Autor.objects.count(),
        "publicaciones": Publicacion.objects.count(),
        "proyectos": Proyecto.objects.count(),
        "sedes": Sede.objects.count(),
        "sedes_activas": Sede.objects.filter(activa=True).count(),
        "carreras_sedes": CarreraSede.objects.count(),
        "carreras_sedes_activas": CarreraSede.objects.filter(
            activa=True,
            sede__activa=True,
        ).count(),
    }


def comparar_snapshots_produccion(
    antes: dict[str, Any] | None,
    despues: dict[str, Any] | None = None,
) -> dict[str, Any]:
    antes = dict(antes or {})
    despues = dict(despues or snapshot_metricas_produccion())
    diferencias: dict[str, Any] = {}
    perdida_detectada = False

    for key in CRITICAL_COUNT_KEYS:
        try:
            before = int(antes.get(key, 0))
            after = int(despues.get(key, 0))
        except (TypeError, ValueError):
            before = 0
            after = 0
        delta = after - before
        diferencias[key] = {
            "antes": before,
            "despues": after,
            "delta": delta,
            "ok": delta >= 0,
        }
        if delta < 0:
            perdida_detectada = True

    return {
        "antes": antes,
        "despues": despues,
        "diferencias": diferencias,
        "perdida_detectada": perdida_detectada,
        "estado": "ERROR" if perdida_detectada else "OK",
    }


def diagnostico_actualizacion_produccion(*, sample_limit: int = 20) -> dict[str, Any]:
    institucionales = Usuario.objects.filter(
        rol=Usuario.Rol.AUTOR,
        auth_source=Usuario.AuthSource.MICROSOFT,
    )
    externos = Usuario.objects.filter(
        rol=Usuario.Rol.AUTOR_EXTERNO,
        auth_source=Usuario.AuthSource.LOCAL,
    )

    usuarios_sin_sede = institucionales.filter(sede_id__isnull=True)
    usuarios_sin_carrera = institucionales.filter(carrera_id__isnull=True)
    perfiles_desincronizados = []
    usuarios_relacion_invalida = []

    for user in institucionales.select_related("sede", "carrera").iterator():
        if user.sede_id and user.carrera_id and not _relation_active(
            sede_id=user.sede_id,
            carrera_id=user.carrera_id,
        ):
            usuarios_relacion_invalida.append(user.pk)
        if bool(user.perfil_completo) != bool(user.calcular_perfil_completo()):
            perfiles_desincronizados.append(user.pk)

    pubs_sin_sede = Publicacion.objects.filter(sede_id__isnull=True)
    proyectos_sin_sede = Proyecto.objects.filter(sede_id__isnull=True)

    publicaciones_relacion_invalida = []
    for pub in Publicacion.objects.exclude(sede_id__isnull=True).select_related("sede", "carrera").iterator():
        if pub.carrera_id and not _relation_active(sede_id=pub.sede_id, carrera_id=pub.carrera_id):
            publicaciones_relacion_invalida.append(pub.pk)

    proyectos_relacion_invalida = []
    for project in Proyecto.objects.exclude(sede_id__isnull=True).select_related("sede", "carrera").iterator():
        if project.carrera_id and not _relation_active(sede_id=project.sede_id, carrera_id=project.carrera_id):
            proyectos_relacion_invalida.append(project.pk)

    valid_states = {value for value, _label in Publicacion.ESTADOS}
    estados = Counter(
        Publicacion.objects.values_list("estado", flat=True)
    )
    estados_invalidos = {
        str(key): value
        for key, value in estados.items()
        if key not in valid_states
    }

    integridad = diagnostico_integridad_documental()

    blockers = []
    warnings = []
    active_sedes = Sede.objects.filter(activa=True).count()
    active_relations = CarreraSede.objects.filter(activa=True, sede__activa=True).count()

    if active_sedes == 0:
        blockers.append("No existe ninguna sede activa. Debe cargar la estructura académica antes de abrir la versión nueva.")
    if active_relations == 0:
        blockers.append("No existe ninguna relación Carrera–Sede activa. La versión nueva rechazará combinaciones académicas hasta configurarlas.")
    if usuarios_relacion_invalida:
        blockers.append("Existen usuarios institucionales con una combinación Sede–Carrera no habilitada.")
    if publicaciones_relacion_invalida:
        warnings.append("Existen publicaciones con Sede–Carrera inconsistente; no serán modificadas automáticamente.")
    if proyectos_relacion_invalida:
        warnings.append("Existen proyectos con Sede–Carrera inconsistente; no serán modificados automáticamente.")
    if estados_invalidos:
        blockers.append("Existen estados de publicación fuera del catálogo final. Revise esos registros antes del despliegue.")
    if usuarios_sin_sede.exists():
        warnings.append("Hay usuarios institucionales sin sede. Pueden normalizarse con evidencia existente o mediante campaña de actualización.")
    if pubs_sin_sede.exists():
        warnings.append("Hay publicaciones históricas sin sede; los filtros/reportes por sede pueden omitirlas hasta completar el dato.")
    if proyectos_sin_sede.exists():
        warnings.append("Hay proyectos históricos sin sede; conviene completarla para reportes y consistencia institucional.")
    if integridad.get("publicaciones_metadata_incompleta", 0) or integridad.get("adjuntos_metadata_incompleta", 0):
        warnings.append("Hay PDF históricos con metadatos técnicos incompletos. Ejecute Integridad documental antes o después de normalizar sede/carrera.")

    return {
        "generado_en": timezone.now().isoformat(),
        "snapshot": snapshot_metricas_produccion(),
        "catalogos": {
            "sedes_activas": active_sedes,
            "carreras_sedes_activas": active_relations,
        },
        "integridad_documental": integridad,
        "usuarios": {
            "institucionales": institucionales.count(),
            "externos": externos.count(),
            "sin_sede": usuarios_sin_sede.count(),
            "sin_carrera": usuarios_sin_carrera.count(),
            "relacion_sede_carrera_invalida": len(usuarios_relacion_invalida),
            "perfil_completo_desincronizado": len(perfiles_desincronizados),
            "muestras": {
                "sin_sede": _sample_ids(usuarios_sin_sede, sample_limit),
                "sin_carrera": _sample_ids(usuarios_sin_carrera, sample_limit),
                "relacion_invalida": usuarios_relacion_invalida[:sample_limit],
                "perfil_desincronizado": perfiles_desincronizados[:sample_limit],
            },
        },
        "publicaciones": {
            "total": Publicacion.objects.count(),
            "sin_sede": pubs_sin_sede.count(),
            "relacion_sede_carrera_invalida": len(publicaciones_relacion_invalida),
            "estados": dict(estados),
            "estados_invalidos": estados_invalidos,
            "muestras": {
                "sin_sede": _sample_ids(pubs_sin_sede, sample_limit),
                "relacion_invalida": publicaciones_relacion_invalida[:sample_limit],
            },
        },
        "proyectos": {
            "total": Proyecto.objects.count(),
            "sin_sede": proyectos_sin_sede.count(),
            "relacion_sede_carrera_invalida": len(proyectos_relacion_invalida),
            "muestras": {
                "sin_sede": _sample_ids(proyectos_sin_sede, sample_limit),
                "relacion_invalida": proyectos_relacion_invalida[:sample_limit],
            },
        },
        "bloqueos": blockers,
        "advertencias": warnings,
        "listo_para_abrir": not blockers,
    }


def _infer_project_sede(project: Proyecto, default_sede_id: int | None, use_default: bool):
    linked = list(
        project.publicaciones.exclude(sede_id__isnull=True)
        .values_list("sede_id", flat=True)
        .distinct()[:2]
    )
    if len(linked) == 1 and _relation_active(sede_id=linked[0], carrera_id=project.carrera_id):
        return linked[0], "publicaciones_vinculadas"
    if use_default and default_sede_id and _relation_active(
        sede_id=default_sede_id,
        carrera_id=project.carrera_id,
    ):
        return default_sede_id, "sede_predeterminada"
    return None, None


def _infer_publication_sede(pub: Publicacion, default_sede_id: int | None, use_default: bool):
    creator = getattr(pub, "usuario_creador", None)
    if creator and creator.sede_id and _relation_active(
        sede_id=creator.sede_id,
        carrera_id=pub.carrera_id,
    ):
        return creator.sede_id, "usuario_creador"

    project = getattr(pub, "proyecto", None)
    if project and project.sede_id and _relation_active(
        sede_id=project.sede_id,
        carrera_id=pub.carrera_id,
    ):
        return project.sede_id, "proyecto"

    if use_default and default_sede_id and _relation_active(
        sede_id=default_sede_id,
        carrera_id=pub.carrera_id,
    ):
        return default_sede_id, "sede_predeterminada"
    return None, None


def normalizar_actualizacion_produccion(
    *,
    dry_run: bool = True,
    default_sede_id: int | None = None,
    usar_sede_predeterminada: bool = False,
    recalcular_perfiles: bool = True,
) -> dict[str, Any]:
    """Normaliza únicamente datos que puedan determinarse de forma segura."""
    default_sede = None
    if default_sede_id:
        default_sede = Sede.objects.filter(pk=default_sede_id, activa=True).first()
        if default_sede is None:
            raise ValueError("La sede predeterminada no existe o está inactiva.")
        default_sede_id = default_sede.pk

    before = snapshot_metricas_produccion()
    changes = {
        "usuarios_sede": [],
        "proyectos_sede": [],
        "publicaciones_sede": [],
        "perfiles_recalculados": [],
    }
    pending = {
        "usuarios_sin_sede": [],
        "proyectos_sin_sede": [],
        "publicaciones_sin_sede": [],
        "relaciones_invalidas": [],
    }

    def execute():
        # 1) Usuarios institucionales: solo sede predeterminada explícita.
        institutional = Usuario.objects.filter(
            rol=Usuario.Rol.AUTOR,
            auth_source=Usuario.AuthSource.MICROSOFT,
        ).select_related("sede", "carrera")

        for user in institutional.iterator():
            assigned_sede = user.sede_id
            if user.sede_id and user.carrera_id and not _relation_active(
                sede_id=user.sede_id,
                carrera_id=user.carrera_id,
            ):
                pending["relaciones_invalidas"].append({"tipo": "usuario", "id": user.pk})
            elif not user.sede_id:
                if (
                    usar_sede_predeterminada
                    and default_sede_id
                    and user.carrera_id
                    and _relation_active(sede_id=default_sede_id, carrera_id=user.carrera_id)
                ):
                    assigned_sede = default_sede_id
                    changes["usuarios_sede"].append(
                        {"id": user.pk, "anterior": None, "nuevo": default_sede_id, "fuente": "sede_predeterminada"}
                    )
                    if not dry_run:
                        Usuario.objects.filter(pk=user.pk, sede_id__isnull=True).update(sede_id=default_sede_id)
                else:
                    pending["usuarios_sin_sede"].append(user.pk)

            if recalcular_perfiles:
                # Se calcula sobre el valor que quedaría después de la normalización.
                original_sede = user.sede_id
                user.sede_id = assigned_sede
                desired = bool(user.calcular_perfil_completo())
                user.sede_id = original_sede
                if bool(user.perfil_completo) != desired:
                    changes["perfiles_recalculados"].append(
                        {"id": user.pk, "anterior": bool(user.perfil_completo), "nuevo": desired}
                    )
                    if not dry_run:
                        Usuario.objects.filter(pk=user.pk).update(perfil_completo=desired)

        # Externos completos según la regla final.
        if recalcular_perfiles:
            for user in Usuario.objects.filter(
                rol=Usuario.Rol.AUTOR_EXTERNO,
                auth_source=Usuario.AuthSource.LOCAL,
            ).iterator():
                desired = bool(user.calcular_perfil_completo())
                if bool(user.perfil_completo) != desired:
                    changes["perfiles_recalculados"].append(
                        {"id": user.pk, "anterior": bool(user.perfil_completo), "nuevo": desired}
                    )
                    if not dry_run:
                        Usuario.objects.filter(pk=user.pk).update(perfil_completo=desired)

        # 2) Proyectos: inferir por publicaciones ya clasificadas; default solo explícito.
        for project in Proyecto.objects.filter(sede_id__isnull=True).select_related("carrera").iterator():
            sede_id, source = _infer_project_sede(project, default_sede_id, usar_sede_predeterminada)
            if sede_id:
                changes["proyectos_sede"].append(
                    {"id": project.pk, "anterior": None, "nuevo": sede_id, "fuente": source}
                )
                if not dry_run:
                    Proyecto.objects.filter(pk=project.pk, sede_id__isnull=True).update(sede_id=sede_id)
            else:
                pending["proyectos_sin_sede"].append(project.pk)

        # 3) Publicaciones: usuario creador > proyecto > default explícito.
        publications = Publicacion.objects.filter(sede_id__isnull=True).select_related(
            "usuario_creador", "proyecto", "carrera"
        )
        for pub in publications.iterator():
            # Si el proyecto fue actualizado en esta misma ejecución, recuperamos su sede.
            if not dry_run and pub.proyecto_id:
                pub.proyecto = Proyecto.objects.filter(pk=pub.proyecto_id).first()
            sede_id, source = _infer_publication_sede(pub, default_sede_id, usar_sede_predeterminada)
            if sede_id:
                changes["publicaciones_sede"].append(
                    {"id": pub.pk, "anterior": None, "nuevo": sede_id, "fuente": source}
                )
                if not dry_run:
                    Publicacion.objects.filter(pk=pub.pk, sede_id__isnull=True).update(sede_id=sede_id)
            else:
                pending["publicaciones_sin_sede"].append(pub.pk)

    if dry_run:
        execute()
    else:
        with transaction.atomic():
            execute()

    after = snapshot_metricas_produccion()
    return {
        "dry_run": dry_run,
        "sede_predeterminada": (
            {"id": default_sede.pk, "nombre": default_sede.nombre}
            if default_sede else None
        ),
        "usar_sede_predeterminada": bool(usar_sede_predeterminada),
        "resumen": {key: len(value) for key, value in changes.items()},
        "cambios": changes,
        "pendientes": pending,
        "snapshot_antes": before,
        "snapshot_despues": after,
        "comparacion": comparar_snapshots_produccion(before, after),
        "diagnostico_despues": diagnostico_actualizacion_produccion(),
    }
