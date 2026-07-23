"""
Configurações centrais do módulo camara_tracker.

Diferente dos demais dados da Câmara (consultados ao vivo pelo
parlamentar_dashboard), este módulo apenas tira um snapshot do registro
de deputados em exercício, para permitir cruzamento com outras fontes
(Senado, TSE etc.) na camada de ETL.
"""

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SistemaCamaraAnalise/1.0 (projeto educacional)",
}

REQUEST_TIMEOUT = 30

# Legislaturas cobertas na coleta de histórico (51ª = 1999-2003 até a atual).
LEGISLATURAS = list(range(51, 58))
