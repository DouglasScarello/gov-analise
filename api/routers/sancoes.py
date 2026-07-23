"""
Endpoints de sanções (CEIS + CNEP unificados) — empresas/pessoas impedidas
de contratar com o poder público ou punidas por corrupção.
"""

from typing import Optional

from fastapi import APIRouter, Query

from ..db import paginar

router = APIRouter(prefix="/sancoes", tags=["sancoes"])


@router.get("")
def listar_sancoes(
    nome: Optional[str] = Query(None, description="Busca parcial pelo nome do sancionado"),
    documento: Optional[str] = Query(None, description="CPF/CNPJ, apenas dígitos"),
    origem: Optional[str] = Query(None, description="CEIS | CNEP"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    condicoes = []
    params: list = []

    if nome:
        condicoes.append("sancionadoNome ILIKE ?")
        params.append(f"%{nome}%")
    if documento:
        condicoes.append("sancionadoDocumentoDigitos = ?")
        params.append("".join(c for c in documento if c.isdigit()))
    if origem:
        condicoes.append("origemSancao = ?")
        params.append(origem.upper())

    where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    return paginar("*", f"FROM entidades_sancionadas {where}", "ORDER BY dataInicioSancao DESC", params, limit, offset)
