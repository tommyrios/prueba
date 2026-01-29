from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Monitor Legislativo BBVA")

# Habilitar CORS para que Streamlit pueda consultar la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SHEET_ID = "16aksCoBrIFB6Vy8JpiuVBEpfGNHdUNJcsCKb2k33tsQ"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
BACKUP_FILE = "datos_monitor.json"

db_proyectos = []

def ejecutar_carga_desde_sheet():
    global db_proyectos
    try:
        print("Sincronizando con Google Sheets...")
        df = pd.read_csv(URL_CSV).fillna("")
        
        # Regla de negocio: Poder Ejecutivo -> Nación
        if 'Partido Político' in df.columns:
            mask = df['Partido Político'].str.upper().str.strip() == "PODER EJECUTIVO"
            df.loc[mask, 'Provincia'] = "NACIÓN"
            
        # Renombrar columnas para la API
        df = df.rename(columns={
            "Cámara de Origen": "Camara_de_Origen",
            "Fecha de inicio": "Fecha_de_inicio",
            "Partido Político": "Partido_Politico"
        })
        
        db_proyectos = df.to_dict(orient="records")
        
        # Guardar backup local
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(db_proyectos, f, ensure_ascii=False, indent=4)
        print(f"Sincronización exitosa: {len(db_proyectos)} registros.")
    except Exception as e:
        print(f"Error en carga: {e}")

@app.on_event("startup")
def startup_event():
    ejecutar_carga_desde_sheet()

@app.get("/")
def home():
    return {"status": "online", "registros": len(db_proyectos)}

@app.get("/datos")
def obtener_datos():
    if not db_proyectos:
        ejecutar_carga_desde_sheet()
    return db_proyectos

@app.get("/forzar-recarga")
def forzar_recarga():
    ejecutar_carga_desde_sheet()
    return {"status": "success", "registros": len(db_proyectos)}
