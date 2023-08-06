from __future__ import annotations

from typing import Dict, List, Optional

import pyspark.sql.functions as F
from pyspark.sql import DataFrame


class IdentityFitTransformer:
    '''An identity transform serving as the base class for other fit and transform logic.
    '''

    def __init__(self, input_columns: List[str], params: Optional[dict] = None) -> None:
        self.input_columns = input_columns
        self.params = params

    @property
    def input_output_columns(self) -> Dict[str, str]:
        '''Input and output columns are one-to-one.

        Note: If multiple columns are created from a single input column, pack a StructType into the
        output column.
        '''
        return {c: f'{c}_{type(self).__name__}' for c in self.input_columns}

    def fit(self, df: DataFrame) -> IdentityFitTransformer:
        '''Modify internal state with an input dataframe.
        '''
        return self

    def transform(self, df: DataFrame) -> DataFrame:
        '''Transform dataframe using only internal state, which is not be modified by this method.

        Note: If you need to do some joins with a mapping created from fit(), use a udf instead,
        which works better by not shuffling.
        '''
        for input_column, output_column in self.input_output_columns.items():
            # An identity transformation is still a transformation
            df = df.withColumn(output_column, F.col(input_column)).drop(input_column)
        return df

    def fit_transform(self, df: DataFrame) -> DataFrame:
        return self.fit(df=df).transform(df=df)
