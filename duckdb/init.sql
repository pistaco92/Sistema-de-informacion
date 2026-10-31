-- Esquema SQL del Modelo Relacional (Entregable Sísifo) para DuckDB

CREATE SEQUENCE IF NOT EXISTS "seq_categories_category_id" START 1;
CREATE TABLE IF NOT EXISTS "categories" (
    "category_id" INTEGER PRIMARY KEY DEFAULT nextval('"seq_categories_category_id"'),
    "name" TEXT NOT NULL UNIQUE
);

CREATE SEQUENCE IF NOT EXISTS "seq_suppliers_supplier_id" START 1;
CREATE TABLE IF NOT EXISTS "suppliers" (
    "supplier_id" INTEGER PRIMARY KEY DEFAULT nextval('"seq_suppliers_supplier_id"'),
    "name" TEXT NOT NULL UNIQUE
);

CREATE SEQUENCE IF NOT EXISTS "seq_users_user_id" START 1;
CREATE TABLE IF NOT EXISTS "users" (
    "user_id" INTEGER PRIMARY KEY DEFAULT nextval('"seq_users_user_id"'),
    "name" TEXT NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "purchases" INTEGER NOT NULL DEFAULT 0,
    "distance" INTEGER
);

CREATE SEQUENCE IF NOT EXISTS "seq_products_product_id" START 1;
CREATE TABLE IF NOT EXISTS "products" (
    "product_id" INTEGER PRIMARY KEY DEFAULT nextval('"seq_products_product_id"'),
    "category_id" INTEGER NOT NULL REFERENCES "categories" ("category_id"),
    "supplier_id" INTEGER REFERENCES "suppliers" ("supplier_id"),
    "name" TEXT NOT NULL,
    "info" TEXT,
    "price" INTEGER NOT NULL,
    "stock" INTEGER NOT NULL,
    "guarantee" INTEGER NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS "seq_composition_id" START 1;
CREATE TABLE IF NOT EXISTS "composition" (
    "id" INTEGER PRIMARY KEY DEFAULT nextval('"seq_composition_id"'),
    "parent_id" INTEGER NOT NULL REFERENCES "products" ("product_id"),
    "component_id" INTEGER NOT NULL REFERENCES "products" ("product_id"),
    "amount" INTEGER NOT NULL,
    UNIQUE ("parent_id", "component_id")
);

CREATE SEQUENCE IF NOT EXISTS "seq_ratings_id" START 1;
CREATE TABLE IF NOT EXISTS "ratings" (
    "id" INTEGER PRIMARY KEY DEFAULT nextval('"seq_ratings_id"'),
    "product_id" INTEGER NOT NULL REFERENCES "products" ("product_id"),
    "user_id" INTEGER NOT NULL REFERENCES "users" ("user_id"),
    "score" INTEGER NOT NULL,
    "comment" TEXT,
    UNIQUE ("product_id", "user_id")
);

CREATE SEQUENCE IF NOT EXISTS "seq_deliveries_delivery_id" START 1;
CREATE TABLE IF NOT EXISTS "deliveries" (
    "delivery_id" INTEGER PRIMARY KEY DEFAULT nextval('"seq_deliveries_delivery_id"'),
    "customer_id" INTEGER NOT NULL REFERENCES "users" ("user_id"),
    "pay_method" TEXT,
    "state" TEXT NOT NULL,
    "datetime" TIMESTAMP NOT NULL,
    "est_delivery_time" INTEGER,
    "real_delivery_time" INTEGER
);

CREATE SEQUENCE IF NOT EXISTS "seq_purchases_id" START 1;
CREATE TABLE IF NOT EXISTS "purchases" (
    "id" INTEGER PRIMARY KEY DEFAULT nextval('"seq_purchases_id"'),
    "delivery_id" INTEGER REFERENCES "deliveries" ("delivery_id"),
    "product_id" INTEGER NOT NULL REFERENCES "products" ("product_id"),
    "amount" INTEGER NOT NULL
);
