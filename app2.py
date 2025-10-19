import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_javascript import st_javascript

# ================== CONFIG
st.set_page_config(page_title="Gastos", layout="wide")
CSV_URL = "https://gist.githubusercontent.com/andresaguilar1125/fd3f8200bcced4147315e6581a9c0eb7/raw/transacciones.csv"

# ================== DATA LOAD & CLEANING
@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url, parse_dates=["Fecha"])
    df = df.dropna(subset=["Monto", "Categoria", "Persona", "Comercio", "Descripcion"])
    df["Monto"] = df["Monto"].astype(str).str.replace(",", "", regex=False).astype("Int64")
    df["Dia"] = df["Fecha"].dt.strftime("%b-%d")
    df["Semana"] = df["Fecha"].apply(lambda x: f"W{min((x.day - 1)//7 + 1, 4)}")
    df["Quincena"] = df["Fecha"].dt.day.map(lambda x: "Q2" if x >= 15 else "Q1")
    df["Periodo"] = df["Fecha"].dt.strftime("%Y%m").astype(int)
    return df

df = load_data(CSV_URL)

# ================== GROUPED DF
df_grouped = (
    df.assign(
        Persona=lambda x: x["Persona"].mask(x["Categoria"] == "Super", "Casa"),
        Descripcion=lambda x: x["Descripcion"].mask(x["Categoria"] == "Super", "Supermercado"),
    )
    .groupby("Fecha", as_index=False)
    .agg({
        "Dia": "first",
        "Persona": "first",
        "Descripcion": "first",
        "Categoria": "first",
        "Comercio": "first",
        "Monto": "sum",
    })
)

# ================== BUDGET SUMMARY
BUDGET_LIMITS = {
    "Familiar": 80, "Medico": 80, "Restaurantes": 120, "Super": 300, "Viajes": 120
}
df_budget = (
    pd.DataFrame(list(BUDGET_LIMITS.items()), columns=["Categoria", "Limite"])
    .merge(df.groupby("Categoria", as_index=False)["Monto"].sum(), on="Categoria", how="left")
    .fillna({"Monto": 0})
    .assign(Monto=lambda d: (d["Monto"] / 1000).round(0),
            Restante=lambda d: d["Limite"] - d["Monto"])
)

# ================== UI CONSTANTS
EMOJIS = {
    "Familiar": "👤", "Medico": "💊", "Restaurantes": "🍕", "Super": "🛒",
    "Viajes": "🚖", "Andres": "🟢", "Casa": "🟣", "Mari": "🔵"
}
def emoji(k): return EMOJIS.get(k, "⚠️")

# ================== TABLE STYLE
def style_table(df: pd.DataFrame, desktop: bool = True):
    if desktop:
        data = df[["Fecha", "Categoria", "Persona", "Comercio", "Descripcion", "Monto"]].copy()
        style = data.style.format({
            "Fecha": lambda t: t.strftime("%m/%d/%Y %I:%M %p"),
            "Categoria": lambda x: f"{emoji(x)} {x}",
            "Persona": lambda x: f"{emoji(x)} {x}",
            "Monto": "{:,.0f}"
        })
    else:
        data = (
            df[["Dia", "Comercio", "Persona", "Descripcion", "Monto", "Categoria"]]
            .assign(
                Comercio=lambda x: x.apply(lambda r: f"{emoji(r['Categoria'])} {r['Comercio']}", axis=1),
                Descripcion=lambda x: x.apply(lambda r: f"{emoji(r['Persona'])} {r['Descripcion']}", axis=1)
            )
            .drop(columns=["Categoria", "Persona"])
        )
        style = data.style.format({"Monto": "{:,.0f}"})
    return style.apply(
        lambda row: ['background-color: #f0f2f6' if row.name % 2 == 0 else '' for _ in row], axis=1
    ).hide(axis="index")

# ================== MOBILE CARD VIEW
def render_cards(df: pd.DataFrame):
    for _, row in df.iterrows():
        st.markdown(
            f"""
            <div style="background-color:#f8f9fa;padding:10px 15px;margin-bottom:8px;
                        border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size:14px;color:#555;">
                    <strong>{emoji(row['Categoria'])} {row['Comercio']}</strong><br>
                    <span>{emoji(row['Persona'])} {row['Descripcion']}</span><br>
                    <span style="color:#777;">{row['Dia']}</span>
                </div>
                <div style="text-align:right;font-weight:600;font-size:16px;color:#333;">
                    {row['Monto']:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ================== FILTERS
col1, col2 = st.columns(2)
with col1:
    selected_period = st.selectbox("Periodo", sorted(df["Periodo"].unique(), reverse=True), index=0)
with col2:
    selected_persona = st.multiselect("Persona", df["Persona"].unique(), default=["Andres", "Casa", "Mari"])

df_filtered = df.query("Periodo == @selected_period and Persona in @selected_persona")
df_grouped_filtered = df_grouped[df_grouped["Persona"].isin(selected_persona)]

# ================== RESPONSIVE WIDTH
width = st_javascript("window.innerWidth") or 1200
is_mobile = width < 700

# ================== TABS
tab1, tab2, tab3, tab4 = st.tabs(["📅 Mes", "➕ Extras", "🛒 Super", "✈️ Viajes"])

with tab1:
    st.subheader("Detalle general")
    if is_mobile:
        render_cards(df_filtered)
    else:
        st.dataframe(style_table(df_filtered, desktop=True), use_container_width=True)

    st.divider()
    st.subheader("Totales agrupados")
    if is_mobile:
        render_cards(df_grouped_filtered)
    else:
        st.dataframe(style_table(df_grouped_filtered, desktop=True), use_container_width=True)

with tab3:
    st.subheader("Presupuesto por categoría")
    st.dataframe(df_budget, use_container_width=True)
