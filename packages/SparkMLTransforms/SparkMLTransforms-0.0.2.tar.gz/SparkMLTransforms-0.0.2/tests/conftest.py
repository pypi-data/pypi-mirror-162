import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope='package')
def spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()
