"""
Configurações centrais do módulo compras_tracker.
"""

from datetime import datetime, timedelta, timezone

BASE_URL = "https://dadosabertos.compras.gov.br/modulo-contratacoes/1_consultarContratacoes_PNCP_14133"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SistemaCamaraAnalise/1.0 (projeto educacional)",
}

REQUEST_TIMEOUT = 30
REQUEST_DELAY = 0.2
TAMANHO_PAGINA = 500

# Janela de datas coletada (a API exige um intervalo de publicação)
DIAS_JANELA = 21
DATA_FINAL = datetime.now(tz=timezone.utc).date()
DATA_INICIAL = DATA_FINAL - timedelta(days=DIAS_JANELA)

# Modalidades de contratação (tabela de domínio do PNCP) coletadas
MODALIDADES = {
    4: "Concorrência",
    5: "Pregão",
    6: "Dispensa",
    7: "Inexigibilidade",
}

# Limite de páginas por modalidade, para não estourar o tempo de coleta
MAX_PAGINAS_POR_MODALIDADE = 20
