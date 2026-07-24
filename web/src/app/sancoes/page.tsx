import Link from "next/link";
import FiltroNome from "@/components/FiltroNome";
import { listarSancoes } from "@/lib/api";

const POR_PAGINA = 24;

type Params = {
  nome?: string;
  origem?: string;
  pagina?: string;
};

const ORIGENS = [
  { valor: undefined, label: "Todas" },
  { valor: "CEIS", label: "CEIS (impedidos de contratar)" },
  { valor: "CNEP", label: "CNEP (empresas punidas)" },
] as const;

function formatarData(iso: string | null) {
  if (!iso) return "não informada";
  const [ano, mes, dia] = iso.split("T")[0].split("-");
  return `${dia}/${mes}/${ano}`;
}

function formatarMoeda(valor: number | null) {
  if (valor == null) return null;
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function construirLink(params: Params, novaPagina: number) {
  const qs = new URLSearchParams();
  if (params.nome) qs.set("nome", params.nome);
  if (params.origem) qs.set("origem", params.origem);
  qs.set("pagina", String(novaPagina));
  return `/sancoes?${qs.toString()}`;
}

export default async function SancoesPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  const { nome, origem } = sp;
  const paginaAtual = Math.max(1, Number(sp.pagina) || 1);
  const offset = (paginaAtual - 1) * POR_PAGINA;

  const pagina = await listarSancoes({ nome, origem, limit: POR_PAGINA, offset });
  const sancoes = pagina.items;
  const temProximaPagina = offset + sancoes.length < pagina.total;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Sanções (CEIS/CNEP)</h1>
      <p className="mt-1 text-neutral-500">
        Empresas e pessoas impedidas de contratar com o poder público ou punidas por atos de corrupção,
        segundo o Portal da Transparência.
      </p>

      <div className="mt-4">
        <FiltroNome action="/sancoes" valorInicial={nome} placeholder="Buscar por nome do sancionado..." />
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {ORIGENS.map((o) => (
          <Link
            key={o.label}
            href={`/sancoes?${(() => {
              const qs = new URLSearchParams();
              if (nome) qs.set("nome", nome);
              if (o.valor) qs.set("origem", o.valor);
              return qs.toString();
            })()}`}
            className={`rounded-full border px-3 py-1 text-sm font-medium ${
              origem === o.valor
                ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {o.label}
          </Link>
        ))}
      </div>

      <ul className="mt-6 divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
        {sancoes.map((s) => (
          <li key={s.id}>
            <Link
              href={`/sancoes/${s.id}`}
              className="block px-4 py-3 hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium">{s.sancionadoNome}</p>
                  <p className="text-sm text-neutral-500">
                    {s.tipoSancao}
                    {s.orgaoSancionador ? ` · ${s.orgaoSancionador}` : ""}
                  </p>
                  <p className="mt-1 text-xs text-neutral-500">
                    Início: {formatarData(s.dataInicioSancao)}
                    {s.dataFimSancao ? ` · Fim: ${formatarData(s.dataFimSancao)}` : ""}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <span className="rounded-full border border-neutral-300 px-2.5 py-1 text-xs font-medium dark:border-neutral-700">
                    {s.origemSancao}
                  </span>
                  {formatarMoeda(s.valorMulta) && (
                    <p className="mt-1 text-xs text-neutral-500">{formatarMoeda(s.valorMulta)}</p>
                  )}
                </div>
              </div>
            </Link>
          </li>
        ))}
      </ul>

      {sancoes.length === 0 && (
        <p className="mt-10 text-center text-neutral-500">Nenhum resultado nesse filtro.</p>
      )}

      <div className="mt-8 flex items-center justify-between">
        {paginaAtual > 1 ? (
          <Link
            href={construirLink({ nome, origem }, paginaAtual - 1)}
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
            href={construirLink({ nome, origem }, paginaAtual + 1)}
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
