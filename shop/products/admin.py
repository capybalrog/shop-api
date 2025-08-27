from django.contrib import admin

from .models import (
    Category,
    Product,
    SubCategory
)
from products.utils import get_image_preview


class CategoryAdminMixin:
    """Миксин для категорий и подкатегорий."""

    list_display = ('name', 'slug', 'image_preview')
    search_fields = ('name', 'slug')

    @admin.display(description='Изображение')
    def image_preview(self, obj):
        return get_image_preview(obj, field_name='image')


@admin.register(Category)
class CategoryAdmin(CategoryAdminMixin, admin.ModelAdmin):
    """Админка для категорий."""


@admin.register(SubCategory)
class SubCategoryAdmin(CategoryAdminMixin, admin.ModelAdmin):
    """Админка для подкатегорий."""

    list_display = ('name', 'slug', 'image_preview', 'category')
    search_fields = ('name', 'slug', 'category__name')
    list_filter = ('category',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для продуктов."""

    list_display = (
        'name',
        'slug',
        'image_preview',
        'base_category',
        'subcategory',
        'price'
    )
    search_fields = (
        'name',
        'slug',
        'subcategory__name',
        'subcategory__category__name'
    )
    list_filter = (
        'subcategory',
        'subcategory__category'
    )

    @admin.display(description='Изображение')
    def image_preview(self, obj):
        return get_image_preview(obj, field_name='image_medium')

    @admin.display(description='Категория')
    def base_category(self, obj):
        if obj.subcategory:
            return obj.subcategory.category

    def get_queryset(self, request):
        return super().get_queryset(
            request
        ).select_related('subcategory')
