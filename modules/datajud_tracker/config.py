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
# Cada um tem dezenas de milhões de processos, com histórico de movimentações
# pesado. Por isso a coleta é uma amostra recente (ordenada por última
# atualização) de um conjunto representativo de tribunais — não a base
# completa. O conjunto abaixo cobre as cinco regiões federais, a justiça do
# trabalho e os tribunais estaduais de maior volume, para dar diversidade
# geográfica e por ramo de justiça sem tentar replicar o acervo inteiro.
TRIBUNAIS = {
    "stj": "Superior Tribunal de Justiça",
    "tst": "Tribunal Superior do Trabalho",
    "tse": "Tribunal Superior Eleitoral",
    "trf1": "Tribunal Regional Federal da 1ª Região",
    "trf2": "Tribunal Regional Federal da 2ª Região",
    "trf3": "Tribunal Regional Federal da 3ª Região",
    "trf4": "Tribunal Regional Federal da 4ª Região",
    "trf5": "Tribunal Regional Federal da 5ª Região",
    "trt2": "Tribunal Regional do Trabalho da 2ª Região (SP)",
    "trt15": "Tribunal Regional do Trabalho da 15ª Região (Campinas)",
    "tjsp": "Tribunal de Justiça de São Paulo",
    "tjrj": "Tribunal de Justiça do Rio de Janeiro",
    "tjmg": "Tribunal de Justiça de Minas Gerais",
    "tjrs": "Tribunal de Justiça do Rio Grande do Sul",
    "tjpr": "Tribunal de Justiça do Paraná",
    "tjba": "Tribunal de Justiça da Bahia",
    "tjpe": "Tribunal de Justiça de Pernambuco",
    "tjce": "Tribunal de Justiça do Ceará",
    "tjdft": "Tribunal de Justiça do Distrito Federal e Territórios",
}

# Quantos processos recentes buscar por tribunal
TAMANHO_AMOSTRA = 300
