from django.db import models


class Category(models.Model):
    """Tabla Categories."""

    category_id = models.AutoField(primary_key=True, db_column="category_id")
    name = models.TextField(unique=True, db_column="name")

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["category_id"]

    def __str__(self):
        return f"{self.name} (#{self.category_id})"


class Supplier(models.Model):
    """Tabla Suppliers."""

    supplier_id = models.AutoField(primary_key=True, db_column="supplier_id")
    name = models.TextField(unique=True, db_column="name")

    class Meta:
        db_table = "suppliers"
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ["supplier_id"]

    def __str__(self):
        return f"{self.name} (#{self.supplier_id})"


class Product(models.Model):
    """Tabla Products."""

    product_id = models.AutoField(primary_key=True, db_column="product_id")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        db_column="category_id",
        related_name="products",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="supplier_id",
        related_name="products",
    )
    name = models.TextField(db_column="name")
    info = models.TextField(null=True, blank=True, db_column="info")
    price = models.IntegerField(db_column="price")
    stock = models.IntegerField(db_column="stock")
    guarantee = models.IntegerField(db_column="guarantee")

    class Meta:
        db_table = "products"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["product_id"]

    def __str__(self):
        return f"{self.name} (#{self.product_id})"


class Composition(models.Model):
    """Tabla Composition (relación muchos a muchos recursiva de Products)."""

    parent = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column="parent_id",
        related_name="compositions_as_parent",
    )
    component = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column="component_id",
        related_name="compositions_as_component",
    )
    amount = models.IntegerField(db_column="amount")

    class Meta:
        db_table = "composition"
        verbose_name = "Composition"
        verbose_name_plural = "Compositions"
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "component"],
                name="pk_composition_parent_component",
            )
        ]
        ordering = ["parent_id", "component_id"]

    def __str__(self):
        return f"Parent #{self.parent_id} -> Component #{self.component_id} (x{self.amount})"


class User(models.Model):
    """Tabla Users."""

    user_id = models.AutoField(primary_key=True, db_column="user_id")
    name = models.TextField(unique=True, db_column="name")
    password = models.TextField(db_column="password")
    role = models.TextField(db_column="role")
    purchases = models.IntegerField(default=0, db_column="purchases")
    distance = models.IntegerField(null=True, blank=True, db_column="distance")

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["user_id"]

    def __str__(self):
        return f"{self.name} ({self.role})"


class Rating(models.Model):
    """Tabla Ratings."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column="product_id",
        related_name="ratings",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="ratings",
    )
    score = models.IntegerField(db_column="score")
    comment = models.TextField(null=True, blank=True, db_column="comment")

    class Meta:
        db_table = "ratings"
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="pk_ratings_product_user",
            )
        ]
        ordering = ["product_id", "user_id"]

    def __str__(self):
        return f"Product #{self.product_id} - User #{self.user_id}: {self.score}"


class Delivery(models.Model):
    """Tabla Deliveries."""

    delivery_id = models.AutoField(primary_key=True, db_column="delivery_id")
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="customer_id",
        related_name="deliveries",
    )
    pay_method = models.TextField(null=True, blank=True, db_column="pay_method")
    state = models.TextField(db_column="state")
    datetime = models.DateTimeField(db_column="datetime")
    est_delivery_time = models.IntegerField(
        null=True, blank=True, db_column="est_delivery_time"
    )
    real_delivery_time = models.IntegerField(
        null=True, blank=True, db_column="real_delivery_time"
    )

    class Meta:
        db_table = "deliveries"
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"
        ordering = ["-datetime"]

    def __str__(self):
        return f"Delivery #{self.delivery_id} - Customer #{self.customer_id} ({self.state})"


class Purchase(models.Model):
    """Tabla Purchases."""

    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="delivery_id",
        related_name="purchases",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column="product_id",
        related_name="purchases",
    )
    amount = models.IntegerField(db_column="amount")

    class Meta:
        db_table = "purchases"
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"
        ordering = ["id"]

    def __str__(self):
        return f"Delivery #{self.delivery_id} - Product #{self.product_id} (x{self.amount})"
