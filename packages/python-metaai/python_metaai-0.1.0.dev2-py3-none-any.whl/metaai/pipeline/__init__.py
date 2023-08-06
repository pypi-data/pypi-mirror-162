from typing import *
from kfp.dsl import pipeline as dsl_pipeline
import kfp.compiler
from kfp.dsl import PipelineConf

from metaai.pipeline.components.constants import ImagePullPolicy

__all__ = ["pipeline"]


class Pipeline:
    def __init__(self, func: Callable):
        self.func = func
        self._pipeline_conf = PipelineConf()
        self._pipeline_func = None

    def _set_image_pull_policy(self, value: str):
        if not value:
            return
        if value not in [
            ImagePullPolicy.Always.value,
            ImagePullPolicy.IfNotPresent.value,
            ImagePullPolicy.Never.value,
        ]:
            raise ValueError(
                "Invalid image_pull_policy. Must be one of `Always`, `Never`, `IfNotPresent`,"
                "see enum of metaai.pipeline.constants.ImagePullPolicy"
            )
        self._pipeline_conf.set_image_pull_policy(value)

    def __call__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image_pull_policy: Optional[str] = None,
    ):
        self._pipeline_func = dsl_pipeline(name=name, description=description)(
            self.func
        )

        self._set_image_pull_policy(image_pull_policy)
        return self

    def to_save(self, file_name: str, file_type: str = "yaml"):
        kfp.compiler.Compiler().compile(
            self.func, f"{file_name}.{file_type}", pipeline_conf=self._pipeline_conf
        )

    def to_yaml(self, file_name):
        self.to_save(file_name=file_name, file_type="yaml")


def pipeline(
    name: Optional[str] = None,
    description: Optional[str] = None,
    image_pull_policy: Optional[str] = None,
):
    def wrapper(func):
        return Pipeline(func)(
            name=name, description=description, image_pull_policy=image_pull_policy
        )

    return wrapper
