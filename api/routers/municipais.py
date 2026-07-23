"""
Endpoints de cargos municipais eleitos (prefeito, vice-prefeito, vereador),
a partir do registro de candidatos do TSE (eleições 2024).

Diferente de pessoas_politicas (Câmara/Senado, mandato atual), aqui a fonte
é o registro de candidatura — por isso filtramos por DS_SIT_TOT_TURNO para
mostrar só quem se elegeu.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..db import query, query_one

router = APIRouter(prefix="/municipais", tags=["municipais"])

ELEITOS = "DS_SIT_TOT_TURNO ILIKE 'ELEITO%'"


@router.get("/politicos")
def listar_politicos_municipais(
    uf: Optional[str] = Query(None, description="Sigla da UF"),
    municipio: Optional[str] = Query(None, description="Busca parcial pelo nome do município"),
    cargo: Optional[str] = Query(None, description="PREFEITO | VICE-PREFEITO | VEREADOR"),
    nome: Optional[str] = Query(None, description="Busca parcial pelo nome do candidato"),
    limit: int = Query(24, le=100),
    offset: int = Query(0, ge=0),
):
    condicoes = [ELEITOS]
    params: list = []

    if uf:
        condicoes.append("SG_UF = ?")
        params.append(uf.upper())
    if municipio:
        condicoes.append("NM_UE ILIKE ?")
        params.append(f"%{municipio}%")
    if cargo:
        condicoes.append("DS_CARGO = ?")
        params.append(cargo.upper())
    if nome:
        condicoes.append("nome_normalizado ILIKE ?")
        params.append(f"%{nome.upper()}%")

    where = f"WHERE {' AND '.join(condicoes)}"
    sql = f"""
        SELECT SQ_CANDIDATO, NM_CANDIDATO, NM_URNA_CANDIDATO, SG_PARTIDO, SG_UF, NM_UE,
               DS_CARGO, DS_SIT_TOT_TURNO
        FROM stg_tse_candidatos
        {where}
        ORDER BY NM_UE, DS_CARGO, NM_CANDIDATO
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    return query(sql, params)


@router.get("/politicos/{sq_candidato}")
def detalhe_politico_municipal(sq_candidato: str):
    pessoa = query_one(
        "SELECT * FROM stg_tse_candidatos WHERE SQ_CANDIDATO = ?", [sq_candidato]
    )
    if not pessoa:
        raise HTTPException(status_code=404, detail="Candidato não encontrado")

    sancoes = query(
        "SELECT * FROM entidades_sancionadas WHERE sancionadoNome ILIKE ? LIMIT 20",
        [f"%{pessoa['NM_CANDIDATO']}%"],
    )
    return {**pessoa, "sancoesVinculadas": sancoes}


@router.get("/municipios")
def listar_municipios(uf: str = Query(..., description="Sigla da UF")):
    """Lista de municípios com candidatos eleitos numa UF — para popular um seletor."""
    return query(
        f"SELECT DISTINCT NM_UE FROM stg_tse_candidatos WHERE {ELEITOS} AND SG_UF = ? ORDER BY NM_UE",
        [uf.upper()],
    )
