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
        
        # --- EL ARREGLO ESTÁ ACÁ ---
        # Reemplazamos los NaN (celdas vacías) por un string vacío
        # Esto hace que los datos sean compatibles con JSON
        df = df.fillna("") 
        
        # Filtramos filas que realmente tengan un ID para no mandar basura
        df = df[df['ID'] != ""]
        
        # Convertimos a la lista de diccionarios
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
