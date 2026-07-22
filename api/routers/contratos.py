"""
Endpoints de contratos públicos (Compras.gov.br + Portal da Transparência unificados).
"""

from typing import Optional

from fastapi import APIRouter, Query

from ..db import query

router = APIRouter(prefix="/contratos", tags=["contratos"])


@router.get("")
def listar_contratos(
    orgao: Optional[str] = Query(None, description="Busca parcial pelo nome do órgão"),
    fornecedor: Optional[str] = Query(None, description="Busca parcial pelo nome do fornecedor"),
    uf: Optional[str] = Query(None, description="Sigla da UF (apenas contratos do Compras.gov.br têm UF)"),
    fonte: Optional[str] = Query(None, description="compras.gov.br | portaldatransparencia.gov.br"),
    valor_min: Optional[float] = Query(None, ge=0),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    condicoes = []
    params: list = []

    if orgao:
        condicoes.append("orgaoNome ILIKE ?")
        params.append(f"%{orgao}%")
    if fornecedor:
        condicoes.append("fornecedorNome ILIKE ?")
        params.append(f"%{fornecedor}%")
    if uf:
        condicoes.append("uf = ?")
        params.append(uf.upper())
    if fonte:
        condicoes.append("fonte = ?")
        params.append(fonte)
    if valor_min is not None:
        condicoes.append("valor >= ?")
        params.append(valor_min)

    where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    sql = f"""
        SELECT * FROM contratos_publicos
        {where}
        ORDER BY data DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    return query(sql, params)
