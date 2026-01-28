import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Monitor BBVA", page_icon="🏛️", layout="wide")

# CSS personalizado para arreglar las tarjetas blancas y fuentes
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #004481; }
    [data-testid="stMetricLabel"] { font-size: 16px; color: #4b4b4b; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

API_URL = "https://prueba-9969.onrender.com/datos"

@st.cache_data(ttl=60)
def fetch_data():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            if not df.empty:
                # LIMPIEZA CRÍTICA: Filtrar solo Impactos válidos para que el gráfico no sea "raro"
                df = df[df['Impacto'].isin(['ALTO', 'MEDIO', 'BAJO'])]
                df = df.sort_values(by="ID", ascending=False)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

df_raw = fetch_data()

# --- BARRA LATERAL CON FILTROS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Logo_BBVA.svg/2560px-Logo_BBVA.svg.png", width=150)
    st.title("Filtros")
    
    # Filtro por Impacto
    filtro_impacto = st.multiselect("Nivel de Impacto", options=['ALTO', 'MEDIO', 'BAJO'], default=['ALTO', 'MEDIO', 'BAJO'])
    
    # Filtro por Cámara
    opciones_camara = df_raw['Camara_de_Origen'].unique().tolist() if not df_raw.empty else []
    filtro_camara = st.multiselect("Cámara", options=opciones_camara, default=opciones_camara)

    if st.button("🔄 Sincronizar API"):
        st.cache_data.clear()
        st.rerun()

# Aplicar filtros
if not df_raw.empty:
    df = df_raw[(df_raw['Impacto'].isin(filtro_impacto)) & (df_raw['Camara_de_Origen'].isin(filtro_camara))]
else:
    df = pd.DataFrame()

if not df.empty:
    # --- MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Proyectos", len(df))
    c2.metric("Impacto ALTO", len(df[df['Impacto'] == 'ALTO']))
    c3.metric("Partidos", df['Partido_Politico'].nunique())
    c4.metric("Provincias", df['Provincia'].nunique())

    st.markdown("---")

    # --- GRÁFICOS ---
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("##### 🎯 Prioridad de Seguimiento")
        fig_pie = px.pie(
            df, names='Impacto', 
            hole=0.5,
            color='Impacto',
            color_discrete_map={'ALTO':'#D35400', 'MEDIO':'#F39C12', 'BAJO':'#27AE60'},
            category_orders={"Impacto": ["ALTO", "MEDIO", "BAJO"]}
        )
        fig_pie.update_layout(margin=dict(t=20, b=0, l=0, r=0), legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("##### 🏛️ Actividad por Bloque Político")
        # Top 10 partidos para que no se vea amontonado
        partidos_count = df['Partido_Politico'].value_counts().head(10).reset_index()
        fig_bar = px.bar(
            partidos_count, x='count', y='Partido_Politico',
            orientation='h',
            labels={'count': 'Cantidad', 'index': ''},
            color='count', color_continuous_scale='Blues'
        )
        fig_bar.update_layout(margin=dict(t=20, b=0, l=0, r=0), showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- NUEVO GRÁFICO: MAPA DE CALOR POR PROVINCIA ---
    st.markdown("##### 🗺️ Distribución Geográfica de Autores")
    prov_count = df['Provincia'].value_counts().reset_index()
    fig_prov = px.bar(prov_count, x='Provincia', y='count', color_discrete_sequence=['#004481'])
    fig_prov.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_prov, use_container_width=True)

    st.markdown("---")

    # --- TABLA FINAL ---
    st.markdown("### 📋 Detalle de Proyectos Legislativos")
    cols_to_show = ["Fecha_de_inicio", "Camara_de_Origen", "Expediente", "Autor", "Proyecto", "Impacto", "Observaciones"]
    
    st.dataframe(
        df,
        column_order=cols_to_show,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Fecha_de_inicio": "Inicio",
            "Camara_de_Origen": "Cámara",
            "Proyecto": st.column_config.TextColumn("Título", width="large"),
            "Impacto": st.column_config.SelectboxColumn("Impacto", options=["ALTO", "MEDIO", "BAJO"]),
            "Observaciones": st.column_config.TextColumn("Análisis", width="medium")
        }
    )
else:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")
