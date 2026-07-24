# Gov Analise (camara-analytics) — status do projeto

> Gerado em 2026-07-22, para retomar o trabalho depois. Reflete o estado da branch
> `feature/nextjs-frontend` (commit `bf30a73`), PR aberto:
> https://github.com/DouglasScarello/gov-analise/pull/1

## O que é

Plataforma de dados públicos do governo brasileiro: coleta, trata e cruza dados de
várias fontes oficiais (Câmara, Senado, TSE, Banco Central, SICONFI, IBGE, CNJ,
Compras.gov.br, Portal da Transparência) num warehouse único, servido por uma API
FastAPI e consumido por um frontend Next.js.

## Stack

- **Coleta/ETL**: Python 3.12+, Poetry, pandas, DuckDB (warehouse embarcado em
  `data/warehouse/camara_analytics.duckdb`)
- **API**: FastAPI (`api/`), uma conexão DuckDB por requisição (read-only)
- **Frontend**: Next.js 16 (App Router, React Server Components), Tailwind v4 —
  em `web/`. **Atenção**: `web/AGENTS.md` avisa que essa versão do Next tem
  breaking changes vs. o que está no treino do modelo; ler
  `node_modules/next/dist/docs/` antes de mexer.
- **Dashboard legado**: Streamlit em `modules/parlamentar_dashboard` (projeto
  original, anterior ao frontend Next.js — ainda funciona, mas o foco atual é o
  frontend novo)

## Pipeline de dados

```
data/raw/<fonte>/<recurso>/<YYYYMMDD>.json|.parquet   (coleta bruta, gitignored)
        ↓ etl/loaders.py (carrega o snapshot mais recente)
        ↓ etl/clean.py (um limpar_<fonte>_<recurso> por fonte, tipagem/achatamento)
        ↓ etl/unify.py (cruza fontes: pessoas, sanções, contratos, tse geral)
        ↓ etl/build_warehouse.py (orquestra tudo, grava no DuckDB)
data/warehouse/camara_analytics.duckdb
```

Rodar o pipeline completo (depois de coletar os dados — ver módulos abaixo):
```
poetry run python -m etl.build_warehouse
```

`data/raw/`, `data/warehouse/` e `data/cache/` são gitignored (regeneráveis, e um
dos arquivos passa de 200MB — acima do limite do GitHub).

## Módulos de coleta (`modules/`)

Cada um segue o padrão `config.py` / `extractor.py` / `collector.py`:

| Módulo | Fonte | O que coleta |
|---|---|---|
| `camara_tracker` | Câmara dos Deputados | Snapshot dos deputados (para ETL) |
| `senado_tracker` | Senado Federal | Senadores, processos, votações |
| `bacen_tracker` | Bacen SGS | Séries (selic, ipca, dólar, etc — máx 20 últimos valores por chamada) |
| `siconfi_tracker` | SICONFI/Tesouro | Entes federativos + DCA (balanço) |
| `ibge_tracker` | IBGE | População estimada, PIB por UF |
| `tse_tracker` | TSE (CKAN) | Candidatos por ano de eleição — **ver detalhe abaixo** |
| `compras_tracker` | Compras.gov.br (PNCP) | Contratações públicas |
| `datajud_tracker` | CNJ DataJud | Processos judiciais (STJ, TST, TRF1, TJSP, TJRJ, TJMG — STF não existe na API) |
| `transparencia_tracker` | Portal da Transparência | CEIS, CNEP, contratos, órgãos SIAFI |
| `municipal_tracker` | — | Ainda não integrado ao pipeline novo (pré-existente) |

Chaves de API ficam em `.env` (gitignored, ver `.env.example`):
`DATAJUD_API_KEY`, `PORTAL_TRANSPARENCIA_API_KEY`.

### TSE — o mais trabalhoso

`modules/tse_tracker/collector.py::collect_candidatos(ano, recurso)` baixa o CSV
nacional consolidado de candidatos de um ano de eleição do TSE e salva como parquet
em `data/raw/tse/<recurso>/`. Anos já coletados:

- **Eleições gerais** (presidente, governador, senador, dep. federal/estadual) —
  recurso `candidatos_<ano>`: **1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022**
- **Eleições municipais** (prefeito, vice-prefeito, vereador) — recurso
  `candidatos_<ano>` para 1996-2020, e `candidatos` (sem sufixo, é o default) para
  2024: **1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024** — todos os anos
  municipais desde a redemocratização.

Para coletar mais um ano (geral ou municipal):
```python
from modules.tse_tracker.collector import collect_candidatos
collect_candidatos(ANO, f"candidatos_{ANO}")
```
depois adicionar `ANO` em `ANOS_ELEICAO_GERAL`/`ANOS_ELEICAO_MUNICIPAL` (em
`etl/build_warehouse.py` e em `api/routers/cargos.py`) e rodar
`poetry run python -m etl.build_warehouse` de novo.

**Nota**: o pacote CKAN de 2020 tem nome irregular (`candidatos-2020-subtemas`, não
`candidatos-2020`) — `modules/tse_tracker/extractor.py::get_candidatos` já trata
esse fallback automaticamente.

## Warehouse (tabelas principais)

- `pessoas_politicas` (593) — Câmara+Senado, mandato atual, casado por nome
- `entidades_sancionadas` (600) — CEIS+CNEP unificados
- `contratos_publicos` (16.557) — Compras.gov.br + Portal da Transparência
- `stg_tse_candidatos` (463.833) — TSE 2024, municipal (tabela legada, mantida
  para o router `municipais.py`)
- `stg_tse_candidatos_geral` (171.988) — TSE 1994-2022 concatenado, com
  `ANO_ELEICAO` — usada pelo nível nacional/estadual da API `cargos.py`
- `stg_tse_candidatos_municipal_geral` (3.510.250) — TSE 1996-2024 concatenado
  (prefeito/vice-prefeito/vereador), com `ANO_ELEICAO` — usada pelo nível
  municipal da API `cargos.py`
- `stg_camara_deputados`, `stg_senado_senadores`, `stg_senado_processos`,
  `stg_senado_votacoes`, `stg_bacen_series`, `stg_siconfi_entes`,
  `stg_siconfi_dca`, `stg_ibge_indicadores_uf`, `stg_compras_contratacoes`,
  `stg_datajud_processos`, `stg_transparencia_*`

## API (`api/`, roda em `poetry run uvicorn api.main:app --reload --port 8000`)

| Router | Endpoints |
|---|---|
| `pessoas.py` | `/pessoas`, `/pessoas/{slug}` — Câmara/Senado (legado, ainda usado pela busca) |
| `municipais.py` | `/municipais/politicos`, `/municipais/politicos/{sq}`, `/municipais/municipios` — TSE 2024 (legado, superado pelo `cargos.py` no frontend, mas mantido como API) |
| `sancoes.py` | `/sancoes` |
| `contratos.py` | `/contratos` |
| `busca.py` | `/busca?q=` — busca unificada (pessoas/sanções/contratos/órgãos) |
| `indicadores.py` | `/economia/series`, `/indicadores/uf`, `/financas/*`, `/judicial/processos`, `/legislativo/senado/processos` |
| **`cargos.py`** | **O principal agora.** `/cargos/tipos`, `/cargos/anos`, `/cargos/politicos` (filtros: `nivel`, `cargo`, `uf`, `municipio`, `ano`, `nome`), `/cargos/politicos/{nivel}/{id}` |

`nivel` em `cargos.py`: `federal` (Câmara/Senado atual, via `pessoas_politicas`),
`nacional` (presidente/vice, via `stg_tse_candidatos_geral`), `estadual`
(governador/vice/dep. estadual/distrital, mesma tabela), `municipal` (prefeito/
vice/vereador, via `stg_tse_candidatos_municipal_geral`, 1996-2024).

**Detalhe importante**: os três níveis baseados em TSE (nacional/estadual/
municipal) usam id composto `"<ano>-<sq_candidato>"` porque `SQ_CANDIDATO` do
TSE **se repete entre anos diferentes** (não é chave global).

`GET /cargos/anos?nivel=` retorna os anos coletados por nível: `nacional`/
`estadual` → 1994-2022 (eleição geral); `municipal` → 1996-2024 (eleição
municipal, ano-base diferente pois municipal é sempre par não-múltiplo de 4).

## Frontend (`web/`, roda em `npm --prefix web run dev`, porta 3000)

- `/` — home com busca
- `/busca?q=` — resultado da busca unificada
- `/politico/[slug]` — detalhe de deputado/senador (via `/pessoas/{slug}`, legado)
- `/politicos` — **página principal de navegação**: abas Federal/Estadual/Nacional/
  Municipal, filtro de cargo, filtro de UF (quando aplicável), filtro de ano
  (nacional/estadual: 1994-2022; municipal: 1996-2024), cards clicáveis
- `/cargo/[nivel]/[id]` — página de detalhe **unificada** para todos os níveis
  (usa `/cargos/politicos/{nivel}/{id}`)

`web/src/lib/api.ts` é o client central tipado. `web/.env.local` tem
`NEXT_PUBLIC_API_URL=http://localhost:8000`.

**Cuidado com cache**: os `fetch()` usam `next: { revalidate }`. O Next persiste
esse cache em disco em `web/.next/dev/cache/fetch-cache` **mesmo entre restarts do
dev server** — se os dados mudarem no backend e o frontend continuar mostrando o
valor antigo, apagar essa pasta resolve.

## Lacunas de dados conhecidas (documentadas no README)

1. **Vice-presidente/vice-governador eleitos antes de 2014** não aparecem — o TSE
   não registra a situação de eleição desse cargo nesses anos (`#NULO` pra todo
   mundo). Testei ligar pelo número de urna: só bateu em 38% dos casos (52/135,
   validado contra os 27 governadores eleitos por ano de 1994-2010) — não confiável
   o bastante pra usar sem risco de atribuir errado. **Não implementado de
   propósito.**
2. **Vice-prefeito eleito antes de 2012** tem a mesma lacuna (corte diferente:
   2012, não 2014). Confirmado nas eleições municipais de 1996, 2000, 2004 e
   2008 — `DS_SIT_TOT_TURNO` vem `#NULO`/`#NULO#` pra todo mundo. Prefeito e
   vereador não têm essa lacuna em nenhum ano.
3. **2006, presidente/vice-presidente**: TSE não tem resultado nenhum registrado
   pra esse ano específico (só esse cargo, nesse ano).
4. **Só político de nível federal tem foto** (vem da API Câmara/Senado). TSE não
   tem foto.
5. **Câmara/Senado só mostram mandato atual**, não histórico de legislaturas.
6. **Cruzamento de sanções é por nome normalizado, não CPF** (CPF vem mascarado
   nas bases públicas do TSE) — risco de homônimos.

## Tarefas que ficaram pendentes / próximos passos possíveis

- [x] ~~Coletar eleições municipais de 1996 a 2020~~ — feito, todos os anos de
      1996 a 2024 estão coletados e unificados em `stg_tse_candidatos_municipal_geral`.
- [x] ~~Avaliar se dá pra linkar vice-presidente/vice-governador/vice-prefeito
      pré-corte usando outro dataset do TSE~~ — investigado (Fase 4.2): não há
      dataset alternativo do TSE com a situação de eleição do vice separada
      nesses anos; `consulta_vagas` só traz número de cadeiras, não vínculo
      titular/vice. Fechado como limitação estrutural da fonte, documentado
      em `/sobre` e no README — a heurística por urna/coligação já testada
      só acerta ~38% dos casos, risco alto demais para publicar.
- [x] ~~Histórico de legislaturas de Câmara/Senado~~ — feito (Fase 3.3),
      1999-2027 em ambas as casas, exposto em `/politico/[slug]`.
- [ ] `municipal_tracker` (módulo pré-existente) ainda não foi integrado ao
      pipeline ETL novo
- [ ] Deputado estadual/distrital não aparece em `/cargos/tipos` com contagem —
      seria bom expor quantos há por UF/ano direto no endpoint de tipos

## Git

- Branch de trabalho: `feature/nextjs-frontend`
- PR aberto: https://github.com/DouglasScarello/gov-analise/pull/1 (contra `main`)
- Commits desta sessão: coleta TSE 1994-2022, tabela `stg_tse_candidatos_geral`,
  router `cargos.py`, unificação do frontend `/politicos` + `/cargo/[nivel]/[id]`,
  documentação das lacunas — tudo já commitado e pushed (`bf30a73`).
