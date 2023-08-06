from ... import settings
from ..component_decorator import component
from kfp.components import OutputPath


# metaai oss location
def download_model_by_url(base_model_url: str, enable_cache: bool = False):
    @component(
        base_image=settings.MODELS_IMAGE,
        enable_cache=enable_cache,
    )
    def download_base_model_op(model_url: str, base_model_path: OutputPath(str)):
        from metaaiclient import ModelClient

        ModelClient(
            model_url,
            {},
            None,
            output=base_model_path,
        ).download_base_model()

    return download_base_model_op(base_model_url)
