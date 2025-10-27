import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
   page_title="Gastos",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",
)

# ********************************** 
# SECRETS
# **********************************
GOOGLESHEET_URL = st.secrets["google_sheet"]["base_url"]
GID_CATEGORY = st.secrets["google_sheet"]["gid"]

# ********************************** 
# Load Google Sheets CSVs
# **********************************
@st.cache_data
def get_csv(_gid_dict):
    dfs = []
    for category, gid in _gid_dict.items():
        df_read = pd.read_csv(GOOGLESHEET_URL + gid)
        df_read["Categoria"] = category
        df_read["Fecha"] = pd.to_datetime(df_read["Fecha"], errors="coerce", infer_datetime_format=True)
        dfs.append(df_read)
    return pd.concat(dfs, ignore_index=True)

df_raw = get_csv(GID_CATEGORY)

# ********************************** 
# Preprocess df (like df_main.sql)
# **********************************
df = df_raw.copy()

# Clean Monto
df["Monto"] = df["Monto"].astype(str).str.replace(",", "").astype(float)

# Derived columns
df["Periodo"] = df["Fecha"].dt.strftime("%Y%m")
df["Dia"] = df["Fecha"].dt.strftime("%m-%d-%Y")
df["Quincena"] = df["Fecha"].dt.day.apply(lambda d: "Q2" if d >= 15 else "Q1")
df["Semana"] = df["Fecha"].dt.day.apply(
    lambda d: "S1" if 1 <= d <= 7 else "S2" if 8 <= d <= 14 else "S3" if 15 <= d <= 21 else "S4"
)

# ********************************** 
# Tabs
# **********************************
tab1, tab2 = st.tabs(["Data", "Mensual"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        personas = ["All"] + df["Persona"].dropna().unique().tolist()
        selected_persona = st.selectbox("Select Persona", options=personas)
    with col2:
        periodos = ["All"] + df["Periodo"].dropna().unique().tolist()
        selected_period = st.selectbox("Select Periodo", options=periodos)
    
    # Filter
    df_filtered = df.copy()
    if selected_persona != "All":
        df_filtered = df_filtered[df_filtered["Persona"] == selected_persona]
    if selected_period != "All":
        df_filtered = df_filtered[df_filtered["Periodo"] == selected_period]
    
    # Sort descending by Fecha
    df_filtered = df_filtered.sort_values("Fecha", ascending=False)
    
    st.dataframe(df_filtered)

with tab2:
    # Budget table
    budget_table = pd.DataFrame({
        "Categoria": ['Familiar','Medico','Recibos','Restaurantes','Super','Viajes'],
        "Budget": [65000,50000,120000,120000,300000,120000]
    })

    # Current period
    current_periodo = datetime.now().strftime("%Y%m")
    
    # Filter df by current period
    df_current = df[df["Periodo"] == current_periodo]
    
    # Aggregate spend per category
    df_sum = df_current.groupby("Categoria")["Monto"].sum().reset_index(name="Sum")
    
    # Merge with budget
    df_budget = budget_table.merge(df_sum, on="Categoria", how="left")
    df_budget["Sum"] = df_budget["Sum"].fillna(0)
    df_budget["Remaining"] = df_budget["Budget"] - df_budget["Sum"]
    
    st.dataframe(df_budget)
