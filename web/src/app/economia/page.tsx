import Link from "next/link";
import SerieLineChart from "@/components/charts/SerieLineChart";
import StatTile from "@/components/charts/StatTile";
import UfBarChart from "@/components/charts/UfBarChart";
import { listarIndicadoresUf, listarSeriesEconomicas } from "@/lib/api";
import { SIGLA_POR_ESTADO } from "@/lib/estados";

// Revalidate a cada 0 segundos (SSR dinâmico, sem cache)
export const revalidate = 0;

const SERIES_CONFIG = [
  { chave: "selic_meta", titulo: "Selic", unidade: "% a.a.", seção: "Contas Públicas", semântica: "neutro" as const },
  { chave: "ipca_variacao_mensal", titulo: "IPCA (mensal)", unidade: "%", seção: "Preços", semântica: "melhor_queda" as const },
  { chave: "ipca_acumulado_12_meses", titulo: "IPCA (acumulado 12m)", unidade: "%", seção: "Preços", semântica: "melhor_queda" as const },
  { chave: "igpm_variacao_mensal", titulo: "IGP-M (mensal)", unidade: "%", seção: "Preços", semântica: "melhor_queda" as const },
  { chave: "dolar_ptax_venda", titulo: "Dólar (venda)", unidade: "R$", seção: "Câmbio", semântica: "neutro" as const },
  { chave: "dolar_ptax_compra", titulo: "Dólar (compra)", unidade: "R$", seção: "Câmbio", semântica: "neutro" as const },
  { chave: "taxa_desocupacao_pnad", titulo: "Desocupação (PNAD)", unidade: "%", seção: "Mercado de Trabalho", semântica: "melhor_queda" as const },
  { chave: "ibc_br", titulo: "IBC-Br (atividade)", unidade: "", seção: "Atividade Econômica", semântica: "melhor_alta" as const },
  { chave: "balanca_comercial_saldo", titulo: "Balança Comercial", unidade: "US$ bi", seção: "Câmbio", semântica: "melhor_alta" as const },
  { chave: "reservas_internacionais", titulo: "Reservas (US$)", unidade: "US$ bi", seção: "Câmbio", semântica: "melhor_alta" as const },
  { chave: "divida_liquida_setor_publico_pct_pib", titulo: "Dívida Líquida", unidade: "% PIB", seção: "Contas Públicas", semântica: "melhor_queda" as const },
] as const;

const INDICADORES_UF = [
  { chave: "pib_uf", titulo: "PIB por estado", unidade: "" },
  { chave: "populacao_estimada_uf", titulo: "População", unidade: "" },
] as const;

const SECOES = ["Preços", "Atividade Econômica", "Mercado de Trabalho", "Câmbio", "Contas Públicas"] as const;

export default async function EconomiaPage() {
  const [seriesRaw, indicadoresRaw] = await Promise.all([
    Promise.all(SERIES_CONFIG.map((s) => listarSeriesEconomicas(s.chave))),
    Promise.all(INDICADORES_UF.map((i) => listarIndicadoresUf(i.chave))),
  ]);

  const series = SERIES_CONFIG.map((config, i) => {
    const raw = seriesRaw[i] || [];
    const reversed = [...raw].reverse();
    const pontos = reversed.map((p: any) => ({ data: p.data, valor: p.valor }));

    return {
      chave: config.chave,
      titulo: config.titulo,
      unidade: config.unidade,
      semântica: config.semântica,
      seção: config.seção,
      pontos,
    };
  });

  const indicadores = indicadoresRaw.map((raw, i) => ({ ...INDICADORES_UF[i], registros: raw }));

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-3xl font-semibold tracking-tight">Economia</h1>
      <p className="mt-2 text-neutral-500">
        Indicadores macroeconômicos do Brasil — compare períodos e veja crescimento ou queda mês a mês e ano a ano.
      </p>

      {/* KPIs principais */}
      <div className="mt-8">
        <h2 className="text-lg font-medium">Indicadores chave</h2>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {series.slice(0, 8).map((s) => (
            <Link key={s.chave} href={`/economia/${s.chave}`} className="hover:opacity-80 transition-opacity">
              <StatTile
                titulo={s.titulo}
                valor={s.pontos[s.pontos.length - 1]?.valor}
                unidade={s.unidade}
                pontos={s.pontos}
                semântica={s.semântica}
              />
            </Link>
          ))}
        </div>
      </div>

      {/* Seções temáticas */}
      {SECOES.map((seção) => {
        const indicadoresNaSeção = series.filter((s) => s.seção === seção);
        if (indicadoresNaSeção.length === 0) return null;
        return (
          <section key={seção} className="mt-10">
            <h2 className="text-xl font-semibold">{seção}</h2>
            <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
              {indicadoresNaSeção.map((s) => (
                <Link key={s.chave} href={`/economia/${s.chave}`} className="block hover:opacity-80 transition-opacity">
                  <div className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800 h-full cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-900">
                    <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{s.titulo}</h3>
                    <SerieLineChart pontos={s.pontos} unidade={s.unidade} />
                  </div>
                </Link>
              ))}
            </div>
          </section>
        );
      })}

      {/* Indicadores por estado */}
      <section className="mt-10">
        <h2 className="text-xl font-semibold">Indicadores por estado</h2>
        <div className="mt-4 grid grid-cols-1 gap-4">
          {indicadores.map((ind) => {
            const registros = ind.registros || [];
            const ultimoPeriodo = registros.reduce(
              (max: any, r: any) => (r.periodo > max ? r.periodo : max),
              registros[0]?.periodo ?? 0
            );
            const itens = registros
              .filter((r: any) => r.periodo === ultimoPeriodo)
              .sort((a: any, b: any) => b.valor - a.valor)
              .map((r: any) => ({ uf: SIGLA_POR_ESTADO[r.localidadeNome] ?? r.localidadeNome, valor: r.valor }));

            return (
              <div key={ind.chave} className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
                <div className="flex items-baseline justify-between">
                  <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">{ind.titulo}</h3>
                  {ultimoPeriodo && <span className="text-xs text-neutral-500">Período: {ultimoPeriodo}</span>}
                </div>
                <UfBarChart itens={itens} unidade={ind.unidade} />
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
