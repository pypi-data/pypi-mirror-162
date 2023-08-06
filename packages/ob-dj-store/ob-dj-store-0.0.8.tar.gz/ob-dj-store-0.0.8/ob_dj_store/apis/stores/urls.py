from django.conf.urls import include
from django.urls import path
from rest_framework_nested import routers

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

# from ob_dj_store.utils.drf.routers import CustomRouter

app_name = "stores"

router = routers.SimpleRouter()
router.register(r"stores", StoreView)

stores_router = routers.NestedSimpleRouter(router, r"stores", lookup="store")
stores_router.register(r"cart", CartView, basename="cart")
stores_router.register(r"order", OrderView, basename="order")
stores_router.register(r"product", ProductView, basename="product")
stores_router.register(r"variant", VariantView, basename="variant")
stores_router.register(r"inventory", InventoryView, basename="inventory")
router.register(r"category", CategoryViewSet, basename="category")
stores_router.register(r"transaction", TransactionsViewSet, basename="transaction")


urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(stores_router.urls)),
]
