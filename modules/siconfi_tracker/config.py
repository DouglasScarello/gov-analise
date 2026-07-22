"""
Configurações centrais do módulo siconfi_tracker.
"""

BASE_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SistemaCamaraAnalise/1.0 (projeto educacional)",
}

REQUEST_TIMEOUT = 30
REQUEST_DELAY = 0.3

# Ano de referência do balanço (DCA - Declaração de Contas Anuais)
ANO_EXERCICIO = 2024

# id_ente: 1 = União; demais = código IBGE de 2 dígitos da UF
ENTES = {
    1: "União",
    11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO",
    21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL",
    28: "SE", 29: "BA",
    31: "MG", 32: "ES", 33: "RJ", 35: "SP",
    41: "PR", 42: "SC", 43: "RS",
    50: "MS", 51: "MT", 52: "GO", 53: "DF",
}
