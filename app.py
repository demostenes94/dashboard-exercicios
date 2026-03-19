import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")

# 🔗 GOOGLE SHEETS
sheet_id = "1RqFBXSu48Mr9y5ocR291v5A7H2sXKJDFG1Hfg6k6UO4"
url = f"https://docs.google.com/spreadsheets/d/1RqFBXSu48Mr9y5ocR291v5A7H2sXKJDFG1Hfg6k6UO4/export?format=csv"

df = pd.read_csv(url)

df['INICIO'] = pd.to_datetime(df['INICIO'], dayfirst=True)
df['FIM'] = pd.to_datetime(df['FIM'], dayfirst=True)

today = pd.to_datetime(datetime.today().date())

def get_status(row):
    if today < row['INICIO']:
        return "Antes"
    elif row['INICIO'] <= today <= row['FIM']:
        return "Em andamento"
    else:
        return "Finalizado"

df['status'] = df.apply(get_status, axis=1)

st.title("📊 Painel de Exercícios")

col1, col2, col3 = st.columns(3)
col1.metric("Total", len(df))
col2.metric("Em andamento", (df['status'] == "Em andamento").sum())
col3.metric("Finalizados", (df['status'] == "Finalizado").sum())

fig = px.timeline(
    df,
    x_start="INICIO",
    x_end="FIM",
    y="EXERCÍCIO",
    color="status",
    color_discrete_map={
        "Antes": "#2196F3",
        "Em andamento": "#4CAF50",
        "Finalizado": "#F44336"
    }
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)
