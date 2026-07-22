"""
Camada de ETL do Câmara Analytics.

Lê os snapshots brutos coletados pelos módulos `*_tracker` em `data/raw/`,
limpa e normaliza cada fonte, cruza o que é possível entre elas, e grava
tudo em um banco DuckDB único (`data/warehouse/camara_analytics.duckdb`)
pronto para ser consumido por uma API/frontend.
"""
