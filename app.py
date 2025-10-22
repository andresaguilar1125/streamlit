import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

GOOGLESHEET_URL = "https://docs.google.com/spreadsheets/d/1rAkmgUkf8xcqlwdcnX0VpHAIgUrHgCRRhU8cBlsA3HA/export?format=csv&gid="  

# Map categories to GIDs
GID_CATEGORY = {
    "Familiar": "164123414",
    "Medico": "754260188",
    "Recibos": "1534979300",
    "Restaurantes": "1270398057",
    "Super": "1192999871",
    "Viajes": "856975249"
}

@st.cache_data
def get_sheet(gid, category_name):
    # Cached function to load Google Sheet as pandas DataFrame and add a category column
    df = pd.read_csv(GOOGLESHEET_URL + gid)
    df["Categoria"] = category_name
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", infer_datetime_format=True)
    df["Monto"] = df["Monto"].str.replace(",", "").astype(float)
    return df

# Concatenate all sheets and transform data
df = pd.concat([get_sheet(gid, category) for category, gid in GID_CATEGORY.items()])

# st.write("### Combined & Transformed Data")
# st.dataframe(df)


# for dataframes tabs
# st.write(duckdb.query(open("df_desktop.sql").read()) .to_df())
# st.write(duckdb.query(open("df_mobile.sql").read()) .to_df())
# st.write(duckdb.query(open("df_budget.sql").read()) .to_df())

# for chart tabs
df_extras = (duckdb.query(open("fig_extras.sql").read()) .to_df())
df_extras
fig = px.bar(df_extras, x="Periodo", y="Total", color="Categoria", barmode="stack")
fig
