from flask_appbuilder import (
    expose as app_builder_expose,
    BaseView as AppBuilderBaseView,
)

import airflow_aggua_plugin.utils as utils
from airflow_aggua_plugin.ui.docs import api_metadata
from airflow_aggua_plugin.config import VIEW_BASE_URL, VIEW_BASE_ROUTE

def get_route_base():
    return VIEW_BASE_ROUTE


class AgguaApiView(AppBuilderBaseView):
    """API View which extends either flask AppBuilderBaseView or flask AdminBaseView"""

    route_base = VIEW_BASE_URL

    # '/' Endpoint where the Admin page is which allows you to view the APIs available and trigger them
    @app_builder_expose("/")
    def list(self):

        return self.render_template(
            "/doc_index.jinja.html",
            airflow_webserver_base_url=utils.get_webserver_base_url(),
            api_endpoint=utils.get_api_endpoint(),
            apis_metadata=api_metadata,
            airflow_version=utils.get_airflow_version(),
            plugin_version=utils.get_plugin_version(),
            static_base_route=VIEW_BASE_ROUTE,
        )
