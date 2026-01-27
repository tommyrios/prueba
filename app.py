import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Monitor Legislativo BBVA", layout="wide")

st.title("📊 Monitor de Asuntos Públicos - BBVA")

# 1. Conexión con tu Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1P0Z8phkksBeCLzn-x5UF5iof7ooH4tKrEcbwBDBhAPc/edit?usp=sharing")

# 2. Sidebar para filtros rápidos
st.sidebar.header("Filtros")
impacto_sel = st.sidebar.multiselect("Nivel de Impacto", df["Impacto"].unique(), default="ALTO")
partido_sel = st.sidebar.multiselect("Partido Político", df["Partido Político"].unique())

# Filtrado de datos
df_filtrado = df[df["Impacto"].isin(impacto_sel)]
if partido_sel:
    df_filtrado = df_filtrado[df_filtrado["Partido Político"].isin(partido_sel)]

# 3. Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Total Proyectos", len(df))
col2.metric("Impacto Alto", len(df[df["Impacto"] == "ALTO"]))
col3.metric("Última Actualización", df["Fecha de inicio"].max())

# 4. Visualización de la Tabla interactiva
st.subheader("Detalle de Proyectos Seleccionados")
st.dataframe(df_filtrado, use_container_width=True)

# 5. Un toque de análisis (Gráfico por Comisión)
st.subheader("Proyectos por Comisión")
comisiones_count = df_filtrado["Comisiones"].value_counts()
st.bar_chart(comisiones_count)
