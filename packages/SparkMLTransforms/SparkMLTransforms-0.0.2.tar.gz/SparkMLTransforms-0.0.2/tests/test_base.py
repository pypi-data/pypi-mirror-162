import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pyspark.sql import SparkSession

from SparkMLTransforms.base import IdentityFitTransformer


@pytest.mark.parametrize(
    ('input_df', 'expected_df'),
    [
        pytest.param(
            pd.DataFrame({'a': [1, 2, 3]}),
            pd.DataFrame({'a_IdentityFitTransformer': [1, 2, 3]}),
            id='integer'
        ),
    ]
)
def test_IdentityFitTransformer(spark: SparkSession, input_df: pd.DataFrame, expected_df: pd.DataFrame):
    input_df = spark.createDataFrame(input_df)
    output_df = IdentityFitTransformer(input_columns=['a']).fit_transform(input_df)
    output_df = output_df.toPandas()
    assert_frame_equal(output_df, expected_df)
