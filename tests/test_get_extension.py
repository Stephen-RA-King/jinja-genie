from pathlib import Path


import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"
SRC_DIR = RESOURCES / "md5_hash_files"


def test_get_extension_ini(create_os_environ):
    genie = main.Genie(create_os_environ)

    result = genie.get_extension("text.ini")
    assert result == "ini"


def test_get_extension_json(create_os_environ):
    genie = main.Genie(create_os_environ)

    result = genie.get_extension("text.JSON")
    assert result == "json"


def test_get_extension_none(create_os_environ):
    genie = main.Genie(create_os_environ)

    result = genie.get_extension("text.txt")
    assert result is None
