from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI(title="API Monitor Legislativo BBVA")

# Nombre del archivo de respaldo
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

# Función para cargar datos al iniciar
def cargar_de_disco():
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Inicializamos la base de datos con lo que haya en disco
db_proyectos = cargar_de_disco()

@app.get("/")
def home():
    return {"status": "Online", "registros": len(db_proyectos)}

@app.post("/actualizar-datos")
def actualizar_datos(proyectos: List[Proyecto]):
    global db_proyectos
    try:
        # Convertimos a lista de dicts
        db_proyectos = [p.dict() for p in proyectos]
        
        # GUARDAMOS EN DISCO (Esto es la persistencia)
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(db_proyectos, f, ensure_ascii=False, indent=4)
            
        return {"status": "success", "mensaje": f"Guardados {len(db_proyectos)} registros en disco."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datos")
def obtener_datos():
    # Siempre devolvemos lo que hay en memoria (que se cargó al iniciar)
    return db_proyectos
