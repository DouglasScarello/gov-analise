"""
Ponto de entrada da API. Roda com:
    poetry run uvicorn api.main:app --reload --port 8000

Documentação interativa em /docs.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import WAREHOUSE_PATH
from .routers import busca, cargos, contratos, indicadores, municipais, pessoas, sancoes

load_dotenv()

# Em produção, defina CORS_ALLOWED_ORIGINS no .env com o(s) domínio(s) do
# frontend, separados por vírgula (ex: "https://govanalise.com.br"). Sem essa
# variável, assume-se ambiente de desenvolvimento local.
_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = (
    [o.strip() for o in _origins_env.split(",") if o.strip()]
    if _origins_env
    else ["http://localhost:3000", "http://127.0.0.1:3000"]
)

app = FastAPI(
    title="Câmara Analytics API",
    description="Dados públicos do governo brasileiro, tratados e unificados.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(pessoas.router)
app.include_router(sancoes.router)
app.include_router(contratos.router)
app.include_router(busca.router)
app.include_router(indicadores.router)
app.include_router(municipais.router)
app.include_router(cargos.router)


@app.get("/", tags=["health"])
def health():
    return {
        "status": "ok",
        "warehouse": str(WAREHOUSE_PATH),
        "warehouse_existe": WAREHOUSE_PATH.exists(),
    }
