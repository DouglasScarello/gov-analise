import Image from "next/image";
import { notFound } from "next/navigation";
import { obterPoliticoCargo, type Nivel } from "@/lib/api";

const CARGO_LABEL: Record<string, string> = {
  "DEPUTADO FEDERAL": "Deputado(a) Federal",
  SENADOR: "Senador(a)",
  PRESIDENTE: "Presidente",
  "VICE-PRESIDENTE": "Vice-presidente",
  GOVERNADOR: "Governador(a)",
  "VICE-GOVERNADOR": "Vice-governador(a)",
  "DEPUTADO ESTADUAL": "Deputado(a) Estadual",
  "DEPUTADO DISTRITAL": "Deputado(a) Distrital",
  PREFEITO: "Prefeito(a)",
  "VICE-PREFEITO": "Vice-prefeito(a)",
  VEREADOR: "Vereador(a)",
};

function iniciais(nome: string) {
  const partes = nome.trim().split(/\s+/);
  return ((partes[0]?.[0] ?? "") + (partes[1]?.[0] ?? "")).toUpperCase();
}

function ehNivel(v: string): v is Nivel {
  return v === "federal" || v === "estadual" || v === "nacional" || v === "municipal";
}

export default async function CargoPoliticoPage({
  params,
}: {
  params: Promise<{ nivel: string; id: string }>;
}) {
  const { nivel, id } = await params;
  if (!ehNivel(nivel)) notFound();

  let pessoa;
  try {
    pessoa = await obterPoliticoCargo(nivel, id);
  } catch {
    notFound();
  }

  const federal = nivel === "federal";

  const nome = federal
    ? (pessoa.nome as string)
    : ((pessoa.NM_URNA_CANDIDATO as string) || (pessoa.NM_CANDIDATO as string));
  const nomeCompleto = federal ? null : (pessoa.NM_CANDIDATO as string | undefined);
  const foto = federal ? ((pessoa.camaraFoto ?? pessoa.senadoFoto) as string | null) : null;
  const partido = federal
    ? ((pessoa.camaraPartido ?? pessoa.senadoPartido) as string | null)
    : (pessoa.SG_PARTIDO as string | null);
  const uf = federal ? ((pessoa.camaraUf ?? pessoa.senadoUf) as string | null) : (pessoa.SG_UF as string | null);
  const municipio = federal ? null : (pessoa.NM_UE as string | undefined);
  const cargo = federal ? (pessoa.casa as string) : (pessoa.DS_CARGO as string);
  const situacao = federal ? null : (pessoa.DS_SIT_TOT_TURNO as string | undefined);
  const ocupacao = federal ? null : (pessoa.DS_OCUPACAO as string | undefined);
  const escolaridade = federal ? null : (pessoa.DS_GRAU_INSTRUCAO as string | undefined);
  const anoEleicao = federal ? null : (pessoa.ANO_ELEICAO as string | undefined);
  const sancoes = pessoa.sancoesVinculadas;

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="flex items-center gap-4">
        {foto ? (
          <Image
            src={foto}
            alt={nome}
            width={88}
            height={88}
            className="h-22 w-22 rounded-full object-cover ring-2 ring-neutral-200 dark:ring-neutral-800"
            unoptimized
          />
        ) : (
          <div className="flex h-22 w-22 shrink-0 items-center justify-center rounded-full bg-neutral-200 text-2xl font-semibold text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
            {iniciais(nome)}
          </div>
        )}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{nome}</h1>
          <p className="text-neutral-500">
            {[partido, municipio, uf].filter(Boolean).join(" · ")}
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
          {federal ? cargo : CARGO_LABEL[cargo] ?? cargo}
          {situacao ? ` — ${situacao.toLowerCase()}` : ""}
        </span>
      </div>

      {!federal && (
        <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
          {nomeCompleto && nomeCompleto !== nome && (
            <div>
              <dt className="text-neutral-500">Nome completo</dt>
              <dd className="font-medium">{nomeCompleto}</dd>
            </div>
          )}
          {ocupacao && (
            <div>
              <dt className="text-neutral-500">Ocupação declarada</dt>
              <dd className="font-medium">{ocupacao}</dd>
            </div>
          )}
          {escolaridade && (
            <div>
              <dt className="text-neutral-500">Escolaridade</dt>
              <dd className="font-medium">{escolaridade}</dd>
            </div>
          )}
          {anoEleicao && (
            <div>
              <dt className="text-neutral-500">Eleição</dt>
              <dd className="font-medium">{anoEleicao}</dd>
            </div>
          )}
        </dl>
      )}

      <section className="mt-8">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Sanções vinculadas ao nome
        </h2>
        {sancoes.length === 0 ? (
          <p className="text-sm text-neutral-500">Nenhuma sanção encontrada com esse nome.</p>
        ) : (
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {sancoes.map((s) => (
              <li key={s.id} className="px-4 py-3">
                <p className="font-medium">{s.sancionadoNome}</p>
                <p className="text-sm text-neutral-500">
                  {s.tipoSancao} · {s.origemSancao}
                </p>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-xs text-neutral-400">
          Cruzamento por nome — pode incluir homônimos.
        </p>
      </section>
    </div>
  );
}
