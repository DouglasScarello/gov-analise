import Link from "next/link";
import type { PoliticoMunicipal } from "@/lib/api";

function iniciais(nome: string) {
  const partes = nome.trim().split(/\s+/);
  return ((partes[0]?.[0] ?? "") + (partes[1]?.[0] ?? "")).toUpperCase();
}

const CARGO_LABEL: Record<string, string> = {
  PREFEITO: "Prefeito(a)",
  "VICE-PREFEITO": "Vice-prefeito(a)",
  VEREADOR: "Vereador(a)",
};

export default function PoliticoMunicipalCard({ pessoa }: { pessoa: PoliticoMunicipal }) {
  return (
    <Link
      href={`/politico-municipal/${pessoa.SQ_CANDIDATO}`}
      className="flex items-center gap-4 rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-400 hover:shadow-md dark:border-neutral-800 dark:bg-neutral-900"
    >
      <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-neutral-200 text-lg font-semibold text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
        {iniciais(pessoa.NM_URNA_CANDIDATO || pessoa.NM_CANDIDATO)}
      </div>
      <div className="min-w-0">
        <p className="truncate font-medium text-neutral-900 dark:text-neutral-100">
          {pessoa.NM_URNA_CANDIDATO || pessoa.NM_CANDIDATO}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
            {CARGO_LABEL[pessoa.DS_CARGO] ?? pessoa.DS_CARGO}
          </span>
          {pessoa.SG_PARTIDO && (
            <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-950 dark:text-blue-300">
              {pessoa.SG_PARTIDO}
            </span>
          )}
        </div>
        <p className="mt-1 truncate text-xs text-neutral-500">
          {pessoa.NM_UE} · {pessoa.SG_UF}
        </p>
      </div>
    </Link>
  );
}
