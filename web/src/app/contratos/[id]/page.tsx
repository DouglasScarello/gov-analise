import Link from "next/link";
import { notFound } from "next/navigation";
import { obterContrato } from "@/lib/api";

function formatarData(iso: string | null) {
  if (!iso) return "data não informada";
  const [ano, mes, dia] = iso.split("T")[0].split("-");
  return `${dia}/${mes}/${ano}`;
}

function formatarMoeda(valor: number | null) {
  if (valor == null) return "valor não informado";
  return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

const EXPLICACAO_FONTE: Record<string, string> = {
  "compras.gov.br":
    "Registrado no Compras.gov.br / PNCP (Portal Nacional de Contratações Públicas) — o sistema oficial onde órgãos federais publicam suas compras e licitações.",
  "portaldatransparencia.gov.br":
    "Registrado no Portal da Transparência do Governo Federal, com os gastos diretos de órgãos e entidades federais.",
};

export default async function ContratoDetalhePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let contrato;
  try {
    contrato = await obterContrato(id);
  } catch {
    notFound();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link href="/contratos" className="text-sm text-neutral-500 hover:text-blue-600">
        ← Todos os contratos
      </Link>

      <h1 className="mt-4 text-2xl font-semibold tracking-tight">{contrato.orgaoNome}</h1>
      <p className="mt-1 text-neutral-500">{contrato.uf ? `${contrato.uf} · ` : ""}{contrato.fonte}</p>

      <div className="mt-6 rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700 dark:border-neutral-800 dark:bg-neutral-900/50 dark:text-neutral-300">
        <p className="font-medium">O que foi contratado?</p>
        <p className="mt-1">{contrato.objeto}</p>
      </div>

      <dl className="mt-6 grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-neutral-500">Valor do contrato</dt>
          <dd className="font-medium">{formatarMoeda(contrato.valor)}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Data</dt>
          <dd className="font-medium">{formatarData(contrato.data)}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Fornecedor</dt>
          <dd className="font-medium">{contrato.fornecedorNome ?? "não informado"}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Modalidade</dt>
          <dd className="font-medium">{contrato.modalidade ?? "não informada"}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Situação</dt>
          <dd className="font-medium">{contrato.situacao ?? "não informada"}</dd>
        </div>
        <div>
          <dt className="text-neutral-500">Órgão (CNPJ)</dt>
          <dd className="font-medium">{contrato.orgaoDocumento ?? "não informado"}</dd>
        </div>
      </dl>

      <p className="mt-8 text-xs text-neutral-500 dark:text-neutral-400">
        {EXPLICACAO_FONTE[contrato.fonte] ?? `Fonte: ${contrato.fonte}.`} Este identificador é
        gerado a partir dos dados do próprio contrato (não existe um número de contrato único
        compartilhado entre as fontes oficiais).
      </p>
    </div>
  );
}
