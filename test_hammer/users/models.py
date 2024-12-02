from django.contrib.auth.models import AbstractUser
from django.db import models

from .utils import generate_code


class CustomerUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    unique_invite_code = models.CharField(max_length=6, unique=True)
    invited_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='invited_users'  # Обратная связь для получения списка приглашенных
    )

    username = models.CharField(max_length=1)
    email = models.CharField(max_length=1)

    USERNAME_FIELD = 'phone'

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        if not self.unique_invite_code:
            while True:  # Перестраховка если код выпал неуникальный
                try:
                    self.unique_invite_code = generate_code(length=6)
                    break
                except Exception:
                    continue
        super().save(*args, **kwargs)
