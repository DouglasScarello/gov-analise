"""
Tabelas unificadas: cruzam registros de fontes diferentes que representam
a mesma entidade do mundo real (pessoa, empresa, contrato).

O cruzamento usa nome normalizado (câmara/senado) ou documento (CPF/CNPJ,
apenas dígitos) quando disponível — não há um ID único global entre as
fontes do governo brasileiro, então essa é a melhor chave possível hoje.
"""

import pandas as pd


def unificar_pessoas_politicas(deputados: pd.DataFrame, senadores: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por político (câmara e/ou senado), casando por nome normalizado."""
    dep = pd.DataFrame()
    if not deputados.empty:
        dep = pd.DataFrame({
            "nome_normalizado": deputados["nome_normalizado"],
            "nome": deputados["nome"],
            "camaraId": deputados["id"],
            "camaraPartido": deputados["siglaPartido"],
            "camaraUf": deputados["siglaUf"],
            "camaraFoto": deputados["urlFoto"],
        })

    sen = pd.DataFrame()
    if not senadores.empty:
        sen = pd.DataFrame({
            "nome_normalizado": senadores["nome_normalizado"],
            "nome": senadores["nome"],
            "senadoId": senadores["id"],
            "senadoPartido": senadores["siglaPartido"],
            "senadoUf": senadores["siglaUf"],
            "senadoFoto": senadores["urlFoto"],
        })

    if dep.empty and sen.empty:
        return pd.DataFrame()
    if dep.empty:
        out = sen.copy()
    elif sen.empty:
        out = dep.copy()
    else:
        out = pd.merge(dep, sen, on="nome_normalizado", how="outer", suffixes=("", "_sen"))
        out["nome"] = out["nome"].fillna(out.pop("nome_sen"))

    out["casa"] = out.apply(
        lambda r: "Câmara e Senado" if pd.notna(r.get("camaraId")) and pd.notna(r.get("senadoId"))
        else ("Câmara" if pd.notna(r.get("camaraId")) else "Senado"),
        axis=1,
    )
    out["slug"] = out["nome_normalizado"].str.lower().str.replace(" ", "-", regex=False)
    return out.reset_index(drop=True)


def unificar_entidades_sancionadas(ceis: pd.DataFrame, cnep: pd.DataFrame) -> pd.DataFrame:
    """União de CEIS + CNEP, cada linha é uma sanção (uma entidade pode aparecer várias vezes)."""
    partes = []
    if not ceis.empty:
        c = ceis.copy()
        c["origemSancao"] = "CEIS"
        partes.append(c)
    if not cnep.empty:
        c = cnep.copy()
        c["origemSancao"] = "CNEP"
        partes.append(c)
    if not partes:
        return pd.DataFrame()
    return pd.concat(partes, ignore_index=True)


def unificar_contratos_publicos(compras: pd.DataFrame, transparencia: pd.DataFrame) -> pd.DataFrame:
    """União de contratações do Compras.gov.br (PNCP) + contratos do Portal da Transparência,
    com colunas padronizadas para consulta única."""
    partes = []

    if not compras.empty:
        partes.append(pd.DataFrame({
            "fonte": "compras.gov.br",
            "orgaoNome": compras["orgaoEntidadeRazaoSocial"],
            "orgaoDocumento": compras["orgaoEntidadeCnpjDigitos"],
            "uf": compras["unidadeOrgaoUfSigla"],
            "objeto": compras["objetoCompra"],
            "modalidade": compras["modalidadeNome"],
            "valor": compras["valorTotalHomologado"].fillna(compras["valorTotalEstimado"]),
            "data": compras["dataPublicacaoPncp"],
            "situacao": compras["situacaoCompraNomePncp"],
        }))

    if not transparencia.empty:
        partes.append(pd.DataFrame({
            "fonte": "portaldatransparencia.gov.br",
            "orgaoNome": transparencia["orgaoNome"],
            "orgaoDocumento": None,
            "uf": None,
            "objeto": transparencia["objeto"],
            "modalidade": None,
            "valor": transparencia["valorFinalCompra"].fillna(transparencia["valorInicialCompra"]),
            "data": transparencia["dataAssinatura"],
            "situacao": transparencia["situacaoContrato"],
            "fornecedorNome": transparencia["fornecedorNome"],
            "fornecedorDocumento": transparencia["fornecedorDocumentoDigitos"],
        }))

    if not partes:
        return pd.DataFrame()
    return pd.concat(partes, ignore_index=True)
