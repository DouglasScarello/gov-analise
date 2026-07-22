import { notFound } from "next/navigation";
import { obterPoliticoMunicipal } from "@/lib/api";

const CARGO_LABEL: Record<string, string> = {
  PREFEITO: "Prefeito(a)",
  "VICE-PREFEITO": "Vice-prefeito(a)",
  VEREADOR: "Vereador(a)",
};

function iniciais(nome: string) {
  const partes = nome.trim().split(/\s+/);
  return ((partes[0]?.[0] ?? "") + (partes[1]?.[0] ?? "")).toUpperCase();
}

export default async function PoliticoMunicipalPage({
  params,
}: {
  params: Promise<{ sq: string }>;
}) {
  const { sq } = await params;

  let pessoa;
  try {
    pessoa = await obterPoliticoMunicipal(sq);
  } catch {
    notFound();
  }

  const nomeExibicao = pessoa.NM_URNA_CANDIDATO || pessoa.NM_CANDIDATO;

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="flex items-center gap-4">
        <div className="flex h-22 w-22 shrink-0 items-center justify-center rounded-full bg-neutral-200 text-2xl font-semibold text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
          {iniciais(nomeExibicao)}
        </div>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{nomeExibicao}</h1>
          <p className="text-neutral-500">
            {pessoa.SG_PARTIDO} · {pessoa.NM_UE} · {pessoa.SG_UF}
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
          {CARGO_LABEL[pessoa.DS_CARGO] ?? pessoa.DS_CARGO} eleito(a) — {pessoa.DS_SIT_TOT_TURNO.toLowerCase()}
        </span>
      </div>

      <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
        {pessoa.NM_CANDIDATO !== nomeExibicao && (
          <div>
            <dt className="text-neutral-500">Nome completo</dt>
            <dd className="font-medium">{pessoa.NM_CANDIDATO}</dd>
          </div>
        )}
        {pessoa.DS_OCUPACAO && (
          <div>
            <dt className="text-neutral-500">Ocupação declarada</dt>
            <dd className="font-medium">{pessoa.DS_OCUPACAO}</dd>
          </div>
        )}
        {pessoa.DS_GRAU_INSTRUCAO && (
          <div>
            <dt className="text-neutral-500">Escolaridade</dt>
            <dd className="font-medium">{pessoa.DS_GRAU_INSTRUCAO}</dd>
          </div>
        )}
        {pessoa.ANO_ELEICAO && (
          <div>
            <dt className="text-neutral-500">Eleição</dt>
            <dd className="font-medium">{pessoa.ANO_ELEICAO}</dd>
          </div>
        )}
      </dl>

      <section className="mt-8">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Sanções vinculadas ao nome
        </h2>
        {pessoa.sancoesVinculadas.length === 0 ? (
          <p className="text-sm text-neutral-500">Nenhuma sanção encontrada com esse nome.</p>
        ) : (
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {pessoa.sancoesVinculadas.map((s) => (
              <li key={s.id} className="px-4 py-3">
                <p className="font-medium">{s.sancionadoNome}</p>
                <p className="text-sm text-neutral-500">
                  {s.tipoSancao} · {s.origemSancao}
                </p>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-xs text-neutral-400">
          Cruzamento por nome — pode incluir homônimos.
        </p>
      </section>
    </div>
  );
}
