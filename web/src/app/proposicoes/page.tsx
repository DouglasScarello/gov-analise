import Link from "next/link";
import FiltroNome from "@/components/FiltroNome";
import { listarProposicoes, listarTiposProposicao } from "@/lib/api";

const POR_PAGINA = 30;
const TIPOS_EXIBIDOS = 12;

type Params = {
  casa?: string;
  tipoSigla?: string;
  ano?: string;
  nome?: string; // reaproveita o FiltroNome genérico como busca de texto na ementa
  pagina?: string;
};

function formatarData(iso: string | null) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("pt-BR");
}

function construirLink(params: Params, novaPagina: number) {
  const qs = new URLSearchParams();
  if (params.casa) qs.set("casa", params.casa);
  if (params.tipoSigla) qs.set("tipoSigla", params.tipoSigla);
  if (params.ano) qs.set("ano", params.ano);
  if (params.nome) qs.set("nome", params.nome);
  qs.set("pagina", String(novaPagina));
  return `/proposicoes?${qs.toString()}`;
}

export default async function ProposicoesPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  const { casa, tipoSigla, ano, nome: q } = sp;
  const paginaAtual = Math.max(1, Number(sp.pagina) || 1);
  const offset = (paginaAtual - 1) * POR_PAGINA;

  const [tipos, pagina] = await Promise.all([
    listarTiposProposicao(),
    listarProposicoes({ casa, tipoSigla, ano: ano ? Number(ano) : undefined, q, limit: POR_PAGINA, offset }),
  ]);
  const proposicoes = pagina.items;
  const temProximaPagina = offset + proposicoes.length < pagina.total;
  const tiposPrincipais = tipos.slice(0, TIPOS_EXIBIDOS);

  const sufixoCasa = casa ? `&casa=${casa}` : "";
  const sufixoAno = ano ? `&ano=${ano}` : "";
  const sufixoQ = q ? `&nome=${encodeURIComponent(q)}` : "";

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Proposições legislativas</h1>
      <p className="mt-1 text-neutral-500">
        Projetos de lei, PECs, requerimentos e emendas de autoria de deputados e senadores —
        toda a carreira de cada um, não só o mandato atual.
      </p>

      <div className="mt-4">
        <FiltroNome action="/proposicoes" valorInicial={q} placeholder="Buscar na ementa..." />
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href={`/proposicoes?${(() => {
            const qs = new URLSearchParams();
            if (q) qs.set("nome", q);
            return qs.toString();
          })()}`}
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            !casa
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Câmara e Senado
        </Link>
        <Link
          href={`/proposicoes?casa=Camara${sufixoAno}${sufixoQ}`}
          className={`rounded-full border px-3 py-1 text-sm ${
            casa === "Camara"
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Câmara
        </Link>
        <Link
          href={`/proposicoes?casa=Senado${sufixoAno}${sufixoQ}`}
          className={`rounded-full border px-3 py-1 text-sm ${
            casa === "Senado"
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Senado
        </Link>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="text-sm text-neutral-500">Tipo:</span>
        <Link
          href={`/proposicoes?${(() => {
            const qs = new URLSearchParams();
            if (casa) qs.set("casa", casa);
            if (ano) qs.set("ano", ano);
            if (q) qs.set("nome", q);
            return qs.toString();
          })()}`}
          className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
            !tipoSigla
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Todos
        </Link>
        {tiposPrincipais.map((t) => (
          <Link
            key={t.tipoSigla}
            href={`/proposicoes?tipoSigla=${t.tipoSigla}${sufixoCasa}${sufixoAno}${sufixoQ}`}
            className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
              tipoSigla === t.tipoSigla
                ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {t.tipoSigla} ({t.total.toLocaleString("pt-BR")})
          </Link>
        ))}
      </div>

      <ul className="mt-6 divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
        {proposicoes.map((p, i) => (
          <li key={i} className="px-4 py-3">
            <a
              href={p.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
            >
              {p.tipoSigla} {p.numero}/{p.ano}
            </a>
            {p.ementa && <p className="mt-1 line-clamp-2 text-sm text-neutral-500">{p.ementa}</p>}
            <p className="mt-1 text-xs text-neutral-400">
              {p.casa === "Camara" ? "Câmara" : "Senado"} · {formatarData(p.dataApresentacao)}
            </p>
          </li>
        ))}
      </ul>

      {proposicoes.length === 0 && (
        <p className="mt-10 text-center text-neutral-500">Nenhum resultado nesse filtro.</p>
      )}

      <div className="mt-8 flex items-center justify-between">
        {paginaAtual > 1 ? (
          <Link
            href={construirLink({ casa, tipoSigla, ano, nome: q }, paginaAtual - 1)}
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
            href={construirLink({ casa, tipoSigla, ano, nome: q }, paginaAtual + 1)}
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
