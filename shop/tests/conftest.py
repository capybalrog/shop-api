import os

import django
import pytest

from django.conf import settings
from rest_framework.test import APIClient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
django.setup()


from products.models import (
    Cart,
    CartProduct,
    Category,
    Product,
    SubCategory
)


@pytest.fixture(scope='session')
def django_db_setup():
    """Фикстура для настройки тестовой БД."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': False
    }


@pytest.fixture
def owner(django_user_model):
    """Владелец корзины."""
    return django_user_model.objects.create(
        username='test_user',
        email='test@test.test',
        password='test12345'
    )


@pytest.fixture
def owner_client(owner):
    """Клиент для владельца."""
    owner_client = APIClient()
    owner_client.force_authenticate(owner)
    return owner_client


@pytest.fixture
def client():
    """Клиент для неавторизованного пользователя."""
    return APIClient()


@pytest.fixture
def category():
    """Категория."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category'
    )


@pytest.fixture
def subcategory(category):
    """Подкатегория."""
    return SubCategory.objects.create(
        name='Test SubCategory',
        slug='test-subcategory',
        category=category
    )


@pytest.fixture
def product1(subcategory):
    """Товар."""
    return Product.objects.create(
        name='Test Product 1',
        slug='test-product1',
        subcategory=subcategory,
        price=100.00
    )


@pytest.fixture
def product2(subcategory):
    """Еще один товар."""
    return Product.objects.create(
        name='Test Product 2',
        slug='test-product2',
        subcategory=subcategory,
        price=100.00
    )


@pytest.fixture
def cart(owner):
    """Корзина."""
    return Cart.objects.create(user=owner)


@pytest.fixture
def cart_product(cart, product1):
    """Товар в корзине."""
    return CartProduct.objects.create(
        cart=cart,
        product=product1,
        quantity=2
    )
