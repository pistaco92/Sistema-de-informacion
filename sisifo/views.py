import duckdb
from django.core.cache import cache
from django.db import connection
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    Category,
    Composition,
    Delivery,
    Product,
    Purchase,
    Rating,
    Supplier,
    User,
)
from .serializers import (
    CategorySerializer,
    CompositionSerializer,
    DeliverySerializer,
    ProductSerializer,
    PurchaseSerializer,
    RatingSerializer,
    SupplierSerializer,
    UserSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["category_id", "name"]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["supplier_id", "name"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category", "supplier").all()
    serializer_class = ProductSerializer
    filterset_fields = ["category", "supplier", "price", "stock", "guarantee"]
    search_fields = ["name", "info"]
    ordering_fields = ["product_id", "name", "price", "stock", "guarantee"]


class CompositionViewSet(viewsets.ModelViewSet):
    queryset = Composition.objects.select_related("parent", "component").all()
    serializer_class = CompositionSerializer
    filterset_fields = ["parent", "component", "amount"]
    ordering_fields = ["parent", "component", "amount"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ["role", "purchases", "distance"]
    search_fields = ["name", "role"]
    ordering_fields = ["user_id", "name", "purchases", "distance"]


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.select_related("product", "user").all()
    serializer_class = RatingSerializer
    filterset_fields = ["product", "user", "score"]
    search_fields = ["comment"]
    ordering_fields = ["product", "user", "score"]


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.select_related("customer").all()
    serializer_class = DeliverySerializer
    filterset_fields = ["customer", "pay_method", "state"]
    search_fields = ["pay_method", "state"]
    ordering_fields = [
        "delivery_id",
        "datetime",
        "est_delivery_time",
        "real_delivery_time",
    ]


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.select_related("delivery", "product").all()
    serializer_class = PurchaseSerializer
    filterset_fields = ["delivery", "product", "amount"]
    ordering_fields = ["id", "delivery", "product", "amount"]


@api_view(["GET"])
def health_check(request):
    """Verifica el estado de DuckDB y Redis dentro del Pod."""
    status = {"django": "ok", "duckdb": "error", "redis": "error"}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.execute("SHOW TABLES")
            tables = [r[0] for r in cursor.fetchall()]
        status["duckdb"] = {
            "status": "ok",
            "version": version,
            "database": connection.settings_dict["NAME"],
            "tables": tables,
        }
    except Exception as exc:
        status["duckdb"] = {"status": "error", "detail": str(exc)}

    try:
        cache.set("sisifo_healthcheck", "ok", timeout=30)
        val = cache.get("sisifo_healthcheck")
        status["redis"] = {"status": "ok" if val == "ok" else "error"}
    except Exception as exc:
        status["redis"] = {"status": "error", "detail": str(exc)}

    return Response(status)
