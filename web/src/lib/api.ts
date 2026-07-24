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

export type LegislaturaCamara = {
  idLegislatura: number;
  siglaPartido: string | null;
  siglaUf: string | null;
};

export type LegislaturaSenado = {
  numeroLegislatura: number;
  dataInicio: string | null;
  dataFim: string | null;
  siglaUf: string | null;
  participacao: string | null;
};

export type ProposicaoLegislativa = {
  casa: "Camara" | "Senado";
  tipoSigla: string;
  numero: string;
  ano: string;
  ementa: string | null;
  dataApresentacao: string | null;
  url: string;
};

export type ProposicaoDetalhe = ProposicaoLegislativa & {
  autorId: string | null;
  totalAutores: number;
  autoresIds: string[];
};

export type Candidatura = {
  ano: string;
  cargo: string;
  uf: string | null;
  municipio: string | null;
  partido: string | null;
  situacao: string | null;
};

export type PessoaDetalhe = Pessoa & {
  genero?: string | null;
  corRaca?: string | null;
  escolaridade?: string | null;
  ocupacao?: string | null;
  sancoesVinculadas: Sancao[];
  contratosVinculados: Contrato[];
  votacoesRecentes: Votacao[];
  legislaturasCamara: LegislaturaCamara[];
  legislaturasSenado: LegislaturaSenado[];
  totalProposicoes: number;
  proposicoesRecentes: ProposicaoLegislativa[];
  candidaturas: Candidatura[];
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
  id?: string;
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

export type Nivel = "federal" | "nacional" | "estadual" | "municipal";

export type TipoCargo = { nivel: Nivel; cargo: string; label: string };

export type PoliticoCargo = {
  id: string;
  nivel: Nivel;
  cargo: string;
  nome: string;
  nome_urna?: string | null;
  partido?: string | null;
  uf?: string | null;
  municipio?: string | null;
  foto?: string | null;
  ano?: string | null;
};

export type PoliticoCargoDetalhe = Record<string, unknown> & {
  nivel: Nivel;
  sancoesVinculadas: Sancao[];
  candidaturas: Candidatura[];
};

export type Paginated<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
};

export type BuscaResultado = {
  termo: string;
  pessoas: Pessoa[];
  sancoes: Pick<Sancao, "id" | "sancionadoNome" | "tipoSancao" | "origemSancao">[];
  contratos: Pick<Contrato, "id" | "fonte" | "orgaoNome" | "fornecedorNome" | "objeto" | "valor">[];
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

export function obterPessoa(slug: string): Promise<PessoaDetalhe> {
  return apiFetch(`/pessoas/${encodeURIComponent(slug)}`, 0);
}

export function listarSancoes(
  params: { nome?: string; origem?: string; limit?: number; offset?: number } = {}
): Promise<Paginated<Sancao>> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/sancoes?${qs.toString()}`, 0);
}

export function listarContratos(
  params: { orgao?: string; fornecedor?: string; uf?: string; limit?: number; offset?: number } = {}
): Promise<Paginated<Contrato>> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/contratos?${qs.toString()}`, 0);
}

export function obterSancao(id: number | string): Promise<Sancao> {
  return apiFetch(`/sancoes/${encodeURIComponent(id)}`, 0);
}

export function obterContrato(id: string): Promise<Contrato> {
  return apiFetch(`/contratos/${encodeURIComponent(id)}`, 0);
}

export function listarTiposDeCargo(): Promise<TipoCargo[]> {
  return apiFetch(`/cargos/tipos`);
}

export async function listarAnosDisponiveis(nivel: Nivel): Promise<number[]> {
  const { anos } = await apiFetch<{ anos: number[] }>(`/cargos/anos?nivel=${nivel}`);
  return anos;
}

export function listarPoliticosCargo(params: {
  nivel: Nivel;
  cargo?: string;
  uf?: string;
  municipio?: string;
  nome?: string;
  ano?: number;
  limit?: number;
  offset?: number;
}): Promise<Paginated<PoliticoCargo>> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/cargos/politicos?${qs.toString()}`, 0);
}

export function obterPoliticoCargo(nivel: Nivel, id: string): Promise<PoliticoCargoDetalhe> {
  return apiFetch(`/cargos/politicos/${nivel}/${encodeURIComponent(id)}`);
}

export type SerieEconomica = {
  data: string;
  valor: number;
  serie: string;
  codigoSgs: number;
};

export type IndicadorUf = {
  recurso: string;
  variavel: string;
  unidade: string | null;
  localidadeId: string;
  localidadeNome: string;
  periodo: number;
  valor: number;
};

export function listarSeriesEconomicas(serie?: string): Promise<SerieEconomica[]> {
  const qs = serie ? `?serie=${encodeURIComponent(serie)}` : "";
  return apiFetch(`/economia/series${qs}`);
}

export function listarIndicadoresUf(recurso?: string): Promise<IndicadorUf[]> {
  const qs = recurso ? `?recurso=${encodeURIComponent(recurso)}` : "";
  return apiFetch(`/indicadores/uf${qs}`);
}

export type ContaBalanco = {
  exercicio: number;
  siglaEnte: string;
  cod_ibge: number;
  uf: string;
  cod_conta: string;
  conta: string;
  valor: number;
  populacao: number;
};

export function listarBalanco(siglaEnte: string, limit = 20): Promise<ContaBalanco[]> {
  return apiFetch(`/financas/balanco?sigla_ente=${encodeURIComponent(siglaEnte)}&limit=${limit}`);
}

export type VotacaoSenado = {
  dataSessao: string | null;
  materiaSigla: string | null;
  materiaNumero: string | null;
  materiaAno: string | null;
  materiaEmenta: string | null;
  descricaoVotacao: string;
  descricaoResultado: string;
  voto: string;
  senadorNome: string | null;
  senadorPartido: string | null;
  senadorUf: string | null;
};

export type VotoDetalhe = {
  voto: string;
  senadorNome: string | null;
  senadorPartido: string | null;
  senadorUf: string | null;
};

export type VotacaoDetalhe = {
  dataSessao: string | null;
  materiaSigla: string | null;
  materiaNumero: string | null;
  materiaAno: string | null;
  materiaEmenta: string | null;
  descricaoVotacao: string;
  descricaoResultado: string;
  votacaoSecreta: string | null;
  votos: VotoDetalhe[];
  contagemVotos: Record<string, number>;
};

export function obterDetalheVotacaoSenado(params: {
  dataSessao: string;
  materiaSigla: string;
  materiaNumero: string;
  materiaAno: string;
  descricaoVotacao: string;
}): Promise<VotacaoDetalhe> {
  const qs = new URLSearchParams(params);
  return apiFetch(`/legislativo/senado/votacoes/detalhe?${qs.toString()}`, 0);
}

export function listarVotacoesSenado(
  params: {
    senador?: string;
    uf?: string;
    materiaSigla?: string;
    resultado?: string;
    limit?: number;
    offset?: number;
  } = {}
): Promise<Paginated<VotacaoSenado>> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/legislativo/senado/votacoes?${qs.toString()}`, 0);
}

export type ProcessoJudicial = {
  id: string;
  tribunal: string;
  grau: string | null;
  numeroProcesso: string;
  dataAjuizamento: string | null;
  classeNome: string | null;
  orgaoJulgadorNome: string | null;
  dataUltimaAtualizacao: string | null;
};

export type TribunalContagem = { tribunal: string; total: number };

export function listarProcessosJudiciais(
  params: { tribunal?: string; classe?: string; limit?: number; offset?: number } = {}
): Promise<Paginated<ProcessoJudicial>> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/judicial/processos?${qs.toString()}`, 0);
}

export function listarTribunaisDisponiveis(): Promise<TribunalContagem[]> {
  return apiFetch(`/judicial/tribunais`, 0);
}

export function obterProcessoJudicial(id: string): Promise<ProcessoJudicial> {
  return apiFetch(`/judicial/processos/${encodeURIComponent(id)}`, 0);
}

export type ProcessoSenado = {
  id: string;
  identificacao: string | null;
  tipoDocumento: string | null;
  tipoConteudo: string | null;
  ementa: string | null;
  autoria: string | null;
  situacaoAtual: string | null;
  tramitando: string | null;
  dataApresentacao: string | null;
  dataSituacaoAtual: string | null;
  dataUltimaAtualizacao: string | null;
  urlDocumento: string | null;
};

export function listarProcessosSenado(
  params: { tramitando?: string; limit?: number } = {}
): Promise<ProcessoSenado[]> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/legislativo/senado/processos?${qs.toString()}`, 0);
}

export function obterProcessoSenado(id: string): Promise<ProcessoSenado> {
  return apiFetch(`/legislativo/senado/processos/${encodeURIComponent(id)}`, 0);
}

export type Orgao = { codigo: string; descricao: string };

export type OrgaoDetalhe = Orgao & {
  contratosVinculados: Contrato[];
  sancoesVinculadas: Sancao[];
};

export function listarOrgaos(
  params: { nome?: string; limit?: number; offset?: number } = {}
): Promise<Paginated<Orgao>> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/orgaos?${qs.toString()}`, 0);
}

export function obterOrgao(codigo: string): Promise<OrgaoDetalhe> {
  return apiFetch(`/orgaos/${encodeURIComponent(codigo)}`, 0);
}

export type TipoProposicao = { tipoSigla: string; total: number };

export function listarTiposProposicao(): Promise<TipoProposicao[]> {
  return apiFetch(`/proposicoes/tipos`, 0);
}

export function listarProposicoes(
  params: {
    casa?: string;
    tipoSigla?: string;
    ano?: number;
    q?: string;
    limit?: number;
    offset?: number;
  } = {}
): Promise<Paginated<ProposicaoLegislativa>> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/proposicoes?${qs.toString()}`, 0);
}

export function obterProposicao(url: string): Promise<ProposicaoDetalhe> {
  return apiFetch(`/proposicoes/detalhe?url=${encodeURIComponent(url)}`, 0);
}

export type EnteFederativo = {
  cod_ibge: number;
  ente: string;
  uf: string;
  regiao: string;
  esfera: string;
  exercicio: number;
  populacao: number | null;
  cnpj: string | null;
};

export function listarEntesFederativos(
  params: { uf?: string; esfera?: string; limit?: number } = {}
): Promise<EnteFederativo[]> {
  const qs = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== "")
      .map(([k, v]) => [k, String(v)])
  );
  return apiFetch(`/financas/entes?${qs.toString()}`, 0);
}

export const UFS = [
  "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT",
  "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
];
