from datetime import datetime
import os
import sys
import pandas as pd
import numpy as np
import requests
import json
import pytz
from google.cloud import bigquery, storage
from google.api_core.exceptions import AlreadyExists, NotFound, BadRequest
from google.cloud import error_reporting
from google.cloud import secretmanager
from pandas.io.sql import DatabaseError
import mysql.connector

import hashlib


def get_sql_data(mysql_con: mysql.connector.connect, query: str) -> pd.core.frame.DataFrame:
    """
    Função para a capturar informação do mysql e retornar em um dataframe

    Args:
        mysql_con: objeto do tipo mysql.connector.connect
        query: query a ser executada
    Returns:    
        df: dataframe com os dados da query
    """
    try:

        results_mysql = pd.read_sql(query, mysql_con)

    except DatabaseError as e:
        print(f'Query failed!\n\n{e}')

    return results_mysql


def get_bq_data(bigquery_client: bigquery.Client, query: str) -> pd.core.frame.DataFrame:
    """
        Função para a captura de dados do Google Cloud

        Args:
        query: query a ser executada

        Returns:
        data: dados capturados
        """
    try:
        data = bigquery_client.query(query).to_dataframe()
    except DatabaseError as e:
        print(f'Query failed!\n\n{e}')

    return data


def load_into_bigquery(input: pd.core.frame.DataFrame, table: str, bigquery_client: bigquery.Client, schema=None):
    """
    Função para subir arquivos na BigQuery
    Args:
        input (Dataframe): arquivo a ser subido
        table: nome da tabela
        bigquery_client: objeto do tipo bigquery.Client
        schema (list): schema da tabela (opcional)
        format
        [
            {
            "description": "[DESCRIPTION]",
            "name": "[NAME]",
            "type": "[TYPE]",
            "mode": "[MODE]"
            },
            {
            "description": "[DESCRIPTION]",
            "name": "[NAME]",
            "type": "[TYPE]",
            "mode": "[MODE]"
            }
            ]
    Returns:
        status: status da subida do arquivo
    """

    job_config = bigquery.LoadJobConfig()
    job_config.autodetect = True
    if schema:
        job_config.schema = schema
    job_config.ignore_unknown_values = True
    job_config.schema_update_options = 'ALLOW_FIELD_RELAXATION'
    job_config.max_bad_records = 1
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
    job = bigquery_client.load_table_from_dataframe(input,
                                                    table,
                                                    job_config=job_config)

    print("Starting job {}".format(job.job_id))

    # Waits for table load to complete.
    try:
        job.result()
    except BadRequest as e:
        for e in job.errors:
            print('ERROR: {}'.format(e['message']))
    assert job.job_type == 'load'
    assert job.state == 'DONE'

    destination_table = bigquery_client.get_table(table)
    print("Loaded {} rows.".format(destination_table.num_rows))


def load_into_bigquery_stream(input: pd.core.frame.DataFrame, table: str, bigquery_client: bigquery.Client, schema=None):

    # Make an API request.
    errors = bigquery_client.insert_rows_json(table, input)

    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))


def clean_columns(input: pd.core.frame.DataFrame):
    """
    Função para 'limpar' colunas do dataframe e deixar no padrão da BigQuery
    Args:
        input: dataframe a ser limpo
    Returns:
        df: dataframe limpo
    """

    #### rename para tirar caracteres especiais####

    input.columns = input.columns.str.replace('ç', 'c', regex=True)
    input.columns = input.columns.str.replace('ã|â|á', 'a', regex=True)
    input.columns = input.columns.str.replace('í', 'i', regex=True)
    input.columns = input.columns.str.replace('õ|ó', 'o', regex=True)
    input.columns = input.columns.str.replace('é', 'e', regex=True)
    input.columns = input.columns.str.replace('-', '_', regex=True)
    input.columns = input.columns.str.replace(' ', '_', regex=True)
    input.columns = input.columns.str.replace('.', '_', regex=True)
    input.columns = input.columns.str.replace('&', '', regex=True)
    input.columns = input.columns.str.replace(r'[/]', '_', regex=True)

    ## drop columns que com ( no DDD e não fazem sentido para o modelo
    input = input.loc[:, ~input.columns.str.contains("\(|\+")]

    return input


def check_columns(dataframe: pd.core.frame.DataFrame, list_columns) -> pd.core.frame.DataFrame:
    """
    Função para verificar se as colunas existem no dataframe e na lista de colunas
    Args:
        dataframe: dataframe a ser verificado
        list_columns: lista de colunas a serem verificadas
    Returns:
        list_results: lista de colunas que existem no dataframe
    """
    dataframe_columns = list(dataframe.columns)
    list_results = list(set(list_columns) & set(dataframe_columns))

    return list_results


def astype_columns(input):
    """
    Função para converter as colunas do dataframe para o tipo do BigQuery
    Args:
        input: campo a ser convertido
    Returns:
        df: campo convertido
    """

    if input == 'FLOAT':
        return "float64"
    elif input == 'INTEGER':
        return "int64"
    elif input == 'STRING':
        return "str"
    elif input == 'BOOLEAN':
        return "bool"


def bq_schema(input: pd.core.frame.DataFrame, schema) -> pd.core.frame.DataFrame:
    """
    Função padroninzar a tipagem dos campos de um dataframe antes de subir na BigQuery
    Args:
        input: dataframe a ser convertido
        schema: schema do BigQuery
    Returns:
        input: dataframe convertido
    """

    schema_df = pd.DataFrame(schema)
    del schema_df['mode']

    schema_df['astype'] = schema_df.apply(
        lambda row: astype_columns(str(row['type'])), axis=1)
    columns = check_columns(input, list(schema_df.name.unique()))
    input = input[columns].fillna(method='ffill')

    for col in input.columns:
        astype_value = schema_df['astype'][schema_df['name'] == str(
            col)].iloc[0]
        type = schema_df['type'][schema_df['name'] == str(col)].iloc[0]

        if type == 'TIMESTAMP':
            try:
                input[col] = pd.to_datetime(
                    input[col].replace(np.nan, "2022-01-31"), utc=True)
            except:
                None
        elif type == 'DATE':
            input[col] = pd.to_datetime(input[col], utc=True)
        elif type == 'FLOAT':
            input[col] = input[col].fillna(0).astype('float64')
        elif type == 'INTEGER':
            input[col] = input[col].fillna(0).astype('int64')
        elif type == 'STRING':
            input[col] = input[col].fillna("None").astype('str')
        elif type == 'BOOLEAN':
            input[col] = input[col].fillna("true").astype('bool')
        else:
            input[col] = input[col].fillna("None").astype(
                str(astype_value), errors='ignore')

    return input

##function to upload the results in the google storage (data lake)##


def upload_blob(bucket_name:str, source_file_name:str, destination_blob_name:str,storage_client: storage.Client): 
    """Uploads a file to the bucket.
    args:
        bucket_name: The name of the bucket to upload to.
        source_file_name: The name of the file to upload.
        destination_blob_name: The name of the blob to upload to.

    Returns:
        staus: The status of the upload.

    """
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(
            source_file_name, content_type='application/json')

    except Exception as e:
        print(e)
    return("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def delete_storage_date(bucket_name: str, file_list: list, storage_client: storage.Client):

    source_bucket = storage_client.bucket(bucket_name)

    for file in file_list:
        file.delete()

    return print(f"All file in bucket {bucket_name} deleted.")

def access_secret(project_id,secret_id, version_id="latest"):
    """
    Accesses the secret version identified by secret_id and version_id.
    Args:
        project_id: The project ID of the secret to access.
        secret_id: The ID of the secret to access.
        version_id: The ID of the secret version to access.
    Returns:
        secret: The secret data.

    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response


def secret_hash(secret_value):
  """
  return the sha224 hash of the secret value
    Args:
        secret_value: The secret value to hash.
    Returns:
        secret_hash: The sha224 hash of the secret value.
        
  """
  return hashlib.sha224(bytes(secret_value, "utf-8")).hexdigest()


def value_def(value):

    """
    Função para verificar se o campo é null ou ''
    Args:
        value: campo a ser verificado
    Returns:
        value: retorna None para campo null ou '' 
        e o campo original caso contrário
    """
    if value == 'null' or value == "":
        return None
    else:
        return value