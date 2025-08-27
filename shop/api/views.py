from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated
)
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK as OK,
    HTTP_201_CREATED as CREATED,
    HTTP_204_NO_CONTENT as NO_CONTENT,
)
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet
)

from api.permissions import (
    CartPermission,
)
from api.serializers import (
    CartSerializer,
    CartProductSerializer,
    CartProductUpdateSerializer,
    CategorySerializer,
    CategoryWithSubcategoriesSerializer,
    ProductSerializer,
    SubCategorySerializer,
    SubCategoryWithProductsSerializer,
    UserSignUpSerializer
)
from api.utils import paginated_response
from products.models import (
    Cart,
    CartProduct,
    Category,
    Product,
    SubCategory
)


class UserViewSet(
    CreateModelMixin,
    GenericViewSet
):
    """Вьюсет для регистрации пользователей."""

    serializer_class = UserSignUpSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        """Создание пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            status=CREATED
        )


class CategoryViewSet(ReadOnlyModelViewSet):
    """
    Категории с подкатегориями.

    - GET /categories/
        - список категорий
    - GET /categories/{slug}/
        - категория с подкатегориями
    - GET /categories/{category_slug}/{subcategory_slug}/
        - подкатегория с продуктами
    """

    queryset = Category.objects.prefetch_related(
        'subcategories'
    ).all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryWithSubcategoriesSerializer
        return CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        """Категория с подкатегориями."""
        instance = self.get_object()
        return paginated_response(
            instance.subcategories.all(),
            request,
            SubCategorySerializer
        )

    @action(detail=True,
        methods=['get'],
        url_path='(?P<subcategory_slug>[^/.]+)'
    )
    def subcategory_products(
            self,
            request,
            slug=None,
            subcategory_slug=None
    ):
        """Подкатегория с продуктами."""
        category = get_object_or_404(
            Category,
            slug=slug,
        )
        subcategory = get_object_or_404(
            SubCategory,
            category=category,
            slug=subcategory_slug
        )

        return paginated_response(
            subcategory.products.all(),
            request,
            ProductSerializer
        )


class ProductViewSet(ReadOnlyModelViewSet):
    """
    Информация о продуктах.

    - GET /products/
        - список продуктов
    - GET /products/{slug}/
        - детальная информация о продукте
    - POST /products/{slug}/to_cart/
        - добавить товар в корзину
    """

    queryset = Product.objects.select_related(
        'subcategory',
        'subcategory__category'
    ).all()
    serializer_class = ProductSerializer
    search_fields = (
        'name',
        'subcategory__name',
        'subcategory__category__name'
    )
    filterset_fields = (
        'subcategory__category__slug',
        'subcategory__slug'
    )
    lookup_field = 'slug'

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def to_cart(self, request, slug=None):
        """Добавить товар в корзину."""
        product = get_object_or_404(Product, slug=slug)
        cart, created = Cart.objects.get_or_create(user=request.user)

        if request.method == 'POST':
            quantity = int(request.data.get('quantity', 1))
            cart_item, created = CartProduct.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(status=CREATED)

        cart_item = get_object_or_404(
            CartProduct, cart=cart,
            product=product
        )
        cart_item.delete()
        return Response(status=NO_CONTENT)


class CartViewSet(ModelViewSet):
    """
    Управление корзиной.

    - GET /cart/
        - получить корзину
    - PUT /cart/{item_id}/
        - изменить количество товара
    - DELETE /cart/{item_id}/
        - удалить товар из корзины
    - DELETE /cart/clear/
        - очистить корзину
    """

    permission_classes = (
        IsAuthenticated,
        CartPermission
    )
    serializer_class = CartProductSerializer

    def get_cart(self):
        cart, created = Cart.objects.get_or_create(
            user=self.request.user
        )
        return cart

    def get_queryset(self):
        return CartProduct.objects.filter(
            cart__user=self.request.user
        ).select_related(
            'product'
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return CartSerializer
        return CartProductUpdateSerializer

    def list(self, request, *args, **kwargs):
        """Список товаров в корзине."""
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response(
            serializer.data,
            status=OK
        )

    def update(self, request, *args, pk=None):
        """Изменить количество товара."""
        cart_product = get_object_or_404(
            CartProduct,
            id=pk
        )
        serializer = CartProductUpdateSerializer(
            cart_product,
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data.get('quantity')
        if quantity == 0:
            cart_product.delete()
            return Response(status=NO_CONTENT)

        serializer.save()
        return Response(
            status=OK,
        )

    def destroy(self, request, *args, pk=None):
        """Удалить товар из корзины."""
        cart_product = get_object_or_404(
            CartProduct,
            id=pk
        )
        cart_product.delete()

        return Response(status=NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Очистить корзину."""
        cart = self.get_cart()
        deleted_count, _ = cart.cart_products.all().delete()

        return Response(status=NO_CONTENT)


def product_redirect(
        request,
        category_slug,
        subcategory_slug,
        product_slug
):
    """Перенаправление на товар из подкатегории."""
    product = get_object_or_404(
        Product,
        slug=product_slug,
        subcategory__slug=subcategory_slug,
        subcategory__category__slug=category_slug
    )
    return redirect(f'/api/{product.short_url}')
