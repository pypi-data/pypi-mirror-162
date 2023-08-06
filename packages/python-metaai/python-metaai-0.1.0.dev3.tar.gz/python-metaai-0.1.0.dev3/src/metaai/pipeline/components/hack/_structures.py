from typing import *
from kfp.components import _structures as structures
from kfp.components._structures import CommandlineArgumentType


class HackContainerSpec(structures.ModelBase):
    _serialized_names = {
        "file_outputs": "fileOutputs",
        # "image_pull_policy": "imagePullPolicy",
    }

    def __init__(
        self,
        image: str,
        command: Optional[List[CommandlineArgumentType]] = None,
        args: Optional[List[CommandlineArgumentType]] = None,
        env: Optional[Mapping[str, str]] = None,
        file_outputs: Optional[Mapping[str, str]] = None,
        # image_pull_policy: str = None,
    ):

        super().__init__(locals())


class HackContainerImplementation(structures.ModelBase):
    def __init__(
        self,
        container: HackContainerSpec,
    ):
        super().__init__(locals())
