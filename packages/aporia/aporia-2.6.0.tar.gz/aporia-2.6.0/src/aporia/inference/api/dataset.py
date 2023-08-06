from typing import Any, Dict, Optional

from aporia.core.http_client import HttpClient
from aporia.core.types.data_source import DataSource


def _get_query_data(
    dataset: str,
    environment: str,
    data_source: DataSource,
    id_column: str,
    timestamp_column: str,
    predictions: Optional[Dict[str, str]] = None,
    features: Optional[Dict[str, str]] = None,
    labels: Optional[Dict[str, str]] = None,
    raw_inputs: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    data = {
        "name": dataset,
        "data_source": data_source.serialize(),
        "sync": {
            "enabled": True,
            "environment": environment,
        },
        "id_column": id_column,
        "timestamp_column": timestamp_column,
    }

    if predictions is not None:
        data["predictions"] = predictions

    if features is not None:
        data["features"] = features

    if labels is not None:
        data["labels"] = labels

    if raw_inputs is not None:
        data["raw_inputs"] = raw_inputs

    return data


async def connect_dataset(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    dataset: str,
    environment: str,
    data_source: DataSource,
    id_column: str,
    timestamp_column: str,
    predictions: Optional[Dict[str, str]] = None,
    features: Optional[Dict[str, str]] = None,
    labels: Optional[Dict[str, str]] = None,
    raw_inputs: Optional[Dict[str, str]] = None,
):
    """Connect to a dataset.

    Args:
        http_client: HTTP client.
        model_id: Model id.
        model_version: Model version.
        dataset: Dataset name.
        environment: Environment.
        data_source: Data source object (for example, `SparkSQLDataSource`).
        id_column: Name of the ID column.
        timestamp_column: Name of the timestamp column.
        predictions: Predictions -> columns mappping. Defaults to None.
        features: Features -> columns mappping. Defaults to None.
        labels: Labels -> columns mappping. Defaults to None.
        raw_inputs: Raw inputs -> columns mappping. Defaults to None.
    """
    await http_client.post(
        url=f"/models/{model_id}/versions/{model_version}/datasets",
        data=_get_query_data(
            dataset=dataset,
            environment=environment,
            data_source=data_source,
            id_column=id_column,
            timestamp_column=timestamp_column,
            features=features,
            predictions=predictions,
            labels=labels,
            raw_inputs=raw_inputs,
        ),
        timeout=60 * 10,
    )
