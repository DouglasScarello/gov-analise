"""
Configurações centrais do módulo senado_tracker.
"""

# API legada (XML/JSON) — usada para senadores e votações
BASE_URL = "https://legis.senado.leg.br/dadosabertos"

# API nova (JSON puro) — usada para processos/matérias legislativas
# Substitui o antigo endpoint /materia/tramitando.json (descontinuado)
PROCESSO_URL = "https://legis.senado.leg.br/dadosabertos/processo"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SistemaCamaraAnalise/1.0 (projeto educacional)",
}

REQUEST_TIMEOUT = 30

# Pausa entre requisições em loop (ex: votações por senador) para não sobrecarregar a API
REQUEST_DELAY = 0.25

# Intervalo de legislaturas cobertas na coleta de histórico (mesmo período do camara_tracker).
LEGISLATURA_INICIO = 51
LEGISLATURA_FIM = 57
