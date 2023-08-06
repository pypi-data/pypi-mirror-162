import airflow
from airflow import configuration

import airflow_aggua_plugin.config as config


def get_config_aggua_api_disabled():
    return configuration.conf.getboolean(config.PLUGIN_NAME, "disabled", fallback=False)


def get_webserver_base_url():
    return configuration.conf.get("webserver", "BASE_URL")


def get_api_endpoint():
    return config.API_BASE_URL


def get_airflow_version():
    return airflow.__version__


def get_plugin_version():
    return config.PLUGIN_VERSION
