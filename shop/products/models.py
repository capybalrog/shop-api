from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, F
from django.utils.text import slugify

from users.consts import MAGIC_NUMBERS


User = get_user_model()


class CategoryBase(models.Model):
    """
    Базовый класс для категорий и подкатегорий.

    Поля:
        name - название категории
        slug - уникальный слаг категории
        image - изображение категории
    """

    name = models.CharField(
        'Название',
        unique=True,
        max_length=MAGIC_NUMBERS['count']['max_length']
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=MAGIC_NUMBERS['count']['max_length']
    )
    image = models.ImageField(
        'Изображение',
        upload_to='categories/',
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name[:MAGIC_NUMBERS['count']['truncated_str']]


class Category(CategoryBase):
    """Основная категория."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)


class SubCategory(CategoryBase):
    """Подкатегория."""

    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='subcategories',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ('name',)


class Product(models.Model):
    """
    Продукт.

    Поля:
        name - название продукта
        slug - уникальный слаг продукта
        subcategory - подкатегория, к которой относится продукт
        image_small - маленькое изображение продукта
        image_medium - среднее изображение продукта
        image_large - большое изображение продукта
        price - цена продукта
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=MAGIC_NUMBERS['count']['max_length']
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=MAGIC_NUMBERS['count']['max_length']
    )
    subcategory = models.ForeignKey(
        SubCategory,
        verbose_name='Подкатегория',
        on_delete=models.CASCADE,
        related_name='products'
    )
    image_small = models.ImageField(
        'Изображение (маленькое)',
        upload_to='products/small/',
        null=True,
        blank=True,
        default=None
    )
    image_medium = models.ImageField(
        'Изображение (среднее)',
        upload_to='products/medium/',
        null=True,
        blank=True,
        default=None
    )
    image_large = models.ImageField(
        'Изображение (большое)',
        upload_to='products/large/',
        null=True,
        blank=True,
        default=None
    )
    price = models.DecimalField(
        'Цена',
        max_digits=MAGIC_NUMBERS['count']['max_decimal_digits'],
        decimal_places=MAGIC_NUMBERS['count']['max_decimal_places']
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    @property
    def category(self):
        return self.subcategory.category

    @property
    def short_url(self):
        return f'products/{self.slug}/'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name[:MAGIC_NUMBERS['count']['truncated_str']]


class Cart(models.Model):
    """
    Корзина пользователя.

    Поля:
        user - пользователь, который добавил товар в корзину
        created_at - дата создания корзины
        products - список продуктов в корзине
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField(
        Product,
        verbose_name='Товары',
        through='CartProduct',
        related_name='carts'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    @property
    def total_quantity(self):
        """Общее количество товаров в корзине."""
        return self.cart_products.aggregate(
            total=Sum('quantity')
        )['total'] or 0

    @property
    def total_price(self):
        """Общая стоимость товаров в корзине."""
        result = self.cart_products.annotate(
            item_total=F('quantity') * F('product__price')
        ).aggregate(
            total=Sum('item_total')
        )['total']
        return result if result else 0

    def __str__(self):
        return f'Корзина пользователя {self.user.username}'


class CartProduct(models.Model):
    """
    Товар в корзине.

    Поля:
        cart - корзина пользователя
        product - продукт
        quantity - количество
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='cart_products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_products'
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.cart.user.username} - {self.product.name}'
