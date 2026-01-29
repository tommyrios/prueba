import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Monitor Legislativo | BBVA", layout="wide")

# 2. ESTILO CSS (Técnico y sobrio)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #0b1226 0%, #0f172a 100%); }
    [data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 1px solid #1e293b !important;
        padding: 20px !important;
        border-radius: 4px !important;
    }
    [data-testid="stMetricValue"] { color: #00a9e0 !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; text-transform: uppercase; font-size: 12px !important; }
    h5 { color: #22d3ee !important; margin-top: 20px !important; font-weight: 500; }
    .stDataFrame { border: 1px solid #334155 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CARGA DE DATOS
API_URL = "https://prueba-9969.onrender.com/datos"

@st.cache_data(ttl=300)
def fetch_data():
    with st.spinner('Sincronizando inteligencia regulatoria...'):
        for intento in range(3):
            try:
                response = requests.get(f"{API_URL}?cache_bust=1", timeout=45)
                if response.status_code == 200:
                    df = pd.DataFrame(response.json())
                    if not df.empty:
                        df['Impacto'] = df['Impacto'].fillna('BAJO').replace('', 'BAJO')
                        df['Comisiones'] = df['Comisiones'].fillna('Sin Giro').replace('', 'Sin Giro')
                        df = df.sort_values(by="ID", ascending=False)
                    return df
            except:
                if intento < 2: time.sleep(2); continue
        return pd.DataFrame()

df_raw = fetch_data()

# 4. HEADER (Estructura solicitada)
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://logos-world.net/wp-content/uploads/2021/02/BBVA-Logo.png", width=140)
with col_title:
    st.markdown("<h2 style='margin:0; padding-top:10px;'>Dirección de Asuntos Públicos</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; margin:0;'>Análisis Predictivo de Riesgo Legislativo</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; margin:0;'>Inteligencia Regulatoria • Focos de Impacto • Seguimiento Territorial</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; margin:0;'>\n</p>", unsafe_allow_html=True)

# 5. BARRA LATERAL
with st.sidebar:
    st.markdown("### FILTROS")
    q = st.text_input("Buscador", placeholder="Palabra clave...")
    f_impacto = st.multiselect("Impacto", options=['ALTO', 'MEDIO', 'BAJO'], default=['ALTO', 'MEDIO', 'BAJO'])
    
    comis_list = sorted(df_raw['Comisiones'].unique()) if not df_raw.empty else []
    f_comision = st.multiselect("Giro a Comisiones", options=comis_list, default=comis_list)
    
    if st.button("Sincronizar Datos"):
        st.cache_data.clear()
        st.rerun()

# Filtrado
if not df_raw.empty:
    df = df_raw[(df_raw['Impacto'].isin(f_impacto)) & (df_raw['Comisiones'].isin(f_comision))]
    if q:
        df = df[df.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
else:
    df = pd.DataFrame()

# 6. DASHBOARD PRINCIPAL
if not df.empty:
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Proyectos", len(df))
    c2.metric("Impacto Alto", len(df[df['Impacto'] == 'ALTO']))
    c3.metric("Bloques", df['Partido_Politico'].nunique())
    c4.metric("Comisiones Activas", df['Comisiones'].nunique())

    st.markdown("<br>", unsafe_allow_html=True)

    # FILA GRÁFICOS 1
    g1, g2 = st.columns([1.2, 0.8])
    with g1:
        st.markdown("##### Volumen por Bloque Político")
        partidos_data = df['Partido_Politico'].value_counts().head(10).reset_index()
        partidos_data.columns = ['Partido', 'count']
        fig_bar = px.bar(partidos_data, x='count', y='Partido', orientation='h', 
                         template="plotly_dark", color_discrete_sequence=['#00a9e0'])
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, yaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True)
    with g2:
        st.markdown("##### Concentración de Riesgo")
        fig_pie = px.pie(df, names='Impacto', hole=0.7, template="plotly_dark",
                         color='Impacto', color_discrete_map={'ALTO':'#d32f2f', 'MEDIO':'#f9a825', 'BAJO':'#2e7d32'})
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # FILA GRÁFICOS 2: PREDICTIVO
    g3, g4 = st.columns(2)
    with g3:
        st.markdown("##### Foco Regulatorio (Top Comisiones)")
        comis_count = df['Comisiones'].str.split(',').explode().str.strip().value_counts().head(10).reset_index()
        comis_count.columns = ['Comision', 'count']
        fig_com = px.bar(comis_count, x='count', y='Comision', orientation='h', 
                         template="plotly_dark", color_discrete_sequence=['#22d3ee'])
        fig_com.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, yaxis_title=None)
        st.plotly_chart(fig_com, use_container_width=True)
        
    with g4:
        st.markdown("##### Autores con Mayor Actividad")
        autores = df['Autor'].value_counts().head(10).reset_index()
        autores.columns = ['Autor', 'count']
        fig_aut = px.scatter(autores, x='count', y='Autor', size='count', 
                             template="plotly_dark", color_discrete_sequence=['#00a9e0'])
        fig_aut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, yaxis_title=None)
        st.plotly_chart(fig_aut, use_container_width=True)

    # TABLA FINAL
    st.markdown("---")
    st.markdown("##### Análisis de Expedientes")
    st.dataframe(df, hide_index=True, use_container_width=True,
                 column_order=["Camara_de_Origen", "Expediente", "Autor", "Comisiones", "Proyecto", "Impacto"],
                 column_config={"Proyecto": st.column_config.TextColumn("Título", width="large"),
                                "Comisiones": st.column_config.TextColumn("Giro / Comisiones", width="medium")})
else:
    st.info("No se detectaron registros para mostrar.")
