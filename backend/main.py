from pathlib import Path
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API - Acoplamento Solar-Magnetosfera")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTADOS_PATH = Path(__file__).parent / "resultados.json"


@app.get("/api/resultados")
def obter_resultados():
    with open(RESULTADOS_PATH, encoding="utf-8") as f:
        return json.load(f)
