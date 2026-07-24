import Link from "next/link";
import FiltroNome from "@/components/FiltroNome";
import { listarOrgaos } from "@/lib/api";

const POR_PAGINA = 40;

type Params = { nome?: string; pagina?: string };

function construirLink(params: Params, novaPagina: number) {
  const qs = new URLSearchParams();
  if (params.nome) qs.set("nome", params.nome);
  qs.set("pagina", String(novaPagina));
  return `/orgaos?${qs.toString()}`;
}

export default async function OrgaosPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  const { nome } = sp;
  const paginaAtual = Math.max(1, Number(sp.pagina) || 1);
  const offset = (paginaAtual - 1) * POR_PAGINA;

  const pagina = await listarOrgaos({ nome, limit: POR_PAGINA, offset });
  const orgaos = pagina.items;
  const temProximaPagina = offset + orgaos.length < pagina.total;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Órgãos públicos federais</h1>
      <p className="mt-1 text-neutral-500">
        Catálogo SIAFI de órgãos e unidades da administração federal.
      </p>

      <div className="mt-4">
        <FiltroNome action="/orgaos" valorInicial={nome} placeholder="Buscar por nome do órgão..." />
      </div>

      <ul className="mt-6 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {orgaos.map((o) => (
          <li key={o.codigo}>
            <Link
              href={`/orgaos/${o.codigo}`}
              className="block rounded-xl border border-neutral-200 px-4 py-3 text-sm hover:border-blue-400 dark:border-neutral-800"
            >
              <p className="font-medium">{o.descricao}</p>
              <p className="mt-1 text-xs text-neutral-500">Código {o.codigo}</p>
            </Link>
          </li>
        ))}
      </ul>

      {orgaos.length === 0 && (
        <p className="mt-10 text-center text-neutral-500">Nenhum resultado nesse filtro.</p>
      )}

      <div className="mt-8 flex items-center justify-between">
        {paginaAtual > 1 ? (
          <Link
            href={construirLink({ nome }, paginaAtual - 1)}
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
            href={construirLink({ nome }, paginaAtual + 1)}
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
