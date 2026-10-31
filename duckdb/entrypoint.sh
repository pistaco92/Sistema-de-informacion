#!/bin/sh
set -e

DB_PATH="${DUCKDB_PATH:-/data/sisifo.duckdb}"

echo "[DuckDB Container] Verificando e inicializando esquema en ${DB_PATH}..."
python3 - <<'EOF'
import os
import duckdb

db_path = os.environ.get("DUCKDB_PATH", "/data/sisifo.duckdb")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

with open("/duckdb_service/init.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

with duckdb.connect(db_path) as con:
    con.execute(sql_script)
    tables = [row[0] for row in con.execute("SHOW TABLES").fetchall()]
    print(f"[DuckDB Container] Tablas listas en {db_path}: {tables}")
EOF

echo "[DuckDB Container] Base de datos lista. Manteniendo contenedor activo en el Pod (sin bloquear archivo)..."
exec sleep infinity
