from typing import Any, Optional

import awswrangler as wr
import boto3
import pandas as pd
from cached_property import cached_property_with_ttl
from pydantic import Field, SecretStr, constr, create_model

from toucan_connectors.common import ConnectorStatus, apply_query_parameters
from toucan_connectors.pandas_translator import PandasConditionTranslator
from toucan_connectors.toucan_connector import (
    DataSlice,
    DataStats,
    DiscoverableConnector,
    TableInfo,
    ToucanConnector,
    ToucanDataSource,
    strlist_to_enum,
)


class AwsathenaDataSource(ToucanDataSource):
    name: str = Field(..., description='Your AWS Athena connector name')
    database: constr(min_length=1) = Field(
        ..., description='The name of the database you want to query.'
    )
    table: str = Field(
        None, **{'ui.hidden': True}
    )  # To avoid previous config migrations, won't be used
    language: str = Field('sql', **{'ui.hidden': True})
    query: constr(min_length=1) = Field(
        None,
        description='The SQL query to execute.',
        widget='sql',
    )
    query_object: dict = Field(
        None,
        description='An object describing a simple select query This field is used internally',
        **{'ui.hidden': True},
    )

    @classmethod
    def get_form(cls, connector: 'AwsathenaConnector', current_config: dict[str, Any]):
        return create_model(
            'FormSchema',
            database=strlist_to_enum('database', connector.available_dbs),
            __base__=cls,
        ).schema()


class AwsathenaConnector(ToucanConnector, DiscoverableConnector):
    data_source_model: AwsathenaDataSource

    name: str = Field(..., description='Your AWS Athena connector name')

    s3_output_bucket: str = Field(
        ..., description='Your S3 Output bucket (where query results are stored.)'
    )
    aws_access_key_id: str = Field(..., description='Your AWS access key ID')
    aws_secret_access_key: SecretStr = Field(None, description='Your AWS secret key')
    region_name: str = Field(..., description='Your AWS region name')

    class Config:
        underscore_attrs_are_private = True
        keep_untouched = (cached_property_with_ttl,)

    def get_session(self) -> boto3.Session:
        return boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            # This is required because this gets appended by boto3
            # internally, and a SecretStr can't be appended to an str
            aws_secret_access_key=self.aws_secret_access_key.get_secret_value(),
            region_name=self.region_name,
        )

    @staticmethod
    def _strip_trailing_semicolumn(query: str) -> str:
        q = query.strip()
        return q[:-1] if q.endswith(';') else q

    @classmethod
    def _add_pagination_to_query(
        cls, query: str, offset: int = 0, limit: Optional[int] = None
    ) -> str:
        if offset and limit:
            return f'SELECT * FROM ({cls._strip_trailing_semicolumn(query)}) LIMIT {limit} OFFSET {offset};'
        if limit:
            return f'SELECT * FROM ({cls._strip_trailing_semicolumn(query)}) LIMIT {limit};'
        return query

    @cached_property_with_ttl(ttl=10)
    def available_dbs(self) -> list[str]:
        return self._list_db_names()

    @cached_property_with_ttl(ttl=60)
    def project_tree(self) -> list[TableInfo]:
        return self._get_project_structure()

    def _retrieve_data(
        self,
        data_source: AwsathenaDataSource,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        df = wr.athena.read_sql_query(
            self._add_pagination_to_query(
                apply_query_parameters(data_source.query, data_source.parameters or {}),
                offset=offset,
                limit=limit,
            ),
            database=data_source.database,
            boto3_session=self.get_session(),
            s3_output=self.s3_output_bucket,
        )
        return df

    def _list_db_names(self) -> list[str]:
        return wr.catalog.databases(
            boto3_session=self.get_session(),
        )['Database'].values

    def _get_project_structure(self) -> list[TableInfo]:
        table_list: list[TableInfo] = []
        session = self.get_session()
        for db in self.available_dbs:
            tables = wr.catalog.tables(boto3_session=session, database=db)[
                ['Table', 'TableType']
            ].to_dict(orient='records')
            for table_object in tables:
                if 'temp_table' not in table_object['Table']:
                    columns = wr.catalog.get_table_types(
                        boto3_session=session, database=db, table=table_object['Table']
                    )
                    table_list.append(
                        {
                            'name': table_object['Table'],
                            'database': db,
                            'type': 'table' if 'TABLE' in table_object['TableType'] else 'view',
                            'columns': [{'name': k, 'type': v} for k, v in columns.items()],
                        }
                    )
        return table_list

    def get_slice(
        self,
        data_source: AwsathenaDataSource,
        permissions: Optional[dict] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        get_row_count: Optional[bool] = False,
    ) -> DataSlice:
        df = self._retrieve_data(data_source, offset=offset, limit=limit)
        df.columns = df.columns.astype(str)

        if permissions is not None:
            permissions_query = PandasConditionTranslator.translate(permissions)
            permissions_query = apply_query_parameters(permissions_query, data_source.parameters)
            df = df.query(permissions_query)

        return DataSlice(
            df,
            stats=DataStats(
                total_returned_rows=len(df),
                total_rows=len(df),
                df_memory_size=df.memory_usage().sum(),
            ),
        )

    def get_status(self) -> ConnectorStatus:
        checks = [
            'Host resolved',
            'Port opened',
            'Connected',
            'Authenticated',
            'Can list databases',
        ]
        session = self.get_session()
        try:
            # Returns a pandas DataFrame of DBs
            wr.catalog.databases(boto3_session=session)
            return ConnectorStatus(status=True, details=[(c, True) for c in checks], error=None)
        # aws-wrangler exceptions all inherit Exception directly:
        # https://github.com/awslabs/aws-data-wrangler/blob/main/awswrangler/exceptions.py
        except Exception as exc:
            try:
                sts_client = session.client('sts')
                sts_client.get_caller_identity()
                # We consider an authenticated client capable of
                # connecting to AWS to be valid, even if sub-optimal
                return ConnectorStatus(
                    status=True,
                    details=[(c, i < 4) for (i, c) in enumerate(checks)],
                    error=f'Cannot list databases: {exc}',
                )
            except Exception as sts_exc:
                # Cannot list databases nor get identity
                return ConnectorStatus(
                    status=False,
                    details=[(c, False) for c in checks],
                    error=f'Cannot verify connection to Athena: {exc}, {sts_exc}',
                )

    def get_model(self) -> list[TableInfo]:
        """Retrieves the database tree structure using current session"""
        return self.project_tree
