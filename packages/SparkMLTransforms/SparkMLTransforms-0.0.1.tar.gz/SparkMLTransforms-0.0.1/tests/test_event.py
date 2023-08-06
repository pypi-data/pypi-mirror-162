from datetime import datetime

import pandas as pd
from pyspark.sql import SparkSession

from SparkMLTransforms.event import HolidayFeatures
from SparkMLTransforms.utils import unpack_structtype_column


def test_HolidayFeatures(spark: SparkSession):
    input_df = pd.DataFrame({'dt': [datetime(2022, 1, 1)]})
    input_df = spark.createDataFrame(input_df)

    params = {
        'years': [2021, 2022, 2023],
        'country': 'US'
    }
    output_df = HolidayFeatures(input_columns=['dt'], params=params).fit_transform(input_df)
    output_df = unpack_structtype_column(output_df, 'dt_HolidayFeatures')
    assert output_df.columns == [
        'dt_HolidayFeatures_us_holiday_days_since_last',
        'dt_HolidayFeatures_us_holiday_days_to_next'
    ]
