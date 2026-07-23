"""
Funções de extração dos dados abertos do Senado Federal.

Endpoints usados:
- /senador/lista/atual.json      → senadores em exercício
- /senador/{codigo}/votacoes.json → votações nominais de um senador
- /processo?ano=&limite=          → matérias/processos legislativos em tramitação
                                     (substitui o antigo /materia/tramitando.json)
"""

import time
from typing import Optional

import requests

from .config import (
    BASE_URL,
    LEGISLATURA_FIM,
    LEGISLATURA_INICIO,
    PROCESSO_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    REQUEST_DELAY,
)


def _get_json(url: str, params: Optional[dict] = None) -> Optional[dict]:
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {url}: {e}")
        return None


def _flatten_senador(parlamentar: dict) -> dict:
    """Achata a estrutura aninhada de um senador para um dict simples e plano."""
    ident = parlamentar.get("IdentificacaoParlamentar", {})
    mandato = parlamentar.get("Mandato", {})
    bloco = ident.get("Bloco") or {}

    return {
        "id": ident.get("CodigoParlamentar"),
        "nome": ident.get("NomeParlamentar"),
        "nomeCompleto": ident.get("NomeCompletoParlamentar"),
        "sexo": ident.get("SexoParlamentar"),
        "siglaPartido": ident.get("SiglaPartidoParlamentar"),
        "siglaUf": ident.get("UfParlamentar"),
        "email": ident.get("EmailParlamentar"),
        "urlFoto": ident.get("UrlFotoParlamentar"),
        "urlPagina": ident.get("UrlPaginaParlamentar"),
        "bloco": bloco.get("NomeBloco"),
        "membroMesa": ident.get("MembroMesa") == "Sim",
        "membroLideranca": ident.get("MembroLideranca") == "Sim",
        "codigoMandato": mandato.get("CodigoMandato"),
        "descricaoParticipacao": mandato.get("DescricaoParticipacao"),
    }


def get_senadores_atuais() -> list[dict]:
    """Retorna a lista de senadores atualmente em exercício, já achatada."""
    print("[senado_tracker] Buscando senadores em exercício...")
    data = _get_json(f"{BASE_URL}/senador/lista/atual.json")
    if not data:
        return []

    parlamentares = (
        data.get("ListaParlamentarEmExercicio", {})
        .get("Parlamentares", {})
        .get("Parlamentar", [])
    )
    if isinstance(parlamentares, dict):  # API retorna dict único se só houver 1 resultado
        parlamentares = [parlamentares]

    senadores = [_flatten_senador(p) for p in parlamentares]
    print(f"[senado_tracker] {len(senadores)} senadores encontrados.")
    return senadores


def get_votacoes_senador(codigo: str) -> list[dict]:
    """Retorna as votações nominais de um senador específico."""
    data = _get_json(f"{BASE_URL}/senador/{codigo}/votacoes.json")
    if not data:
        return []

    parlamentar = data.get("VotacaoParlamentar", {}).get("Parlamentar", {})
    votacoes = (parlamentar.get("Votacoes") or {}).get("Votacao", [])
    if isinstance(votacoes, dict):
        votacoes = [votacoes]

    for v in votacoes:
        v["_codigoSenador"] = codigo
    return votacoes


def get_votacoes_todos_senadores(codigos: list[str]) -> list[dict]:
    """
    Coleta votações de uma lista de senadores, com pausa entre requisições.
    Pode levar alguns minutos para os ~81 senadores atuais.
    """
    todas_votacoes: list[dict] = []
    total = len(codigos)

    for i, codigo in enumerate(codigos, start=1):
        print(f"[senado_tracker] Votações {i}/{total} (senador {codigo})...")
        votacoes = get_votacoes_senador(codigo)
        todas_votacoes.extend(votacoes)
        time.sleep(REQUEST_DELAY)

    print(f"[senado_tracker] Total de votações coletadas: {len(todas_votacoes)}")
    return todas_votacoes


def get_processos(ano: Optional[int] = None, limite: int = 1000) -> list[dict]:
    """
    Retorna processos/matérias legislativas (tramitando ou não) via API nova.
    ano: filtra pelo ano de apresentação (opcional).
    """
    print(f"[senado_tracker] Buscando processos legislativos (ano={ano or 'todos'})...")
    params: dict = {"limite": limite}
    if ano:
        params["ano"] = ano

    data = _get_json(PROCESSO_URL, params=params)
    if not data:
        return []

    processos = data if isinstance(data, list) else data.get("dados", [])
    print(f"[senado_tracker] {len(processos)} processos encontrados.")
    return processos


def _extrair_legislaturas_do_mandato(mandato: dict) -> list[dict]:
    """Um mandato de senador dura 2 legislaturas (8 anos) — extrai cada uma."""
    legislaturas = []
    for chave in ("PrimeiraLegislaturaDoMandato", "SegundaLegislaturaDoMandato"):
        leg = mandato.get(chave)
        if leg:
            legislaturas.append(leg)
    return legislaturas


def get_senadores_legislaturas(
    inicio: int = LEGISLATURA_INICIO, fim: int = LEGISLATURA_FIM
) -> list[dict]:
    """Retorna um registro por (senador, legislatura, mandato) no intervalo
    informado — permite montar o histórico de mandatos por pessoa."""
    print(f"[senado_tracker] Buscando senadores das legislaturas {inicio} a {fim}...")
    data = _get_json(f"{BASE_URL}/senador/lista/legislatura/{inicio}/{fim}")
    if not data:
        return []

    parlamentares = (
        data.get("ListaParlamentarLegislatura", {})
        .get("Parlamentares", {})
        .get("Parlamentar", [])
    )
    if isinstance(parlamentares, dict):
        parlamentares = [parlamentares]

    registros: list[dict] = []
    for p in parlamentares:
        ident = p.get("IdentificacaoParlamentar", {})
        mandatos = p.get("Mandatos", {}).get("Mandato", [])
        if isinstance(mandatos, dict):
            mandatos = [mandatos]

        for mandato in mandatos:
            for leg in _extrair_legislaturas_do_mandato(mandato):
                registros.append({
                    "id": ident.get("CodigoParlamentar"),
                    "nome": ident.get("NomeParlamentar"),
                    "nomeCompleto": ident.get("NomeCompletoParlamentar"),
                    "siglaUf": mandato.get("UfParlamentar"),
                    "numeroLegislatura": leg.get("NumeroLegislatura"),
                    "dataInicio": leg.get("DataInicio"),
                    "dataFim": leg.get("DataFim"),
                    "participacao": mandato.get("DescricaoParticipacao"),
                })

    print(f"[senado_tracker] {len(registros)} registros de mandatos por legislatura encontrados.")
    return registros
