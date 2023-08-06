import enum


class ImagePullPolicy(enum.Enum):
    IfNotPresent = "IfNotPresent"
    Always = "Always"
    Never = "Never"


METAAI_USER_INFO_PLACEHOLDER = "{{workflow.annotations.metaai.zjuici.com/user-id}}"


METAAI_MLMODELS_ENDPOINT_PLACEHOLDER = (
    "{{workflow.annotations.metaai.zjuici.com/mlmodels-endpoint}}"
)

METAAI_MLDATASETS_ENDPOINT_PLACEHOLDER = (
    "{{workflow.annotations.metaai.zjuici.com/mldatasets-endpoint}}"
)
