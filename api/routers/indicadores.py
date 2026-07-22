"""
Indicadores agregados: economia (Bacen), socioeconômicos por UF (IBGE) e
finanças públicas (SICONFI).
"""

from typing import Optional

from fastapi import APIRouter, Query

from ..db import query

router = APIRouter(tags=["indicadores"])


@router.get("/economia/series")
def series_economicas(serie: Optional[str] = Query(None, description="Nome da série, ex: selic_meta")):
    if serie:
        return query(
            "SELECT * FROM stg_bacen_series WHERE serie = ? ORDER BY data DESC", [serie]
        )
    return query("SELECT * FROM stg_bacen_series ORDER BY serie, data DESC")


@router.get("/indicadores/uf")
def indicadores_por_uf(recurso: Optional[str] = Query(None, description="populacao_estimada_uf | pib_uf")):
    if recurso:
        return query(
            "SELECT * FROM stg_ibge_indicadores_uf WHERE recurso = ? ORDER BY valor DESC", [recurso]
        )
    return query("SELECT * FROM stg_ibge_indicadores_uf ORDER BY recurso, valor DESC")


@router.get("/financas/entes")
def entes_federativos(
    uf: Optional[str] = None,
    esfera: Optional[str] = Query(None, description="M (município) | E (estado) | U (união)"),
    limit: int = Query(100, le=500),
):
    condicoes = []
    params: list = []
    if uf:
        condicoes.append("uf = ?")
        params.append(uf.upper())
    if esfera:
        condicoes.append("esfera = ?")
        params.append(esfera.upper())

    where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    params.append(limit)
    return query(f"SELECT * FROM stg_siconfi_entes {where} LIMIT ?", params)


@router.get("/financas/balanco")
def balanco_patrimonial(
    sigla_ente: str = Query(..., description="Ex: União, SP, MG"),
    limit: int = Query(200, le=1000),
):
    return query(
        "SELECT * FROM stg_siconfi_dca WHERE siglaEnte = ? LIMIT ?", [sigla_ente, limit]
    )


@router.get("/judicial/processos")
def processos_judiciais(
    tribunal: Optional[str] = Query(None, description="STJ | TST | TRF1 | TJSP | TJRJ | TJMG"),
    limit: int = Query(50, le=500),
):
    if tribunal:
        return query(
            "SELECT * FROM stg_datajud_processos WHERE tribunal = ? ORDER BY dataUltimaAtualizacao DESC LIMIT ?",
            [tribunal.upper(), limit],
        )
    return query("SELECT * FROM stg_datajud_processos ORDER BY dataUltimaAtualizacao DESC LIMIT ?", [limit])


@router.get("/legislativo/senado/processos")
def processos_senado(tramitando: Optional[str] = Query(None, description="Sim | Não"), limit: int = Query(50, le=500)):
    if tramitando:
        return query(
            "SELECT * FROM stg_senado_processos WHERE tramitando = ? ORDER BY dataUltimaAtualizacao DESC LIMIT ?",
            [tramitando, limit],
        )
    return query("SELECT * FROM stg_senado_processos ORDER BY dataUltimaAtualizacao DESC LIMIT ?", [limit])
