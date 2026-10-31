from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CompositionViewSet,
    DeliveryViewSet,
    ProductViewSet,
    PurchaseViewSet,
    RatingViewSet,
    SupplierViewSet,
    UserViewSet,
    health_check,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"compositions", CompositionViewSet, basename="composition")
router.register(r"users", UserViewSet, basename="user")
router.register(r"ratings", RatingViewSet, basename="rating")
router.register(r"deliveries", DeliveryViewSet, basename="delivery")
router.register(r"purchases", PurchaseViewSet, basename="purchase")

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("", include(router.urls)),
]
