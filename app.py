import streamlit as st
import pandas as pd
import duckdb
from pathlib import Path

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
# DuckDB in-memory connection
# **********************************
conn = duckdb.connect(database=":memory:")
conn.register("df", df_raw)  # register raw dataframe as table

# ********************************** 
# Load SQL template
# **********************************
sql_template = Path("df_main.sql").read_text()

# ********************************** 
# Get initial df for widget options
# **********************************
temp_df = conn.execute(sql_template.format(filters="TRUE")).fetchdf()

selected_persona = st.selectbox(
    "Select Persona",
    options=["All"] + temp_df["Persona"].dropna().unique().tolist()
)

selected_period = st.selectbox(
    "Select Periodo",
    options=["All"] + temp_df["Periodo"].dropna().unique().tolist()
)

# ********************************** 
# Build dynamic filters
# **********************************
filter_clauses = []

if selected_persona != "All":
    filter_clauses.append(f"Persona = '{selected_persona}'")
if selected_period != "All":
    filter_clauses.append(f"Periodo = '{selected_period}'")

filters_sql = " AND ".join(filter_clauses) if filter_clauses else "TRUE"

# ********************************** 
# Execute final query
# **********************************
final_df = conn.execute(sql_template.format(filters=filters_sql)).fetchdf()

# ********************************** 
# Display
# **********************************
tab1, tab2 = st.tabs(["Super", "Extras"])
with tab1:
    st.dataframe(final_df)
with tab2:
    st.write("Extra tab content goes here.")
