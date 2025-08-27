import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK as OK,
    HTTP_201_CREATED as CREATED,
    HTTP_204_NO_CONTENT as NO_CONTENT,
    HTTP_400_BAD_REQUEST as BAD_REQUEST,
    HTTP_401_UNAUTHORIZED as UNAUTHORIZED,
)

from products.models import CartProduct


pytestmark = pytest.mark.django_db


def assert_empty(cart_response):
    """Вспомогательная функция для проверки пустой корзины."""
    assert cart_response.data['total_quantity'] == 0
    assert cart_response.data['total_price'] == '0.00'
    assert len(cart_response.data['products']) == 0


def test_get_empty_cart(owner_client):
    """Авторизованный пользователь получает корзину."""
    url = reverse('cart-list')
    response = owner_client.get(url)

    assert response.status_code == OK
    assert_empty(response)


def test_get_cart_with_no_auth(client):
    """Неавторизованный пользователь стучится в корзину."""
    url = reverse('cart-list')
    response = client.get(url)

    assert response.status_code == UNAUTHORIZED


def test_add_product_to_cart(owner_client, product1):
    """Пользователь добавляет товар в корзину."""
    cart_url = reverse('cart-list')
    initial_response = owner_client.get(cart_url)
    assert_empty(initial_response)

    add_url = reverse(
        'products-to-cart',
        kwargs={'slug': product1.slug}
    )
    data = {'quantity': 2}
    response = owner_client.post(add_url, data)

    assert response.status_code == CREATED
    cart_response = owner_client.get(cart_url)

    assert cart_response.status_code == OK
    assert cart_response.data['total_quantity'] == 2
    assert cart_response.data['total_price'] == '200.00'
    assert len(cart_response.data['products']) == 1
    assert cart_response.data[
        'products'
    ][0]['product']['slug'] == product1.slug
    assert cart_response.data['products'][0]['quantity'] == 2


def test_update_cart_item_quantity(owner_client, cart_product):
    """Пользователь обновляет количество товара в корзине."""
    url = reverse(
        'cart-detail',
        kwargs={'pk': cart_product.id}
    )
    data = {'quantity': 5}
    response = owner_client.put(url, data)

    assert response.status_code == OK

    cart_url = reverse('cart-list')
    cart_response = owner_client.get(cart_url)

    assert cart_response.status_code == OK
    assert cart_response.data['total_quantity'] == 5
    assert cart_response.data['total_price'] == '500.00'
    assert cart_response.data['products'][0]['quantity'] == 5


def test_wrong_item_quantity(owner_client, cart_product):
    """Пользователь указывает неверное количество товара."""
    url = reverse(
        'cart-detail',
        kwargs={'pk': cart_product.id}
    )
    data = {'quantity': -1}
    response = owner_client.put(url, data)

    assert response.status_code == BAD_REQUEST


def test_remove_product_from_cart(owner_client, cart_product):
    """Пользователь удаляет товар из корзины."""
    url = reverse(
        'cart-detail',
        kwargs={'pk': cart_product.id}
    )
    response = owner_client.delete(url)

    assert response.status_code == NO_CONTENT

    cart_url = reverse('cart-list')
    cart_response = owner_client.get(cart_url)

    assert_empty(cart_response)


def test_update_quantity_to_zero_removes_item(owner_client, cart_product):
    """
    Пользователь указывает 0 в количестве товара.

    При этом товар удаляется из корзины.
    """
    url = reverse('cart-detail', kwargs={'pk': cart_product.id})
    data = {'quantity': 0}

    response = owner_client.put(url, data)

    assert response.status_code == NO_CONTENT

    cart_url = reverse('cart-list')
    cart_response = owner_client.get(cart_url)

    assert_empty(cart_response)


def test_clear_cart(owner_client, cart, cart_product, product2):
    """Пользователь очищает корзину."""
    CartProduct.objects.create(
        cart=cart,
        product=product2,
        quantity=3
    )

    cart_url = reverse('cart-list')
    cart_response_before = owner_client.get(cart_url)
    assert cart_response_before.data['total_quantity'] == 5
    assert len(cart_response_before.data['products']) == 2

    delete_url = reverse('cart-clear')
    response = owner_client.delete(delete_url)
    assert response.status_code == NO_CONTENT

    cart_response_after = owner_client.get(cart_url)
    assert_empty(cart_response_after)
