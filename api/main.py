"""
Ponto de entrada da API. Roda com:
    poetry run uvicorn api.main:app --reload --port 8000

Documentação interativa em /docs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import WAREHOUSE_PATH
from .routers import busca, contratos, indicadores, pessoas, sancoes

app = FastAPI(
    title="Câmara Analytics API",
    description="Dados públicos do governo brasileiro, tratados e unificados.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringir ao domínio do frontend em produção
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(pessoas.router)
app.include_router(sancoes.router)
app.include_router(contratos.router)
app.include_router(busca.router)
app.include_router(indicadores.router)


@app.get("/", tags=["health"])
def health():
    return {
        "status": "ok",
        "warehouse": str(WAREHOUSE_PATH),
        "warehouse_existe": WAREHOUSE_PATH.exists(),
    }
