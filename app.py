import streamlit as st
import pandas as pd

GOOGLESHEET_URL = "https://docs.google.com/spreadsheets/d/1rAkmgUkf8xcqlwdcnX0VpHAIgUrHgCRRhU8cBlsA3HA/export?format=csv&gid="  

# Mapping GID to category names
GID_CATEGORY = {
    "FAMILIAR": "164123414",
    "MEDICO": "754260188",
    "RECIBOS": "1534979300",
    "RESTAURANTES": "1270398057",
    "SUPER": "1192999871",
    "VIAJES": "856975249"
}

# Function to get a sheet as a DataFrame
@st.cache_data
def get_sheet(gid):
    return pd.read_csv(GOOGLESHEET_URL + gid)

# Load all sheets dynamically into a dictionary
dfs = {category: get_sheet(gid) for category, gid in GID_CATEGORY.items()}

# Example: access the 'FAMILIAR' DataFrame
st.write(dfs["MEDICO"])
