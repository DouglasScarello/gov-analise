# 🏛️ Câmara Analytics

<div align="center">

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Poetry](https://img.shields.io/badge/package%20manager-poetry-blueviolet.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/frontend-streamlit-ff4b4b.svg)

**Sistema Modular de Análise de Dados da Câmara dos Deputados do Brasil**

Dashboard interativo e conjunto de ferramentas para analisar dados públicos da Câmara dos Deputados, consumindo a [API de Dados Abertos](https://dadosabertos.camara.leg.br) em tempo real.

</div>

---

## 📸 Visão Geral

O projeto é composto por **5 módulos independentes**, cada um com uma responsabilidade específica:

| Módulo | Tipo | Descrição |
|--------|------|-----------|
| `parlamentar_dashboard` | 🌐 Web App | Dashboard Streamlit com análise individual de deputados |
| `tracker_gastos` | 🐍 Script | Download e análise local das despesas CEAP em CSV/Parquet |
| `network_analyst` | 🐍 Script | Geração de grafos de redes políticas via frentes parlamentares |
| `legis_notifier` | 🤖 Bot | Monitoramento de proposições legislativas com alertas via Telegram |
| `tema_miner` | 🐍 Script | Mineração de temas em ementas legislativas com NLP |

---

## 🚀 Início Rápido

### Pré-requisitos

- Python **3.12+**
- [Poetry](https://python-poetry.org/docs/#installation) (gerenciador de dependências)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/FuriaLLMs/camara-analytics.git
cd camara-analytics

# 2. Instale as dependências
poetry install

# 3. Ative o ambiente virtual
poetry shell
```

### Rodando o Dashboard

```bash
poetry run streamlit run modules/parlamentar_dashboard/app.py
```

Acesse em: **http://localhost:8501**

---

## 🌐 Dashboard Parlamentar (`parlamentar_dashboard`)

O módulo principal — uma aplicação web completa para analisar o perfil e a atuação de qualquer um dos **513 deputados federais**.

### Funcionalidades

#### Aba 👥 Deputados
- Lista completa dos 513 deputados com paginação automática
- Filtros por **Estado (UF)** e **Partido**
- Métricas: total de deputados, número de partidos, estados representados
- **Tabela interativa** com nome, partido, UF e e-mail
- **Gráfico donut** com distribuição de deputados por partido

#### Aba 🔍 Análise Individual
Selecione qualquer deputado e visualize:

| Sub-aba | O que mostra |
|---------|--------------|
| 💰 Despesas CEAP | Treemap colorido por categoria de gasto + tabela detalhada |
| 🎙️ Discursos | Histórico mensal de discursos em plenário |
| 📅 Eventos | Distribuição de participações por tipo de sessão |
| 🏛️ Órgãos | Comissões e órgãos dos quais o deputado é membro |
| 🏳️ Frentes | Frentes parlamentares das quais participa |

**6 métricas de atividade:** Gasto CEAP total · Notas fiscais · Discursos · Eventos · Comissões · Frentes

---

## 💰 Tracker de Gastos (`tracker_gastos`)

Script para download batch das despesas CEAP de todos os deputados.

```bash
poetry run python -m modules.tracker_gastos.main
```

- Exporta dados em `.csv` e `.parquet`
- Calcula totais por deputado, partido e tipo de despesa
- Gera relatório resumido em texto

**Saída:** `outputs/despesas_YYYY.csv`

---

## 🕸️ Network Analyst (`network_analyst`)

Analisa redes de influência política a partir de frentes parlamentares compartilhadas.

```bash
poetry run python -m modules.network_analyst.main
```

- Cria grafo de co-participação em frentes parlamentares
- Detecta comunidades políticas automaticamente
- Exporta visualização interativa em HTML

**Saída:** `outputs/rede_politica.html`

---

## 🤖 Legis Notifier (`legis_notifier`)

Bot que monitora novas proposições legislativas e envia alertas via **Telegram**.

### Configuração

O bot utiliza variáveis de ambiente geridas pelo `python-dotenv`.

1. Obtenha um token com o [@BotFather](https://t.me/botfather).
2. Obtenha seu Chat ID (pode usar o [@userinfobot](https://t.me/userinfobot)).

```bash
# Copie o arquivo de configuração
cp modules/legis_notifier/.env.example modules/legis_notifier/.env

# Edite o arquivo .env com suas credenciais:
TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

```bash
# Execute o monitor
poetry run python -m modules.legis_notifier.main
```

---

## 🔍 Tema Miner (`tema_miner`)

Classifica automaticamente o tema de proposições legislativas usando NLP.

```bash
poetry run python -m modules.tema_miner.main
```

- Busca proposições recentes na API
- Limpa e normaliza o texto das ementas
- Classifica por área temática (saúde, educação, economia, etc.)
- Gera gráficos de distribuição de temas

**Saída:** `outputs/temas_YYYY-MM-DD.csv`

---

## 📁 Estrutura do Projeto

```
camara-analytics/
│
├── modules/
│   ├── parlamentar_dashboard/   # Dashboard Streamlit
│   ├── tracker_gastos/          # Extração de despesas CEAP
│   ├── network_analyst/         # Análise de grafos/redes
│   ├── legis_notifier/          # Monitoramento e bot Telegram
│   └── tema_miner/              # Classificação NLP de temas
│
├── outputs/                     # Arquivos gerados (gitignored)
├── pyproject.toml               # Configuração Poetry
└── README.md
```

---

## 🛠️ Tecnologias

- **Interface:** [Streamlit](https://streamlit.io/)
- **Visualização:** [Plotly](https://plotly.com/python/), [NetworkX](https://networkx.org/)
- **Dados:** [Pandas](https://pandas.pydata.org/)
- **Comunicação:** [Requests](https://requests.readthedocs.io/), [Python Telegram Bot](https://python-telegram-bot.org/)

---

## 🤝 Contribuição

Contribuições são muito bem-vindas!

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 🔌 Fonte de Dados

Além da **API de Dados Abertos da Câmara dos Deputados** ([swagger/api.html](https://dadosabertos.camara.leg.br/swagger/api.html)), o projeto também coleta dados do Senado Federal, Banco Central (SGS), SICONFI, IBGE, TSE (`dadosabertos.tse.jus.br`), Compras.gov.br, CNJ (DataJud) e Portal da Transparência.

---

## ⚠️ Limitações conhecidas dos dados

O cruzamento de fontes públicas do governo brasileiro tem lacunas estruturais que vale documentar,
para não serem confundidas com bugs:

- **Vice-presidente e vice-governador eleitos antes de 2014 não são identificáveis.** O arquivo de
  candidatos do TSE (`consulta_cand_<ano>_BRASIL.csv`) não preenche `DS_SIT_TOT_TURNO` para esses
  cargos nas eleições de 1994 a 2010 — todos os candidatos a vice aparecem com situação `#NULO`,
  vencedores e perdedores igual. Não há, nesses anos, nenhum campo confiável (número de urna,
  coligação, partido) que ligue de forma consistente o vice à chapa do titular eleito — testamos a
  hipótese de casar pelo número de urna e o padrão só se confirmou em ~38% dos casos (validado
  contra os 27 governadores eleitos de 1994 a 2010). Por isso, esses vices ficam de fora das
  listagens de "eleitos" desses anos — a alternativa seria adivinhar, o que arriscaria atribuir o
  cargo à pessoa errada.
- **Vice-prefeito eleito antes de 2012 tem a mesma lacuna, com corte diferente.** Nas eleições
  municipais de 1996, 2000, 2004 e 2008, `DS_SIT_TOT_TURNO` também vem `#NULO`/`#NULO#` para todos
  os candidatos a vice-prefeito. A partir de 2012 o TSE passou a registrar a situação normalmente.
  Prefeito e vereador não têm essa lacuna em nenhum ano coletado.
- **Eleição de 2006 para presidente/vice-presidente não tem resultado no dado do TSE.** Só nesse
  ano específico, `DS_SIT_TOT_TURNO` vem `#NULO#` para todos os candidatos a presidente e
  vice-presidente (governadores de 2006 não têm esse problema).
- **Só há foto para políticos de nível federal** (deputados/senadores, via API da Câmara/Senado).
  Presidente, governadores, deputados estaduais/distritais, prefeitos e vereadores vêm do registro
  de candidatura do TSE, que não inclui foto — o frontend mostra as iniciais do nome nesses casos.
- **Câmara/Senado mostram só o mandato atual, não o histórico de legislaturas passadas.** Já o TSE
  cobre candidatos de todas as eleições gerais (1994-2022) e municipais (1996-2024) desde a
  redemocratização. Um vereador ou deputado federal de legislaturas anteriores só aparece pelo lado
  de candidatura, dentro dos anos já coletados, não pelo lado de mandato exercido.
- **Cruzamento de sanções (CEIS/CNEP) é por nome, não por CPF.** O CPF nas bases públicas do TSE
  vem mascarado/redigido, então não há identificador único entre as fontes — o cruzamento por nome
  normalizado pode incluir homônimos.

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações (uso educacional e de pesquisa).

---

<div align="center">
  Desenvolvido com ❤️ usando dados públicos da Câmara dos Deputados do Brasil
</div>
