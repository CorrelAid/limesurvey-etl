import os
from datetime import timedelta

from airflow import DAG
from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from limesurvey_plugin.operators.limesurvey_transform_operator import (
    LimesurveyTransformOperator,
)

from include.extract import extract_limesurvey
from include.load import load

# list of table names
SURVEY_ID = "977429"
TABLE_NAMES = [
    "lime_group_l10ns",
    "lime_questions",
    "lime_question_l10ns",
    f"lime_survey_{SURVEY_ID}",
]

CONFIGS_BASE_PATH = "include/configs/"
META_DATA_CONFIG_PATH = os.path.join(CONFIGS_BASE_PATH, "meta_data_config.yaml")
QUESTIONS_CONFIG_PATH = os.path.join(CONFIGS_BASE_PATH, "questions_config.yaml")

TRANSFORM_TASKS = [
    ("respondents", os.path.join(CONFIGS_BASE_PATH, "respondents_config.yaml")),
    ("question_groups", QUESTIONS_CONFIG_PATH),
    ("question_items", QUESTIONS_CONFIG_PATH),
    ("question_items_dict", META_DATA_CONFIG_PATH),
    ("subquestions", QUESTIONS_CONFIG_PATH),
    ("subquestions_dict", META_DATA_CONFIG_PATH),
    ("question_answers_dict", META_DATA_CONFIG_PATH),
    ("diversity_items", os.path.join(CONFIGS_BASE_PATH, "diversity_dims_config.yaml")),
    ("diversity_items_dict", META_DATA_CONFIG_PATH),
]

CONNECTION_CONF = {
    "LIMESURVEY_SQL_USER": Variable.get("LIMESURVEY_SECRET_SQL_USER"),
    "LIMESURVEY_SQL_PASSWORD": Variable.get("LIMESURVEY_SQL_PASSWORD"),
    "LIMESURVEY_DATABASE_PORT": int(Variable.get("LIMESURVEY_SECRET_DATABASE_PORT")),
    "LIMESURVEY_DATABASE_NAME": Variable.get("LIMESURVEY_SECRET_DATABASE_NAME"),
    "COOLIFY_MARIADB_HOST": Variable.get("COOLIFY_SECRET_MARIADB_HOST"),
    "COOLIFY_MARIADB_PORT": int(Variable.get("COOLIFY_SECRET_MARIADB_PORT")),
    "COOLIFY_MARIADB_USER": Variable.get("COOLIFY_SECRET_MARIADB_USER"),
    "COOLIFY_MARIADB_PASSWORD": Variable.get("COOLIFY_MARIADB_PASSWORD"),
    "COOLIFY_MARIADB_DATABASE": Variable.get("COOLIFY_SECRET_MARIADB_DATABASE"),
}

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    #'email': ['airflow@example.com'], # uncomment this line and the next and
    # add your email address to get notified on task failure
    #'email_on_failure': True, # uncomment this
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
    "execution_timeout": timedelta(minutes=5),
}

with DAG(
    dag_id="Limesurvey_ETL",
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    schedule="0 6 * * *",  # runs every day at 6 AM
) as dag:
    ssh_hook = (
        SSHHook(ssh_conn_id="limesurvey_ssh", keepalive_interval=60)
        .get_tunnel(
            remote_port=CONNECTION_CONF["LIMESURVEY_DATABASE_PORT"],
            remote_host="localhost",
            local_port=CONNECTION_CONF["LIMESURVEY_DATABASE_PORT"],
        )
        .start()
    )

    ssh_operator = SSHOperator(
        ssh_conn_id="limesurvey_ssh",
        ssh_hook=ssh_hook,
        task_id="open_tunnel_to_SERVER",
        command="ls -al",
    )

    extract_limesurvey_data = PythonOperator(
        task_id="limesurvey_to_mariadb",
        python_callable=extract_limesurvey,
        op_kwargs={"config": CONNECTION_CONF, "table_names": TABLE_NAMES},
    )

    with TaskGroup(group_id="transform") as tg1:
        task_list = []
        for task in TRANSFORM_TASKS:
            task_list.append(
                LimesurveyTransformOperator(
                    task_id=f"get_{task[0]}",
                    config_path=task[1],
                    table_name=task[0],
                    connection_config=CONNECTION_CONF,
                )
            )
        for pos, _ in enumerate(task_list[:-1]):
            task_list[pos] >> task_list[pos + 1]

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
        op_kwargs={"config": CONNECTION_CONF},
    )

ssh_operator >> extract_limesurvey_data >> tg1 >> load_task
