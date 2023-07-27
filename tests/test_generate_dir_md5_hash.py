from pathlib import Path

import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"
SRC_DIR = RESOURCES / "md5_hash_files"


def test_generate_dir_md5(create_os_environ):
    genie = main.Genie(create_os_environ)

    expected_hash = "b46b12f88320ad6cc5084db48560468f"
    calculated_hash = genie.generate_dir_md5_hash(SRC_DIR)

    assert calculated_hash == expected_hash
