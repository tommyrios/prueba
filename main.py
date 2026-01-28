from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

app = FastAPI(title="API Monitor Legislativo BBVA")

# 1. Definimos el modelo de datos exacto de tu tabla
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

# 2. Base de datos en memoria (se resetea si la API se reinicia)
# Para una pasantía esto sobra, si escala usaríamos una DB real.
db_proyectos = []

@app.get("/")
def home():
    return {
        "status": "Online",
        "organizacion": "Asuntos Públicos - BBVA",
        "registros_actuales": len(db_proyectos)
    }

# 3. Endpoint para recibir los datos desde GitHub Actions
@app.post("/actualizar-datos")
def actualizar_datos(proyectos: List[Proyecto]):
    global db_proyectos
    try:
        # Convertimos la lista de objetos Pydantic a una lista de diccionarios
        db_proyectos = [p.dict() for p in proyectos]
        return {
            "status": "success", 
            "mensaje": f"Se actualizaron {len(db_proyectos)} registros correctamente."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Endpoint para que Streamlit consuma los datos
@app.get("/datos")
def obtener_datos():
    if not db_proyectos:
        return {"mensaje": "No hay datos cargados aún", "datos": []}
    return db_proyectos

if __name__ == "__main__":
    import uvicorn
    import os
    # Render asigna un puerto dinámico en la variable de entorno PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
