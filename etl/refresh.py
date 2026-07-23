"""
Orquestra a re-coleta de todas as fontes e reconstrói o warehouse, num só
comando. Cada fonte roda isoladamente — se uma falhar (fonte fora do ar,
mudança de schema, chave de API ausente), as demais continuam normalmente.

Uso: poetry run python -m etl.refresh
"""

import logging
import time

log = logging.getLogger(__name__)

# (nome, função collect_all) — todas seguem a mesma convenção de retorno
# {recurso: total_coletado}. TSE e SICONFI só re-coletam o ano/exercício
# "atual" configurado no módulo; anos históricos já coletados não precisam
# ser re-buscados a cada refresh (ver PROJETO_STATUS.md).
def _coletores():
    from modules.bacen_tracker.collector import collect_all as bacen
    from modules.camara_tracker.collector import collect_all as camara
    from modules.compras_tracker.collector import collect_all as compras
    from modules.datajud_tracker.collector import collect_all as datajud
    from modules.ibge_tracker.collector import collect_all as ibge
    from modules.senado_tracker.collector import collect_all as senado
    from modules.siconfi_tracker.collector import collect_all as siconfi
    from modules.transparencia_tracker.collector import collect_all as transparencia
    from modules.tse_tracker.collector import collect_all as tse

    return [
        ("camara", camara),
        ("senado", senado),
        ("bacen", bacen),
        ("siconfi", siconfi),
        ("ibge", ibge),
        ("tse", tse),
        ("compras", compras),
        ("datajud", datajud),
        ("transparencia", transparencia),
    ]


def refresh_fontes() -> dict:
    """Roda o collect_all de cada módulo, tolerando falha individual."""
    resultado: dict[str, dict] = {}
    for nome, coletar in _coletores():
        inicio = time.time()
        try:
            resultado[nome] = {"ok": True, "detalhe": coletar(), "duracao_s": round(time.time() - inicio, 1)}
        except Exception as e:  # qualquer fonte pode falhar sem derrubar as outras
            log.warning(f"[refresh] {nome} falhou: {e}")
            resultado[nome] = {"ok": False, "erro": str(e), "duracao_s": round(time.time() - inicio, 1)}
    return resultado


def refresh_tudo() -> tuple[dict, dict]:
    """Re-coleta todas as fontes e reconstrói o warehouse. Retorna (fontes, tabelas)."""
    from etl.build_warehouse import build

    fontes = refresh_fontes()
    tabelas = build()
    return fontes, tabelas


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    print("\n🔄 Refresh — Re-coletando todas as fontes e reconstruindo o warehouse")
    print("─" * 60)

    fontes, tabelas = refresh_tudo()

    print("\n── Fontes ──")
    for nome, r in fontes.items():
        status = "✅" if r["ok"] else "❌"
        extra = r["detalhe"] if r["ok"] else r["erro"]
        print(f"  {status} {nome} ({r['duracao_s']}s): {extra}")

    print("\n── Tabelas do warehouse ──")
    for tabela, total in tabelas.items():
        print(f"  {'✅' if total > 0 else '⚠️ '} {tabela}: {total} registros")

    falhas = [nome for nome, r in fontes.items() if not r["ok"]]
    if falhas:
        print(f"\n⚠️  Fontes que falharam nesta rodada: {', '.join(falhas)} — dado anterior dessas fontes foi mantido.")
    print("\nConcluído.")
