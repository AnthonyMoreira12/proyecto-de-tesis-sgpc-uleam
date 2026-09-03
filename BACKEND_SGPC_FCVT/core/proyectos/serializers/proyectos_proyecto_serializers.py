"""
Serializers del módulo de proyectos.

Este módulo gestiona:

- Representación resumida de proyectos.
- Representación completa de proyectos.
- Equipo investigador.
- Normalización de fechas y años.
- Validación del documento PDF.
- Creación y actualización transaccional.
- Sincronización de autores.
- Reglas requeridas para cerrar un proyecto.
"""

import logging
import os
import unicodedata

from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError, transaction
from django.utils import timezone

from rest_framework import serializers

from core.models import (
    Proyecto,
    Sede,
)
from core.proyectos.services.proyectos_proyecto_services import (
    autores_payload_tiene_principal,
    normalize_proyecto_autores_payload,
    proyecto_tiene_investigador_principal,
    sync_proyecto_autores,
    user_is_project_admin,
)


logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROYECTO_PDF_MAX_BYTES = 5 * 1024 * 1024

ALLOWED_PDF_EXTENSIONS = {
    ".pdf",
}

ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}

MIN_PROJECT_YEAR = 1900
MAX_PROJECT_FUTURE_YEARS = 50


# ============================================================
# UTILIDADES DE TEXTO
# ============================================================

def _normalize_single_line(
    value,
    *,
    allow_blank=False,
):
    """
    Normaliza textos destinados a una sola línea.
    """
    if value is None:
        if allow_blank:
            return ""

        raise serializers.ValidationError(
            "Este campo no puede ser nulo."
        )

    normalized = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    normalized = " ".join(
        normalized.split()
    )

    if not normalized and not allow_blank:
        raise serializers.ValidationError(
            "Este campo no puede estar vacío."
        )

    return normalized


def _normalize_multiline(
    value,
    *,
    allow_blank=True,
):
    """
    Normaliza una descripción conservando sus párrafos.
    """
    if value is None:
        return "" if allow_blank else None

    normalized = unicodedata.normalize(
        "NFKC",
        str(value),
    )

    normalized = (
        normalized
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    normalized_lines = []

    for raw_line in normalized.split("\n"):
        clean_line = " ".join(
            raw_line
            .replace("\t", " ")
            .split()
        )

        normalized_lines.append(
            clean_line
        )

    while (
        normalized_lines
        and not normalized_lines[-1]
    ):
        normalized_lines.pop()

    result = "\n".join(
        normalized_lines
    ).strip()

    if not result and not allow_blank:
        raise serializers.ValidationError(
            "Este campo no puede estar vacío."
        )

    return result


def _optional_text(value):
    """
    Devuelve un texto normalizado o None.
    """
    normalized = _normalize_single_line(
        value,
        allow_blank=True,
    )

    return normalized or None


# ============================================================
# UTILIDADES DE ARCHIVOS
# ============================================================

def _get_file_object(uploaded_file):
    """
    Obtiene el archivo interno del objeto cargado.
    """
    return getattr(
        uploaded_file,
        "file",
        uploaded_file,
    )


def _rewind_file(uploaded_file):
    """
    Restablece el puntero del archivo.
    """
    file_object = _get_file_object(
        uploaded_file
    )

    seek_method = getattr(
        file_object,
        "seek",
        None,
    )

    if callable(seek_method):
        try:
            seek_method(0)

        except (
            OSError,
            ValueError,
        ):
            pass


def _safe_file_url(
    file_field,
    *,
    request=None,
):
    """
    Obtiene la URL segura de un archivo almacenado.
    """
    if not file_field:
        return None

    file_name = getattr(
        file_field,
        "name",
        None,
    )

    if not file_name:
        return None

    try:
        file_url = file_field.url

    except (
        ValueError,
        OSError,
        NotImplementedError,
    ):
        return None

    if request is None:
        return file_url

    try:
        return request.build_absolute_uri(
            file_url
        )
    except (
        ValueError,
        TypeError,
    ):
        return file_url


def _get_storage_reference(
    file_field,
):
    """
    Obtiene el almacenamiento y el nombre de un archivo.

    La referencia se captura antes de modificar el modelo para
    poder eliminar el archivo anterior después del commit.
    """
    if not file_field:
        return None, None

    file_name = getattr(
        file_field,
        "name",
        None,
    )

    storage = getattr(
        file_field,
        "storage",
        None,
    )

    if (
        not file_name
        or storage is None
    ):
        return None, None

    return storage, file_name


def _delete_storage_file(
    storage,
    file_name,
):
    """
    Elimina un archivo de almacenamiento sin comprometer la
    respuesta ya confirmada en la base de datos.
    """
    if (
        storage is None
        or not file_name
    ):
        return

    try:
        if storage.exists(
            file_name
        ):
            storage.delete(
                file_name
            )

    except Exception:
        logger.exception(
            (
                "No fue posible eliminar el archivo de "
                "proyecto '%s' del almacenamiento."
            ),
            file_name,
        )


def _schedule_storage_file_delete(
    storage,
    file_name,
):
    """
    Programa la eliminación física únicamente después de que la
    transacción de base de datos se confirme.
    """
    if (
        storage is None
        or not file_name
    ):
        return

    transaction.on_commit(
        lambda: _delete_storage_file(
            storage,
            file_name,
        )
    )


def _get_file_size(uploaded_file):
    """
    Obtiene el tamaño del archivo como entero seguro.
    """
    try:
        return int(
            getattr(
                uploaded_file,
                "size",
                0,
            )
            or 0
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return 0


def _normalize_content_type(value):
    """
    Normaliza el tipo MIME recibido.
    """
    content_type = str(
        value or ""
    ).strip().lower()

    if ";" in content_type:
        content_type = content_type.split(
            ";",
            1,
        )[0].strip()

    return content_type or None


def _validate_pdf_signature(uploaded_file):
    """
    Comprueba que el archivo contenga una cabecera PDF real.

    El encabezado %PDF- debe aparecer dentro de los primeros
    1024 bytes del documento.
    """
    file_object = _get_file_object(
        uploaded_file
    )

    read_method = getattr(
        file_object,
        "read",
        None,
    )

    if not callable(read_method):
        raise serializers.ValidationError(
            "El documento adjunto no es válido."
        )

    _rewind_file(
        uploaded_file
    )

    try:
        header = read_method(
            1024
        )

    except (
        OSError,
        ValueError,
    ) as exc:
        raise serializers.ValidationError(
            "No fue posible leer el documento PDF."
        ) from exc

    finally:
        _rewind_file(
            uploaded_file
        )

    if isinstance(
        header,
        str,
    ):
        header = header.encode(
            "utf-8",
            errors="ignore",
        )

    if b"%PDF-" not in bytes(
        header or b""
    ):
        raise serializers.ValidationError(
            (
                "El archivo adjunto no contiene un "
                "documento PDF válido."
            )
        )


# ============================================================
# UTILIDADES DE VALIDACIÓN
# ============================================================

def _django_validation_payload(exc):
    """
    Convierte ValidationError de Django en una estructura DRF.
    """
    if hasattr(
        exc,
        "message_dict",
    ):
        return exc.message_dict

    if hasattr(
        exc,
        "messages",
    ):
        return {
            "detail": list(
                exc.messages
            )
        }

    return {
        "detail": str(exc),
    }


def _validate_project_year(
    value,
    *,
    field_name,
):
    """
    Valida un año dentro de un rango razonable.
    """
    if value is None:
        return None

    minimum_year = MIN_PROJECT_YEAR

    maximum_year = (
        timezone.localdate().year
        + MAX_PROJECT_FUTURE_YEARS
    )

    if not (
        minimum_year
        <= value
        <= maximum_year
    ):
        raise serializers.ValidationError(
            {
                field_name: (
                    f"El año debe estar entre {minimum_year} "
                    f"y {maximum_year}."
                )
            }
        )

    return value


# ============================================================
# CAMPOS FLEXIBLES
# ============================================================

class EmptyStringToNoneDateField(
    serializers.DateField
):
    """
    Convierte cadenas vacías en None.
    """

    def to_internal_value(
        self,
        value,
    ):
        if value in (
            "",
            None,
        ):
            return None

        return super().to_internal_value(
            value
        )


class EmptyStringToNoneIntegerField(
    serializers.IntegerField
):
    """
    Convierte cadenas vacías en None y rechaza booleanos.
    """

    def to_internal_value(
        self,
        value,
    ):
        if value in (
            "",
            None,
        ):
            return None

        if isinstance(
            value,
            bool,
        ):
            self.fail(
                "invalid"
            )

        return super().to_internal_value(
            value
        )


class FlexibleJSONField(
    serializers.Field
):
    """
    Conserva el valor recibido para que el servicio pueda
    procesar listas, objetos o cadenas JSON de multipart.
    """

    def to_internal_value(
        self,
        data,
    ):
        return data

    def to_representation(
        self,
        value,
    ):
        return value


# ============================================================
# SERIALIZERS DE PARTICIPACIONES
# ============================================================

class ProyectoAutorResumenSerializer(
    serializers.Serializer
):
    """
    Representación académica mínima de un integrante.

    Se utiliza en listados y respuestas para usuarios que no
    administran proyectos. No expone:

    - Identificación.
    - Correo.
    - Identificador interno del Usuario.
    """

    participacion_id = serializers.IntegerField(
        source="id",
        read_only=True,
    )

    id = serializers.IntegerField(
        source="autor.id",
        read_only=True,
    )

    nombre = serializers.SerializerMethodField(
        read_only=True,
    )

    nombre_completo = serializers.SerializerMethodField(
        read_only=True,
    )

    institucion = serializers.CharField(
        source="autor.institucion",
        read_only=True,
        allow_null=True,
    )

    es_externo = serializers.BooleanField(
        source="autor.es_externo",
        read_only=True,
    )

    rol = serializers.CharField(
        read_only=True,
    )

    rol_label = serializers.SerializerMethodField(
        read_only=True,
    )

    orden = serializers.IntegerField(
        read_only=True,
    )

    def _get_author(
        self,
        obj,
    ):
        return getattr(
            obj,
            "autor",
            None,
        )

    def get_nombre_completo(
        self,
        obj,
    ):
        author = self._get_author(
            obj
        )

        if author is None:
            return ""

        names = _optional_text(
            getattr(
                author,
                "nombres",
                None,
            )
        )

        surnames = _optional_text(
            getattr(
                author,
                "apellidos",
                None,
            )
        )

        return " ".join(
            value
            for value in [
                names,
                surnames,
            ]
            if value
        )

    def get_nombre(
        self,
        obj,
    ):
        return self.get_nombre_completo(
            obj
        )

    def get_rol_label(
        self,
        obj,
    ):
        get_display = getattr(
            obj,
            "get_rol_display",
            None,
        )

        if callable(
            get_display
        ):
            label = _optional_text(
                get_display()
            )

            if label:
                return label

        return _optional_text(
            getattr(
                obj,
                "rol",
                None,
            )
        )


class ProyectoAutorReadSerializer(
    ProyectoAutorResumenSerializer
):
    """
    Representación administrativa del integrante.

    Los campos personales se entregan solamente cuando la vista
    ha comprobado que el solicitante administra proyectos.
    """

    nombres = serializers.CharField(
        source="autor.nombres",
        read_only=True,
    )

    apellidos = serializers.CharField(
        source="autor.apellidos",
        read_only=True,
    )

    identificacion = serializers.CharField(
        source="autor.identificacion",
        read_only=True,
        allow_null=True,
    )

    correo = serializers.SerializerMethodField(
        read_only=True,
    )

    usuario_id = serializers.IntegerField(
        source="autor.usuario_id",
        read_only=True,
        allow_null=True,
    )

    def get_correo(
        self,
        obj,
    ):
        """
        Prioriza el correo del Usuario vinculado.
        """
        author = self._get_author(
            obj
        )

        if author is None:
            return None

        linked_user = getattr(
            author,
            "usuario",
            None,
        )

        user_email = _optional_text(
            getattr(
                linked_user,
                "email",
                None,
            )
            if linked_user is not None
            else None
        )

        author_email = _optional_text(
            getattr(
                author,
                "correo",
                None,
            )
        )

        return user_email or author_email


# ============================================================
# MIXIN DE REPRESENTACIÓN
# ============================================================

class ProyectoRepresentationMixin:
    """
    Métodos compartidos por los serializers de proyecto.
    """

    def _request_is_project_admin(
        self,
    ):
        """
        Comprueba si la respuesta puede incluir datos
        administrativos del equipo investigador.
        """
        request = self.context.get(
            "request"
        )

        if request is None:
            return False

        return user_is_project_admin(
            getattr(
                request,
                "user",
                None,
            )
        )


    def _get_participaciones(
        self,
        obj,
    ):
        cache_attribute = (
            "_serializer_participaciones_cache"
        )

        if hasattr(
            obj,
            cache_attribute,
        ):
            return getattr(
                obj,
                cache_attribute,
            )

        participations_manager = getattr(
            obj,
            "participaciones",
            None,
        )

        if participations_manager is None:
            participations = []

        else:
            participations = list(
                participations_manager.all()
            )

        setattr(
            obj,
            cache_attribute,
            participations,
        )

        return participations

    def get_sede_nombre(
        self,
        obj,
    ):
        site = getattr(
            obj,
            "sede",
            None,
        )

        if site is None:
            return None

        return _optional_text(
            getattr(
                site,
                "nombre",
                None,
            )
        )

    def get_carrera_nombre(
        self,
        obj,
    ):
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        return _optional_text(
            getattr(
                career,
                "nombre",
                None,
            )
        )

    def get_facultad(
        self,
        obj,
    ):
        career = getattr(
            obj,
            "carrera",
            None,
        )

        if career is None:
            return None

        faculty = getattr(
            career,
            "facultad",
            None,
        )

        if faculty is None:
            return None

        return _optional_text(
            getattr(
                faculty,
                "nombre",
                None,
            )
        )

    def get_estado_label(
        self,
        obj,
    ):
        get_display = getattr(
            obj,
            "get_estado_display",
            None,
        )

        if callable(get_display):
            label = _optional_text(
                get_display()
            )

            if label:
                return label

        return _optional_text(
            getattr(
                obj,
                "estado",
                None,
            )
        )

    def get_archivo_pdf_url(
        self,
        obj,
    ):
        return _safe_file_url(
            getattr(
                obj,
                "archivo_pdf",
                None,
            ),
            request=self.context.get(
                "request"
            ),
        )

    def get_autores_total(
        self,
        obj,
    ):
        return len(
            self._get_participaciones(
                obj
            )
        )

    def get_tiene_investigador_principal(
        self,
        obj,
    ):
        return any(
            getattr(
                participation,
                "rol",
                None,
            )
            == "principal"
            for participation
            in self._get_participaciones(
                obj
            )
        )

    def get_equipo_pendiente(
        self,
        obj,
    ):
        return (
            self.get_autores_total(
                obj
            )
            == 0
        )


# ============================================================
# SERIALIZER DE LISTADO
# ============================================================

class ProyectoListSerializer(
    ProyectoRepresentationMixin,
    serializers.ModelSerializer,
):
    """
    Representación ligera utilizada en listados paginados.
    """

    sede_nombre = serializers.SerializerMethodField(
        read_only=True,
    )

    carrera_nombre = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad = serializers.SerializerMethodField(
        read_only=True,
    )

    estado_label = serializers.SerializerMethodField(
        read_only=True,
    )

    fecha_fin_vigente = serializers.DateField(
        read_only=True,
        allow_null=True,
    )

    archivo_pdf_url = serializers.SerializerMethodField(
        read_only=True,
    )

    autores_resumen = serializers.SerializerMethodField(
        read_only=True,
    )

    autores_total = serializers.SerializerMethodField(
        read_only=True,
    )

    tiene_investigador_principal = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    equipo_pendiente = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Proyecto

        fields = [
            "id",
            "nombre",
            "descripcion",
            "estado",
            "estado_label",

            "sede",
            "sede_nombre",
            "carrera",
            "carrera_nombre",
            "facultad",

            "fecha_inicio",
            "fecha_fin_planificada",
            "fecha_fin_prorrogada",
            "fecha_fin_vigente",
            "fecha_cierre",

            "anio_inicio",
            "anio_fin",

            "archivo_pdf_url",

            "autores_resumen",
            "autores_total",
            "tiene_investigador_principal",
            "equipo_pendiente",
        ]

        read_only_fields = fields

    def get_autores_resumen(
        self,
        obj,
    ):
        serializer = ProyectoAutorResumenSerializer(
            self._get_participaciones(
                obj
            ),
            many=True,
            context=self.context,
        )

        return serializer.data


# ============================================================
# SERIALIZER COMPLETO
# ============================================================

class ProyectoSerializer(
    ProyectoRepresentationMixin,
    serializers.ModelSerializer,
):
    """
    Serializer completo para crear, consultar y actualizar
    proyectos.
    """

    sede = serializers.PrimaryKeyRelatedField(
        queryset=Sede.objects.all(),
        required=False,
        allow_null=True,
    )

    sede_nombre = serializers.SerializerMethodField(
        read_only=True,
    )

    carrera_nombre = serializers.SerializerMethodField(
        read_only=True,
    )

    facultad = serializers.SerializerMethodField(
        read_only=True,
    )

    creado_por = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    estado = serializers.ChoiceField(
        choices=Proyecto.ESTADOS,
        required=False,
    )

    estado_label = serializers.SerializerMethodField(
        read_only=True,
    )

    fecha_inicio = EmptyStringToNoneDateField(
        required=False,
        allow_null=True,
    )

    fecha_fin_planificada = (
        EmptyStringToNoneDateField(
            required=False,
            allow_null=True,
        )
    )

    fecha_fin_prorrogada = (
        EmptyStringToNoneDateField(
            required=False,
            allow_null=True,
        )
    )

    fecha_cierre = EmptyStringToNoneDateField(
        required=False,
        allow_null=True,
    )

    anio_inicio = EmptyStringToNoneIntegerField(
        required=False,
        allow_null=True,
    )

    anio_fin = EmptyStringToNoneIntegerField(
        required=False,
        allow_null=True,
    )

    fecha_fin_vigente = serializers.DateField(
        read_only=True,
        allow_null=True,
    )

    archivo_pdf = serializers.FileField(
        required=False,
        allow_null=True,
        allow_empty_file=False,
    )

    archivo_pdf_url = serializers.SerializerMethodField(
        read_only=True,
    )

    autores = serializers.SerializerMethodField(
        read_only=True,
    )

    autores_data = FlexibleJSONField(
        write_only=True,
        required=False,
        allow_null=True,
    )

    eliminar_archivo_pdf = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False,
    )

    autores_total = serializers.SerializerMethodField(
        read_only=True,
    )

    tiene_investigador_principal = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    equipo_pendiente = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Proyecto

        fields = [
            "id",
            "nombre",
            "descripcion",
            "estado",
            "estado_label",

            "sede",
            "sede_nombre",
            "carrera",
            "carrera_nombre",
            "facultad",

            "fecha_inicio",
            "fecha_fin_planificada",
            "fecha_fin_prorrogada",
            "fecha_fin_vigente",
            "fecha_cierre",

            "anio_inicio",
            "anio_fin",

            "archivo_pdf",
            "archivo_pdf_url",
            "eliminar_archivo_pdf",

            "autores",
            "autores_data",
            "autores_total",
            "tiene_investigador_principal",
            "equipo_pendiente",

            "fecha_creacion",
            "creado_por",
        ]

        read_only_fields = [
            "id",
            "sede_nombre",
            "carrera_nombre",
            "facultad",
            "fecha_fin_vigente",
            "archivo_pdf_url",
            "autores",
            "autores_total",
            "tiene_investigador_principal",
            "equipo_pendiente",
            "fecha_creacion",
            "creado_por",
            "estado_label",
        ]

    def get_autores(
        self,
        obj,
    ):
        """
        Expone datos personales del equipo únicamente a
        administradores de proyectos.
        """
        serializer_class = (
            ProyectoAutorReadSerializer
            if self._request_is_project_admin()
            else ProyectoAutorResumenSerializer
        )

        serializer = serializer_class(
            self._get_participaciones(
                obj
            ),
            many=True,
            context=self.context,
        )

        return serializer.data

    # ========================================================
    # VALIDACIONES DE CAMPOS
    # ========================================================

    def validate_nombre(
        self,
        value,
    ):
        return _normalize_single_line(
            value,
            allow_blank=False,
        )

    def validate_descripcion(
        self,
        value,
    ):
        return _normalize_multiline(
            value,
            allow_blank=True,
        )

    def validate_anio_inicio(
        self,
        value,
    ):
        return _validate_project_year(
            value,
            field_name="anio_inicio",
        )

    def validate_anio_fin(
        self,
        value,
    ):
        return _validate_project_year(
            value,
            field_name="anio_fin",
        )

    def validate_archivo_pdf(
        self,
        value,
    ):
        """
        Valida extensión, MIME, tamaño y contenido real del PDF.
        """
        if value is None:
            return None

        file_name = str(
            getattr(
                value,
                "name",
                "",
            )
            or ""
        ).strip()

        if not file_name:
            raise serializers.ValidationError(
                (
                    "No fue posible determinar el nombre "
                    "del archivo."
                )
            )

        extension = os.path.splitext(
            file_name.lower()
        )[1]

        if extension not in ALLOWED_PDF_EXTENSIONS:
            raise serializers.ValidationError(
                "Solo se permiten documentos PDF."
            )

        content_type = _normalize_content_type(
            getattr(
                value,
                "content_type",
                None,
            )
            or getattr(
                getattr(
                    value,
                    "file",
                    None,
                ),
                "content_type",
                None,
            )
        )

        if (
            content_type is not None
            and content_type
            not in ALLOWED_PDF_CONTENT_TYPES
        ):
            raise serializers.ValidationError(
                "El archivo debe tener formato PDF."
            )

        file_size = _get_file_size(
            value
        )

        if file_size <= 0:
            raise serializers.ValidationError(
                "El documento PDF está vacío."
            )

        if file_size > PROYECTO_PDF_MAX_BYTES:
            raise serializers.ValidationError(
                (
                    "El documento PDF supera el tamaño "
                    "máximo permitido de 5 MB."
                )
            )

        _validate_pdf_signature(
            value
        )

        _rewind_file(
            value
        )

        return value

    def validate_autores_data(
        self,
        value,
    ):
        return normalize_proyecto_autores_payload(
            value
        )

    # ========================================================
    # VALIDACIÓN CONJUNTA
    # ========================================================

    def validate(
        self,
        attrs,
    ):
        instance = getattr(
            self,
            "instance",
            None,
        )

        sede_was_sent = (
            "sede" in attrs
        )

        carrera_was_sent = (
            "carrera" in attrs
        )

        site = attrs.get(
            "sede",
            getattr(
                instance,
                "sede",
                None,
            ),
        )

        career = attrs.get(
            "carrera",
            getattr(
                instance,
                "carrera",
                None,
            ),
        )

        # Los proyectos nuevos deben quedar clasificados por Sede.
        # Los registros históricos con sede NULL pueden seguir
        # consultándose y recibir cambios no académicos durante la
        # transición de datos.
        if instance is None and site is None:
            raise serializers.ValidationError(
                {
                    "sede": (
                        "La sede es obligatoria para registrar "
                        "un proyecto nuevo."
                    )
                }
            )

        if (
            instance is not None
            and (sede_was_sent or carrera_was_sent)
            and site is None
        ):
            raise serializers.ValidationError(
                {
                    "sede": (
                        "Debe seleccionar una sede al modificar "
                        "la clasificación académica del proyecto."
                    )
                }
            )

        if site is not None and not bool(
            getattr(site, "activa", False)
        ):
            raise serializers.ValidationError(
                {
                    "sede": (
                        "La sede seleccionada no está activa."
                    )
                }
            )

        if site is not None and career is not None:
            relation_is_active = (
                career
                .sedes_carrera
                .filter(
                    sede_id=site.pk,
                    activa=True,
                )
                .exists()
            )

            if not relation_is_active:
                raise serializers.ValidationError(
                    {
                        "carrera": (
                            "La carrera seleccionada no está "
                            "habilitada en la sede indicada."
                        )
                    }
                )

        current_state = str(
            getattr(
                instance,
                "estado",
                "nuevo",
            )
            or "nuevo"
        ).strip().lower()

        state = str(
            attrs.get(
                "estado",
                current_state,
            )
            or "nuevo"
        ).strip().lower()

        start_date = attrs.get(
            "fecha_inicio",
            getattr(
                instance,
                "fecha_inicio",
                None,
            ),
        )

        planned_end_date = attrs.get(
            "fecha_fin_planificada",
            getattr(
                instance,
                "fecha_fin_planificada",
                None,
            ),
        )

        extended_end_date = attrs.get(
            "fecha_fin_prorrogada",
            getattr(
                instance,
                "fecha_fin_prorrogada",
                None,
            ),
        )

        closing_date = attrs.get(
            "fecha_cierre",
            getattr(
                instance,
                "fecha_cierre",
                None,
            ),
        )

        start_year = attrs.get(
            "anio_inicio",
            getattr(
                instance,
                "anio_inicio",
                None,
            ),
        )

        end_year = attrs.get(
            "anio_fin",
            getattr(
                instance,
                "anio_fin",
                None,
            ),
        )

        allow_state_transition = bool(
            self.context.get(
                "allow_state_transition",
                False,
            )
        )

        state_was_sent = (
            "estado" in attrs
        )

        if instance is None:
            if (
                state_was_sent
                and state != "nuevo"
            ):
                raise serializers.ValidationError(
                    {
                        "estado": (
                            "Los proyectos nuevos deben "
                            "registrarse inicialmente con "
                            "estado 'nuevo'."
                        )
                    }
                )

        elif (
            state_was_sent
            and state != current_state
            and not allow_state_transition
        ):
            raise serializers.ValidationError(
                {
                    "estado": (
                        "El estado no puede modificarse desde "
                        "el formulario general. Utilice la "
                        "acción de cambio de estado."
                    )
                }
            )

        delete_pdf = bool(
            attrs.get(
                "eliminar_archivo_pdf",
                False,
            )
        )

        new_pdf_was_sent = (
            "archivo_pdf" in attrs
            and attrs.get(
                "archivo_pdf"
            )
            is not None
        )

        if (
            delete_pdf
            and new_pdf_was_sent
        ):
            raise serializers.ValidationError(
                {
                    "eliminar_archivo_pdf": (
                        "No puede cargar un PDF nuevo y "
                        "solicitar la eliminación del archivo "
                        "actual en la misma operación."
                    )
                }
            )

        if (
            instance is None
            and delete_pdf
        ):
            raise serializers.ValidationError(
                {
                    "eliminar_archivo_pdf": (
                        "No existe un archivo previo que pueda "
                        "eliminarse durante la creación."
                    )
                }
            )

        # ----------------------------------------------------
        # ESTADO Y FECHA DE CIERRE
        # ----------------------------------------------------

        if state == "cierre":
            if not closing_date:
                closing_date = (
                    timezone.localdate()
                )

                attrs["fecha_cierre"] = (
                    closing_date
                )

        elif closing_date is not None:
            closing_date = None
            attrs["fecha_cierre"] = None

        # ----------------------------------------------------
        # FECHA Y AÑO DE INICIO
        # ----------------------------------------------------

        if start_date is not None:
            calculated_start_year = (
                start_date.year
            )

            if (
                "anio_inicio" in attrs
                and attrs.get(
                    "anio_inicio"
                )
                is not None
                and attrs["anio_inicio"]
                != calculated_start_year
            ):
                raise serializers.ValidationError(
                    {
                        "anio_inicio": (
                            "El año de inicio no coincide "
                            "con la fecha de inicio."
                        )
                    }
                )

            start_year = calculated_start_year
            attrs["anio_inicio"] = start_year

        # ----------------------------------------------------
        # FECHA Y AÑO FINAL
        # ----------------------------------------------------

        if state == "cierre":
            final_reference_date = (
                closing_date
            )

        else:
            final_reference_date = (
                extended_end_date
                or planned_end_date
            )

        if final_reference_date is not None:
            calculated_end_year = (
                final_reference_date.year
            )

            if (
                "anio_fin" in attrs
                and attrs.get(
                    "anio_fin"
                )
                is not None
                and attrs["anio_fin"]
                != calculated_end_year
            ):
                raise serializers.ValidationError(
                    {
                        "anio_fin": (
                            "El año de finalización no coincide "
                            "con la fecha final vigente."
                        )
                    }
                )

            end_year = calculated_end_year
            attrs["anio_fin"] = end_year

        else:
            end_dates_changed = any(
                field_name in attrs
                for field_name in (
                    "fecha_fin_planificada",
                    "fecha_fin_prorrogada",
                    "fecha_cierre",
                )
            )

            reopened_project = (
                current_state == "cierre"
                and state != "cierre"
            )

            if (
                "anio_fin" not in attrs
                and (
                    end_dates_changed
                    or reopened_project
                )
            ):
                end_year = None
                attrs["anio_fin"] = None

        # ----------------------------------------------------
        # RANGO DE AÑOS
        # ----------------------------------------------------

        if (
            start_year is not None
            and end_year is not None
            and end_year < start_year
        ):
            raise serializers.ValidationError(
                {
                    "anio_fin": (
                        "El año de finalización no puede "
                        "ser menor al año de inicio."
                    )
                }
            )

        # ----------------------------------------------------
        # ORDEN CRONOLÓGICO
        # ----------------------------------------------------

        if (
            start_date is not None
            and planned_end_date is not None
            and planned_end_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "fecha_fin_planificada": (
                        "La fecha de finalización planificada "
                        "no puede ser menor a la fecha de inicio."
                    )
                }
            )

        if (
            start_date is not None
            and extended_end_date is not None
            and extended_end_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "fecha_fin_prorrogada": (
                        "La fecha prorrogada no puede ser "
                        "menor a la fecha de inicio."
                    )
                }
            )

        if (
            planned_end_date is not None
            and extended_end_date is not None
            and extended_end_date
            < planned_end_date
        ):
            raise serializers.ValidationError(
                {
                    "fecha_fin_prorrogada": (
                        "La fecha prorrogada no puede ser "
                        "menor a la fecha planificada."
                    )
                }
            )

        if (
            closing_date is not None
            and start_date is not None
            and closing_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "fecha_cierre": (
                        "La fecha de cierre no puede ser "
                        "menor a la fecha de inicio."
                    )
                }
            )

        # ----------------------------------------------------
        # EQUIPO REQUERIDO PARA CIERRE
        # ----------------------------------------------------

        authors_payload_was_sent = (
            "autores_data" in attrs
            and attrs.get(
                "autores_data"
            )
            is not None
        )

        if state == "cierre":
            if authors_payload_was_sent:
                has_main_researcher = (
                    autores_payload_tiene_principal(
                        attrs["autores_data"]
                    )
                )

            else:
                has_main_researcher = (
                    proyecto_tiene_investigador_principal(
                        instance
                    )
                )

            if not has_main_researcher:
                raise serializers.ValidationError(
                    {
                        "autores_data": (
                            "Para cerrar el proyecto debe "
                            "existir al menos un investigador "
                            "principal."
                        )
                    }
                )

        return attrs

    # ========================================================
    # CREACIÓN
    # ========================================================

    def create(
        self,
        validated_data,
    ):
        authors_data = validated_data.pop(
            "autores_data",
            None,
        )

        validated_data.pop(
            "eliminar_archivo_pdf",
            False,
        )

        created_file_storage = None
        created_file_name = None

        try:
            try:
                with transaction.atomic():
                    project = Proyecto(
                        **validated_data
                    )

                    project.full_clean()
                    project.save()

                    (
                        created_file_storage,
                        created_file_name,
                    ) = _get_storage_reference(
                        getattr(
                            project,
                            "archivo_pdf",
                            None,
                        )
                    )

                    if authors_data is not None:
                        sync_proyecto_autores(
                            project,
                            authors_data,
                        )

                    return project

            except Exception:
                if (
                    created_file_storage is not None
                    and created_file_name
                ):
                    _delete_storage_file(
                        created_file_storage,
                        created_file_name,
                    )

                raise

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible crear el proyecto "
                        "debido a un conflicto con los "
                        "datos almacenados."
                    )
                }
            ) from exc

        except OSError as exc:
            raise serializers.ValidationError(
                {
                    "archivo_pdf": (
                        "No fue posible almacenar el "
                        "documento PDF del proyecto."
                    )
                }
            ) from exc

    # ========================================================
    # ACTUALIZACIÓN
    # ========================================================

    def update(
        self,
        instance,
        validated_data,
    ):
        authors_data = validated_data.pop(
            "autores_data",
            None,
        )

        delete_pdf = bool(
            validated_data.pop(
                "eliminar_archivo_pdf",
                False,
            )
        )

        new_pdf_was_sent = (
            "archivo_pdf" in validated_data
            and validated_data.get(
                "archivo_pdf"
            )
            is not None
        )

        project_id = getattr(
            instance,
            "pk",
            None,
        )

        if not project_id:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "El proyecto debe estar guardado "
                        "antes de actualizarse."
                    )
                }
            )

        new_file_storage = None
        new_file_name = None
        old_file_storage = None
        old_file_name = None

        try:
            try:
                with transaction.atomic():
                    try:
                        locked_project = (
                            Proyecto.objects
                            .select_for_update()
                            .get(
                                pk=project_id
                            )
                        )

                    except Proyecto.DoesNotExist as exc:
                        raise serializers.ValidationError(
                            {
                                "detail": (
                                    "El proyecto ya no existe."
                                )
                            }
                        ) from exc

                    (
                        old_file_storage,
                        old_file_name,
                    ) = _get_storage_reference(
                        getattr(
                            locked_project,
                            "archivo_pdf",
                            None,
                        )
                    )

                    if delete_pdf:
                        validated_data[
                            "archivo_pdf"
                        ] = None

                    for field_name, value in (
                        validated_data.items()
                    ):
                        setattr(
                            locked_project,
                            field_name,
                            value,
                        )

                    locked_project.full_clean()
                    locked_project.save()

                    if new_pdf_was_sent:
                        (
                            new_file_storage,
                            new_file_name,
                        ) = _get_storage_reference(
                            getattr(
                                locked_project,
                                "archivo_pdf",
                                None,
                            )
                        )

                    if authors_data is not None:
                        sync_proyecto_autores(
                            locked_project,
                            authors_data,
                        )

                    file_was_replaced = bool(
                        new_pdf_was_sent
                        and old_file_name
                        and new_file_name
                        and old_file_name
                        != new_file_name
                    )

                    if (
                        old_file_name
                        and (
                            delete_pdf
                            or file_was_replaced
                        )
                    ):
                        _schedule_storage_file_delete(
                            old_file_storage,
                            old_file_name,
                        )

                    if hasattr(
                        locked_project,
                        "_prefetched_objects_cache",
                    ):
                        locked_project._prefetched_objects_cache = {}

                    if hasattr(
                        locked_project,
                        "_serializer_participaciones_cache",
                    ):
                        delattr(
                            locked_project,
                            "_serializer_participaciones_cache",
                        )

                    return locked_project

            except Exception:
                if (
                    new_file_storage is not None
                    and new_file_name
                    and new_file_name != old_file_name
                ):
                    _delete_storage_file(
                        new_file_storage,
                        new_file_name,
                    )

                raise

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                _django_validation_payload(
                    exc
                )
            ) from exc

        except IntegrityError as exc:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "No fue posible actualizar el proyecto "
                        "debido a un conflicto con los "
                        "datos almacenados."
                    )
                }
            ) from exc

        except OSError as exc:
            raise serializers.ValidationError(
                {
                    "archivo_pdf": (
                        "No fue posible almacenar el "
                        "documento PDF del proyecto."
                    )
                }
            ) from exc