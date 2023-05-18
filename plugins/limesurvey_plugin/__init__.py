from airflow.plugins_manager import AirflowPlugin
from limesurvey_plugin.operators.limesurvey_transform_operator import (
    LimesurveyTransformOperator,
)


class LimesurveyPlugin(AirflowPlugin):
    name = "limesurvey_plugin"
