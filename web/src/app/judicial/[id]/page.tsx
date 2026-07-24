import Link from "next/link";
import { notFound } from "next/navigation";
import { obterProcessoJudicial } from "@/lib/api";

function formatarData(iso: string | null) {
  if (!iso) return "data não informada";
  return new Date(iso).toLocaleDateString("pt-BR");
}

const EXPLICACAO_GRAU: Record<string, string> = {
  G1: "1º grau — a instância inicial, onde o processo começa e é julgado pela primeira vez.",
  G2: "2º grau — instância de recurso (tribunal), que revisa decisões tomadas no 1º grau.",
  JE: "Juizado Especial — instância para causas de menor complexidade, com rito mais simples e rápido.",
};

export default async function ProcessoJudicialDetalhePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let processo;
  try {
    processo = await obterProcessoJudicial(id);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link href="/judicial" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Todos os processos
      </Link>

      <h1 className="mt-4 text-2xl font-semibold tracking-tight">{processo.numeroProcesso}</h1>
      <p className="mt-1 text-neutral-500">
        {processo.tribunal}
        {processo.grau ? ` · ${processo.grau}` : ""}
      </p>

      <div className="mt-6 rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700 dark:border-neutral-800 dark:bg-neutral-900/50 dark:text-neutral-300">
        <p className="font-medium">O que é este processo?</p>
        <p className="mt-1">
          Classe processual <strong>{processo.classeNome ?? "não informada"}</strong>, tramitando em{" "}
          {processo.orgaoJulgadorNome ?? "órgão não informado"}.
          {processo.grau && EXPLICACAO_GRAU[processo.grau]
            ? ` ${EXPLICACAO_GRAU[processo.grau]}`
            : ""}
        </p>
      </div>

      <dl className="mt-6 grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-neutral-500">Tribunal</dt>
          <dd className="font-medium">{processo.tribunal}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Órgão julgador</dt>
          <dd className="font-medium">{processo.orgaoJulgadorNome ?? "não informado"}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Ajuizado em</dt>
          <dd className="font-medium">{formatarData(processo.dataAjuizamento)}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Última atualização</dt>
          <dd className="font-medium">{formatarData(processo.dataUltimaAtualizacao)}</dd>
        </div>
      </dl>

      <p className="mt-8 text-xs text-neutral-500 dark:text-neutral-400">
        Dados públicos do CNJ DataJud. Por padrão, o DataJud não expõe os nomes das partes
        envolvidas nem o inteiro teor do processo — para consultar esses detalhes, use o número do
        processo acima no site oficial do tribunal ({processo.tribunal}).
      </p>
    </div>
  );
}
