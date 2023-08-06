# Airflow Aggua API - Plugin

Apache Airflow plugin that exposes aggua secure API endpoints similar to the official [Airflow API (Stable) (1.0.0)](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html), providing richer capabilities. Apache Airflow version 2.1.0 or higher is necessary.

## Requirements

- [apache-airflow](https://github.com/apache/airflow)
- [marshmallow](https://github.com/marshmallow-code/marshmallow)


## Installation

```python
python3 -m pip install airflow-aggua-api
```

## Authentication

Airflow Aggua API plugin uses the same auth mechanism as [Airflow API (Stable) (1.0.0)](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#section/Trying-the-API). So, by default APIs exposed via this plugin respect the auth mechanism used by your Airflow webserver and also complies with the existing RBAC policies. Note that you will need to pass credentials data as part of the request. Here is a snippet from the official docs when basic authorization is used:

```bash
curl -X POST 'http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/dags/{dag_id}?update_mask=is_paused' \
-H 'Content-Type: application/json' \
--user "username:password" \
-d '{
    "is_paused": true
}'
```

## Using the Custom API

All the supported endpoints are exposed in the below format:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/aggua/{ENDPOINT_NAME}
```

Following are the names of endpoints which are currently supported.

- [serializedDags](#serialized_dags)


### **_<span id="serialized_dags">serializedDags</span>_**

##### Description:

- Get the serialized representation of a DAG.

##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/aggua/serializedDags
```

##### Method:

- GET

##### GET request query parameters :

- limit (optional) - number - The number of items to return. default = 10.
- offset (optional) - number - The number of items to skip before starting to collect the result set.


##### Endpoint:

```text
http://{AIRFLOW_HOST}:{AIRFLOW_PORT}/api/v1/aggua/serializedDags/{dag_id}
```

##### Method:

- GET

##### Get request path parameter:

- dag_id - string - the DAG ID.

