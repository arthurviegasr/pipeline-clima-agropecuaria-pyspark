import json
import os
from datetime import datetime, timezone
from typing import Any
from pyspark.sql import DataFrame
import pyspark.sql.functions as F

COLUNAS_OBRIGATORIAS = [
    "codigo_pais",
    "nome_pais",
    "ano",
    "mes",
    "temp_media_mensal_c",
    "chuva_total_mensal_mm",
    "agro_pct_pib",
]

def validar_e_gerar_relatorio(df: DataFrame, caminho_relatorio: str) -> dict[str, Any]:
    """Test de integridade basica, schema, unicidade da chave e nulos."""
    df.cache()
    try:
        total_linhas = df.count()
        colunas_faltantes = sorted(list(set(COLUNAS_OBRIGATORIAS) - set(df.columns)))
        schema_ok = not colunas_faltantes

        null_ratios: dict[str, float] = {}
        total_unicos = 0
        erros_range = 0

        if total_linhas > 0 and schema_ok:
            null_exprs = [
                (F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)) / F.lit(total_linhas)).alias(c)
                for c in COLUNAS_OBRIGATORIAS
            ]
            res_nulos = df.agg(*null_exprs).collect()[0].asDict()
            null_ratios = {col: round(float(val or 0.0), 4) for col, val in res_nulos.items()}

            total_unicos = df.select("codigo_pais", "ano", "mes").dropDuplicates().count()

            erros_range = df.filter(
                (F.col("mes") < 1) | (F.col("mes") > 12) |
                (F.col("chuva_total_mensal_mm") < 0) |
                (F.col("temp_media_mensal_c") < -90) | (F.col("temp_media_mensal_c") > 60)
            ).count()

        unicidade_ok = (total_linhas == total_unicos) if total_linhas > 0 else False
        intervalo_ok = erros_range == 0
        aprovado = schema_ok and unicidade_ok and intervalo_ok and (total_linhas > 0)

        relatorio: dict[str, Any] = {
            "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
            "status": "APROVADO" if aprovado else "REPROVADO",
            "total_registros": total_linhas,
            "registros_unicos_chave": total_unicos,
            "checks": {
                "schema_ok": schema_ok,
                "colunas_faltantes": colunas_faltantes,
                "unicidade_ok": unicidade_ok,
                "intervalo_ok": intervalo_ok,
                "violacoes_intervalo": erros_range,
            },
            "null_ratio": null_ratios,
        }
        pasta_destino = os.path.dirname(caminho_relatorio)
        if pasta_destino:
            os.makedirs(pasta_destino, exist_ok=True)

        with open(caminho_relatorio, "w", encoding="utf-8") as arquivo:
            json.dump(relatorio, arquivo, indent=2, ensure_ascii=False)

        return relatorio

    finally:
        df.unpersist()