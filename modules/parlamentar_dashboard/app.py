"""
Dashboard interativo de dados parlamentares — Módulo 4.
Execute com: poetry run streamlit run modules/parlamentar_dashboard/app.py

Endpoints utilizados: /deputados, /deputados/{id}, /deputados/{id}/despesas,
/deputados/{id}/discursos, /deputados/{id}/eventos, /deputados/{id}/orgaos,
/deputados/{id}/frentes, /partidos
"""

from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image

from modules.parlamentar_dashboard.data_loader import (
    get_deputados,
    get_deputado_detail,
    get_despesas,
    get_discursos,
    get_eventos,
    get_orgaos,
    get_frentes_deputado,
    get_partidos,
    get_ufs,
    get_proposicoes,
    calcular_total_despesas,
    get_ranking_gastos_global,
)
from modules.parlamentar_dashboard.charts import (
    plot_despesas_categoria,
    plot_donut_partidos,
    plot_discursos_timeline,
    plot_eventos_presenca,
    plot_orgaos_table,
    plot_frentes_table,
    plot_gauge_participacao,
    plot_spending_ranking,
    plot_anomaly_bubbles,
    plot_ceap_limit_gauge,
    plot_efficiency_quadrants,
)
from modules.tracker_gastos.analyzer import (
    detect_outliers,
    check_ceap_usage,
    analyze_marketing_costs,
)
import importlib
from modules.tema_miner.ai_core import AICore
importlib.reload(importlib.import_module("modules.tema_miner.ai_core"))
from modules.tema_miner.cleaner import process_ementas
from modules.tema_miner.visualizer import generate_wordcloud
from modules.municipal_tracker.loader_municipal import MunicipalLoader

# ── Identidade visual — logotipo ─────────────────────────────────
ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_FAVICON = Image.open(ASSETS_DIR / "logo_64.png")


def _logo_b64(size: int = 128) -> str:
    return base64.b64encode((ASSETS_DIR / f"logo_{size}.png").read_bytes()).decode()


# ── Configuração da Página ──────────────────────────────────────
st.set_page_config(
    page_title="Câmara Analytics",
    page_icon=LOGO_FAVICON,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://dadosabertos.camara.leg.br",
        "About": "Sistema Modular de Análise de Dados da Câmara dos Deputados",
    },
)

ESCOPO_FEDERAL = "Federal (Brasília)"
ESCOPO_MUNICIPAL = "Municipal (Florianópolis)"

# Global variables para os loaders
loader_mun = MunicipalLoader()

# ── CSS Personalizado — Identidade "Arquivo Nacional" ───────────
# Paleta institucional: tinta quase-preta + dourado latão + verde-selo.
# Serifada (Fraunces) para títulos com peso editorial, Inter para dados.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,500,0,0&display=swap');

.material-symbols-outlined {
    font-family: 'Material Symbols Rounded';
    font-weight: normal;
    font-style: normal;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
}

:root {
    --ink:          #08090c;
    --ink-2:        #0d0f14;
    --surface:      #12141b;
    --surface-2:    #171a23;
    --surface-hov:  #1c202b;
    --hairline:     #262a37;
    --hairline-2:   rgba(201, 162, 71, 0.22);
    --paper:        #EFEAE0;
    --paper-dim:    #a29c8c;
    --muted:        #6e6b78;
    --gold:         #c9a247;
    --gold-hi:      #e8c877;
    --seal:         #3a8f74;
    --seal-hi:      #4fb694;
    --amber:        #d99a3d;
    --rust:         #c1583f;
}

html, body, .stApp {
    background: var(--ink) !important;
    color: var(--paper);
}
.stApp {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background:
        radial-gradient(ellipse 1200px 600px at 15% -10%, rgba(201,162,71,0.06), transparent 55%),
        radial-gradient(ellipse 900px 500px at 100% 0%, rgba(58,143,116,0.05), transparent 50%),
        var(--ink) !important;
}
p, span, div, label { color: var(--paper); }
p, label, div[data-testid="stMarkdownContainer"] p { font-family: 'Inter', sans-serif; }

/* ─ Tipografia editorial para títulos ─ */
h1, h2, h3 {
    font-family: 'Fraunces', Georgia, serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
    color: var(--paper) !important;
}
h4, h5, h6 { font-family: 'Inter', sans-serif !important; color: var(--paper) !important; }

/* Números tabulares — despesas, contagens */
[data-testid="stMetricValue"], .stDataFrame, .kicker-num {
    font-variant-numeric: tabular-nums;
}

/* ─ Container principal: leve respiro extra ─ */
.block-container { padding-top: 1.2rem; }

/* ─ Esconde a barra nativa do Streamlit (Deploy + menu ⋮) do usuário final ─ */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* ─ Tabs externas: navegação editorial com sublinhado ─ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid var(--hairline);
    padding: 0;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--paper-dim);
    border-radius: 0;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    padding: 10px 18px 12px 18px;
    border-bottom: 2px solid transparent;
    transition: color 0.15s ease, border-color 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--paper); }
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: var(--gold-hi) !important;
    font-weight: 700 !important;
    border-bottom: 2px solid var(--gold) !important;
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ─ Métricas: sem caixa — se funde no fundo da página, só um traço ─ */
[data-testid="stMetric"] {
    background: transparent;
    border: none;
    border-bottom: 1px solid var(--hairline);
    border-radius: 0;
    padding: 6px 4px 14px 4px;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover { border-bottom-color: var(--gold); }
[data-testid="stMetricValue"] {
    font-family: 'Fraunces', Georgia, serif !important;
    font-size: 1.9rem !important;
    font-weight: 600 !important;
    color: var(--paper) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--gold) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
[data-testid="stMetricDelta"] { font-family: 'Inter', sans-serif !important; }

/* ─ Blocos/containers do Streamlit: nunca caixas visíveis ─ */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlock"] > div[style*="border"],
div[data-testid="stColumn"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ─ Botão primário: pílula dourada ─ */
.stButton > button[kind="primary"] {
    background: var(--gold);
    color: var(--ink);
    border: none;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    padding: 10px 24px;
    transition: all 0.15s ease;
}
.stButton > button[kind="primary"]:hover {
    background: var(--gold-hi);
    box-shadow: 0 4px 16px rgba(201, 162, 71, 0.35);
}

/* ─ Botão secundário (Limpar Cache): pílula contornada ─ */
.stButton > button[kind="secondary"] {
    background: transparent;
    color: var(--paper-dim);
    border: 1px solid var(--hairline);
    border-radius: 999px;
    font-weight: 500;
    transition: all 0.15s ease;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--gold);
    color: var(--gold-hi);
}
.stDownloadButton > button, .stLinkButton > a {
    border-radius: 999px !important;
}

/* ─ Selectboxes / inputs: bem arredondados, sem preencher em caixa forte ─ */
div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
    background: transparent !important;
    border-color: var(--hairline) !important;
    color: var(--paper) !important;
    border-radius: 999px !important;
    padding-left: 6px;
}
div[data-baseweb="select"]:focus-within > div, .stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px var(--gold) !important;
}
div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
    border-radius: 16px !important;
    overflow: hidden;
}

/* ─ Expanders: arredondados, sem caixa preenchida ─ */
.streamlit-expanderHeader, details summary,
div[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid var(--hairline) !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
}
div[data-testid="stExpander"] details { border: none !important; }

/* ─ Divisores e alerts: arredondados, tom sutil sobre o fundo ─ */
hr { border-color: var(--hairline); margin: 1.5rem 0; }
.stAlert {
    border-radius: 14px;
    border-left-width: 3px;
    background: rgba(255,255,255,0.02) !important;
}

/* ─ Dataframes / tabelas nativas: arredondadas e discretas ─ */
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--hairline);
}

/* ─ Imagens (fotos de perfil) ─ */
div[data-testid="stImage"] img { border-radius: 14px; }

/* ─ Gráficos Plotly: sem moldura, fundem no fundo da página ─ */
div[data-testid="stPlotlyChart"] { border-radius: 14px; overflow: hidden; }

/* ─ Ícones Material Symbols: alinhamento e peso consistentes ─ */
[data-testid="stIconMaterial"] {
    vertical-align: -4px;
    font-variation-settings: 'FILL' 0, 'wght' 500, 'GRAD' 0, 'opsz' 24;
}
.stTabs [data-testid="stIconMaterial"] { color: inherit; }

/* ─ Scrollbar fina, discreta ─ */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--ink); }
::-webkit-scrollbar-thumb { background: var(--hairline); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ─ Header customizado: barra de site, logo + marca + escopo ─ */
.ca-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 0.6rem 0 1.1rem 0;
    flex-wrap: wrap;
}
.ca-brand {
    display: flex;
    align-items: center;
    gap: 16px;
}
.ca-logo {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 0 1px var(--hairline-2), 0 6px 20px rgba(0,0,0,0.45);
    transition: box-shadow 0.2s ease;
}
.ca-brand:hover .ca-logo {
    box-shadow: 0 0 0 1px var(--gold), 0 6px 20px rgba(201,162,71,0.25);
}
.ca-kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--seal-hi);
    margin: 0 0 4px 1px;
    display: flex;
    align-items: center;
    gap: 9px;
}
.ca-kicker::before {
    content: "";
    width: 6px; height: 6px;
    background: var(--seal-hi);
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px var(--seal-hi);
}
.ca-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 2.15rem;
    font-weight: 600;
    letter-spacing: -0.015em;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(100deg, var(--paper) 40%, var(--gold-hi) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.ca-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    color: var(--paper-dim);
    margin: 4px 0 0 1px;
}
.ca-rule {
    height: 1px;
    margin: 0 0 1.6rem 0;
    background: linear-gradient(90deg, var(--gold) 0%, var(--hairline) 35%, transparent 70%);
}

/* ─ Escopo: segmented control no header, estilo pílula ─ */
.ca-scope-wrap { min-width: 260px; }
.ca-scope-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 6px 2px;
    text-align: right;
}
.ca-scope-wrap .stButtonGroup { justify-content: flex-end; }
.stButtonGroup > div {
    background: var(--surface);
    border: 1px solid var(--hairline);
    border-radius: 999px;
    padding: 3px;
    gap: 2px;
}
button[data-testid^="stBaseButton-segmented_control"] {
    border-radius: 999px !important;
    border: none !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: var(--paper-dim) !important;
    transition: all 0.15s ease;
    box-shadow: none !important;
}
button[data-testid^="stBaseButton-segmented_control"]:hover {
    color: var(--paper) !important;
    background: var(--surface-hov) !important;
}
button[data-testid="stBaseButton-segmented_controlActive"] {
    background: var(--gold) !important;
    color: var(--ink) !important;
    font-weight: 700 !important;
}
button[data-testid="stBaseButton-segmented_controlActive"]:hover {
    background: var(--gold-hi) !important;
    color: var(--ink) !important;
}
button[data-testid^="stBaseButton-segmented_control"] p { color: inherit !important; }

/* ─ Toolbar de filtros: barra horizontal no topo, estilo site ─ */
.ca-toolbar-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--gold);
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 0 0 10px 1px;
}
.ca-toolbar-label [data-testid="stIconMaterial"] { color: var(--gold); }
.ca-toolbar-icon {
    font-family: 'Material Symbols Rounded';
    font-size: 1rem;
    font-variation-settings: 'FILL' 0, 'wght' 500, 'GRAD' 0, 'opsz' 24;
    line-height: 1;
}
.ca-toolbar-rule {
    height: 1px;
    margin: 1.4rem 0 1.6rem 0;
    background: var(--hairline);
}
div[data-testid="stPopoverBody"] {
    border-radius: 16px !important;
    border-color: var(--hairline) !important;
}
.stPopover > div > button {
    border-radius: 999px !important;
    width: 100%;
}

/* ─ Grade de perfis — estilo rede social, cada deputado é um card retangular clicável ─
   Seletor de profundidade exata (não usar apenas :has(.ca-profile-card) — isso também
   casa com a coluna externa que contém a grade inteira, não só o card individual). */
div[data-testid="stColumn"]:has(> div.stVerticalBlock > div.stElementContainer > div.stMarkdown .ca-profile-card) {
    position: relative;
    margin-bottom: 10px;
}
.ca-profile-card {
    position: relative;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    text-align: left;
    gap: 16px;
    padding: 14px 18px;
    min-height: 80px;
    border: 1px solid var(--hairline);
    border-radius: 16px;
    background: var(--surface);
    transition: border-color 0.18s ease, background 0.18s ease, transform 0.12s ease;
}
/* Hover: o card fica sob um botão invisível, então o :hover real acontece no botão —
   usamos o elementContainer do card como ponte via sibling combinator (~). */
div.stElementContainer:has(> div.stMarkdown .ca-profile-card):has(~ div.stElementContainer .stButton:hover) .ca-profile-card {
    border-color: var(--gold);
    background: var(--surface-hov);
    transform: translateX(2px);
}
.ca-profile-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    object-fit: cover;
    background: var(--surface-hov);
    box-shadow: 0 0 0 2px var(--hairline-2), 0 3px 12px rgba(0,0,0,0.45);
    flex-shrink: 0;
}
div.stElementContainer:has(> div.stMarkdown .ca-profile-card):has(~ div.stElementContainer .stButton:hover) .ca-profile-avatar {
    box-shadow: 0 0 0 2px var(--gold), 0 3px 12px rgba(201,162,71,0.3);
}
.ca-profile-info {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.ca-profile-name {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.14rem;
    font-weight: 700;
    color: var(--paper);
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ca-profile-badges {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 8px;
}
.ca-party-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--ink);
    background: var(--gold);
    border-radius: 999px;
    padding: 3px 11px;
}
.ca-uf-badge {
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--paper-dim);
}
/* Botão real do Streamlit sobe por cima do card inteiro via margem negativa
   (mais robusto que position:absolute dentro do flex interno do Streamlit),
   tornando o card clicável sem exibir nenhum botão de texto ("Ver perfil"). */
div[data-testid="stColumn"]:has(> div.stVerticalBlock > div.stElementContainer > div.stMarkdown .ca-profile-card) .stButton {
    position: relative;
    z-index: 2;
    margin-top: -100px;
    height: 0;
    overflow: visible;
}
div[data-testid="stColumn"]:has(> div.stVerticalBlock > div.stElementContainer > div.stMarkdown .ca-profile-card) .stButton > button {
    width: 100%;
    height: 100px;
    background: transparent !important;
    border: none !important;
    border-radius: 16px !important;
    box-shadow: none !important;
    padding: 0 !important;
    cursor: pointer;
}
/* Esconde todo o conteúdo interno do botão (texto/ícone) — só a área clicável fica */
div[data-testid="stColumn"]:has(> div.stVerticalBlock > div.stElementContainer > div.stMarkdown .ca-profile-card) .stButton > button * {
    display: none !important;
}

/* ─ Modal de perfil (st.dialog) ─ */
.ca-modal-header {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-bottom: 6px;
}
.ca-modal-avatar {
    width: 88px;
    height: 88px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 0 0 2px var(--gold), 0 6px 18px rgba(0,0,0,0.45);
    flex-shrink: 0;
}
.ca-modal-name {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--paper);
    line-height: 1.2;
    margin: 0 0 6px 0;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────
def _fmt_int(valor: int) -> str:
    """Formata inteiros com separador de milhar brasileiro."""
    return f"{valor:,}".replace(",", ".")

def _fmt_brl(valor: float) -> str:
    """Formata valores monetários no padrão brasileiro com segurança para NaN."""
    try:
        if pd.isna(valor) or valor is None:
            return "R$ 0,00"
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"


# ── Session state ──────────────────────────────────────────────
for key, default in {
    "analise_feita": False,
    "analise_dep_id": None,
    "analise_dados": {},
    "perfil_aberto": None,
    "perfis_visiveis": 24,
    "nome_sel_input": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


@st.dialog("Perfil do Parlamentar")
def _dialog_perfil(dep: dict) -> None:
    """Card de perfil rápido — estilo rede social — ao clicar em um deputado."""
    nome = dep.get("nome", "—")
    partido = dep.get("siglaPartido", "—")
    uf = dep.get("siglaUf", "—")
    email = dep.get("email") or "Não informado"
    foto = dep.get("urlFoto") or ""

    st.markdown(f"""
    <div class="ca-modal-header">
        <img src="{foto}" class="ca-modal-avatar" onerror="this.style.visibility='hidden'" />
        <div>
            <div class="ca-modal-name">{nome}</div>
            <div class="ca-profile-badges" style="justify-content:flex-start;">
                <span class="ca-party-badge">{partido}</span>
                <span class="ca-uf-badge">{uf}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f":material/mail: {email}")
    st.caption("Toque em analisar para ver despesas, discursos, eventos e frentes na aba **Análise Individual**.")

    if st.button("Analisar mandato completo", icon=":material/search:", type="primary", width="stretch"):
        st.session_state.nome_sel_input = nome
        st.session_state.perfil_aberto = None
        st.rerun()


# ══ Header ══════════════════════════════════════════════════════
col_brand, col_scope = st.columns([3, 2], vertical_alignment="center")

with col_scope:
    st.markdown('<div class="ca-scope-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="ca-scope-label">Escopo de transparência</div>', unsafe_allow_html=True)
    escopo = st.segmented_control(
        "Escopo de transparência",
        [ESCOPO_FEDERAL, ESCOPO_MUNICIPAL],
        default=ESCOPO_FEDERAL,
        label_visibility="collapsed",
        key="escopo_control",
    )
    if not escopo:
        escopo = ESCOPO_FEDERAL
    st.markdown('</div>', unsafe_allow_html=True)

with col_brand:
    if escopo == ESCOPO_FEDERAL:
        kicker = "Dados Abertos · Câmara dos Deputados"
        titulo = "Câmara Analytics"
        subtitulo = "Leitura pública e independente da atividade parlamentar brasileira"
    else:
        kicker = "Dados Abertos · Câmara Municipal de Florianópolis"
        titulo = "Florianópolis Analytics"
        subtitulo = "Monitoramento legislativo da Câmara Municipal (CMF-SC)"

    st.markdown(f"""
    <div class="ca-header">
        <div class="ca-brand">
            <img src="data:image/png;base64,{_logo_b64(128)}" class="ca-logo" alt="Câmara Analytics" />
            <div>
                <div class="ca-kicker">{kicker}</div>
                <h1 class="ca-title">{titulo}</h1>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<p class="ca-subtitle">{subtitulo}</p><div class="ca-rule"></div>', unsafe_allow_html=True)


# ══ Toolbar de filtros ═════════════════════════════════════════
st.markdown(
    '<div class="ca-toolbar-label"><span class="ca-toolbar-icon">tune</span> Filtros</div>',
    unsafe_allow_html=True,
)

# Bug Hunt: Anos dinâmicos
ano_atual = datetime.now().year
anos_disponiveis = [ano_atual, ano_atual - 1, ano_atual - 2]

col_uf, col_partido, col_spacer, col_sobre, col_limpar = st.columns(
    [1.6, 1.6, 3.2, 1.2, 1.5], vertical_alignment="bottom"
)

with col_uf:
    with st.spinner("Carregando UFs..."):
        ufs = get_ufs()
    uf = st.selectbox(":material/map: Estado (UF)", options=["Todos"] + ufs, index=0)
    uf_param = None if uf == "Todos" else uf

with col_partido:
    with st.spinner("Carregando partidos..."):
        partidos = get_partidos()
    partido = st.selectbox(":material/military_tech: Partido", options=["Todos"] + partidos, index=0)
    partido_param = None if partido == "Todos" else partido

with col_sobre:
    with st.popover(":material/info: Sobre", width="stretch"):
        st.markdown("""
        **Câmara Analytics v1.0**

        Dados: [API Dados Abertos](https://dadosabertos.camara.leg.br)

        :material/sync: Cache: 1h (listas) / 30min (análises)
        """)

with col_limpar:
    if st.button("Limpar Cache", icon=":material/delete:", help="Força atualização de todos os dados", width="stretch"):
        st.cache_data.clear()
        st.session_state.analise_feita = False
        st.session_state.analise_dados = {}
        st.toast("Cache limpo!", icon=":material/check_circle:")

st.markdown('<div class="ca-toolbar-rule"></div>', unsafe_allow_html=True)


def main_federal():
    # ══ Abas Principais ═════════════════════════════════════════════
    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/group: Deputados",
        ":material/search: Análise Individual",
        ":material/trophy: Rankings & Auditoria",
        ":material/info: Sobre"
    ])


    # ─── Aba 1: Lista de Deputados ──────────────────────────────────
    with tab1:
        st.subheader("Deputados Federais")

        with st.spinner("Buscando todos os deputados..."):
            deputados = get_deputados(uf=uf_param, partido=partido_param)

        if not deputados:
            st.warning("Nenhum deputado encontrado. Tente outros filtros.", icon=":material/search:")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Deputados", len(deputados))
            partidos_unicos = len({d.get("siglaPartido") for d in deputados if d.get("siglaPartido")})
            c2.metric("Partidos", partidos_unicos)
            ufs_unicas = len({d.get("siglaUf") for d in deputados if d.get("siglaUf")})
            c3.metric("Estados", ufs_unicas)

            st.divider()

            col_perfis, col_donut = st.columns([3, 2])
            with col_donut:
                st.plotly_chart(plot_donut_partidos(deputados), width="stretch")

            with col_perfis:
                st.caption(f":material/badge: Perfis — {len(deputados)} deputados")

                limite = min(st.session_state.perfis_visiveis, len(deputados))
                visiveis = deputados[:limite]

                n_colunas = 2
                linhas = [visiveis[i:i + n_colunas] for i in range(0, len(visiveis), n_colunas)]
                for linha in linhas:
                    cols = st.columns(n_colunas, gap="small")
                    for col, dep in zip(cols, linha):
                        with col:
                            nome = dep.get("nome", "—")
                            partido = dep.get("siglaPartido", "—")
                            uf = dep.get("siglaUf", "—")
                            foto = dep.get("urlFoto") or ""
                            st.markdown(f"""
                            <div class="ca-profile-card">
                                <img src="{foto}" class="ca-profile-avatar" onerror="this.style.visibility='hidden'" />
                                <div class="ca-profile-info">
                                    <div class="ca-profile-name">{nome}</div>
                                    <div class="ca-profile-badges">
                                        <span class="ca-party-badge">{partido}</span>
                                        <span class="ca-uf-badge">{uf}</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button("Ver perfil", key=f"perfil_btn_{dep.get('id')}", width="stretch"):
                                st.session_state.perfil_aberto = dep

                if limite < len(deputados):
                    restantes = len(deputados) - limite
                    if st.button(
                        f"Carregar mais perfis ({restantes} restantes)",
                        icon=":material/expand_more:",
                        width="stretch",
                    ):
                        st.session_state.perfis_visiveis += 24
                        st.rerun()

            if st.session_state.perfil_aberto is not None:
                _dialog_perfil(st.session_state.perfil_aberto)


    # ─── Aba 2: Análise Individual ──────────────────────────────────
    with tab2:
        st.subheader("Análise Individual do Parlamentar")

        with st.spinner("Carregando lista de deputados..."):
            lista_base = get_deputados(uf=uf_param, partido=partido_param)

        if not lista_base:
            st.warning("Nenhum deputado disponível. Ajuste os filtros na sidebar.", icon=":material/warning:")
        else:
            opcoes = {dep["nome"]: dep["id"] for dep in lista_base if dep.get("nome")}

            col_sel, col_btn = st.columns([5, 1])
            with col_sel:
                nome_sel = st.selectbox(
                    "Selecione o Deputado",
                    options=sorted(opcoes.keys()),
                    label_visibility="collapsed",
                    placeholder="Digite o nome do deputado...",
                    key="nome_sel_input",
                )
            with col_btn:
                analisar = st.button("Analisar", icon=":material/search:", type="primary")

            dep_id = opcoes.get(nome_sel)

            # Guard: nome_sel pode ser None se opcoes estiver vazio
            if not dep_id:
                st.info("Selecione um deputado e clique em Analisar.", icon=":material/touch_app:")
            elif analisar or (st.session_state.analise_feita and st.session_state.analise_dep_id == dep_id):
                if analisar or not st.session_state.analise_dados:
                    # Ano padrão: current – 1 (mais completo)
                    ano = ano_atual - 1

                    with st.status("Carregando dados do parlamentar...", expanded=True) as status:
                        st.write(":material/description: Dados cadastrais...")
                        detalhes = get_deputado_detail(dep_id)
                        dados_dep = detalhes.get("ultimoStatus", {}) if detalhes else {}

                        st.write(f":material/payments: Despesas CEAP ({ano})...")
                        df_desp = get_despesas(dep_id, ano)

                        st.write(f":material/mic: Discursos ({ano})...")
                        df_disc = get_discursos(dep_id, ano)

                        st.write(f":material/event: Eventos ({ano})...")
                        df_eventos = get_eventos(dep_id, ano)

                        st.write(":material/account_balance: Órgãos e comissões...")
                        orgaos = get_orgaos(dep_id)

                        st.write(":material/flag: Frentes parlamentares...")
                        frentes = get_frentes_deputado(dep_id)

                        st.write(":material/fact_check: Auditoria e anomalias...")
                        df_desp_audit = df_desp.rename(columns={
                            "tipoDespesa": "categoria", 
                            "valorLiquido": "valor_liquido", 
                            "dataDocumento": "data_documento",
                            "nomeFornecedor": "fornecedor"
                        })
                        df_outliers = detect_outliers(df_desp_audit)
                        ceap_status = check_ceap_usage(df_desp_audit.rename(columns={"ano": "ano", "mes": "mes"}), dados_dep.get("siglaUf", "DF"))

                        st.write(":material/bar_chart: Produtividade Legislativa...")
                        prop = get_proposicoes(dep_id, ano)
                        qtd_prop = len(prop)
                        total_g = calcular_total_despesas(df_desp)
                        # Bug Hunt: ROI mais informativo para produção zero
                        roi = total_g / qtd_prop if qtd_prop > 0 else 0
                        
                        textos_ementas = [p.get("ementa", "") for p in prop if p.get("ementa")]
                        # Unir ementas para análise de complexidade média
                        texto_completo = " ".join(textos_ementas)
                        complexidade = AICore.calcular_indice_complexidade(texto_completo)
                        tokens_deputado = process_ementas(textos_ementas)
                        
                        # Chamadas reais do Gemini (Com Fallback e Cache Persistente)
                        resumo_ia = AICore.sumarizar_perfil_llm(tokens_deputado, dep_id)
                        
                        primeira_ementa = textos_ementas[0] if textos_ementas else ""
                        politiques = AICore.traduzir_politiques(primeira_ementa)
                        
                        # Sentimento - Pegar o discurso mais recente
                        ultimo_discurso = df_disc.iloc[0]["transcricao"] if not df_disc.empty else ""
                        sentimento = AICore.analisar_sentimento_llm(ultimo_discurso, dep_id)

                        status.update(label="Dados carregados!", state="complete", expanded=False)

                    st.session_state.analise_feita = True
                    st.session_state.analise_dep_id = dep_id
                    st.session_state.analise_dados = {
                        "detalhes": detalhes, "df_desp": df_desp,
                        "df_disc": df_disc, "df_eventos": df_eventos,
                        "orgaos": orgaos, "frentes": frentes, "ano": ano,
                        "outliers": df_outliers, "ceap": ceap_status,
                        "qtd_prop": qtd_prop, "roi": roi,
                        "complexidade": complexidade,
                        "tokens": tokens_deputado,
                        "resumo_ia": resumo_ia,
                        "politiques": politiques,
                        "sentimento": sentimento
                    }
                else:
                    d = st.session_state.analise_dados
                    detalhes   = d["detalhes"]
                    df_desp    = d["df_desp"]
                    df_disc    = d["df_disc"]
                    df_eventos = d["df_eventos"]
                    orgaos     = d["orgaos"]
                    frentes    = d["frentes"]
                    df_outliers = d.get("outliers", pd.DataFrame())
                    ceap_status = d.get("ceap", {})
                    qtd_prop    = d.get("qtd_prop", 0)
                    roi         = d.get("roi", 0)
                    complexidade = d.get("complexidade", {"score": 0, "nivel": "N/A"})
                    tokens_deputado = d.get("tokens", [])
                    resumo_ia = d.get("resumo_ia", "Processando...")
                    politiques = d.get("politiques", "N/A")
                    sentimento = d.get("sentimento", "N/A")
                    ano        = d.get("ano", ano_atual - 1)

                # ── Perfil ────────────────────────────────────────

                col_foto, col_info = st.columns([1, 4])
                with col_foto:
                    foto = dados_dep.get("urlFoto")
                    if foto:
                        st.image(foto, width=130)
                    else:
                        st.markdown("## :material/account_circle:")

                with col_info:
                    nome_oficial = dados_dep.get("nome", nome_sel)
                    st.markdown(f"### {nome_oficial}")
                    ic1, ic2, ic3 = st.columns(3)
                    ic1.markdown(f"**:material/military_tech: Partido**\n\n{dados_dep.get('siglaPartido', '—')}")
                    ic2.markdown(f"**:material/map: Estado**\n\n{dados_dep.get('siglaUf', '—')}")
                    gab = dados_dep.get("gabinete") or {}
                    ic3.markdown(f"**:material/apartment: Gabinete**\n\nPrédio {gab.get('predio', '—')}, Sala {gab.get('sala', '—')}")
                    email = dados_dep.get("email") or "—"
                    st.caption(f":material/mail: {email}")

                st.info(
                    f"Dados do ano **{ano}** "
                    f"— o mais recente com informações completas.",
                    icon=":material/info:",
                )
                st.divider()

                # ── Métricas de atividade ─────────────────────────
                total_desp = calcular_total_despesas(df_desp)
                total_notas = len(df_desp)
                total_disc = len(df_disc)
                total_eventos = len(df_eventos)
                total_orgaos = len(orgaos)
                total_frentes = len(frentes)

                st.divider()

                # Bug Hunt: Layout métricas (3x2 em telas pequenas é melhor do que 6 columns)
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("Gasto CEAP", _fmt_brl(total_desp))
                    st.metric("Eventos", total_eventos)
                with m_col2:
                    st.metric("Notas Fiscais", total_notas)
                    st.metric("Comissões", total_orgaos)
                with m_col3:
                    st.metric("Discursos", total_disc)
                    st.metric("Frentes", total_frentes)

                st.divider()

                # ── Indicadores de Produção vs Gasto (V3.0)
                st.markdown("### :material/bar_chart: Eficiência Legislativa")
                c_roi1, c_roi2, c_roi3 = st.columns(3)
                with c_roi1:
                    st.metric("Proposições", _fmt_int(qtd_prop))
                with c_roi2:
                    # Gasto Total com formato BRL resumido ou completo
                    gasto_fmt = _fmt_brl(total_desp).replace(",00", "")
                    st.metric("Gasto Total", gasto_fmt)
                with c_roi3:
                    # ROI com formatação BRL correta
                    roi_label = _fmt_brl(roi).replace(",00", "") if roi > 0 else "N/A (Sem Produção)"
                    st.metric("R$ / Proposição", roi_label,
                              help="Custo médio por projeto de lei ou proposição legislativa.")

                st.divider()

                # ── Abas de visualização ──────────────────────────
                sub1, sub2, sub3, sub4, sub5, sub6 = st.tabs([
                    ":material/payments: Despesas CEAP",
                    ":material/mic: Discursos",
                    ":material/event: Eventos",
                    ":material/account_balance: Órgãos",
                    ":material/flag: Frentes",
                    ":material/psychology: IA & Linguística",
                ])

                with sub1:
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        st.plotly_chart(
                            plot_despesas_categoria(df_desp, nome_oficial),
                            width="stretch",
                        )
                    with col_g2:
                        st.plotly_chart(
                            plot_gauge_participacao(total_notas, total_esperado=500),
                            width="stretch",
                        )

                    if not df_desp.empty:
                        with st.expander(":material/list_alt: Ver detalhamento completo das despesas"):
                            cols_show = [c for c in [
                                "tipoDespesa", "dataDocumento", "nomeFornecedor",
                                "valorDocumento", "valorLiquido",
                            ] if c in df_desp.columns]
                            df_show = df_desp[cols_show].copy()
                            if "valorLiquido" in df_show.columns:
                                df_show["valorLiquido"] = pd.to_numeric(
                                    df_show["valorLiquido"], errors="coerce"
                                )
                            st.dataframe(
                                df_show.sort_values("valorLiquido", ascending=False)
                                if "valorLiquido" in df_show.columns else df_show,
                                width="stretch",
                                height=400,
                            )

                with sub2:
                    st.plotly_chart(
                        plot_discursos_timeline(df_disc, nome_oficial),
                        width="stretch",
                    )
                    if not df_disc.empty and "tipoDiscurso" in df_disc.columns:
                        with st.expander(":material/list_alt: Ver lista de discursos"):
                            cols_d = [c for c in ["dataHoraInicio", "tipoDiscurso", "sumario", "urlTexto"]
                                      if c in df_disc.columns]
                            st.dataframe(df_disc[cols_d], width="stretch", height=350)

                with sub3:
                    st.plotly_chart(
                        plot_eventos_presenca(df_eventos, nome_oficial),
                        width="stretch",
                    )
                    if not df_eventos.empty:
                        with st.expander(":material/list_alt: Ver lista de eventos"):
                            cols_e = [c for c in ["dataHoraInicio", "situacao", "descricaoTipo", "descricao"]
                                      if c in df_eventos.columns]
                            st.dataframe(df_eventos[cols_e], width="stretch", height=350)

                with sub4:
                    st.caption(f":material/account_balance: {total_orgaos} órgão(s) e comissão(es) registrados. Linhas azul-claro = mandato ativo.")
                    st.plotly_chart(
                        plot_orgaos_table(orgaos),
                        width="stretch",
                    )

                with sub5:
                    st.caption(f":material/flag: {total_frentes} frente(s) parlamentar(es) registrada(s).")
                    st.plotly_chart(
                        plot_frentes_table(frentes),
                        width="stretch",
                    )

                with sub6:
                    st.markdown("### :material/psychology: Inteligência Artificial (V4.0)")
                    ci1, ci2 = st.columns([1, 2])

                    with ci1:
                        st.metric("Índice de Complexidade", complexidade["score"],
                                  help="Flesch Reading Ease (PT). Quanto maior, mais acessível o texto.")
                        st.markdown(f"**Nível de Acesso:**\n`{complexidade['nivel']}`")

                        st.divider()
                        st.markdown("#### :material/record_voice_over: Sentimento & Retórica")
                        st.info(f"O tom predominante do discurso mais recente foi: **{sentimento}**")

                        st.divider()
                        st.markdown("#### :material/history_edu: Resumo do Perfil (IA)")
                        st.success(resumo_ia)

                    with ci2:
                        st.markdown("#### :material/lock_open: Tradutor de Politiquês")
                        if politiques != "N/A":
                            st.markdown(f"> **Último Projeto Simplicado:**\n> {politiques}")
                        else:
                            st.write("Nenhuma ementa recente para traduzir.")

                        st.markdown("#### :material/cloud: Nuvem de Temas Legislativos")
                        if tokens_deputado:
                            fig_wc = generate_wordcloud(tokens_deputado, titulo=f"Eixos de Atuação — {nome_oficial}")
                            if fig_wc:
                                st.pyplot(fig_wc)
                        else:
                            st.info("Nenhuma proposição registrada para gerar nuvem de temas.")

                # ── Seção de Auditoria (Novidade V2.0) ────────────
                st.divider()
                col_a1, col_a2 = st.columns([2, 1])
                with col_a1:
                    st.plotly_chart(plot_anomaly_bubbles(df_outliers), use_container_width=True)
                with col_a2:
                    if ceap_status:
                        st.plotly_chart(
                            plot_ceap_limit_gauge(ceap_status["total"], ceap_status["limite"], dados_dep.get("siglaUf", "??")),
                            use_container_width=True
                        )
                        if ceap_status["excedeu"]:
                            st.error(f"**ALERTA**: O parlamentar excedeu o limite mensal da UF ({ceap_status['percentual']}% do teto).", icon=":material/warning:")
                        elif ceap_status["percentual"] > 80:
                            st.warning(f"**Atenção**: Gasto próximo ao limite mensal ({ceap_status['percentual']}%).", icon=":material/notifications:")


    # ─── Aba 3: Rankings & Auditoria Global ────────────────────────
    with tab3:
        st.subheader(":material/trophy: Rankings Globais e Auditoria da Casa")
        ano_sel_rank = st.selectbox("Escolha o ano para o ranking", options=anos_disponiveis, index=1)

        # Verifica se já tem cache em disco — se sim, carrega direto; se não, exige clique
        from pathlib import Path as _PathR
        _cache_dir  = _PathR(__file__).parent.parent.parent / "data" / "cache"
        _cache_file = _cache_dir / f"ranking_global_{ano_sel_rank}.parquet"
        _tem_cache  = _cache_file.exists()

        if not _tem_cache:
            st.info(
                "**Ranking não calculado ainda para este ano.**\n\n"
                "A geração inicial busca dados de todos os 513 deputados (≈ 2-3 min). "
                "Após a primeira vez, o resultado fica em cache e carrega instantaneamente."
            )
            if not st.button("Gerar Ranking Agora", icon=":material/rocket_launch:", type="primary", key="btn_gerar_ranking"):
                st.stop()

        with st.spinner("Carregando ranking..."):
            df_rank = get_ranking_gastos_global(ano_sel_rank)

        if df_rank.empty:
            st.info("Dados não disponíveis para este ano.")
        else:
            c1, c2, c3 = st.columns(3)
            total_casa = df_rank["total_gasto"].sum()
            c1.metric("Total Gasto pela Câmara", f"R$ {total_casa/1e6:.1f}M")
            c2.metric("Média por Deputado", f"R$ {(total_casa/513)/1e3:.1f}k")
            top_g = df_rank.iloc[0]["total_gasto"]
            c3.metric("Maior Gasto Individual", f"R$ {top_g/1e3:.1f}k", help=f"Responsável: {df_rank.iloc[0]['nome']}")

            st.divider()
            col_r1, col_r2 = st.columns([2, 1])
            with col_r1:
                st.plotly_chart(plot_efficiency_quadrants(df_rank), use_container_width=True)
                st.plotly_chart(plot_spending_ranking(df_rank), use_container_width=True)
            with col_r2:
                st.markdown("### :material/trophy: Top 10 Eficiência (ROI)")
                # Ordenar por menor custo por proposição, mas apenas para quem tem ao menos 1 proposição
                df_roi = df_rank[df_rank["qtd_proposicoes"] > 0].sort_values("custo_por_proposicao", ascending=True).head(10)
                st.dataframe(
                    df_roi[["nome", "qtd_proposicoes", "custo_por_proposicao"]].style.format({
                        "custo_por_proposicao": lambda x: _fmt_brl(x).replace(",00", ""),
                        "qtd_proposicoes": "{:n}"
                    }),
                    hide_index=True,
                    use_container_width=True
                )
                
                st.divider()
                st.markdown("### :material/list_alt: Maiores Gastos")
                st.dataframe(
                    df_rank[["nome", "siglaPartido", "total_gasto"]].head(10).style.format({"total_gasto": "R$ {:,.2f}"}),
                    hide_index=True,
                    use_container_width=True
                )


    # ─── Aba 4: Sobre ───────────────────────────────────────────────
    with tab4:
        st.subheader(":material/info: Sobre o Câmara Analytics")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            ### :material/account_balance: O que é?
            O **Câmara Analytics** faz parte do **Sistema Modular de Análise de Dados da Câmara dos Deputados**.

            ### :material/inventory_2: Módulos do Sistema
            | Módulo | Função |
            |--------|--------|
            | `tracker_gastos` | Despesas CEAP (CSV/Parquet) |
            | `network_analyst` | Redes de influência política |
            | `legis_notifier` | Alertas via Telegram |
            | `parlamentar_dashboard` | **Este dashboard** |
            | `tema_miner` | NLP em ementas legislativas |
            """)
        with col_b:
            st.markdown("""
            ### :material/cable: Endpoints da API Utilizados
            | Dado | Endpoint |
            |------|----------|
            | Lista de deputados | `GET /deputados` |
            | Detalhe do deputado | `GET /deputados/{id}` |
            | Despesas CEAP | `GET /deputados/{id}/despesas` |
            | Discursos | `GET /deputados/{id}/discursos` |
            | Presença em eventos | `GET /deputados/{id}/eventos` |
            | Órgãos/comissões | `GET /deputados/{id}/orgaos` |
            | Frentes parlamentares | `GET /deputados/{id}/frentes` |
            | Lista de partidos | `GET /partidos` |

            ### :material/storage: Cache Configurado
            - **Listas** (deputados, partidos): **1 hora**
            - **Análises individuais**: **30 minutos**

        ---
        Fonte: [API de Dados Abertos da Câmara](https://dadosabertos.camara.leg.br)
        """)

def main_municipal():
    """Painel Legislativo da Câmara Municipal de Florianópolis."""
    tab1, tab2, tab3 = st.tabs([
        ":material/group: Servidores Públicos",
        ":material/list_alt: Pautas e Sessões",
        ":material/tv: TV Câmara & Notícias"
    ])
    
    with tab1:
        # ── Inicializa estado de navegação ────────────────────────
        if "vereador_sel" not in st.session_state:
            st.session_state.vereador_sel = None

        veredadores = loader_mun.get_vereadores()
        if not veredadores:
            st.warning("Não foi possível carregar a lista de servidores públicos.")
        else:
            COR_PARTIDO = {
                "PT": "#E53E3E", "PL": "#2B6CB0", "MDB": "#D69E2E",
                "PSD": "#2F855A", "PSOL": "#6B46C1", "PP": "#C05621",
                "REPUBLICANOS": "#B83280", "PDT": "#285E61", "PSDB": "#2563EB",
                "SOLIDARIEDADE": "#D97706", "UNIÃO": "#0F766E",
            }

            # ════════════════════════════════════════════════════════
            # MODO DETALHE: exibe perfil completo do vereador selecionado
            # ════════════════════════════════════════════════════════
            if st.session_state.vereador_sel is not None:
                v = st.session_state.vereador_sel
                nome    = v.get("nome") or v.get("nomeVereador") or "N/A"
                partido = (v.get("partido") or v.get("siglaPartido") or "—").upper()
                funcao  = v.get("funcao") or v.get("cargo") or "Vereador(a)"
                foto    = v.get("imagem") or v.get("urlFoto") or v.get("foto") or ""
                link    = v.get("link") or v.get("url") or ""
                cor     = COR_PARTIDO.get(partido, "#4A5568")

                # Botão de voltar
                if st.button("Voltar à lista", icon=":material/arrow_back:", key="btn_voltar_vereador"):
                    st.session_state.vereador_sel = None
                    st.rerun()

                st.divider()

                # ── Header do perfil ──────────────────────────────
                col_foto, col_info = st.columns([1, 3])
                with col_foto:
                    if foto:
                        st.markdown(
                            f"<img src='{foto}' style='width:160px;height:160px;border-radius:50%;"
                            f"object-fit:cover;border:4px solid {cor};display:block;margin:0 auto'>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<div style='width:160px;height:160px;border-radius:50%;background:{cor};"
                            f"display:flex;align-items:center;justify-content:center;"
                            f"margin:0 auto'><span class='material-symbols-outlined' "
                            f"style='font-size:64px;color:white'>person</span></div>",
                            unsafe_allow_html=True
                        )

                with col_info:
                    st.markdown(f"## {nome}")
                    st.markdown(
                        f"<span style='background:{cor};color:white;font-size:14px;font-weight:700;"
                        f"padding:4px 14px;border-radius:20px'>{partido}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**Cargo:** {funcao}")
                    st.markdown(f"**Câmara:** Câmara Municipal de Florianópolis (CMF-SC)")
                    if link:
                        st.link_button("Ver perfil oficial na CMF", link, icon=":material/account_balance:")
                st.divider()

                # ── Análise Crítica a partir dos PDFs manuais ──────────────
                import subprocess as _sp
                import unicodedata as _ud
                from pathlib import Path as _Path

                BASE_DIR = _Path(__file__).parent.parent.parent
                ANALISE_DIR = BASE_DIR / "Analise"

                def _normalizar_texto(texto: str) -> str:
                    """Remove acentos, converte para minúsculas e limpa caracteres especiais."""
                    if not texto: return ""
                    texto = texto.lower()
                    # Remove acentos
                    texto = "".join(
                        c for c in _ud.normalize('NFD', texto)
                        if _ud.category(c) != 'Mn'
                    )
                    # Remove pontuação básica para facilitar o match
                    for char in "._-()[],:":
                        texto = texto.replace(char, " ")
                    return " ".join(texto.split())

                def _buscar_pdf_analise(nome_vereador: str):
                    """
                    Busca dinamicamente na pasta Analise/ um PDF que corresponda ao nome.
                    """
                    if not ANALISE_DIR.exists():
                        return None
                    
                    nome_norm = _normalizar_texto(nome_vereador)
                    primeiro_nome = nome_norm.split()[0]
                    
                    # Scaneia todos os PDFs na pasta
                    for pdf_path in ANALISE_DIR.glob("*.pdf"):
                        pdf_norm = _normalizar_texto(pdf_path.name)
                        
                        # Match se o nome normalizado do vereador estiver no nome do arquivo
                        # ou se partes significativas (como sobrenome único ou apelido) baterem
                        if nome_norm in pdf_norm:
                            return pdf_path
                        
                        # Match secundário por primeiro nome + partes adicionais
                        partes_vereador = set(nome_norm.split())
                        partes_pdf = set(pdf_norm.split())
                        
                        # Se houver interseção significativa (ex: primeiro nome + sobrenome)
                        intersecao = partes_vereador.intersection(partes_pdf)
                        # Ignora palavras curtas/comuns no match
                        intersecao = {p for p in intersecao if len(p) > 3}
                        
                        if len(intersecao) >= 1:
                            # Se for o primeiro nome + algo mais, ou um nome único longo
                            if primeiro_nome in intersecao or any(len(p) > 5 for p in intersecao):
                                return pdf_path
                                
                    return None


                def _ler_pdf_texto(pdf_path) -> str:
                    try:
                        result = _sp.run(
                            ["pdftotext", "-layout", str(pdf_path), "-"],
                            capture_output=True, text=True, timeout=10
                        )
                        return result.stdout.strip()
                    except Exception:
                        return ""

                pdf_path = _buscar_pdf_analise(nome)

                if pdf_path:
                    st.markdown("### :material/description: Análise Crítica")
                    st.success(f"Análise disponível — {pdf_path.name}", icon=":material/push_pin:")

                    texto_pdf = _ler_pdf_texto(pdf_path)
                    if texto_pdf:
                        import re as _re

                        def _render_pdf_formatado(texto: str):
                            """
                            Renderiza texto de PDF como markdown limpo.
                            Agrupa por blocos (separados por linha em branco),
                            detecta títulos curtos e renderiza o resto como parágrafo.
                            """
                            # Normaliza múltiplas linhas em branco
                            texto = _re.sub(r'\n{3,}', '\n\n', texto)
                            blocos = texto.split('\n\n')

                            for bloco in blocos:
                                # Junta linhas do bloco num texto contínuo
                                linhas = [l.strip() for l in bloco.strip().split('\n') if l.strip()]
                                if not linhas:
                                    continue

                                texto_bloco = ' '.join(linhas)
                                # Remove números de referência soltos no final (ex: .3, 12)
                                texto_bloco = _re.sub(r'\s+\d+\s*$', '', texto_bloco).strip()

                                if not texto_bloco:
                                    continue

                                # --- Detecta título ---
                                # Bloco de 1 linha, curto (≤ 90 chars),
                                # sem ponto/vírgula no fim, começando com maiúscula
                                eh_titulo = (
                                    len(linhas) <= 2 and
                                    len(texto_bloco) <= 90 and
                                    not texto_bloco.endswith(('.', ',')) and
                                    not texto_bloco.startswith('|') and
                                    texto_bloco[0].isupper() and
                                    ':' not in texto_bloco
                                )

                                if eh_titulo:
                                    st.markdown(f"### {texto_bloco}")
                                else:
                                    # Parágrafo — remove espaços internos excessivos
                                    texto_bloco = _re.sub(r'  +', ' ', texto_bloco)
                                    st.markdown(texto_bloco)

                        _render_pdf_formatado(texto_pdf)

                    else:
                        st.info("PDF carregado mas texto não pôde ser extraído. Baixe o PDF para visualizar.")

                    # Botão de download do PDF
                    with open(pdf_path, "rb") as f_pdf:
                        st.download_button(
                            label="Baixar análise completa (PDF)",
                            data=f_pdf.read(),
                            file_name=pdf_path.name,
                            mime="application/pdf",
                            icon=":material/download:",
                        )
                else:
                    st.markdown("### :material/description: Análise Crítica")
                    st.info("Análise individual ainda não disponível para este servidor. Em breve.", icon=":material/info:")
                    if link:
                        st.markdown(f"Consulte o [perfil oficial na CMF]({link}) enquanto isso.")

            # ════════════════════════════════════════════════════════
            # MODO GRID: lista todos os vereadores em cards clicáveis
            # ════════════════════════════════════════════════════════
            else:
                st.subheader("Servidores Públicos de Florianópolis")
                st.metric("Total de Servidores", len(veredadores))
                st.divider()

                cols = st.columns(4)
                for i, v in enumerate(veredadores):
                    nome    = v.get("nome") or v.get("nomeVereador") or "N/A"
                    partido = (v.get("partido") or v.get("siglaPartido") or "—").upper()
                    funcao  = v.get("funcao") or v.get("cargo") or "Vereador(a)"
                    foto    = v.get("imagem") or v.get("urlFoto") or v.get("foto") or ""
                    cor     = COR_PARTIDO.get(partido, "#4A5568")

                    with cols[i % 4]:
                        foto_html = (
                            f"<img src='{foto}' style='width:80px;height:80px;border-radius:50%;"
                            f"object-fit:cover;border:3px solid {cor};margin-bottom:8px;"
                            f"display:block;margin-left:auto;margin-right:auto'>"
                            if foto else
                            f"<div style='width:80px;height:80px;border-radius:50%;background:{cor};"
                            f"display:flex;align-items:center;justify-content:center;"
                            f"margin:0 auto 8px auto'><span class='material-symbols-outlined' "
                            f"style='font-size:32px;color:white'>person</span></div>"
                        )
                        st.markdown(f"""
                        <div style='background:transparent;border:1px solid #262a37;border-radius:16px;
                            padding:16px 12px;text-align:center;margin-bottom:4px'>
                            {foto_html}
                            <div style='font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:14px;color:#EFEAE0;
                                margin-bottom:4px;white-space:nowrap;overflow:hidden;
                                text-overflow:ellipsis' title='{nome}'>{nome}</div>
                            <span style='background:{cor};color:white;font-size:11px;
                                font-weight:700;padding:2px 8px;border-radius:20px;
                                display:inline-block;margin-bottom:4px'>{partido}</span>
                            <div style='color:#a29c8c;font-size:12px'>{funcao}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Botão Streamlit sobreposto ao card
                        if st.button("Ver perfil", icon=":material/visibility:", key=f"ver_{i}", use_container_width=True):
                            st.session_state.vereador_sel = v
                            st.rerun()

    with tab2:
        st.subheader("Pautas das Próximas Sessões")
        pautas = loader_mun.get_pautas()
        if not pautas:
            st.info("Nenhuma pauta recente encontrada.")
        else:
            # Dicionário de Comissões da CMF-Florianópolis
            COMISSOES_CMF = {
                "CCJ":      ("Constituição e Justiça",                       "Analisa a constitucionalidade e legalidade de propostas de lei."),
                "CECD":     ("Educação, Cultura e Desporto",                   "Discute ensino, projetos culturais e programas esportivos no município."),
                "CDDPD":    ("Direitos das Pessoas com Deficiência",           "Analisa políticas de acessibilidade, inclusão e direitos de PcD."),
                "CDDMPIG":  ("Direitos das Mulheres e Inclusão de Gênero",    "Pauta políticas para igualdade de gênero e proteção à mulher."),
                "CTLSSP":   ("Turismo, Lazer, Segurança e Serviço Público",  "Debute turismo sustentável, segurança pública e serviços ao cidadão."),
                "CCTOII":   ("Ciência, Tecnologia, Obras e Infraestrutura",   "Pauta inovação, obras públicas e desenvolvimento de infraestrutura."),
                "CVOPU":    ("Vigilância, Obras Públicas e Urbanismo",        "Fiscaliza obras públicas e discute planejamento urbano da cidade."),
                "CS":       ("Saúde",                                          "Debate saúde pública: UBSs, hospitais, vigilância sanitária."),
                "CF":       ("Finanças",                                       "Analisa o orçamento municipal, tributos e contas públicas."),
                "CMMA":     ("Meio Ambiente",                                   "Discusses preservação ambiental, saneamento e fauna urbana."),
                "CMH":      ("Habitação",                                      "Analisa projetos de moradia, regularização fundiária e PMCMV."),
                "CTA":      ("Transporte e Acessibilidade",                    "Debate mobilidade urbana, transporte coletivo e ciclovias."),
            }
            TIPO_SESSAO = {
                "Audiência Pública":             (":material/mic:", "Sessão aberta à participação cidadã. Qualquer pessoa pode se inscrever para falar."),
                "Sessão Ordinária":              (":material/gavel:", "Sessão regular do plenário para votação de projetos de lei e deliberações."),
                "Sessão Extraordinária":         (":material/bolt:", "Convocada fora do calendário regular para pautas urgentes."),
                "Reunião Ordinária de Comissão": (":material/list_alt:", "Reunião técnica de comissão para análise detalhada de propostas."),
                "Reunião Extraordinária de Comissão": (":material/bolt:", "Reunião de comissão fora do calendário por urgência."),
            }

            import re as _re

            def _resumo_pauta(titulo: str) -> tuple:
                icone, tipo_desc = ":material/list_alt:", ""
                for tipo, (ico, desc) in TIPO_SESSAO.items():
                    if tipo.lower() in titulo.lower():
                        icone, tipo_desc = ico, desc
                        break
                match = _re.search(r'\(([A-Z]{2,10})\)', titulo)
                comissao_txt = ""
                if match:
                    sigla = match.group(1)
                    if sigla in COMISSOES_CMF:
                        nome, desc_c = COMISSOES_CMF[sigla]
                        comissao_txt = f"**Comissão:** {nome} `({sigla})`  —  {desc_c}"
                    else:
                        comissao_txt = f"**Comissão:** `{sigla}`"
                resumo = comissao_txt
                if tipo_desc:
                    resumo += ("\n\n" if comissao_txt else "") + f"_{tipo_desc}_"
                return icone, resumo or "Sessão legislativa da Câmara Municipal de Florianópolis."


            # --- Busca e Filtragem Hardcore ---
            st.markdown("#### :material/search: Buscar nas Pautas")
            col_search_1, col_search_2 = st.columns([3, 1])
            with col_search_1:
                search_query = st.text_input("Filtrar por título, data ou comissão:", placeholder="Ex: CCJ, 2024, Audiência...", label_visibility="collapsed")
            with col_search_2:
                st.write(f":material/bar_chart: {len(pautas)} pautas carregadas")

            if search_query:
                pautas_filtered = [
                    p for p in pautas 
                    if search_query.lower() in (p.get("titulo", "") + p.get("data", "")).lower()
                ]
                st.info(f"Encontradas {len(pautas_filtered)} pautas correspondentes.")
            else:
                pautas_filtered = pautas

            # --- Lógica de Paginação das Pautas ---
            if "pautas_limit" not in st.session_state or search_query:
                # Reset do limite ao pesquisar para mostrar resultados relevantes
                st.session_state.pautas_limit = 100 if not search_query else 50
            
            pautas_page = pautas_filtered[:st.session_state.pautas_limit]

            for p in pautas_page:
                data_fmt = p.get("data") or p.get("dataSessao") or "Data não informada"
                titulo = p.get("titulo") or p.get("nome") or "Sem Título"
                link = p.get("url") or p.get("link") or p.get("urlPauta") or ""
                icone, resumo = _resumo_pauta(titulo)
                with st.expander(f"{icone} {data_fmt} — {titulo}"):
                    st.markdown(resumo)
                    if link:
                        st.markdown(f":material/description: [Ver proposições em pauta]({link})")

            # Botão para carregar mais pautas
            if len(pautas_filtered) > st.session_state.pautas_limit:
                if st.button(f"Ver mais 100 pautas (+{len(pautas_filtered) - st.session_state.pautas_limit} restantes)", icon=":material/expand_more:", use_container_width=True):
                    st.session_state.pautas_limit += 100
                    st.rerun()


    with tab3:
        st.subheader("Últimas Notícias e Vídeos")
        noticias = loader_mun.get_noticias()
        tv = loader_mun.get_tv_camara()
        
        col_n, col_v = st.columns(2)
        with col_n:
            st.markdown("#### :material/newspaper: Portal de Notícias (CMF)")
            for n in noticias[:5]:
                st.markdown(f"**{n.get('data')}** - {n.get('titulo')}")
                st.caption(n.get("resumo", ""))
                st.divider()

        with col_v:
            st.markdown("#### :material/videocam: TV Câmara Florianópolis")
            if not tv:
                st.info("Nenhum vídeo disponível no momento.")
            else:
                for video in tv[:5]:
                    titulo = video.get("titulo") or video.get("descricao") or "Vídeo CMF"
                    legenda = video.get("data") or video.get("dataSessao") or ""

                    # A CMF pode usar campos variados para a URL
                    link = (
                        video.get("url") or video.get("urlVideo") or
                        video.get("link") or video.get("urlYoutube") or ""
                    )

                    # Tenta embed do YouTube se for link YT
                    if link and ("youtube.com" in link or "youtu.be" in link):
                        try:
                            st.video(link)
                            st.caption(f":material/event: {legenda} — {titulo}")
                        except Exception:
                            st.markdown(f":material/movie: [{titulo}]({link})")
                    elif link:
                        # Link de página HTML → exibe como card clicável
                        st.markdown(
                            f"""<div style='border:1px solid #262a37; border-left:3px solid #c9a247;
                                border-radius:16px; padding:12px 16px; margin-bottom:8px; background:transparent'>
                            <span class='material-symbols-outlined' style='font-size:16px;
                                vertical-align:-3px;color:#e8c877'>movie</span>
                            <a href="{link}" target="_blank" style='color:#e8c877;
                                text-decoration:none; font-weight:600'>{titulo}</a>
                            <br><small style='color:#a29c8c'>{legenda}</small>
                            </div>""",
                            unsafe_allow_html=True
                        )
                    else:
                        # Sem URL — mostra o que tiver
                        with st.expander(f":material/movie: {titulo}"):
                            st.json(video)

# ── Execução do App ───────────────────────────────────────────
if escopo == ESCOPO_FEDERAL:
    main_federal()
else:
    main_municipal()
