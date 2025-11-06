import streamlit as st
import pandas as pd

# Load secrets
BASE_URL = st.secrets["google_sheet"]["base_url"]
GIDS = dict(st.secrets["google_sheet"]["gids"])

# Cache CSV

import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=True)
def fetch_csv() -> pd.DataFrame:
   """Fetch all published Google Sheet CSVs listed in secrets.toml, clean, and concatenate."""
   base_url = st.secrets["google_sheet"]["base_url"]
   gids = dict(st.secrets["google_sheet"]["gids"])

   frames = []

   for category, gid in gids.items():
       url = f"{base_url}{gid}"
       try:
           df = (
               pd.read_csv(url, skip_blank_lines=True)  # skip blank lines
               .dropna(how="all")                       # drop fully empty rows
               .reset_index(drop=True)
           )

           # Clean and cast known columns if present
           if "Fecha" in df.columns: df["Fecha"] = pd.to_datetime( df["Fecha"], format="%m/%d/%y %I:%M %p", errors="coerce" )
           if "Monto" in df.columns: df["Monto"] = ( pd.to_numeric( df["Monto"].astype(str) .str.replace(",", "", regex=False) .str.strip(), errors="coerce", ) .fillna(0) .astype(int) )

           df["Categoria"] = category
           frames.append(df)
           print(f"[DEBUG] Loaded {len(df)} rows from {category} sheet.")

       except Exception as e:
           st.error(f"Error loading {category}: {e}")
           print(f"[DEBUG] Failed to load {category}: {e}")

   if not frames:
       print("[DEBUG] No sheets loaded.")
       return pd.DataFrame()

   combined = pd.concat(frames, ignore_index=True)
   combined.reset_index(drop=True, inplace=True)
   print(f"[DEBUG] Total rows combined and reindexed: {len(combined)}")

   return combined


df = fetch_csv()
df
