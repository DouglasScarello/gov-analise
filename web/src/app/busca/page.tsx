import Link from "next/link";
import SearchBar from "@/components/SearchBar";
import { buscar } from "@/lib/api";

function formatarMoeda(valor: number | null | undefined) {
  if (valor == null) return "valor não informado";
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default async function BuscaPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const termo = (q ?? "").trim();

  if (termo.length < 2) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <SearchBar valorInicial={termo} />
        <p className="mt-6 text-center text-neutral-500">Digite ao menos 2 letras para buscar.</p>
      </div>
    );
  }

  const resultado = await buscar(termo);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <SearchBar valorInicial={termo} />

      <p className="mt-6 text-sm text-neutral-500">
        {resultado.total} resultado{resultado.total === 1 ? "" : "s"} para &ldquo;{termo}&rdquo;
      </p>

      {resultado.pessoas.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Políticos
          </h2>
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {resultado.pessoas.map((p) => (
              <li key={p.slug}>
                <Link
                  href={`/politico/federal/${p.slug}`}
                  className="flex items-center justify-between px-4 py-3 hover:bg-neutral-100 dark:hover:bg-neutral-900"
                >
                  <span className="font-medium">{p.nome}</span>
                  <span className="text-sm text-neutral-500">
                    {p.camaraPartido ?? p.senadoPartido} · {p.camaraUf ?? p.senadoUf} · {p.casa}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {resultado.sancoes.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Sanções (CEIS/CNEP)
          </h2>
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {resultado.sancoes.map((s) => (
              <li key={s.id}>
                <Link
                  href={`/sancoes/${s.id}`}
                  className="block px-4 py-3 hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                >
                  <p className="font-medium">{s.sancionadoNome}</p>
                  <p className="text-sm text-neutral-500">
                    {s.tipoSancao} · {s.origemSancao}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {resultado.contratos.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Contratos públicos
          </h2>
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {resultado.contratos.map((c, i) => (
              <li key={c.id ?? i}>
                <Link
                  href={c.id ? `/contratos/${c.id}` : "#"}
                  className="block px-4 py-3 hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                >
                  <p className="font-medium">{c.orgaoNome}</p>
                  <p className="text-sm text-neutral-500 line-clamp-2">{c.objeto}</p>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    {formatarMoeda(c.valor)} {c.fornecedorNome ? `· ${c.fornecedorNome}` : ""}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {resultado.orgaos.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Órgãos públicos
          </h2>
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {resultado.orgaos.map((o) => (
              <li key={o.codigo} className="px-4 py-3">
                {o.descricao}
              </li>
            ))}
          </ul>
        </section>
      )}

      {resultado.total === 0 && (
        <p className="mt-8 text-center text-neutral-500">Nenhum resultado encontrado.</p>
      )}
    </div>
  );
}
