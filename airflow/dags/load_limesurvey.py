import sys
import pandas as pd
from datetime import timedelta
from sqlalchemy import create_engine, inspect, exc, text
import sqlparse

from airflow.utils.dates import days_ago
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.task_group import TaskGroup

OWNER = "timo"
# list of table names
TABLE_NAMES = ["lime_question_attributes", "lime_questions", "lime_survey_916481", "lime_survey_916481_timings"]
CONFIG = {
    "LIMESURVEY_SQL_USER": Variable.get('LIMESURVEY_SECRET_SQL_USER'),
    "LIMESURVEY_SQL_PASSWORD": Variable.get('LIMESURVEY_SQL_PASSWORD'),
    "LIMESURVEY_DATABASE_PORT": int(Variable.get('LIMESURVEY_SECRET_DATABASE_PORT')),
    "LIMESURVEY_DATABASE_NAME": Variable.get('LIMESURVEY_SECRET_DATABASE_NAME'),
    "COOLIFY_MARIADB_HOST": Variable.get('COOLIFY_SECRET_MARIADB_HOST'),
    "COOLIFY_MARIADB_PORT": int(Variable.get('COOLIFY_SECRET_MARIADB_PORT')),
    "COOLIFY_MARIADB_USER": Variable.get('COOLIFY_SECRET_MARIADB_USER'),
    "COOLIFY_MARIADB_PASSWORD": Variable.get('COOLIFY_MARIADB_PASSWORD'),
    "COOLIFY_MARIADB_DATABASE": Variable.get("COOLIFY_SECRET_MARIADB_DATABASE")
}


def extract_limesurvey(config, table_names=None):
    # connect to source MariaDB Platform
    try:
        print("Connecting to Limesurvey DB")
        source_url = (
            f"mariadb+mariadbconnector://{config['LIMESURVEY_SQL_USER']}"
            f":{config['LIMESURVEY_SQL_PASSWORD']}"
            f"@127.0.0.1"
            f":{config['LIMESURVEY_DATABASE_PORT']}"
            f"/{config['LIMESURVEY_DATABASE_NAME']}"
        )
        engine_source = create_engine(source_url, echo=True)
        print("Connection to Limesurvey DB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to source MariaDB Platform: {e}")
        sys.exit(1)

    # connect to target MariaDB Platform
    try:
        print("Connecting to target MariaDB")
        target_url = (
            f"mariadb+mariadbconnector"
            f"://{config['COOLIFY_MARIADB_USER']}"
            f":{config['COOLIFY_MARIADB_PASSWORD']}"
            f"@{config['COOLIFY_MARIADB_HOST']}"
            f":{config['COOLIFY_MARIADB_PORT']}"
            f"/{config['COOLIFY_MARIADB_DATABASE']}"
        )
        engine_target =  create_engine(target_url, echo=True)
       
        print("Connection to target MariaDB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to target MariaDB Platform: {e}")
        sys.exit(1)

    if not table_names:
        source_inspector = inspect(engine_source)
        table_names = [table for table in source_inspector.get_table_names() \
            if not table.startswith("lime_old_survey")]

    # load tables to target DB
    with engine_target.connect() as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    for table in table_names:
        print(f"table: {table}")
        dataFrame = pd.read_sql(f"SELECT * FROM {table};", engine_source)

        dataFrame.to_sql(
            name=table,
            con=engine_target,
            schema="raw",
            if_exists='replace',
            index=False
        )

def transform(config, sql_file):
    # connect to target MariaDB Platform
    try:
        print("Connecting to MariaDB")
        target_url = (
            f"mariadb+mariadbconnector"
            f"://{config['COOLIFY_MARIADB_USER']}"
            f":{config['COOLIFY_MARIADB_PASSWORD']}"
            f"@{config['COOLIFY_MARIADB_HOST']}"
            f":{config['COOLIFY_MARIADB_PORT']}"
            f"/{config['COOLIFY_MARIADB_DATABASE']}"
        )
        engine =  create_engine(target_url, echo=True)
        print("Connection to target MariaDB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to target MariaDB Platform: {e}")
        sys.exit(1)
    
    with engine.connect() as con:
        with open(sql_file, 'r') as f:
            sql = f.read()
            sql_stmts = sqlparse.split(sql)
            print(sql_stmts)
        for sql_stmt in sql_stmts:
            con.execute(text(sql_stmt))


def load(config, schema='reporting', table_names=None):
    # connect to source MariaDB Platform
    try:
        print("Connecting to target MariaDB")
        source_url = (
            f"mariadb+mariadbconnector"
            f"://{config['COOLIFY_MARIADB_USER']}"
            f":{config['COOLIFY_MARIADB_PASSWORD']}"
            f"@{config['COOLIFY_MARIADB_HOST']}"
            f":{config['COOLIFY_MARIADB_PORT']}"
            f"/{config['COOLIFY_MARIADB_DATABASE']}"
        )
        engine_source =  create_engine(source_url, echo=True)
       
        print("Connection to target MariaDB established")
    except exc.SQLAlchemyError as e:
        print(f"Error connecting to target MariaDB Platform: {e}")
        sys.exit(1)

    # connect to target PG DB
    pg_hook = PostgresHook(
        postgres_conn_id="coolify_pg"
    )
    engine_target = pg_hook.get_sqlalchemy_engine()
    print("Connected to target Postgres DB")

    if not table_names:
        source_inspector = inspect(engine_source)
        table_names = source_inspector.get_table_names(schema=schema)

    for table in table_names:
        print(f"table: {table}")
        dataFrame = pd.read_sql(f"SELECT * FROM {schema}.{table};", engine_source)

        dataFrame.to_sql(
            name=table,
            con=engine_target,
            schema="temp_dwh",
            if_exists='replace',
            index=False
        )
    
default_args = {
    'owner': OWNER,    
    'start_date': days_ago(1),
    #'email': ['airflow@example.com'],
    #'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id="extract_limesurvey_data",
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    schedule="0 6 * * *"
) as dag:

    ssh_hook = SSHHook(ssh_conn_id='limesurvey_ssh', keepalive_interval=60).get_tunnel(
        remote_port=CONFIG['LIMESURVEY_DATABASE_PORT'],
        remote_host='localhost',
        local_port=CONFIG['LIMESURVEY_DATABASE_PORT']
    ).start()

    ssh_operator = SSHOperator(
        ssh_conn_id='limesurvey_ssh',
        ssh_hook=ssh_hook,
        task_id='open_tunnel_to_SERVER',
        command='ls -al',
    )

    extract_limesurvey_data = PythonOperator(
        task_id="limesurvey_to_mariadb",
        python_callable=extract_limesurvey,
        op_kwargs={"config": CONFIG, "table_names": ["lime_group_l10ns"]}
    )

    with TaskGroup(group_id='transform') as tg1:
        get_question_groups = PythonOperator(
            task_id='get_question_groups',
            python_callable=transform,
            op_kwargs={"config": CONFIG, "sql_file": "./include/question_groups.sql"}
        )

        dummy_task = EmptyOperator(
            task_id="finish_transform"
        )

        get_question_groups >> dummy_task

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
        op_kwargs={"config": CONFIG}
    )

ssh_operator >> extract_limesurvey_data >> tg1 >> load_task
