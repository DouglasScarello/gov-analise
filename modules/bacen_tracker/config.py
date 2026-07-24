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
    11: "ipca_acumulado_12_meses",  # inflação acumulada no ano
    1: "dolar_ptax_venda",
    3698: "dolar_ptax_compra",
    189: "igpm_variacao_mensal",
    24369: "divida_liquida_setor_publico_pct_pib",
    4447: "taxa_desocupacao_pnad",
    21862: "ibc_br",  # Atividade econômica / proxy de PIB mensal
    12991: "balanca_comercial_saldo",  # Saldo da balança comercial
    3437: "reservas_internacionais",
    20783: "spread_bancario",  # Spread médio das operações de crédito com recursos livres
    11752: "taxa_cambio_real_efetiva",  # Taxa de câmbio real efetiva (IPCA)
    5793: "resultado_primario_governo",  # NFSP sem desvalorização cambial / PIB - resultado primário
}

# Quantos últimos valores buscar por série via /ultimos/N (a API do SGS limita
# esse endpoint a no máximo 20 valores por requisição) — usado só como fallback.
ULTIMOS_N = 20

# Quantos anos de histórico buscar via o endpoint de intervalo de datas
# (/dados?dataInicial=...&dataFinal=...), que não tem o limite de 20 pontos.
ANOS_HISTORICO = 10
