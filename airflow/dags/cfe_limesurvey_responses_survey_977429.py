from datetime import datetime, timedelta
from pathlib import Path

from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.contrib.operators.ssh_operator import SSHOperator
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup

from airflow import DAG
from limesurvey_etl.etl_pipeline import Pipeline

PIPELINE = Pipeline.get_pipeline(
    Path("/opt/airflow/dags/configs/cfe_responses_survey_977429.yaml")
)

DEFAULT_ARGS = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
    "execution_timeout": timedelta(minutes=5),
}

with DAG(
    dag_id="cfe-limesurvey-responses-survey-977429",
    default_args=DEFAULT_ARGS,
    catchup=False,
    max_active_runs=1,
    schedule_interval=None,
) as dag:
    extract_limesurvey_data = PythonOperator(
        task_id="extract", python_callable=PIPELINE.run_extract
    )

    with TaskGroup(group_id="transform") as transform:
        task_list = []
        for transformation_pipeline in PIPELINE.transformation_pipelines:
            task_id = transformation_pipeline["table_name"]
            task_list.append(
                PythonOperator(
                    task_id=task_id,
                    python_callable=PIPELINE.run_transform,
                    op_kwargs={"table_name": task_id},
                )
            )
            for pos, _ in enumerate(task_list[:-1]):
                task_list[pos] >> task_list[pos + 1]

    load_data = PythonOperator(task_id="load", python_callable=PIPELINE.run_load)


extract_limesurvey_data >> transform >> load_data
