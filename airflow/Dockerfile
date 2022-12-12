FROM apache/airflow:2.4.2-python3.9
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
COPY dags/ /opt/airflow/dags
