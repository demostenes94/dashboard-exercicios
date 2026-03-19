import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")

# 🔗 GOOGLE SHEETS
sheet_id = "1RqFBXSu48Mr9y5ocR291v5A7H2sXKJDFG1Hfg6k6UO4"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

df = pd.read_csv(url)

# 🔧 TRATAMENTO
df['INICIO'] = pd.to_datetime(df['INICIO'], dayfirst=True)
df['FIM'] = pd.to_datetime(df['FIM'], dayfirst=True)

# 🔥 ORDENAR POR DATA (melhor prática)
df = df.sort_values(by="INICIO")

today = pd.to_datetime(datetime.today().date())

# 🎯 STATUS (com alerta opcional)
def get_status(row):
    if today < row['INICIO']:
        return "Previsto"
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
        "Previsto": "#1565C0",
        "Em andamento": "#2E7D32",
        "Finalizado": "#C62828"
    }
)

# 🔥 ORDEM VISUAL
fig.update_yaxes(categoryorder="total ascending")

# 🔥 LINHA DO "HOJE" (CORRIGIDO)
fig.add_vline(
    x=today,
    line_width=3,
    line_dash="dash",
    line_color="#FFD600"
)

# 🔥 MELHORIAS VISUAIS
fig.update_traces(
    marker_line_width=1,
    marker_line_color="black"
)

fig.update_xaxes(
    tickformat="%b %Y"
)

fig.update_yaxes(autorange="reversed")

# 📊 EXIBIR
st.plotly_chart(fig, use_container_width=True)
