from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from pyspark.sql.types import DoubleType, StructField, StructType
from stpd.fourier import Fourier

from SparkMLTransforms.base import IdentityFitTransformer


class FourierFeatures(IdentityFitTransformer):

    def __init__(self, input_columns: List[str], params: Optional[dict] = None) -> None:
        self.input_columns = input_columns
        self.f = Fourier(**params)

    def transform(self, df: DataFrame):
        for c in self.input_columns:
            sample_output_value = self.f(datetime(2000, 1, 1))
            mapping = {
                row[c]: self.f(row[c])
                for row in df.select(c).distinct().collect()
            }
            udf_return_schema = StructType([
                StructField(k, DoubleType(), False)
                for k in sample_output_value
            ])
            udf = F.udf(lambda v: mapping.get(v), udf_return_schema)
            df = df.withColumn(self.input_output_columns[c], udf(c)).drop(c)
        return df
