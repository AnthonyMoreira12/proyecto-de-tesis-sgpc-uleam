"""ViewSet para consultar, registrar y administrar autores."""

import logging
import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.autores.serializers.autores_autor_serializers import AutorSerializer
from core.autores.services.autores_usuario_sync_services import (
    AutorUsuarioSyncError,
    asegurar_usuario_pendiente_para_autor,
    buscar_autor_existente,
    serializar_autor_match,
)
from core.models import Autor


logger = logging.getLogger(__name__)
User = get_user_model()

MAX_SEARCH_LENGTH = 200
CEDULA_PATTERN = re.compile(r"^\d{10}$")


def _normalize_query(value):
    return " ".join(str(value or "").split())


def _normalize_email(value):
    normalized = str(value or "").strip()
    if not normalized:
        return ""
    return User.objects.normalize_email(normalized).strip().lower()


def _parse_optional_positive_integer(value, *, field_name):
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        raise ValidationError(
            {field_name: "Debe proporcionar un identificador válido."}
        )
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError(
            {field_name: "Debe proporcionar un identificador válido."}
        ) from exc
    if parsed < 1:
        raise ValidationError(
            {field_name: "Debe proporcionar un identificador válido."}
        )
    return parsed


def _django_validation_payload(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"detail": list(exc.messages)}
    return {"detail": str(exc)}


def _is_admin_user(user):
    return bool(
        user is not None
        and (
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
        )
    )


def _has_usable_password(user):
    if user is None:
        return False
    try:
        return bool(user.has_usable_password())
    except (AttributeError, TypeError, ValueError):
        return False


def _is_pending_external_user(user):
    if user is None:
        return False
    return bool(
        str(getattr(user, "rol", "")).strip().lower() == "autor_externo"
        and str(getattr(user, "auth_source", "")).strip().lower() == "local"
        and not getattr(user, "is_active", False)
        and not _has_usable_password(user)
    )


def _author_has_scientific_relations(author):
    for relation_name in ("participaciones", "proyectos_participaciones"):
        manager = getattr(author, relation_name, None)
        if manager is not None and manager.exists():
            return True
    return False


def _empty_match_payload(*, input_incomplete=False):
    payload = serializar_autor_match(None, None)
    payload["input_incomplete"] = bool(input_incomplete)
    return payload


class AutoresViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AutorSerializer
    http_method_names = [
        "get", "post", "put", "patch", "delete", "head", "options"
    ]
    lookup_field = "pk"
    lookup_value_regex = r"\d+"

    def check_write_permission(self):
        if not _is_admin_user(self.request.user):
            raise PermissionDenied(
                "Solo un administrador puede modificar o eliminar autores."
            )

    def get_queryset(self):
        queryset = Autor.objects.select_related("usuario").all()

        search_query = _normalize_query(
            self.request.query_params.get("q")
            or self.request.query_params.get("search")
        )

        if search_query:
            if len(search_query) > MAX_SEARCH_LENGTH:
                raise ValidationError(
                    {
                        "q": (
                            "La búsqueda no puede superar "
                            f"los {MAX_SEARCH_LENGTH} caracteres."
                        )
                    }
                )

            # Cada término puede coincidir con cualquiera de los
            # campos, lo que permite buscar nombres completos.
            for term in search_query.split():
                queryset = queryset.filter(
                    Q(nombres__icontains=term)
                    | Q(apellidos__icontains=term)
                    | Q(identificacion__icontains=term)
                    | Q(correo__icontains=term)
                    | Q(institucion__icontains=term)
                    | Q(usuario__email__icontains=term)
                    | Q(usuario__identificacion__icontains=term)
                    | Q(usuario__nombres__icontains=term)
                    | Q(usuario__apellidos__icontains=term)
                )

        return queryset.order_by("apellidos", "nombres", "pk")

    def _get_locked_author(self):
        """
        Bloquea únicamente la fila de Autor. No se combina
        select_for_update() con select_related("usuario"), porque
        Autor.usuario es nullable y PostgreSQL rechaza bloquear
        el lado nullable del LEFT OUTER JOIN.
        """
        lookup_value = self.kwargs.get(self.lookup_field)
        try:
            author = Autor.objects.select_for_update().get(pk=lookup_value)
        except Autor.DoesNotExist as exc:
            raise NotFound("El autor solicitado no existe.") from exc

        self.check_object_permissions(self.request, author)
        return author

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                author = serializer.save()
                asegurar_usuario_pendiente_para_autor(author)
                created_author = Autor.objects.select_related("usuario").get(
                    pk=author.pk
                )
        except AutorUsuarioSyncError as exc:
            return Response(exc.detail, status=exc.status_code)
        except DjangoValidationError as exc:
            raise ValidationError(_django_validation_payload(exc)) from exc
        except IntegrityError as exc:
            logger.exception("Conflicto al registrar un autor externo.")
            return Response(
                {
                    "detail": (
                        "No fue posible registrar el autor por un "
                        "conflicto de cédula, correo o vínculo."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )
        except DatabaseError:
            logger.exception(
                "Error de base de datos al registrar un autor externo."
            )
            return Response(
                {
                    "detail": (
                        "No fue posible registrar el autor debido a "
                        "un error temporal de la base de datos."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        output = self.get_serializer(created_author)
        response = Response(
            output.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(output.data),
        )
        response["Cache-Control"] = "no-store"
        return response

    def update(self, request, *args, **kwargs):
        self.check_write_permission()
        partial = kwargs.pop("partial", False)

        try:
            with transaction.atomic():
                author = self._get_locked_author()
                serializer = self.get_serializer(
                    author,
                    data=request.data,
                    partial=partial,
                )
                serializer.is_valid(raise_exception=True)
                updated_author = serializer.save()

                if bool(updated_author.es_externo):
                    asegurar_usuario_pendiente_para_autor(updated_author)

                updated_author = Autor.objects.select_related("usuario").get(
                    pk=updated_author.pk
                )
        except AutorUsuarioSyncError as exc:
            return Response(exc.detail, status=exc.status_code)
        except DjangoValidationError as exc:
            raise ValidationError(_django_validation_payload(exc)) from exc
        except IntegrityError as exc:
            logger.exception("Conflicto al actualizar un autor.")
            return Response(
                {
                    "detail": (
                        "No fue posible actualizar el autor porque "
                        "los datos entran en conflicto."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )
        except DatabaseError:
            logger.exception("Error de base de datos al actualizar un autor.")
            return Response(
                {
                    "detail": (
                        "No fue posible actualizar el autor debido a "
                        "un error temporal de la base de datos."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        response = Response(self.get_serializer(updated_author).data)
        response["Cache-Control"] = "no-store"
        return response

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.check_write_permission()

        try:
            with transaction.atomic():
                author = self._get_locked_author()

                if _author_has_scientific_relations(author):
                    return Response(
                        {
                            "detail": (
                                "No se puede eliminar el autor porque "
                                "mantiene participaciones en publicaciones "
                                "o proyectos."
                            )
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                linked_user = (
                    User.objects.select_for_update()
                    .filter(pk=author.usuario_id)
                    .first()
                    if author.usuario_id
                    else None
                )

                if linked_user is not None:
                    removable_pending_user = bool(
                        _is_pending_external_user(linked_user)
                        and getattr(
                            linked_user,
                            "creado_desde_selector",
                            False,
                        )
                    )

                    if not removable_pending_user:
                        return Response(
                            {
                                "detail": (
                                    "El autor está vinculado a una cuenta "
                                    "que ya recibió acceso. Administre esa "
                                    "cuenta desde Gestión de usuarios."
                                )
                            },
                            status=status.HTTP_409_CONFLICT,
                        )

                    author.delete()
                    linked_user.delete()
                else:
                    author.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "No se puede eliminar el autor porque mantiene "
                        "información protegida relacionada."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )
        except IntegrityError:
            return Response(
                {"detail": "No se puede eliminar el autor por sus relaciones."},
                status=status.HTTP_409_CONFLICT,
            )
        except DatabaseError:
            logger.exception("Error de base de datos al eliminar un autor.")
            return Response(
                {
                    "detail": (
                        "No fue posible eliminar el autor debido a "
                        "un error temporal de la base de datos."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="validar-existencia",
        url_name="validar-existencia",
    )
    def validar_existencia(self, request):
        raw_identification = _normalize_query(
            request.query_params.get("identificacion")
        )
        raw_email = _normalize_query(request.query_params.get("correo"))
        names = _normalize_query(request.query_params.get("nombres"))
        surnames = _normalize_query(request.query_params.get("apellidos"))
        excluded_id = _parse_optional_positive_integer(
            request.query_params.get("exclude_autor_id"),
            field_name="exclude_autor_id",
        )

        for field_name, field_value in {
            "identificacion": raw_identification,
            "correo": raw_email,
            "nombres": names,
            "apellidos": surnames,
        }.items():
            if len(field_value) > MAX_SEARCH_LENGTH:
                raise ValidationError(
                    {
                        field_name: (
                            "El valor no puede superar "
                            f"los {MAX_SEARCH_LENGTH} caracteres."
                        )
                    }
                )

        identification = None
        identification_incomplete = False
        if raw_identification:
            if not raw_identification.isdigit():
                raise ValidationError(
                    {"identificacion": "La cédula solo puede contener números."}
                )
            if len(raw_identification) > 10:
                raise ValidationError(
                    {
                        "identificacion": (
                            "La cédula debe contener exactamente "
                            "10 dígitos numéricos."
                        )
                    }
                )
            if CEDULA_PATTERN.fullmatch(raw_identification):
                identification = raw_identification
            else:
                identification_incomplete = True

        email = None
        email_incomplete = False
        if raw_email:
            normalized_email = _normalize_email(raw_email)
            try:
                validate_email(normalized_email)
            except DjangoValidationError:
                email_incomplete = True
            else:
                email = normalized_email

        names_ready = bool(
            names and surnames and len(names) >= 2 and len(surnames) >= 2
        )
        names_incomplete = bool(names or surnames) and not names_ready

        if not any((identification, email, names_ready)):
            response = Response(
                _empty_match_payload(
                    input_incomplete=(
                        identification_incomplete
                        or email_incomplete
                        or names_incomplete
                    )
                )
            )
            response["Cache-Control"] = "no-store"
            return response

        found = buscar_autor_existente(
            identificacion=identification,
            correo=email,
            nombres=names if names_ready else "",
            apellidos=surnames if names_ready else "",
            exclude_autor_id=excluded_id,
        )

        response = Response(
            serializar_autor_match(
                found.get("autor"),
                found.get("match_type"),
            )
        )
        response["Cache-Control"] = "no-store"
        return response