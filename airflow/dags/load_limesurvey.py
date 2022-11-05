import sys
import pandas as pd
from datetime import timedelta
from sqlalchemy import create_engine, inspect, exc

import socket

from airflow.utils.dates import days_ago
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator

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
        inspector = inspect(engine_source)
        table_names = [table for table in inspector.get_table_names() \
            if not table.startswith("lime_old_survey")]

    # load tables to target DB
    for table in table_names:
        print(f"table: {table}")
        dataFrame = pd.read_sql(f"SELECT * FROM {table};", engine_source)

        dataFrame.to_sql(
            name=table,
            con=engine_target,
            if_exists='replace',
            index=False
        )


default_args = {
    'owner': 'airflow',    
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

    load_limesurvey_data = PythonOperator(
        task_id="limesurvey_to_mariadb",
        python_callable=extract_limesurvey,
        op_kwargs={"config": CONFIG}
    )

ssh_operator >> load_limesurvey_data
