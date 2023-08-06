import os
import json
from mysql.connector import errorcode
import mysql.connector
import psycopg2
from sqlalchemy import create_engine
import pymysql
import copy
from psycopg2 import Error
from google.cloud import bigquery
from google.api_core.exceptions import AlreadyExists, NotFound,BadRequest
import pandas as pd


class google_connection():
    """
    Função para a conexão com o Google Cloud
    
    Args:
    
    Returns:
    
    bigquery_client: objeto do tipo bigquery
    storage_client: objeto do tipo storage

    """

    def __init__(self, credentials_file:json):
        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
            ##create connection##
            self.bigquery_client = bigquery.Client()
        except:
            raise ValueError("Erro em capturar os dados da BigQuery")


    def bq_connection(self) -> bigquery.Client:
        """
        Função para a conexão com a BigQuery
        
        Args:
        credentials_file: arquivo de credenciais
        
        Returns:
        
        bigquery_client: objeto do tipo bigquery

        """
        try:
            ##create connection##
            bigquery_client = self.bigquery_client

        except BadRequest as e:
            for e in bigquery_client.errors:
                print('ERROR: {}'.format(e['message']))

        return bigquery_client

class connection_db():
    """
    Função para a conexão com o PostgreSQL

    Args:
    params: parametros de conexão
    

    Returns:
    mysql_con: objeto do tipo mysql
    postgres_con: objeto do tipo postgres

    """

    def __init__(self,params:dict):
        self.port = params['port']
        self.host = params['host']
        self.user = params['user']
        self.password = params['password']
        self.database = params['database']

    def connect_postgres(self) -> psycopg2.extensions.connection:
        try:
            # construct an engine connection string
            engine_string = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
                )

            # create sqlalchemy engine
            engine = create_engine(engine_string)
        except psycopg2.OperationalError as e:
            print('Unable to connect!\n{0}').format(e)

        return engine

    def connect_mysql(self) -> pymysql.connections.Connection:
        """
        Função para a conexão com o MySQL

        Args:

        Returns:

        mysql_con: objeto do tipo mysql

        """
        # construct an engine connection string
        engine_string = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )
        try:
        # create sqlalchemy engine
            engine = create_engine(engine_string)

        except pymysql.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))

        return engine
