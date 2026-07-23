import Link from "next/link";
import FiltroNome from "@/components/FiltroNome";
import VotacaoItem from "@/components/VotacaoItem";
import { listarVotacoesSenado, UFS } from "@/lib/api";

const POR_PAGINA = 30;

type Params = {
  senador?: string;
  uf?: string;
  resultado?: string;
  pagina?: string;
};

const RESULTADOS = ["Aprovado", "Rejeitado", "Prejudicado", "Empate"] as const;

function construirLink(params: Params, novaPagina: number) {
  const qs = new URLSearchParams();
  if (params.senador) qs.set("senador", params.senador);
  if (params.uf) qs.set("uf", params.uf);
  if (params.resultado) qs.set("resultado", params.resultado);
  qs.set("pagina", String(novaPagina));
  return `/legislativo?${qs.toString()}`;
}

export default async function LegislativoPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  const { senador, uf, resultado } = sp;
  const paginaAtual = Math.max(1, Number(sp.pagina) || 1);
  const offset = (paginaAtual - 1) * POR_PAGINA;

  const pagina = await listarVotacoesSenado({ senador, uf, resultado, limit: POR_PAGINA, offset });
  const votacoes = pagina.items;
  const temProximaPagina = offset + votacoes.length < pagina.total;

  const sufixoSenador = senador ? `&senador=${encodeURIComponent(senador)}` : "";
  const sufixoUf = uf ? `&uf=${uf}` : "";

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Legislativo — Votações do Senado</h1>
      <p className="mt-1 text-neutral-500">
        Votações nominais dos senadores em exercício, por matéria e resultado.
      </p>

      <div className="mt-4">
        <FiltroNome action="/legislativo" valorInicial={senador} placeholder="Buscar por senador..." />
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <Link
          href={`/legislativo?${(() => {
            const qs = new URLSearchParams();
            if (senador) qs.set("senador", senador);
            if (uf) qs.set("uf", uf);
            return qs.toString();
          })()}`}
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            !resultado
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Todos os resultados
        </Link>
        {RESULTADOS.map((r) => (
          <Link
            key={r}
            href={`/legislativo?resultado=${r}${sufixoSenador}${sufixoUf}`}
            className={`rounded-full border px-3 py-1 text-sm ${
              resultado === r
                ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {r}
          </Link>
        ))}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="text-sm text-neutral-500">Estado:</span>
        <Link
          href={`/legislativo?${(() => {
            const qs = new URLSearchParams();
            if (senador) qs.set("senador", senador);
            if (resultado) qs.set("resultado", resultado);
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
            href={`/legislativo?uf=${sigla}${sufixoSenador}${resultado ? `&resultado=${resultado}` : ""}`}
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

      <p className="mt-4 text-xs text-neutral-400">Clique em uma votação para ver a ementa completa e o voto de todos os senadores.</p>

      <ul className="mt-2 divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
        {votacoes.map((v, i) => (
          <VotacaoItem key={i} votacao={v} />
        ))}
      </ul>

      {votacoes.length === 0 && (
        <p className="mt-10 text-center text-neutral-500">Nenhum resultado nesse filtro.</p>
      )}

      <div className="mt-8 flex items-center justify-between">
        {paginaAtual > 1 ? (
          <Link
            href={construirLink({ senador, uf, resultado }, paginaAtual - 1)}
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
            href={construirLink({ senador, uf, resultado }, paginaAtual + 1)}
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
