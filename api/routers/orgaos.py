"""
Catálogo de órgãos públicos federais (SIAFI). Serve como glossário — os
demais dados (contratos, sanções) não têm um código de órgão em comum com o
SIAFI, então o cruzamento na página de detalhe é por nome, best-effort.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..db import paginar, query, query_one

router = APIRouter(prefix="/orgaos", tags=["orgaos"])

SUFIXOS_IGNORADOS = [" - Unidades com vínculo direto", " - Unidades Gestoras"]


def _termo_busca(descricao: str) -> str:
    """Extrai o núcleo do nome do órgão para cruzar por ILIKE com outras
    fontes (que não compartilham código com o SIAFI)."""
    nucleo = descricao
    for sufixo in SUFIXOS_IGNORADOS:
        nucleo = nucleo.replace(sufixo, "")
    palavras = [p for p in nucleo.split() if len(p) > 3]
    return " ".join(palavras[:4]) or nucleo


@router.get("")
def listar_orgaos(
    nome: Optional[str] = Query(
        None, description="Busca parcial pela descrição do órgão"
    ),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    condicoes = ["descricao NOT ILIKE '%CODIGO INVALIDO%'"]
    params: list = []
    if nome:
        condicoes.append("descricao ILIKE ?")
        params.append(f"%{nome}%")

    where = f"WHERE {' AND '.join(condicoes)}"
    return paginar(
        "codigo, descricao",
        f"FROM stg_transparencia_orgaos_siafi {where}",
        "ORDER BY descricao",
        params,
        limit,
        offset,
    )


@router.get("/{codigo}")
def detalhe_orgao(codigo: str):
    orgao = query_one(
        "SELECT codigo, descricao FROM stg_transparencia_orgaos_siafi WHERE codigo = ?",
        [codigo],
    )
    if not orgao:
        raise HTTPException(status_code=404, detail="Órgão não encontrado")

    termo = f"%{_termo_busca(orgao['descricao'])}%"
    contratos = query(
        "SELECT * FROM contratos_publicos WHERE orgaoNome ILIKE ? ORDER BY data DESC LIMIT 20",
        [termo],
    )
    sancoes = query(
        "SELECT * FROM entidades_sancionadas WHERE orgaoSancionador ILIKE ? ORDER BY dataInicioSancao DESC LIMIT 20",
        [termo],
    )
    return {**orgao, "contratosVinculados": contratos, "sancoesVinculadas": sancoes}
