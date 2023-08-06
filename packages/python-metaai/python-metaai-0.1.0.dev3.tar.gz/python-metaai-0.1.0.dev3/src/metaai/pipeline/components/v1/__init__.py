from kfp.dsl import ContainerOp

from kubernetes.client import V1EnvVar
from .. import constants


def set_required_env_in_op_from_workflow(op: ContainerOp):
    # op.add_env_variable() 这个也可以，使用下面这个好定位，以及配合 type hint
    op.container.add_env_variable(
        V1EnvVar(name="METAAI_USER_ID", value=constants.METAAI_USER_INFO_PLACEHOLDER)
    )
    op.container.add_env_variable(
        V1EnvVar(
            name="MLMODELS_ENDPOINT",
            value=constants.METAAI_MLMODELS_ENDPOINT_PLACEHOLDER,
        )
    )
    op.container.add_env_variable(
        V1EnvVar(
            name="DATASETS_ENDPOINT",
            value=constants.METAAI_MLDATASETS_ENDPOINT_PLACEHOLDER,
        )
    )

    return op
