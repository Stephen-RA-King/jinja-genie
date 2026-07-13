import os
import sys
from pathlib import Path

import pytest

# Make the project root (containing main.py / entrypoint.py) importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def isolated_cwd(tmp_path, monkeypatch):
    """Run every test inside its own tmp directory.

    Genie.hash_db ("jinja-genie.pkl") is a bare relative filename, so tests
    must not share a working directory or they'll pollute each other's
    hash database.
    """
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture(autouse=True)
def clean_input_env(monkeypatch):
    """Ensure no INPUT_* / stray env vars leak in from the host environment."""
    for key in list(os.environ):
        if key.startswith("INPUT_"):
            monkeypatch.delenv(key, raising=False)
    yield
