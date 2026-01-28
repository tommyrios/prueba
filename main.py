from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd

app = FastAPI()

# Modelo de datos para validar lo que viene de GitHub
class Proyecto(BaseModel):
    id: str
    proyecto: str
    impacto: str
    autor: str
    comisiones: str

# Base de datos temporal (en un entorno real usarías SQL)
db_proyectos = []

@app.get("/")
def home():
    return {"status": "Monitor Legislativo API Activa"}

# Endpoint para recibir datos desde GitHub Actions
@app.post("/actualizar-datos")
def actualizar(datos: List[Proyecto]):
    global db_proyectos
    db_proyectos = [d.dict() for d in datos]
    return {"message": f"Se cargaron {len(db_proyectos)} proyectos con éxito"}

# Endpoint para que Streamlit consuma los datos
@app.get("/datos")
def obtener_datos():
    return db_proyectos
