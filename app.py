import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la interfaz
st.set_page_config(
    page_title="Monitor Legislativo BBVA",
    page_icon="🏛️",
    layout="wide"
)

# Estilo personalizado para el banco (opcional)
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Monitor de Actividad Parlamentaria")
st.subheader("Análisis de Impacto Regulatorio - BBVA Argentina")

# 2. Conexión a los datos
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Si configuraste el Secret como 'spreadsheet', no hace falta pasar la URL aquí
    df = conn.read()
    
    # Limpieza básica: Asegurarnos de que las columnas de impacto sean legibles
    df['Impacto'] = df['Impacto'].str.upper()

    # 3. Barra Lateral (Filtros)
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/BBVA_2019.svg/1200px-BBVA_2019.svg.png", width=150)
    st.sidebar.header("Opciones de Filtrado")

    filtro_impacto = st.sidebar.multiselect(
        "Filtrar por Nivel de Impacto:",
        options=df["Impacto"].unique(),
        default=["ALTO", "MEDIO"]
    )

    filtro_partido = st.sidebar.multiselect(
        "Filtrar por Partido Político:",
        options=df["Partido Político"].unique()
    )

    # Aplicar filtros
    df_filtrado = df[df["Impacto"].isin(filtro_impacto)]
    if filtro_partido:
        df_filtrado = df_filtrado[df_filtrado["Partido Político"].isin(filtro_partido)]

    # 4. Métricas en la parte superior
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Proyectos", len(df))
    m2.metric("Impacto Alto", len(df[df["Impacto"] == "ALTO"]))
    m3.metric("Impacto Medio", len(df[df["Impacto"] == "MEDIO"]))
    m4.metric("Última Actualización", df["Fecha de inicio"].max())

    # 5. Visualización de Datos
    tab1, tab2 = st.tabs(["📋 Detalle de Proyectos", "📊 Análisis Visual"])

    with tab1:
        st.write("Mostrando proyectos según filtros seleccionados:")
        # Configuramos st.column_config para que las celdas de texto largo no ocupen todo el espacio
        st.dataframe(
            df_filtrado, 
            column_config={
                "Proyecto": st.column_config.TextColumn("Título del Proyecto", width="large"),
                "Observaciones": st.column_config.TextColumn("Análisis Técnico", width="medium"),
            },
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.write("### Proyectos por Comisión")
            comisiones_data = df_filtrado["Comisiones"].value_counts()
            st.bar_chart(comisiones_data)

        with col_right:
            st.write("### Distribución por Partido")
            partido_data = df_filtrado["Partido Político"].value_counts()
            st.pie_chart(partido_data)

except Exception as e:
    st.error(f"Error al conectar con los datos: {e}")
    st.info("Asegurate de que el archivo requirements.txt contenga 'st-gsheets-connection' y que los Secrets estén configurados.")

# Footer
st.divider()
st.caption("Pasantía Asuntos Públicos - BBVA. Desarrollado con Streamlit & GitHub Actions.")
