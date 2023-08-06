import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pyspark.sql import SparkSession

from SparkMLTransforms.encoder import CategoricalToIntegerEncoder


@pytest.mark.parametrize(
    ('input_df', 'expected_df'),
    [
        pytest.param(
            pd.DataFrame({'a': [0, 1, 2, 3]}),
            pd.DataFrame({'a_CategoricalToIntegerEncoder': [0, 1, 2, 3]}),
            id='identity'
        ),
    ]
)
def test_CategoricalToIntegerEncoder(spark: SparkSession, input_df: pd.DataFrame, expected_df: pd.DataFrame):
    input_df = spark.createDataFrame(input_df)
    output_df = CategoricalToIntegerEncoder(input_columns=['a']).fit_transform(input_df)
    output_df = output_df.toPandas()
    assert_frame_equal(output_df, expected_df)
