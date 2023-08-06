from typing import Optional

from aporia.core.types.field import FieldType


class PySparkFieldMetadata:
    """Field metadata for pyspark training calculations."""

    def __init__(
        self, name: str, type: FieldType, column: str, group: str, key_at_dict: Optional[str] = None
    ):
        """Initializes the object.

        Args:
            name: Field name
            type: Field type
            column: Column corresponding to the field in a dataframe
            group: Field group (features, predictions, etc.)
            key_at_dict: Key of nested field in dict
        """
        self.name = name
        self.type = type
        self.column = column
        self.group = group
        self.key_at_dict = key_at_dict

    def __str__(self) -> str:
        """Returns a string representation of the object."""
        key_at_dict_txt = None
        if self.key_at_dict is not None:
            key_at_dict_txt = f"| Key At Parent Dict Field: {self.key_at_dict}"
        return f"Field Name: {self.name} | Field type: {self.type} | Field Col: {self.column} | Field Group: {self.group} {key_at_dict_txt}"  # noqa: B950
