"""
Funções de extração de contratações públicas federais via Compras.gov.br.

Endpoint: /modulo-contratacoes/1_consultarContratacoes_PNCP_14133
Cobre contratações sob a Lei 14.133/2021 (concorrência, pregão, dispensa,
inexigibilidade etc.), publicadas no PNCP - Portal Nacional de Contratações Públicas.
"""

import time
from typing import Optional

import requests

from .config import (
    BASE_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    REQUEST_DELAY,
    TAMANHO_PAGINA,
    DATA_INICIAL,
    DATA_FINAL,
    MODALIDADES,
    MAX_PAGINAS_POR_MODALIDADE,
)


def _get_json(params: dict) -> Optional[dict]:
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha na requisição a {BASE_URL}: {e}")
        return None


def get_contratacoes_modalidade(codigo_modalidade: int, nome_modalidade: str) -> list[dict]:
    """Pagina todas as contratações de uma modalidade na janela de datas configurada."""
    registros: list[dict] = []
    pagina = 1

    while pagina <= MAX_PAGINAS_POR_MODALIDADE:
        params = {
            "pagina": pagina,
            "tamanhoPagina": TAMANHO_PAGINA,
            "dataPublicacaoPncpInicial": DATA_INICIAL.isoformat(),
            "dataPublicacaoPncpFinal": DATA_FINAL.isoformat(),
            "codigoModalidade": codigo_modalidade,
        }
        data = _get_json(params)
        if not data:
            break

        itens = data.get("resultado", [])
        registros.extend(itens)

        total_paginas = data.get("totalPaginas", 1)
        print(f"[compras_tracker] {nome_modalidade}: página {pagina}/{min(total_paginas, MAX_PAGINAS_POR_MODALIDADE)} ({len(itens)} itens)")

        if pagina >= total_paginas or not itens:
            break

        pagina += 1
        time.sleep(REQUEST_DELAY)

    return registros


def get_todas_contratacoes() -> list[dict]:
    """Coleta contratações de todas as modalidades configuradas em MODALIDADES."""
    todas: list[dict] = []
    for codigo, nome in MODALIDADES.items():
        print(f"[compras_tracker] Buscando modalidade '{nome}' (código {codigo})...")
        registros = get_contratacoes_modalidade(codigo, nome)
        print(f"[compras_tracker] {nome}: {len(registros)} contratações coletadas")
        todas.extend(registros)
    return todas
