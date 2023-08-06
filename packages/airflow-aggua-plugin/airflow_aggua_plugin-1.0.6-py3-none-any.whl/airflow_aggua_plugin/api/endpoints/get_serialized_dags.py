from airflow.api_connexion import security
from airflow.security import permissions
from airflow.utils.session import provide_session
from airflow.www.app import csrf
from airflow.models.serialized_dag import SerializedDagModel
from flask import request

from airflow_aggua_plugin.api.app import blueprint
from airflow_aggua_plugin.api.response import ApiResponse
from airflow_aggua_plugin.api.schemas.serialized_dag_schema import serialized_dags_collection_schema, serialized_dag_schema,\
    SerializedDAGCollection


@blueprint.route("/serializedDags", methods=["GET"])
@csrf.exempt
@security.requires_access([(permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG)])
@provide_session
def get_serialized_dags(session):
    try:
        limit = request.args.get("limit", 10)
        offset = request.args.get("offset", None)
        query = session.query(SerializedDagModel)
        total_entries = query.count()
        serialized_dags = query.offset(offset).limit(limit).all()
        return serialized_dags_collection_schema.dump(SerializedDAGCollection(serialized_dags=serialized_dags,
                                                                              total_entries=total_entries))
    except Exception:
        return ApiResponse.server_error("failed to get serialized dags")


@blueprint.route("/serializedDags/<string:dag_id>", methods=["GET"])
@csrf.exempt
@security.requires_access([(permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG)])
@provide_session
def get_serialized_dag(dag_id, session):
    try:
        serialized_dag = session.query(SerializedDagModel).filter_by(dag_id=dag_id).one()
        return serialized_dag_schema.dump(serialized_dag)
    except Exception:
        return ApiResponse.server_error("failed to get serialized dag")
