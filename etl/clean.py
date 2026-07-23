"""
Funções de limpeza/normalização por fonte: tipagem de datas e valores,
achatamento de campos aninhados e padronização de nomes de coluna.

Cada função recebe o DataFrame bruto (como veio do snapshot) e devolve
um DataFrame "staging" pronto para virar tabela no warehouse.
"""

import pandas as pd

from .utils import corrigir_dupla_codificacao, extrair_campo, normalizar_nome, somente_digitos


def limpar_camara_deputados(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df[["id", "nome", "siglaPartido", "siglaUf", "email", "urlFoto", "idLegislatura"]].copy()
    out["nome_normalizado"] = out["nome"].map(normalizar_nome)
    return out


def limpar_camara_legislaturas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df[["id", "nome", "siglaPartido", "siglaUf", "idLegislatura"]].copy()
    out = out.drop_duplicates(subset=["id", "idLegislatura", "siglaPartido"])
    return out


def limpar_senado_legislaturas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df[[
        "id", "nome", "nomeCompleto", "siglaUf",
        "numeroLegislatura", "dataInicio", "dataFim", "participacao",
    ]].copy()
    out["numeroLegislatura"] = pd.to_numeric(out["numeroLegislatura"], errors="coerce").astype("Int64")
    out["dataInicio"] = pd.to_datetime(out["dataInicio"], errors="coerce")
    out["dataFim"] = pd.to_datetime(out["dataFim"], errors="coerce")
    out = out.drop_duplicates(subset=["id", "numeroLegislatura"])
    return out


def limpar_senado_senadores(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df[[
        "id", "nome", "nomeCompleto", "sexo", "siglaPartido", "siglaUf",
        "email", "urlFoto", "urlPagina", "bloco", "membroMesa", "membroLideranca",
        "descricaoParticipacao",
    ]].copy()
    out["nome_normalizado"] = out["nome"].map(normalizar_nome)
    return out


def limpar_senado_processos(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df[[
        "id", "identificacao", "tipoDocumento", "tipoConteudo", "ementa", "autoria",
        "situacaoAtual", "tramitando", "dataApresentacao", "dataSituacaoAtual",
        "dataUltimaAtualizacao", "urlDocumento",
    ]].copy()
    out["dataApresentacao"] = pd.to_datetime(out["dataApresentacao"], errors="coerce")
    out["dataSituacaoAtual"] = pd.to_datetime(out["dataSituacaoAtual"], errors="coerce")
    return out


def limpar_senado_votacoes(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    materia = df["Materia"]
    sessao = df["SessaoPlenaria"]
    out = pd.DataFrame({
        "codigoSenador": df["_codigoSenador"],
        "sequencial": df["Sequencial"],
        "descricaoVotacao": df["DescricaoVotacao"],
        "descricaoResultado": df["DescricaoResultado"],
        "voto": df["SiglaDescricaoVoto"],
        "votacaoSecreta": df["IndicadorVotacaoSecreta"],
        "materiaSigla": extrair_campo(materia, "Sigla"),
        "materiaNumero": extrair_campo(materia, "Numero"),
        "materiaAno": extrair_campo(materia, "Ano"),
        "materiaEmenta": extrair_campo(materia, "Ementa"),
        "dataSessao": extrair_campo(sessao, "DataSessao"),
    })
    out["dataSessao"] = pd.to_datetime(out["dataSessao"], errors="coerce")
    return out


def limpar_bacen_series(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["data"] = pd.to_datetime(out["data"], format="%d/%m/%Y", errors="coerce")
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce")
    return out


def limpar_siconfi_entes(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df[["cod_ibge", "ente", "uf", "regiao", "esfera", "exercicio", "populacao", "cnpj"]].copy()


def limpar_siconfi_dca(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.rename(columns={"_siglaEnte": "siglaEnte"})
    out = out[["exercicio", "siglaEnte", "cod_ibge", "uf", "cod_conta", "conta", "valor", "populacao"]].copy()
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce")
    return out


def limpar_ibge_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce")
    out["periodo"] = pd.to_numeric(out["periodo"], errors="coerce").astype("Int64")
    return out


def limpar_tse_candidatos(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    colunas = [
        "SQ_CANDIDATO", "NR_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO",
        "SG_PARTIDO", "SG_UF", "NM_UE", "DS_CARGO", "DS_SITUACAO_CANDIDATURA",
        "DS_SIT_TOT_TURNO", "DS_GENERO", "DS_COR_RACA", "DS_GRAU_INSTRUCAO",
        "DS_OCUPACAO", "ANO_ELEICAO",
    ]
    out = df[colunas].copy()
    out["nome_normalizado"] = out["NM_CANDIDATO"].map(normalizar_nome)
    return out


def limpar_compras_contratacoes(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df[[
        "idCompra", "numeroControlePNCP", "orgaoEntidadeRazaoSocial", "orgaoEntidadeCnpj",
        "unidadeOrgaoUfSigla", "unidadeOrgaoMunicipioNome", "modalidadeNome",
        "objetoCompra", "valorTotalEstimado", "valorTotalHomologado",
        "dataPublicacaoPncp", "situacaoCompraNomePncp",
    ]].copy()
    out["dataPublicacaoPncp"] = pd.to_datetime(out["dataPublicacaoPncp"], errors="coerce")
    out["valorTotalEstimado"] = pd.to_numeric(out["valorTotalEstimado"], errors="coerce")
    out["valorTotalHomologado"] = pd.to_numeric(out["valorTotalHomologado"], errors="coerce")
    out["orgaoEntidadeCnpjDigitos"] = out["orgaoEntidadeCnpj"].map(somente_digitos)
    return out


def limpar_datajud_processos(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = pd.DataFrame({
        "id": df["id"],
        "tribunal": df["_tribunalSigla"],
        "grau": df["grau"],
        "numeroProcesso": df["numeroProcesso"],
        "dataAjuizamento": pd.to_datetime(df["dataAjuizamento"], format="%Y%m%d%H%M%S", errors="coerce"),
        "classeNome": extrair_campo(df["classe"], "nome").map(corrigir_dupla_codificacao),
        "orgaoJulgadorNome": extrair_campo(df["orgaoJulgador"], "nome").map(corrigir_dupla_codificacao),
        "dataUltimaAtualizacao": pd.to_datetime(df["dataHoraUltimaAtualizacao"], errors="coerce", utc=True),
    })
    return out


def limpar_transparencia_sancoes(df: pd.DataFrame) -> pd.DataFrame:
    """Comum a CEIS e CNEP — ambos têm a mesma estrutura de sancionado/fonteSancao/tipoSancao."""
    if df.empty:
        return df
    out = pd.DataFrame({
        "id": df["id"],
        "sancionadoNome": extrair_campo(df["sancionado"], "nome"),
        "sancionadoDocumento": extrair_campo(df["sancionado"], "codigoFormatado"),
        "tipoSancao": df["tipoSancao"].apply(lambda d: (d or {}).get("descricaoResumida")),
        "orgaoSancionador": extrair_campo(df["orgaoSancionador"], "nome") if "orgaoSancionador" in df.columns else None,
        "fonteSancao": extrair_campo(df["fonteSancao"], "nomeExibicao"),
        "dataInicioSancao": pd.to_datetime(df["dataInicioSancao"], format="%d/%m/%Y", errors="coerce"),
        "dataFimSancao": pd.to_datetime(df["dataFimSancao"], format="%d/%m/%Y", errors="coerce"),
        "valorMulta": pd.to_numeric(df["valorMulta"], errors="coerce") if "valorMulta" in df.columns else None,
    })
    out["sancionadoDocumentoDigitos"] = out["sancionadoDocumento"].map(somente_digitos)
    return out


def limpar_transparencia_contratos(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = pd.DataFrame({
        "id": df["id"],
        "numero": df["numero"],
        "objeto": df["objeto"],
        "orgaoNome": df["_orgaoNome"],
        "fornecedorNome": extrair_campo(df["fornecedor"], "nome"),
        "fornecedorDocumento": df["fornecedor"].apply(
            lambda d: (d or {}).get("cnpjFormatado") or (d or {}).get("cpfFormatado")
        ),
        "situacaoContrato": df["situacaoContrato"],
        "dataAssinatura": pd.to_datetime(df["dataAssinatura"], format="%d/%m/%Y", errors="coerce"),
        "dataInicioVigencia": pd.to_datetime(df["dataInicioVigencia"], format="%d/%m/%Y", errors="coerce"),
        "dataFimVigencia": pd.to_datetime(df["dataFimVigencia"], format="%d/%m/%Y", errors="coerce"),
        "valorInicialCompra": pd.to_numeric(df["valorInicialCompra"], errors="coerce"),
        "valorFinalCompra": pd.to_numeric(df["valorFinalCompra"], errors="coerce"),
    })
    out["fornecedorDocumentoDigitos"] = out["fornecedorDocumento"].map(somente_digitos)
    return out


def limpar_transparencia_orgaos(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df.copy()
