"""Tests for entrypoint.py -- main() and the __main__ script block."""
import runpy
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

import entrypoint
import main as main_module

ENTRYPOINT_PATH = str(Path(entrypoint.__file__).resolve())

BASE_ENV = {
    "INPUT_DYNAMIC_SCRIPT": "",
    "INPUT_VARIABLES": "",
    "INPUT_DATA_SOURCE": "",
}


# ---------------------------------------------------------------------------
# entrypoint.main()
# ---------------------------------------------------------------------------


class TestMainFunction:
    def test_all_optional_steps_skipped(self, monkeypatch):
        mock_genie = MagicMock()
        mock_genie_cls = MagicMock(return_value=mock_genie)
        monkeypatch.setattr(entrypoint, "Genie", mock_genie_cls)

        entrypoint.main(dict(BASE_ENV))

        mock_genie.use_env_variables.assert_called_once()
        mock_genie.use_dynamic_variables.assert_not_called()
        mock_genie.use_manual_variables.assert_not_called()
        mock_genie.use_data_source.assert_not_called()
        mock_genie.render_template.assert_called_once()

    def test_all_optional_steps_triggered(self, monkeypatch):
        mock_genie = MagicMock()
        mock_genie_cls = MagicMock(return_value=mock_genie)
        monkeypatch.setattr(entrypoint, "Genie", mock_genie_cls)

        env = {
            "INPUT_DYNAMIC_SCRIPT": "script.py",
            "INPUT_VARIABLES": "a=1",
            "INPUT_DATA_SOURCE": "data.json",
        }
        entrypoint.main(env)

        mock_genie.use_env_variables.assert_called_once()
        mock_genie.use_dynamic_variables.assert_called_once()
        mock_genie.use_manual_variables.assert_called_once()
        mock_genie.use_data_source.assert_called_once()
        mock_genie.render_template.assert_called_once()

    def test_genie_constructed_with_os_environ(self, monkeypatch):
        # Note: main() builds Genie from os.environ directly (not from the
        # env_variables argument it receives) -- this pins that behaviour.
        mock_genie_cls = MagicMock(return_value=MagicMock())
        monkeypatch.setattr(entrypoint, "Genie", mock_genie_cls)
        monkeypatch.setattr(entrypoint.os, "environ", {"SOME": "value"})

        entrypoint.main(dict(BASE_ENV))

        mock_genie_cls.assert_called_once_with({"SOME": "value"})


# ---------------------------------------------------------------------------
# The `if __name__ == "__main__":` block, exercised via runpy so it counts
# toward coverage. subprocess.run and Genie are patched so no real pip
# installs or file rendering happen.
# ---------------------------------------------------------------------------


class TestDunderMain:
    def _set_base_env(self, monkeypatch):
        for key, value in BASE_ENV.items():
            monkeypatch.setenv(key, value)

    def test_no_requires_skips_pip_install(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv("INPUT_REQUIRES", "")

        run_mock = MagicMock()
        monkeypatch.setattr(subprocess, "run", run_mock)
        monkeypatch.setattr(main_module, "Genie", MagicMock(return_value=MagicMock()))

        runpy.run_path(ENTRYPOINT_PATH, run_name="__main__")

        run_mock.assert_not_called()

    def test_requires_installs_each_package(self, monkeypatch):
        self._set_base_env(monkeypatch)
        monkeypatch.setenv(
            "INPUT_REQUIRES", "requests==2.31.0\n\n   \npandas\n"
        )

        run_mock = MagicMock()
        monkeypatch.setattr(subprocess, "run", run_mock)
        monkeypatch.setattr(main_module, "Genie", MagicMock(return_value=MagicMock()))

        runpy.run_path(ENTRYPOINT_PATH, run_name="__main__")

        expected_calls = [
            call(["pip", "install", "--no-cache-dir", "requests==2.31.0"]),
            call(["pip", "install", "--no-cache-dir", "pandas"]),
        ]
        run_mock.assert_has_calls(expected_calls)
        assert run_mock.call_count == 2

    def test_requires_with_escaped_characters(self, monkeypatch):
        self._set_base_env(monkeypatch)
        # unicode_escape decoding of a literal backslash-n should not split
        # into a new requirement line by itself; here we just prove escape
        # decoding runs without error on a normal requirement.
        monkeypatch.setenv("INPUT_REQUIRES", "  numpy  ")

        run_mock = MagicMock()
        monkeypatch.setattr(subprocess, "run", run_mock)
        monkeypatch.setattr(main_module, "Genie", MagicMock(return_value=MagicMock()))

        runpy.run_path(ENTRYPOINT_PATH, run_name="__main__")

        run_mock.assert_called_once_with(["pip", "install", "--no-cache-dir", "numpy"])
