import pyspark.sql.functions as F
from pyspark.sql import DataFrame


def unpack_structtype_column(df: DataFrame, column: str) -> DataFrame:
    for sub_c in df.select(f'{column}.*').columns:
        df = df.withColumn(f'{column}_{sub_c}', F.col(f'{column}.{sub_c}'))
    return df.drop(column)
