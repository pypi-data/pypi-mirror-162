import logging
from typing import Dict, List, Optional

from pyspark.sql import DataFrame

from aporia.core.errors import AporiaError
from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.types.field import FieldType
from aporia.pyspark.training.pyspark_field_metadata import PySparkFieldMetadata
from aporia.training.training_validator import TrainingDataType, TrainingValidator
from .pyspark_utils import infer_schema_from_pyspark_dataframe

logger = logging.getLogger(LOGGER_NAME)


class PySparkTrainingValidator(TrainingValidator):
    """PySpark training data validator."""

    def validate_pyspark(
        self,
        features: DataFrame,
        labels: DataFrame,
        predictions: Optional[DataFrame] = None,
        raw_inputs: Optional[DataFrame] = None,
    ):
        """Validates pyspark training dataframes.

        Args:
            features: Features dataframe
            labels: Labels (predictions) dataframe
            predictions: Predictions dataframe
            raw_inputs: Raw inputs dataframe
        """
        for training_data_type, data in [
            (TrainingDataType.FEATURES, features),
            (TrainingDataType.LABELS, labels),
            (TrainingDataType.PREDICTIONS, predictions),
            (TrainingDataType.RAW_INPUTS, raw_inputs),
        ]:
            if data is None:
                continue

            self.validate_field_category_is_in_schema(training_data_type)
            self.validate_no_field_mismatch_in_category(
                columns=data.columns, training_data_type=training_data_type
            )

            self._validate_pyspark_field_types_match_schema(
                training_data_type=training_data_type, data=data
            )

    def _validate_pyspark_field_types_match_schema(
        self, training_data_type: TrainingDataType, data: DataFrame
    ):
        inferred_schema = infer_schema_from_pyspark_dataframe(data)
        if inferred_schema is None:
            raise AporiaError(
                "Validating {} dataframe failed - could not infer the schema of the {} dataframe".format(
                    self.dataset_type.value, training_data_type.value
                )
            )

        field_category = training_data_type.to_field_category()
        missing_fields = self.schema[field_category].keys() - set(data.columns)

        for field_name, field_type in self.schema[field_category].items():
            if field_name in missing_fields:
                continue

            inferred_field_type = FieldType(inferred_schema[field_name])
            # Don't verify boolean fields, since we're going to cast them anyway
            if field_type != FieldType.BOOLEAN and field_type is not inferred_field_type:
                logger.warning(
                    "Detected type mismatch on field {field_name}: expected {expected_type} "
                    "type, got {actual_type}".format(
                        field_name=field_name,
                        expected_type=field_type.value,
                        actual_type=inferred_field_type.value,
                    )
                )

    def validate_all_fields_in_df(self, df: DataFrame, fields: List[PySparkFieldMetadata]):
        """Validates that all the fields exists in the dataframe.

        Args:
            df: Dataframe to check the fields against.
            fields: list of fields metadata to to check in scheme
        """
        inferred_schema = self._infer_df_schema(df)

        for field in fields:

            if field.column not in inferred_schema:
                logger.warning(
                    f"Column {field.column}"
                    f"corresponding to {field.group} field {field.name} "
                    "not found in the dataframe"
                )
                continue

            inferred_field_type = FieldType(inferred_schema[field.column])
            if field.type not in [FieldType.BOOLEAN, inferred_field_type]:
                logger.warning(
                    "Detected type mismatch on field {field_name}: expected {expected_type} "
                    "type, got {actual_type}".format(
                        field_name=field.name,
                        expected_type=field.type.value,
                        actual_type=inferred_field_type.value,
                    )
                )

    def _infer_df_schema(self, df: DataFrame) -> Dict[str, str]:
        inferred_schema = infer_schema_from_pyspark_dataframe(df)
        if inferred_schema is None:
            raise AporiaError(
                "Validating  dataframe failed - could not infer the schema of the dataframe"
            )

        return inferred_schema
