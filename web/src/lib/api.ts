const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Pessoa = {
  slug: string;
  nome: string;
  nome_normalizado?: string;
  casa: string;
  camaraId?: number | null;
  camaraPartido?: string | null;
  camaraUf?: string | null;
  camaraFoto?: string | null;
  senadoId?: string | null;
  senadoPartido?: string | null;
  senadoUf?: string | null;
  senadoFoto?: string | null;
};

export type PessoaDetalhe = Pessoa & {
  sancoesVinculadas: Sancao[];
  votacoesRecentes: Votacao[];
};

export type Sancao = {
  id: number;
  sancionadoNome: string;
  sancionadoDocumento: string;
  tipoSancao: string;
  orgaoSancionador: string | null;
  fonteSancao: string;
  dataInicioSancao: string | null;
  dataFimSancao: string | null;
  valorMulta: number | null;
  origemSancao: "CEIS" | "CNEP";
};

export type Contrato = {
  fonte: string;
  orgaoNome: string;
  orgaoDocumento: string | null;
  uf: string | null;
  objeto: string;
  modalidade: string | null;
  valor: number | null;
  data: string | null;
  situacao: string | null;
  fornecedorNome?: string | null;
  fornecedorDocumento?: string | null;
};

export type Votacao = {
  codigoSenador: string;
  descricaoVotacao: string;
  descricaoResultado: string;
  voto: string;
  materiaSigla: string | null;
  materiaNumero: string | null;
  materiaAno: string | null;
  dataSessao: string | null;
};

export type OrgaoSiafi = { codigo: string; descricao: string };

export type PoliticoMunicipal = {
  SQ_CANDIDATO: string;
  NM_CANDIDATO: string;
  NM_URNA_CANDIDATO: string;
  SG_PARTIDO: string;
  SG_UF: string;
  NM_UE: string;
  DS_CARGO: string;
  DS_SIT_TOT_TURNO: string;
};

export type PoliticoMunicipalDetalhe = PoliticoMunicipal & {
  DS_GENERO?: string;
  DS_OCUPACAO?: string;
  DS_GRAU_INSTRUCAO?: string;
  ANO_ELEICAO?: string;
  sancoesVinculadas: Sancao[];
};

export type BuscaResultado = {
  termo: string;
  pessoas: Pessoa[];
  sancoes: Pick<Sancao, "id" | "sancionadoNome" | "tipoSancao" | "origemSancao">[];
  contratos: Pick<Contrato, "fonte" | "orgaoNome" | "fornecedorNome" | "objeto" | "valor">[];
  orgaos: OrgaoSiafi[];
  total: number;
};

async function apiFetch<T>(path: string, revalidateSeconds = 300): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    next: { revalidate: revalidateSeconds },
  });
  if (!res.ok) {
    throw new Error(`API ${path} respondeu ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function buscar(q: string): Promise<BuscaResultado> {
  return apiFetch(`/busca?q=${encodeURIComponent(q)}`, 0);
}

export function listarPessoas(params: {
  nome?: string;
  casa?: string;
  partido?: string;
  uf?: string;
  limit?: number;
  offset?: number;
}): Promise<Pessoa[]> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/pessoas?${qs.toString()}`, 0);
}

export function obterPessoa(slug: string): Promise<PessoaDetalhe> {
  return apiFetch(`/pessoas/${encodeURIComponent(slug)}`);
}

export function listarSancoes(params: { nome?: string } = {}): Promise<Sancao[]> {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => !!v) as [string, string][]
  );
  return apiFetch(`/sancoes?${qs.toString()}`);
}

export function listarContratos(params: { orgao?: string; fornecedor?: string } = {}): Promise<Contrato[]> {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => !!v) as [string, string][]
  );
  return apiFetch(`/contratos?${qs.toString()}`);
}

export function listarPoliticosMunicipais(params: {
  uf?: string;
  municipio?: string;
  cargo?: string;
  nome?: string;
  limit?: number;
  offset?: number;
}): Promise<PoliticoMunicipal[]> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/municipais/politicos?${qs.toString()}`, 0);
}

export function obterPoliticoMunicipal(sqCandidato: string): Promise<PoliticoMunicipalDetalhe> {
  return apiFetch(`/municipais/politicos/${encodeURIComponent(sqCandidato)}`);
}

export const UFS = [
  "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT",
  "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
];
