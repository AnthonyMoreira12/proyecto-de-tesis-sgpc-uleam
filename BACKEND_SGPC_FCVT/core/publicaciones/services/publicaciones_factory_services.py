from rest_framework.exceptions import ValidationError

from core.models import Publicacion, TipoPublicacion


def obtener_o_crear_tipo_publicacion(*, codigo: str, nombre: str, categoria: str, orden: int):
    tipo, created = TipoPublicacion.objects.get_or_create(
        codigo=codigo,
        defaults={
            "nombre": nombre,
            "categoria": categoria,
            "orden": orden,
        },
    )

    if not created:
        changed = False

        if (tipo.nombre or "") != nombre:
            tipo.nombre = nombre
            changed = True

        if (tipo.categoria or "") != categoria:
            tipo.categoria = categoria
            changed = True

        if tipo.orden != orden:
            tipo.orden = orden
            changed = True

        if changed:
            tipo.save(update_fields=["nombre", "categoria", "orden"])

    return tipo


def crear_publicacion_base(
    *,
    proyecto,
    tipo,
    usuario,
    facultad,
    carrera,
    area=None,
    subarea=None,
    pais=None,
    ciudad=None,
    origen_tipo="ninguno",
    origen_grado=None,
    fecha_publicacion=None,
    archivo_pdf=None,
    registrado_por_admin=False,
    admin_registrador=None,
):
    if ciudad is not None and pais is None:
        raise ValidationError({"pais": ["Debe seleccionar país si selecciona ciudad."]})

    if pais is not None and ciudad is not None:
        if getattr(ciudad, "pais_id", None) != getattr(pais, "id", None):
            raise ValidationError(
                {"ciudad": ["La ciudad seleccionada no pertenece al país indicado."]}
            )

    ot = str(origen_tipo or "ninguno").strip().lower()

    og = origen_grado
    if og is not None:
        og = str(og).strip() or None

    if ot == "tic":
        if not og:
            raise ValidationError(
                {"origen_grado": ["Debe especificar el grado cuando el origen es TIC."]}
            )
    else:
        og = None

    if admin_registrador is not None:
        if not getattr(admin_registrador, "is_staff", False) and not getattr(
            admin_registrador,
            "is_superuser",
            False,
        ):
            raise ValidationError(
                {"admin_registrador": ["El usuario registrador debe ser administrador."]}
            )
        registrado_por_admin = True

    anio_publicacion = fecha_publicacion.year if fecha_publicacion else None

    return Publicacion.objects.create(
        proyecto=proyecto,
        tipo=tipo,
        usuario_creador=usuario,
        facultad=facultad,
        carrera=carrera,
        area=area,
        subarea=subarea,
        pais=pais,
        ciudad=ciudad,
        origen_tipo=ot,
        origen_grado=og,
        fecha_publicacion=fecha_publicacion,
        anio_publicacion=anio_publicacion,
        archivo_pdf=archivo_pdf,
        registrado_por_admin=bool(registrado_por_admin),
        admin_registrador=admin_registrador,
    )