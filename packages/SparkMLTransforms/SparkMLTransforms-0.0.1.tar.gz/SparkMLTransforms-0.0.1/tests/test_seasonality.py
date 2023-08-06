from datetime import datetime

import pandas as pd
from pyspark.sql import SparkSession

from SparkMLTransforms.seasonality import FourierFeatures
from SparkMLTransforms.utils import unpack_structtype_column


def test_FourierFeatures(spark: SparkSession):
    input_df = pd.DataFrame({'dt': [datetime(2000, 1, 1)]})
    input_df = spark.createDataFrame(input_df)

    params = {
        'week_of_year': False,
        'day_of_month': False,
        'day_of_week': True,
        'hour_of_day': False,
        'minute_of_hour': False,
        # limits the number of output columns to check
        'use_period_fraction': 1. / 7.,
    }
    output_df = FourierFeatures(input_columns=['dt'], params=params).fit_transform(input_df)
    output_df = unpack_structtype_column(output_df, 'dt_FourierFeatures')
    assert output_df.columns == [
        'dt_FourierFeatures_day_of_week_sine_phase_0',
        'dt_FourierFeatures_day_of_week_cos_phase_0'
    ]
