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

from include.config import CONFIG
from include.extract import extract_limesurvey
from include.load import load
from include.transformations.diversity_dimensions import get_diversity_items
from include.transformations.meta_data import (
    get_diversity_items_dict,
    get_question_answers_dict,
    get_question_items_dict,
    get_subquestions_dict,
)
from include.transformations.questions import (
    get_question_groups,
    get_question_items,
    get_subquestions,
)
from include.transformations.respondents import get_respondents

# list of table names
TABLE_NAMES = ["lime_group_l10ns", "lime_questions"]

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
        respondents = PythonOperator(
            task_id="get_respondents",
            python_callable=get_respondents,
            op_kwargs={
                "config": CONNECTION_CONF,
                "columns": CONFIG["respondents"],
            },
        )

        question_groups = PythonOperator(
            task_id="get_question_groups",
            python_callable=get_question_groups,
            op_kwargs={
                "config": CONNECTION_CONF,
                "columns": CONFIG["question_groups"],
            },
        )

        question_items = PythonOperator(
            task_id="get_question_items",
            python_callable=get_question_items,
            op_kwargs={
                "config": CONNECTION_CONF,
                "columns": CONFIG["question_items"],
            },
        )

        # question_items_dict = PythonOperator(
        #     task_id="get_question_items_dict",
        #     python_callable=get_question_items_dict,
        #     op_kwargs={
        #         "CONNECTION_CONF": CONNECTION_CONF,
        #         "columns": CONFIG["question_items_dict"],
        #     },
        # )

        question_items_dict = LimesurveyTransformOperator(
            task_id="get_question_items_dict",
            config_path="include/config.yaml",
            table_name="question_items_dict",
            connection_config=CONNECTION_CONF,
        )

        subquestions = PythonOperator(
            task_id="get_subquestions",
            python_callable=get_subquestions,
            op_kwargs={
                "config": CONNECTION_CONF,
                "columns": CONFIG["subquestions"],
            },
        )

        subquestions_dict = PythonOperator(
            task_id="get_subquestions_dict",
            python_callable=get_subquestions_dict,
            op_kwargs={
                "config": CONNECTION_CONF,
                "columns": CONFIG["subquestions_dict"],
            },
        )

        question_answers_dict = PythonOperator(
            task_id="get_question_answers_dict",
            python_callable=get_question_answers_dict,
            op_kwargs={
                "config": CONNECTION_CONF,
                "columns": CONFIG["question_answers_dict"],
            },
        )

        diversity_items = PythonOperator(
            task_id="get_diversity_items",
            python_callable=get_diversity_items,
            op_kwargs={
                "config": CONNECTION_CONF,
                "columns": CONFIG["diversity_items"],
            },
        )

        diversity_items_dict = PythonOperator(
            task_id="get_diversity_items_dict",
            python_callable=get_diversity_items_dict,
            op_kwargs={
                "config": CONNECTION_CONF,
                "columns": CONFIG["diversity_items_dict"],
            },
        )

        (
            respondents
            >> question_groups
            >> question_items
            >> question_items_dict
            >> subquestions
            >> subquestions_dict
            >> question_answers_dict
            >> diversity_items
            >> diversity_items_dict
        )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
        op_kwargs={"config": CONNECTION_CONF},
    )

ssh_operator >> extract_limesurvey_data >> tg1 >> load_task
