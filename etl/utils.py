"""
Helpers compartilhados pela camada de ETL.
"""

import unicodedata

import pandas as pd


def normalizar_nome(nome) -> str:
    """Maiúsculas, sem acento, espaços colapsados — chave de cruzamento entre fontes."""
    if not isinstance(nome, str) or not nome.strip():
        return ""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    return " ".join(sem_acento.upper().split())


def somente_digitos(valor) -> str:
    """Extrai apenas os dígitos de um CPF/CNPJ formatado (ex: '42.146.902/0009-38')."""
    if not isinstance(valor, str):
        return ""
    return "".join(c for c in valor if c.isdigit())


def extrair_campo(serie: pd.Series, chave: str):
    """De uma coluna de dicts (ou None), extrai o valor de `chave` em cada linha."""
    return serie.apply(lambda d: d.get(chave) if isinstance(d, dict) else None)


def corrigir_dupla_codificacao(texto):
    """Corrige texto UTF-8 codificado duas vezes (bug visto em alguns tribunais do
    DataJud, ex: 'PRESIDÃŠNCIA' → 'PRESIDÊNCIA'). Round-trip seguro: só aplica a
    correção quando o resultado é decodificável, senão mantém o texto original."""
    if not isinstance(texto, str) or not texto:
        return texto
    try:
        return texto.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return texto
