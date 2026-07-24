"""
Busca única, tipo "Google": um termo, resultados de todas as tabelas.
"""

from fastapi import APIRouter, Query

from ..db import CONTRATO_HASH_ID, query

router = APIRouter(tags=["busca"])


@router.get("/busca")
def busca_unificada(q: str = Query(..., min_length=2), limit: int = Query(10, le=50)):
    termo = f"%{q}%"

    pessoas = query(
        """
        SELECT slug, nome, casa, camaraPartido, senadoPartido, camaraUf, senadoUf
        FROM pessoas_politicas WHERE nome ILIKE ? LIMIT ?
        """,
        [termo, limit],
    )
    sancoes = query(
        """
        SELECT id, sancionadoNome, tipoSancao, origemSancao
        FROM entidades_sancionadas WHERE sancionadoNome ILIKE ? LIMIT ?
        """,
        [termo, limit],
    )
    contratos = query(
        f"""
        SELECT fonte, orgaoNome, fornecedorNome, objeto, valor, {CONTRATO_HASH_ID}
        FROM contratos_publicos
        WHERE orgaoNome ILIKE ? OR fornecedorNome ILIKE ? OR objeto ILIKE ?
        LIMIT ?
        """,
        [termo, termo, termo, limit],
    )
    orgaos = query(
        "SELECT codigo, descricao FROM stg_transparencia_orgaos_siafi WHERE descricao ILIKE ? LIMIT ?",
        [termo, limit],
    )

    return {
        "termo": q,
        "pessoas": pessoas,
        "sancoes": sancoes,
        "contratos": contratos,
        "orgaos": orgaos,
        "total": len(pessoas) + len(sancoes) + len(contratos) + len(orgaos),
    }
