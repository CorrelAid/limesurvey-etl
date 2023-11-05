from limesurvey_etl.connectors.base_db_connect import BaseDBConnect
from limesurvey_etl.settings.reporting_db_settings import ReportingDBSettings


class ReportingDBConnect(BaseDBConnect):
    def __init__(self, settings: ReportingDBSettings) -> None:
        super().__init__(settings)
        self.db_host = settings.reporting_db_host
        self.db_port = settings.reporting_db_port
        self.db_user = settings.reporting_db_username
        self.db_password = settings.reporting_db_password
        self.db_name = settings.reporting_db_name
        self.db_driver = settings.reporting_db_sqlalchemy_driver
