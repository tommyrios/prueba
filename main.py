from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import subprocess
import threading
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Híbrida Monitor Legislativo")

# Habilitar CORS para que el dashboard pueda consultar la API sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKUP_FILE = "datos_monitor.json"

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

def cargar_de_disco():
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

db_proyectos = cargar_de_disco()

# --- ENDPOINTS DE LA API ---

@app.get("/")
def home():
    return {"status": "Online", "registros": len(db_proyectos), "nota": "Dashboard corriendo en puerto 8501"}

@app.post("/actualizar-datos")
def actualizar_datos(proyectos: List[Proyecto]):
    global db_proyectos
    try:
        db_proyectos = [p.dict() for p in proyectos]
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(db_proyectos, f, ensure_ascii=False, indent=4)
        return {"status": "success", "mensaje": "Datos actualizados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datos")
def obtener_datos():
    return db_proyectos

# --- LOGICA PARA CORRER STREAMLIT EN PARALELO ---

def run_streamlit():
    # Intentamos ejecutar streamlit apuntando al archivo app.py
    subprocess.run(["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"])

# Solo iniciamos Streamlit si el archivo app.py existe
if os.path.exists("app.py"):
    thread = threading.Thread(target=run_streamlit)
    thread.start()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
