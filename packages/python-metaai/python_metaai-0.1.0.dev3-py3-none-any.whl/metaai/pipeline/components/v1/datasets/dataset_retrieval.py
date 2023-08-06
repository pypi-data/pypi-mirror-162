from typing import Dict, Optional
from kfp.components import OutputPath

from ... import settings
from ..component_decorator import component
from .. import set_required_env_in_op_from_workflow


def tabular_datasets(
    datasets_repo: Dict,
    enable_cache: Optional[bool] = True,
):
    @component(
        base_image=settings.DATASETS_IMAGE,
        enable_cache=enable_cache,
    )
    def tabular_datasets_op(datasets_origin: Dict, datasets_path: OutputPath(str)):
        from metaaiclient import DatasetClient

        data_client = DatasetClient(datasets_origin, datasets_path)

        data_client(datasets_type="tabular")

    return set_required_env_in_op_from_workflow(tabular_datasets_op(datasets_repo))


def image_datasets(
    datasets_repo: Dict,
    enable_cache: Optional[bool] = True,
):
    # 新增env
    @component(
        base_image=settings.DATASETS_IMAGE,
        enable_cache=enable_cache,
    )
    def image_datasets_op(datasets_origin: Dict, datasets_path: OutputPath(str)):
        from metaaiclient import DatasetClient

        data_client = DatasetClient(datasets_origin, datasets_path)

        data_client(datasets_type="image")

    return set_required_env_in_op_from_workflow(image_datasets_op(datasets_repo))
