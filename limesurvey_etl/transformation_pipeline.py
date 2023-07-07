from typing import Generic, TypeVar

from limesurvey_etl.config.transform_config.transformation_pipeline import (
    TransformationPipelineConfig,
)

C = TypeVar("C", bound=TransformationPipelineConfig)


class TransformationPipeline(Generic[C]):
    def __init__(self, config: C) -> None:
        self.config = config
