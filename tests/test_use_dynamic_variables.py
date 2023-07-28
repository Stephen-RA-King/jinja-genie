import os
from pathlib import Path

import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"


def test_use_dynamic_variables(create_os_environ):
    genie = main.Genie(create_os_environ)

    os.environ["INPUT_DYNAMIC_SCRIPT"] = "resources/dynamic_script.py"
    genie.run_dynamic_script()

    # assert pkl_file.exists()
