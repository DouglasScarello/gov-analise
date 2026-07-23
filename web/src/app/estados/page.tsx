import Link from "next/link";
import { listarIndicadoresUf } from "@/lib/api";
import { NOME_POR_UF, SIGLA_POR_ESTADO } from "@/lib/estados";

function formatarCompacto(valor: number) {
  return new Intl.NumberFormat("pt-BR", { notation: "compact", maximumFractionDigits: 1 }).format(valor);
}

function ultimoPorEstado(registros: { localidadeNome: string; periodo: number; valor: number }[]) {
  const ultimoPeriodo = registros.reduce((max, r) => (r.periodo > max ? r.periodo : max), registros[0]?.periodo ?? 0);
  const mapa = new Map<string, number>();
  for (const r of registros) {
    if (r.periodo === ultimoPeriodo) {
      mapa.set(SIGLA_POR_ESTADO[r.localidadeNome] ?? r.localidadeNome, r.valor);
    }
  }
  return mapa;
}

export default async function EstadosPage() {
  const [pib, populacao] = await Promise.all([
    listarIndicadoresUf("pib_uf"),
    listarIndicadoresUf("populacao_estimada_uf"),
  ]);

  const pibPorUf = ultimoPorEstado(pib);
  const populacaoPorUf = ultimoPorEstado(populacao);

  const siglas = Object.keys(NOME_POR_UF).sort((a, b) => NOME_POR_UF[a].localeCompare(NOME_POR_UF[b]));

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Estados</h1>
      <p className="mt-1 text-neutral-500">
        Indicadores socioeconômicos, finanças públicas e políticos eleitos por estado.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3">
        {siglas.map((sigla) => (
          <Link
            key={sigla}
            href={`/estados/${sigla}`}
            className="rounded-xl border border-neutral-200 p-4 transition hover:border-blue-500 dark:border-neutral-800"
          >
            <p className="font-medium">
              {NOME_POR_UF[sigla]} <span className="text-neutral-500">({sigla})</span>
            </p>
            <p className="mt-1 text-sm text-neutral-500">
              {populacaoPorUf.has(sigla) && `${formatarCompacto(populacaoPorUf.get(sigla)!)} hab.`}
              {pibPorUf.has(sigla) && ` · PIB ${formatarCompacto(pibPorUf.get(sigla)!)}`}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
