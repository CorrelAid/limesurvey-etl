import os

from airflow.models import Variable

os.environ["LIMESURVEY_DB_NAME"] = Variable.get("LIMESURVEY_SECRET_DB_NAME")
os.environ["LIMESURVEY_DB_PORT"] = Variable.get("LIMESURVEY_SECRET_DB_PORT")
os.environ["LIMESURVEY_DB_USERNAME"] = Variable.get("LIMESURVEY_SECRET_DB_USERNAME")
os.environ["LIMESURVEY_DB_PASSWORD"] = Variable.get("LIMESURVEY_DB_PASSWORD")
os.environ["LIMESURVEY_DB_HOST"] = (
    Variable.get("LIMESURVEY_SECRET_DB_HOST") or "127.0.0.1"
)
os.environ["LIMESURVEY_SHH_HOST"] = Variable.get("LIMESURVEY_SSH_HOST")
os.environ["LIMESURVEY_SSH_USERNAME"] = Variable.get("LIMESURVEY_SSH_USERNAME")
os.environ["LIMESURVEY_SSH_PASSWORD"] = Variable.get("LIMESURVEY_SSH_PASSWORD")
os.environ["LIMESURVEY_SSH_PORT"] = Variable.get("LIMESURVEY_SSH_PORT") or 22

os.environ["STAGING_DB_SQLALCHEMY_DRIVER"] = Variable.get(
    "STAGING_DB_SQLALCHEMY_DRIVER"
)
os.environ["STAGING_DB_PASSWORD"] = Variable.get("STAGING_DB_PASSWORD")
os.environ["LIMESURVEY_DB_PORT"] = Variable.get("STAGING_DB_PORT")
os.environ["STAGING_DB_NAME"] = Variable.get("STAGING_DB_NAME")
os.environ["STAGING_DB_PASSWORD"] = Variable.get("STAGING_DB_PASSWORD")
os.environ["STAGING_DB_HOST"] = Variable.get("STAGING_DB_HOST")

os.environ["REPORTING_DB_SQLALCHEMY_DRIVER"] = Variable.get(
    "REPORTING_DB_SQLALCHEMY_DRIVER"
)
os.environ["REPORTING_DB_PASSWORD"] = Variable.get("REPORTING_DB_PASSWORD")
os.environ["REPORTING_DB_NAME"] = Variable.get("REPORTING_DB_NAME")
os.environ["REPORTING_DB_HOST"] = Variable.get("REPORTING_DB_HOST")
os.environ["REPORTING_DB_PORT"] = Variable.get("REPORTING_DB_PORT")
os.environ["REPORTING_DB_USERNAME"] = Variable.get("REPORTING_DB_USERNAME")
