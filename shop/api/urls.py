from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CartViewSet,
    product_redirect,
    ProductViewSet,
    UserViewSet,
)


router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('products', ProductViewSet, basename='products')
router.register('cart', CartViewSet, basename='cart')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'categories/'
        '<slug:category_slug>/'
        '<slug:subcategory_slug>/'
        '<slug:product_slug>/',
        product_redirect,
        name='product-redirect'
    ),
    path('', include(router.urls)),
]
