"""
Configurações centrais do módulo datajud_tracker.

A chave de API (DATAJUD_API_KEY) é lida do .env na raiz do projeto —
não deve ser commitada (ver .env.example).
"""

import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api-publica.datajud.cnj.jus.br"

DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY", "")

HEADERS = {
    "Authorization": f"APIKey {DATAJUD_API_KEY}",
    "Content-Type": "application/json",
}

REQUEST_TIMEOUT = 60
REQUEST_DELAY = 0.3

# DataJud cobre ~90 tribunais (STJ, TST, TREs, TRTs, TRFs, TJs estaduais...).
# Cada um tem milhões de processos, com histórico de movimentações pesado.
# Por isso o v1 coleta apenas uma amostra recente de um conjunto representativo
# de tribunais, ordenada pela última atualização — não a base completa.
TRIBUNAIS = {
    "stj": "Superior Tribunal de Justiça",
    "tst": "Tribunal Superior do Trabalho",
    "trf1": "Tribunal Regional Federal da 1ª Região",
    "tjsp": "Tribunal de Justiça de São Paulo",
    "tjrj": "Tribunal de Justiça do Rio de Janeiro",
    "tjmg": "Tribunal de Justiça de Minas Gerais",
}

# Quantos processos recentes buscar por tribunal
TAMANHO_AMOSTRA = 200
