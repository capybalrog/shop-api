from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from users.consts import ADMIN, ERRORS, MAGIC_NUMBERS, USER_ROLES


class User(AbstractUser):
    """
    Модель пользователя.

    Кроме базовых полей, добавлены поля:
    - role (админ или юзер)
    """

    role = models.CharField(
        'Роль',
        choices=USER_ROLES,
        default='user',
    )

    @property
    def is_admin(self):
        """Проверка на админа."""
        return self.role == ADMIN

    def clean(self):
        """Проверяет, валидна ли роль."""
        super().clean()
        if self.role not in dict(USER_ROLES):
            raise ValidationError(
                {'role': ERRORS['role']['wrong']}
            )

    def save(self, *args, **kwargs):
        """
        Сохраняет пользователя.

        Если это суперпользователь,
        и его роль не админ,
        то роль меняется на админа.
        """
        if self.is_superuser and self.role != ADMIN:
            self.role = ADMIN
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:MAGIC_NUMBERS['count']['truncated_str']]
