from collections import defaultdict
from json import dumps, loads
import logging
from typing import Any, Dict, List, Optional, Tuple

from aporia.core.logging_utils import LOGGER_NAME
from aporia.pyspark.training.pyspark_field_metadata import PySparkFieldMetadata
from aporia.training.api.log_training import FieldTrainingData

logger = logging.getLogger(LOGGER_NAME)


def get_field_identifier(field_group: str, field_name: str, dict_key: Optional[str] = None) -> str:
    """Returns a string that can be used to identify a field from the model."""
    hash_data: Dict = {"group": field_group, "name": field_name}
    if dict_key is not None:
        hash_data["key_at_dict"] = dict_key
    return dumps(hash_data)


def _parse_field_identifier(field_identifier_str: str) -> Tuple[str, str, Optional[str]]:
    hash_data: Dict = loads(field_identifier_str)
    group = hash_data["group"]
    name = hash_data["name"]
    dict_key = hash_data.get("key_at_dict", None)
    return group, name, dict_key


def create_alias(aggregation_name: str, field: PySparkFieldMetadata) -> str:
    """Create the alias string for the pyspark quires."""
    alias_data = {
        "aggregation_name": aggregation_name,
        "group": field.group,
        "column": field.column,
        "name": field.name,
    }
    if field.key_at_dict is not None:
        alias_data["key_at_dict"] = field.key_at_dict
    return dumps(alias_data)


def _parse_alias(alias_str: str) -> Tuple[str, str]:
    """Parse an alias str."""
    logger.debug("parsing aggregation alias: " + alias_str)
    alias_data: Dict[str, str] = loads(alias_str)
    field_identifier = get_field_identifier(
        field_group=alias_data["group"],
        field_name=alias_data["name"],
        dict_key=alias_data.get("key_at_dict", None),
    )
    return field_identifier, alias_data["aggregation_name"]


def parse_aggregation_results_to_field_training_data_by_group(
    aggregate_results_dict: dict,
) -> Dict[str, List[FieldTrainingData]]:
    """Parses aggregation results.

    Args:
        aggregate_results_dict: Aggregation results

    Returns:
        Field training data for each field group
    """
    field_identifier_to_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {})
    for agg_alias, agg_result in aggregate_results_dict.items():
        field_identifier, aggregation_name = _parse_alias(agg_alias)
        field_identifier_to_metrics[field_identifier][aggregation_name] = agg_result

    fields_training_data_by_group: Dict[str, List[FieldTrainingData]] = {}
    for field_identifier, metrics in field_identifier_to_metrics.items():
        group, name, dict_key = _parse_field_identifier(field_identifier)
        if group not in fields_training_data_by_group:
            fields_training_data_by_group[group] = []
        if dict_key is None:
            fields_training_data_by_group[group].append(
                FieldTrainingData(field_name=name, **metrics)
            )
        else:
            fields_training_data_by_group[group].append(
                FieldTrainingData(field_name=name, key=dict_key, **metrics)
            )
    return fields_training_data_by_group
