import Link from "next/link";
import { notFound } from "next/navigation";
import SerieLineChart from "@/components/charts/SerieLineChart";
import { listarBalanco, listarIndicadoresUf } from "@/lib/api";
import { NOME_POR_UF } from "@/lib/estados";

function formatarMoeda(valor: number) {
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
}

const CONTA_TOP_NIVEL = /^P\d\.0\.0\.0\.0\.00\.00$/;

export default async function EstadoPage({ params }: { params: Promise<{ uf: string }> }) {
  const { uf: ufParam } = await params;
  const uf = ufParam.toUpperCase();
  const nomeEstado = NOME_POR_UF[uf];
  if (!nomeEstado) notFound();

  const [pib, populacao, balanco] = await Promise.all([
    listarIndicadoresUf("pib_uf"),
    listarIndicadoresUf("populacao_estimada_uf"),
    listarBalanco(uf, 200),
  ]);

  const pibEstado = pib
    .filter((r) => r.localidadeNome === nomeEstado)
    .sort((a, b) => a.periodo - b.periodo)
    .map((r) => ({ data: String(r.periodo), valor: r.valor }));

  const populacaoEstado = populacao
    .filter((r) => r.localidadeNome === nomeEstado)
    .sort((a, b) => a.periodo - b.periodo)
    .map((r) => ({ data: String(r.periodo), valor: r.valor }));

  const contasPrincipais = balanco.filter((c) => CONTA_TOP_NIVEL.test(c.cod_conta));
  const exercicio = balanco[0]?.exercicio;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Link href="/estados" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Todos os estados
      </Link>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight">
        {nomeEstado} <span className="text-neutral-500">({uf})</span>
      </h1>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
          <h2 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">PIB</h2>
          <SerieLineChart pontos={pibEstado} />
        </div>
        <div className="rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
          <h2 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">População estimada</h2>
          <SerieLineChart pontos={populacaoEstado} />
        </div>
      </div>

      {contasPrincipais.length > 0 && (
        <div className="mt-6 rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
          <div className="flex items-baseline justify-between">
            <h2 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
              Balanço patrimonial (contas principais)
            </h2>
            {exercicio && <span className="text-xs text-neutral-500">Exercício {exercicio}</span>}
          </div>
          <ul className="mt-3 divide-y divide-neutral-200 dark:divide-neutral-800">
            {contasPrincipais.map((c) => (
              <li key={c.cod_conta} className="flex items-center justify-between py-2 text-sm">
                <span>{c.conta.replace(/^P?\d(\.\d+)*\s*-\s*/, "")}</span>
                <span className="font-medium">{formatarMoeda(c.valor)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-6">
        <Link
          href={`/politicos?nivel=estadual&uf=${uf}`}
          className="inline-block rounded-full border border-neutral-300 px-4 py-2 text-sm hover:border-blue-500 dark:border-neutral-700"
        >
          Ver políticos estaduais de {nomeEstado} →
        </Link>
      </div>
    </div>
  );
}
