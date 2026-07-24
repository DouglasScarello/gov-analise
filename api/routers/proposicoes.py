"""
Proposições legislativas (Câmara + Senado) unificadas em
proposicoes_legislativas — hoje só apareciam embutidas no perfil de um
político; aqui ficam pesquisáveis por conta própria.
"""

from typing import Optional

from fastapi import APIRouter, Query

from ..db import paginar, query

router = APIRouter(prefix="/proposicoes", tags=["proposicoes"])


@router.get("/tipos")
def listar_tipos():
    """Tipos de proposição com registros, para montar um filtro no frontend."""
    return query(
        "SELECT tipoSigla, COUNT(*) AS total FROM proposicoes_legislativas "
        "GROUP BY tipoSigla ORDER BY total DESC"
    )


@router.get("")
def listar_proposicoes(
    casa: Optional[str] = Query(None, description="Camara | Senado"),
    tipoSigla: Optional[str] = Query(None, description="Ex: PL, PEC, REQ"),
    ano: Optional[int] = Query(None),
    q: Optional[str] = Query(None, description="Busca parcial na ementa"),
    limit: int = Query(24, le=100),
    offset: int = Query(0, ge=0),
):
    condicoes = []
    params: list = []

    if casa:
        condicoes.append("casa = ?")
        params.append(casa)
    if tipoSigla:
        condicoes.append("tipoSigla = ?")
        params.append(tipoSigla.upper())
    if ano:
        condicoes.append("ano = ?")
        params.append(str(ano))
    if q:
        condicoes.append("ementa ILIKE ?")
        params.append(f"%{q}%")

    where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    return paginar(
        "casa, autorId, tipoSigla, numero, ano, ementa, dataApresentacao, url",
        f"FROM proposicoes_legislativas {where}",
        "ORDER BY dataApresentacao DESC",
        params,
        limit,
        offset,
    )
