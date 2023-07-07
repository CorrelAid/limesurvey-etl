# TODO: Update Documentation
# CFE Limesurvey

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

export LIMESURVEY_SSH_PORT="<LIMESURVEY_SSH_PORT_IF_SSH_IS_USED>"
export LIMESURVEY_SSH_HOST="<LIMESURVEY_SSH_HOST_IF_SSH_IS_USED>"
export LIMESURVEY_SSH_USERNAME="<LIMESURVEY_SSH_USER_IF_SSH_IS_USED>"
export LIMESURVEY_SSH_PASSWORD="<LIMESURVEY_SSH_PW_IF_SSH_IS_USED>"
export LIMESURVEY_DB_NAME="<NAME OF THE LIMESURVEY DB>"
export LIMESURVEY_DB_PORT="<PORT OF THE LIMESURVEY DB>"
export LIMESURVEY_DB_USERNAME="<LIMESURVEY DB SQL USER>"
export LIMESURVEY_DB_PASSWORD="LIMESURVEY DB SQL PASSWORD"
export LIMESURVEY_DB_HOST="127.0.0.1" # or actual host if SSH is not used

export STAGING_DB_SQLALCHEMY_DRIVER="postgresql" # or "mysql+pymysql" if Staging DB is a MYSQL DB (e.g., MariaDB)
export STAGING_DB_USERNAME="<SQL USER OF THE STAGING DB"
export STAGING_DB_PASSWORD="<PASSWORD OF THE STAGING DB SQL USER>"
export STAGING_DB_NAME="<NAME OF THE STAGING DB>"
export STAGING_DB_HOST="<HOST OF THE STAGING DB>" # host.docker.internal for usage with ariflow if DB is running on same machine as airflow
export STAGING_DB_PORT="<PORT OF THE STAGING DB>"


export REPORTING_DB_SQLALCHEMY_DRIVER="postgresql" # or "mysql+pymysql" if reporting DB is a MYSQL DB (e.g., MariaDB)
export REPORTING_DB_PASSWORD="<PW OF THE REPORTING DB SQL USER>"
export REPORTING_DB_NAME="<NAME OF THE REPORTING DB>"
export REPORTING_DB_HOST="<HOST OF THE REPORTING DB>" # host.docker.internal for usage with ariflow if DB is running on same machine as airflow
export REPORTING_DB_PORT="<PORT OF THE REPORTING DB>"
export REPORTING_DB_USERNAME="<SQL USER OF THE REPORTING DB>"


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
