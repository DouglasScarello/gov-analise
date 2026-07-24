import Link from "next/link";
import type { VotacaoSenado } from "@/lib/api";

function formatarData(iso: string | null) {
  if (!iso) return "data não informada";
  const [ano, mes, dia] = iso.split("T")[0].split("-");
  return `${dia}/${mes}/${ano}`;
}

const RESULTADO_COR: Record<string, string> = {
  Aprovado: "border-emerald-300 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-400",
  Rejeitado: "border-red-300 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-400",
};

export default function VotacaoItem({ votacao }: { votacao: VotacaoSenado }) {
  const qs = new URLSearchParams({
    dataSessao: votacao.dataSessao ?? "",
    materiaSigla: votacao.materiaSigla ?? "",
    materiaNumero: votacao.materiaNumero ?? "",
    materiaAno: votacao.materiaAno ?? "",
    descricaoVotacao: votacao.descricaoVotacao,
  });

  return (
    <li>
      <Link
        href={`/legislativo/votacao?${qs.toString()}`}
        target="_blank"
        rel="noopener noreferrer"
        className="block px-4 py-3 hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium">{votacao.descricaoVotacao}</p>
            {votacao.materiaEmenta && (
              <p className="mt-1 line-clamp-2 text-sm text-neutral-500">{votacao.materiaEmenta}</p>
            )}
            <p className="mt-1 text-xs text-neutral-500">
              {votacao.senadorNome} · {votacao.senadorPartido}/{votacao.senadorUf} · voto:{" "}
              {votacao.voto} · {formatarData(votacao.dataSessao)}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <span
              className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
                RESULTADO_COR[votacao.descricaoResultado] ?? "border-neutral-300 dark:border-neutral-700"
              }`}
            >
              {votacao.descricaoResultado}
            </span>
            <span className="text-neutral-500 dark:text-neutral-400">↗</span>
          </div>
        </div>
      </Link>
    </li>
  );
}
