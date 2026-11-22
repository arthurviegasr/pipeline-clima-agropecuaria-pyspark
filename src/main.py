from src.config import TOP_30_PAISES, get_config
from src.extract import extrair_clima_open_meteo, extrair_pib_world_bank
from src.load import salvar_parquet_particionado
from src.quality import validar_e_gerar_relatorio
from src.transform import criar_sessao_spark, transformar_dados


def main() -> None:
    config = get_config()
    ano_ini = int(config.start_date[:4])
    ano_fim = int(config.end_date[:4])
    paises_iso3 = [p["iso3"] for p in TOP_30_PAISES]

    print("[1/4] Início da Extração de dados das APIs (World Bank e Open-Meteo)...")
    dados_wb = extrair_pib_world_bank(paises_iso3, config.wb_indicator, ano_ini, ano_fim, config)
    dados_clima = extrair_clima_open_meteo(TOP_30_PAISES, config)

    print("[2/4] Processando e relacionando os dados com PySpark...")
    spark = criar_sessao_spark()
    try:
        df_final = transformar_dados(spark, dados_wb, dados_clima, config.wb_indicator)

        print("[3/4] Validações de dados - Data Quality...")
        relatorio = validar_e_gerar_relatorio(df_final, config.quality_report_path)
        print(f"-> Status: {relatorio['status']} | Total de registros: {relatorio['total_registros']}")

        if relatorio["status"] != "APROVADO":
            raise RuntimeError(f"Pipeline sem aprovação no teste de qualidade. Detalhes em: {config.quality_report_path}")

        print(f"[4/4] Gravação do dataset Parquet particionado em: {config.output_dir}")
        salvar_parquet_particionado(df_final, config.output_dir)
        print("O Pipeline foi concluído com sucesso!")
    finally:
        spark.stop()
        
if __name__ == "__main__":
    main()