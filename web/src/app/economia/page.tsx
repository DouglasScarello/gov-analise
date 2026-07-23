import SerieLineChart from "@/components/charts/SerieLineChart";
import UfBarChart from "@/components/charts/UfBarChart";
import { listarIndicadoresUf, listarSeriesEconomicas } from "@/lib/api";
import { SIGLA_POR_ESTADO } from "@/lib/estados";

const SERIES = [
  { chave: "selic_meta", titulo: "Selic (meta)", unidade: "% a.a." },
  { chave: "ipca_variacao_mensal", titulo: "IPCA (variação mensal)", unidade: "%" },
  { chave: "igpm_variacao_mensal", titulo: "IGP-M (variação mensal)", unidade: "%" },
  { chave: "dolar_ptax_venda", titulo: "Dólar (PTAX venda)", unidade: " R$" },
  { chave: "taxa_desocupacao_pnad", titulo: "Taxa de desocupação (PNAD)", unidade: "%" },
  {
    chave: "divida_liquida_setor_publico_pct_pib",
    titulo: "Dívida líquida do setor público",
    unidade: "% do PIB",
  },
] as const;

const INDICADORES_UF = [
  { chave: "pib_uf", titulo: "PIB por estado", unidade: "" },
  { chave: "populacao_estimada_uf", titulo: "População estimada por estado", unidade: "" },
] as const;

export default async function EconomiaPage() {
  const [series, indicadores] = await Promise.all([
    Promise.all(SERIES.map((s) => listarSeriesEconomicas(s.chave))),
    Promise.all(INDICADORES_UF.map((i) => listarIndicadoresUf(i.chave))),
  ]);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Economia</h1>
      <p className="mt-1 text-neutral-500">
        Séries históricas do Banco Central (últimos 10 anos) e indicadores socioeconômicos do IBGE por estado.
      </p>

      <h2 className="mt-8 text-lg font-medium">Indicadores macroeconômicos</h2>
      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
        {SERIES.map((s, i) => {
          const pontos = [...series[i]].reverse().map((p) => ({ data: p.data, valor: p.valor }));
          return (
            <div
              key={s.chave}
              className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800"
            >
              <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{s.titulo}</h3>
              <SerieLineChart pontos={pontos} unidade={s.unidade} />
            </div>
          );
        })}
      </div>

      <h2 className="mt-10 text-lg font-medium">Indicadores por estado</h2>
      <div className="mt-4 grid grid-cols-1 gap-4">
        {INDICADORES_UF.map((ind, i) => {
          const registros = indicadores[i];
          const ultimoPeriodo = registros.reduce(
            (max, r) => (r.periodo > max ? r.periodo : max),
            registros[0]?.periodo ?? 0
          );
          const itens = registros
            .filter((r) => r.periodo === ultimoPeriodo)
            .sort((a, b) => b.valor - a.valor)
            .map((r) => ({ uf: SIGLA_POR_ESTADO[r.localidadeNome] ?? r.localidadeNome, valor: r.valor }));

          return (
            <div
              key={ind.chave}
              className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800"
            >
              <div className="flex items-baseline justify-between">
                <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{ind.titulo}</h3>
                {ultimoPeriodo && (
                  <span className="text-xs text-neutral-500">Ano de referência: {ultimoPeriodo}</span>
                )}
              </div>
              <UfBarChart itens={itens} unidade={ind.unidade} />
            </div>
          );
        })}
      </div>
    </div>
  );
}
