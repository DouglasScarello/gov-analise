import Link from "next/link";
import FiltroContratos from "@/components/FiltroContratos";
import { listarContratos, UFS } from "@/lib/api";

const POR_PAGINA = 24;

type Params = {
  orgao?: string;
  fornecedor?: string;
  uf?: string;
  pagina?: string;
};

function formatarData(iso: string | null) {
  if (!iso) return "data não informada";
  const [ano, mes, dia] = iso.split("T")[0].split("-");
  return `${dia}/${mes}/${ano}`;
}

function formatarMoeda(valor: number | null) {
  if (valor == null) return "valor não informado";
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function construirLink(params: Params, novaPagina: number) {
  const qs = new URLSearchParams();
  if (params.orgao) qs.set("orgao", params.orgao);
  if (params.fornecedor) qs.set("fornecedor", params.fornecedor);
  if (params.uf) qs.set("uf", params.uf);
  qs.set("pagina", String(novaPagina));
  return `/contratos?${qs.toString()}`;
}

export default async function ContratosPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  const { orgao, fornecedor, uf } = sp;
  const paginaAtual = Math.max(1, Number(sp.pagina) || 1);
  const offset = (paginaAtual - 1) * POR_PAGINA;

  const pagina = await listarContratos({ orgao, fornecedor, uf, limit: POR_PAGINA, offset });
  const contratos = pagina.items;
  const temProximaPagina = offset + contratos.length < pagina.total;

  const sufixoOrgao = orgao ? `&orgao=${encodeURIComponent(orgao)}` : "";
  const sufixoFornecedor = fornecedor ? `&fornecedor=${encodeURIComponent(fornecedor)}` : "";

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Contratos públicos</h1>
      <p className="mt-1 text-neutral-500">
        Contratos e compras de órgãos federais, cruzando Compras.gov.br e Portal da Transparência.
      </p>

      <div className="mt-4">
        <FiltroContratos orgaoInicial={orgao} fornecedorInicial={fornecedor} />
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="text-sm text-neutral-500">Estado:</span>
        <Link
          href={`/contratos?${(() => {
            const qs = new URLSearchParams();
            if (orgao) qs.set("orgao", orgao);
            if (fornecedor) qs.set("fornecedor", fornecedor);
            return qs.toString();
          })()}`}
          className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
            !uf
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Todos
        </Link>
        {UFS.map((sigla) => (
          <Link
            key={sigla}
            href={`/contratos?uf=${sigla}${sufixoOrgao}${sufixoFornecedor}`}
            className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
              uf === sigla
                ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {sigla}
          </Link>
        ))}
      </div>

      <ul className="mt-6 divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
        {contratos.map((c, i) => (
          <li key={i} className="px-4 py-3">
            <p className="font-medium">{c.orgaoNome}</p>
            <p className="text-sm text-neutral-500 line-clamp-2">{c.objeto}</p>
            <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
              {formatarMoeda(c.valor)}
              {c.fornecedorNome ? ` · ${c.fornecedorNome}` : ""}
              {c.uf ? ` · ${c.uf}` : ""}
            </p>
            <p className="mt-1 text-xs text-neutral-500">
              {formatarData(c.data)} · {c.modalidade ?? c.fonte}
            </p>
          </li>
        ))}
      </ul>

      {contratos.length === 0 && (
        <p className="mt-10 text-center text-neutral-500">Nenhum resultado nesse filtro.</p>
      )}

      <div className="mt-8 flex items-center justify-between">
        {paginaAtual > 1 ? (
          <Link
            href={construirLink({ orgao, fornecedor, uf }, paginaAtual - 1)}
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
            href={construirLink({ orgao, fornecedor, uf }, paginaAtual + 1)}
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
