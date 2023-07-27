from pathlib import Path
import pytest

import main

ROOT_DIR = Path(__file__).parents[0]
RESOURCES = ROOT_DIR / "resources"


def test_save_file_hash_db(create_os_environ):
    genie = main.Genie(create_os_environ)
    main.Config.hash_db = ROOT_DIR / ".jinja-genie.pkl"
    hashdb = {
        "action.yaml": "1d3309e61d470e2e95b08d38b843fe22",
        "Dockerfile": "5208ee5e734cde24c49fb1d0975891c7",
        "entrypoint.py": "aa74c3df3f0a5ad0bd4c3b90fdc26265",
        "LICENSE": "5691d2d44026b88d8928e5e30822cd16"
    }
    genie.save_file_hash_db(hashdb)

    pkl_file = ROOT_DIR / ".jinja-genie.pkl"

    assert pkl_file.exists()

    pkl_file.unlink()




