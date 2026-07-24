import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { obterPessoa, obterPoliticoCargo, type Candidatura, type Nivel, type Sancao } from "@/lib/api";

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

const VALORES_INVALIDOS = ["#NULO", "#NULO#", "#NE", "#NE#", "NÃO DIVULGÁVEL", "NÃO INFORMADO"];

function campoValido(valor: string | null | undefined): valor is string {
  return !!valor && !VALORES_INVALIDOS.includes(valor.toUpperCase());
}

function titleCase(valor: string) {
  return valor
    .toLowerCase()
    .split(" ")
    .map((p) => (p.length > 2 ? p[0].toUpperCase() + p.slice(1) : p))
    .join(" ");
}

function iniciais(nome: string) {
  const partes = nome.trim().split(/\s+/);
  return ((partes[0]?.[0] ?? "") + (partes[1]?.[0] ?? "")).toUpperCase();
}

function formatarData(iso: string | null | undefined) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString("pt-BR");
}

function formatarMoeda(valor: number | null | undefined) {
  if (valor == null) return "valor não informado";
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function ehNivel(v: string): v is Nivel {
  return v === "federal" || v === "estadual" || v === "nacional" || v === "municipal";
}

type PerfilComum = {
  nome: string;
  nomeCompleto: string | null;
  foto: string | null;
  partido: string | null;
  uf: string | null;
  municipio: string | null;
  cargoLabel: string;
  situacao: string | null;
  anoEleicao: string | null;
  genero: string | null;
  corRaca: string | null;
  escolaridade: string | null;
  ocupacao: string | null;
  sancoes: Sancao[];
  candidaturas: Candidatura[];
};

export default async function PoliticoPage({
  params,
}: {
  params: Promise<{ nivel: string; id: string }>;
}) {
  const { nivel: nivelParam, id } = await params;
  if (!ehNivel(nivelParam)) notFound();
  const federal = nivelParam === "federal";

  let comum: PerfilComum;
  let pessoaFederal: Awaited<ReturnType<typeof obterPessoa>> | null = null;

  try {
    if (federal) {
      pessoaFederal = await obterPessoa(id);
      comum = {
        nome: pessoaFederal.nome,
        nomeCompleto: null,
        foto: pessoaFederal.camaraFoto ?? pessoaFederal.senadoFoto ?? null,
        partido: pessoaFederal.camaraPartido ?? pessoaFederal.senadoPartido ?? null,
        uf: pessoaFederal.camaraUf ?? pessoaFederal.senadoUf ?? null,
        municipio: null,
        cargoLabel: pessoaFederal.casa,
        situacao: null,
        anoEleicao: null,
        genero: pessoaFederal.genero ?? null,
        corRaca: pessoaFederal.corRaca ?? null,
        escolaridade: pessoaFederal.escolaridade ?? null,
        ocupacao: pessoaFederal.ocupacao ?? null,
        sancoes: pessoaFederal.sancoesVinculadas,
        candidaturas: pessoaFederal.candidaturas,
      };
    } else {
      const pessoa = await obterPoliticoCargo(nivelParam, id);
      const nome = (pessoa.NM_URNA_CANDIDATO as string) || (pessoa.NM_CANDIDATO as string);
      const nomeCompleto = pessoa.NM_CANDIDATO as string | undefined;
      const cargo = pessoa.DS_CARGO as string;
      comum = {
        nome,
        nomeCompleto: nomeCompleto && nomeCompleto !== nome ? nomeCompleto : null,
        foto: null,
        partido: (pessoa.SG_PARTIDO as string | null) ?? null,
        uf: (pessoa.SG_UF as string | null) ?? null,
        municipio: (pessoa.NM_UE as string | undefined) ?? null,
        cargoLabel: CARGO_LABEL[cargo] ?? cargo,
        situacao: (pessoa.DS_SIT_TOT_TURNO as string | undefined) ?? null,
        anoEleicao: (pessoa.ANO_ELEICAO as string | undefined) ?? null,
        genero: (pessoa.DS_GENERO as string | undefined) ?? null,
        corRaca: (pessoa.DS_COR_RACA as string | undefined) ?? null,
        escolaridade: (pessoa.DS_GRAU_INSTRUCAO as string | undefined) ?? null,
        ocupacao: (pessoa.DS_OCUPACAO as string | undefined) ?? null,
        sancoes: pessoa.sancoesVinculadas,
        candidaturas: pessoa.candidaturas,
      };
    }
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link href="/politicos" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Todos os políticos
      </Link>
      <div className="mt-4 flex items-center gap-4">
        {comum.foto ? (
          <Image
            src={comum.foto}
            alt={comum.nome}
            width={88}
            height={88}
            className="h-22 w-22 rounded-full object-cover ring-2 ring-neutral-200 dark:ring-neutral-800"
            unoptimized
          />
        ) : (
          <div className="flex h-22 w-22 shrink-0 items-center justify-center rounded-full bg-neutral-200 text-2xl font-semibold text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
            {iniciais(comum.nome)}
          </div>
        )}
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{comum.nome}</h1>
          <p className="text-neutral-500">
            {[comum.partido, comum.municipio, comum.uf].filter(Boolean).join(" · ")}
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
          {comum.cargoLabel}
          {comum.situacao ? ` — ${comum.situacao.toLowerCase()}` : ""}
        </span>
      </div>

      {(comum.nomeCompleto ||
        campoValido(comum.genero) ||
        campoValido(comum.corRaca) ||
        campoValido(comum.escolaridade) ||
        campoValido(comum.ocupacao) ||
        comum.anoEleicao) && (
        <dl className="mt-6 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
          {comum.nomeCompleto && (
            <div>
              <dt className="text-neutral-500">Nome completo</dt>
              <dd className="font-medium">{comum.nomeCompleto}</dd>
            </div>
          )}
          {campoValido(comum.genero) && (
            <div>
              <dt className="text-neutral-500">Gênero</dt>
              <dd className="font-medium">{titleCase(comum.genero)}</dd>
            </div>
          )}
          {campoValido(comum.corRaca) && (
            <div>
              <dt className="text-neutral-500">Cor/raça (autodeclarada)</dt>
              <dd className="font-medium">{titleCase(comum.corRaca)}</dd>
            </div>
          )}
          {campoValido(comum.ocupacao) && (
            <div>
              <dt className="text-neutral-500">Ocupação declarada</dt>
              <dd className="font-medium">{titleCase(comum.ocupacao)}</dd>
            </div>
          )}
          {campoValido(comum.escolaridade) && (
            <div>
              <dt className="text-neutral-500">Escolaridade</dt>
              <dd className="font-medium">{titleCase(comum.escolaridade)}</dd>
            </div>
          )}
          {comum.anoEleicao && (
            <div>
              <dt className="text-neutral-500">Eleição</dt>
              <dd className="font-medium">{comum.anoEleicao}</dd>
            </div>
          )}
        </dl>
      )}

      {comum.candidaturas.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Todas as candidaturas no TSE
          </h2>
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {comum.candidaturas.map((c, i) => (
              <li key={i} className="flex items-center justify-between gap-4 px-4 py-3 text-sm">
                <div>
                  <p className="font-medium">
                    {c.ano} — {CARGO_LABEL[c.cargo] ?? titleCase(c.cargo)}
                  </p>
                  <p className="text-neutral-500">
                    {[c.partido, c.municipio, c.uf].filter(Boolean).join(" · ")}
                  </p>
                </div>
                {c.situacao && (
                  <span
                    className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${
                      c.situacao.toUpperCase().includes("ELEITO")
                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                        : "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300"
                    }`}
                  >
                    {titleCase(c.situacao)}
                  </span>
                )}
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400">
            Cruzamento por nome no TSE — inclui candidaturas não eleitas e de qualquer nível
            (federal, estadual, municipal), pode incluir homônimos.
          </p>
        </section>
      )}

      {federal && pessoaFederal && pessoaFederal.totalProposicoes > 0 && (
        <section className="mt-8">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Proposições de autoria
          </h2>
          <p className="mb-3 text-sm text-neutral-600 dark:text-neutral-400">
            <span className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
              {pessoaFederal.totalProposicoes}
            </span>{" "}
            {pessoaFederal.totalProposicoes === 1 ? "proposição de autoria" : "proposições de autoria"} —
            projetos de lei, propostas de emenda, requerimentos e emendas, como autor principal ou coautor,
            incluindo as de legislaturas anteriores.
          </p>
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {pessoaFederal.proposicoesRecentes.map((p, i) => (
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
                <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
                  {p.casa === "Camara" ? "Câmara" : "Senado"} · {formatarData(p.dataApresentacao)}
                </p>
              </li>
            ))}
          </ul>
          {pessoaFederal.totalProposicoes > pessoaFederal.proposicoesRecentes.length && (
            <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400">
              Mostrando as {pessoaFederal.proposicoesRecentes.length} mais recentes de{" "}
              {pessoaFederal.totalProposicoes}.
            </p>
          )}
        </section>
      )}

      {federal &&
        pessoaFederal &&
        (pessoaFederal.legislaturasCamara.length > 0 || pessoaFederal.legislaturasSenado.length > 0) && (
          <section className="mt-8">
            <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
              Histórico de legislaturas
            </h2>
            <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
              {pessoaFederal.legislaturasCamara.map((l) => (
                <li key={`camara-${l.idLegislatura}`} className="px-4 py-3">
                  <p className="font-medium">{l.idLegislatura}ª legislatura (Câmara)</p>
                  <p className="text-sm text-neutral-500">
                    {l.siglaPartido} · {l.siglaUf}
                  </p>
                </li>
              ))}
              {pessoaFederal.legislaturasSenado.map((l) => (
                <li key={`senado-${l.numeroLegislatura}`} className="px-4 py-3">
                  <p className="font-medium">{l.numeroLegislatura}ª legislatura (Senado)</p>
                  <p className="text-sm text-neutral-500">
                    {l.participacao} · {l.siglaUf} · {formatarData(l.dataInicio)} a {formatarData(l.dataFim)}
                  </p>
                </li>
              ))}
            </ul>
          </section>
        )}

      <section className="mt-8">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          Sanções vinculadas ao nome
        </h2>
        {comum.sancoes.length === 0 ? (
          <p className="text-sm text-neutral-500">Nenhuma sanção encontrada com esse nome.</p>
        ) : (
          <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
            {comum.sancoes.map((s) => (
              <li key={s.id} className="px-4 py-3">
                <p className="font-medium">{s.sancionadoNome}</p>
                <p className="text-sm text-neutral-500">
                  {s.tipoSancao} · {s.origemSancao} · {formatarData(s.dataInicioSancao)}
                </p>
              </li>
            ))}
          </ul>
        )}
        <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400">
          Cruzamento por nome — pode incluir homônimos, já que não há um identificador único público
          entre as fontes.
        </p>
      </section>

      {federal && pessoaFederal && (
        <section className="mt-8">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Contratos vinculados ao nome
          </h2>
          {pessoaFederal.contratosVinculados.length === 0 ? (
            <p className="text-sm text-neutral-500">Nenhum contrato encontrado com esse nome.</p>
          ) : (
            <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
              {pessoaFederal.contratosVinculados.map((c, i) => (
                <li key={i} className="px-4 py-3">
                  <p className="font-medium">{c.orgaoNome}</p>
                  <p className="text-sm text-neutral-500 line-clamp-2">{c.objeto}</p>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    {formatarMoeda(c.valor)} · {formatarData(c.data)}
                  </p>
                </li>
              ))}
            </ul>
          )}
          <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400">
            Cruzamento por nome do fornecedor — pode incluir homônimos.
          </p>
        </section>
      )}

      {federal && pessoaFederal && pessoaFederal.senadoId && (
        <section className="mt-8">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
            Votações recentes no Senado
          </h2>
          {pessoaFederal.votacoesRecentes.length === 0 ? (
            <p className="text-sm text-neutral-500">Nenhuma votação recente encontrada.</p>
          ) : (
            <ul className="divide-y divide-neutral-200 rounded-xl border border-neutral-200 dark:divide-neutral-800 dark:border-neutral-800">
              {pessoaFederal.votacoesRecentes.map((v, i) => (
                <li key={i} className="px-4 py-3">
                  <p className="font-medium">
                    {v.materiaSigla} {v.materiaNumero}/{v.materiaAno}
                  </p>
                  <p className="text-sm text-neutral-500">
                    Voto: {v.voto} · Resultado: {v.descricaoResultado} · {formatarData(v.dataSessao)}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}
