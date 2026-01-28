import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Monitor Legislativo BBVA", page_icon="🏛️", layout="wide")

st.title("🏛️ Monitor de Actividad Parlamentaria")
st.subheader("Visualización vía API - Asuntos Públicos BBVA")

# Reemplaza con tu URL de Render (la que termina en /datos)
API_URL = "https://prueba-9969.onrender.com/datos"

@st.cache_data(ttl=600)  # Actualiza cada 10 minutos
def fetch_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return None
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

df = fetch_data()

if df is not None and not df.empty:
    # Métricas rápidas
    c1, c2, c3 = st.columns(3)
    c1.metric("Proyectos en API", len(df))
    c2.metric("Impacto ALTO", len(df[df['Impacto'] == 'ALTO']))
    
    # Tabla interactiva
    st.write("### Últimos proyectos detectados")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Un gráfico simple para ver que todo fluye
    st.bar_chart(df['Impacto'].value_counts())
else:
    st.warning("Todavía no hay datos disponibles en la API.")
