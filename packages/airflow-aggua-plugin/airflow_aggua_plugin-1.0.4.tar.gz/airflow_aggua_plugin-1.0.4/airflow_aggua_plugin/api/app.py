from flask import Blueprint

import airflow_aggua_plugin.utils as utils

# setup blueprint
blueprint = Blueprint("airflow_api", __name__, url_prefix=utils.get_api_endpoint())

# setup api
from airflow_aggua_plugin.api import api_setup
