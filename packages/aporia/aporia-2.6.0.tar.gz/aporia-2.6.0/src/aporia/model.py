from typing import Any, Mapping, Optional, Union

from aporia.core.errors import AporiaError
from aporia.inference.inference_model import InferenceModel

try:
    import numpy
    import pandas

    import aporia.training
    from aporia.training.training_model import SAMPLE_SIZE

    ndarray = numpy.ndarray
    DataFrame = pandas.DataFrame
    TRAINING_ENABLED = True

except ImportError:
    ndarray = Any  # type: ignore
    DataFrame = Any
    TRAINING_ENABLED = False
    SAMPLE_SIZE = 1000

try:
    import numpy
    import pandas
    import pyspark.sql

    import aporia.pyspark

    PySparkDataFrame = pyspark.sql.DataFrame
    PYSPARK_ENABLED = True

except ImportError:
    PySparkDataFrame = Any  # type: ignore
    PYSPARK_ENABLED = False


class Model(InferenceModel):
    """Model object for logging model events."""

    def __init__(self, model_id: str, model_version: str):
        """Initializes a model object.

        Args:
            model_id: Model identifier, as received from the Aporia dashboard.
            model_version: Model version - this can be any string that represents the model
                version, such as "v1" or a git commit hash.
        """
        super().__init__(model_id=model_id, model_version=model_version)

        self._training = None
        if TRAINING_ENABLED:
            self._training = aporia.training.TrainingModel(
                model_id=model_id, model_version=model_version
            )

        self._pyspark_inference = None
        if PYSPARK_ENABLED:
            self._pyspark_inference = aporia.pyspark.PySparkInferenceModel(inference_model=self)

        self._pyspark_training = None
        if PYSPARK_ENABLED and self._training is not None:
            self._pyspark_training = aporia.pyspark.PySparkTrainingModel(
                training_model=self._training
            )

    def __getstate__(self) -> dict:
        """Returns picklable representation of the Model object."""
        return {
            "model_id": self.model_id,
            "model_version": self.model_version,
        }

    def __setstate__(self, state: dict):
        """Loads Model object from pickled state.

        Args:
            state: Pickled state
        """
        self.__init__(  # type: ignore
            model_id=state["model_id"],
            model_version=state["model_version"],
        )

    def log_training_set(
        self,
        features: Union[DataFrame, ndarray],  # type: ignore
        labels: Optional[DataFrame] = None,  # type: ignore
        raw_inputs: Optional[DataFrame] = None,  # type: ignore
        log_sample: bool = True,
        sample_size: int = SAMPLE_SIZE,
    ):
        """Logs aggregations of the whole set and logs a sample of the data.

        Args:
            features: Training set features
            labels: Training set labels
            raw_inputs: Training set raw inputs.
            log_sample: Whether to log a sample of the data.
            sample_size: Number of records to sample.

        Notes:
            * Each dataframe corresponds to a field category defined in create_model_version:
                * features -> features
                * labels -> predictions
                * raw_inputs -> raw_inputs
            * Each column in the dataframe should match a field defined in create_model_version
                * Missing fields will be handled as missing values
                * Columns that do not match a defined field will be ignored
                * The column name must match the field name
            * This function is blocking and may take a while to finish running.
        """
        with self.handle_error("{}"):
            if self._training is None:
                raise AporiaError(
                    short_message="Logging training data failed, Aporia training extension not found",
                    verbose_message=(
                        "The Aporia training extension is required to log training data. "
                        "Install it with `pip install aporia[training] and try again."
                    ),
                )

            self._training.log_training_set(
                features=features,
                labels=labels,
                raw_inputs=raw_inputs,
                log_sample=log_sample,
                sample_size=sample_size,
            )

    def log_training_sample(
        self,
        features: Union[DataFrame, ndarray],  # type: ignore
        labels: DataFrame,  # type: ignore
        raw_inputs: Optional[DataFrame] = None,  # type: ignore
        sample_size: int = SAMPLE_SIZE,
    ):
        """Logs a sample of the training data.

        Args:
            features: Training set features
            labels: Training set labels
            raw_inputs: Training set raw_inputs
            sample_size: Number of records to sample

        Notes:
            * Each dataframe corresponds to a field category defined in create_model_version:
                * features -> features
                * labels -> predictions
            * Each column in the dataframe should match a field defined in create_model_version
                * Missing fields will be handled as missing values
                * Columns that do not match a defined field will be ignored
                * The column name must match the field name
            * This function is blocking and may take a while to finish running.
        """
        with self.handle_error("{}"):
            if self._training is None:
                raise AporiaError(
                    short_message="Logging training samples failed, Aporia training extension not found",
                    verbose_message=(
                        "The Aporia training extension is required to log training samples. "
                        "Install it with `pip install aporia[training] and try again."
                    ),
                )

            self._training.log_training_data(
                features=features, labels=labels, raw_inputs=raw_inputs, sample_size=sample_size
            )

    def log_test_set(
        self,
        features: Union[DataFrame, ndarray],  # type: ignore
        predictions: DataFrame,  # type: ignore
        labels: DataFrame,  # type: ignore
        raw_inputs: Optional[DataFrame] = None,  # type: ignore
        confidences: Optional[ndarray] = None,  # type: ignore
    ):
        """Logs test data.

        Args:
            features: Test set features
            predictions: Test set predictions
            labels: Test set labels
            raw_inputs: Test set raw inputs.
            confidences: Confidence values for the test predictions.

        Notes:
            * Each dataframe corresponds to a field category defined in create_model_version:
                * features -> features
                * predictions -> predictions
                * labels -> predictions
                * raw_inputs -> raw_inputs
            * Each column in the dataframe should match a field defined in create_model_version
                * Missing fields will be handled as missing values
                * Columns that do not match a defined field will be ignored
                * The column name must match the field name
            * This function is blocking and may take a while to finish running.
        """
        with self.handle_error("{}"):
            if self._training is None:
                raise AporiaError(
                    short_message="Logging test data failed, Aporia training extension not found",
                    verbose_message=(
                        "The Aporia training extension is required to log test data. "
                        "Install it with `pip install aporia[training] and try again."
                    ),
                )

            self._training.log_test_set(
                features=features,
                predictions=predictions,
                labels=labels,
                raw_inputs=raw_inputs,
                confidences=confidences,
            )

    def log_batch_pyspark_raw_inputs(
        self,
        ids: PySparkDataFrame,  # type: ignore
        raw_inputs: PySparkDataFrame,  # type: ignore
    ):
        """Logs raw inputs of multiple predictions.

        Args:
            ids: Prediction identifiers
            raw_inputs: Raw inputs of each prediction

        Notes:
            * The ids dataframe must contain exactly one column
            * The ids and raw_inputs dataframes must have the same number of rows
        """
        with self.handle_error("{}"):
            if self._pyspark_inference is None:
                raise AporiaError(
                    short_message="Logging pyspark raw inputs failed, Aporia pyspark extension not found",
                    verbose_message=(
                        "The Aporia pyspark extension is required to log raw inputs from pyspark "
                        "dataframes. Install it with `pip install aporia[pyspark] and try again."
                    ),
                )

            self._pyspark_inference.log_batch_pyspark_raw_inputs(ids=ids, raw_inputs=raw_inputs)

    def log_batch_pyspark_actuals(
        self,
        ids: PySparkDataFrame,  # type: ignore
        actuals: PySparkDataFrame,  # type: ignore
    ):
        """Logs actual values of multiple predictions.

        Args:
            ids: Prediction identifiers
            actuals: Actual prediction results of each prediction

        Notes:
            * The ids dataframe must contain exactly one column
            * The ids and actuals dataframes must have the same number of rows
        """
        with self.handle_error("{}"):
            if self._pyspark_inference is None:
                raise AporiaError(
                    short_message="Logging pyspark actuals failed, Aporia pyspark extension not found",
                    verbose_message=(
                        "The Aporia pyspark extension is required to log actuals from pyspark "
                        "dataframes. Install it with `pip install aporia[pyspark] and try again."
                    ),
                )

            self._pyspark_inference.log_batch_pyspark_actuals(ids=ids, actuals=actuals)

    def log_batch_pyspark_prediction(
        self,
        data: PySparkDataFrame,
        id_column: Optional[str] = None,
        timestamp_column: Optional[str] = None,
        features: Optional[Mapping[str, str]] = None,
        predictions: Optional[Mapping[str, str]] = None,
        raw_inputs: Optional[Mapping[str, str]] = None,
        labels: Optional[Mapping[str, str]] = None,
        spark_options: Optional[Mapping[str, str]] = None,
    ):
        """Logs multiple predictions.

        Args:
            data: PsSpark dataframe
            id_column: Optional dataframe column to use as an id.
            timestamp_column: Optional dataframe column to use as an id.
            features: A mapping of feature names (from the schema) to dataframe columns
            predictions: A mapping of predictions names (from the schema) to dataframe columns
            raw_inputs: A mapping of raw input names (from the schema) to dataframe columns
            labels: A mapping of label names (from the schema) to dataframe columns
            spark_options: Optional configuration extension for spark elastic connector. See
                https://www.elastic.co/guide/en/elasticsearch/hadoop/master/configuration.html
        """
        with self.handle_error("{}"):
            if self._pyspark_inference is None:
                raise AporiaError(
                    short_message="Logging pyspark predictions failed, Aporia pyspark extension not found",
                    verbose_message=(
                        "The Aporia pyspark extension is required to log predictions from pyspark "
                        "dataframes. Install it with `pip install aporia[pyspark] and try again."
                    ),
                )
            from aporia.experimental.model_versions_api import get_model_versions

            version_id = next(
                version.id
                for version in get_model_versions(self.model_id)
                if version.name == self.model_version
            )
            self._pyspark_inference.log_batch_pyspark_prediction(
                version_id=version_id,
                model=self,
                data=data,
                id_column=id_column,
                features=features,
                predictions=predictions,
                timestamp_column=timestamp_column,
                raw_inputs=raw_inputs,
                labels=labels,
                spark_options=spark_options,
            )

    def log_streaming_pyspark_prediction(
        self,
        data: PySparkDataFrame,
        id_column: Optional[str] = None,
        timestamp_column: Optional[str] = None,
        features: Optional[Mapping[str, str]] = None,
        predictions: Optional[Mapping[str, str]] = None,
        raw_inputs: Optional[Mapping[str, str]] = None,
        labels: Optional[Mapping[str, str]] = None,
        spark_options: Optional[Mapping[str, str]] = None,
    ):
        """Logs stream of predictions.

        Args:
            data: PsSpark dataframe
            id_column: Optional dataframe column to use as an id.
            timestamp_column: Optional dataframe column to use as an id.
            features: A mapping of feature names (from the schema) to dataframe columns
            predictions: A mapping of predictions names (from the schema) to dataframe columns
            raw_inputs: A mapping of raw input names (from the schema) to dataframe columns
            labels: A mapping of label names (from the schema) to dataframe columns
            spark_options: Optional configuration extension for spark elastic connector. See
                https://www.elastic.co/guide/en/elasticsearch/hadoop/master/configuration.html
        """
        with self.handle_error("{}"):
            if self._pyspark_inference is None:
                raise AporiaError(
                    short_message="Logging pyspark predictions failed, Aporia pyspark extension not found",
                    verbose_message=(
                        "The Aporia pyspark extension is required to log predictions from pyspark "
                        "dataframes. Install it with `pip install aporia[pyspark] and try again."
                    ),
                )
            from aporia.experimental.model_versions_api import get_model_versions

            version_id = next(
                version.id
                for version in get_model_versions(self.model_id)
                if version.name == self.model_version
            )
            
            return self._pyspark_inference.log_streaming_pyspark_prediction(
                version_id=version_id,
                model=self,
                data=data,
                id_column=id_column,
                features=features,
                predictions=predictions,
                timestamp_column=timestamp_column,
                raw_inputs=raw_inputs,
                labels=labels,
                spark_options=spark_options,
            )

    def log_pyspark_training_set(
        self,
        data: PySparkDataFrame,
        features: Optional[Mapping[str, str]] = None,
        predictions: Optional[Mapping[str, str]] = None,
        raw_inputs: Optional[Mapping[str, str]] = None,
    ):
        """Logs training data from PySpark DataFrames.

        Args:
            data: PySparkDataFrame all the data
            features: Optional[Mapping[str,str]]
                mapping of column to features as configured in the schema.
                Key is the name in the schema and the value is the name of the corresponding dataframe column
            predictions:Optional[Mapping[str,str]]
                mapping of column to predictions as configured in the schema.
                Key is the name in the schema and the value is the name of the corresponding dataframe column
            raw_inputs: Optional[Mapping[str, str]]
                mapping of column to raw inputs as configured in the schema.
                Key is the name in the schema and the value is the name of the corresponding dataframe column

        """
        with self.handle_error("{}"):
            if self._pyspark_training is None:
                raise AporiaError(
                    short_message="Logging training data failed, Aporia pyspark extension not found",
                    verbose_message=(
                        "The Aporia pyspark extension is required to log training data from "
                        "pyspark dataframes. Install it with `pip install aporia[pyspark]` "
                        "and try again."
                    ),
                )

            self._pyspark_training.log_pyspark_training_set(
                data=data,
                features_schema_df_mapping=features,
                predictions_schema_df_mapping=predictions,
                raw_inputs_schema_df_mapping=raw_inputs,
            )

    def log_pyspark_test_set(
        self,
        features: PySparkDataFrame,  # type: ignore
        predictions: PySparkDataFrame,  # type: ignore
        labels: PySparkDataFrame,  # type: ignore
        raw_inputs: Optional[PySparkDataFrame] = None,  # type: ignore
    ):
        """Logs test data from PySpark DataFrames.

        Args:
            features: Test set features
            predictions: Test set predictions
            labels: Test set labels
            raw_inputs: Test set raw inputs.

        Notes:
            * Each dataframe corresponds to a field category defined in create_model_version:
                * features -> features
                * predictions -> predictions
                * labels -> predictions
                * raw_inputs -> raw_inputs
            * Each column in the dataframe should match a field defined in create_model_version
                * Missing fields will be handled as missing values
                * Columns that do not match a defined field will be ignored
                * The column name must match the field name
            * This function is blocking and may take a while to finish running.
        """
        with self.handle_error("{}"):
            if self._pyspark_training is None:
                raise AporiaError(
                    short_message="Logging test data failed, Aporia pyspark extension not found",
                    verbose_message=(
                        "The Aporia training extension is required to log test data from "
                        "pyspark dataframes. Install it with `pip install aporia[pyspark]` "
                        "and try again."
                    ),
                )

            self._pyspark_training.log_pyspark_test_set(
                features=features,
                predictions=predictions,
                labels=labels,
                raw_inputs=raw_inputs,
            )
