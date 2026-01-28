import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuración de pantalla completa
st.set_page_config(page_title="Dashboard Legislativo BBVA", page_icon="🏛️", layout="wide")

# Estilo CSS para mejorar la estética
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Monitor de Actividad Parlamentaria")
st.subheader("Análisis Estratégico de Impacto Regulatorio")

API_URL = "https://prueba-9969.onrender.com/datos"

@st.cache_data(ttl=60)
def fetch_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            # Limpieza y Orden
            if not df.empty:
                # Convertimos ID a numérico si es posible para un orden lógico (ej: PL134 -> 134)
                # O simplemente ordenamos alfabético descendente
                df = df.sort_values(by="ID", ascending=False)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

df = fetch_data()

if not df.empty:
    # --- BLOQUE 1: MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    total = len(df)
    alto_impacto = len(df[df['Impacto'] == 'ALTO'])
    ult_fecha = df['Fecha_de_inicio'].iloc[0] # Al estar ordenado desc, el primero es el más nuevo
    
    m1.metric("Total Proyectos", total)
    m2.metric("Impacto ALTO", alto_impacto, delta_color="inverse")
    m3.metric("Última Actualización", ult_fecha)
    m4.metric("Cámaras", f"{df['Camara_de_Origen'].nunique()}")

    st.divider()

    # --- BLOQUE 2: GRÁFICOS ---
    col1, col2 = st.columns(2)

    with col1:
        st.write("#### 📊 Distribución por Nivel de Impacto")
        # Gráfico de Torta (Donut)
        fig_impacto = px.pie(df, names='Impacto', hole=0.4, 
                             color='Impacto',
                             color_discrete_map={'ALTO':'#E74C3C', 'MEDIO':'#F1C40F', 'BAJO':'#2ECC71'})
        fig_impacto.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_impacto, use_container_width=True)

    with col2:
        st.write("#### 🏛️ Proyectos por Partido Político")
        # Gráfico de Barras Horizontal
        partidos = df['Partido_Politico'].value_counts().reset_index()
        fig_partido = px.bar(partidos, x='count', y='Partido_Politico', 
                             orientation='h', labels={'count':'Cantidad', 'Partido_Politico':''},
                             color='count', color_continuous_scale='Blues')
        fig_partido.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_partido, use_container_width=True)

    st.write("#### 📂 Concentración por Comisiones")
    # Para comisiones, a veces vienen varias separadas por coma. 
    # Esto las separa para contarlas individualmente (Toque de Ingeniería)
    comisiones_list = df['Comisiones'].str.split(', ').explode()
    fig_com = px.bar(comisiones_list.value_counts().head(10), 
                     color_discrete_sequence=['#004481']) # Azul BBVA
    fig_com.update_layout(xaxis_title="", yaxis_title="Cantidad", showlegend=False)
    st.plotly_chart(fig_com, use_container_width=True)

    st.divider()

    # --- BLOQUE 3: LA TABLA (AL FINAL) ---
    st.write("### 🔍 Detalle de Iniciativas Legislativas")
    
    # Configuramos las columnas para ocultar el ID y mejorar títulos
    columnas_visibles = [col for col in df.columns if col != "ID"]
    
    st.dataframe(
        df,
        column_order=columnas_visibles, # El ID no está en esta lista, por lo que desaparece
        hide_index=True,
        use_container_width=True,
        column_config={
            "Proyecto": st.column_config.TextColumn("Resumen del Proyecto", width="large"),
            "Fecha_de_inicio": "Fecha",
            "Impacto": st.column_config.SelectboxColumn("Impacto", options=["ALTO", "MEDIO", "BAJO"]),
            "Observaciones": st.column_config.TextColumn("Análisis Técnico", width="medium")
        }
    )

else:
    st.error("No se pudieron cargar los datos de la API. Verificá que el servidor en Render esté activo.")
