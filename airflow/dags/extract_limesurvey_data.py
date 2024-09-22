from datetime import timedelta

from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from include.extract import extract_limesurvey

from airflow import DAG

# list of table names to be extracted from limesurvey
TABLE_NAMES = [
    "lime_group_l10ns",
    "lime_questions",
    "lime_question_l10ns",
    "lime_survey_977429",
]

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
    dag_id="extract_limesurvey_data",
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    schedule="0 5 * * *",  # runs every day at 5 AM
) as dag:
    ssh_hook = (
        SSHHook(ssh_conn_id="limesurvey_ssh", keepalive_interval=60)
        .get_tunnel(
            remote_port=int(Variable.get("LIMESURVEY_SECRET_DATABASE_PORT")),
            remote_host="localhost",
            local_port=int(Variable.get("LIMESURVEY_SECRET_DATABASE_PORT")),
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
        op_kwargs={"target_db_conn_id": "target_db", "table_names": TABLE_NAMES},
    )

    trigger_dbt_meta_tables_dag = TriggerDagRunOperator(
        task_id="trigger_run_dbt_meta_tables",
        trigger_dag_id="run_dbt_meta_tables",
        wait_for_completion=True,
    )

    trigger_dbt_surveys_dag = TriggerDagRunOperator(
        task_id="trigger_run_dbt_surveys",
        trigger_dag_id="run_dbt_surveys",
        wait_for_completion=True,
    )

    (
        ssh_operator
        >> extract_limesurvey_data
        >> trigger_dbt_meta_tables_dag
        >> trigger_dbt_surveys_dag
    )
