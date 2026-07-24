from rest_framework.exceptions import ValidationError

from core.models import Publicacion, TipoPublicacion


def _norm_text(value):
    return str(value or "").strip()


def _norm_lower(value):
    value = _norm_text(value)
    return value.lower() if value else ""


def obtener_o_crear_tipo_publicacion(
    *,
    codigo: str,
    nombre: str,
    categoria: str,
    orden: int,
):
    codigo = _norm_lower(codigo)
    nombre = _norm_text(nombre)
    categoria = _norm_lower(categoria)

    if not codigo:
        raise ValidationError(
            {"tipo_codigo": ["El código del tipo de publicación es obligatorio."]}
        )

    if not nombre:
        raise ValidationError(
            {"tipo_codigo": ["El nombre del tipo de publicación es obligatorio."]}
        )

    categorias_validas = {
        value
        for value, _label
        in TipoPublicacion.CATEGORIAS
    }

    if categoria not in categorias_validas:
        raise ValidationError(
            {
                "tipo_codigo": [
                    "La categoría del tipo de publicación no es válida."
                ]
            }
        )

    try:
        orden = int(orden)
    except (TypeError, ValueError):
        raise ValidationError(
            {"tipo_codigo": ["El orden del tipo de publicación debe ser numérico."]}
        )

    if orden < 1:
        raise ValidationError(
            {
                "tipo_codigo": [
                    "El orden del tipo de publicación debe ser mayor o igual a 1."
                ]
            }
        )

    tipo, created = TipoPublicacion.objects.get_or_create(
        codigo=codigo,
        defaults={
            "nombre": nombre,
            "categoria": categoria,
            "orden": orden,
        },
    )

    if created:
        return tipo

    changed_fields = []

    if tipo.nombre != nombre:
        tipo.nombre = nombre
        changed_fields.append("nombre")

    if tipo.categoria != categoria:
        tipo.categoria = categoria
        changed_fields.append("categoria")

    if tipo.orden != orden:
        tipo.orden = orden
        changed_fields.append("orden")

    if changed_fields:
        tipo.save(update_fields=changed_fields)

    return tipo


def crear_publicacion_base(
    *,
    proyecto,
    tipo,
    usuario,
    carrera,
    facultad=None,
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
    """
    Crea la entidad Publicacion común a todos sus subtipos.

    IMPORTANTE:
    Publicacion NO almacena facultad directamente.

    La relación institucional correcta es:

        Publicacion -> Carrera -> Facultad

    El argumento ``facultad`` se conserva temporalmente únicamente por
    compatibilidad con los serializers/formularios existentes. Se utiliza
    para validar la coherencia Carrera/Facultad, pero nunca se persiste
    directamente en Publicacion.
    """

    if tipo is None:
        raise ValidationError(
            {"tipo": ["El tipo de publicación es obligatorio."]}
        )

    if usuario is None:
        raise ValidationError(
            {"usuario_creador": ["El usuario creador es obligatorio."]}
        )

    if carrera is None:
        raise ValidationError(
            {"carrera": ["La carrera es obligatoria."]}
        )

    # ---------------------------------------------------------
    # Carrera -> Facultad
    # ---------------------------------------------------------

    if facultad is not None:
        carrera_facultad_id = getattr(
            carrera,
            "facultad_id",
            None,
        )

        facultad_id = getattr(
            facultad,
            "id",
            None,
        )

        if carrera_facultad_id != facultad_id:
            raise ValidationError(
                {
                    "carrera": [
                        "La carrera seleccionada no pertenece "
                        "a la facultad indicada."
                    ]
                }
            )

    # ---------------------------------------------------------
    # Proyecto -> Carrera
    # ---------------------------------------------------------

    if proyecto is not None:
        proyecto_carrera_id = getattr(
            proyecto,
            "carrera_id",
            None,
        )

        carrera_id = getattr(
            carrera,
            "id",
            None,
        )

        if proyecto_carrera_id != carrera_id:
            raise ValidationError(
                {
                    "proyecto": [
                        "El proyecto seleccionado no pertenece "
                        "a la carrera indicada."
                    ]
                }
            )

    # ---------------------------------------------------------
    # Área -> Subárea
    # ---------------------------------------------------------

    if subarea is not None and area is None:
        area = getattr(
            subarea,
            "area",
            None,
        )

    if area is not None and subarea is not None:
        if getattr(subarea, "area_id", None) != getattr(area, "id", None):
            raise ValidationError(
                {
                    "subarea": [
                        "La subárea seleccionada no pertenece "
                        "al área indicada."
                    ]
                }
            )

    # ---------------------------------------------------------
    # País -> Ciudad
    # ---------------------------------------------------------

    if ciudad is not None and pais is None:
        raise ValidationError(
            {
                "pais": [
                    "Debe seleccionar un país cuando "
                    "seleccione una ciudad."
                ]
            }
        )

    if pais is not None and ciudad is not None:
        if getattr(ciudad, "pais_id", None) != getattr(pais, "id", None):
            raise ValidationError(
                {
                    "ciudad": [
                        "La ciudad seleccionada no pertenece "
                        "al país indicado."
                    ]
                }
            )

    # ---------------------------------------------------------
    # Origen
    # ---------------------------------------------------------

    origen_tipo = (
        _norm_lower(origen_tipo)
        or "ninguno"
    )

    origenes_validos = {
        value
        for value, _label
        in Publicacion.ORIGEN_TIPO
    }

    if origen_tipo not in origenes_validos:
        raise ValidationError(
            {
                "origen_tipo": [
                    "El origen de la publicación no es válido."
                ]
            }
        )

    origen_grado = (
        _norm_text(origen_grado)
        or None
    )

    if origen_tipo == "tic":
        if not origen_grado:
            raise ValidationError(
                {
                    "origen_grado": [
                        "Debe especificar el grado cuando "
                        "el origen es TIC."
                    ]
                }
            )
    else:
        origen_grado = None

    # ---------------------------------------------------------
    # Registro administrativo
    # ---------------------------------------------------------

    if admin_registrador is not None:
        es_admin = bool(
            getattr(
                admin_registrador,
                "is_staff",
                False,
            )
            or getattr(
                admin_registrador,
                "is_superuser",
                False,
            )
        )

        if not es_admin:
            raise ValidationError(
                {
                    "admin_registrador": [
                        "El usuario registrador debe tener "
                        "privilegios administrativos."
                    ]
                }
            )

        registrado_por_admin = True

    if registrado_por_admin and admin_registrador is None:
        raise ValidationError(
            {
                "admin_registrador": [
                    "Debe indicar el administrador que "
                    "registró la publicación."
                ]
            }
        )

    if not registrado_por_admin:
        admin_registrador = None

    # ---------------------------------------------------------
    # Creación
    # ---------------------------------------------------------

    return Publicacion.objects.create(
        proyecto=proyecto,
        tipo=tipo,
        usuario_creador=usuario,

        # NO existe:
        # facultad=facultad

        carrera=carrera,
        area=area,
        subarea=subarea,
        pais=pais,
        ciudad=ciudad,
        origen_tipo=origen_tipo,
        origen_grado=origen_grado,
        fecha_publicacion=fecha_publicacion,
        archivo_pdf=archivo_pdf,
        registrado_por_admin=bool(
            registrado_por_admin
        ),
        admin_registrador=admin_registrador,
    )