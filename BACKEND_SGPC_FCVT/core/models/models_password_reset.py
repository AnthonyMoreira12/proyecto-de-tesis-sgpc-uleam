from datetime import timedelta
import hashlib
import secrets

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "password_reset_tokens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "used_at"],
            ),
            models.Index(
                fields=["created_at"],
            ),
        ]

    def is_expired(self):
        return (
            self.created_at
            < timezone.now() - timedelta(hours=1)
        )

    @property
    def is_used(self):
        return self.used_at is not None

    def mark_used(self, commit=True):
        if self.used_at is None:
            self.used_at = timezone.now()

            if commit:
                self.save(
                    update_fields=["used_at"]
                )

        return self

    @staticmethod
    def hash_token(raw_token):
        raw_token = str(raw_token or "")
        return hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()

    @classmethod
    def create_for_user(cls, user):
        raw_token = secrets.token_urlsafe(48)
        token_hash = cls.hash_token(raw_token)

        with transaction.atomic():
            cls.objects.select_for_update().filter(
                user=user,
                used_at__isnull=True,
            ).delete()

            cls.objects.create(
                user=user,
                token_hash=token_hash,
            )

        return raw_token

    @classmethod
    def find_valid_token(cls, raw_token):
        if not raw_token:
            return None

        token_hash = cls.hash_token(raw_token)

        token = (
            cls.objects
            .filter(
                token_hash=token_hash,
                used_at__isnull=True,
            )
            .order_by("-created_at")
            .first()
        )

        if token is None or token.is_expired():
            return None

        return token

    def __str__(self):
        status = (
            "usado"
            if self.is_used
            else (
                "expirado"
                if self.is_expired()
                else "activo"
            )
        )

        return f"Token de {self.user_id} ({status})"
