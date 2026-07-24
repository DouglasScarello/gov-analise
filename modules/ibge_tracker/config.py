"""
Configurações centrais do módulo ibge_tracker.
"""

AGREGADOS_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"
LOCALIDADES_URL = "https://servicodados.ibge.gov.br/api/v3/localidades"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "SistemaCamaraAnalise/1.0 (projeto educacional)",
}

REQUEST_TIMEOUT = 30

# Tabelas SIDRA coletadas, por estado (N3): (id_tabela, id_variavel, nome_recurso)
TABELAS = [
    (6579, 9324, "populacao_estimada_uf"),
    (5938, 37, "pib_uf"),
    # Nota: taxa_desocupacao_uf e rendimento_medio_uf requerem códigos SIDRA válidos — validar em https://sidra.ibge.gov.br antes de usar
]

# Quantos períodos (anos) buscar de cada tabela, para permitir gráfico de
# evolução por UF em vez de só o valor mais recente.
ANOS_HISTORICO = 10

# Tabela nacional (N1) do PIB — taxa de variação trimestral (Contas Nacionais)
# (id_tabela, id_variavel, classificacao, nome_recurso)
PIB_NACIONAL = (5932, 6562, "11255[90707]", "pib_taxa_crescimento")

# Quantos trimestres de histórico buscar para o PIB nacional (trimestral)
TRIMESTRES_HISTORICO = 40  # ~10 anos
