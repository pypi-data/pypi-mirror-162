from typing import List, NamedTuple

from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from airflow.models.serialized_dag import SerializedDagModel


class SerializedDAGSchema(SQLAlchemySchema):
    """Serialized DAG schema"""

    class Meta:
        """Meta"""

        model = SerializedDagModel

    dag_id = fields.String(dump_only=True)
    data = fields.Dict(dump_only=True)
    last_updated = fields.DateTime(dump_only=True)
    fileloc = fields.String(dump_only=True)
    dag_hash = fields.String(dump_only=True)


class SerializedDAGCollection(NamedTuple):
    """List of Serialized DAGs with metadata"""

    serialized_dags: List[SerializedDagModel]
    total_entries: int


class SerializedDAGCollectionSchema(Schema):
    """Serialized DAG Collection schema"""

    serialized_dags = fields.List(fields.Nested(SerializedDAGSchema))
    total_entries = fields.Int()


serialized_dags_collection_schema = SerializedDAGCollectionSchema()
serialized_dag_schema = SerializedDAGSchema()
