import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")

# 🔗 GOOGLE SHEETS (SEU ID JÁ INSERIDO)
sheet_id = "1RqFBXSu48Mr9y5ocR291v5A7H2sXKJDFG1Hfg6k6UO4"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

df = pd.read_csv(url)

# 🔧 TRATAMENTO
df['INICIO'] = pd.to_datetime(df['INICIO'], dayfirst=True)
df['FIM'] = pd.to_datetime(df['FIM'], dayfirst=True)

# 🔥 ORDENAR POR DATA
df = df.sort_values(by="INICIO")

today = pd.to_datetime(datetime.today().date())

# 🎯 STATUS
def get_status(row):
    if today < row['INICIO']:
        return "Antes"
    elif row['INICIO'] <= today <= row['FIM']:
        return "Em andamento"
    else:
        return "Finalizado"

df['status'] = df.apply(get_status, axis=1)

# 🔎 FILTRO
trigram = st.multiselect(
    "Filtrar TRIGRAMA",
    options=df['TRIGRAMA'].dropna().unique(),
    default=df['TRIGRAMA'].dropna().unique()
)

df = df[df['TRIGRAMA'].isin(trigram)]

# 🧠 TÍTULO
st.title("📊 Painel de Exercícios")
st.markdown("### Situação operacional dos exercícios")

# 📊 KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", len(df))
col2.metric("Em andamento", (df['status'] == "Em andamento").sum())
col3.metric("Finalizados", (df['status'] == "Finalizado").sum())

# 🔥 KPI NOVO
col4.metric(
    "A iniciar (7 dias)",
    ((df['INICIO'] - today).dt.days.between(0,7)).sum()
)

# 📊 GANTT
fig = px.timeline(
    df,
    x_start="INICIO",
    x_end="FIM",
    y="EXERCÍCIO",
    color="status",
    hover_data=["TRIGRAMA", "TIPO"],
    color_discrete_map={
        "Antes": "#1E88E5",
        "Em andamento": "#43A047",
        "Finalizado": "#E53935"
    }
)

# 🔥 LINHA DO "HOJE"
fig.add_vline(
    x=today,
    line_width=2,
    line_dash="dash",
    line_color="yellow"
)

fig.update_yaxes(autorange="reversed")

st.plotly_chart(fig, use_container_width=True)
