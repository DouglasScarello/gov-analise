"""
Indicadores agregados: economia (Bacen), socioeconômicos por UF (IBGE) e
finanças públicas (SICONFI).
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..db import paginar, query, query_one

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
    tribunal: Optional[str] = Query(None, description="Sigla do tribunal, ex: STJ, TJSP, TRF1"),
    classe: Optional[str] = Query(None, description="Busca parcial pela classe processual"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    condicoes = []
    params: list = []
    if tribunal:
        condicoes.append("tribunal = ?")
        params.append(tribunal.upper())
    if classe:
        condicoes.append("classeNome ILIKE ?")
        params.append(f"%{classe}%")
    where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    return paginar(
        "*", f"FROM stg_datajud_processos {where}", "ORDER BY dataUltimaAtualizacao DESC", params, limit, offset
    )


@router.get("/judicial/tribunais")
def tribunais_disponiveis():
    return query(
        "SELECT tribunal, COUNT(*) AS total FROM stg_datajud_processos GROUP BY tribunal ORDER BY tribunal"
    )


@router.get("/judicial/processos/{id}")
def detalhe_processo_judicial(id: str):
    processo = query_one("SELECT * FROM stg_datajud_processos WHERE id = ?", [id])
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return processo


@router.get("/legislativo/senado/votacoes")
def votacoes_senado(
    senador: Optional[str] = Query(None, description="Busca parcial pelo nome do senador"),
    uf: Optional[str] = None,
    materiaSigla: Optional[str] = Query(None, description="Ex: PL, PLP, PEC, MSF"),
    resultado: Optional[str] = Query(None, description="Aprovado | Rejeitado | Prejudicado | Empate"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    condicoes = []
    params: list = []

    if senador:
        condicoes.append("s.nome ILIKE ?")
        params.append(f"%{senador}%")
    if uf:
        condicoes.append("s.siglaUf = ?")
        params.append(uf.upper())
    if materiaSigla:
        condicoes.append("v.materiaSigla = ?")
        params.append(materiaSigla.upper())
    if resultado:
        condicoes.append("v.descricaoResultado = ?")
        params.append(resultado)

    where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    from_where = (
        "FROM stg_senado_votacoes v "
        "LEFT JOIN stg_senado_senadores s ON s.id = v.codigoSenador "
        f"{where}"
    )
    select = (
        "v.dataSessao, v.materiaSigla, v.materiaNumero, v.materiaAno, v.materiaEmenta, "
        "v.descricaoVotacao, v.descricaoResultado, v.voto, "
        "s.nome AS senadorNome, s.siglaPartido AS senadorPartido, s.siglaUf AS senadorUf"
    )
    return paginar(select, from_where, "ORDER BY v.dataSessao DESC", params, limit, offset)


@router.get("/legislativo/senado/votacoes/detalhe")
def detalhe_votacao_senado(
    dataSessao: str = Query(..., description="Data da sessão, formato YYYY-MM-DD"),
    materiaSigla: str = Query(...),
    materiaNumero: str = Query(...),
    materiaAno: str = Query(...),
    descricaoVotacao: str = Query(...),
):
    votos = query(
        "SELECT v.voto, s.nome AS senadorNome, s.siglaPartido AS senadorPartido, s.siglaUf AS senadorUf "
        "FROM stg_senado_votacoes v LEFT JOIN stg_senado_senadores s ON s.id = v.codigoSenador "
        "WHERE v.dataSessao = ? AND v.materiaSigla = ? AND v.materiaNumero = ? "
        "AND v.materiaAno = ? AND v.descricaoVotacao = ? "
        "ORDER BY s.nome",
        [dataSessao, materiaSigla, materiaNumero, materiaAno, descricaoVotacao],
    )
    if not votos:
        raise HTTPException(status_code=404, detail="Votação não encontrada")

    materia = query_one(
        "SELECT dataSessao, materiaSigla, materiaNumero, materiaAno, materiaEmenta, "
        "descricaoVotacao, descricaoResultado, votacaoSecreta "
        "FROM stg_senado_votacoes "
        "WHERE dataSessao = ? AND materiaSigla = ? AND materiaNumero = ? "
        "AND materiaAno = ? AND descricaoVotacao = ? LIMIT 1",
        [dataSessao, materiaSigla, materiaNumero, materiaAno, descricaoVotacao],
    )

    contagem: dict[str, int] = {}
    for v in votos:
        contagem[v["voto"]] = contagem.get(v["voto"], 0) + 1

    return {**materia, "votos": votos, "contagemVotos": contagem}


@router.get("/legislativo/senado/processos")
def processos_senado(tramitando: Optional[str] = Query(None, description="Sim | Não"), limit: int = Query(50, le=500)):
    if tramitando:
        return query(
            "SELECT * FROM stg_senado_processos WHERE tramitando = ? ORDER BY dataUltimaAtualizacao DESC LIMIT ?",
            [tramitando, limit],
        )
    return query("SELECT * FROM stg_senado_processos ORDER BY dataUltimaAtualizacao DESC LIMIT ?", [limit])


@router.get("/legislativo/senado/processos/{id}")
def detalhe_processo_senado(id: int):
    processo = query_one("SELECT * FROM stg_senado_processos WHERE id = ?", [id])
    if not processo:
        raise HTTPException(status_code=404, detail="Matéria não encontrada")
    return processo
