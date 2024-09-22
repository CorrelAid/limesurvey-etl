FROM apache/airflow:2.9.0-python3.10
USER root
RUN apt-get update \
    && apt install -yy wget \
    && sudo apt-get install -yy libmariadb3 libmariadb-dev \
    && sudo apt-get install -y python3-dev \
    && sudo apt-get install -y python3-pymysql \
    && sudo apt install -y gcc

USER airflow
WORKDIR "/usr/bin/airflow"

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-core==1.7.* dbt-postgres==1.7.* && deactivate
