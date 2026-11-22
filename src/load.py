import os
import shutil
import pyarrow as pa
import pyarrow.parquet as pq
from pyspark.sql import DataFrame


def salvar_parquet_particionado(df: DataFrame, output_dir: str) -> None:
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    df_pandas = df.toPandas()
    
    tabela = pa.Table.from_pandas(df_pandas, preserve_index=False)

    pq.write_to_dataset(
        tabela,
        root_path=output_dir,
        partition_cols=["ano", "mes"],
        compression="snappy",
    )