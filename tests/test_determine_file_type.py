from pathlib import Path

import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"
SRC_DIR = RESOURCES / "md5_hash_files"


def test_determine_file_type_ini(create_os_environ):
    genie = main.Genie(create_os_environ)

    file = RESOURCES / "ini_file"
    result = genie.determine_file_type(file)

    assert result == "ini"


def test_determine_file_type_json(create_os_environ):
    genie = main.Genie(create_os_environ)

    file = RESOURCES / "json_file"
    result = genie.determine_file_type(file)

    assert result == "json"


def test_determine_file_type_toml(create_os_environ):
    genie = main.Genie(create_os_environ)

    file = RESOURCES / "toml_file"
    result = genie.determine_file_type(file)

    assert result == "toml"


def test_determine_file_type_yaml(create_os_environ):
    genie = main.Genie(create_os_environ)

    file = RESOURCES / "yaml_file"
    result = genie.determine_file_type(file)

    assert result == "yaml"
