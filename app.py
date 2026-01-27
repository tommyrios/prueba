import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Monitor Legislativo BBVA", page_icon="🏛️", layout="wide")

st.title("🏛️ Monitor de Actividad Parlamentaria")
st.subheader("Análisis de Impacto Regulatorio - BBVA Argentina")

# URL del CSV que me pasaste
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdSCxYZyR3msEswZzbV5hTsCtSOFSTekgQeZJ5FfJw8KUwJP2LfoGLLKCL7b06RiOtf1YjLVDDFdMG/pub?gid=794974288&single=true&output=csv"

@st.cache_data(ttl=3600)  # Cacheamos los datos por 1 hora para que sea veloz
def load_data():
    df = pd.read_csv(CSV_URL)
    # Limpieza: quitar espacios en nombres de columnas
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros")
    
    # Filtro de Impacto
    impactos = df["Impacto"].unique().tolist()
    filtro_impacto = st.sidebar.multiselect("Nivel de Impacto", impactos, default=impactos)

    # Filtro de Partido
    partidos = df["Partido Político"].unique().tolist()
    filtro_partido = st.sidebar.multiselect("Partido Político", partidos, default=partidos)

    # Aplicar Filtros
    mask = (df["Impacto"].isin(filtro_impacto)) & (df["Partido Político"].isin(filtro_partido))
    df_filtrado = df[mask]

    # --- MÉTRICAS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Proyectos", len(df_filtrado))
    col2.metric("Impacto ALTO", len(df_filtrado[df_filtrado["Impacto"] == "ALTO"]))
    col3.metric("Última Fecha", df["Fecha de inicio"].max())

    # --- TABLA INTERACTIVA ---
    st.write("### Detalle de Proyectos")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    # --- GRÁFICOS ---
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("#### Proyectos por Comisión")
        st.bar_chart(df_filtrado["Comisiones"].value_counts())
        
    with c2:
        st.write("#### Distribución por Impacto")
        st.bar_chart(df_filtrado["Impacto"].value_counts())

except Exception as e:
    st.error(f"Hubo un problema al cargar los datos: {e}")
