import Link from "next/link";
import { listarProcessosJudiciais, listarTribunaisDisponiveis } from "@/lib/api";

const POR_PAGINA = 30;

type Params = {
  tribunal?: string;
  pagina?: string;
};

function formatarData(iso: string | null) {
  if (!iso) return "data não informada";
  return new Date(iso).toLocaleDateString("pt-BR");
}

function construirLink(tribunal: string | undefined, novaPagina: number) {
  const qs = new URLSearchParams();
  if (tribunal) qs.set("tribunal", tribunal);
  qs.set("pagina", String(novaPagina));
  return `/judicial?${qs.toString()}`;
}

export default async function JudicialPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  const { tribunal } = sp;
  const paginaAtual = Math.max(1, Number(sp.pagina) || 1);
  const offset = (paginaAtual - 1) * POR_PAGINA;

  const [pagina, tribunais] = await Promise.all([
    listarProcessosJudiciais({ tribunal, limit: POR_PAGINA, offset }),
    listarTribunaisDisponiveis(),
  ]);
  const processos = pagina.items;
  const temProximaPagina = offset + processos.length < pagina.total;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Judiciário — Processos</h1>
      <p className="mt-1 text-neutral-500">
        Amostra recente de processos (CNJ DataJud), ordenada pela última movimentação, em um
        conjunto representativo de tribunais.
      </p>
      <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400">
        O DataJud cobre dezenas de milhões de processos por tribunal — esta página mostra uma
        amostra recente, não o acervo completo.
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href="/judicial"
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            !tribunal
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Todos os tribunais
        </Link>
        {tribunais.map((t) => (
          <Link
            key={t.tribunal}
            href={`/judicial?tribunal=${t.tribunal}`}
            className={`rounded-full border px-3 py-1 text-sm ${
              tribunal === t.tribunal
                ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {t.tribunal} ({t.total})
          </Link>
        ))}
      </div>

      <ul className="mt-6 divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
        {processos.map((p) => (
          <li key={p.id}>
            <Link
              href={`/judicial/${encodeURIComponent(p.id)}`}
              className="block px-4 py-3 hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium">{p.numeroProcesso}</p>
                  <p className="mt-1 text-sm text-neutral-500">
                    {p.classeNome} · {p.orgaoJulgadorNome}
                  </p>
                  <p className="mt-1 text-xs text-neutral-500">
                    Ajuizado em {formatarData(p.dataAjuizamento)} · última atualização em{" "}
                    {formatarData(p.dataUltimaAtualizacao)}
                  </p>
                </div>
                <span className="shrink-0 rounded-full border border-neutral-300 px-2.5 py-1 text-xs font-medium dark:border-neutral-700">
                  {p.tribunal}
                </span>
              </div>
            </Link>
          </li>
        ))}
      </ul>

      {processos.length === 0 && (
        <p className="mt-10 text-center text-neutral-500">Nenhum resultado nesse filtro.</p>
      )}

      <div className="mt-8 flex items-center justify-between">
        {paginaAtual > 1 ? (
          <Link
            href={construirLink(tribunal, paginaAtual - 1)}
            className="rounded-full border border-neutral-300 px-4 py-2 text-sm hover:border-blue-500 dark:border-neutral-700"
          >
            ← Anterior
          </Link>
        ) : (
          <span />
        )}
        <span className="text-sm text-neutral-500">
          Página {paginaAtual}
          {pagina.total > 0 && ` de ${Math.ceil(pagina.total / POR_PAGINA)} (${pagina.total} resultados)`}
        </span>
        {temProximaPagina ? (
          <Link
            href={construirLink(tribunal, paginaAtual + 1)}
            className="rounded-full border border-neutral-300 px-4 py-2 text-sm hover:border-blue-500 dark:border-neutral-700"
          >
            Próxima →
          </Link>
        ) : (
          <span />
        )}
      </div>
    </div>
  );
}
