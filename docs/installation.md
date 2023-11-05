# Getting Started
The following documentation describes the installation process that will get you up and running to implement your own ETL jobs.

## Prerequisites
Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

If you want to contribute to this project or run an ETL pipeline locally without Airflow, you need to install the required dependencies.

- [`Python`](https://www.python.org/)>=3.10.0
- [`poetry`](https://python-poetry.org/)>=1.6.1

Once you installed the dependencies, `cd` into the project's root directory in your terminal and run `poetry install --with dev` to install the required python dependencies into a virtual environment. To activate the virtual environment, run `poetry shell`.

## Running ETL pipelines
You can run your ETL pipelines either locally with Python or using Airflow.

### 1. Running an ETL pipeline locally
To run an ETL pipeline locally, you must set a number of environment variables.

Create a `.env` file and store it at the project repository's root directory. Open the `.env` file you just created in your IDE or text editor and append the following three blocks of environment variables to it:

- **Limesurvey DB related variables**: These variables are required for the platform to connect with the Limesurvey database. You must provide the variables for establishing an SSH connection as well as for the actual Limesurvey database.
- **Staging database related variables**: The staging database is where the raw and intermediary data are stored. **this database is NOT created automatically for you!** You can provide values for a MySQL DB / MariaDB (set `STAGING_DB_SQLALCHEMY_DRIVER="mysql+pymysql"`) or a PostgresDB (set `STAGING_DB_SQLALCHEMY_DRIVER="postgresql"`). Other databases are currently not supported.
- **Reporting database related variables**:  The reporting database is where the final (i.e., reporting) data is stored. **this database is NOT created automatically for you!** You can provide values for a MySQL DB / MariaDB (set `STAGING_DB_SQLALCHEMY_DRIVER="mysql+pymysql"`) or a PostgresDB (set `STAGING_DB_SQLALCHEMY_DRIVER="postgresql"`). Other databases are currently not supported. **It is possible to use the same database as staging and reporting database**.

```bash
# Variables required to connect with the Limesurvey Database
LIMESURVEY_USE_SSH=True # set to False if ssh is not used
LIMESURVEY_SSH_PORT="<LIMESURVEY_SSH_PORT_IF_SSH_IS_USED_ELSE_DELETE_VARIABLE>"
LIMESURVEY_SSH_HOST="<LIMESURVEY_SSH_HOST_IF_SSH_IS_USED_ELSE_DELETE_VARIABLE>"
LIMESURVEY_SSH_USERNAME="<LIMESURVEY_SSH_USER_IF_SSH_IS_USED_ELSE_DELETE_VARIABLE>"
LIMESURVEY_SSH_PASSWORD="<LIMESURVEY_SSH_PW_IF_SSH_IS_USED_ELSE_DELETE_VARIABLE>"
LIMESURVEY_DB_NAME="<NAME OF THE LIMESURVEY DB>"
LIMESURVEY_DB_PORT="<PORT OF THE LIMESURVEY DB>"
LIMESURVEY_DB_USERNAME="<LIMESURVEY DB SQL USER>"
LIMESURVEY_DB_PASSWORD="LIMESURVEY DB SQL PASSWORD"
LIMESURVEY_DB_HOST="127.0.0.1" # always 127.0.0.1 if SSH is used, or actual host if SSH is not used

# Variables for connecting with the database where you want raw and intermediary data to be stored
STAGING_DB_SQLALCHEMY_DRIVER="postgresql" # "postgresql" for a postgres DB or "mysql+pymysql" if Staging DB is a MYSQL DB (e.g., MariaDB)
STAGING_DB_USERNAME="<SQL USER OF THE STAGING DB"
STAGING_DB_PASSWORD="<PASSWORD OF THE STAGING DB SQL USER>"
STAGING_DB_NAME="<NAME OF THE STAGING DB>"
STAGING_DB_HOST="<HOST OF THE STAGING DB>"
STAGING_DB_PORT="<PORT OF THE STAGING DB>"

# Variables for connecting with the database where you want the final (i.e., reporting) data to be stored
# Can be the same database as the staging database
REPORTING_DB_SQLALCHEMY_DRIVER="postgresql" # "postgresql" for a postgres DB or "mysql+pymysql" if reporting DB is a MYSQL DB (e.g., MariaDB)
REPORTING_DB_PASSWORD="<PW OF THE REPORTING DB SQL USER>"
REPORTING_DB_NAME="<NAME OF THE REPORTING DB>"
REPORTING_DB_HOST="<HOST OF THE REPORTING DB>"
REPORTING_DB_PORT="<PORT OF THE REPORTING DB>"
REPORTING_DB_USERNAME="<SQL USER OF THE REPORTING DB>"
```

Next, you can start adding an ETL pipeline configuration as described in the [User Guide](user-how-to/creating-dags.md) section.

Once you created a pipeline configuration, you can run it from your terminal by entering the following command:

`poetry run python -m limesurvey_etl --config_file <PATH/TO/YOUR/config.yaml --step all`

- The `--config_file` flag specifies the path to the configuration `.yaml`-file to be used for the pipeline
- The `--steps` flag specifies which step(s) of the ETL pipeline should be executed. Choices:
    - `extract`: Only the extract step is executed.
    - `transform`: Only the transform step is executed.
    - `load`: Only the load step is executed.
    - `all`: All steps (i.e., extract, transform, and load) are executed.
### 2. Orchestrating ETL pipelines with Airflow
This project supports [Airflow](https://airflow.apache.org/) to orchestrate ETL pipelines.

#### Setting necessary environment variables
In order to run Airflow and allow the ETL pipelines to communicate with the source and target databases, you must set a number of environment variables.

Create a `.env` file and set the Airflow UID by running the following command from the project's root directory:

```bash
echo -e "AIRFLOW_UID=$(id -u)" >> .env
```

Open the `.env` file you just created in your IDE or text editor and append the following four blocks of environment variables to it:

- **Airflow related variables**: You can choose arbitrary values here. These are required for logging into the Airflow UI and the Airflow DB (advanced users), which contains Airflow related metadata.
- **Limesurvey DB related variables**: These variables are required for the platform to connect with the Limesurvey database. You must provide the variables for establishing an SSH connection as well as for the actual Limesurvey database.
- **Staging database related variables**: The staging database is where the raw and intermediary data are stored. You must provide the database credentials to an existing database maintained by you, i.e., **this database is NOT created automatically for you!** You can provide values for a MySQL DB / MariaDB (set `STAGING_DB_SQLALCHEMY_DRIVER="mysql+pymysql"`) or a PostgresDB (set `STAGING_DB_SQLALCHEMY_DRIVER="postgresql"`). Other databases are currently not supported. **Note:** If the database is running on the same machine as airflow, then set `STAGING_DB_HOST=host.docker.internal`!
- **Reporting database related variables**:  The reporting database is where the final (i.e., reporting) data is stored. **this database is NOT created automatically for you!** You can provide values for a MySQL DB / MariaDB (set `STAGING_DB_SQLALCHEMY_DRIVER="mysql+pymysql"`) or a PostgresDB (set `STAGING_DB_SQLALCHEMY_DRIVER="postgresql"`). Other databases are currently not supported. **Note:** If the database is running on the same machine as airflow, then set `REPORTING_DB_HOST=host.docker.internal`! **It is possible to use the same database as staging and reporting database**.

```bash
# Airflow related variables
AIRFLOW_PG_USER="<USERNAME_FOR_AIRFLOW_DB>" # choose a username for the airflow db
AIRFLOW_PG_PASSWORD="<PASSWORD_FOR_AIRFLOW_DB_USER>" # set a password for the airflow db user
AIRFLOW_PG_DB="<AIRFLOW_DB_NAME>" # choose a name for the airflow db
_AIRFLOW_WWW_USER_USERNAME="<USERNAME_FOR_AIRFLOW_UI_LOGIN>" # choose an admin username for logging into the Airflow UI (you can add additional users later via the "Security" tab in the Airflow UI)
_AIRFLOW_WWW_USER_PASSWORD="<PW_FOR_AIRFLOW_UI_LOGIN>" # choose a password to login to the Airflow UI

# Variables required to connect with the Limesurvey Database
LIMESURVEY_SSH_PORT="<LIMESURVEY_SSH_PORT_IF_SSH_IS_USED_ELSE_DELETE_VARIABLE>"
LIMESURVEY_SSH_HOST="<LIMESURVEY_SSH_HOST_IF_SSH_IS_USED_ELSE_DELETE_VARIABLE>"
LIMESURVEY_SSH_USERNAME="<LIMESURVEY_SSH_USER_IF_SSH_IS_USED_ELSE_DELETE_VARIABLE>"
LIMESURVEY_SSH_PASSWORD="<LIMESURVEY_SSH_PW_IF_SSH_IS_USED_ELSE_DELETE_VARIABLE>"
LIMESURVEY_DB_NAME="<NAME OF THE LIMESURVEY DB>"
LIMESURVEY_DB_PORT="<PORT OF THE LIMESURVEY DB>"
LIMESURVEY_DB_USERNAME="<LIMESURVEY DB SQL USER>"
LIMESURVEY_DB_PASSWORD="LIMESURVEY DB SQL PASSWORD"
LIMESURVEY_DB_HOST="127.0.0.1" # or actual host if SSH is not used

# Variables for connecting with the database where you want raw and intermediary data to be stored
STAGING_DB_SQLALCHEMY_DRIVER="postgresql" # "postgresql" for a postgres DB or "mysql+pymysql" if Staging DB is a MYSQL DB (e.g., MariaDB)
STAGING_DB_USERNAME="<SQL USER OF THE STAGING DB"
STAGING_DB_PASSWORD="<PASSWORD OF THE STAGING DB SQL USER>"
STAGING_DB_NAME="<NAME OF THE STAGING DB>"
STAGING_DB_HOST="<HOST OF THE STAGING DB>" # host.docker.internal for usage with ariflow if DB is running on same machine as airflow
STAGING_DB_PORT="<PORT OF THE STAGING DB>"

# Variables for connecting with the database where you want the final (i.e., reporting) data to be stored
# Can be the same database as the staging database
REPORTING_DB_SQLALCHEMY_DRIVER="postgresql" # "postgresql" for a postgres DB or "mysql+pymysql" if reporting DB is a MYSQL DB (e.g., MariaDB)
REPORTING_DB_PASSWORD="<PW OF THE REPORTING DB SQL USER>"
REPORTING_DB_NAME="<NAME OF THE REPORTING DB>"
REPORTING_DB_HOST="<HOST OF THE REPORTING DB>" # host.docker.internal for usage with ariflow if DB is running on same machine as airflow
REPORTING_DB_PORT="<PORT OF THE REPORTING DB>"
REPORTING_DB_USERNAME="<SQL USER OF THE REPORTING DB>"
```

#### Setup Airflow
To start Airflow, make sure the Docker daemon is running (e.g., by starting docker desktop or starting the docker service) and run
```bash
docker compose up
```
This may take a while. Once the setup is complete, you should repeatedly see a message similar to the following in your terminal:
```
limesurvey-etl-airflow-webserver-1  | 127.0.0.1 - - [19/Oct/2023:14:16:17 +0000] "GET /health HTTP/1.1" 200 141 "-" "curl/7.74.0"
```

The Airflow Webserver is now running and the Airflow UI can be accessed through a regular browser by entering the following URL: `localhost:8080`. Use the credentials defined in your `.env` file (`_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD`) to login. You can add additional users via the "Security" tab at the top of the Airflow UI after successful login. Airflow DAGs will run depending on their schedules as long as Airflow is running. Press `control+c` or `strg+c` to stop the process, depending on your operating system.

#### Adding ETL pipelines
Once Airflow is up and running, you can start adding your ETL pipelines as described in the [User Guide](user-how-to/creating-dags.md).

#### Clean up
To clean up the environment, run
```
docker compose down --volumes --rmi all
```
Note: This will not delete any Limesurvey data or data generated during an ETL pipeline run from your target databases, but only remove the Airflow environment.# Partner organization

This project was conducted in collaboration with the [Vielfalt entscheidet](https://citizensforeurope.org/advocating_for_inclusion_page/) project of Citizens For Europe gUG.
