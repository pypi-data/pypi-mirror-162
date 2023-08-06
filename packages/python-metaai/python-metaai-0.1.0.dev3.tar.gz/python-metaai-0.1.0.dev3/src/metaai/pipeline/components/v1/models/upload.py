from typing import Dict, Optional

from kfp.dsl import RUN_ID_PLACEHOLDER
from kfp.components import InputPath

from ... import settings
from ..component_decorator import component
from .. import set_required_env_in_op_from_workflow


def upload_model(
    model: InputPath(str),
    to_upload_model: Dict,
    metadata_schema: Dict,
    enable_cache: Optional[bool] = True,
):
    @component(
        base_image=settings.MODELS_IMAGE,
        enable_cache=enable_cache,
    )
    def upload_model_op(
        model_path: InputPath(str),
        model_info: Dict,
        meta_schema: Dict,
        run_id: str = None,
    ):

        from metaaiclient import ModelClient

        ModelClient(
            model_path,
            model_info,
            run_id,
            metadata_schema=meta_schema,
        )()

    return set_required_env_in_op_from_workflow(
        upload_model_op(
            model,
            to_upload_model,
            metadata_schema,
            RUN_ID_PLACEHOLDER,
        )
    )
