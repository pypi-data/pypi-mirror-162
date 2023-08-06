from typing import List, Tuple

from pyspark.sql import Column, DataFrame
import pyspark.sql.functions as F

from aporia.core.types.field import FieldType
from aporia.pyspark.training.pyspark_field_metadata import PySparkFieldMetadata


def _get_keys_of_dict_col(data: DataFrame, col: str) -> List[str]:
    # Inspired by https://mungingdata.com/pyspark/dict-map-to-multiple-columns/
    keys_df = data.select(F.explode(F.map_keys(F.col(col)))).distinct()
    return [row[0] for row in keys_df.collect()]


def expand_dicts_keys_attributes_to_regular_fields(
    data: DataFrame, dict_fields: List[PySparkFieldMetadata]
) -> List[Tuple[PySparkFieldMetadata, Column]]:
    """Expands dict fields to columns in a dataframe.

    Each attribute in the dict key will be expanded to an independent column.

    Args:
        data: the original dataframe
        dict_fields: A list of dict fields to expand

    Returns:
        List of (field metadata, corresponding dataframe column) tuples.
    """
    result: List[Tuple[PySparkFieldMetadata, Column]] = []

    for dict_field in dict_fields:
        keys = _get_keys_of_dict_col(data=data, col=dict_field.column)
        for key in keys:

            col_name = dict_field.column + "." + key

            key_field_metadata = PySparkFieldMetadata(
                column=col_name,
                name=dict_field.name,
                group=dict_field.group,
                type=FieldType.NUMERIC,
                key_at_dict=key,
            )

            col_query = F.col(dict_field.column).getItem(key).alias(col_name)

            result.append((key_field_metadata, col_query))

    return result
