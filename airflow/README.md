# CFE Limesurvey

## Prerequisites
Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

## Usage

Create a `.env` file.

```bash
touch .env
```
Export the following environment variables:

```bash
AIRFLOW_UID=502
AIRFLOW_PG_USER=<DEFAULT_AIRFLOW_USER>
AIRFLOW_PG_PASSWORD=<DEFAULT_AIRFLOW_USER_PW>
AIRFLOW_PG_DB=<AIRFLOW_DB>
export AIRFLOW_CONN_LIMESURVEY_SSH='ssh://<SSH_USER>:<SSH_PASSWORD>@<SSH_HOST>:<SSH_PORT>'
export AIRFLOW_VAR_LIMESURVEY_SECRET_DATABASE_NAME="<LIMESURVEY_DB_NAME>"
export AIRFLOW_VAR_LIMESURVEY_SECRET_DATABASE_PORT="<LIMESURVEY_DB_PORT>"
export AIRFLOW_VAR_LIMESURVEY_SECRET_SQL_USER="<LIMESURVEY_DB_USER>"
export AIRFLOW_VAR_LIMESURVEY_SQL_PASSWORD="<LIMESURVEY_DB_PW>"
export AIRFLOW_VAR_COOLIFY_MARIADB_PASSWORD="<COOLIFY_MARIADB_PW>"
export AIRFLOW_VAR_COOLIFY_SECRET_MARIADB_DATABASE="<COOLIFY_MARIADB_NAME>"
export AIRFLOW_VAR_COOLIFY_SECRET_MARIADB_HOST="<COOLIFY_MARIADB_HOST>"
export AIRFLOW_VAR_COOLIFY_SECRET_MARIADB_PORT="<COOLIFY_MARIADB_PORT>"
export AIRFLOW_VAR_COOLIFY_SECRET_MARIADB_USER="<COOLIFY_MARIADB_USER>"

```

Initialize the Airflow DB.

```bash
docker-compose up airflow-init
````

After initialization is complete, you should see a message like this:

```
airflow-init_1       | Upgrades done
airflow-init_1       | Admin user <DEFAULT_AIRFLOW_USER> created
airflow-init_1       | 2.4.2
start_airflow-init_1 exited with code 0
``` 

The account created has the login `<DEFAULT_AIRFLOW_USER>` and the password `<DEFAULT_AIRFLOW_USER_PW>` exported in the `.env` file.

To run airflow, start all services:

```bash
docker-compose up
```

The Airflow UI is now running on `localhost:8080`.

To clean up the environment, run

```bash
docker-compose down --volumes --rmi all
```