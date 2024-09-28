# Getting Started
The following documentation describes the installation process that will get you up and running to implement your own ETL jobs.

## Prerequisites
Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

#### Local Development
If you want to contribute to this project or run an ETL pipeline locally without Airflow, you need to install the required dependencies.

- [`Python`](https://www.python.org/)>=3.10.0
- [`poetry`](https://python-poetry.org/)>=1.6.1

Once you installed the dependencies, `cd` into the project's root directory in your terminal and run `poetry install --with dev` to install the required python dependencies into a virtual environment. To activate the virtual environment, run `poetry shell`.

## Running ETL pipelines
This project uses [Airflow](https://airflow.apache.org/) to orchestrate ETL pipelines.

#### Setting necessary environment variables
In order to run Airflow and allow the ETL pipelines to communicate with the source and target databases, you must set a number of environment variables.

Create a `.env` file and set the Airflow UID by running the following command from the project's root directory:

```bash
echo -e "AIRFLOW_UID=$(id -u)" >> .env
```

Open the `.env` file you just created in your IDE or text editor and append the following four blocks of environment variables to it:

- **Airflow related variables**: You can choose arbitrary values here. These are required for logging into the Airflow UI and the Airflow DB (advanced users), which contains Airflow related metadata.
- **Limesurvey DB related variables**: These variables are required for the platform to connect with the Limesurvey database. You must provide the variables for establishing an SSH connection as well as for the actual Limesurvey database. The `AIRFLOW_VAR_`/`AIRFLOW_CONN` prefixes ensure they are available as Airflow Variables or Connections, respectively.
- **Target database related variables**: The target database is where the raw and transformed data are stored. **This database can, optionally, be created for you upon deployment when [running ETL pipelines with Airflow](#2-orchestrating-etl-pipelines-with-airflow), but you can also use your own database to run pipelines locally.**


```bash
AIRFLOW_PG_PASSWORD="<AIRFLOW_PG_PASSWORD>" # arbitrary value
_AIRFLOW_WWW_USER_USERNAME="<USERNAME_TO_LOGIN_TO_AIRFLOW_UI>"
_AIRFLOW_WWW_USER_PASSWORD="<PASSWORD_TO_LOGIN_TO_AIRFLOW_UI>"

# Variables required to connect with the Limesurvey Database
AIRFLOW_CONN_LIMESURVEY_SSH='ssh://<LIMESURVEY_USERNAME>:<LIMESURVEY_PASSWORD>@<LIMESURVEY_HOST>:<LIMESURVEY_PORT>' # replace with actual values to SSH into the limesurvey host, e.g., 'ssh://limeuser:secretpw@10.0.0.1:22'
AIRFLOW_VAR_LIMESURVEY_SECRET_DATABASE_NAME="<NAME_OF_LIMESURVEY_DB>"
AIRFLOW_VAR_LIMESURVEY_SECRET_DATABASE_PORT="<LIMESURVEY_DB_PORT>"
AIRFLOW_VAR_LIMESURVEY_SECRET_SQL_USER="<LIMESURVEY_DB_USERNAME>"
AIRFLOW_VAR_LIMESURVEY_SQL_PASSWORD="<LIMESURVEY_DB_PASSWORD>"

# Variables for connecting with the database where you want the raw and transformed data to be stored.
# You can choose arbitrary values for the following variables if you use the full deployment (i.e., a database is created for you in Docker) or add values to use your own Postgres DB
TARGET_DB_NAME="<NAME OF THE DATABASE>"
TARGET_DB_USERNAME="<USERNAME TO AUTHENTICATE WITH THE DB>"
TARGET_DB_PASSWORD="<PASSWORD TO AUTHENTICATE WITH THE DB"
# TARGET_DB_HOST=<HOST_OF_DB> # Only if using your own database
```

#### Setup Airflow
To start Airflow, make sure the Docker daemon is running (e.g., by starting docker desktop or starting the docker service) and run
```bash
docker compose --profile fullDeployment up
```
This will setup a target postgres database, an airflow database, and the airflow components. This may take a while. Once the setup is complete, you should repeatedly see a message similar to the following in your terminal:
```
limesurvey-etl-airflow-webserver-1  | 127.0.0.1 - - [19/Oct/2023:14:16:17 +0000] "GET /health HTTP/1.1" 200 141 "-" "curl/7.74.0"
```
In case you do not want a full deployment including a target database, run the following command instead:
```bash
docker compose up
```

The Airflow Webserver is now running and the Airflow UI can be accessed through a regular browser by entering the following URL: `localhost:8080`. Use the credentials defined in your `.env` file (`_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD`) to login. You can add additional users via the "Security" tab at the top of the Airflow UI after successful login. Airflow DAGs will run depending on their schedules as long as Airflow is running. If using the `fullDeployment` profile, the target DB is available at `localhost:5433`.

Press `control+c` or `strg+c` to stop the process in your terminal, depending on your operating system. **This will shut down all docker containers, including the target database.**

By default, three example DAGs should be visible in the Airflow UI.

- `extract_limesurvey_data`: This DAG includes functionality to extract the raw data from Limesurvey using SSH and load it to the `raw` schema in the target database.
- `run_dbt_meta_tables`: This DAG runs the dbt models to transform the meta tables, e.g., question ansers, question items, respondents, etc. After successful completion, the transformed data will be available in the reporting schema of the target database.
- `run_dbt_surveys`: This DAG runs the dbt models to transform the actual survey data. After successful completion, the transformed data will be available in the reporting schema of the target database.

#### Adding ETL pipelines
Once Airflow is up and running, you can start adding your ETL pipelines as described in the [User Guide](user-how-to/creating-dags.md).

#### Accessing the data when using the full deployment
When you run the `docker compose up` command with the `--profile fullDeployment` flag, a target database will be created for you. It is served at `localhost:5433` and you can access it using a tool like [pgcli](https://www.pgcli.com/) or [dbeaver](https://dbeaver.io/).

For example, you can connect using pgcli using the following command in your terminal:

```bash
pgcli -u <TARGET_DB_USERNAME> -p 5433 -h localhost -d <TARGET_DB_NAME>
```
You will be asked to enter your password, i.e., `<TARGET_DB_PASSWORD>`.

#### Clean up
To clean up the environment, run
```
docker compose down --volumes --rmi all
```
Note: This will not delete any Limesurvey data. However, if using the full deployment, it will alsow remove all data in the target Postgres Database.
