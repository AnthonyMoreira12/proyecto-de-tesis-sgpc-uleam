from datetime import timedelta
import hashlib
import secrets

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class PasswordResetToken(models.Model):
    # Usuario al que pertenece el token de recuperación.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )

    # Hash del token (SHA-256). Nunca se almacena el token en texto plano.
    token_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True
    )

    # Fecha de creación del token.
    created_at = models.DateTimeField(auto_now_add=True)

    # Fecha en que el token fue utilizado (null = aún válido).
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "password_reset_tokens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "used_at"]),
            models.Index(fields=["created_at"]),
        ]

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(hours=1)

    @property
    def is_used(self):
        return self.used_at is not None

    def mark_used(self, commit=True):
        self.used_at = timezone.now()
        if commit:
            self.save(update_fields=["used_at"])
        return self

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def create_for_user(cls, user):
        raw = secrets.token_urlsafe(48)
        token_hash = cls.hash_token(raw)

        with transaction.atomic():
            cls.objects.select_for_update().filter(
                user=user,
                used_at__isnull=True,
            ).delete()

            cls.objects.create(
                user=user,
                token_hash=token_hash
            )

        return raw

    @classmethod
    def find_valid_token(cls, raw_token: str):
        token_hash = cls.hash_token(raw_token)

        token = cls.objects.filter(
            token_hash=token_hash,
            used_at__isnull=True,
        ).order_by("-created_at").first()

        if not token:
            return None

        if token.is_expired():
            return None

        return token