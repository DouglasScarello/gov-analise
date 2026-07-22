# CLAUDE.md

## Stack
- Python 3.12+, gerenciado via Poetry (não usar pip diretamente)
- Dashboard: Streamlit + Plotly
- Dados: pandas, pyarrow (parquet), networkx (grafos)
- Fonte de dados: API pública `dadosabertos.camara.leg.br`

## Estrutura
Módulos independentes em `modules/` (não compartilham estado entre si):
- `parlamentar_dashboard` — app Streamlit principal
- `tracker_gastos` — download/análise de despesas CEAP
- `network_analyst` — grafos de frentes parlamentares
- `legis_notifier` — bot Telegram de proposições
- `tema_miner` — mineração de temas via NLP
- `municipal_tracker` — dados municipais
`civic_framework/` contém código compartilhado (collector, database, adapters).

## Convenções
- Formatação: black + isort + ruff (sem config custom além do padrão)
- Rodar app: `poetry run streamlit run modules/parlamentar_dashboard/app.py`

## Regras
- Não commitar `.env` (usar `.env.example` como referência)
- Não adicionar dependências fora do `pyproject.toml`/poetry
