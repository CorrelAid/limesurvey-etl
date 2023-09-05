# CFE Limesurvey

⚠️ not production ready - documentation might not work ⚠️ check most up-to-date branches for updates if things do not work.  

## Prerequisites
Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

## Usage

Create a `.env` file inside the `airflow` directory and set the Airflow UID:

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```
Add the following environment variables to the `.env` file you just created:

```bash
AIRFLOW_PG_USER=<USERNAME_FOR_AIRFLOW_DB>
AIRFLOW_PG_PASSWORD=<PASSWORD_FOR_AIRFLOW_DB_USER>
AIRFLOW_PG_DB=<AIRFLOW_DB_NAME>
_AIRFLOW_WWW_USER_USERNAME=<USERNAME_FOR_AIRFLOW_UI_LOGIN>
_AIRFLOW_WWW_USER_PASSWORD=<PW_FOR_AIRFLOW_UI_LOGIN>
AIRFLOW_CONN_LIMESURVEY_SSH='ssh://<SSH_USER>:<SSH_PASSWORD>@<SSH_HOST>:<SSH_PORT>'
AIRFLOW_CONN_COOLIFY_PG='postgres://<PG_USER>:<PG_PASSWORD>@<PG_HOST>:<PG_PORT>/<PG_DB_NAME>'
AIRFLOW_VAR_LIMESURVEY_SECRET_DATABASE_NAME="<LIMESURVEY_DB_NAME>"
AIRFLOW_VAR_LIMESURVEY_SECRET_DATABASE_PORT="<LIMESURVEY_DB_PORT>"
AIRFLOW_VAR_LIMESURVEY_SECRET_SQL_USER="<LIMESURVEY_DB_USER>"
AIRFLOW_VAR_LIMESURVEY_SQL_PASSWORD="<LIMESURVEY_DB_PW>"
AIRFLOW_VAR_COOLIFY_MARIADB_PASSWORD="<COOLIFY_MARIADB_PW>"
AIRFLOW_VAR_COOLIFY_SECRET_MARIADB_DATABASE="<COOLIFY_MARIADB_NAME>"
AIRFLOW_VAR_COOLIFY_SECRET_MARIADB_HOST="<COOLIFY_MARIADB_HOST>"
AIRFLOW_VAR_COOLIFY_SECRET_MARIADB_PORT="<COOLIFY_MARIADB_PORT>"
AIRFLOW_VAR_COOLIFY_SECRET_MARIADB_USER="<COOLIFY_MARIADB_USER>"

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

The account created has the login <_AIRFLOW_WWW_USER_USERNAME> and the password <_AIRFLOW_WWW_USER_PASSWORD>.

To run airflow, start all services:

```bash
docker-compose up
```

The Airflow UI is now running on `localhost:8080`.

To clean up the environment, run

```bash
docker-compose down --volumes --rmi all
```
# Partner organization

This project was conducted in collaboration with the [Vielfalt entscheidet](https://citizensforeurope.org/advocating_for_inclusion_page/) project of Citizens For Europe gUG.
