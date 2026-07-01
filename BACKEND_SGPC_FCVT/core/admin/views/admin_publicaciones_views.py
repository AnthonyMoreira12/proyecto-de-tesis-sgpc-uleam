# ViewSet administrativo de publicaciones:
# permite listar, consultar, actualizar, eliminar y crear publicaciones delegadas
# desde el panel admin, incluyendo artículos, ponencias, libros, capítulos y adjuntos PDF.

import json
import os

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.admin.selectors.admin_publicaciones_selectors import (
    admin_publicaciones_base_queryset,
    filter_admin_publicaciones_queryset,
)
from core.admin.serializers.admin_publicaciones_serializers import (
    AdminPublicacionDetalleSerializer,
    AdminPublicacionListadoSerializer,
)
from core.admin.services.admin_publicaciones_services import (
    AdminPublicacionesServiceError,
    prepare_admin_publicacion_payload,
)
from core.models import PublicacionArchivo
from core.permisos.es_admin import EsAdmin
from core.publicaciones.serializers.create.publicaciones_articulo_create_serializers import (
    ArticuloRegistroSerializer,
)
from core.publicaciones.serializers.create.publicaciones_capitulo_libro_create_serializers import (
    CapituloLibroRegistroSerializer,
)
from core.publicaciones.serializers.create.publicaciones_libro_create_serializers import (
    LibroRegistroSerializer,
)
from core.publicaciones.serializers.create.publicaciones_ponencia_create_serializers import (
    PonenciaRegistroSerializer,
)
from core.publicaciones.serializers.update.publicaciones_actualizacion_serializers import (
    PublicacionActualizacionSerializer,
)


MAX_ADJUNTOS_POR_PUBLICACION_ADMIN = 2


def _parse_bool(value):
    if value is None:
        return None

    s = str(value).strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return None


def _django_validation_to_payload(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict

    if hasattr(exc, "messages"):
        return {"detail": exc.messages}

    return {"detail": str(exc)}


class AdminPublicacionViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, EsAdmin]
    queryset = admin_publicaciones_base_queryset()
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        q = self.request.query_params.get("q", "")
        tipo = self.request.query_params.get("tipo") or self.request.query_params.get(
            "tipo_publicacion_final",
            "",
        )

        usuario_objetivo_id = (
            self.request.query_params.get("usuario_objetivo_id")
            or self.request.query_params.get("usuario_id")
        )
        autor_objetivo_id = (
            self.request.query_params.get("autor_objetivo_id")
            or self.request.query_params.get("autor_id")
        )

        admin_registrador_id = self.request.query_params.get("admin_registrador_id")
        facultad_id = self.request.query_params.get("facultad_id")
        carrera_id = self.request.query_params.get("carrera_id")
        anio = self.request.query_params.get("anio")

        solo_delegadas = _parse_bool(self.request.query_params.get("solo_delegadas"))
        solo_con_pdf = _parse_bool(self.request.query_params.get("solo_con_pdf"))
        solo_con_adjuntos = _parse_bool(self.request.query_params.get("solo_con_adjuntos"))

        ordering = self.request.query_params.get("ordering", "")

        return filter_admin_publicaciones_queryset(
            admin_publicaciones_base_queryset(),
            q=q,
            tipo=tipo,
            usuario_objetivo_id=usuario_objetivo_id,
            autor_objetivo_id=autor_objetivo_id,
            admin_registrador_id=admin_registrador_id,
            facultad_id=facultad_id,
            carrera_id=carrera_id,
            anio=anio,
            solo_delegadas=solo_delegadas,
            solo_con_pdf=solo_con_pdf,
            solo_con_adjuntos=solo_con_adjuntos,
            ordering=ordering,
        )

    def get_serializer_class(self):
        if self.action == "list":
            return AdminPublicacionListadoSerializer

        if self.action == "retrieve":
            return AdminPublicacionDetalleSerializer

        if self.action in ("update", "partial_update"):
            return PublicacionActualizacionSerializer

        return AdminPublicacionListadoSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        return Response(
            {
                "detail": (
                    "Use los endpoints específicos de creación delegada: "
                    "articulos/crear, ponencias/crear, libros/crear o capitulos/crear."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def _build_plain_data(self, request):
        source = request.data
        data = {}

        if hasattr(source, "lists"):
            for key, values in source.lists():
                if len(values) == 0:
                    data[key] = ""
                elif len(values) == 1:
                    data[key] = values[0]
                else:
                    data[key] = values
        else:
            data = dict(source)

        if "archivo_pdf" in request.FILES:
            data["archivo_pdf"] = request.FILES["archivo_pdf"]

        return data

    def _default_nombre_from_file(self, uploaded_file):
        raw_name = str(getattr(uploaded_file, "name", "") or "").strip()

        if not raw_name:
            return "Archivo PDF"

        base, _ext = os.path.splitext(raw_name)
        base = str(base or "").strip()

        return base or raw_name or "Archivo PDF"

    def _extract_files(self, request):
        files = []

        if hasattr(request.FILES, "getlist"):
            files = request.FILES.getlist("files") or request.FILES.getlist("archivos")

        return [f for f in files if f]

    def _parse_meta_json(self, raw_meta):
        if raw_meta in (None, "", [], {}, "[]", "null", "None"):
            return []

        if isinstance(raw_meta, list):
            if len(raw_meta) == 1 and isinstance(raw_meta[0], str):
                raw_meta = raw_meta[0]
            elif all(isinstance(item, dict) for item in raw_meta):
                return raw_meta
            else:
                return None

        if isinstance(raw_meta, str):
            raw = raw_meta.strip()

            if not raw or raw in ("[]", "null", "None"):
                return []

            try:
                parsed = json.loads(raw)
            except Exception:
                return None

            if parsed is None:
                return []

            if not isinstance(parsed, list):
                return None

            return parsed

        return None

    def _normalize_adjuntos_payload(self, request, plain_data):
        files = self._extract_files(request)

        if not files:
            return []

        if len(files) > MAX_ADJUNTOS_POR_PUBLICACION_ADMIN:
            raise AdminPublicacionesServiceError(
                {
                    "archivos": [
                        f"Solo se permiten {MAX_ADJUNTOS_POR_PUBLICACION_ADMIN} adjuntos por publicación."
                    ]
                }
            )

        raw_meta = plain_data.get("meta") or plain_data.get("archivos_meta") or ""
        meta_list = self._parse_meta_json(raw_meta)

        if meta_list is None:
            raise AdminPublicacionesServiceError(
                {"meta": ["Formato inválido. Debe ser JSON válido."]}
            )

        if meta_list and len(meta_list) != len(files):
            raise AdminPublicacionesServiceError(
                {
                    "detail": (
                        "La cantidad de metadatos debe coincidir con la cantidad "
                        "de archivos adjuntos."
                    )
                }
            )

        if not meta_list:
            normalized = []

            for index, uploaded_file in enumerate(files, start=1):
                normalized.append(
                    {
                        "file": uploaded_file,
                        "nombre": self._default_nombre_from_file(uploaded_file),
                        "orden": index,
                    }
                )

            return normalized

        normalized = []

        for index, uploaded_file in enumerate(files, start=1):
            item = meta_list[index - 1]

            if not isinstance(item, dict):
                raise AdminPublicacionesServiceError(
                    {"meta": [f"El adjunto #{index} debe ser un objeto JSON."]}
                )

            nombre = str(item.get("nombre") or "").strip()

            if not nombre:
                nombre = self._default_nombre_from_file(uploaded_file)

            orden = item.get("orden")

            if orden in (None, "", 0):
                orden = index

            try:
                orden = int(orden)
            except Exception:
                raise AdminPublicacionesServiceError(
                    {"meta": [f"El 'orden' del adjunto #{index} debe ser numérico."]}
                )

            if orden < 1:
                raise AdminPublicacionesServiceError(
                    {"meta": [f"El 'orden' del adjunto #{index} debe ser >= 1."]}
                )

            normalized.append(
                {
                    "file": uploaded_file,
                    "nombre": nombre,
                    "orden": orden,
                }
            )

        ordenes = [item["orden"] for item in normalized]

        if len(ordenes) != len(set(ordenes)):
            raise AdminPublicacionesServiceError(
                {"meta": ["No se permite repetir el campo 'orden' en adjuntos."]}
            )

        return sorted(normalized, key=lambda item: item["orden"])

    def _apply_target_defaults(self, data, usuario_objetivo, *, tipo_creacion):
        output = data.copy()

        if not output.get("facultad") and getattr(usuario_objetivo, "facultad_id", None):
            output["facultad"] = usuario_objetivo.facultad_id

        if not output.get("carrera") and getattr(usuario_objetivo, "carrera_id", None):
            output["carrera"] = usuario_objetivo.carrera_id

        return output

    def _serialize_created_publicacion(self, publicacion):
        instance = admin_publicaciones_base_queryset().get(pk=publicacion.pk)

        return AdminPublicacionDetalleSerializer(
            instance,
            context=self.get_serializer_context(),
        ).data

    def _resolve_publicacion_title(self, publicacion):
        titulo = str(getattr(publicacion, "titulo_admin", "") or "").strip()

        if titulo:
            return titulo

        articulo = getattr(publicacion, "articulo", None)
        ponencia = getattr(publicacion, "ponencia", None)
        libro = getattr(publicacion, "libro", None)
        capitulo = getattr(publicacion, "capitulo_libro", None)
        proyecto = getattr(publicacion, "proyecto", None)

        for value in (
            getattr(articulo, "nombre_articulo", None),
            getattr(ponencia, "nombre_ponencia", None),
            getattr(libro, "nombre_libro", None),
            getattr(capitulo, "nombre_capitulo", None),
            getattr(proyecto, "nombre", None),
        ):
            value = str(value or "").strip()
            if value:
                return value

        tipo_nombre = getattr(getattr(publicacion, "tipo", None), "nombre", None) or "Publicación"
        numero = publicacion.numero if getattr(publicacion, "numero", None) is not None else publicacion.pk

        return f"{tipo_nombre} #{numero}"

    def _delete_publicacion_adjuntos(self, publicacion):
        adjuntos = (
            PublicacionArchivo.objects
            .filter(publicacion_id=publicacion.pk)
            .order_by("orden", "id")
        )

        for adjunto in adjuntos:
            adjunto.delete()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = AdminPublicacionDetalleSerializer(
            instance,
            context=self.get_serializer_context(),
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = PublicacionActualizacionSerializer(
            instance=instance,
            data=request.data,
            partial=False,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        instance = admin_publicaciones_base_queryset().get(pk=instance.pk)

        read_serializer = AdminPublicacionDetalleSerializer(
            instance,
            context=self.get_serializer_context(),
        )

        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = PublicacionActualizacionSerializer(
            instance=instance,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        instance = admin_publicaciones_base_queryset().get(pk=instance.pk)

        read_serializer = AdminPublicacionDetalleSerializer(
            instance,
            context=self.get_serializer_context(),
        )

        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        payload = {
            "id": instance.pk,
            "titulo": self._resolve_publicacion_title(instance),
            "usuario_objetivo_id": getattr(instance, "usuario_creador_id", None),
            "admin_registrador_id": getattr(instance, "admin_registrador_id", None),
            "registrado_por_admin": bool(getattr(instance, "registrado_por_admin", False)),
        }

        self._delete_publicacion_adjuntos(instance)
        instance.delete()

        return Response(
            {
                "message": "Publicación eliminada correctamente.",
                "publicacion_eliminada": payload,
            },
            status=status.HTTP_200_OK,
        )

    def _crear_adjuntos_publicacion(self, *, publicacion, adjuntos):
        if not adjuntos:
            return []

        adjunto_objs = []

        for item in adjuntos:
            adjunto_objs.append(
                PublicacionArchivo(
                    publicacion=publicacion,
                    nombre=item["nombre"],
                    orden=item["orden"],
                    archivo=item["file"],
                )
            )

        for adjunto in adjunto_objs:
            adjunto.full_clean()

        created = []

        for adjunto in adjunto_objs:
            adjunto.save()
            created.append(adjunto)

        return created

    @transaction.atomic
    def _crear_delegada(self, request, *, serializer_class, tipo_creacion, label_ok):
        plain_data = self._build_plain_data(request)

        try:
            prepared_data, usuario_objetivo, autor_objetivo = prepare_admin_publicacion_payload(
                raw_data=plain_data
            )
            prepared_data = self._apply_target_defaults(
                prepared_data,
                usuario_objetivo,
                tipo_creacion=tipo_creacion,
            )
            adjuntos = self._normalize_adjuntos_payload(request, plain_data)

        except AdminPublicacionesServiceError as exc:
            return Response(exc.detail, status=exc.status_code)

        serializer = serializer_class(
            data=prepared_data,
            context={
                "request": request,
                "usuario_creador_override": usuario_objetivo,
                "admin_registrador": request.user,
                "registrado_por_admin": True,
            },
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.save()
        publicacion = obj.publicacion

        try:
            created_adjuntos = self._crear_adjuntos_publicacion(
                publicacion=publicacion,
                adjuntos=adjuntos,
            )
        except DjangoValidationError as exc:
            return Response(
                _django_validation_to_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            "message": label_ok,
            "usuario_objetivo": {
                "id": usuario_objetivo.id,
                "nombre": f"{usuario_objetivo.nombres or ''} {usuario_objetivo.apellidos or ''}".strip(),
                "email": usuario_objetivo.email,
            },
            "autor_objetivo": {
                "id": autor_objetivo.id,
                "nombre": f"{autor_objetivo.nombres or ''} {autor_objetivo.apellidos or ''}".strip(),
            },
            "publicacion": self._serialize_created_publicacion(publicacion),
            "adjuntos": {
                "total": len(created_adjuntos),
            },
        }

        return Response(payload, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="articulos/crear")
    def crear_articulo(self, request):
        return self._crear_delegada(
            request,
            serializer_class=ArticuloRegistroSerializer,
            tipo_creacion="articulo",
            label_ok="Artículo delegado registrado correctamente.",
        )

    @action(detail=False, methods=["post"], url_path="libros/crear")
    def crear_libro(self, request):
        return self._crear_delegada(
            request,
            serializer_class=LibroRegistroSerializer,
            tipo_creacion="libro",
            label_ok="Libro delegado registrado correctamente.",
        )

    @action(detail=False, methods=["post"], url_path="capitulos/crear")
    def crear_capitulo(self, request):
        return self._crear_delegada(
            request,
            serializer_class=CapituloLibroRegistroSerializer,
            tipo_creacion="capitulo",
            label_ok="Capítulo delegado registrado correctamente.",
        )

    @action(detail=False, methods=["post"], url_path="ponencias/crear")
    def crear_ponencia(self, request):
        return self._crear_delegada(
            request,
            serializer_class=PonenciaRegistroSerializer,
            tipo_creacion="ponencia",
            label_ok="Ponencia delegada registrada correctamente.",
        )