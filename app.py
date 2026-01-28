import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Monitor Legislativo BBVA", page_icon="🏛️", layout="wide")

# Estética corporativa BBVA
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #d1d8e0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Monitor de Actividad Parlamentaria")
st.subheader("Visualización vía API - Asuntos Públicos BBVA")

# URL de tu API en Render
API_URL = "https://prueba-9969.onrender.com/datos"

# 2. Función de carga de datos con manejo de caché y errores
@st.cache_data(ttl=60) # Actualiza automáticamente cada 1 minuto
def fetch_data():
    try:
        # Usamos un parámetro dummy para evitar respuestas cacheadas por el navegador
        response = requests.get(f"{API_URL}?update=true", timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            
            # Verificamos si la respuesta es una lista directa o un dict con clave 'datos'
            if isinstance(res_json, dict) and "datos" in res_json:
                data = res_json["datos"]
            else:
                data = res_json
                
            df = pd.DataFrame(data)
            
            if not df.empty:
                # Ordenar por ID descendente
                df = df.sort_values(by="ID", ascending=False)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.sidebar.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# --- CARGA DE DATOS ---
df = fetch_data()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Logo_BBVA.svg/2560px-Logo_BBVA.svg.png", width=150)
    st.write("### Opciones")
    if st.button("🔄 Sincronizar ahora"):
        st.cache_data.clear()
        st.rerun()

if not df.empty:
    # --- BLOQUE 1: MÉTRICAS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Proyectos Totales", len(df))
    col2.metric("Impacto ALTO", len(df[df['Impacto'] == 'ALTO']))
    col3.metric("Última Iniciativa", df['Fecha_de_inicio'].iloc[0])

    st.divider()

    # --- BLOQUE 2: VISUALIZACIONES INTERACTIVAS ---
    c_left, c_right = st.columns(2)

    with c_left:
        st.write("#### 📊 Distribución por Impacto")
        fig_pie = px.pie(df, names='Impacto', hole=0.4,
                         color='Impacto',
                         color_discrete_map={'ALTO':'#D35400', 'MEDIO':'#F39C12', 'BAJO':'#27AE60'})
        fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c_right:
        st.write("#### 🏛️ Proyectos por Partido")
        partidos = df['Partido_Politico'].value_counts().reset_index()
        fig_bar = px.bar(partidos, x='count', y='Partido_Politico', 
                         orientation='h',
                         labels={'count':'Cantidad', 'Partido_Politico':''},
                         color_discrete_sequence=['#004481'])
        fig_bar.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- BLOQUE 3: TABLA DE DATOS (ORDENADA Y SIN ID) ---
    st.write("### 🔍 Listado Detallado de Proyectos")
    
    # Creamos lista de columnas EXCLUYENDO el ID
    cols_to_show = [c for c in df.columns if c != "ID"]
    
    st.dataframe(
        df,
        column_order=cols_to_show, # Aquí forzamos a que NO muestre el ID
        hide_index=True,
        use_container_width=True,
        column_config={
            "Fecha_de_inicio": "Fecha",
            "Camara_de_Origen": "Cámara",
            "Proyecto": st.column_config.TextColumn("Título del Proyecto", width="large"),
            "Impacto": st.column_config.SelectboxColumn("Impacto", options=["ALTO", "MEDIO", "BAJO"]),
            "Observaciones": st.column_config.TextColumn("Análisis Técnico", width="medium")
        }
    )

else:
    # Mensaje amigable si la API devuelve vacío
    st.info("💡 **Aviso:** No se detectaron proyectos cargados. Si acabas de actualizar la planilla, presiona el botón 'Sincronizar ahora' en la barra lateral.")
    st.image("https://cdn.dribbble.com/users/252114/screenshots/3840347/no_data_found.png", width=400)
