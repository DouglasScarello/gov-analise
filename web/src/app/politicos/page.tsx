import Link from "next/link";
import PoliticoCargoCard from "@/components/PoliticoCargoCard";
import { listarAnosDisponiveis, listarPoliticosCargo, listarTiposDeCargo, UFS, type Nivel } from "@/lib/api";

const POR_PAGINA = 24;

type Params = {
  nivel?: string;
  cargo?: string;
  uf?: string;
  municipio?: string;
  ano?: string;
  pagina?: string;
};

const NIVEL_LABEL: Record<Nivel, string> = {
  federal: "Federal",
  estadual: "Estadual",
  nacional: "Nacional",
  municipal: "Municipal",
};

const NIVEL_DESCRICAO: Record<Nivel, string> = {
  federal: "Deputados federais e senadores em exercício.",
  estadual: "Governadores, vice-governadores e deputados estaduais/distritais eleitos de 1994 a 2022.",
  nacional: "Presidente e vice-presidente eleitos de 1994 a 2022.",
  municipal: "Prefeitos, vice-prefeitos e vereadores eleitos de 1996 a 2024.",
};

const NIVEL_TEM_UF: Record<Nivel, boolean> = {
  federal: true,
  estadual: true,
  nacional: false,
  municipal: true,
};

const NIVEL_TEM_ANO: Record<Nivel, boolean> = {
  federal: false,
  estadual: true,
  nacional: true,
  municipal: true,
};

const NIVEL_AVISO: Partial<Record<Nivel, string>> = {
  nacional:
    "Vice-presidentes eleitos antes de 2014 não aparecem: o TSE não registrou a situação de eleição desse cargo nessas eleições, e não há como ligar o vice à chapa vencedora com segurança. A eleição de 2006 também não tem resultado de presidente/vice-presidente disponível na fonte.",
  estadual:
    "Vice-governadores eleitos antes de 2014 não aparecem pelo mesmo motivo: o TSE não registrou a situação de eleição desse cargo nessas eleições. Governadores e deputados estaduais/distritais não têm essa lacuna.",
  municipal:
    "Vice-prefeitos eleitos antes de 2012 não aparecem: o TSE não registrou a situação de eleição desse cargo nas eleições de 1996 a 2008. Prefeitos e vereadores não têm essa lacuna em nenhum ano.",
};

function ehNivel(v: string | undefined): v is Nivel {
  return v === "federal" || v === "estadual" || v === "nacional" || v === "municipal";
}

function construirLink(params: Params, novaPagina: number) {
  const qs = new URLSearchParams();
  if (params.nivel) qs.set("nivel", params.nivel);
  if (params.cargo) qs.set("cargo", params.cargo);
  if (params.uf) qs.set("uf", params.uf);
  if (params.municipio) qs.set("municipio", params.municipio);
  if (params.ano) qs.set("ano", params.ano);
  qs.set("pagina", String(novaPagina));
  return `/politicos?${qs.toString()}`;
}

export default async function PoliticosPage({
  searchParams,
}: {
  searchParams: Promise<Params>;
}) {
  const sp = await searchParams;
  const nivel: Nivel = ehNivel(sp.nivel) ? sp.nivel : "federal";
  const { cargo, uf, municipio, ano } = sp;
  const paginaAtual = Math.max(1, Number(sp.pagina) || 1);
  const offset = (paginaAtual - 1) * POR_PAGINA;

  const tipos = await listarTiposDeCargo();
  const cargosDoNivel = tipos.filter((t) => t.nivel === nivel);
  const temAno = NIVEL_TEM_ANO[nivel];
  const anosDisponiveis = temAno ? await listarAnosDisponiveis(nivel) : [];

  const precisaUf = NIVEL_TEM_UF[nivel] && nivel !== "federal";
  const pagina =
    precisaUf && !uf
      ? { items: [], total: 0, limit: POR_PAGINA, offset }
      : await listarPoliticosCargo({
          nivel,
          cargo,
          uf,
          municipio,
          ano: ano ? Number(ano) : undefined,
          limit: POR_PAGINA,
          offset,
        });
  const pessoas = pagina.items;
  const temProximaPagina = offset + pessoas.length < pagina.total;

  const sufixoUf = uf ? `&uf=${uf}` : "";
  const sufixoAno = ano ? `&ano=${ano}` : "";

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="text-2xl font-semibold tracking-tight">Todos os cargos políticos</h1>
      <p className="mt-1 text-neutral-500">{NIVEL_DESCRICAO[nivel]}</p>

      {NIVEL_AVISO[nivel] && (
        <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-300">
          ⚠️ {NIVEL_AVISO[nivel]}
        </p>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        {(Object.keys(NIVEL_LABEL) as Nivel[]).map((n) => (
          <Link
            key={n}
            href={`/politicos?nivel=${n}`}
            className={`rounded-full border px-3 py-1 text-sm font-medium ${
              nivel === n
                ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {NIVEL_LABEL[n]}
          </Link>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          href={`/politicos?nivel=${nivel}${sufixoUf}${sufixoAno}`}
          className={`rounded-full border px-3 py-1 text-sm ${
            !cargo
              ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
              : "border-neutral-300 dark:border-neutral-700"
          }`}
        >
          Todos os cargos
        </Link>
        {cargosDoNivel.map((t) => (
          <Link
            key={t.cargo}
            href={`/politicos?nivel=${nivel}&cargo=${encodeURIComponent(t.cargo)}${sufixoUf}${sufixoAno}`}
            className={`rounded-full border px-3 py-1 text-sm ${
              cargo === t.cargo
                ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            {t.label}
          </Link>
        ))}
      </div>

      {temAno && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-sm text-neutral-500">Ano da eleição:</span>
          <Link
            href={`/politicos?nivel=${nivel}${cargo ? `&cargo=${encodeURIComponent(cargo)}` : ""}${sufixoUf}`}
            className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
              !ano
                ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                : "border-neutral-300 dark:border-neutral-700"
            }`}
          >
            Todos
          </Link>
          {anosDisponiveis.map((a) => (
            <Link
              key={a}
              href={`/politicos?nivel=${nivel}${cargo ? `&cargo=${encodeURIComponent(cargo)}` : ""}${sufixoUf}&ano=${a}`}
              className={`rounded-full border px-2.5 py-1 text-xs font-medium ${
                ano === String(a)
                  ? "border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300"
                  : "border-neutral-300 dark:border-neutral-700"
              }`}
            >
              {a}
            </Link>
          ))}
        </div>
      )}

      {precisaUf && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-sm text-neutral-500">Estado:</span>
          {UFS.map((sigla) => (
            <Link
              key={sigla}
              href={`/politicos?nivel=${nivel}&uf=${sigla}${cargo ? `&cargo=${encodeURIComponent(cargo)}` : ""}${sufixoAno}`}
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
      )}

      {precisaUf && !uf ? (
        <p className="mt-10 text-center text-neutral-500">
          Selecione um estado para ver os políticos desse nível.
        </p>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {pessoas.map((p) => (
              <PoliticoCargoCard key={`${p.nivel}-${p.id}`} pessoa={p} />
            ))}
          </div>

          {pessoas.length === 0 && (
            <p className="mt-10 text-center text-neutral-500">Nenhum resultado nesse filtro.</p>
          )}

          <div className="mt-8 flex items-center justify-between">
            {paginaAtual > 1 ? (
              <Link
                href={construirLink({ nivel, cargo, uf, municipio, ano }, paginaAtual - 1)}
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
                href={construirLink({ nivel, cargo, uf, municipio, ano }, paginaAtual + 1)}
                className="rounded-full border border-neutral-300 px-4 py-2 text-sm hover:border-blue-500 dark:border-neutral-700"
              >
                Próxima →
              </Link>
            ) : (
              <span />
            )}
          </div>
        </>
      )}
    </div>
  );
}
