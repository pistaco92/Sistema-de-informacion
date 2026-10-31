from rest_framework import serializers

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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "name"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["supplier_id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "product_id",
            "category",
            "supplier",
            "name",
            "info",
            "price",
            "stock",
            "guarantee",
        ]


class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = ["id", "parent", "component", "amount"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "name", "password", "role", "purchases", "distance"]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "product", "user", "score", "comment"]


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = [
            "delivery_id",
            "customer",
            "pay_method",
            "state",
            "datetime",
            "est_delivery_time",
            "real_delivery_time",
        ]


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ["id", "delivery", "product", "amount"]
