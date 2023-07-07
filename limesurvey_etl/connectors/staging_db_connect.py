from limesurvey_etl.connectors.base_db_connect import BaseDBConnect
from limesurvey_etl.settings.staging_db_settings import StagingDBSettings


class StagingDBConnect(BaseDBConnect):
    def __init__(self, settings: StagingDBSettings) -> None:
        super().__init__(settings)
        self.db_host = settings.staging_db_host
        self.db_port = settings.staging_db_port
        self.db_user = settings.staging_db_username
        self.db_password = settings.staging_db_password
        self.db_name = settings.staging_db_name
        self.db_driver = settings.staging_db_sqlalchemy_driver
