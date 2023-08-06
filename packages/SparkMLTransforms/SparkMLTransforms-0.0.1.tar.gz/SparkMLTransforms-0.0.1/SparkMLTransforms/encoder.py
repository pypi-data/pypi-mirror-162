from __future__ import annotations

from typing import List, Optional

import pyspark.sql.functions as F
from pyspark.sql import DataFrame

from SparkMLTransforms.base import IdentityFitTransformer


class CategoricalToIntegerEncoder(IdentityFitTransformer):

    def __init__(self, input_columns: List[str], params: Optional[dict] = None) -> None:
        if params is not None:
            raise ValueError('Not expecting any values for params but received {params}.')
        self.input_columns = input_columns
        self.params = params
        self.unique_values = {c: [] for c in input_columns}

    def fit(self, df: DataFrame) -> CategoricalToIntegerEncoder:
        for c in self.input_columns:
            df_unique_values = [row[c] for row in df.select(c).distinct().collect()]
            new_unique_values = [
                v for v in df_unique_values
                if v is not None and v not in self.unique_values[c]
            ]
            self.unique_values[c] += sorted(new_unique_values)
        return self

    def transform(self, df: DataFrame) -> DataFrame:
        for c in self.input_columns:
            mapping = {c: i for i, c in enumerate(self.unique_values[c])}
            print(c, mapping)
            udf = F.udf(lambda s: mapping.get(s), 'long')
            df = df.withColumn(self.input_output_columns[c], udf(c)).drop(c)
        return df
