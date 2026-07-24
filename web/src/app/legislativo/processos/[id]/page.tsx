import Link from "next/link";
import { notFound } from "next/navigation";
import { obterProcessoSenado } from "@/lib/api";

function formatarData(iso: string | null) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("pt-BR");
}

export default async function ProcessoSenadoDetalhePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let processo;
  try {
    processo = await obterProcessoSenado(id);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link href="/legislativo/processos" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Todas as matérias
      </Link>

      <div className="mt-4 flex items-start justify-between gap-4">
        <h1 className="text-xl font-semibold tracking-tight">{processo.identificacao}</h1>
        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${
            processo.tramitando === "Sim"
              ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
              : "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300"
          }`}
        >
          {processo.tramitando === "Sim" ? "Em tramitação" : "Encerrada"}
        </span>
      </div>
      <p className="mt-1 text-sm text-neutral-500">
        {processo.tipoDocumento ?? "Matéria legislativa"} · {processo.autoria ?? "autoria não informada"}
      </p>

      {processo.ementa && (
        <div className="mt-6 rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700 dark:border-neutral-800 dark:bg-neutral-900/50 dark:text-neutral-300">
          <p className="font-medium">Do que trata</p>
          <p className="mt-1">{processo.ementa}</p>
        </div>
      )}

      <dl className="mt-6 grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-neutral-500">Situação atual</dt>
          <dd className="font-medium">{processo.situacaoAtual ?? "não informada"}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Desde</dt>
          <dd className="font-medium">{formatarData(processo.dataSituacaoAtual) ?? "não informada"}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Apresentada em</dt>
          <dd className="font-medium">{formatarData(processo.dataApresentacao) ?? "não informada"}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Última atualização</dt>
          <dd className="font-medium">{formatarData(processo.dataUltimaAtualizacao) ?? "não informada"}</dd>
        </div>
      </dl>

      {processo.urlDocumento && (
        <a
          href={processo.urlDocumento}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-6 inline-block rounded-full border border-neutral-300 px-4 py-2 text-sm hover:border-blue-500 hover:text-blue-600 dark:border-neutral-700"
        >
          Ver documento completo no Senado ↗
        </a>
      )}
    </div>
  );
}
