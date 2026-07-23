"""
Configurações centrais do módulo transparencia_tracker.

A chave de API (PORTAL_TRANSPARENCIA_API_KEY) é lida do .env na raiz do
projeto — não deve ser commitada (ver .env.example).
"""

import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

PORTAL_TRANSPARENCIA_API_KEY = os.getenv("PORTAL_TRANSPARENCIA_API_KEY", "")

HEADERS = {
    "chave-api-dados": PORTAL_TRANSPARENCIA_API_KEY,
    "Accept": "application/json",
}

REQUEST_TIMEOUT = 30
# A API impõe limite de requisições por minuto — pausa conservadora entre chamadas
REQUEST_DELAY = 0.7

# Sanções (CEIS/CNEP): quantas páginas buscar (15 registros por página).
# A paginação já para sozinha quando uma página vem com menos de 15 itens
# (fim da base) — este número é só um teto de segurança, bem acima do
# tamanho real das bases (CEIS ~1.550 páginas, CNEP ~115, em 2026-07).
MAX_PAGINAS_SANCOES = 2000

# Contratos: órgãos superiores (código SIAFI) amostrados e páginas por órgão
ORGAOS_CONTRATOS = {
    "20000": "Presidência da República",
    "25000": "Ministério da Fazenda",
    "26000": "Ministério da Educação",
    "30000": "Ministério da Justiça e Segurança Pública",
    "36000": "Ministério da Saúde",
    "52000": "Ministério da Defesa",
}
MAX_PAGINAS_CONTRATOS_POR_ORGAO = 3

# Catálogo de órgãos SIAFI: quantas páginas buscar
MAX_PAGINAS_ORGAOS = 60
