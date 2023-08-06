from django.conf.urls import include
from django.urls import path

from ob_dj_store.apis.stores.views import (
    CartView,
    CategoryViewSet,
    InventoryView,
    OrderView,
    ProductView,
    StoreView,
    TransactionsViewSet,
    VariantView,
)
from ob_dj_store.utils.drf.routers import CustomRouter

app_name = "stores"

router = CustomRouter(trailing_slash=False)

router.register(r"", StoreView, basename="store")
router.register(r"cart", CartView, basename="cart")
router.register(r"order", OrderView, basename="order")
router.register(r"product", ProductView, basename="product")
router.register(r"variant", VariantView, basename="variant")
router.register(r"inventory", InventoryView, basename="inventory")
router.register(r"category", CategoryViewSet, basename="category")
router.register(r"transaction", TransactionsViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
]
