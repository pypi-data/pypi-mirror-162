from typing import *
from kfp.components._python_op import _func_to_component_dict
from kfp.components._python_op import _create_task_factory_from_component_spec
from kfp.components.structures import ComponentSpec
from kfp.components import _structures as structures

from ..settings import KFP_DISABLE_CACHE_ANNOTATIONS


def create_component_from_func(
    func: Callable,
    enable_cache: Optional[bool] = True,
    output_component_file: Optional[str] = None,
    base_image: Optional[str] = None,
    packages_to_install: List[str] = None,
    # image_pull_policy: Optional[str] = None,
    annotations: Optional[Dict[str, str]] = None,
):
    component_spec_dict = _func_to_component_dict(
        func, base_image=base_image, packages_to_install=packages_to_install
    )
    # NOTE: 这个东西写到component的yaml里面了 然后发现load不进来，不支持这个参数！。简直离谱！
    # container_implementation = component_spec_dict.pop("implementation")
    #
    # container_dict = container_implementation.pop("container")
    # NOTE: 主要添加了当前这个镜像的拉取策略

    # if image_pull_policy is not None:
    #     try:
    #         ImagePullPolicy(image_pull_policy)
    #     except Exception:
    #         raise RuntimeError(
    #             f"image_pull_policy now supported value from metaai.pipeline.constants.ImagePullPolicy,"
    #             f"given '{image_pull_policy}' not in enumeration"
    #         )
    #     # NOTE: 这个dict的key是和在yaml中的key相同的
    #     container_dict["imagePullPolicy"] = image_pull_policy

    component_spec = ComponentSpec.from_dict(component_spec_dict)

    # component_spec.implementation = HackContainerImplementation(
    #     container=HackContainerSpec.from_dict(container_dict)
    # )

    if not annotations:
        annotations = {}

    if not enable_cache:

        annotations.update(KFP_DISABLE_CACHE_ANNOTATIONS)
        component_spec.metadata = structures.MetadataSpec(
            annotations=annotations,
        )

    if output_component_file:
        component_spec.save(output_component_file)

    return _create_task_factory_from_component_spec(component_spec)
