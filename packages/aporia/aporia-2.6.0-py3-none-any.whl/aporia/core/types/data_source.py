from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional


class DataSourceType(Enum):
    """Enum containing all supported data source types."""

    BIGQUERY = "bigquery"
    JDBC = "jdbc"
    POSTGRES_JDBC = "postgres-jdbc"
    ATHENA = "athena"


class DataSource(ABC):
    """Base class for data sources."""

    def serialize(self) -> Dict[str, Any]:
        """Serialize data source to dict."""
        return {"type": self.type.value, "config": self.serialize_config()}

    @property
    @abstractmethod
    def type(self) -> DataSourceType:
        """Returns data source type."""
        ...

    @abstractmethod
    def serialize_config(self) -> Dict[str, Any]:
        """Serialize data source configuration to dict."""
        ...


class SparkDataSource(DataSource):
    """Base class for spark-based data sources."""

    def __init__(
        self,
        sample_size: float = 1.0,
        select_expr: Optional[List[str]] = None,
        read_options: Optional[Dict[str, Any]] = None,
    ):
        """Initializes a SparkDataSource.

        Args:
            sample_size: Fraction of data to sample
            select_expr: Select expressions to apply to the dataframe after reading
            read_options: Additional spark read options
        """
        super().__init__()
        self.sample_size = sample_size
        self.select_expr = select_expr
        self.read_options = read_options

    def serialize_config(self) -> Dict[str, Any]:
        """See base class."""
        return {
            "sample_size": self.sample_size,
            "select_expr": self.select_expr,
            "read_options": self.read_options,
        }


class JDBCDataSource(SparkDataSource):
    """Generic JDBC data source."""

    def __init__(
        self,
        url: str,
        query: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
        sample_size: float = 1,
        select_expr: Optional[List[str]] = None,
        read_options: Optional[Dict[str, Any]] = None,
    ):
        """Initializes a JDBCDataSource.

        Args:
            url: Database connection URL
            query: SQL query to read data from the database
            user: Database user
            password: Database password
            sample_size: Fraction of data to sample
            select_expr: Select expressions to apply to the dataframe after reading
            read_options: Additional spark read options
        """
        super().__init__(
            sample_size=sample_size, select_expr=select_expr, read_options=read_options
        )
        self.url = url
        self.query = query
        self.user = user
        self.password = password

    @property
    def type(self) -> DataSourceType:
        """See base class."""
        return DataSourceType.JDBC

    def serialize_config(self) -> Dict[str, Any]:
        """See base class."""
        return {
            **super().serialize_config(),
            "url": self.url,
            "query": self.query,
            "user": self.user,
            "password": self.password,
        }


class PostgresJDBCDataSource(JDBCDataSource):
    """Postgres (via JDBC) data source."""

    @property
    def type(self) -> DataSourceType:
        """See base class."""
        return DataSourceType.POSTGRES_JDBC


class AthenaDataSource(JDBCDataSource):
    """AWS Athena data source."""

    def __init__(
        self,
        url: str,
        query: str,
        s3_output_location: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
        sample_size: float = 1,
        select_expr: Optional[List[str]] = None,
        read_options: Optional[Dict[str, Any]] = None,
    ):
        """Initializes a JDBCDataSource.

        Args:
            url: Database connection URL
            query: SQL query to read data from the database
            s3_output_location: Path to S3 bucket for storing query results
            user: Database user
            password: Database password
            sample_size: Fraction of data to sample
            select_expr: Select expressions to apply to the dataframe after reading
            read_options: Additional spark read options
        """
        super().__init__(
            url=url,
            query=query,
            user=user,
            password=password,
            sample_size=sample_size,
            select_expr=select_expr,
            read_options=read_options,
        )
        self.s3_output_location = s3_output_location

    @property
    def type(self) -> DataSourceType:
        """See base class."""
        return DataSourceType.ATHENA

    def serialize_config(self) -> Dict[str, Any]:
        """See base class."""
        return {
            **super().serialize_config(),
            "s3_output_location": self.s3_output_location,
        }


class BigQueryDataSource(SparkDataSource):
    """BigQuery data source."""

    def __init__(
        self,
        credentials_base64: str,
        table: str,
        dataset: Optional[str] = None,
        project: Optional[str] = None,
        parent_project: Optional[str] = None,
        sample_size: float = 1.0,
        select_expr: Optional[List[str]] = None,
        read_options: Optional[Dict[str, Any]] = None,
    ):
        """Initializes a SparkDataSource.

        Args:
            credentials_base64: Base64 encoded JSON string containing GCP service account details.
            table: Table to query
            dataset: Dataset to query
            project: Project name
            parent_project: Parent project name
            sample_size: Fraction of data to sample
            select_expr: Select expressions to apply to the dataframe after reading
            read_options: Additional spark read options
        """
        super().__init__(
            sample_size=sample_size, select_expr=select_expr, read_options=read_options
        )
        self.credentials_base64 = credentials_base64
        self.table = table
        self.dataset = dataset
        self.project = project
        self.parent_project = parent_project

    @property
    def type(self) -> DataSourceType:
        """See base class."""
        return DataSourceType.BIGQUERY

    def serialize_config(self) -> Dict[str, Any]:
        """See base class."""
        return {
            **super().serialize_config(),
            "credentials_base64": self.credentials_base64,
            "table": self.table,
            "dataset": self.dataset,
            "project": self.project,
            "parent_project": self.parent_project,
        }
