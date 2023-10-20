# Creation and configuration of new ETL pipelines in Airflow

## Step 1: Creating an ETL configuration
- add a new `.yaml` file inside `airflow/dags/configs`
- add your desired ETL-steps (i.e., extract, transform, load) to the configuration file (see the [ETL Configs How To](etl-config-how-to.md) for a detailed description of all available configuration options), for example:

    ```yaml
    extract:
      extract_type: limesurvey_extract
      tables:
        - lime_questions

    transformation_pipelines:
      - table_name: question_items
        staging_schema: staging
        source_data:
          source_tables:
            - table_name: lime_questions
              columns:
                - qid AS question_item_id
                - title AS question_item_title
                - gid AS question_group_id
                - type AS type_major
                - type AS type_minor
        transform_steps:
          - transform_type: join_with_csv_mapping
            mapping_path: /opt/airflow/include/mappings/Mapping_LS-QuestionTypesMajor.csv
            mapping_delimiter: ;
            keep_columns:
              - "Fragetyp Major (CFE)"
            left_on: type_major
            right_on: "Fragetyp-ID (LS)"
            how: left
          - transform_type: rename_columns
            colname_to_colname: "Fragetyp Major (CFE)": type_major

    load:
      load_type: reporting_db_load
      staging_schema: staging
      target_schema: reporting
      tables:
          - question_items
    ```
    In this example, the table `lime_questions` is extracted from Limesurvey and stored in the `raw` schema of the staging database based on the `.env` file (if you do not have an `.env` file yet, follow the procedure desscribed [here](../installation.md#setting-necessary-environment-variables)).

    Next, a transformation pipeline is defined that transforms data based on `raw.lime_questions` (i.e., the extracted table) and stores it in a table `question_items` in the `staging` schema of the staging database. The transformation pipeline consists of two transformation steps: first, the data is joined with a mapping `.csv`-file stored in the `airflow/include/mappings` directory (note: to be available, mapping files must be placed inside the `airflow/include` directory and the `/opt/` prefix is always required when specifying the path in the configuration file). Second, the column "Fragetyp Major (CFE)" is renamed to "type_major".

    Finally, the load step loads the `question_items` table to the `reporting` schema of the database.

- **you can choose from a variety of extractors, transformers, and loaders that can be combined in any way**
- **detailed documentation on the types of extractors, transformers, and loaders as well as their parameters can be found [here](./etl-config-how-to.md)**

## Step 2: Creating a DAG
A DAG (Directed Acyclic Graph) is a pipeline that is executed by Airflow. To run your ETL job in Airflow, you must add a DAG-file.

- Add a file named `<YOUR_PIPELINE_NAME>_dag.py` to the `airflow/dags` directory
- Copy the following code and replace the placeholders with your values (Note: in a future version, this procedure will be simplified by allowing to create DAGs from configuration files):
  ```python
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

  # REPLACE THE FOLLOWING VALUES

  # replace with the name of your etl configuration file
  CONFIG_FILE_NAME = "<YOUR_ETL_CONFIG_FILE>.yaml"
  # give your DAG a unique name (it will be used to be displayed in the Airflow UI)
  DAG_ID = "<YOUR_DAG_NAME>"
  # set the schedule defining when your DAG should run using a crontab or None
  # e.g., "0 0 * * *" for once a day at 12:00 AM
  DAG_SCHEDULE = "YOUR_DAG_SCHEDULE"

  # OPTIONALLY MODIFY THE AIRFLOW DEFAULT_ARGS (advanced users)
  DEFAULT_ARGS = {
      "start_date": days_ago(1),
      "retries": 1,
      "retry_delay": timedelta(seconds=30),
      "execution_timeout": timedelta(minutes=5),
  }

  PIPELINE = Pipeline.get_pipeline(Path(f"/opt/airflow/dags/configs/{CONFIG_FILE_NAME}"))

  with DAG(
      dag_id=DAG_ID,
      default_args=DEFAULT_ARGS,
      catchup=False,
      max_active_runs=1,
      schedule=DAG_SCHEDULE,
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

  ```

## Step 3: Monitoring / running a DAG
Save the changes you made. You should now be able to see the DAG with your `DAG_ID` in the Airflow UI. You can click on the DAG to open Airflow's grid view and monitor the DAG runs.
