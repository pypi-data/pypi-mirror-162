import logging
from typing import Any, Dict, List, Sequence, Tuple

from pyspark.sql import Column, DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import DoubleType, IntegerType

from aporia.core.errors import AporiaError
from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.types.field import FieldType
from aporia.pyspark.training.pyspark_aggregation_alias import (
    create_alias,
    parse_aggregation_results_to_field_training_data_by_group,
)
from aporia.pyspark.training.pyspark_field_metadata import PySparkFieldMetadata
from aporia.pyspark.training.utils import expand_dicts_keys_attributes_to_regular_fields
from aporia.training.api.log_training import FieldTrainingData

logger = logging.getLogger(LOGGER_NAME)


def get_positive_infinity() -> Column:
    """Returns pyspark positive infinity."""
    return F.lit("+Infinity").cast("double")


def get_negative_infinity() -> Column:
    """Returns pyspark negative infinity."""
    return F.lit("-Infinity").cast("double")


def percentile_approximate_accuracy() -> Column:
    """Returns pyspark proximity."""
    return F.lit(100000)


TRAINING_BIN_COUNT = 50
HISTOGRAMABLE_TYPES = [
    FieldType.NUMERIC,
    FieldType.BOOLEAN,
    FieldType.STRING,
    FieldType.CATEGORICAL,
]

NOT_A_DICT_KEY = "NOT_A_DICT_KEY"


class _TrainingAggregatorPySpark:
    def __init__(self, data: DataFrame, fields: List[PySparkFieldMetadata]):
        """Initializes the training aggregator.

        Args:
            data: Data to compute training aggregations on
            fields: Field metadata
        """
        # Cache the dataframe to improve performance
        self.initial_data_cached = data.cache()
        # Enrich the dataframe by expanding dict fields
        (normalized_data, normalized_fields) = self._normalize_dict_fields(df=data, fields=fields)
        self.data = normalized_data
        self.fields = normalized_fields
        # Cache the modified dataframe to improve performance
        self.data.cache()

    def __del__(self):
        """Clean the cached dataframe from the init step."""
        self.initial_data_cached.unpersist()
        self.data.unpersist()

    def aggregate_training_fields(self) -> Dict[str, List[FieldTrainingData]]:
        """This function gets list of fields and calculate the training aggregations from them."""
        aggregation_columns = self._generate_all_aggregations(self.fields)
        aggregations_by_alias = dict()
        for agg_col in aggregation_columns:
            logger.info("aggregating col:")
            logger.info(agg_col)
            agg = self.data.select(agg_col).collect()[0].asDict()
            aggregations_by_alias.update(agg)
        logger.info("done with aggregation that are not histogram")

        aggregations_by_alias.update(self._compute_group_histograms_array(self.data, self.fields))

        fields_training_data_by_group = parse_aggregation_results_to_field_training_data_by_group(
            aggregations_by_alias
        )

        return fields_training_data_by_group

    def _normalize_dict_fields(
        self, df: DataFrame, fields: List[PySparkFieldMetadata]
    ) -> Tuple[DataFrame, List[PySparkFieldMetadata]]:
        dict_type_fields = [field for field in fields if field.type is FieldType.DICT]

        field_metadata_and_column_pairs = expand_dicts_keys_attributes_to_regular_fields(
            df, dict_type_fields
        )

        # add the keys of the dict field to the dataframe
        dict_keys_cols = [col for _, col in field_metadata_and_column_pairs]
        all_cols = [F.col(col) for col in df.columns] + dict_keys_cols
        # add the fields metadata for each dict field.
        fields_with_expanded_dicts = [
            *[field for field in fields if field.type is not FieldType.DICT],
            *[field_metadata for field_metadata, _ in field_metadata_and_column_pairs],
        ]

        return (df.select(all_cols), fields_with_expanded_dicts)

    def _get_column_valid_values(self, column: Column) -> Column:
        return F.when(
            condition=(self._get_numeric_valid_condition(column)),
            value=column,
        )

    def _get_numeric_valid_condition(self, column: Column) -> Column:
        return (
            ~F.isnan(column)
            & ~column.isNull()
            & ~column.isin([get_positive_infinity(), get_negative_infinity()])
        )

    def _calculate_histogram(
        self, data: DataFrame, field: PySparkFieldMetadata
    ) -> Tuple[Sequence[Any], List[int]]:
        logger.debug("Generating histogram aggregations for:" f"{field}")

        if field.type is FieldType.NUMERIC:
            bins, counts = (
                data.select(field.column)
                .replace([float("inf"), float("-inf")], None)
                .rdd.flatMap(lambda x: x)
                .histogram(TRAINING_BIN_COUNT)
            )

        elif field.type in [FieldType.BOOLEAN, FieldType.STRING, FieldType.CATEGORICAL]:
            distinct_values = (
                data.select(field.column)
                .replace([float("inf"), float("-inf")], None)
                .dropna()
                .groupBy(field.column)
                .count()
                .orderBy(F.col("count").desc())
                .orderBy(field.column)
            )

            bins = []
            counts = []
            for row in distinct_values.collect():
                bins.append(row[field.column])
                counts.append(row["count"])

        else:
            raise AporiaError(f"Unsupported data type {field.type} of column {field.column}")

        return bins, counts

    def _compute_group_histograms_array(
        self, data: DataFrame, fields: List[PySparkFieldMetadata]
    ) -> dict:
        result: Dict[str, Any] = {}
        for field in fields:
            if field.type in HISTOGRAMABLE_TYPES:
                bins, counts = self._calculate_histogram(data=data, field=field)
                result[create_alias("bins", field)] = bins
                result[create_alias("counts", field)] = counts
                if field.type is FieldType.BOOLEAN:
                    result[create_alias("num_unique_values", field)] = len(bins)

        return result

    def _generate_all_aggregations(self, fields: List[PySparkFieldMetadata]) -> List[Column]:
        result: List[Column] = []
        for field in fields:
            result.extend(self._generate_column_aggregations(field))
        return result

    def _generate_column_aggregations(self, field: PySparkFieldMetadata) -> List[Column]:
        logger.debug("Generating aggregations for:" f"{field}")
        if field.type in [FieldType.DATETIME, FieldType.VECTOR, FieldType.TEXT]:
            return self._aggregate_any_column(field)
        elif field.type == FieldType.NUMERIC:
            return self._aggregate_numeric_column(field)
        elif field.type == FieldType.BOOLEAN:
            return self._aggregate_boolean_column(field)
        elif field.type in [FieldType.STRING, FieldType.CATEGORICAL]:
            return self._aggregate_categorical_column(field)

        raise AporiaError(f"Unsupported field type {field.type} of column {field.column}")

    def _aggregate_numeric_column(self, field: PySparkFieldMetadata) -> List[Column]:
        column = field.column
        valid_values = self._get_column_valid_values(F.col(column))

        return [
            F.max(valid_values).alias(create_alias("max", field)),
            F.min(valid_values).alias(create_alias("min", field)),
            F.sum(valid_values).alias(create_alias("sum", field)),
            F.avg(valid_values).alias(create_alias("average", field)),
            F.stddev(valid_values).alias(create_alias("std", field)),
            F.variance(valid_values).alias(create_alias("variance", field)),
            F.count(valid_values).alias(create_alias("num_samples", field)),
            F.count(F.when(F.col(column) == 0, column)).alias(
                create_alias("num_zero_values", field)
            ),
            F.percentile_approx(valid_values, 0.5, percentile_approximate_accuracy()).alias(
                create_alias("median", field)
            ),
            F.count(F.when(F.isnan(column) | F.col(column).isNull(), column)).alias(
                create_alias("num_missing_values", field)
            ),
            F.count(F.when(F.col(column) == (get_positive_infinity()), column)).alias(
                create_alias("num_posinf_values", field)
            ),
            F.count(F.when(F.col(column) == get_negative_infinity(), column)).alias(
                create_alias("num_neginf_values", field)
            ),
        ]

    def _aggregate_boolean_column(self, field: PySparkFieldMetadata) -> List[Column]:
        all_values = F.col(field.column)
        colType = self.data.schema[field.column].dataType
        isNumricCol = isinstance(colType, DoubleType) or isinstance(colType, IntegerType)

        valid_condition = ~all_values.isNull()
        if isNumricCol:
            valid_condition = self._get_numeric_valid_condition(all_values)

        unvalid_values = F.when(F.col(field.column).isNull(), field.column)
        if isNumricCol:
            unvalid_values = F.when(condition=~valid_condition, value=field.column)

        valid_values = F.when(condition=valid_condition, value=all_values)
        return [
            F.count(valid_values).alias(create_alias("num_samples", field)),
            F.count(unvalid_values).alias(create_alias("num_missing_values", field)),
        ]

    def _aggregate_categorical_column(self, field: PySparkFieldMetadata) -> List[Column]:
        column = field.column
        valid_values = self._get_column_valid_values(F.col(column))

        return [
            F.count(valid_values).alias(create_alias("num_samples", field)),
            F.approx_count_distinct(valid_values).alias(create_alias("num_unique_values", field)),
            F.count(F.when(F.isnan(column) | F.col(column).isNull(), column)).alias(
                create_alias("num_missing_values", field)
            ),
        ]

    def _aggregate_any_column(self, field: PySparkFieldMetadata) -> List[Column]:
        column = field.column
        all_values = F.col(field.column)
        valid_condition = ~all_values.isNull()

        valid_values = F.when(condition=valid_condition, value=all_values)
        return [
            F.count(valid_values).alias(create_alias("num_samples", field)),
            F.count(F.when(F.col(column).isNull(), column)).alias(
                create_alias("num_missing_values", field)
            ),
        ]


def calculate_training_fields(
    data: DataFrame, fields: List[PySparkFieldMetadata]
) -> Dict[str, List[FieldTrainingData]]:
    """Calculates training aggregations on columns in a pyspark dataframe.

    Args:
        data: The dataframe representing the training data
        fields: A list of fields meta data that will be used to calculate the aggregations.

    Returns:
        the aggregation results grouped by the field groups
    """
    aggregator = _TrainingAggregatorPySpark(data=data, fields=fields)
    return aggregator.aggregate_training_fields()
