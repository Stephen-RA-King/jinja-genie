from pathlib import Path


import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"
SRC_DIR = RESOURCES / "md5_hash_files"


def test_use_manual_variables(create_input_variables):
    genie = main.Genie(create_input_variables)

    genie.use_manual_variables()

    assert (
        str(genie._var_dict)
        == "{'server_host': 'staging.example.com', 'timeout': '45'}"
    )
