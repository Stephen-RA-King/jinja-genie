# Core Library modules
import os
import shutil
from pathlib import Path

# Third party modules
import pytest

BASE_DIR = Path(__file__).parents[0]


@pytest.fixture()
def create_os_environ():
    environ = os.environ
    environ.clear()
    environ["INPUT_DYNAMIC_SCRIPT"] = "none"
    environ["INPUT_DATA_FILE"] = ""
    environ["INPUT_DATA_FORMAT"] = "env"
    environ["INPUT_TEMPLATE"] = ""
    environ["INPUT_OUTPUT_FILE"] = ""
    environ["INPUT_VARIABLES"] = ""
    return environ


@pytest.fixture()
def create_input_variables():
    environ = os.environ
    environ.clear()
    environ["INPUT_DYNAMIC_SCRIPT"] = "none"
    environ["INPUT_DATA_FILE"] = ""
    environ["INPUT_DATA_FORMAT"] = "env"
    environ["INPUT_TEMPLATE"] = ""
    environ["INPUT_OUTPUT_FILE"] = ""
    environ["INPUT_VARIABLES"] = "server_host=staging.example.com\ntimeout=45\n"
    return environ
