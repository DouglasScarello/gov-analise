import Link from "next/link";
import { notFound } from "next/navigation";
import { obterDetalheVotacaoSenado } from "@/lib/api";

type Params = {
  dataSessao?: string;
  materiaSigla?: string;
  materiaNumero?: string;
  materiaAno?: string;
  descricaoVotacao?: string;
};

function formatarData(iso: string | null) {
  if (!iso) return "data não informada";
  const [ano, mes, dia] = iso.split("T")[0].split("-");
  return `${dia}/${mes}/${ano}`;
}

const RESULTADO_COR: Record<string, string> = {
  Aprovado: "border-emerald-300 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-400",
  Rejeitado: "border-red-300 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-400",
};

export default async function VotacaoDetalhePage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  if (!sp.dataSessao || !sp.materiaSigla || !sp.materiaNumero || !sp.materiaAno || !sp.descricaoVotacao) {
    notFound();
  }

  let detalhe;
  try {
    detalhe = await obterDetalheVotacaoSenado({
      dataSessao: sp.dataSessao,
      materiaSigla: sp.materiaSigla,
      materiaNumero: sp.materiaNumero,
      materiaAno: sp.materiaAno,
      descricaoVotacao: sp.descricaoVotacao,
    });
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link href="/legislativo" className="text-sm text-blue-600 hover:underline dark:text-blue-400">
        ← Voltar para Legislativo
      </Link>

      <div className="mt-4 flex items-start justify-between gap-4">
        <h1 className="text-xl font-semibold tracking-tight">{detalhe.descricaoVotacao}</h1>
        <span
          className={`shrink-0 rounded-full border px-3 py-1 text-sm font-medium ${
            RESULTADO_COR[detalhe.descricaoResultado] ?? "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          {detalhe.descricaoResultado}
        </span>
      </div>

      <p className="mt-2 text-sm text-neutral-500">
        {detalhe.materiaSigla} {detalhe.materiaNumero}/{detalhe.materiaAno} · {formatarData(detalhe.dataSessao)} ·{" "}
        {detalhe.votacaoSecreta === "Sim" ? "votação secreta" : "votação aberta"}
      </p>

      {detalhe.materiaEmenta && (
        <p className="mt-4 rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700 dark:border-neutral-800 dark:bg-neutral-900/50 dark:text-neutral-300">
          {detalhe.materiaEmenta}
        </p>
      )}

      <div className="mt-6 flex flex-wrap gap-2">
        {Object.entries(detalhe.contagemVotos).map(([voto, total]) => (
          <span
            key={voto}
            className="rounded-full border border-neutral-300 px-3 py-1 text-sm dark:border-neutral-700"
          >
            {voto}: {total}
          </span>
        ))}
      </div>

      <h2 className="mt-8 mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
        Voto de cada senador ({detalhe.votos.length})
      </h2>
      <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
        {detalhe.votos.map((v, i) => (
          <li key={i} className="flex items-center justify-between px-4 py-2.5 text-sm">
            <span>
              {v.senadorNome} <span className="text-neutral-400">({v.senadorPartido}/{v.senadorUf})</span>
            </span>
            <span className="shrink-0 font-medium text-neutral-600 dark:text-neutral-400">{v.voto}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
