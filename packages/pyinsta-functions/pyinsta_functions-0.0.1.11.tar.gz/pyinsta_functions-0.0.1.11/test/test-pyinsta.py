#### lib criada pelo instaviagem ####
# import pyinsta.functions as func
# import pyinsta.connectors as con
# ####
import pandas as pd
import pytest
import os
from pytest import mark, param
from os.path import dirname
import pandas as pd
from pandas.io.sql import DatabaseError
import sys
import json
from sqlalchemy import create_engine
import pymysql

pyinsta_dir = dirname(dirname(__file__))  # This is your Project Root
root_dir = os.path.realpath(os.path.join(dirname(dirname(__file__)), '..'))
sys.path.append(pyinsta_dir+'/src/pyinsta/')
sys.path.append('./pyinsta/src/pyinsta/')


credentials_file = root_dir + \
    '/functions/producer/facebook/credentials/data-science-279809-3a77dceb5e8e.json'

import connectors as con
import functions as func

@pytest.mark.bq_connection
def bigquery_connections():
    bigquery_client = con.google_connection(credentials_file).bq_connection()
    assert bigquery_client is not None


@pytest.mark.bq_data
def bigquery_data():
    bigquery_client = con.google_connection(credentials_file).bq_connection()
    query = 'SELECT * FROM `data-science-279809.tables_fields.experience` LIMIT 1'
    data = func.google_data(bigquery_client).get_data(query)
    assert data is not None


@pytest.mark.load_to_bq
def load_to_bq():
    bigquery_client = con.google_connection(credentials_file).bq_connection()

    table_name = "rds.teste"
    schema = [{"name": "id", "type": "STRING", "mode": "NULLABLE"},
              {"name": "AddedDate", "type": "TIMESTAMP", "mode": "NULLABLE"},
              {"name": "value", "type": "STRING", "mode": "NULLABLE"}]

    input = [{"id": "56", "AddedDate": "2021-07-22 09:00:00 UTC", "value": "5555"}]
    input = pd.DataFrame(data=input)
    results = func.bq_schema(input, schema)

    func.load_into_bigquery(results, table_name,
                            bigquery_client, schema=schema)
    assert True


@pytest.mark.get_aws_data
def get_aws_data():
    rds_config = func.access_secret(
        project_id="727211862808", secret_id="rds-replica-key", version_id="latest")
    rds_config_json = json.loads(rds_config.payload.data.decode('UTF-8'))
    rds_config_json['port']= 3306

    rds_engine = con.connection_db(rds_config_json).connect_mysql()
    data = func.get_sql_data(
        rds_engine, query='SELECT * FROM alexa.experience LIMIT 1')

    assert data is not None