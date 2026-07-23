"""
Configurações centrais do módulo bacen_tracker.
"""

BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SistemaCamaraAnalise/1.0 (projeto educacional)",
}

REQUEST_TIMEOUT = 30

# Séries do SGS a coletar: código -> nome legível
SERIES = {
    432: "selic_meta",
    433: "ipca_variacao_mensal",
    1: "dolar_ptax_venda",
    189: "igpm_variacao_mensal",
    24369: "divida_liquida_setor_publico_pct_pib",
    4447: "taxa_desocupacao_pnad",
}

# Quantos últimos valores buscar por série via /ultimos/N (a API do SGS limita
# esse endpoint a no máximo 20 valores por requisição) — usado só como fallback.
ULTIMOS_N = 20

# Quantos anos de histórico buscar via o endpoint de intervalo de datas
# (/dados?dataInicial=...&dataFinal=...), que não tem o limite de 20 pontos.
ANOS_HISTORICO = 10
