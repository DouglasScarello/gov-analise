"""
Configurações centrais do módulo tse_tracker.

Diferente das demais fontes (Câmara, Senado, Bacen, SICONFI, IBGE), o TSE não
expõe uma API REST paginada: os dados são publicados como pacotes CKAN cujos
recursos são arquivos ZIP/CSV nacionais consolidados por ano de eleição.
"""

CKAN_BASE_URL = "https://dadosabertos.tse.jus.br/api/3/action"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SistemaCamaraAnalise/1.0 (projeto educacional)",
}

REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 180

# Ano de eleição a coletar
ANO_ELEICAO = 2024

# Nome do pacote CKAN de candidatos para o ano configurado
PACOTE_CANDIDATOS = f"candidatos-{ANO_ELEICAO}"

# Nome do recurso CSV consolidado (todo o Brasil) dentro do ZIP de candidatos
NOME_ARQUIVO_BRASIL = f"consulta_cand_{ANO_ELEICAO}_BRASIL.csv"

CSV_ENCODING = "latin-1"
CSV_SEP = ";"
