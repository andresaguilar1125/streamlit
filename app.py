import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# ********************************** 
# FUNCTIONS
# **********************************
@st.cache_data
def get_sheet(gid, category_name):
    # Cached function to load Google Sheet as pandas DataFrame and add a category column
    df = pd.read_csv(GOOGLESHEET_URL + gid)
    df["Categoria"] = category_name
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", infer_datetime_format=True)
    df["Monto"] = df["Monto"].str.replace(",", "").astype(float)
    return df

def get_unique_values(df, column_name):

    # Returns a list of unique, non-null values from the specified column in a pandas DataFrame.

    # Parameters:
    # - dataframe (pd.DataFrame): The DataFrame to process.
    # - column_name (str): The name of the column to extract unique values from.

    # Returns:
    # - List of unique values.

    return sorted(df[column_name].dropna().unique().tolist(), reverse=True)

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
df = pd.concat([get_sheet(gid, category) for category, gid in GID_CATEGORY.items()])

# **********************************
# WIDGETS
# **********************************
# Create multiselect widget with dynamic options
persona = st.multiselect("Selecciona Persona", get_unique_values(df, "Persona"))

# Filter DataFrame based on selected personas
df = df[df["Persona"].isin(persona)]

# ********************************** 
# DISPLAY
# **********************************
st.write(df)


# for dataframes tabs
# st.write(duckdb.query(open("df_budget.sql").read()) .to_df())