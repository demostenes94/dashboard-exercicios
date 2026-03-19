import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")

# =========================
# 🔗 GOOGLE SHEETS
# =========================
sheet_id = "1RqFBXSu48Mr9y5ocR291v5A7H2sXKJDFG1Hfg6k6UO4"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

df = pd.read_csv(url)

# =========================
# 🔧 TRATAMENTO
# =========================
df['INICIO'] = pd.to_datetime(df['INICIO'], dayfirst=True)
df['FIM'] = pd.to_datetime(df['FIM'], dayfirst=True)

today = pd.to_datetime(datetime.today().date())

# =========================
# 🎯 STATUS INTELIGENTE
# =========================
def get_status(row):
    dias = (row['INICIO'] - today).days
    if dias >= 0 and dias <= 7:
        return "Inicia em breve"
    elif today < row['INICIO']:
        return "Previsto"
    elif row['INICIO'] <= today <= row['FIM']:
        return "Em andamento"
    else:
        return "Finalizado"

df['status'] = df.apply(get_status, axis=1)

# =========================
# 🔎 FILTROS
# =========================
st.sidebar.header("Filtros")

trigram = st.sidebar.multiselect(
    "TRIGRAMA",
    options=df['TRIGRAMA'].dropna().unique(),
    default=df['TRIGRAMA'].dropna().unique()
)

df = df[df['TRIGRAMA'].isin(trigram)]

# =========================
# 🔥 ORDENAÇÃO
# =========================
df = df.sort_values(by=["TRIGRAMA", "INICIO"])

# =========================
# 🧠 TÍTULO
# =========================
st.title("📊 Painel de Exercícios")
st.markdown("### Situação operacional dos exercícios")

# =========================
# 📊 KPIs
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", len(df))
col2.metric("Em andamento", (df['status'] == "Em andamento").sum())
col3.metric("Finalizados", (df['status'] == "Finalizado").sum())
col4.metric("A iniciar (7 dias)", (df['status'] == "Inicia em breve").sum())

# =========================
# 🚨 ALERTAS
# =========================
alertas = df[df['status'] == "Inicia em breve"]

if not alertas.empty:
    st.warning(f"⚠️ {len(alertas)} exercício(s) iniciam nos próximos 7 dias")

# =========================
# 📊 GANTT LIMPO
# =========================
fig = px.timeline(
    df,
    x_start="INICIO",
    x_end="FIM",
    y=df["TRIGRAMA"] + " | " + df["EXERCÍCIO"],
    color="status",
    hover_data=["TRIGRAMA", "TIPO"],
    color_discrete_map={
        "Previsto": "#1976D2",
        "Em andamento": "#2E7D32",
        "Finalizado": "#C62828",
        "Inicia em breve": "#FF9800"
    }
)

fig.update_layout(height=600 + (len(df) * 25))

fig.add_vline(
    x=today,
    line_width=3,
    line_dash="dash",
    line_color="#FFD600"
)

fig.update_traces(marker_line_width=1, marker_line_color="black")

fig.update_xaxes(tickformat="%b %Y")

fig.update_yaxes(
    title=None,
    tickfont=dict(size=14)  # 👈 AQUI aumenta o tamanho
)

fig.update_layout(
    font=dict(size=12),
    bargap=0.2,
    legend_title_text="Status"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📊 MISSÕES POR TRIGRAMA
# =========================
st.subheader("📊 Total de exercícios por OCE")

df_total = df.groupby('TRIGRAMA').size().reset_index(name='quantidade')

# ordenar do maior para o menor
df_total = df_total.sort_values(by="quantidade", ascending=False)

fig_total = px.bar(
    df_total,
    x="TRIGRAMA",
    y="quantidade",
    text="quantidade",
    color="quantidade",
    color_continuous_scale="Blues"
)

fig_total.update_layout(
    xaxis_title="TRIGRAMA",
    yaxis_title="Quantidade de exercícios",
    showlegend=False
)

fig_total.update_traces(textposition="outside")

st.plotly_chart(fig_total, use_container_width=True)
