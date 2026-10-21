"""
Ejecuta este script UNA sola vez para agregar la columna 'empresa' a la BD.
Corre desde la carpeta donde está tu app:
  python migrar_empresa.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'helpdesk.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Verificar si ya existe la columna
cur.execute("PRAGMA table_info(tickets)")
cols = [row[1] for row in cur.fetchall()]

if 'empresa' not in cols:
    cur.execute("ALTER TABLE tickets ADD COLUMN empresa VARCHAR(50) NOT NULL DEFAULT 'SPARK'")
    conn.commit()
    print("✅ Columna 'empresa' agregada correctamente.")
else:
    print("ℹ️  La columna 'empresa' ya existe, no se hizo nada.")

conn.close()
