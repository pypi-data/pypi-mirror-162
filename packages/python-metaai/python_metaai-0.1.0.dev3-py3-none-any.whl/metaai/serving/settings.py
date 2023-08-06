import os


DEFAULT_MODEL_FOLDER_PATH = os.getenv("MODEL_FOLDER_PATH", "/mnt/models")

DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "model")

DEFAULT_MODEL_PATH = os.getenv(
    "MODEL_PATH", str(os.path.join(DEFAULT_MODEL_FOLDER_PATH, DEFAULT_MODEL_NAME))
)
