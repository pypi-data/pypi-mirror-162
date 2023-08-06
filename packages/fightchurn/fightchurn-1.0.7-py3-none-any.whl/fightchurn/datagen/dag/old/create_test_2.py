# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Demonstrates how to use connections in an Airflow DAG."""

import datetime

from airflow import models
from airflow.providers.google.cloud.operators import bigquery
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator


yesterday = datetime.datetime.combine(
    datetime.datetime.today() - datetime.timedelta(1),
    datetime.datetime.min.time())

default_dag_args = {
    # Setting start date as yesterday starts the DAG immediately when it is
    # detected in the Cloud Storage bucket.
    'start_date': yesterday,
    'retries': 1,
}

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG('create_test_2',
        schedule_interval=datetime.timedelta(days=1),
        default_args=default_dag_args) as dag:
    # [START composer_connections_default]
    task_default = bigquery.BigQueryInsertJobOperator(
        task_id='task_default_connection',
        configuration={
            "query": {
                "query": 'SELECT 1',
                "useLegacySql": False
            }
        }
    )
    # [END composer_connections_default]
    # [START composer_connections_explicit]
    # Composer creates a 'google_cloud_default' connection by default.
    task_explicit = bigquery.BigQueryInsertJobOperator(
        task_id='task_explicit_connection',
        gcp_conn_id='google_cloud_default',
        configuration={
            "query": {
                "query": 'SELECT 1',
                "useLegacySql": False
            }
        }
    )
    # [END composer_connections_explicit]
    #

    check0 = BigQueryCheckOperator(task_id='check_public_event_data_exists',
                           sql="""
                            select count(*) > 0
                            from bigquery-public-data.austin_bikeshare.bikeshare_trips
                        """,
                           use_legacy_sql=False)


    check1 = bigquery.BigQueryInsertJobOperator(
        task_id='check_with_insert_operator',
        gcp_conn_id='google_cloud_default',
        configuration={
            "query": {
                "query": 'select distinct 1 > 0 from churn-1.socialnet7.event',
                "useLegacySql": False
            }
        }
    )

    create_table = bigquery.BigQueryCreateEmptyTableOperator(
        task_id="create_table",
        dataset_id='churn-1',
        table_id="metrics",
        schema_fields=[
            {"name": "account_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "metric_time", "type": "TIMESTAMP", "mode": "REQUIRED"},
            {"name": "metric_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "metric_value", "type": "FLOAT", "mode": "REQUIRED"},
        ],
    )

    # upsert_table = bigquery.BigQueryUpsertTableOperator(
    #     task_id="upsert_table",
    #     dataset_id='churn-1',
    #     table_resource={
    #         "tableReference": {"tableId": "test_table_id"},
    #         "expirationTime": (int(time.time()) + 300) * 1000,
    #     },
    # )

task_default >> task_explicit >> check0 >> check1 >> create_table
