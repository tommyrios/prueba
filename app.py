import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitor Regulatorio BBVA", layout="wide")

st.title("🏛️ Dashboard de Asuntos Públicos")

# Conectar con tu Google Sheet (simplificado)
# df = cargar_datos_desde_sheets() 

# Filtros en la barra lateral
impacto_filtro = st.sidebar.multiselect("Nivel de Impacto", ["Alto", "Medio", "Bajo"], default="Alto")

# Mostrar métricas clave
col1, col2 = st.columns(2)
col1.metric("Proyectos Mes Actual", "24", "+5%")
col2.metric("Impacto Alto detectado", "3", "-2")

st.subheader("Proyectos de Ley Filtrados")
# Mostrás la tabla que ya tenés automatizada
st.dataframe(df[df['impacto'].isin(impacto_filtro)])

# Un gráfico rápido de los temas más tratados
st.bar_chart(df['tema'].value_counts())
