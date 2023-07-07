FROM apache/airflow:2.4.3-python3.10
USER root
RUN apt-get update \
    && apt install -yy wget \
    && sudo apt-get install -yy libmariadb3 libmariadb-dev \
    && sudo apt-get install -y python3-dev \
    && sudo apt-get install -y python3-pymysql \
    && sudo apt install -y gcc
USER airflow
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./airflow/dags/ /opt/airflow/dags/
COPY ./limesurvey_etl/ /opt/airflow/include/limesurvey_etl/
WORKDIR /airflow
