import sqlite3
import pandas as pd

DB_PATH = "db.sqlite"

TABLES = {
    "Familiar": {
        "Fecha": "TEXT",
        "Persona": "TEXT",
        "Comercio": "TEXT",
        "Descripcion": "TEXT",
        "Monto": "INTEGER"
    },
    "Medico": {
        "Fecha": "TEXT",
        "Persona": "TEXT",
        "Comercio": "TEXT",
        "Descripcion": "TEXT",
        "Monto": "INTEGER"
    },
    "Recibos": {
        "Fecha": "TEXT",
        "Persona": "TEXT",
        "Comercio": "TEXT",
        "Monto": "INTEGER"
    },
    "Restaurantes": {
        "Fecha": "TEXT",
        "Persona": "TEXT",
        "Comercio": "TEXT",
        "Descripcion": "TEXT",
        "Monto": "INTEGER"
    },
    "Super": {
        "Fecha": "TEXT",
        "Persona": "TEXT",
        "Comercio": "TEXT",
        "Grupo": "TEXT",
        "Descripcion": "TEXT",
        "Monto": "INTEGER"
    },
    "Viajes": {
        "Fecha": "TEXT",
        "Persona": "TEXT",
        "Comercio": "TEXT",
        "Descripcion": "TEXT",
        "Monto": "INTEGER"
    }
}

CSV_MAP = {
    "Familiar": "https://raw.githubusercontent.com/andresaguilar1125/streamlit/sqlite_1/data/Familiar.csv",
    "Medico": "https://raw.githubusercontent.com/andresaguilar1125/streamlit/sqlite_1/data/Medico.csv",
    "Recibos": "https://raw.githubusercontent.com/andresaguilar1125/streamlit/sqlite_1/data/Recibos.csv",
    "Restaurantes": "https://raw.githubusercontent.com/andresaguilar1125/streamlit/sqlite_1/data/Restaurantes.csv",
    "Super": "https://raw.githubusercontent.com/andresaguilar1125/streamlit/sqlite_1/data/Super.csv",
    "Viajes": "https://raw.githubusercontent.com/andresaguilar1125/streamlit/sqlite_1/data/Viajes.csv"
}

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create and clear tables
for table, columns in TABLES.items():
    col_defs = ", ".join([f"{col} {ctype}" for col, ctype in columns.items()])
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_defs});")
    cur.execute(f"DELETE FROM {table};")

# Load and insert data
inserted = 0
for table, url in CSV_MAP.items():
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"Skipping {table}: {e}")
        continue

    cols = list(TABLES[table].keys())
    placeholders = ", ".join(["?"] * len(cols))

    for _, row in df.iterrows():
        values = [row.get(col, None) for col in cols]
        cur.execute(
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders});",
            values
        )
        inserted += 1

conn.commit()
conn.close()
print(f"Inserted {inserted} rows total.")
