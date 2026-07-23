"""
Funções de extração de dados socioeconômicos do IBGE.

Endpoints usados:
- /agregados/{tabela}/periodos/-1/variaveis/{variavel}?localidades=N3[all]
    → última série anual disponível, por Unidade da Federação
- /localidades/estados
    → catálogo de estados (id, sigla, nome, região)
"""

from typing import Optional

import requests

from .config import AGREGADOS_URL, ANOS_HISTORICO, LOCALIDADES_URL, HEADERS, REQUEST_TIMEOUT, TABELAS


def _get_json(url: str) -> Optional[object]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {url}: {e}")
        return None


def _achatar_serie(resposta: list, recurso: str) -> list[dict]:
    """Achata a estrutura aninhada de uma resposta de agregados SIDRA."""
    registros: list[dict] = []
    if not resposta:
        return registros

    for bloco in resposta:
        variavel = bloco.get("variavel")
        unidade = bloco.get("unidade")
        for resultado in bloco.get("resultados", []):
            for serie in resultado.get("series", []):
                localidade = serie.get("localidade", {})
                for periodo, valor in serie.get("serie", {}).items():
                    registros.append({
                        "recurso": recurso,
                        "variavel": variavel,
                        "unidade": unidade,
                        "localidadeId": localidade.get("id"),
                        "localidadeNome": localidade.get("nome"),
                        "periodo": periodo,
                        "valor": valor,
                    })
    return registros


def get_tabela_por_uf(id_tabela: int, id_variavel: int, recurso: str, anos: int = ANOS_HISTORICO) -> list[dict]:
    """Busca os últimos `anos` períodos de uma tabela SIDRA, agregado por UF (N3)."""
    print(f"[ibge_tracker] Buscando {anos} anos de {recurso} (tabela {id_tabela})...")
    url = f"{AGREGADOS_URL}/{id_tabela}/periodos/-{anos}/variaveis/{id_variavel}?localidades=N3[all]"
    dados = _get_json(url)
    registros = _achatar_serie(dados, recurso)
    print(f"[ibge_tracker] {recurso}: {len(registros)} registros")
    return registros


def get_todas_tabelas() -> list[dict]:
    """Coleta todas as tabelas configuradas em TABELAS e retorna uma lista plana."""
    todos: list[dict] = []
    for id_tabela, id_variavel, recurso in TABELAS:
        todos.extend(get_tabela_por_uf(id_tabela, id_variavel, recurso))
    return todos


def get_estados() -> list[dict]:
    """Retorna o catálogo de estados (id, sigla, nome, região)."""
    print("[ibge_tracker] Buscando catálogo de estados...")
    dados = _get_json(f"{LOCALIDADES_URL}/estados")
    if not isinstance(dados, list):
        print("[ibge_tracker] Catálogo de estados indisponível no momento.")
        return []
    print(f"[ibge_tracker] {len(dados)} estados encontrados.")
    return dados
