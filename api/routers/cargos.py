"""
Endpoint unificado de cargos políticos do Brasil, cobrindo os quatro níveis
para os quais há dado coletado:

- nacional  → presidente / vice-presidente (TSE, eleições 1994-2022)
- federal   → deputado federal / senador (Câmara e Senado, mandato atual)
- estadual  → governador / vice-governador / deputado estadual / deputado
              distrital (TSE, eleições 1994-2022)
- municipal → prefeito / vice-prefeito / vereador (TSE, eleições 1996-2024)

Nacional, estadual e municipal vêm do registro de candidatura do TSE, por
isso são filtrados por DS_SIT_TOT_TURNO = 'ELEITO' (não interessa quem
concorreu e perdeu). Federal vem das APIs de Câmara/Senado, que já refletem
o mandato em exercício, então não tem conceito de "ano" — é sempre o atual.

SQ_CANDIDATO não é único entre anos diferentes (o TSE reaproveita a
sequência a cada eleição), então nacional/estadual/municipal usam um id
composto "<ano>-<sq_candidato>" para não colidir.

Observação: o arquivo de candidatos de 2006 do TSE não preenche
DS_SIT_TOT_TURNO (vem todo "#NULO#"), então esse ano fica ausente dos
resultados de "eleitos" — é uma lacuna na fonte, não um bug daqui.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..db import query, query_one

router = APIRouter(prefix="/cargos", tags=["cargos"])

ELEITO = "DS_SIT_TOT_TURNO ILIKE 'ELEITO%'"

CARGOS_NACIONAL = ["PRESIDENTE", "VICE-PRESIDENTE"]
CARGOS_ESTADUAL = ["GOVERNADOR", "VICE-GOVERNADOR", "DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL"]
CARGOS_MUNICIPAL = ["PREFEITO", "VICE-PREFEITO", "VEREADOR"]

ANOS_ELEICAO_GERAL = [1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]
ANOS_ELEICAO_MUNICIPAL = [1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]

NIVEIS = {
    "nacional": {"tabela": "stg_tse_candidatos_geral", "cargos": CARGOS_NACIONAL, "tem_uf": False, "tem_municipio": False, "tem_ano": True},
    "estadual": {"tabela": "stg_tse_candidatos_geral", "cargos": CARGOS_ESTADUAL, "tem_uf": True, "tem_municipio": False, "tem_ano": True},
    "municipal": {"tabela": "stg_tse_candidatos_municipal_geral", "cargos": CARGOS_MUNICIPAL, "tem_uf": True, "tem_municipio": True, "tem_ano": True},
}

ANOS_POR_NIVEL = {
    "nacional": ANOS_ELEICAO_GERAL,
    "estadual": ANOS_ELEICAO_GERAL,
    "municipal": ANOS_ELEICAO_MUNICIPAL,
}

CARGO_LABEL = {
    "PRESIDENTE": "Presidente",
    "VICE-PRESIDENTE": "Vice-presidente",
    "GOVERNADOR": "Governador(a)",
    "VICE-GOVERNADOR": "Vice-governador(a)",
    "DEPUTADO ESTADUAL": "Deputado(a) Estadual",
    "DEPUTADO DISTRITAL": "Deputado(a) Distrital",
    "PREFEITO": "Prefeito(a)",
    "VICE-PREFEITO": "Vice-prefeito(a)",
    "VEREADOR": "Vereador(a)",
    "DEPUTADO FEDERAL": "Deputado(a) Federal",
    "SENADOR": "Senador(a)",
}


@router.get("/tipos")
def listar_tipos_de_cargo():
    """Catálogo de nível + cargo disponíveis, para montar um filtro no frontend."""
    tipos = [
        {"nivel": "federal", "cargo": "DEPUTADO FEDERAL", "label": CARGO_LABEL["DEPUTADO FEDERAL"]},
        {"nivel": "federal", "cargo": "SENADOR", "label": CARGO_LABEL["SENADOR"]},
    ]
    for nivel in ("nacional", "estadual", "municipal"):
        for cargo in NIVEIS[nivel]["cargos"]:
            tipos.append({"nivel": nivel, "cargo": cargo, "label": CARGO_LABEL.get(cargo, cargo.title())})
    return tipos


@router.get("/anos")
def listar_anos_disponiveis(nivel: str = Query("nacional", description="nacional | estadual | municipal")):
    """Anos de eleição com dado coletado para o nível informado."""
    anos = ANOS_POR_NIVEL.get(nivel.lower())
    if anos is None:
        raise HTTPException(status_code=400, detail="nivel deve ser: nacional, estadual ou municipal")
    return {"anos": anos}


def _listar_federal(cargo: Optional[str], uf: Optional[str], nome: Optional[str], limit: int, offset: int):
    condicoes = []
    params: list = []

    if cargo == "DEPUTADO FEDERAL":
        condicoes.append("casa ILIKE '%Câmara%'")
    elif cargo == "SENADOR":
        condicoes.append("casa ILIKE '%Senado%'")

    if uf:
        condicoes.append("(camaraUf = ? OR senadoUf = ?)")
        params.extend([uf.upper(), uf.upper()])
    if nome:
        condicoes.append("nome_normalizado ILIKE ?")
        params.append(f"%{nome.upper()}%")

    where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    sql = f"""
        SELECT slug AS id, nome, casa,
               COALESCE(camaraPartido, senadoPartido) AS partido,
               COALESCE(camaraUf, senadoUf) AS uf,
               COALESCE(camaraFoto, senadoFoto) AS foto
        FROM pessoas_politicas
        {where}
        ORDER BY nome
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    linhas = query(sql, params)
    for l in linhas:
        l["nivel"] = "federal"
        l["cargo"] = cargo or l.pop("casa", None)
    return linhas


def _listar_tse(nivel: str, cargo: Optional[str], uf: Optional[str], municipio: Optional[str], nome: Optional[str], ano: Optional[int], limit: int, offset: int):
    cfg = NIVEIS[nivel]
    condicoes = [ELEITO]
    params: list = []

    if cargo:
        condicoes.append("DS_CARGO = ?")
        params.append(cargo.upper())
    else:
        placeholders = ", ".join(["?"] * len(cfg["cargos"]))
        condicoes.append(f"DS_CARGO IN ({placeholders})")
        params.extend(cfg["cargos"])

    if cfg["tem_uf"] and uf:
        condicoes.append("SG_UF = ?")
        params.append(uf.upper())
    if cfg["tem_municipio"] and municipio:
        condicoes.append("NM_UE ILIKE ?")
        params.append(f"%{municipio}%")
    if cfg["tem_ano"] and ano:
        condicoes.append("ANO_ELEICAO = ?")
        params.append(str(ano))
    if nome:
        condicoes.append("nome_normalizado ILIKE ?")
        params.append(f"%{nome.upper()}%")

    # id composto (ano-sq) para nacional/estadual, já que SQ_CANDIDATO se repete
    # entre eleições diferentes; municipal (um ano só) usa o SQ_CANDIDATO puro.
    id_expr = "ANO_ELEICAO || '-' || SQ_CANDIDATO" if cfg["tem_ano"] else "SQ_CANDIDATO"

    where = f"WHERE {' AND '.join(condicoes)}"
    sql = f"""
        SELECT {id_expr} AS id, NM_CANDIDATO AS nome, NM_URNA_CANDIDATO AS nome_urna,
               SG_PARTIDO AS partido, SG_UF AS uf, NM_UE AS municipio, DS_CARGO AS cargo,
               ANO_ELEICAO AS ano
        FROM {cfg["tabela"]}
        {where}
        ORDER BY ANO_ELEICAO DESC, SG_UF, DS_CARGO, NM_CANDIDATO
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    linhas = query(sql, params)
    for l in linhas:
        l["nivel"] = nivel
    return linhas


@router.get("/politicos")
def listar_politicos(
    nivel: str = Query(..., description="federal | estadual | nacional | municipal"),
    cargo: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
    municipio: Optional[str] = Query(None),
    nome: Optional[str] = Query(None),
    ano: Optional[int] = Query(None, description="Ano da eleição (nacional/estadual, 1994-2022)"),
    limit: int = Query(24, le=100),
    offset: int = Query(0, ge=0),
):
    nivel = nivel.lower()
    if nivel == "federal":
        return _listar_federal(cargo, uf, nome, limit, offset)
    if nivel in NIVEIS:
        return _listar_tse(nivel, cargo, uf, municipio, nome, ano, limit, offset)
    raise HTTPException(status_code=400, detail="nivel deve ser: federal, estadual, nacional ou municipal")


@router.get("/politicos/{nivel}/{id}")
def detalhe_politico(nivel: str, id: str):
    nivel = nivel.lower()

    if nivel == "federal":
        pessoa = query_one("SELECT * FROM pessoas_politicas WHERE slug = ?", [id])
        if not pessoa:
            raise HTTPException(status_code=404, detail="Político não encontrado")
        sancoes = query(
            "SELECT * FROM entidades_sancionadas WHERE sancionadoNome ILIKE ? LIMIT 20",
            [f"%{pessoa['nome']}%"],
        )
        return {**pessoa, "nivel": "federal", "sancoesVinculadas": sancoes}

    if nivel in NIVEIS:
        cfg = NIVEIS[nivel]
        tabela = cfg["tabela"]

        if cfg["tem_ano"]:
            # id vem como "<ano>-<sq_candidato>" (ver _listar_tse)
            ano, _, sq = id.partition("-")
            if not sq:
                raise HTTPException(status_code=400, detail="id inválido, esperado <ano>-<sq_candidato>")
            condicao, valores = "ANO_ELEICAO = ? AND SQ_CANDIDATO = ?", [ano, sq]
        else:
            condicao, valores = "SQ_CANDIDATO = ?", [id]

        # Candidatos que foram a 2º turno têm mais de uma linha com o mesmo
        # SQ_CANDIDATO (uma por turno) — prioriza a que registra o resultado final.
        pessoa = query_one(
            f"""
            SELECT * FROM {tabela}
            WHERE {condicao}
            ORDER BY CASE WHEN DS_SIT_TOT_TURNO ILIKE 'ELEITO%' THEN 0 ELSE 1 END
            LIMIT 1
            """,
            valores,
        )
        if not pessoa:
            raise HTTPException(status_code=404, detail="Político não encontrado")
        sancoes = query(
            "SELECT * FROM entidades_sancionadas WHERE sancionadoNome ILIKE ? LIMIT 20",
            [f"%{pessoa['NM_CANDIDATO']}%"],
        )
        return {**pessoa, "nivel": nivel, "sancoesVinculadas": sancoes}

    raise HTTPException(status_code=400, detail="nivel deve ser: federal, estadual, nacional ou municipal")
