from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для юзеров."""

    actions = None

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
        'id'
    )
    search_fields = (
        'email',
        'username',
    )
    list_filter = (
        'role',
    )


admin.site.unregister(Group)
