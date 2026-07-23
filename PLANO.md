# Gov Analise — Plano de Produto e Arquitetura

> Documento de referência do que o projeto é, pra onde vai, e em que ordem.
> Complementa o [PROJETO_STATUS.md](PROJETO_STATUS.md), que é o retrato técnico
> do estado atual (tabelas, endpoints, páginas). Este aqui é o plano.

## 1. Visão

**Gov Analise** é uma plataforma web de transparência pública que reúne, em um
só lugar e com visual limpo, os dados abertos do Estado brasileiro: quem ocupa
e ocupou cada cargo político desde a redemocratização, como o dinheiro público
é gasto, quais empresas e pessoas foram sancionadas, e os principais
indicadores econômicos e sociais do país.

**Proposta de valor:** os dados já são públicos, mas estão espalhados em
dezenas de portais com formatos diferentes e difíceis de usar. O Gov Analise
os coleta, trata, cruza e apresenta de forma navegável por qualquer cidadão —
sem precisar entender de API, CSV ou sigla de órgão.

**Princípios do produto:**
1. **Fidelidade ao dado** — nunca inferir ou "adivinhar" informação (ex.: a
   decisão de não atribuir vices eleitos pré-2014/2012 por heurística).
   Lacunas da fonte são exibidas como avisos, não escondidas.
2. **Navegação por filtros** — o padrão já validado em `/politicos` (abas de
   nível → chips de cargo/ano/UF → cards → detalhe) é a linguagem de
   navegação de todo o site.
3. **Clareza visual** — tema claro e escuro à escolha do usuário, gráficos
   simples e legíveis, sem poluição.

## 2. O produto final (escopo completo)

Um portal com sete áreas, todas seguindo o mesmo padrão de navegação:

| Área | Conteúdo | Fonte |
|---|---|---|
| **Políticos** | Todos os cargos eletivos do Brasil, eleições 1994–2024, 4 níveis (federal/nacional/estadual/municipal) | Câmara, Senado, TSE |
| **Sanções** | Empresas e pessoas punidas pelo poder público (inidôneas, multadas) | CEIS/CNEP (Portal da Transparência) |
| **Contratos** | Contratações e compras públicas, por órgão, fornecedor e valor | Compras.gov.br, Portal da Transparência |
| **Economia** | Séries históricas: Selic, IPCA, câmbio, e outros indicadores | Banco Central (SGS) |
| **Estados & Municípios** | População, PIB, finanças públicas de cada ente federativo | IBGE, SICONFI |
| **Judiciário** | Processos por tribunal | CNJ DataJud |
| **Legislativo** | Proposições em tramitação, votações | Senado, Câmara |

Transversal a tudo: **busca unificada** (já existe) e **cruzamento por nome**
entre políticos ↔ sanções ↔ contratos.

## 3. Arquitetura (evolução, não reescrita)

```
                    ┌─ coleta agendada (um comando: python -m etl.refresh) ─┐
Fontes públicas ──► modules/*_tracker ──► data/raw/ ──► etl/ ──► DuckDB (1 arquivo)
                                                                    │ conexão read-only por request
                                                              FastAPI (/docs)
                                                                    │ JSON { items, total }
                                                              Next.js (RSC + fetch cache)
                                                       7 áreas · tema claro/escuro · gráficos
```

A fundação (coleta → ETL → DuckDB → FastAPI → Next.js) está pronta e validada.
O trabalho restante é: (a) expor no frontend o que a API já serve, (b) ampliar
a coleta onde há lacuna, (c) polir a experiência visual.

## 4. Auditoria do estado atual (o que muda o plano)

Uma auditoria do warehouse mostrou que **metade das fontes foi coletada como
amostra**, não como base completa — isso muda a ordem de trabalho: não dá pra
construir uma boa página em cima de dado raso.

| Fonte | Coletado hoje | Suficiente p/ página? |
|---|---|---|
| TSE (políticos) | 4,1 mi de registros, 1994–2024 | ✅ Completo |
| Contratos | 16,5 mil (R$ 78 bi) | ✅ Bom para v1 |
| Sanções CEIS/CNEP | 600 registros | ⚠️ Amostra — coletar base completa |
| Senado votações | 84 mil registros | ✅ Rico e **sem nenhuma página no frontend** |
| Bacen | Só 20 pontos por série (6 séries) | ❌ Gráfico de série histórica fica ridículo com 20 pontos |
| IBGE | Só 2 indicadores × 27 UFs | ⚠️ Mínimo — sem série temporal |
| DataJud | 200 processos por tribunal (amostra fixa) | ❌ Não representa nada, só demonstra |
| SICONFI | 5.598 entes, 88 mil linhas DCA | ✅ Bom para v1 |

**Gaps técnicos encontrados no código:**
1. **Frontend sem biblioteca de gráficos** — `web/package.json` só tem
   React/Next/Tailwind.
2. **Sem dark mode controlável** — `globals.css` usa apenas
   `prefers-color-scheme`; não há toggle nem classe no `<html>`.
3. **API sem envelope de paginação** — endpoints retornam array puro; o
   frontend "adivinha" se há próxima página pelo tamanho da resposta. Falta
   `{ items, total }`.
4. **Navegação global vazia** — o header do `layout.tsx` só tem o link
   "Políticos"; as outras 6 áreas não têm entrada.
5. **CORS `allow_origins=["*"]`** — aceitável em dev, precisa restringir se um
   dia publicar.
6. **Coleta manual módulo a módulo** — não existe um orquestrador global; para
   re-coletar tudo é preciso rodar 9 módulos na mão.

## 5. Decisões de arquitetura (deep dives)

### 5.1 Contrato de API — padronizar antes de multiplicar páginas
Construir as 6 páginas novas sobre o formato atual (array puro) espalha o
problema pra 9 consumidores. **Decisão: antes da Fase 1, padronizar resposta
de listagem** em `{ items: [...], total: n, limit, offset }`. Custo baixo
agora (3 páginas consumidoras); alto depois.

### 5.2 Tema claro/escuro
Cookie (`tema=claro|escuro|sistema`) lido no server component do layout →
classe `dark` no `<html>` — evita o "flash" de tema errado que uma abordagem
só-localStorage causa em SSR. Tailwind v4: trocar a variante `dark` de
media-query para classe.

### 5.3 Biblioteca de gráficos — trade-off

| Opção | Prós | Contras |
|---|---|---|
| **Recharts** ✅ | Componentes React declarativos, leve, tema via CSS vars, cobre linha/barra/donut | Menos tipos de gráfico exóticos |
| Plotly.js | Paridade com o dashboard Streamlit legado | ~1 MB de bundle, estética destoa do Tailwind |
| D3 puro | Controle total | Custo de desenvolvimento alto demais pro escopo |

**Decisão: Recharts.** Todo o escopo é linha, barra e donut. Paleta única
validada para daltonismo, nos dois temas.

### 5.4 Coleta — profundidade antes de largura
A ordem racional é **enriquecer as fontes rasas antes de construir as páginas
delas**:
- **Bacen**: o SGS aceita `dataInicial/dataFinal` — coletar 10+ anos por série
  (hoje: últimos 20 valores). Sem isso, a página de economia não se sustenta.
- **CEIS/CNEP**: paginar a coleta até o fim da base (hoje: 300 + 300
  registros).
- **DataJud**: ou aumentar a amostra com critério claro (ex.: processos de
  réus que são políticos — cruzamento novo e valioso), ou rebaixar a página
  `/judicial` para o fim da fila. A amostra atual de 200/tribunal não informa
  nada.
- **IBGE**: adicionar série histórica de população/PIB (API SIDRA) para
  gráficos de evolução por UF.

### 5.5 Orquestração da coleta
Novo `etl/refresh.py`: roda todos os coletores em sequência com tolerância a
falha individual (uma fonte fora do ar não aborta o resto), depois
`build_warehouse`. Um comando, re-executável, com resumo final do que
atualizou.

## 6. Escala e confiabilidade
- **Volume**: 372 MB / 4,6 mi de linhas — DuckDB resolve com folga; margem de
  ~10× antes de precisar repensar. Se a listagem municipal (3,5 mi) degradar,
  materializar tabela só de eleitos (~500 mil).
- **Disponibilidade das fontes**: snapshots datados em `data/raw/` preservam
  o último dado bom; ETL usa sempre o snapshot mais recente.
- **Monitoramento**: para o estágio atual, o resumo do `refresh.py`
  (contagens por tabela vs. execução anterior) é o alerta suficiente — queda
  brusca de contagem = fonte quebrou.

## 7. Roadmap

**Fase 0 — Fundações** *(1 sessão)*
- 0.1 Merge PR #1 em `main`
- 0.2 Envelope de paginação na API
- 0.3 Tema claro/escuro (cookie + classe)
- 0.4 Navegação global (7 áreas)
- 0.5 Instalar e configurar Recharts + paleta

**Fase 1 — Enriquecer coletas rasas** *(1–2 sessões)*
- 1.1 Bacen histórico longo
- 1.2 CEIS/CNEP completos
- 1.3 IBGE série histórica
- 1.4 `etl/refresh.py`

**Fase 2 — Páginas com dado bom** *(2–3 sessões)*
- 2.1 `/economia` (gráficos Recharts)
- 2.2 `/sancoes`
- 2.3 `/contratos`
- 2.4 `/estados` (indicadores + finanças SICONFI + políticos do estado)

**Fase 3 — Legislativo e cruzamentos** *(2 sessões)*
- 3.1 `/legislativo` (as 84 mil votações do Senado já coletadas — dado rico
  parado)
- 3.2 Detalhe do político enriquecido (votações + contratos vinculados)
- 3.3 Histórico de legislaturas Câmara/Senado

**Fase 4 — Judiciário e investigações** *(quando houver dado)*
- 4.1 DataJud com coleta criteriosa (ou corte)
- 4.2 Dataset alternativo TSE p/ lacuna dos vices

**Fase 5 — Qualidade contínua**
- 5.1 Responsividade
- 5.2 `/sobre` com metodologia e limitações
- 5.3 CORS restrito + hardening p/ publicação

Ordem de execução: cada item é uma unidade de trabalho fechada — implementa,
valida no navegador, commita. Não pular pra fase seguinte antes de a anterior
estar navegável.

## 8. Riscos e limitações assumidas

| Risco | Mitigação |
|---|---|
| Lacunas estruturais das fontes (vices pré-2012/2014, eleição 2006) | Avisos visíveis na interface; documentado no README |
| Cruzamento por nome pode gerar homônimos | Aviso "pode incluir homônimos" em todo cruzamento; CPF não está disponível público |
| APIs públicas mudam ou saem do ar | Snapshots em `data/raw/` preservam o último dado bom; coleta é re-executável |
| Volume municipal (3,5 mi de registros) pode pesar em queries | DuckDB aguenta bem; se degradar, criar tabela só de eleitos (~500 mil) |

## 9. O que revisitar quando crescer
- **> ~2 GB de warehouse ou consultas > 1 s**: particionar TSE por ano em
  arquivos Parquet consultados via DuckDB `read_parquet`.
- **Publicação real**: warehouse deixa de ser gerado na máquina — pipeline de
  build que gera o `.duckdb` e o publica junto do deploy da API.
- **Múltiplos usuários simultâneos**: hoje irrelevante (leitura pura, conexão
  por request); só vira tema com escrita ou personalização.
