from datetime import datetime
import pandas as pd
import streamlit as st
# import altair as alt

# ================== Constants ==================

CSV_URL = "https://gist.githubusercontent.com/andresaguilar1125/fd3f8200bcced4147315e6581a9c0eb7/raw/transacciones.csv"

BUDGET_BASE = {
    "Familiar": 80,
    "Medico": 80,
    "Restaurantes": 120,
    "Super": 300,
    "Viajes": 120
}

CATEGORY_ICON = {
    "Familiar": "👤",
    "Medico": "💊",
    "Restaurantes": "🍕",
    "Super": "🛒",
    "Viajes": "🚖"
}

PERSONA_ICON = {
    "Andres": "🟢",
    "Casa": "🟣",
    "Mari": "🔵",
}

# ================== Dataframes ==================

df = (
    pd.read_csv(CSV_URL, parse_dates=["Fecha"])
    .dropna(subset=["Monto", "Categoria", "Persona", "Comercio", "Descripcion"])
    .assign(
        Dia=lambda d: d["Fecha"].dt.strftime("%b-%d"),
        Semana=lambda d: d["Fecha"].apply(lambda x: f"W{min((x.day - 1) // 7 + 1, 4)}"),
        Quincena=lambda d: d["Fecha"].dt.day.map(lambda x: "Q2" if x >= 15 else "Q1"),
        Monto=lambda d: d["Monto"].astype(str).str.replace(",", "", regex=False).astype(float),
        Periodo=lambda d: d["Fecha"].dt.strftime("%Y%m").astype(int),
        Super=lambda d: d["Descripcion"].where(d["Categoria"] == "Super").str.split(" - ").str[0]
    )
    # .set_index("Fecha")
    # .pipe(lambda d: d.set_index(d.index.strftime("%m/%d/%Y %I:%M %p")))
)

df_grouped = (
    df.copy()
      .assign(
          Persona=lambda x: x['Persona'].where(x['Categoria'] != 'Super', 'Casa'),
          Descripcion=lambda x: x['Descripcion'].where(x['Categoria'] != 'Super', 'Supermercado')
      )
      .groupby('Fecha', as_index=False)
      .agg({
        'Dia': 'first',
        'Persona': 'first',
        'Descripcion': 'first',
        'Categoria': 'first',
        'Comercio': 'first',
        'Monto': 'sum'
      })
)

st.dataframe(df)
st.dataframe(df_grouped)

# ================== Functions ==================

def build_budget(df):
    df_budget = (
        pd.DataFrame([{"Categoria": k, "Prespuesto": v} for k, v in BUDGET_BASE.items()])
        .merge(
            df.groupby("Categoria", as_index=False)["Monto"].sum(),
            on="Categoria",
            how="left"
        )
        .fillna({"Monto": 0})
        .assign(
            Monto=lambda d: (d["Monto"] / 1000).round(0),
            Restante=lambda d: d["Prespuesto"] - d["Monto"]
        )
    )

    return df_budget


# st.dataframe(build_budget(df))