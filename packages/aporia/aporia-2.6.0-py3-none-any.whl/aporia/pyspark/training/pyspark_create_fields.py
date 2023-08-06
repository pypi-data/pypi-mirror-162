from typing import List, Mapping, Optional

from aporia.core.types.field import FieldType
from aporia.pyspark.training.pyspark_field_metadata import PySparkFieldMetadata


def create_fields_metadata(
    field_category: str,
    schema: Mapping[str, FieldType],
    schema_to_columns_mapping: Optional[Mapping[str, str]] = None,
) -> List[PySparkFieldMetadata]:
    """A function that prepate the input for the pyspark traning data aggreator.

    Args:
        field_category: The category we create fields for (e.g raw_inputs predicitons)
        schema: The schema configured for that category
        schema_to_columns_mapping: optional mappig of df columns names ot be used instead of schema names

    Returns:
        a list of PySparkFieldMetadata. which the traning data aggreagtor know how to work with
    """
    result = []
    for field_schema_name, field_value_type in schema.items():
        field_column_name = field_schema_name
        if schema_to_columns_mapping is not None:
            field_column_name = schema_to_columns_mapping.get(field_schema_name, field_schema_name)
        result.append(
            PySparkFieldMetadata(
                name=field_schema_name,
                type=field_value_type,
                group=field_category,
                column=field_column_name,
            )
        )
    return result
