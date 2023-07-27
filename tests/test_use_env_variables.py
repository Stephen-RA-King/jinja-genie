from pathlib import Path
import os


import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"
SRC_DIR = RESOURCES / "md5_hash_files"


def test_use_env_variables(create_os_environ):
    genie = main.Genie(create_os_environ)

    genie.use_env_variables()

    assert (
        str(genie._var_dict)
        == "{'env': environ({'INPUT_DYNAMIC_SCRIPT': 'none', 'INPUT_DATA_FILE': '', "
           "'INPUT_DATA_FORMAT': 'env', 'INPUT_TEMPLATE': '', 'INPUT_OUTPUT_FILE': '', "
           "'INPUT_VARIABLES': '', 'PYTEST_CURRENT_TEST': "
           "'test_use_os_environ.py::test_use_os_environ (call)'})}"
    )
