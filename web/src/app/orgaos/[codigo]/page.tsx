import Link from "next/link";
import { notFound } from "next/navigation";
import { obterOrgao } from "@/lib/api";

function formatarData(iso: string | null) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("pt-BR");
}

function formatarMoeda(valor: number | null) {
  if (valor == null) return "valor não informado";
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default async function OrgaoPage({
  params,
}: {
  params: Promise<{ codigo: string }>;
}) {
  const { codigo } = await params;

  let orgao;
  try {
    orgao = await obterOrgao(codigo);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link href="/orgaos" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Todos os órgãos
      </Link>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight">{orgao.descricao}</h1>
      <p className="mt-1 text-neutral-500">Código SIAFI {orgao.codigo}</p>

      <section className="mt-8">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Contratos vinculados ao nome
        </h2>
        {orgao.contratosVinculados.length === 0 ? (
          <p className="text-sm text-neutral-500">Nenhum contrato encontrado com esse nome.</p>
        ) : (
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {orgao.contratosVinculados.map((c, i) => (
              <li key={i} className="px-4 py-3">
                <p className="font-medium">{c.orgaoNome}</p>
                <p className="text-sm text-neutral-500 line-clamp-2">{c.objeto}</p>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  {formatarMoeda(c.valor)} · {formatarData(c.data)}
                </p>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400">
          Cruzamento por nome — o SIAFI não compartilha código com as demais fontes, então pode não
          encontrar nada mesmo quando existe contrato vinculado.
        </p>
      </section>

      <section className="mt-8">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Sanções vinculadas ao nome
        </h2>
        {orgao.sancoesVinculadas.length === 0 ? (
          <p className="text-sm text-neutral-500">Nenhuma sanção encontrada com esse nome.</p>
        ) : (
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {orgao.sancoesVinculadas.map((s) => (
              <li key={s.id} className="px-4 py-3">
                <p className="font-medium">{s.sancionadoNome}</p>
                <p className="text-sm text-neutral-500">
                  {s.tipoSancao} · {s.origemSancao} · {formatarData(s.dataInicioSancao)}
                </p>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400">Cruzamento por nome — pode incluir homônimos.</p>
      </section>
    </div>
  );
}
