import Link from "next/link";
import PoliticoCard from "@/components/PoliticoCard";
import PoliticoMunicipalCard from "@/components/PoliticoMunicipalCard";
import { listarPessoas, listarPoliticosMunicipais, UFS } from "@/lib/api";

const POR_PAGINA = 24;

type Params = {
  nivel?: string;
  casa?: string;
  uf?: string;
  cargo?: string;
  pagina?: string;
};

function construirLink(params: Params, novaPagina: number) {
  const qs = new URLSearchParams();
  if (params.nivel) qs.set("nivel", params.nivel);
  if (params.casa) qs.set("casa", params.casa);
  if (params.uf) qs.set("uf", params.uf);
  if (params.cargo) qs.set("cargo", params.cargo);
  qs.set("pagina", String(novaPagina));
  return `/politicos?${qs.toString()}`;
}

export default async function PoliticosPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const { nivel = "federal", casa, uf, cargo, pagina } = await searchParams;
  const paginaAtual = Math.max(1, Number(pagina) || 1);
  const offset = (paginaAtual - 1) * POR_PAGINA;
  const municipal = nivel === "municipal";

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Todos os políticos</h1>
      <p className="mt-1 text-neutral-500">
        {municipal
          ? "Prefeitos, vice-prefeitos e vereadores eleitos em 2024."
          : "Deputados federais e senadores em exercício, com foto e partido."}
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href="/politicos?nivel=federal"
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            !municipal ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300" : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Federal
        </Link>
        <Link
          href="/politicos?nivel=municipal"
          className={`rounded-full border px-3 py-1 text-sm font-medium ${
            municipal ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300" : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Municipal
        </Link>
      </div>

      {municipal ? (
        <MunicipalSection uf={uf} cargo={cargo} paginaAtual={paginaAtual} offset={offset} />
      ) : (
        <FederalSection casa={casa} uf={uf} paginaAtual={paginaAtual} offset={offset} />
      )}
    </div>
  );
}

async function FederalSection({
  casa,
  uf,
  paginaAtual,
  offset,
}: {
  casa?: string;
  uf?: string;
  paginaAtual: number;
  offset: number;
}) {
  const pessoas = await listarPessoas({ casa, uf, limit: POR_PAGINA, offset });
  const casas = ["Câmara", "Senado"];

  return (
    <>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href="/politicos?nivel=federal"
          className={`rounded-full border px-3 py-1 text-sm ${
            !casa ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300" : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Todos
        </Link>
        {casas.map((c) => (
          <Link
            key={c}
            href={`/politicos?nivel=federal&casa=${encodeURIComponent(c)}`}
            className={`rounded-full border px-3 py-1 text-sm ${
              casa === c ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300" : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {c}
          </Link>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {pessoas.map((p) => (
          <PoliticoCard key={p.slug} pessoa={p} />
        ))}
      </div>

      {pessoas.length === 0 && (
        <p className="mt-10 text-center text-neutral-500">Nenhum político encontrado.</p>
      )}

      <Paginacao
        params={{ nivel: "federal", casa, uf }}
        paginaAtual={paginaAtual}
        temProxima={pessoas.length === POR_PAGINA}
      />
    </>
  );
}

async function MunicipalSection({
  uf,
  cargo,
  paginaAtual,
  offset,
}: {
  uf?: string;
  cargo?: string;
  paginaAtual: number;
  offset: number;
}) {
  const cargos = ["PREFEITO", "VICE-PREFEITO", "VEREADOR"];
  const pessoas = uf
    ? await listarPoliticosMunicipais({ uf, cargo, limit: POR_PAGINA, offset })
    : [];

  return (
    <>
      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className="text-sm text-neutral-500">Estado:</span>
        {UFS.map((sigla) => (
          <Link
            key={sigla}
            href={`/politicos?nivel=municipal&uf=${sigla}${cargo ? `&cargo=${cargo}` : ""}`}
            className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
              uf === sigla ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300" : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {sigla}
          </Link>
        ))}
      </div>

      {uf && (
        <div className="mt-3 flex flex-wrap gap-2">
          <Link
            href={`/politicos?nivel=municipal&uf=${uf}`}
            className={`rounded-full border px-3 py-1 text-sm ${
              !cargo ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300" : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            Todos os cargos
          </Link>
          {cargos.map((c) => (
            <Link
              key={c}
              href={`/politicos?nivel=municipal&uf=${uf}&cargo=${c}`}
              className={`rounded-full border px-3 py-1 text-sm ${
                cargo === c ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300" : "border-neutral-300 dark:border-neutral-700"
              }`}
            >
              {c === "PREFEITO" ? "Prefeitos" : c === "VICE-PREFEITO" ? "Vice-prefeitos" : "Vereadores"}
            </Link>
          ))}
        </div>
      )}

      {!uf ? (
        <p className="mt-10 text-center text-neutral-500">
          Selecione um estado para ver prefeitos, vice-prefeitos e vereadores eleitos.
        </p>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {pessoas.map((p) => (
              <PoliticoMunicipalCard key={p.SQ_CANDIDATO} pessoa={p} />
            ))}
          </div>

          {pessoas.length === 0 && (
            <p className="mt-10 text-center text-neutral-500">Nenhum resultado nesse filtro.</p>
          )}

          <Paginacao
            params={{ nivel: "municipal", uf, cargo }}
            paginaAtual={paginaAtual}
            temProxima={pessoas.length === POR_PAGINA}
          />
        </>
      )}
    </>
  );
}

function Paginacao({
  params,
  paginaAtual,
  temProxima,
}: {
  params: Params;
  paginaAtual: number;
  temProxima: boolean;
}) {
  return (
    <div className="mt-8 flex items-center justify-between">
      {paginaAtual > 1 ? (
        <Link
          href={construirLink(params, paginaAtual - 1)}
          className="rounded-full border border-neutral-300 px-4 py-2 text-sm hover:border-blue-500 dark:border-neutral-700"
        >
          ← Anterior
        </Link>
      ) : (
        <span />
      )}
      <span className="text-sm text-neutral-500">Página {paginaAtual}</span>
      {temProxima ? (
        <Link
          href={construirLink(params, paginaAtual + 1)}
          className="rounded-full border border-neutral-300 px-4 py-2 text-sm hover:border-blue-500 dark:border-neutral-700"
        >
          Próxima →
        </Link>
      ) : (
        <span />
      )}
    </div>
  );
}
