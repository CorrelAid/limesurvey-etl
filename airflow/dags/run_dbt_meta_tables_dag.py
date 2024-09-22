import os
from datetime import timedelta
from pathlib import Path

from airflow.utils.dates import days_ago
from cosmos import DbtDag, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping

DEFAULT_DBT_ROOT_PATH = "/opt/airflow/limesurvey_dbt"
DBT_ROOT_PATH = Path(os.getenv("DBT_ROOT_PATH", DEFAULT_DBT_ROOT_PATH))

profile_config = ProfileConfig(
    profile_name="limesurvey_dbt",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="target_db",
        profile_args={"schema": "staging"},
    ),
)

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

# [START local_example]
basic_cosmos_dag = DbtDag(
    # dbt/cosmos-specific parameters
    project_config=ProjectConfig(
        dbt_project_path=DBT_ROOT_PATH, seeds_relative_path="seeds"
    ),
    render_config=RenderConfig(
        emit_datasets=False,
        select=["staging.meta_tables", "tag:limesurvey_seeds", "config.schema:staging"],
    ),
    profile_config=profile_config,
    operator_args={
        "install_deps": True,  # install any necessary dependencies before running any dbt command
        "full_refresh": True,  # used only in dbt commands that support this flag
    },
    # normal dag parameters
    schedule=None,
    catchup=False,
    dag_id="run_dbt_meta_tables",
    max_active_runs=1,
    default_args={"retries": 2},
)
