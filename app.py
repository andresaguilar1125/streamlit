import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# ********************************** 
# DATA
# **********************************
@st.cache_data
def get_csv(gid_dict):
    """Load multiple CSVs from Google Sheets and concatenate into one DataFrame."""
    dfs = []
    for category, gid in gid_dict.items():
        df_read = pd.read_csv(GOOGLESHEET_URL + gid)
        # Add category column as table name
        df_read["Categoria"] = category
        # Cast to datetime object
        df_read["Fecha"] = pd.to_datetime(df_read["Fecha"], errors="coerce", infer_datetime_format=True)
        dfs.append(df_read)
    df = pd.concat(dfs, ignore_index=True)
    print(df.dtypes)
    return df

# ********************************** 
# CONSTANTS
# **********************************
# Google Sheet Base URL
GOOGLESHEET_URL = "https://docs.google.com/spreadsheets/d/1rAkmgUkf8xcqlwdcnX0VpHAIgUrHgCRRhU8cBlsA3HA/export?format=csv&gid="  

# GID Google Sheets
GID_CATEGORY = {
    "Familiar": "164123414",
    "Medico": "754260188",
    "Recibos": "1534979300",
    "Restaurantes": "1270398057",
    "Super": "1192999871",
    "Viajes": "856975249"
}

# Dataframes
df = get_csv(GID_CATEGORY)
df_main = duckdb.query(open("df_main.sql").read()).to_df()
# df_grouped = duckdb.query(open("df_grouped.sql").read()).to_df()

# **********************************
# WIDGETS
# **********************************

# ********************************** 
# STREAMLIT
# **********************************
# st.write(df)
tab1, tab2 = st.tabs(["Super", "Extras"])
with tab1:
    st.write(df_main.loc[df_main["Categoria"] == "Super"])
    # st.write(df_grouped.loc[df_grouped["Categoria"] == "Super"])
with tab2:
    st.write(df)