"""
Endpoints de pessoas políticas (deputados + senadores unificados por nome).
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..db import paginar, query, query_one

router = APIRouter(prefix="/pessoas", tags=["pessoas"])


@router.get("")
def listar_pessoas(
    nome: Optional[str] = Query(None, description="Busca parcial por nome (case-insensitive)"),
    casa: Optional[str] = Query(None, description="Câmara | Senado | Câmara e Senado"),
    partido: Optional[str] = Query(None, description="Sigla do partido"),
    uf: Optional[str] = Query(None, description="Sigla da UF"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    condicoes = []
    params: list = []

    if nome:
        condicoes.append("nome_normalizado ILIKE ?")
        params.append(f"%{nome.upper()}%")
    if casa:
        condicoes.append("casa = ?")
        params.append(casa)
    if partido:
        condicoes.append("(camaraPartido = ? OR senadoPartido = ?)")
        params.extend([partido, partido])
    if uf:
        condicoes.append("(camaraUf = ? OR senadoUf = ?)")
        params.extend([uf, uf])

    where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    select = """slug, nome, casa, camaraId, camaraPartido, camaraUf, camaraFoto,
               senadoId, senadoPartido, senadoUf, senadoFoto"""
    return paginar(select, f"FROM pessoas_politicas {where}", "ORDER BY nome", params, limit, offset)


@router.get("/{slug}")
def detalhe_pessoa(slug: str):
    pessoa = query_one("SELECT * FROM pessoas_politicas WHERE slug = ?", [slug])
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    nome_normalizado = pessoa["nome_normalizado"]

    # Sanções e contratos vinculados por nome (melhor cruzamento disponível hoje —
    # não há CPF público em comum entre as fontes federais e o TSE municipal).
    sancoes = query(
        "SELECT * FROM entidades_sancionadas WHERE sancionadoNome ILIKE ? LIMIT 20",
        [f"%{pessoa['nome']}%"],
    )
    contratos = query(
        "SELECT * FROM contratos_publicos WHERE fornecedorNome ILIKE ? ORDER BY data DESC LIMIT 20",
        [f"%{pessoa['nome']}%"],
    )
    votacoes = []
    if pessoa.get("senadoId"):
        votacoes = query(
            "SELECT * FROM stg_senado_votacoes WHERE codigoSenador = ? ORDER BY dataSessao DESC LIMIT 20",
            [str(int(float(pessoa["senadoId"])))] if pessoa["senadoId"] else [],
        )

    legislaturas_camara = []
    if pessoa.get("camaraId"):
        legislaturas_camara = query(
            "SELECT idLegislatura, siglaPartido, siglaUf FROM stg_camara_legislaturas "
            "WHERE id = ? ORDER BY idLegislatura DESC",
            [int(pessoa["camaraId"])],
        )

    legislaturas_senado = []
    if pessoa.get("senadoId"):
        legislaturas_senado = query(
            "SELECT numeroLegislatura, dataInicio, dataFim, siglaUf, participacao "
            "FROM stg_senado_legislaturas WHERE id = ? ORDER BY numeroLegislatura DESC",
            [str(int(float(pessoa["senadoId"])))],
        )

    return {
        **pessoa,
        "sancoesVinculadas": sancoes,
        "contratosVinculados": contratos,
        "votacoesRecentes": votacoes,
        "legislaturasCamara": legislaturas_camara,
        "legislaturasSenado": legislaturas_senado,
    }
