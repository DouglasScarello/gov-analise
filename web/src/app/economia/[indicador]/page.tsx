import Link from "next/link";
import { notFound } from "next/navigation";
import SerieLineChart from "@/components/charts/SerieLineChart";
import { listarSeriesEconomicas, listarIndicadoresUf } from "@/lib/api";

// Revalidate a cada 0 segundos (SSR dinâmico, sem cache)
export const revalidate = 0;

// Configuração de indicadores com explicação em linguagem leiga
const INDICADORES = {
  selic_meta: {
    nome: "Selic (meta)",
    unidade: "% a.a.",
    explicacao: `A Selic é a taxa básica de juros definida pelo Banco Central. Quando sobe, crédito fica mais caro e poupança rende mais. Quando cai, facilita compras parceladas mas poupança rende menos.`,
    meta: { valor: 10, label: "Meta histórica média" },
    intervalo: { minBom: 8, maxBom: 13, label: "8% a 13% é considerado moderado" },
    interpretacao: (valor: number) => {
      if (valor < 8) return { status: "bom", msg: "Juros baixos facilitam compras, mas poupança não rende bem. Bom para devedores." };
      if (valor <= 13) return { status: "neutro", msg: "Nível moderado de juros, balanceado entre poupança e crédito." };
      return { status: "ruim", msg: "Juros altos encarecem crédito e compras. Bom só para quem poupa." };
    },
  },
  ipca_variacao_mensal: {
    nome: "IPCA (variação mensal)",
    unidade: "%",
    explicacao: `Índice de Preços ao Consumidor Amplo. Mede a variação mensal de preços que você paga na vida cotidiana (alimento, gasolina, aluguel, etc). Acima de zero significa inflação (tudo fica mais caro).`,
    meta: { valor: 0.25, label: "Meta mensal (~3% ao ano)" },
    intervalo: { minBom: -0.1, maxBom: 0.4, label: "Até 0,4% ao mês é aceitável" },
    interpretacao: (valor: number) => {
      if (valor < 0) return { status: "bom", msg: "Deflação — preços caindo. Ótimo para o bolso, raro no Brasil." };
      if (valor <= 0.4) return { status: "bom", msg: "Inflação controlada. Seus gastos aumentam lentamente." };
      return { status: "ruim", msg: "Inflação alta. Tudo fica mais caro rapidamente. Seu poder de compra diminui." };
    },
  },
  ipca_acumulado_12_meses: {
    nome: "IPCA (acumulado 12 meses)",
    unidade: "%",
    explicacao: `Acumulação da inflação nos últimos 12 meses. Mostra quanto seus gastos aumentaram no período de um ano. É a métrica de inflação que mais você percebe no dia a dia.`,
    meta: { valor: 3, label: "Meta do Banco Central" },
    intervalo: { minBom: 2, maxBom: 4, label: "2% a 4% é saudável" },
    interpretacao: (valor: number) => {
      if (valor < 2) return { status: "bom", msg: "Inflação baixa. Seu dinheiro compra mais no ano." };
      if (valor <= 4) return { status: "bom", msg: "Inflação na meta. Estável e previsível." };
      if (valor <= 8) return { status: "neutro", msg: "Inflação acima da meta. Preços subiram bastante no ano." };
      return { status: "ruim", msg: "Inflação muito alta. Seu poder de compra caiu significativamente no ano." };
    },
  },
  igpm_variacao_mensal: {
    nome: "IGP-M (variação mensal)",
    unidade: "%",
    explicacao: `Índice Geral de Preços do Mercado. Mede inflação com foco em atacado e matérias-primas (afeta mais empresas e indústria). É usado para reajustes de aluguel e contratos.`,
    meta: { valor: 0.25, label: "Meta mensal (~3% ao ano)" },
    intervalo: { minBom: -0.5, maxBom: 0.5, label: "±0,5% é normal" },
    interpretacao: (valor: number) => {
      if (Math.abs(valor) <= 0.5) return { status: "bom", msg: "Variação normal. Afeta principalmente empresas e reajustes de contrato." };
      if (valor > 0.5) return { status: "ruim", msg: "Alta inflação de matérias-primas. Aluguéis e contratos podem reajustar mais." };
      return { status: "bom", msg: "Deflação de custos. Podem haver reajustes menores em aluguéis." };
    },
  },
  dolar_ptax_venda: {
    nome: "Dólar (PTAX venda)",
    unidade: "R$",
    explicacao: `Cotação do dólar americano em reais. Sobe quando Real enfraquece (importações ficam caras, exportações ganham competitividade). Cai quando Real fortalece.`,
    meta: null,
    intervalo: { minBom: 4.5, maxBom: 5.5, label: "Entre 4,5 e 5,5 é histórico normal" },
    interpretacao: (valor: number) => {
      if (valor < 4.5) return { status: "bom", msg: "Real forte. Viagens ao exterior ficam mais baratas, mas produtos importados estão em desvantagem." };
      if (valor <= 5.5) return { status: "neutro", msg: "Câmbio estável. Equilíbrio entre importações e exportações." };
      return { status: "ruim", msg: "Real fraco. Importações caras (tecnologia, combustível). Viagens externas ficam caras." };
    },
  },
  dolar_ptax_compra: {
    nome: "Dólar (PTAX compra)",
    unidade: "R$",
    explicacao: `Cotação de compra do dólar. Similar ao de venda, mas é o preço que os bancos pagam por dólares. A diferença entre compra e venda é o spread dos bancos.`,
    meta: null,
    intervalo: { minBom: 4.5, maxBom: 5.5, label: "Entre 4,5 e 5,5 é histórico normal" },
    interpretacao: (valor: number) => {
      if (valor < 4.5) return { status: "bom", msg: "Real forte. Similar ao câmbio de venda." };
      if (valor <= 5.5) return { status: "neutro", msg: "Câmbio normal." };
      return { status: "ruim", msg: "Real fraco. Tudo que precisa ser importado fica mais caro." };
    },
  },
  taxa_desocupacao_pnad: {
    nome: "Taxa de desocupação (PNAD)",
    unidade: "%",
    explicacao: `Percentual de pessoas que querem trabalhar mas não têm emprego. Medida mensal pela PNAD Contínua do IBGE. Acima de 10% indica mercado de trabalho tenso.`,
    meta: { valor: 7, label: "Taxa natural de desemprego" },
    intervalo: { minBom: 6, maxBom: 9, label: "6% a 9% é saudável" },
    interpretacao: (valor: number) => {
      if (valor < 6) return { status: "bom", msg: "Desemprego muito baixo. Mercado de trabalho aquecido, oportunidades de emprego." };
      if (valor <= 9) return { status: "bom", msg: "Desemprego normal. Mercado de trabalho saudável." };
      if (valor <= 12) return { status: "neutro", msg: "Desemprego elevado. Muitas pessoas buscando emprego." };
      return { status: "ruim", msg: "Desemprego muito alto. Mercado de trabalho em crise, poucas oportunidades." };
    },
  },
  ibc_br: {
    nome: "IBC-Br (Atividade Econômica)",
    unidade: "",
    explicacao: `Índice de Atividade Econômica do Banco Central. É um proxy do PIB mensal que mostra se a economia está acelerando ou desacelerando. Sobe = economia crescendo, cai = economia contraindo.`,
    meta: null,
    intervalo: null,
    interpretacao: (valor: number, histórico?: Array<{ valor: number }>) => {
      if (!histórico || histórico.length < 2) return { status: "neutro", msg: "Atividade econômica — veja a tendência no gráfico." };
      const anterior = histórico[histórico.length - 2].valor;
      const mudanca = valor - anterior;
      if (mudanca > 0) return { status: "bom", msg: "Economia crescendo. Mais produção, mais empregos, mais atividade econômica." };
      if (mudanca < 0) return { status: "ruim", msg: "Economia contraindo. Menos produção e atividade — sinal de recessão." };
      return { status: "neutro", msg: "Atividade econômica estável." };
    },
  },
  balanca_comercial_saldo: {
    nome: "Balança Comercial (saldo)",
    unidade: "US$ bilhões",
    explicacao: `Diferença entre exportações e importações em dólares. Positivo = exportamos mais (bom para o câmbio). Negativo = importamos mais (gasto de dólar).`,
    meta: { valor: 0, label: "Equilibrado" },
    intervalo: { minBom: 0, maxBom: 10, label: "Superávit de até 10 bi é bom" },
    interpretacao: (valor: number) => {
      if (valor > 2) return { status: "bom", msg: "Superávit. Exportamos mais que importamos — entram dólares, fortalece o Real." };
      if (valor >= -2) return { status: "neutro", msg: "Balança equilibrada. Exportações e importações próximas." };
      return { status: "ruim", msg: "Déficit. Importamos mais que exportamos — saem dólares, enfraquece o Real." };
    },
  },
  reservas_internacionais: {
    nome: "Reservas Internacionais",
    unidade: "US$ bilhões",
    explicacao: `Dólares e outros ativos que o Brasil tem guardados. Usados para proteger o câmbio em crises. Reservas altas dão segurança econômica, reservas baixas indicam stress.`,
    meta: { valor: 300, label: "Nível de segurança" },
    intervalo: { minBom: 250, maxBom: 400, label: "250 a 400 bi é saudável" },
    interpretacao: (valor: number) => {
      if (valor > 350) return { status: "bom", msg: "Reservas altas. Brasil tem proteção contra crises. Moeda forte, segurança econômica." };
      if (valor >= 250) return { status: "bom", msg: "Reservas adequadas. Suficientes para proteger o câmbio em crises." };
      if (valor >= 200) return { status: "neutro", msg: "Reservas baixas. Proteção reduzida contra crises cambiais." };
      return { status: "ruim", msg: "Reservas muito baixas. Risco de crise cambial. Economia vulnerável." };
    },
  },
  divida_liquida_setor_publico_pct_pib: {
    nome: "Dívida Líquida (% do PIB)",
    unidade: "% do PIB",
    explicacao: `Quanto o governo deve, em proporção do que o país produz em um ano. Acima de 60% é considerado alto. Sobe quando governo gasta mais que arrecada.`,
    meta: { valor: 45, label: "Nível sustentável" },
    intervalo: { minBom: 40, maxBom: 55, label: "Abaixo de 55% é controlado" },
    interpretacao: (valor: number) => {
      if (valor < 40) return { status: "bom", msg: "Dívida baixa. Governo tem espaço para investir ou ajudar em crises." };
      if (valor <= 55) return { status: "bom", msg: "Dívida controlada. Sustentável no longo prazo." };
      if (valor <= 70) return { status: "neutro", msg: "Dívida elevada. Governo com menos espaço para gastar. Risco de aumento de impostos." };
      return { status: "ruim", msg: "Dívida muito alta. Insustentável. Risco de crise fiscal ou aumento de inflação." };
    },
  },
  pib_taxa_crescimento: {
    nome: "PIB (taxa de crescimento)",
    unidade: "% a.a.",
    explicacao: `Taxa acumulada em 4 trimestres do Produto Interno Bruto. Mede se a economia está expandindo estruturalmente. PIB potencial brasileiro estimado em 2,0%-2,5% a.a. pós-reformas (média 2014-2024: ~0,8% a.a., fortemente impactada por recessões). Comparar sempre contra a taxa natural.`,
    meta: { valor: 2.5, label: "PIB potencial ~2,0%-2,5% a.a." },
    intervalo: { minBom: 2.5, maxBom: 3.5, label: "Acima de 2,5% é expansão real" },
    interpretacao: (valor: number) => {
      if (valor > 2.5) return { status: "bom", msg: "Expansão real da economia. Crescimento acima do PIB potencial, fechamento de hiato do produto, economia em avanço estrutural." };
      if (valor >= 1.5) return { status: "neutro", msg: "Crescimento sustentável. Alinhado ao PIB potencial, crescimento em linha com o potencial estimado, sem pressões de superaquecimento." };
      return { status: "ruim", msg: "Abaixo do potencial / Estagnação. Economia crescendo abaixo do potencial ou em contração, próxima à estagnação da renda per capita, ociodade generalizada." };
    },
  },
  spread_bancario: {
    nome: "Spread Bancário",
    unidade: "%",
    explicacao: `Diferença entre taxa média de juros cobrada (aplicação) e custo de captação de crédito livre. Spread alto = crédito caro. Decomposição: risco/inadimplência (~35-37%), custos administrativos (~25%), tributos/FGC (~20%), margem do banco (~15-19%). Brasil tem um dos maiores spreads do mundo (~28% média histórica).`,
    meta: { valor: 26, label: "Média histórica recente" },
    intervalo: { minBom: 20, maxBom: 30, label: "Entre 20% e 30% é histórico" },
    interpretacao: (valor: number) => {
      if (valor < 24) return { status: "bom", msg: "Spread baixo. Ambiente de liquidez sustentável, economia em fase de expansão creditícia, concorrência saudável, redução de risco de crédito." };
      if (valor <= 30) return { status: "neutro", msg: "Spread na faixa histórica normal (~24%-30%). Sistema financeiro resiliente apesar do risco de crédito elevado, típico do Brasil." };
      return { status: "ruim", msg: "Spread em nível de estresse (>30%). Crédito asfixiante, economia em contração, Selic elevada, alta inadimplência." };
    },
  },
  taxa_cambio_real_efetiva: {
    nome: "Taxa de Câmbio Real Efetiva (TCRE)",
    unidade: "Índice (jun/1994=100)",
    explicacao: `Índice de competitividade do Brasil vs. ~23-24 parceiros comerciais, ajustado por diferenciais de inflação (IPCA vs. CPI exterior). Base: junho/1994=100. Acima de 100 = Real fraco (exportações mais competitivas). Abaixo de 100 = Real forte (importações ganham). Faixa histórica: 70-145; média de longo prazo: 105-115.`,
    meta: { valor: 110, label: "Faixa histórica equilibrada" },
    intervalo: { minBom: 100, maxBom: 120, label: "Entre 100 e 120 é equilíbrio" },
    interpretacao: (valor: number) => {
      if (valor >= 100 && valor <= 120) return { status: "bom", msg: "Câmbio em equilíbrio. Faixa da média móvel histórica, Real nem muito forte nem muito fraco, câmbio não pressiona inflação, exportações competitivas sem estresse." };
      if ((valor >= 85 && valor < 100) || (valor > 120 && valor <= 130)) return { status: "neutro", msg: "Desalinhamento moderado. Fora da faixa ideal de equilíbrio, mas sem crise cambial ou inflacionária severa." };
      return { status: "ruim", msg: "Desalinhamento severo. Real excessivamente valorizado (<85) causando desindustrialização, OU excessivamente desvalorizado (>130) causando choque inflacionário e estresse." };
    },
  },
  resultado_primario_governo: {
    nome: "Resultado Primário do Governo (% PIB)",
    unidade: "% do PIB",
    explicacao: `Saldo entre receitas e despesas primárias (excluindo juros). Superávit = governo reduz dívida; Déficit = dívida cresce. Metas Arcabouço Fiscal 2025: 0% (banda ±0,25%), 2026: +0,25%. Para estabilizar dívida estruturalmente, exige ~1,5%-2,0% do PIB (r-g>0 atual).`,
    meta: { valor: 1.0, label: "Superávit estrutural necessário ~1,5%-2,0%" },
    intervalo: { minBom: 1.0, maxBom: 2, label: "Acima de 1,0% estabiliza dívida" },
    interpretacao: (valor: number) => {
      if (valor > 1.0) return { status: "bom", msg: "Superávit em nível estrutural. Governo reversendo dinâmica de dívida, poupança crescente, risco-país caindo, sustentabilidade fiscal." };
      if (valor >= -0.25) return { status: "neutro", msg: "Dentro da meta legal (Arcabouço Fiscal). Conformidade jurídica até o limite inferior da banda (±0,25%), mas insuficiente para estabilizar dívida bruta no longo prazo." };
      return { status: "ruim", msg: "Déficit acelerado (< -0,25%). Fora da banda legal, gatilhos de contenção fiscal acionados, dívida acelerando, risco de dominância fiscal." };
    },
  },
  pib_uf: {
    nome: "PIB por estado",
    unidade: "",
    explicacao: `Produto Interno Bruto estadual. Mede o valor total de tudo que é produzido em cada estado. Cresce = economia estadual em expansão. Cai = economia estadual retraindo.`,
    meta: null,
    intervalo: null,
    interpretacao: () => ({ status: "neutro", msg: "Veja o PIB de cada estado e compare com anos anteriores no gráfico." }),
  },
  populacao_estimada_uf: {
    nome: "População estimada",
    unidade: "",
    explicacao: `Número de habitantes por estado, atualizado anualmente pelo IBGE. Usado para calcular PIB per capita e entender crescimento demográfico.`,
    meta: null,
    intervalo: null,
    interpretacao: () => ({ status: "neutro", msg: "Dados de população por estado, atualizados anualmente." }),
  },
  taxa_desocupacao_uf: {
    nome: "Taxa de desocupação por estado",
    unidade: "%",
    explicacao: `Desemprego em cada estado. Varia bastante por região — algumas têm mercado de trabalho mais dinâmico que outras.`,
    meta: null,
    intervalo: null,
    interpretacao: () => ({ status: "neutro", msg: "Desemprego varia por estado. Compare e veja quais regiões têm melhor mercado de trabalho." }),
  },
  rendimento_medio_uf: {
    nome: "Rendimento médio por estado",
    unidade: "R$",
    explicacao: `Salário médio em cada estado (ajustado pela inflação). Varia muito entre regiões — São Paulo e Distrito Federal têm rendimentos maiores que nordeste.`,
    meta: null,
    intervalo: null,
    interpretacao: () => ({ status: "neutro", msg: "Salários variam bastante por região. Compare a renda média de cada estado." }),
  },
};

type IndicadorKey = keyof typeof INDICADORES;

export default async function IndicadorPage({ params }: { params: Promise<{ indicador: string }> }) {
  const { indicador: indicadorParam } = await params;
  const indicador = indicadorParam as IndicadorKey;

  if (!(indicador in INDICADORES)) {
    notFound();
  }

  const config = INDICADORES[indicador];

  let dados: Array<{ data: string; valor: number }> = [];
  let mín = 0,
    máx = 0,
    médio = 0;

  try {
    const raw = await listarSeriesEconomicas(indicador);
    dados = [...(raw || [])].reverse().map((p: any) => ({ data: p.data, valor: p.valor }));

    if (dados.length > 0) {
      const valores = dados.map((d) => d.valor);
      mín = Math.min(...valores);
      máx = Math.max(...valores);
      médio = valores.reduce((a, b) => a + b, 0) / valores.length;
    }
  } catch {
    // Série não encontrada na API
  }

  const valorAtual = dados.length > 0 ? dados[dados.length - 1].valor : 0;
  const interpretacao = config.interpretacao ? config.interpretacao(valorAtual, dados) : { status: "neutro", msg: "" };

  const statusColors = {
    bom: "bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800",
    neutro: "bg-yellow-50 border-yellow-200 dark:bg-yellow-950 dark:border-yellow-800",
    ruim: "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800",
  };

  const statusTextColors = {
    bom: "text-green-900 dark:text-green-200",
    neutro: "text-yellow-900 dark:text-yellow-200",
    ruim: "text-red-900 dark:text-red-200",
  };

  const statusBadgeColors = {
    bom: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    neutro: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    ruim: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link href="/economia" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Voltar à Economia
      </Link>

      <h1 className="mt-4 text-3xl font-semibold tracking-tight">{config.nome}</h1>

      <div className="mt-6 rounded-xl border border-neutral-200 bg-neutral-50 p-6 dark:border-neutral-800 dark:bg-neutral-900">
        <h2 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">O que significa</h2>
        <p className="mt-2 leading-relaxed text-neutral-600 dark:text-neutral-400">{config.explicacao}</p>
      </div>

      {dados.length > 0 && (
        <>
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
              <p className="text-xs text-neutral-500">Valor mais recente</p>
              <p className="mt-1 text-2xl font-bold">
                {valorAtual.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}
                <span className="text-sm text-neutral-500 ml-1">{config.unidade}</span>
              </p>
            </div>
            <div className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
              <p className="text-xs text-neutral-500">Mínimo histórico</p>
              <p className="mt-1 text-2xl font-bold">
                {mín.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}
              </p>
            </div>
            <div className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
              <p className="text-xs text-neutral-500">Máximo histórico</p>
              <p className="mt-1 text-2xl font-bold">
                {máx.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>

          <div className={`mt-8 rounded-xl border p-6 ${statusColors[interpretacao.status]}`}>
            <div className="flex items-start gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${statusBadgeColors[interpretacao.status]}`}>
                    {interpretacao.status === "bom" ? "✓ Bom" : interpretacao.status === "ruim" ? "✗ Ruim" : "~ Neutro"}
                  </span>
                </div>
                <p className={`text-sm leading-relaxed ${statusTextColors[interpretacao.status]}`}>
                  {interpretacao.msg}
                </p>
              </div>
            </div>
            {config.intervalo && (
              <div className="mt-4 pt-4 border-t border-current border-opacity-20">
                <p className="text-xs opacity-75">{config.intervalo.label}</p>
              </div>
            )}
          </div>

          <div className="mt-8 rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
            <h2 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Série histórica (últimos 10 anos)</h2>
            <SerieLineChart pontos={dados} unidade={config.unidade} />
          </div>
        </>
      )}

      {dados.length === 0 && (
        <div className="mt-8 rounded-xl border border-neutral-200 p-8 text-center dark:border-neutral-800">
          <p className="text-neutral-500">Sem dados disponíveis para este indicador.</p>
        </div>
      )}
    </div>
  );
}
