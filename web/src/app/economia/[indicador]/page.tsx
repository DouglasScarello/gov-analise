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
  },
  ipca_variacao_mensal: {
    nome: "IPCA (variação mensal)",
    unidade: "%",
    explicacao: `Índice de Preços ao Consumidor Amplo. Mede a variação mensal de preços que você paga na vida cotidiana (alimento, gasolina, aluguel, etc). Acima de zero significa inflação (tudo fica mais caro).`,
  },
  ipca_acumulado_12_meses: {
    nome: "IPCA (acumulado 12 meses)",
    unidade: "%",
    explicacao: `Acumulação da inflação nos últimos 12 meses. Mostra quanto seus gastos aumentaram no período de um ano. É a métrica de inflação que mais você percebe no dia a dia.`,
  },
  igpm_variacao_mensal: {
    nome: "IGP-M (variação mensal)",
    unidade: "%",
    explicacao: `Índice Geral de Preços do Mercado. Mede inflação com foco em atacado e matérias-primas (afeta mais empresas e indústria). É usado para reajustes de aluguel e contratos.`,
  },
  dolar_ptax_venda: {
    nome: "Dólar (PTAX venda)",
    unidade: "R$",
    explicacao: `Cotação do dólar americano em reais. Sobe quando Real enfraquece (importações ficam caras, exportações ganham competitividade). Cai quando Real fortalece.`,
  },
  dolar_ptax_compra: {
    nome: "Dólar (PTAX compra)",
    unidade: "R$",
    explicacao: `Cotação de compra do dólar. Similar ao de venda, mas é o preço que os bancos pagam por dólares. A diferença entre compra e venda é o spread dos bancos.`,
  },
  taxa_desocupacao_pnad: {
    nome: "Taxa de desocupação (PNAD)",
    unidade: "%",
    explicacao: `Percentual de pessoas que querem trabalhar mas não têm emprego. Medida mensal pela PNAD Contínua do IBGE. Acima de 10% indica mercado de trabalho tenso.`,
  },
  ibc_br: {
    nome: "IBC-Br (Atividade Econômica)",
    unidade: "",
    explicacao: `Índice de Atividade Econômica do Banco Central. É um proxy do PIB mensal que mostra se a economia está acelerando ou desacelerando. Sobe = economia crescendo, cai = economia contraindo.`,
  },
  balanca_comercial_saldo: {
    nome: "Balança Comercial (saldo)",
    unidade: "US$ bilhões",
    explicacao: `Diferença entre exportações e importações em dólares. Positivo = exportamos mais (bom para o câmbio). Negativo = importamos mais (gasto de dólar).`,
  },
  reservas_internacionais: {
    nome: "Reservas Internacionais",
    unidade: "US$ bilhões",
    explicacao: `Dólares e outros ativos que o Brasil tem guardados. Usados para proteger o câmbio em crises. Reservas altas dão segurança econômica, reservas baixas indicam stress.`,
  },
  divida_liquida_setor_publico_pct_pib: {
    nome: "Dívida Líquida (% do PIB)",
    unidade: "% do PIB",
    explicacao: `Quanto o governo deve, em proporção do que o país produz em um ano. Acima de 60% é considerado alto. Sobe quando governo gasta mais que arrecada.`,
  },
  pib_uf: {
    nome: "PIB por estado",
    unidade: "",
    explicacao: `Produto Interno Bruto estadual. Mede o valor total de tudo que é produzido em cada estado. Cresce = economia estadual em expansão. Cai = economia estadual retraindo.`,
  },
  populacao_estimada_uf: {
    nome: "População estimada",
    unidade: "",
    explicacao: `Número de habitantes por estado, atualizado anualmente pelo IBGE. Usado para calcular PIB per capita e entender crescimento demográfico.`,
  },
  taxa_desocupacao_uf: {
    nome: "Taxa de desocupação por estado",
    unidade: "%",
    explicacao: `Desemprego em cada estado. Varia bastante por região — algumas têm mercado de trabalho mais dinâmico que outras.`,
  },
  rendimento_medio_uf: {
    nome: "Rendimento médio por estado",
    unidade: "R$",
    explicacao: `Salário médio em cada estado (ajustado pela inflação). Varia muito entre regiões — São Paulo e Distrito Federal têm rendimentos maiores que nordeste.`,
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
                {dados[0].valor.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}
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
