# Make backend a package and re-export download_model for build steps
from .sentiment import download_model  # noqa: F401
