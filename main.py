
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import datetime

app = FastAPI()

# Habilitar CORS para conexión con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENWEATHER_API_KEY = "6f5e9d4e1418f6edffda5a76396bbe41"

@app.get("/api/clima")
def obtener_clima(ciudad: str = Query(...)):
    """Obtiene el clima actual de una ciudad"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&units=metric&lang=es&appid={OPENWEATHER_API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        return {"error": "Error al obtener clima"}

    data = res.json()
    desc = data['weather'][0]['description']
    temp = data['main']['temp']
    viento = data['wind']['speed']
    alerta = "tormenta" in desc or viento > 40

    return {
        "ciudad": ciudad,
        "descripcion": desc,
        "temperatura": temp,
        "viento": viento,
        "alerta": alerta,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/alertas")
def alertas_regionales():
    """Obtiene alertas para varias ciudades claves en Argentina"""
    ciudades = [
        {"nombre": "Buenos Aires", "lat": -34.61, "lon": -58.38},
        {"nombre": "Córdoba", "lat": -31.42, "lon": -64.18},
        {"nombre": "Mendoza", "lat": -32.89, "lon": -68.83},
        {"nombre": "Salta", "lat": -24.79, "lon": -65.41},
        {"nombre": "Tucumán", "lat": -26.82, "lon": -65.22}
    ]
    alertas = []
    for ciudad in ciudades:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={ciudad['lat']}&lon={ciudad['lon']}&exclude=minutely,hourly,daily&units=metric&appid={OPENWEATHER_API_KEY}&lang=es"
        res = requests.get(url)
        if res.status_code != 200:
            continue
        data = res.json()
        if 'alerts' in data:
            for alerta in data['alerts']:
                alertas.append({
                    "ciudad": ciudad['nombre'],
                    "evento": alerta['event'],
                    "descripcion": alerta['description']
                })
    return {"alertas": alertas}

@app.get("/api/prediccion")
def prediccion_basica(viento: float = Query(...), descripcion: str = Query(...)):
    """Motor de predicción REA simplificado"""
    if "tormenta" in descripcion.lower() or viento > 50:
        nivel = "ALTA"
    elif viento > 30:
        nivel = "MEDIA"
    else:
        nivel = "BAJA"

    return {
        "descripcion": descripcion,
        "viento": viento,
        "riesgo": nivel
    }
