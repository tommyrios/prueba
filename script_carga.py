import pandas as pd
import requests

# 1. URL de tu planilla (exportada como CSV para lectura rápida)
SHEET_ID = "16aksCoBrIFB6Vy8JpiuVBEpfGNHdUNJcsCKb2k33tsQ"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 2. URL de tu API en Render
API_URL = "https://prueba-9969.onrender.com/actualizar-datos"

def ejecutar_carga():
    try:
        # Leemos los datos
        df = pd.read_csv(URL_CSV)
        
        # 1. Limpieza de NaN
        df = df.fillna("")
        
        # 2. MAPEAMOS LOS NOMBRES (De Planilla -> A nombres de API)
        # Esto corrige el error 422
        df = df.rename(columns={
            "Cámara de Origen": "Camara_de_Origen",
            "Fecha de inicio": "Fecha_de_inicio",
            "Partido Político": "Partido_Politico"
        })
        
        # 3. Filtramos filas vacías
        df = df[df['ID'] != ""]
        
        # Convertimos a JSON
        proyectos = df.to_dict(orient="records")
        
        # Enviamos el POST
        response = requests.post(API_URL, json=proyectos)
        
        if response.status_code == 200:
            print(f"✅ Éxito: {len(proyectos)} proyectos cargados.")
        else:
            print(f"❌ Error API: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"🚨 Error en el proceso: {e}")

if __name__ == "__main__":
    ejecutar_carga()
