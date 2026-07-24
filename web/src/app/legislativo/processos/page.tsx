import Link from "next/link";
import { listarProcessosSenado } from "@/lib/api";

type Params = { tramitando?: string };

function formatarData(iso: string | null) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("pt-BR");
}

export default async function ProcessosSenadoPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const { tramitando } = await searchParams;

  const processos = await listarProcessosSenado({ tramitando, limit: 100 });

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <Link href="/legislativo" className="text-neutral-500 hover:text-blue-600">
          Votações
        </Link>
        <span className="text-neutral-300 dark:text-neutral-700">/</span>
        <span className="font-medium">Matérias em tramitação</span>
      </div>

      <h1 className="mt-2 text-2xl font-semibold tracking-tight">Legislativo — Matérias no Senado</h1>
      <p className="mt-1 text-neutral-500">
        Status de tramitação de proposições no Senado, independente de quem é o autor.
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href="/legislativo/processos"
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            !tramitando
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Todas
        </Link>
        <Link
          href="/legislativo/processos?tramitando=Sim"
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            tramitando === "Sim"
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Em tramitação
        </Link>
        <Link
          href="/legislativo/processos?tramitando=Não"
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            tramitando === "Não"
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Encerradas
        </Link>
      </div>

      <ul className="mt-6 divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
        {processos.map((p) => (
          <li key={p.id} className="px-4 py-3">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <a
                  href={p.urlDocumento ?? undefined}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-blue-600 hover:underline dark:text-blue-400"
                >
                  {p.identificacao}
                </a>
                {p.ementa && <p className="mt-1 line-clamp-2 text-sm text-neutral-500">{p.ementa}</p>}
                <p className="mt-1 text-xs text-neutral-400">
                  {p.tipoDocumento} · {p.autoria ?? "autoria não informada"} · apresentado em{" "}
                  {formatarData(p.dataApresentacao) ?? "data não informada"}
                </p>
              </div>
              <div className="shrink-0 text-right">
                <span
                  className={`inline-block rounded-full px-2.5 py-1 text-xs font-medium ${
                    p.tramitando === "Sim"
                      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                      : "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300"
                  }`}
                >
                  {p.tramitando === "Sim" ? "Em tramitação" : "Encerrada"}
                </span>
                {p.situacaoAtual && (
                  <p className="mt-1 max-w-[16rem] text-xs text-neutral-500">{p.situacaoAtual.toLowerCase()}</p>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>

      {processos.length === 0 && (
        <p className="mt-10 text-center text-neutral-500">Nenhuma matéria encontrada nesse filtro.</p>
      )}
    </div>
  );
}
