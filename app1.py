import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_javascript import st_javascript

# ================== LAYOUT
# DEFINE LAYOUT DO NOT UNCOMMENT OR DELETE THIS SECTION
# # Get the viewport width
# width = st_javascript("window.innerWidth")
# st.write("Screen width:", width)

# # Example responsive layout
# if width < 600:
#     st.write("Mobile layout: do A")
# else:
#     st.write("Desktop layout: do B")

# ================== SOURCES
CSV_URL = "https://gist.githubusercontent.com/andresaguilar1125/fd3f8200bcced4147315e6581a9c0eb7/raw/transacciones.csv"

# ================== DATAFRAMES
df = (
    pd.read_csv(CSV_URL, parse_dates=["Fecha"])
    .dropna(subset=["Monto", "Categoria", "Persona", "Comercio", "Descripcion"])
    .assign(
        Dia=lambda d: d["Fecha"].dt.strftime("%b-%d"),
        Semana=lambda d: d["Fecha"].apply(lambda x: f"W{min((x.day - 1) // 7 + 1, 4)}"),
        Quincena=lambda d: d["Fecha"].dt.day.map(lambda x: "Q2" if x >= 15 else "Q1"),
        Monto=lambda d: d["Monto"].astype(str).str.replace(",", "", regex=False).astype("Int64"),
        Periodo=lambda d: d["Fecha"].dt.strftime("%Y%m").astype(int),
        # Super=lambda d: d["Descripcion"].where(d["Categoria"] == "Super").str.split(" - ").str[0]
    )
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

df_budget = (
    pd.DataFrame([
        {'Categoria': 'Familiar', 'Limite': 80},
        {'Categoria': 'Medico', 'Limite': 80},
        {'Categoria': 'Restaurantes', 'Limite': 120},
        {'Categoria': 'Super', 'Limite': 300},
        {'Categoria': 'Viajes', 'Limite': 120}
    ])
    .merge(
        df.groupby("Categoria", as_index=False)["Monto"].sum(),
        on="Categoria",
        how="left"
    )
    .fillna({"Monto": 0})
    .assign(
        Monto=lambda d: (d["Monto"] / 1000).round(0),
        Restante=lambda d: d["Limite"] - d["Monto"]
    )
)

# ================== STYLES
EMOJIS = {
    "Familiar": "👤",
    "Medico": "💊",
    "Restaurantes": "🍕",
    "Super": "🛒",
    "Viajes": "🚖",
    "Andres": "🟢",
    "Casa": "🟣",
    "Mari": "🔵",
}

def get_emoji(key):
    return EMOJIS.get(key, "⚠️")

# def highlight_even_rows(row):
#     return ['background-color: #f0f2f6' if row.name % 2 == 0 else '' for _ in row]

def df_desktop(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    # Make a copy so original stays intact
    df_copy = df[["Fecha", "Categoria", "Persona", "Comercio", "Descripcion", "Monto"]].copy().reset_index(drop=True)
    
    # Apply formatting
    styled = df_copy.style.format({
        "Fecha": lambda t: t.strftime("%m/%d/%Y %I:%M %p"),
        "Categoria": lambda x: f"{get_emoji(x)} {x}",
        "Persona": lambda x: f"{get_emoji(x)} {x}",
        "Monto": "{:,.0f}"
    }).apply(lambda row: ['background-color: lightgray' if row.name % 2 == 0 else '' for _ in row], axis=1).hide(axis="index")
    #.apply(highlight_even_rows, axis=1)
    
    return styled

def df_mobile(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    # Data transformations
    df_copy = (
        df[["Dia", "Comercio", "Persona", "Descripcion", "Monto", "Categoria"]]
        .assign(
            Comercio=lambda x: x.apply(lambda row: f"{get_emoji(row['Categoria'])} {row['Comercio']}", axis=1),
            Descripcion=lambda x: x.apply(lambda row: f"{get_emoji(row['Persona'])} {row['Descripcion']}", axis=1)
        )
        .drop(columns=["Categoria", "Persona"])
        .reset_index(drop=True)  # ensures there is no index to display
    )

    # Apply formatting and row highlighting
    styled = df_copy.style.format({"Monto": "{:,.0f}"})#.apply(highlight_even_rows, axis=1)

    return styled

# ================== WIDGETS
col1, col2 = st.columns(2)

with col1:
    selected_period = st.selectbox(
        "Periodo",
        options=sorted(df['Periodo'].unique(), reverse=True),
        index=0
    )
    
with col2:
    selected_persona = st.multiselect(
        "Persona",
        options=df['Persona'].unique(),
        default=["Andres", "Casa", "Mari"]
    )
    
tab1, tab2, tab3, tab4 = st.tabs([ "📅 Mes", "➕ Extras", "🛒 Super", "✈️ Viajes" ])

# st.dataframe(df_mobile(df))
st.write(df_desktop(df))
# df_grouped
# st.dataframe(df_mobile(df_grouped))
st.write(df_desktop(df_grouped))
