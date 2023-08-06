IMAGE_REPO_HOST = "10.0.0.68:8089"

DATASETS_IMAGE = f"{IMAGE_REPO_HOST}/metaai/metaai-client:0.2.0"

MODELS_IMAGE = f"{IMAGE_REPO_HOST}/metaai/metaai-client:0.2.0"

# 配置harbor的python，使用清华镜像的源
DEFAULT_BASE_PYTHON_IMAGE = f"{IMAGE_REPO_HOST}/library/python:3.7"

KFP_DISABLE_CACHE_ANNOTATIONS = {"pipelines.kubeflow.org/max_cache_staleness": "P0D"}
