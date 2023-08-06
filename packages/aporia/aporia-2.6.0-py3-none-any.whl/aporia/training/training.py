from typing import Dict, List, Optional

import numpy as np
from pandas import DataFrame, Series

from aporia.core.consts import TRAINING_BIN_COUNT
from aporia.core.errors import AporiaError
from aporia.core.types.field import FieldType
from .api.log_training import FieldTrainingData


def calculate_dataframe_training_data(
    data: DataFrame, fields_schema: Dict[str, FieldType]
) -> List[FieldTrainingData]:
    """Calculates training data for all fields in a DataFrame.

    Args:
        data: Raw training data
        fields_schema: Fields schema for the category that is being calculated.

    Returns:
        Training data for all fields in the dataframe
    """
    training_data = []
    for field_name, field_data in data.items():
        # Ignore fields that are not defined in the model version schema
        if field_name not in fields_schema:
            continue

        training_data.extend(
            calculate_training_data(
                field_name=field_name,
                field_data=field_data,
                field_type=fields_schema[field_name],
            )
        )

    return training_data


def calculate_training_data(
    field_name: str, field_data: Series, field_type: FieldType
) -> List[FieldTrainingData]:
    """Calculates training data for a single field.

    Args:
        field_name: Field name
        field_data: Field data
        field_type: Field type

    Returns:
        Field training data.
    """
    # We currently don't support datetime, vector, text & dict training data
    if field_type in [FieldType.DATETIME, FieldType.VECTOR, FieldType.TEXT]:
        return [
            _calculate_training_data_without_histogram(field_name=field_name, field_data=field_data)
        ]
    elif field_type == FieldType.NUMERIC:
        return [_calculate_numeric_training_data(field_name=field_name, field_data=field_data)]
    elif field_type == FieldType.DICT:
        return _calculate_dict_training_data(field_name=field_name, field_data=field_data)
    elif field_type in [FieldType.BOOLEAN, FieldType.STRING, FieldType.CATEGORICAL]:
        return [
            _calculate_categorical_training_data(
                field_name=field_name, field_data=field_data, field_type=field_type
            )
        ]

    raise AporiaError("Unsupported field type {} of field {}".format(field_type.value, field_name))


def _calculate_dict_training_data(field_name: str, field_data: Series) -> List[FieldTrainingData]:
    # Each row in field_data is expected to be a dict: {"a": 0.5, "b": 0.2}
    # By using .apply(Series), we can expand each key to a column in a dataframe
    expanded_dict_data = field_data.apply(Series)

    training_data = []
    for key, key_data in expanded_dict_data.items():
        training_data.append(
            _calculate_numeric_training_data(field_name=field_name, key=key, field_data=key_data)
        )

    return training_data


def _calculate_training_data_without_histogram(
    field_name: str, field_data: Series
) -> FieldTrainingData:
    valid_values = field_data[field_data.notnull()]

    return FieldTrainingData(
        field_name=field_name,
        num_samples=len(valid_values),
        num_missing_values=len(field_data) - len(valid_values),
    )


def _calculate_categorical_training_data(
    field_name: str, field_data: Series, field_type: FieldType
) -> FieldTrainingData:
    valid_values = field_data[field_data.notnull()]
    if field_type == field_type.BOOLEAN:
        valid_values = valid_values.astype("bool")

    bins, counts = np.unique(valid_values, return_counts=True)

    # Note: There is a possible edge case here in which a user passes an infinite value
    # as one of the categories. We chose not to count those values at the moment, since
    # most numpy functions don't handle str and bool well, which would force us to split
    # this function up for each field type.
    return FieldTrainingData(
        field_name=field_name,
        bins=bins.tolist(),
        counts=counts.tolist(),
        num_samples=len(valid_values),
        num_missing_values=len(field_data) - len(valid_values),
        num_unique_values=len(bins),
    )


def _calculate_numeric_training_data(
    field_name: str, field_data: Series, key: Optional[str] = None
) -> FieldTrainingData:
    # Cast everything to float and normalize null values (some operations don't work on pd.NA)
    field_data = field_data.fillna(np.nan).astype(float)  # type: ignore

    # Filter out infinite and NaN values (isfinite is False for NaN)
    finite_values = field_data[np.isfinite(field_data)]
    counts, bins = np.histogram(finite_values, bins=TRAINING_BIN_COUNT)

    # np.median and np.average print redundant runtime warnings when the data is empty
    median = np.median(finite_values) if finite_values.size > 0 else np.nan
    average = np.average(finite_values) if finite_values.size > 0 else np.nan
    return FieldTrainingData(
        field_name=field_name,
        key=key,
        bins=bins.tolist(),
        counts=counts.tolist(),
        min=np.min(finite_values),
        max=np.max(finite_values),
        sum=np.sum(finite_values),  # type: ignore
        median=median,
        average=average,
        std=np.std(finite_values),  # type: ignore
        variance=np.var(finite_values),  # type: ignore
        num_samples=len(finite_values),
        num_missing_values=np.count_nonzero(np.isnan(field_data)),
        num_posinf_values=np.count_nonzero(np.isposinf(field_data)),
        num_neginf_values=np.count_nonzero(np.isneginf(field_data)),
        num_zero_values=np.count_nonzero(finite_values == 0),
    )
