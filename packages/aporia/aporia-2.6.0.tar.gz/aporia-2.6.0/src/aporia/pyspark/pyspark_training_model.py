import logging
from typing import Mapping, Optional

from pyspark.sql import DataFrame

from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.types.field import FieldCategory
from aporia.pyspark.pyspark_training import calculate_dataframe_training_data
from aporia.pyspark.pyspark_training_validator import PySparkTrainingValidator
from aporia.pyspark.training.pyspark_calculate_fields import calculate_training_fields
from aporia.pyspark.training.pyspark_create_fields import create_fields_metadata
from aporia.training.training_model import TrainingModel
from aporia.training.training_validator import TrainingDataset

logger = logging.getLogger(LOGGER_NAME)


class PySparkTrainingModel:
    """PySpark training model."""

    def __init__(self, training_model: TrainingModel):
        """Initializes a PySparkTrainingModel.

        Args:
            training_model: A training model object, which will be used to report training data.
        """
        self._training_model = training_model

    def log_pyspark_training_set(
        self,
        data: DataFrame,
        features_schema_df_mapping: Optional[Mapping[str, str]] = None,
        predictions_schema_df_mapping: Optional[Mapping[str, str]] = None,
        raw_inputs_schema_df_mapping: Optional[Mapping[str, str]] = None,
    ) -> None:
        """See aporia.model.Model."""
        logger.debug("Logging pyspark training set.")
        with self._training_model.handle_error("Logging pyspark training set failed, error: {}"):
            version_schema = self._training_model.get_version_schema()

            validator = PySparkTrainingValidator(
                dataset_type=TrainingDataset.TRAINING, schema=version_schema
            )

            fields_metadata = []
            if FieldCategory.PREDICTIONS in version_schema:
                fields_metadata.extend(
                    create_fields_metadata(
                        field_category="labels",
                        schema=version_schema[FieldCategory.PREDICTIONS],
                        schema_to_columns_mapping=predictions_schema_df_mapping,
                    )
                )

            if FieldCategory.FEATURES in version_schema:
                fields_metadata.extend(
                    create_fields_metadata(
                        field_category="features",
                        schema=version_schema[FieldCategory.FEATURES],
                        schema_to_columns_mapping=features_schema_df_mapping,
                    )
                )

            if FieldCategory.RAW_INPUTS in version_schema:
                fields_metadata.extend(
                    create_fields_metadata(
                        field_category="raw_inputs",
                        schema=version_schema[FieldCategory.RAW_INPUTS],
                        schema_to_columns_mapping=raw_inputs_schema_df_mapping,
                    )
                )

            validator.validate_all_fields_in_df(data, fields_metadata)
            training_data = calculate_training_fields(data=data, fields=fields_metadata)

            return self._training_model.log_training_set_aggregations(
                features=training_data["features"],
                labels=training_data["labels"],
                raw_inputs=training_data.get("raw_inputs", None),
            )

    def log_pyspark_test_set(
        self,
        features: DataFrame,
        predictions: DataFrame,
        labels: DataFrame,
        raw_inputs: Optional[DataFrame] = None,
    ):
        """See aporia.model.Model."""
        logger.debug("Logging pyspark test set.")
        with self._training_model.handle_error("Logging test set failed, error: {}"):
            version_schema = self._training_model.get_version_schema()
            validator = PySparkTrainingValidator(
                dataset_type=TrainingDataset.TEST, schema=version_schema
            )
            validator.validate_pyspark(
                features=features, labels=labels, predictions=predictions, raw_inputs=raw_inputs
            )

            raw_inputs_training_data = None
            if raw_inputs is not None:
                raw_inputs_training_data = calculate_dataframe_training_data(
                    raw_inputs, version_schema[FieldCategory.RAW_INPUTS]
                )

            self._training_model.log_test_set_aggregations(
                features=calculate_dataframe_training_data(
                    features, version_schema[FieldCategory.FEATURES]
                ),
                predictions=calculate_dataframe_training_data(
                    predictions, version_schema[FieldCategory.PREDICTIONS]
                ),
                labels=calculate_dataframe_training_data(
                    labels, version_schema[FieldCategory.PREDICTIONS]
                ),
                raw_inputs=raw_inputs_training_data,
            )
