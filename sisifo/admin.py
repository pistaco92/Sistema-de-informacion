from django.contrib import admin

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

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Composition)
admin.site.register(User)
admin.site.register(Rating)
admin.site.register(Delivery)
admin.site.register(Purchase)
