from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers

from products.models import (
    Cart,
    CartProduct,
    Category,
    Product,
    SubCategory
)
from users.consts import ERRORS, MAGIC_NUMBERS


User = get_user_model()


class UserSignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password'
        )
        write_only_fields = ('password',)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError(
                {
                    'email':
                        [ERRORS['email']['exists']]
                }
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError(
                {
                    'username':
                        [ERRORS['username']['exists']]
                }
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class BaseCategorySerializer(serializers.ModelSerializer):
    """Базовый сериализатор для категорий и подкатегорий."""

    class Meta:
        fields = [
            'id',
            'name',
            'slug',
            'image',
        ]
        read_only_fields = fields

    def get_image_url(self, obj):
        return obj.image.url if obj.image.url else None


class CategorySerializer(BaseCategorySerializer):
    """Сериализатор для категорий."""

    class Meta(BaseCategorySerializer.Meta):
        model = Category


class SubCategorySerializer(BaseCategorySerializer):
    """Сериализатор для подкатегорий."""

    category = CategorySerializer(read_only=True)

    class Meta(BaseCategorySerializer.Meta):
        model = SubCategory
        fields = BaseCategorySerializer.Meta.fields + ['category']
        read_only_fields = fields


class CategoryWithSubcategoriesSerializer(
    BaseCategorySerializer
):
    """Сериализатор для категорий с подкатегориями."""

    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta(BaseCategorySerializer.Meta):
        model = Category
        fields = BaseCategorySerializer.Meta.fields + [
            'subcategories'
        ]
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для товаров."""

    category = serializers.CharField(
        source='subcategory.category.name',
        read_only=True
    )
    subcategory = SubCategorySerializer(read_only=True)
    product_url = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'price',
            'category',
            'image_small',
            'subcategory',
            'image_medium',
            'image_large',
            'product_url'
        )
        read_only_fields = fields

    def get_product_url(self, obj):
        return obj.short_url


class SubCategoryWithProductsSerializer(SubCategorySerializer):
    """Сериализатор для подкатегорий с товарами."""

    products = ProductSerializer(many=True, read_only=True)

    class Meta(SubCategorySerializer.Meta):
        model = Category
        fields = SubCategorySerializer.Meta.fields + [
            'products'
        ]
        read_only_fields = fields


class CartProductSerializer(serializers.ModelSerializer):
    """Сериализатор для товаров в корзине."""

    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=MAGIC_NUMBERS['count']['max_decimal_digits'],
        decimal_places=MAGIC_NUMBERS['count']['max_decimal_places'],
        read_only=True
    )

    class Meta:
        model = CartProduct
        fields = (
            'id',
            'product',
            'quantity',
            'total_price'
        )


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины."""

    products = CartProductSerializer(many=True, source='cart_products')
    total_quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=MAGIC_NUMBERS['count']['max_decimal_digits'],
        decimal_places=MAGIC_NUMBERS['count']['max_decimal_places'],
        read_only=True
    )

    class Meta:
        model = Cart
        fields = (
            'id',
            'products',
            'total_quantity',
            'total_price',
            'updated_at'
        )


class CartProductUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения количества товара в корзине."""

    class Meta:
        model = CartProduct
        fields = ('quantity',)

    def validate_quantity(self, value):
        if value < 0:
            raise ValidationError(
                ERRORS['quantity']['less_than_zero']
            )
        return value
