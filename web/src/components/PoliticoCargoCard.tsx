import Image from "next/image";
import Link from "next/link";
import type { PoliticoCargo } from "@/lib/api";

const CARGO_LABEL: Record<string, string> = {
  "DEPUTADO FEDERAL": "Deputado(a) Federal",
  SENADOR: "Senador(a)",
  PRESIDENTE: "Presidente",
  "VICE-PRESIDENTE": "Vice-presidente",
  GOVERNADOR: "Governador(a)",
  "VICE-GOVERNADOR": "Vice-governador(a)",
  "DEPUTADO ESTADUAL": "Deputado(a) Estadual",
  "DEPUTADO DISTRITAL": "Deputado(a) Distrital",
  PREFEITO: "Prefeito(a)",
  "VICE-PREFEITO": "Vice-prefeito(a)",
  VEREADOR: "Vereador(a)",
};

function iniciais(nome: string) {
  const partes = nome.trim().split(/\s+/);
  return ((partes[0]?.[0] ?? "") + (partes[1]?.[0] ?? "")).toUpperCase();
}

export default function PoliticoCargoCard({ pessoa }: { pessoa: PoliticoCargo }) {
  const nomeExibicao = pessoa.nome_urna || pessoa.nome;

  return (
    <Link
      href={`/politico/${pessoa.nivel}/${encodeURIComponent(pessoa.id)}`}
      className="flex items-center gap-4 rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-400 hover:shadow-md dark:border-neutral-800 dark:bg-neutral-900"
    >
      {pessoa.foto ? (
        <Image
          src={pessoa.foto}
          alt={nomeExibicao}
          width={64}
          height={64}
          unoptimized
          className="h-16 w-16 shrink-0 rounded-full object-cover ring-2 ring-neutral-100 dark:ring-neutral-800"
        />
      ) : (
        <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-neutral-200 text-lg font-semibold text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
          {iniciais(nomeExibicao)}
        </div>
      )}
      <div className="min-w-0">
        <p className="truncate font-medium text-neutral-900 dark:text-neutral-100">
          {nomeExibicao}
        </p>
        <div className="mt-1 flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
            {CARGO_LABEL[pessoa.cargo] ?? pessoa.cargo}
          </span>
          {pessoa.partido && (
            <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-950 dark:text-blue-300">
              {pessoa.partido}
            </span>
          )}
          {pessoa.ano && (
            <span className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs font-semibold text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
              {pessoa.ano}
            </span>
          )}
        </div>
        <p className="mt-1 truncate text-xs text-neutral-500">
          {[pessoa.municipio, pessoa.uf].filter(Boolean).join(" · ")}
        </p>
      </div>
    </Link>
  );
}
