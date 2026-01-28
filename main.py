from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Monitor Legislativo BBVA")

# Configuración de CORS para permitir que Streamlit acceda sin problemas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la fuente de datos
SHEET_ID = "16aksCoBrIFB6Vy8JpiuVBEpfGNHdUNJcsCKb2k33tsQ"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
BACKUP_FILE = "datos_monitor.json"

# Esquema de datos
class Proyecto(BaseModel):
    ID: str
    Camara_de_Origen: str
    Expediente: str
    Autor: str
    Fecha_de_inicio: str
    Proyecto: str
    Comisiones: str
    Impacto: str
    Partido_Politico: str
    Provincia: str
    Observaciones: Optional[str] = None

db_proyectos = []

def ejecutar_carga_desde_sheet():
    """Función para leer el Google Sheet y actualizar la memoria"""
    global db_proyectos
    try:
        print("🔄 Iniciando carga desde Google Sheets...")
        df = pd.read_csv(URL_CSV)
        
        # Limpieza y renombramiento para que coincida con el modelo Proyecto
        df = df.fillna("")
        df = df.rename(columns={
            "Cámara de Origen": "Camara_de_Origen",
            "Fecha de inicio": "Fecha_de_inicio",
            "Partido Político": "Partido_Politico"
        })
        
        # Filtrar solo las filas que tengan un ID válido
        df = df[df['ID'] != ""]
        
        # Actualizar base de datos en memoria
        db_proyectos = df.to_dict(orient="records")
        
        # Guardar backup local por seguridad
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(db_proyectos, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Carga completada: {len(db_proyectos)} registros.")
    except Exception as e:
        print(f"❌ Error en la carga automática: {e}")

# --- EVENTO DE INICIO ---
# Esto hace que la carga ocurra automáticamente al desplegar o reiniciar
@app.on_event("startup")
def startup_event():
    ejecutar_carga_desde_sheet()

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {
        "status": "Online",
        "organizacion": "BBVA Asuntos Públicos",
        "registros_en_memoria": len(db_proyectos)
    }

@app.get("/datos")
def obtener_datos():
    """Endpoint que consume Streamlit"""
    if not db_proyectos:
        # Si la memoria está vacía, intentamos cargar de nuevo antes de responder
        ejecutar_carga_desde_sheet()
    return db_proyectos

@app.post("/actualizar-datos")
def actualizar_datos(proyectos: List[Proyecto]):
    """Endpoint para actualizaciones manuales o via GitHub Actions"""
    global db_proyectos
    try:
        db_proyectos = [p.dict() for p in proyectos]
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(db_proyectos, f, ensure_ascii=False, indent=4)
        return {"status": "success", "mensaje": f"Se recibieron {len(db_proyectos)} registros."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/forzar-recarga")
def forzar_recarga():
    """Endpoint manual por si querés disparar la recarga desde el navegador"""
    ejecutar_carga_desde_sheet()
    return {"status": "success", "registros": len(db_proyectos)}
