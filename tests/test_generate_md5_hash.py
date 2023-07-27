from pathlib import Path

import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"
SRC_DIR = RESOURCES / "md5_hash_files"


def test_generate_md5(create_os_environ):
    genie = main.Genie(create_os_environ)

    expected_hash = "1d3309e61d470e2e95b08d38b843fe22"
    calculated_hash = genie.generate_md5_hash(SRC_DIR / "action.yaml")

    assert calculated_hash == expected_hash


def test_generate_md5_none(create_os_environ):
    genie = main.Genie(create_os_environ)

    expected_hash = None
    calculated_hash = genie.generate_md5_hash(SRC_DIR / "action1.yaml")

    assert calculated_hash == expected_hash
