from flask import Blueprint
from airflow.plugins_manager import AirflowPlugin

import airflow_aggua_plugin.utils as utils
from airflow_aggua_plugin.api import app
import airflow_aggua_plugin.config as config
import airflow_aggua_plugin.ui.app_builder_view as view


# Creating Blueprint
api_ui_blueprint = Blueprint(
    "api_ui_blueprint",
    __name__,
    template_folder="ui/templates",
    static_folder="ui/static",
    static_url_path="/static/" + view.get_route_base(),
)

api_blueprint = app.blueprint

api_view = {
    "category": config.AIRFLOW_UI_MENU_ENTRY,
    "name": config.AIRFLOW_UI_SUB_MENU_ENTRY,
    "view": view.AgguaApiView(),
}


class AgguaApi(AirflowPlugin):
    name = config.PLUGIN_NAME
    operators = []
    hooks = []
    executors = []
    menu_links = []

    if utils.get_config_aggua_api_disabled():
        flask_blueprints = []
        appbuilder_views = []
    else:
        flask_blueprints = [api_ui_blueprint, api_blueprint]
        appbuilder_views = [api_view]
