"""
Endpoints de pessoas políticas (deputados + senadores unificados por nome).
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..db import paginar, query, query_one

router = APIRouter(prefix="/pessoas", tags=["pessoas"])


@router.get("")
def listar_pessoas(
    nome: Optional[str] = Query(
        None, description="Busca parcial por nome (case-insensitive)"
    ),
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
    return paginar(
        select,
        f"FROM pessoas_politicas {where}",
        "ORDER BY nome",
        params,
        limit,
        offset,
    )


@router.get("/{slug}")
def detalhe_pessoa(slug: str):
    pessoa = query_one("SELECT * FROM pessoas_politicas WHERE slug = ?", [slug])
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    nome_normalizado = pessoa["nome_normalizado"]

    # Dados biográficos (gênero, cor/raça, escolaridade, ocupação declarada) só
    # existem no registro de candidatura do TSE, não nas APIs de Câmara/Senado —
    # busca pela candidatura mais recente da própria pessoa ao cargo que ocupa
    # hoje (nome normalizado + cargo == mandato atual, risco de homônimo baixo
    # porque filtra pelo cargo exato, não é um cruzamento genérico por nome).
    cargo_tse = "DEPUTADO FEDERAL" if pessoa["casa"] == "Câmara" else "SENADOR"
    bio = query_one(
        "SELECT DS_GENERO AS genero, DS_COR_RACA AS corRaca, "
        "DS_GRAU_INSTRUCAO AS escolaridade, DS_OCUPACAO AS ocupacao "
        "FROM stg_tse_candidatos_geral "
        "WHERE (nome_normalizado = ? OR nome_urna_normalizado = ?) AND DS_CARGO = ? "
        "ORDER BY ANO_ELEICAO DESC LIMIT 1",
        [nome_normalizado, nome_normalizado, cargo_tse],
    )

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

    proposicoes = []
    if pessoa.get("camaraId"):
        proposicoes += query(
            "SELECT casa, tipoSigla, numero, ano, ementa, dataApresentacao, url "
            "FROM proposicoes_legislativas WHERE casa = 'Camara' AND autorId = ? "
            "ORDER BY dataApresentacao DESC",
            [str(int(pessoa["camaraId"]))],
        )
    if pessoa.get("senadoId"):
        proposicoes += query(
            "SELECT casa, tipoSigla, numero, ano, ementa, dataApresentacao, url "
            "FROM proposicoes_legislativas WHERE casa = 'Senado' AND autorId = ? "
            "ORDER BY dataApresentacao DESC",
            [str(int(float(pessoa["senadoId"])))],
        )

    # Histórico completo de candidaturas no TSE (eleitas ou não, qualquer cargo/ano) —
    # cruzamento por nome legal ou nome de urna, mesmo critério usado para os dados
    # biográficos acima; aqui sem filtro de cargo porque o objetivo é justamente ver
    # toda a trajetória eleitoral, não só o mandato atual.
    candidaturas = query(
        "SELECT ANO_ELEICAO AS ano, DS_CARGO AS cargo, SG_UF AS uf, NM_UE AS municipio, "
        "SG_PARTIDO AS partido, DS_SIT_TOT_TURNO AS situacao "
        "FROM stg_tse_candidatos_geral WHERE nome_normalizado = ? OR nome_urna_normalizado = ? "
        "UNION ALL "
        "SELECT ANO_ELEICAO AS ano, DS_CARGO AS cargo, SG_UF AS uf, NM_UE AS municipio, "
        "SG_PARTIDO AS partido, DS_SIT_TOT_TURNO AS situacao "
        "FROM stg_tse_candidatos_municipal_geral WHERE nome_normalizado = ? OR nome_urna_normalizado = ? "
        "ORDER BY ano DESC",
        [nome_normalizado, nome_normalizado, nome_normalizado, nome_normalizado],
    )

    return {
        **pessoa,
        **(bio or {}),
        "sancoesVinculadas": sancoes,
        "contratosVinculados": contratos,
        "votacoesRecentes": votacoes,
        "legislaturasCamara": legislaturas_camara,
        "legislaturasSenado": legislaturas_senado,
        "totalProposicoes": len(proposicoes),
        "proposicoesRecentes": proposicoes[:20],
        "candidaturas": candidaturas,
    }
