import Link from "next/link";
import { notFound } from "next/navigation";
import { obterSancao } from "@/lib/api";

function formatarData(iso: string | null) {
  if (!iso) return "não informada";
  const [ano, mes, dia] = iso.split("T")[0].split("-");
  return `${dia}/${mes}/${ano}`;
}

function formatarMoeda(valor: number | null) {
  if (valor == null) return null;
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

const EXPLICACAO_ORIGEM: Record<string, string> = {
  CEIS:
    "CEIS é o Cadastro de Empresas Inidôneas e Suspensas. Empresas ou pessoas aqui estão proibidas de firmar novos contratos com o poder público (federal, estadual ou municipal) por um período determinado.",
  CNEP:
    "CNEP é o Cadastro Nacional de Empresas Punidas. Reúne empresas condenadas por atos de corrupção contra a administração pública, com base na Lei Anticorrupção (Lei 12.846/2013).",
};

export default async function SancaoDetalhePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let sancao;
  try {
    sancao = await obterSancao(id);
  } catch {
    notFound();
  }

  const hoje = new Date();
  const fimSancao = sancao.dataFimSancao ? new Date(sancao.dataFimSancao) : null;
  const vigente = !fimSancao || fimSancao > hoje;

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link href="/sancoes" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Todas as sanções
      </Link>

      <div className="mt-4 flex items-start justify-between gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">{sancao.sancionadoNome}</h1>
        <span
          className={`shrink-0 rounded-full border px-3 py-1 text-sm font-medium ${
            vigente
              ? "border-red-300 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-400"
              : "border-neutral-300 text-neutral-600 dark:border-neutral-700 dark:text-neutral-400"
          }`}
        >
          {vigente ? "Sanção vigente" : "Sanção encerrada"}
        </span>
      </div>
      <p className="mt-1 text-sm text-neutral-500">
        {sancao.sancionadoDocumento} · {sancao.origemSancao}
      </p>

      <div className="mt-6 rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700 dark:border-neutral-800 dark:bg-neutral-900/50 dark:text-neutral-300">
        <p className="font-medium">O que significa esta sanção?</p>
        <p className="mt-1">{EXPLICACAO_ORIGEM[sancao.origemSancao]}</p>
      </div>

      <dl className="mt-6 grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-neutral-500">Tipo de penalidade</dt>
          <dd className="font-medium">{sancao.tipoSancao}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Órgão que aplicou a sanção</dt>
          <dd className="font-medium">{sancao.orgaoSancionador ?? "não informado"}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Início da sanção</dt>
          <dd className="font-medium">{formatarData(sancao.dataInicioSancao)}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Fim da sanção</dt>
          <dd className="font-medium">
            {sancao.dataFimSancao ? formatarData(sancao.dataFimSancao) : "por prazo indeterminado"}
          </dd>
        </div>
        {formatarMoeda(sancao.valorMulta) && (
          <div>
            <dt className="text-neutral-500">Valor da multa</dt>
            <dd className="font-medium">{formatarMoeda(sancao.valorMulta)}</dd>
          </div>
        )}
        <div>
          <dt className="text-neutral-500">Fonte oficial</dt>
          <dd className="font-medium">{sancao.fonteSancao}</dd>
        </div>
      </dl>

      <p className="mt-8 text-xs text-neutral-500 dark:text-neutral-400">
        Dados do Portal da Transparência (Cadastros CEIS/CNEP). Esta página lista uma sanção
        aplicada a este CPF/CNPJ — a mesma empresa ou pessoa pode ter outras sanções em nome
        ligeiramente diferente, já que não há um identificador único compartilhado entre todas as
        fontes públicas.
      </p>
    </div>
  );
}
