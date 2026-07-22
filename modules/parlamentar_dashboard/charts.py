"""
Gráficos Plotly para o dashboard parlamentar — design premium para cliente final.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Paleta de cores curada — identidade "Arquivo Nacional" ──────
# Os 8 primeiros tons passam validação CVD/contraste completa contra o fundo
# escuro (#171a23) — ordem fixa, nunca ciclada. Do 9º em diante são variações
# de apoio para séries de cauda longa (ex.: partidos menores em donuts).
CORES_CATEGORIAS = [
    "#3987e5", "#008300", "#d55181", "#c98500",
    "#199e70", "#d95926", "#9085e9", "#e66767",
    "#6a4f9e", "#2c7a9e", "#9e7a2c", "#7a9e2c",
    "#9e2c5a", "#4a4a8f", "#8f6a4a",
]

BG_CARD   = "#08090c"   # Fundo dos cards — igual ao fundo da página (unificado, sem caixas)
BG_PLOT   = "#08090c"   # Fundo da área de plotagem — mesma cor, sem blocos destacados
BORDA     = "#262a37"   # Bordas / hairline
TEXTO     = "#EFEAE0"   # Texto principal (papel)
TEXTO2    = "#a29c8c"   # Texto secundário
AZUL      = "#c9a247"   # Dourado — destaque de marca (ex-azul)
VERDE     = "#3a8f74"   # Verde-selo — sucesso
AMARELO   = "#d99a3d"   # Âmbar — atenção
VERMELHO  = "#c1583f"   # Terracota — alerta

_FONTE = dict(family="Inter, 'Segoe UI', sans-serif")


def _layout(**extra) -> dict:
    """Base de layout dark premium."""
    base = dict(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_PLOT,
        font=dict(color=TEXTO, family=_FONTE["family"], size=13),
        title_font=dict(color=TEXTO, size=17, family=_FONTE["family"]),
        margin=dict(t=60, l=20, r=20, b=30),
        coloraxis_showscale=False,
        legend=dict(
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor=BORDA,
            borderwidth=1,
            font=dict(color=TEXTO2, size=12),
        ),
        hoverlabel=dict(
            bgcolor=BG_PLOT,
            bordercolor=BORDA,
            font=dict(color=TEXTO, size=13),
        ),
    )
    base.update(extra)
    return base


def _empty_fig(mensagem: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=f"<b>{mensagem}</b>",
        showarrow=False,
        font=dict(size=15, color=TEXTO2, family=_FONTE["family"]),
        xref="paper", yref="paper",
        x=0.5, y=0.5,
    )
    fig.update_layout(**_layout(height=280))
    return fig


def _fmt_brl(v: float) -> str:
    """Formatação BRL robusta."""
    try:
        if pd.isna(v) or v is None:
            return "R$ 0,00"
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"


# ── 1. Treemap de despesas ──────────────────────────────────────
def plot_despesas_categoria(df: pd.DataFrame, nome_dep: str = "") -> go.Figure:
    """Treemap colorido e legível das despesas CEAP por categoria."""
    if df.empty or "tipoDespesa" not in df.columns:
        return _empty_fig("Sem dados de despesas para este período")

    df_copy = df.copy()
    df_copy["valorLiquido"] = pd.to_numeric(
        df_copy.get("valorLiquido", 0), errors="coerce"
    ).fillna(0.0)
    df_copy = df_copy[df_copy["valorLiquido"] > 0]

    if df_copy.empty:
        return _empty_fig("Nenhuma despesa com valor positivo encontrada")

    agrupado = (
        df_copy.groupby("tipoDespesa", as_index=False)
        .agg(total=("valorLiquido", "sum"), qtd=("valorLiquido", "count"))
        .sort_values("total", ascending=False)
    )
    total_geral = agrupado["total"].sum()
    agrupado["pct"] = (agrupado["total"] / total_geral * 100).round(1)
    agrupado["label"] = agrupado.apply(
        lambda r: f"{r['tipoDespesa']}<br><b>{_fmt_brl(r['total'])}</b><br>{r['pct']}%", axis=1
    )

    fig = px.treemap(
        agrupado,
        path=["tipoDespesa"],
        values="total",
        title="Distribuição de Despesas CEAP",
        color="tipoDespesa",
        color_discrete_sequence=CORES_CATEGORIAS,
        custom_data=["total", "pct", "qtd"],
    )
    fig.update_traces(
        texttemplate=(
            "<b>%{label}</b><br>"
            "%{customdata[1]:.1f}%"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Total: <b>R$ %{value:,.2f}</b><br>"
            "Participação: <b>%{customdata[1]:.1f}%</b><br>"
            "Notas: <b>%{customdata[2]}</b><extra></extra>"
        ),
        textfont=dict(size=13, color="white", family=_FONTE["family"]),
        marker=dict(line=dict(color=BG_CARD, width=3)),
    )
    fig.update_layout(
        **_layout(height=420),
        title=dict(
            text=f"Despesas CEAP — <b>{nome_dep}</b>",
            font=dict(size=16, color=TEXTO),
            x=0,
        ),
    )
    return fig


# ── 2. Gráfico de votações por mês ─────────────────────────────
def plot_votacoes_timeline(df: pd.DataFrame, nome_dep: str = "") -> go.Figure:
    """Barras horizontais com ranking de participação mensal."""
    if df.empty or "dataVotacao" not in df.columns:
        return _empty_fig("Sem dados de votações para este período")

    df_copy = df.copy()
    df_copy["dataVotacao"] = pd.to_datetime(df_copy["dataVotacao"], errors="coerce")
    df_copy = df_copy.dropna(subset=["dataVotacao"])

    if df_copy.empty:
        return _empty_fig("Datas de votação inválidas")

    df_copy["mes"] = df_copy["dataVotacao"].dt.to_period("M").astype(str)
    contagem = (
        df_copy.groupby("mes").size()
        .reset_index(name="votacoes")
        .sort_values("mes")
    )

    # Colorir barras pelo volume (mais escuro = mais votações)
    max_v = contagem["votacoes"].max()
    contagem["cor"] = contagem["votacoes"].apply(
        lambda v: AZUL if v >= max_v * 0.7
        else (VERDE if v >= max_v * 0.4 else TEXTO2)
    )

    fig = go.Figure(
        go.Bar(
            x=contagem["mes"],
            y=contagem["votacoes"],
            marker=dict(
                color=contagem["cor"],
                line=dict(color=BG_CARD, width=1),
                opacity=0.9,
            ),
            text=contagem["votacoes"],
            textposition="outside",
            textfont=dict(color=TEXTO, size=12),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Votações: <b>%{y}</b><extra></extra>"
            ),
        )
    )
    fig.update_layout(
        **_layout(height=380),
        title=dict(
            text=f"Participação em Votações — <b>{nome_dep}</b>",
            font=dict(size=16),
            x=0,
        ),
        xaxis=dict(
            tickangle=-40,
            gridcolor=BORDA,
            tickfont=dict(color=TEXTO2, size=11),
            title="",
            linecolor=BORDA,
        ),
        yaxis=dict(
            gridcolor=BORDA,
            tickfont=dict(color=TEXTO2, size=11),
            title="Votações",
            titlefont=dict(color=TEXTO2),
            linecolor=BORDA,
        ),
    )
    return fig


# ── 4. Gauge de participação ────────────────────────────────────
def plot_gauge_participacao(votacoes: int, total_esperado: int = 300) -> go.Figure:
    """Velocímetro de taxa de participação em votações."""
    pct = min((votacoes / total_esperado) * 100, 100) if total_esperado > 0 else 0
    cor = VERDE if pct >= 75 else (AMARELO if pct >= 40 else VERMELHO)
    label_status = (
        "Alta participação" if pct >= 75
        else ("Participação moderada" if pct >= 40
              else "Baixa participação")
    )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=votacoes,
            number=dict(
                font=dict(color=cor, size=36, family=_FONTE["family"]),
                suffix=" votos",
            ),
            title=dict(
                text=f"<b>Presença em Plenário</b><br><span style='font-size:13px;color:{TEXTO2}'>{label_status}</span>",
                font=dict(color=TEXTO, size=15, family=_FONTE["family"]),
            ),
            gauge=dict(
                axis=dict(
                    range=[0, total_esperado],
                    tickcolor=TEXTO2,
                    tickfont=dict(color=TEXTO2, size=11),
                    nticks=6,
                ),
                bar=dict(color=cor, thickness=0.7),
                bgcolor=BG_PLOT,
                borderwidth=2,
                bordercolor=BORDA,
                steps=[
                    dict(range=[0, total_esperado * 0.4], color="#2D1B1B"),
                    dict(range=[total_esperado * 0.4, total_esperado * 0.75], color="#2D2B1B"),
                    dict(range=[total_esperado * 0.75, total_esperado], color="#1B2D1B"),
                ],
                threshold=dict(
                    line=dict(color=TEXTO2, width=2),
                    thickness=0.8,
                    value=total_esperado * 0.75,
                ),
            ),
        )
    )
    fig.update_layout(
        paper_bgcolor=BG_CARD,
        font=dict(color=TEXTO, family=_FONTE["family"]),
        height=260,
        margin=dict(t=50, b=10, l=30, r=30),
    )
    return fig


# ── 5. Donut de participação por partido ───────────────────────
def plot_donut_partidos(deputados: list[dict]) -> go.Figure:
    """Ranking editorial (barras horizontais finas) da bancada por partido."""
    if not deputados:
        return _empty_fig("Sem dados de partidos")

    df = pd.DataFrame(deputados)
    if "siglaPartido" not in df.columns:
        return _empty_fig("Dados de partido indisponíveis")

    contagem = df["siglaPartido"].value_counts().reset_index()
    contagem.columns = ["partido", "total"]

    TOP_N = 10
    top = contagem.head(TOP_N).copy()
    resto = contagem.iloc[TOP_N:]["total"].sum()
    if resto > 0:
        top = pd.concat([top, pd.DataFrame([{"partido": "Outros", "total": resto}])], ignore_index=True)

    # Ordem ascendente para o maior partido ficar no topo da barra horizontal
    top = top.sort_values("total", ascending=True).reset_index(drop=True)
    total_geral = len(df)

    cores = [AZUL if p != "Outros" else BORDA for p in top["partido"]]
    # Destaque dourado apenas na maior bancada; demais em tom neutro de apoio
    cores = [
        AZUL if i == len(top) - 1 else ("#4a4636" if top["partido"].iloc[i] != "Outros" else BORDA)
        for i in range(len(top))
    ]

    fig = go.Figure(
        go.Bar(
            x=top["total"],
            y=top["partido"],
            orientation="h",
            marker=dict(color=cores, line=dict(width=0)),
            text=[f"{v}  ·  {v/total_geral*100:.1f}%" for v in top["total"]],
            textposition="outside",
            textfont=dict(color=TEXTO2, size=11.5, family=_FONTE["family"]),
            hovertemplate="<b>%{y}</b><br>Deputados: <b>%{x}</b><extra></extra>",
            cliponaxis=False,
        )
    )
    fig.update_traces(marker_cornerradius=6)
    fig.update_layout(
        **_layout(
            title=dict(
                text=f"Bancada por Partido — <span style='color:{TEXTO2};font-size:12px'>{total_geral} deputados</span>",
                font=dict(size=15, color=TEXTO, family=_FONTE["family"]),
                x=0,
            ),
            height=max(380, 34 * len(top)),
            margin=dict(t=55, l=10, r=60, b=10),
            showlegend=False,
            bargap=0.35,
        )
    )
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(
        showgrid=False,
        tickfont=dict(color=TEXTO, size=12.5, family=_FONTE["family"]),
        ticksuffix="  ",
    )
    return fig


# ── 6. Timeline de discursos ────────────────────────────────────
def plot_discursos_timeline(df: pd.DataFrame, nome_dep: str = "") -> go.Figure:
    """Barras mensais de discursos em plenário."""
    if df.empty or "dataHoraInicio" not in df.columns:
        return _empty_fig("Nenhum discurso registrado neste período")

    df_copy = df.copy()
    df_copy["dataHoraInicio"] = pd.to_datetime(df_copy["dataHoraInicio"], errors="coerce")
    df_copy = df_copy.dropna(subset=["dataHoraInicio"])

    if df_copy.empty:
        return _empty_fig("Datas de discursos inválidas")

    df_copy["mes"] = df_copy["dataHoraInicio"].dt.to_period("M").astype(str)
    contagem = df_copy.groupby("mes").size().reset_index(name="qtd").sort_values("mes")

    fig = go.Figure(
        go.Bar(
            x=contagem["mes"],
            y=contagem["qtd"],
            marker=dict(
                color=VERDE,
                line=dict(color=BG_CARD, width=1),
                opacity=0.85,
            ),
            text=contagem["qtd"],
            textposition="outside",
            textfont=dict(color=TEXTO, size=12),
            hovertemplate="<b>%{x}</b><br>Discursos: <b>%{y}</b><extra></extra>",
        )
    )
    fig.update_layout(
        **_layout(height=340),
        title=dict(
            text=f"Discursos em Plenário — <b>{nome_dep}</b>",
            font=dict(size=16), x=0,
        ),
        xaxis=dict(tickangle=-40, gridcolor=BORDA, tickfont=dict(color=TEXTO2, size=11),
                   title="", linecolor=BORDA),
        yaxis=dict(gridcolor=BORDA, tickfont=dict(color=TEXTO2, size=11),
                   title="Discursos", titlefont=dict(color=TEXTO2), linecolor=BORDA),
    )
    return fig


# ── 7. Presença em eventos por tipo ────────────────────────────
def plot_eventos_presenca(df: pd.DataFrame, nome_dep: str = "") -> go.Figure:
    """Distribuição de eventos por tipo de sessão."""
    if df.empty or "descricaoTipo" not in df.columns:
        return _empty_fig("Nenhum evento registrado neste período")

    contagem = (
        df["descricaoTipo"].value_counts()
        .reset_index()
    )
    # Garantir nomes de colunas independente da versão do pandas
    contagem.columns = ["tipo", "qtd"]
    contagem = contagem.head(10)

    fig = go.Figure(
        go.Bar(
            x=contagem["qtd"],
            y=contagem["tipo"],
            orientation="h",
            marker=dict(
                color=CORES_CATEGORIAS[:len(contagem)],
                line=dict(color=BG_CARD, width=1),
            ),
            text=contagem["qtd"],
            textposition="outside",
            textfont=dict(color=TEXTO, size=12),
            hovertemplate="<b>%{y}</b><br>Eventos: <b>%{x}</b><extra></extra>",
        )
    )
    fig.update_layout(
        **_layout(height=min(420, 120 + len(contagem) * 38)),
        title=dict(
            text=f"Presença em Eventos — <b>{nome_dep}</b>",
            font=dict(size=16), x=0,
        ),
        xaxis=dict(gridcolor=BORDA, tickfont=dict(color=TEXTO2, size=11),
                   title="Eventos", titlefont=dict(color=TEXTO2)),
        yaxis=dict(gridcolor=BORDA, tickfont=dict(color=TEXTO2, size=11),
                   title="", autorange="reversed"),
    )
    return fig


# ── 8. Tabela de órgãos/comissões ──────────────────────────────
def plot_orgaos_table(orgaos: list[dict]) -> go.Figure:
    """Tabela premium de comissões e órgãos do deputado."""
    if not orgaos:
        return _empty_fig("Deputado não participa de órgãos registrados")

    df = pd.DataFrame(orgaos)

    colunas_map = {
        "siglaOrgao":  "Sigla",
        "nomeOrgao":   "Órgão / Comissão",
        "titulo":      "Cargo",
        "dataInicio":  "Início",
        "dataFim":     "Fim",
    }
    cols = [c for c in colunas_map if c in df.columns]
    df_disp = df[cols].rename(columns=colunas_map).fillna("—")

    # Formatar datas
    for col in ["Início", "Fim"]:
        if col in df_disp.columns:
            df_disp[col] = pd.to_datetime(
                df_disp[col], errors="coerce", format="ISO8601"
            ).dt.strftime("%d/%m/%Y").fillna("—")

    # Highlight linha ainda ativa (sem dataFim)
    n = len(df_disp)
    # is_active pode ser pd.Series (quando dataFim existe) ou list pura
    # Convertemos para list para evitar AttributeError com .iloc em lista
    if "dataFim" in df.columns:
        is_active_list = df["dataFim"].isna().tolist()
    else:
        is_active_list = [False] * n
    AZUL_ALPHA = "rgba(59,130,246,0.20)"  # #3B82F6 com 20% de opacidade
    fill = [
        [AZUL_ALPHA if is_active_list[i] else (BG_PLOT if i % 2 == 0 else BG_CARD)
         for i in range(n)]
        for _ in df_disp.columns
    ]

    col_widths = [60, 350, 160, 90, 90][:len(df_disp.columns)]
    fig = go.Figure(go.Table(
        columnwidth=col_widths,
        header=dict(
            values=[f"<b>{c}</b>" for c in df_disp.columns],
            fill_color=AZUL,
            font=dict(color=BG_CARD, size=13, family=_FONTE["family"]),
            align="left", height=40,
            line=dict(color=BG_CARD, width=2),
        ),
        cells=dict(
            values=[df_disp[c].tolist() for c in df_disp.columns],
            fill_color=fill,
            font=dict(color=TEXTO, size=12, family=_FONTE["family"]),
            align="left", height=32,
            line=dict(color=BORDA, width=1),
        ),
    ))
    fig.update_layout(
        paper_bgcolor=BG_CARD,
        margin=dict(t=5, l=0, r=0, b=5),
        height=min(640, 80 + n * 33),
    )
    return fig


# ── 9. Tabela de frentes parlamentares ─────────────────────────
def plot_frentes_table(frentes: list[dict]) -> go.Figure:
    """Tabela compacta das frentes parlamentares do deputado."""
    if not frentes:
        return _empty_fig("Deputado não participa de frentes parlamentares registradas")

    df = pd.DataFrame(frentes).fillna("—")

    colunas_map = {
        "titulo":        "Frente Parlamentar",
        "idLegislatura": "Legislatura",
    }
    cols = [c for c in colunas_map if c in df.columns]
    df_disp = df[cols].rename(columns=colunas_map)

    n = len(df_disp)
    fill = [
        [BG_PLOT if i % 2 == 0 else BG_CARD for i in range(n)]
        for _ in df_disp.columns
    ]

    fig = go.Figure(go.Table(
        columnwidth=[500, 100],
        header=dict(
            values=[f"<b>{c}</b>" for c in df_disp.columns],
            fill_color=AMARELO,
            font=dict(color=BG_CARD, size=13, family=_FONTE["family"]),
            align="left", height=40,
            line=dict(color=BG_CARD, width=2),
        ),
        cells=dict(
            values=[df_disp[c].tolist() for c in df_disp.columns],
            fill_color=fill,
            font=dict(color=TEXTO, size=12, family=_FONTE["family"]),
            align="left", height=30,
            line=dict(color=BORDA, width=1),
        ),
    ))
    fig.update_layout(
        paper_bgcolor=BG_CARD,
        margin=dict(t=5, l=0, r=0, b=5),
        height=min(620, 80 + n * 31),
    )
    return fig


# ── 10. Ranking Global de Gastos ────────────────────────────────
def plot_spending_ranking(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras horizontal dos maiores gastadores."""
    if df.empty:
        return _empty_fig("Ranking indisponível")

    df_top = df.head(15).copy()
    df_top = df_top.sort_values("total_gasto", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_top["total_gasto"],
        y=df_top["nome"],
        orientation="h",
        marker=dict(
            color=df_top["total_gasto"],
            colorscale="Reds",
            line=dict(color=BG_CARD, width=1)
        ),
        text=df_top["total_gasto"].apply(_fmt_brl),
        textposition="inside",
        hovertemplate="<b>%{y}</b><br>Total: <b>%{x:,.2f}</b><br>Notas: %{customdata[0]}<extra></extra>",
        customdata=df_top[["num_notas"]]
    ))

    fig.update_layout(
        **_layout(height=500),
        title=dict(text="Top 15 Maiores Gastos (Ano Selecionado)", x=0),
        xaxis=dict(title="Total Gasto (R$)", gridcolor=BORDA),
        yaxis=dict(title="")
    )
    return fig


# ── 11. Bolhas de Anomalias (Outliers) ─────────────────────────
def plot_anomaly_bubbles(df_outliers: pd.DataFrame) -> go.Figure:
    """Gráfico de dispersão evidenciando gastos anômalos.
    
    Converte o z_score em tamanho visual através de normalização Min-Max [5, 55],
    garantindo que: (a) não existam tamanhos negativos e (b) outliers extremos não
    dominem a escala visual, mantendo todas as bolhas proporcionalmente legíveis.
    """
    if df_outliers.empty:
        return _empty_fig("Nenhuma anomalia estatística detectada (Z-Score < 3.0)")

    df_plot = df_outliers.copy()

    # Passo 1: Magnitude absoluta (sinal não faz sentido como tamanho geométrico)
    magnitude = df_plot["z_score"].abs()

    # Passo 2: Normalização Min-Max → escala visual [5, 55] px
    # O epsilon (1e-9) evita divisão por zero quando todos os z-scores são iguais
    min_m, max_m = magnitude.min(), magnitude.max()
    df_plot["bubble_size"] = (
        (magnitude - min_m) / (max_m - min_m + 1e-9)
    ) * 50 + 5   # range: 5 (mínimo legível) → 55 (máximo expressivo)

    fig = px.scatter(
        df_plot,
        x="data_documento" if "data_documento" in df_plot.columns else "mes",
        y="valor_liquido",
        size="bubble_size",
        size_max=60,   # cap para evitar bolhas absurdas em datasets com outliers extremos
        color="categoria",
        hover_name="fornecedor",
        title="Gastos com Desvio Estatístico Alto (Outliers)",
        template="plotly_dark",
        color_discrete_sequence=CORES_CATEGORIAS,
        labels={
            "valor_liquido": "Valor (R$)",
            "data_documento": "Data",
            "mes": "Mês",
            "categoria": "Categoria",
            "bubble_size": "Intensidade (Normalizada)"
        },
        custom_data=["z_score"]  # Sinal real preservado para o hover
    )

    fig.update_traces(
        marker=dict(line=dict(width=1, color=TEXTO)),
        selector=dict(mode="markers"),
        # Hover mostra o z-score original (com sinal) para precisão estatística
        hovertemplate="<b>%{hovertext}</b><br>Valor: R$ %{y:,.2f}<br>Desvio: %{customdata[0]:.2f}σ<extra></extra>"
    )

    fig.update_layout(
        **_layout(
            height=450,
            legend=dict(title_text="Categorias de Gastos", orientation="h", y=-0.2)
        )
    )
    return fig


# ── 12. Gauge de Limite CEAP ────────────────────────────────────
def plot_ceap_limit_gauge(total: float, limite: float, uf: str) -> go.Figure:
    """Velocímetro comparando gasto mensal com limite da UF."""
    pct = (total / limite) * 100 if limite > 0 else 0
    cor = VERMELHO if pct > 90 else (AMARELO if pct > 70 else VERDE)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total,
        number={
            "suffix": " / mês", 
            "font": {"color": cor, "size": 32},
            "valueformat": ",.2f"
        },
        title={"text": f"<b>Limite Cota ({uf})</b>", "font": {"size": 20}},
        gauge={
            "axis": {
                "range": [0, max(limite * 1.1, total * 1.1)], 
                "tickwidth": 1, 
                "tickformat": ",.0f",
                "tickprefix": "R$ "
            },
            "bar": {"color": cor},
            "steps": [
                {"range": [0, limite * 0.7], "color": "rgba(16, 185, 129, 0.15)"},
                {"range": [limite * 0.7, limite], "color": "rgba(245, 158, 11, 0.15)"},
                {"range": [limite, max(limite * 1.1, total * 1.1)], "color": "rgba(239, 68, 68, 0.15)"}
            ],
            "threshold": {
                "line": {"color": "white", "width": 4},
                "thickness": 0.75,
                "value": limite
            }
        }
    ))

    fig.update_layout(
        **_layout(height=320, margin=dict(t=100, b=20, l=40, r=40)),
        title=dict(text="") # Forçar título vazio para evitar "undefined"
    )
    return fig


# ── 13. Quadrantes de Eficiência (ROI) ─────────────────────────
def plot_efficiency_quadrants(df: pd.DataFrame) -> go.Figure:
    """Gráfico de Quadrantes: Custo (CEAP) vs. Entrega (Proposições)."""
    if df.empty or "qtd_proposicoes" not in df.columns:
        return _empty_fig("Dados de eficiência não disponíveis")

    # Média para definir os quadrantes
    med_gasto = df["total_gasto"].median()
    med_prop = df["qtd_proposicoes"].median()

    fig = px.scatter(
        df,
        x="total_gasto",
        y="qtd_proposicoes",
        color="siglaPartido",
        hover_name="nome",
        size="num_notas",
        title="Custo-Benefício Parlamentar: Gasto vs. Produção",
        labels={
            "total_gasto": "Total Gasto (R$)",
            "qtd_proposicoes": "Proposições Legislativas",
            "siglaPartido": "Partido"
        },
        template="plotly_dark",
        color_discrete_sequence=CORES_CATEGORIAS
    )

    # Linhas dos Quadrantes
    fig.add_vline(x=med_gasto, line_dash="dash", line_color=TEXTO2, opacity=0.5)
    fig.add_hline(y=med_prop, line_dash="dash", line_color=TEXTO2, opacity=0.5)

    # Anotações dos Quadrantes (cantos baseados em percentis para maior robustez)
    y_max = df["qtd_proposicoes"].max()
    x_max = df["total_gasto"].max()

    fig.add_annotation(x=med_gasto*0.3, y=y_max*0.8, text="Alta Eficiência", showarrow=False, font=dict(color=VERDE, size=14))
    fig.add_annotation(x=x_max*0.7, y=y_max*0.8, text="Alto Investimento", showarrow=False, font=dict(color=AZUL, size=14))
    fig.add_annotation(x=med_gasto*0.3, y=med_prop*0.3, text="Baixa Exposição", showarrow=False, font=dict(color=AMARELO, size=14))
    fig.add_annotation(x=x_max*0.7, y=med_prop*0.3, text="Baixa Eficiência", showarrow=False, font=dict(color=VERMELHO, size=14))

    fig.update_layout(
        **_layout(height=500, legend=dict(orientation="h", y=-0.2))
    )
    return fig

