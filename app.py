import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Monitor Legislativo | BBVA",
    layout="wide"
)

# 2. ESTILO CSS PARA ALTO CONTRASTE Y LOGO
st.markdown("""
    <style>
    /* Fondo principal Dark Slate */
    .stApp {
        background: linear-gradient(180deg, #0b1226 0%, #0f172a 100%);
    }
    
    /* Títulos y textos generales */
    h1, h2, h3, h4, h5, p, span, label {
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Tarjetas de métricas (KPIs) - Alto Contraste */
    [data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 1px solid #1e293b !important;
        padding: 20px !important;
        border-radius: 4px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Valores de métricas en Cyan Institucional */
    [data-testid="stMetricValue"] {
        color: #00a9e0 !important;
        font-weight: 700 !important;
    }
    
    /* Etiquetas de métricas */
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 12px !important;
    }

    /* Input de búsqueda y selects */
    .stTextInput input {
        background-color: #0f172a !important;
        color: #f1f5f9 !important;
        border: 1px solid #334155 !important;
    }

    /* Tabla de datos */
    .stDataFrame {
        border: 1px solid #334155 !important;
    }

    /* Logo Header */
    .logo-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CARGA DE DATOS
API_URL = "https://prueba-9969.onrender.com/datos"

@st.cache_data(ttl=300)
def fetch_data():
    try:
        response = requests.get(f"{API_URL}?cache_bust=1", timeout=15)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            if not df.empty:
                # Regla de negocio: Poder Ejecutivo -> Nación
                mask = df['Partido_Politico'].str.upper().str.strip() == "PODER EJECUTIVO"
                df.loc[mask, 'Provincia'] = "NACIÓN"
                
                df['Impacto'] = df['Impacto'].fillna('BAJO').replace('', 'BAJO')
                df = df.sort_values(by="ID", ascending=False)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

df_raw = fetch_data()

# 4. HEADER (Sin emojis, Logo corregido)
col_logo, col_title = st.columns([1, 5])

with col_logo:
    # URL alternativa del logo de BBVA (Vectorial estable)
    logo_url = "https://logos-world.net/wp-content/uploads/2021/02/BBVA-Logo.png"
    st.image(logo_url, width=150)

with col_title:
    st.markdown("<h2 style='margin:0; padding-top:10px;'>Monitor Legislativo — Asuntos Públicos</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; margin:0;'>Análisis de Impacto Legislativo y Riesgo Regulatorio</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; margin:0;'>Inteligencia Regulatoria • Focos de Impacto • Seguimiento Territorial</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; margin:0;'>\n</p>", unsafe_allow_html=True)

# 5. BARRA LATERAL (Sobria)
with st.sidebar:
    st.markdown("### FILTROS")
    q = st.text_input("Buscar por palabra clave", placeholder="Ej: Energía")
    
    f_impacto = st.multiselect("Nivel de Impacto", options=['ALTO', 'MEDIO', 'BAJO'], default=['ALTO', 'MEDIO', 'BAJO'])
    
    camaras = sorted(df_raw['Camara_de_Origen'].unique()) if not df_raw.empty else []
    f_camara = st.multiselect("Cámara de Origen", options=camaras, default=camaras)
    
    st.markdown("---")
    if st.button("Sincronizar Datos"):
        st.cache_data.clear()
        st.rerun()

# Lógica de filtrado
if not df_raw.empty:
    df = df_raw[(df_raw['Impacto'].isin(f_impacto)) & (df_raw['Camara_de_Origen'].isin(f_camara))]
    if q:
        df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
else:
    df = pd.DataFrame()

# 6. CUERPO PRINCIPAL
if not df.empty:
    # FILA 1: KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Proyectos Analizados", len(df))
    c2.metric("Impacto Alto", len(df[df['Impacto'] == 'ALTO']))
    c3.metric("Bloques Políticos", df['Partido_Politico'].nunique())
    c4.metric("Provincias", df['Provincia'].nunique())

    st.markdown("<br>", unsafe_allow_html=True)

    # FILA 2: GRÁFICOS (Layout Técnico 1.2fr - 0.8fr)
    col_main, col_side = st.columns([1.2, 0.8])

    with col_main:
        st.markdown("##### Iniciativas por Bloque Político")
        partidos = df['Partido_Politico'].value_counts().head(10).sort_values(ascending=True).reset_index()
        fig_bar = px.bar(
            partidos, x='count', y='Partido_Politico',
            orientation='h',
            template="plotly_dark",
            color_discrete_sequence=['#00a9e0'] # Azul BBVA
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title=None, yaxis_title=None, height=350,
            font=dict(color="#f1f5f9")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_side:
        st.markdown("##### Categorización de Riesgo")
        fig_donut = px.pie(
            df, names='Impacto', hole=0.7,
            color='Impacto',
            color_discrete_map={'ALTO':'#d32f2f', 'MEDIO':'#f9a825', 'BAJO':'#2e7d32'},
            template="plotly_dark"
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', showlegend=True,
            legend=dict(orientation="h", y=-0.1, x=0.1),
            margin=dict(t=0, b=50, l=0, r=0), height=350,
            annotations=[dict(text="Distribución", x=0.5, y=0.5, font_size=14, showarrow=False, font_color="#94a3b8")]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # FILA 3: TABLA DE DETALLE
    st.markdown("---")
    st.markdown("##### Detalle de Iniciativas Legislativas")
    
    # Columnas técnicas
    cols_to_show = ["Camara_de_Origen", "Expediente", "Autor", "Partido_Politico", "Provincia", "Proyecto", "Impacto", "Observaciones"]
    
    st.dataframe(
        df,
        column_order=cols_to_show,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Camara_de_Origen": "Cámara",
            "Proyecto": st.column_config.TextColumn("Título", width="large"),
            "Partido_Politico": "Bloque",
            "Observaciones": st.column_config.TextColumn("Análisis Técnico", width="medium"),
            "Fecha_de_inicio": "Fecha"
        }
    )

else:
    st.info("No se encontraron registros para los criterios seleccionados.")
