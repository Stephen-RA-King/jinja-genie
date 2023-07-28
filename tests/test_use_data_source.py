from pathlib import Path

import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"
SRC_DIR = RESOURCES / "md5_hash_files"


def test_use_data_source(create_data_source_variables):
    genie = main.Genie(create_data_source_variables)

    genie.use_data_source()

    assert (
        str(genie._var_dict)
        == "{}"
    )
