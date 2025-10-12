from datetime import datetime
import pandas as pd
import streamlit as st
import altair as alt

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
        Quincena=lambda d: d["Fecha"].dt.day.map(lambda x: "W2" if x >= 15 else "W1"),
        Monto=lambda d: d["Monto"].astype(str).str.replace(",", "", regex=False).astype(float),
        Periodo=lambda d: d["Fecha"].dt.strftime("%Y%m").astype(int),
        Super=lambda d: d["Descripcion"].where(d["Categoria"] == "Super").str.split(" - ").str[0]
    )
)


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

def pivot_metrics(df, index='Categoria', categories=''):
    return (
        df.loc[
            df["Categoria"].isin(categories)
            & (df["Periodo"] >= df["Periodo"].max() - 3)
        ]
        .pivot_table(
            index=index,
            columns="Periodo",
            values="Monto",
            aggfunc="sum", 
        )
        .fillna(0)
        .sort_index(axis=1, ascending=False)
        .style.format("{:,.0f}")
    )

def display_category_tab(df, groupby_cols=None):
    groupby_cols = groupby_cols or ["Dia", "Comercio", "Descripcion"]

    # Add icons
    df["Comercio"] = df["Categoria"].map(CATEGORY_ICON).fillna("🌑") + " " + df["Comercio"]
    df["Descripcion"] = df["Persona"].map(PERSONA_ICON).fillna("🌑") + " " + df["Descripcion"]

    # Aggregate
    df_agg = df.groupby(groupby_cols, as_index=False).agg(Monto=("Monto", "sum"))

    # Explicit column order
    df_agg = df_agg[["Dia", "Monto", "Comercio", "Descripcion"]]

    # Display with proper height/width
    st.dataframe(df_agg.set_index("Dia").style.format({"Monto": "{:,.0f}"}))

def display_bar_chart(df, categories, groupby, axis, color):

    df_agg = (
        df.loc[df["Categoria"].isin(categories)]
        .groupby(groupby, as_index=False)
        .agg(Monto=("Monto", "sum"))
    )

    chart = (
        alt.Chart(df_agg)
        .mark_bar()
        .encode(
            y=alt.Y(f"{axis}:O", title=None),
            x=alt.X("Monto:Q", title=None),
            color=alt.Color(f"{color}:N", title=None),
            tooltip=groupby + ["Monto"]
        )
        .configure_legend(orient='top', title=None)
        # .properties(height=600, width=500)
    )

    st.altair_chart(chart, use_container_width=True)
   
# ================== Streamlit Widgets ==================

selected_period = st.selectbox(
    "Seleccione Periodo",
    options=sorted(df['Periodo'].unique(), reverse=True),
    index=0
)

selected_persona = st.multiselect(
    "Filtrar por Persona",
    options=df['Persona'].unique(),
    default=["Andres", "Casa", "Mari"]
)

tab1, tab2, tab3, tab4 = st.tabs(["Mes", "Extras", "Super", "Viajes"])

# ================== Tabs ==================

df_tabs = (df.loc[
    (df["Periodo"] == selected_period) & 
    (df["Persona"].isin(selected_persona))
])

with tab1:
    st.markdown(f"#### Periodo {selected_period}")
    
    st.dataframe(
        build_budget(df.loc[df["Periodo"] == selected_period])
        .set_index("Categoria")
    )
    
    categories= CATEGORY_ICON.keys()
    
    display_bar_chart(
        df = df.loc[
            (df["Categoria"]).isin(categories) & 
            (df["Periodo"] == selected_period) & 
            (df["Persona"].isin(selected_persona))
        ]
        .groupby(["Semana", "Categoria"], as_index=False)
        .agg(Monto=("Monto", "sum")),
        categories = categories, 
        groupby = ["Semana", "Categoria"],
        axis = 'Semana', 
        color = 'Categoria'
    )
    
    display_category_tab( df = df_tabs.loc[(df_tabs["Categoria"]).isin(categories)] )    
    
with tab2:
    st.markdown(f"#### Familiar + Medico + Restaurantes")
    
    categories= ['Familiar', 'Medico', 'Restaurantes']
    
    st.dataframe(pivot_metrics(df, 'Categoria', categories))
    
    display_bar_chart(
        df = df.loc[
            (df["Categoria"]).isin(categories) & 
            (df["Periodo"] == selected_period) & 
            (df["Persona"].isin(selected_persona))
        ],
        categories = categories, 
        groupby = ["Dia", "Categoria", "Descripcion"],
        axis = 'Dia', 
        color = 'Categoria'
    )
    
    display_category_tab( df = df_tabs.loc[(df_tabs["Categoria"]).isin(categories)] ) 
    
with tab3:
    st.markdown(f"#### Supermercado")
    
    categories= ['Super']
        
    st.dataframe(pivot_metrics(df, 'Categoria', categories))
    
    display_bar_chart(
        df = df.loc[
            (df["Categoria"]).isin(categories) & 
            (df["Periodo"] == selected_period) & 
            (df["Persona"].isin(selected_persona))
        ],
        categories = categories, 
        groupby = ["Super", "Quincena"],
        axis = 'Super', 
        color = 'Quincena'
    )
    
    display_category_tab( df = df_tabs.loc[(df_tabs["Categoria"]).isin(categories)] ) 
    
with tab4:
    st.markdown(f"#### Viajes")
    
    categories= ['Viajes']
    
    st.dataframe(pivot_metrics(df, 'Comercio', categories))
    
    display_bar_chart(
        df = df.loc[
            (df["Categoria"]).isin(categories) & 
            (df["Periodo"] == selected_period) & 
            (df["Persona"].isin(selected_persona))
        ],
        categories = categories, 
        groupby = ["Dia", "Persona"],
        axis = 'Dia', 
        color = 'Persona'
    )
    
    df_chart = (
        df_tabs.loc[df_tabs["Categoria"].isin(categories)]
        .groupby(["Persona", "Comercio"], as_index=False)
        .agg(
            Count=("Monto", "count"),
            Monto=("Monto", "sum"),
            Avg=("Monto", "mean"),
        )
        .assign(
            Monto=lambda d: (d["Monto"] / 1000).round(0),  # scale
            Avg=lambda d: (d["Avg"] / 1000).round(0),      # scale
        )
    )
    
    st.dataframe(
        df_tabs.loc[df_tabs["Categoria"].isin(categories)]
        .groupby(["Persona", "Comercio"], as_index=False)
        .agg(
            Count=("Monto", "count"),
            Monto=("Monto", "sum"),
            Avg=("Monto", "mean"),
        )
        .set_index("Persona")
        .style.format(subset=["Monto", "Avg", "Count"], formatter="{:,.0f}")
    )

    display_category_tab( df = df_tabs.loc[(df_tabs["Categoria"]).isin(categories)] ) 
