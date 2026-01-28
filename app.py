import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE PÁGINA (ESTILO DARK BBVA)
st.set_page_config(
    page_title="Monitor Legislativo | BBVA",
    layout="wide"
)

# Estilo CSS para emular el HTML proporcionado (Slate-900 background)
st.markdown("""
    <style>
    /* Fondo principal y gradiente */
    .main {
        background: linear-gradient(180deg, #0b1226 0%, #0f172a 100%);
        color: #e5e7eb;
    }
    
    /* Contenedor de métricas (KPIs) */
    [data-testid="stMetric"] {
        background-color: #1f2937;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 15px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Títulos de métricas en gris suave */
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 14px !important;
    }
    
    /* Valores de métricas en blanco/cyan */
    [data-testid="stMetricValue"] {
        color: #22d3ee !important;
        font-size: 24px !important;
    }

    /* Ajuste para que el texto de los inputs sea visible */
    .stMarkdown, p, h1, h2, h3, h4 {
        color: #f1f5f9 !important;
    }
    
    /* Separadores */
    hr {
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS DESDE LA API
API_URL = "https://prueba-9969.onrender.com/datos"

@st.cache_data(ttl=300)
def fetch_data():
    try:
        response = requests.get(API_URL, timeout=15)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            if not df.empty:
                # Regla de negocio solicitada aplicada en el front también por seguridad
                df.loc[df['Partido_Politico'].str.upper() == "PODER EJECUTIVO", 'Provincia'] = "NACIÓN"
                df['Impacto'] = df['Impacto'].fillna('BAJO').replace('', 'BAJO')
                df = df.sort_values(by="ID", ascending=False)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

df_raw = fetch_data()

# 3. HEADER PERSONALIZADO CON LOGO
col_text = st.columns([1, 4])

with col_text:
    st.markdown("<h1 style='margin-bottom:0'>Monitor Legislativo — Asuntos Públicos BBVA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8'>Inteligencia Regulatoria • Focos de Impacto • Seguimiento Territorial</p>", unsafe_allow_html=True)

st.markdown("---")

# 4. BARRA LATERAL (Filtros Estilo "Pills")
with st.sidebar:
    st.markdown("### Parámetros de Filtro")
    q = st.text_input("Buscador por palabra clave", "")
    
    st.markdown("---")
    f_impacto = st.multiselect("Nivel de Impacto", options=['ALTO', 'MEDIO', 'BAJO'], default=['ALTO', 'MEDIO', 'BAJO'])
    
    camaras = sorted(df_raw['Camara_de_Origen'].unique()) if not df_raw.empty else []
    f_camara = st.multiselect("Cámara de Origen", options=camaras, default=camaras)
    
    st.markdown("---")
    if st.button("Refrescar Datos"):
        st.cache_data.clear()
        st.rerun()

# Filtrar Datos
if not df_raw.empty:
    df = df_raw[(df_raw['Impacto'].isin(f_impacto)) & (df_raw['Camara_de_Origen'].isin(f_camara))]
    if q:
        df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
else:
    df = pd.DataFrame()

if not df.empty:
    # 5. BLOQUE DE KPIs (Tarjetas con fondo oscuro e íconos)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Proyectos Totales", len(df))
    c2.metric("Impacto Crítico", len(df[df['Impacto'] == 'ALTO']))
    c3.metric("Bloques Activos", df['Partido_Politico'].nunique())
    c4.metric("Autores", df['Autor'].nunique())

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. BLOQUE DE GRÁFICOS (Layout 1.2fr - 0.8fr como en tu HTML)
    col_main, col_side = st.columns([1.2, 0.8])

    with col_main:
        st.markdown("#### Iniciativas por Partido Político")
        # Gráfico de barras horizontales (Estilo azul BBVA)
        partidos = df['Partido_Politico'].value_counts().head(10).sort_values(ascending=True).reset_index()
        fig_bar = px.bar(
            partidos, x='count', y='Partido_Politico',
            orientation='h',
            template="plotly_dark",
            color_discrete_sequence=['#22d3ee'] # Cyan primario del código
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title=None, yaxis_title=None
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_side:
        st.markdown("#### Composición de Impacto")
        # Gráfico de Gauge / Donut para ejecución (simulando el gauge del HTML)
        fig_donut = px.pie(
            df, names='Impacto', hole=0.7,
            color='Impacto',
            color_discrete_map={'ALTO':'#ef4444', 'MEDIO':'#f59e0b', 'BAJO':'#22c55e'},
            template="plotly_dark"
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            annotations=[dict(text=f"{len(df[df['Impacto']=='ALTO'])} ALTO", x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # 7. TABLA DE DETALLE (Ocupa todo el ancho abajo)
    st.markdown("---")
    st.markdown("### Detalle de Iniciativas Legislativas")
    
    # Configuración de columnas visibles (Sin ID)
    cols_to_show = ["Camara_de_Origen", "Expediente", "Autor", "Partido_Politico", "Provincia", "Proyecto", "Impacto", "Observaciones"]
    
    st.dataframe(
        df,
        column_order=cols_to_show,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Camara_de_Origen": st.column_config.TextColumn("Cámara", width="small"),
            "Proyecto": st.column_config.TextColumn("Título del Proyecto", width="large"),
            "Impacto": st.column_config.TextColumn("Impacto", width="small"),
            "Partido_Politico": st.column_config.TextColumn("Bloque", width="medium"),
            "Observaciones": st.column_config.TextColumn("Análisis", width="medium")
        }
    )

else:
    st.info("No hay datos disponibles que coincidan con los filtros aplicados.")
