"""Tests for main.py -- read_context_data() and the Genie class."""
import io
import json
import pickle
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from jinja2.exceptions import UndefinedError

import main
from main import Config, Genie, read_context_data


# ---------------------------------------------------------------------------
# read_context_data
# ---------------------------------------------------------------------------


class TestReadContextData:
    def test_json(self):
        content = json.dumps({"a": 1, "b": "two"})
        result = read_context_data("json", io.StringIO(content), None)
        assert result == {"a": 1, "b": "two"}

    def test_yaml(self):
        content = "a: 1\nb: two\n"
        result = read_context_data("yaml", io.StringIO(content), None)
        assert result == {"a": 1, "b": "two"}

    def test_yml_alias(self):
        content = "a: 1\n"
        result = read_context_data("yml", io.StringIO(content), None)
        assert result == {"a": 1}

    def test_yaml_empty_returns_empty_dict(self):
        # yaml.safe_load("") -> None; function should coerce to {}
        result = read_context_data("yaml", io.StringIO(""), None)
        assert result == {}

    def test_ini(self):
        content = "[section]\nkey = value\nother = 1\n"
        result = read_context_data("ini", io.StringIO(content), None)
        assert result == {"section": {"key": "value", "other": "1"}}

    def test_env(self):
        content = "# comment\nFOO=bar\n\nBAZ=qux\nMALFORMED_LINE\n"
        result = read_context_data("env", io.StringIO(content), None)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_env_skips_comments_and_blank_lines(self):
        content = "\n# just a comment\n   \nA=1\n"
        result = read_context_data("env", io.StringIO(content), None)
        assert result == {"A": "1"}

    def test_toml(self):
        content = 'name = "test"\nvalue = 42\n'
        result = read_context_data("toml", io.StringIO(content), None)
        assert result == {"name": "test", "value": 42}

    def test_unknown_type_returns_empty_dict(self):
        result = read_context_data("bogus", io.StringIO("irrelevant"), None)
        assert result == {}


# ---------------------------------------------------------------------------
# Genie: hash db persistence
# ---------------------------------------------------------------------------


class TestHashDb:
    def test_save_and_load_round_trip(self, tmp_path):
        data = {"file.txt": "abc123"}
        Genie.save_file_hash_db(data)
        assert Path(Config.hash_db).exists()
        loaded = Genie.load_file_hash_db()
        assert loaded == data

    def test_load_missing_file_returns_empty_dict(self):
        assert not Path(Config.hash_db).exists()
        assert Genie.load_file_hash_db() == {}


# ---------------------------------------------------------------------------
# Genie: md5 hashing
# ---------------------------------------------------------------------------


class TestMd5Hashing:
    def test_generate_md5_hash_known_content(self, tmp_path):
        f = tmp_path / "sample.txt"
        f.write_bytes(b"hello world")
        import hashlib

        expected = hashlib.md5(b"hello world").hexdigest()
        assert Genie.generate_md5_hash(f) == expected

    def test_generate_md5_hash_missing_file_returns_none(self, tmp_path):
        f = tmp_path / "does_not_exist.txt"
        assert Genie.generate_md5_hash(f) is None

    def test_generate_md5_hash_large_file_multiple_chunks(self, tmp_path):
        f = tmp_path / "big.txt"
        f.write_bytes(b"x" * 10000)  # forces multiple 4096-byte reads
        import hashlib

        expected = hashlib.md5(b"x" * 10000).hexdigest()
        assert Genie.generate_md5_hash(f) == expected

    def test_generate_dir_md5_hash_is_deterministic(self, tmp_path):
        d = tmp_path / "pkg"
        d.mkdir()
        (d / "a.txt").write_bytes(b"aaa")
        (d / "b.txt").write_bytes(b"bbb")
        sub = d / "sub"
        sub.mkdir()
        (sub / "c.txt").write_bytes(b"ccc")

        first = Genie.generate_dir_md5_hash(d)
        second = Genie.generate_dir_md5_hash(d)
        assert first == second
        assert len(first) == 32  # hex md5 digest length

    def test_generate_dir_md5_hash_changes_with_content(self, tmp_path):
        d = tmp_path / "pkg"
        d.mkdir()
        (d / "a.txt").write_bytes(b"aaa")
        before = Genie.generate_dir_md5_hash(d)
        (d / "a.txt").write_bytes(b"changed")
        after = Genie.generate_dir_md5_hash(d)
        assert before != after


# ---------------------------------------------------------------------------
# Genie: update_hashdb
# ---------------------------------------------------------------------------


class TestUpdateHashdb:
    def test_updates_and_persists_hash(self, tmp_path):
        target = tmp_path / "out.txt"
        target.write_text("content")
        Genie.update_hashdb(str(target))
        db = Genie.load_file_hash_db()
        assert target.name in db
        assert db[target.name] == Genie.generate_md5_hash(target)

    def test_missing_file_does_not_touch_hashdb(self, tmp_path, monkeypatch):
        save_mock = MagicMock()
        monkeypatch.setattr(Genie, "save_file_hash_db", save_mock)
        Genie.update_hashdb(str(tmp_path / "nope.txt"))
        save_mock.assert_not_called()


# ---------------------------------------------------------------------------
# Genie: protected_status
# ---------------------------------------------------------------------------


class TestProtectedStatus:
    def test_target_file_missing_returns_true(self, tmp_path):
        target = tmp_path / "missing.txt"
        assert Genie.protected_status(str(target)) is True

    def test_no_hashdb_file_returns_true(self, tmp_path):
        target = tmp_path / "file.txt"
        target.write_text("content")
        assert not Path(Config.hash_db).exists()
        assert Genie.protected_status(str(target)) is True

    def test_hashdb_exists_but_file_not_tracked_returns_true(self, tmp_path):
        target = tmp_path / "file.txt"
        target.write_text("content")
        Genie.save_file_hash_db({"unrelated.txt": "deadbeef"})
        assert Genie.protected_status(str(target)) is True

    def test_hash_matches_returns_true(self, tmp_path):
        target = tmp_path / "file.txt"
        target.write_text("content")
        current_hash = Genie.generate_md5_hash(target)
        Genie.save_file_hash_db({target.name: current_hash})
        assert Genie.protected_status(str(target)) is True

    def test_hash_mismatch_returns_false(self, tmp_path):
        target = tmp_path / "file.txt"
        target.write_text("original content")
        Genie.save_file_hash_db({target.name: "not-the-real-hash"})
        assert Genie.protected_status(str(target)) is False


# ---------------------------------------------------------------------------
# Genie: use_dynamic_variables
# ---------------------------------------------------------------------------


class TestUseDynamicVariables:
    def test_script_exists_runs_and_loads_env_file(self, tmp_path, monkeypatch):
        script = tmp_path / "gen.py"
        script.write_text("# pretend script\n")
        env_file = tmp_path / "gen.env"

        run_mock = MagicMock()

        def fake_run(cmd, *args, **kwargs):
            # Simulate the script producing its .env output.
            env_file.write_text("DYNVAR=dynvalue\n")
            return MagicMock()

        monkeypatch.setattr(subprocess, "run", fake_run)

        genie = Genie({})
        genie._osenv = {"INPUT_DYNAMIC_SCRIPT": str(script)}
        genie.use_dynamic_variables()

        assert genie._var_dict == {"DYNVAR": "dynvalue"}
        assert not env_file.exists()  # removed after reading

    def test_script_missing_subprocess_not_called(self, tmp_path, monkeypatch):
        run_mock = MagicMock()
        monkeypatch.setattr(subprocess, "run", run_mock)

        genie = Genie({})
        genie._osenv = {"INPUT_DYNAMIC_SCRIPT": str(tmp_path / "nope.py")}
        genie.use_dynamic_variables()

        run_mock.assert_not_called()
        assert genie._var_dict == {}

    def test_no_env_file_produced_var_dict_unchanged(self, tmp_path, monkeypatch):
        script = tmp_path / "gen.py"
        script.write_text("# does nothing\n")
        monkeypatch.setattr(subprocess, "run", MagicMock())

        genie = Genie({})
        genie._osenv = {"INPUT_DYNAMIC_SCRIPT": str(script)}
        genie.use_dynamic_variables()

        assert genie._var_dict == {}


# ---------------------------------------------------------------------------
# Genie: use_env_variables
# ---------------------------------------------------------------------------


class TestUseEnvVariables:
    def test_adds_env_key(self):
        osenv = {"FOO": "bar"}
        genie = Genie(osenv)
        genie.use_env_variables()
        assert genie._var_dict == {"env": osenv}


# ---------------------------------------------------------------------------
# Genie: use_manual_variables
# ---------------------------------------------------------------------------


class TestUseManualVariables:
    def test_parses_multiple_variables(self):
        genie = Genie({"INPUT_VARIABLES": "name=Alice\nrole=Admin"})
        genie.use_manual_variables()
        assert genie._var_dict == {"name": "Alice", "role": "Admin"}

    def test_skips_blank_lines(self):
        genie = Genie({"INPUT_VARIABLES": "name=Alice\n\n\nrole=Admin"})
        genie.use_manual_variables()
        assert genie._var_dict == {"name": "Alice", "role": "Admin"}

    def test_no_variables_set_leaves_dict_empty(self):
        genie = Genie({})  # INPUT_VARIABLES not present -> default ""
        genie.use_manual_variables()
        assert genie._var_dict == {}

    def test_unicode_escape_decoding(self):
        genie = Genie({"INPUT_VARIABLES": r"greeting=Hello\nWorld"})
        genie.use_manual_variables()
        assert genie._var_dict == {"greeting": "Hello\nWorld"}

    def test_value_containing_equals_sign(self):
        genie = Genie({"INPUT_VARIABLES": "url=http://example.com?a=1"})
        genie.use_manual_variables()
        assert genie._var_dict == {"url": "http://example.com?a=1"}


# ---------------------------------------------------------------------------
# Genie: use_data_source
# ---------------------------------------------------------------------------


class TestUseDataSource:
    def test_explicit_data_type(self, tmp_path):
        f = tmp_path / "data.cfg"
        f.write_text(json.dumps({"x": 1}))
        genie = Genie({"INPUT_DATA_SOURCE": str(f), "INPUT_DATA_TYPE": "json"})
        genie.use_data_source()
        assert genie._var_dict == {"x": 1}

    def test_data_type_inferred_from_extension(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text(json.dumps({"y": 2}))
        genie = Genie({"INPUT_DATA_SOURCE": str(f), "INPUT_DATA_TYPE": ""})
        genie.use_data_source()
        assert genie._var_dict == {"y": 2}

    def test_data_type_inferred_via_content_sniffing(self, tmp_path):
        # No recognised extension -> falls through to determine_file_type
        f = tmp_path / "data.conf"
        f.write_text(json.dumps({"z": 3}))
        genie = Genie({"INPUT_DATA_SOURCE": str(f), "INPUT_DATA_TYPE": ""})
        genie.use_data_source()
        assert genie._var_dict == {"z": 3}

    def test_undeterminable_type_raises_value_error(self, tmp_path):
        f = tmp_path / "data.mystery"
        # Fails ini, json, and yaml parsing; has no '=' so toml is skipped too.
        f.write_text("key: [1,2")
        genie = Genie({"INPUT_DATA_SOURCE": str(f), "INPUT_DATA_TYPE": ""})
        with pytest.raises(ValueError):
            genie.use_data_source()

    def test_no_data_source_is_noop(self):
        genie = Genie({"INPUT_DATA_SOURCE": ""})
        genie.use_data_source()
        assert genie._var_dict == {}

    def test_missing_data_source_file_suppressed(self, tmp_path):
        f = tmp_path / "missing.json"
        genie = Genie({"INPUT_DATA_SOURCE": str(f), "INPUT_DATA_TYPE": "json"})
        genie.use_data_source()  # should not raise
        assert genie._var_dict == {}


# ---------------------------------------------------------------------------
# Genie: get_extension
# ---------------------------------------------------------------------------


class TestGetExtension:
    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("data.json", "json"),
            ("data.yaml", "yaml"),
            ("data.yml", "yml"),
            ("data.ini", "ini"),
            ("data.env", "env"),
            ("data.toml", "toml"),
            ("data.JSON", "json"),  # case-insensitive
        ],
    )
    def test_recognised_extensions(self, filename, expected):
        assert Genie.get_extension(filename) == expected

    def test_unrecognised_extension_returns_none(self):
        assert Genie.get_extension("data.txt") is None

    def test_no_extension_returns_none(self):
        assert Genie.get_extension("data") is None


# ---------------------------------------------------------------------------
# Genie: determine_file_type
# ---------------------------------------------------------------------------


class TestDetermineFileType:
    def test_detects_ini(self, tmp_path):
        f = tmp_path / "f"
        f.write_text("[section]\nkey=value\n")
        assert Genie.determine_file_type(f) == "ini"

    def test_detects_json(self, tmp_path):
        f = tmp_path / "f"
        f.write_text('{"a": 1}')
        assert Genie.determine_file_type(f) == "json"

    def test_detects_yaml(self, tmp_path):
        f = tmp_path / "f"
        f.write_text("a: 1\nb: 2\n")
        assert Genie.determine_file_type(f) == "yaml"

    def test_detects_toml(self, tmp_path):
        f = tmp_path / "f"
        # Fails ini (no section header), fails json, fails yaml (tab indent
        # is illegal), but is valid TOML.
        f.write_text("a = 1\n\tb = 2\n")
        assert Genie.determine_file_type(f) == "toml"

    def test_returns_none_when_undeterminable(self, tmp_path):
        f = tmp_path / "f"
        f.write_text("key: [1,2")
        assert Genie.determine_file_type(f) is None

    def test_accepts_string_path(self, tmp_path):
        f = tmp_path / "f"
        f.write_text('{"a": 1}')
        assert Genie.determine_file_type(str(f)) == "json"

    def test_toml_namerror_guard_is_suppressed(self, tmp_path, monkeypatch):
        # The `except NameError` around the toml check is a defensive guard
        # (relevant on Python < 3.11 where `tomllib` wouldn't exist). We
        # simulate that condition to exercise it: content contains '=' so
        # the toml branch is entered, and tomllib.loads is forced to raise
        # NameError instead of actually parsing.
        f = tmp_path / "f"
        f.write_text("a = 1\n\tb = 2\n")  # fails ini/json/yaml, has '='

        def raise_name_error(_content):
            raise NameError("tomllib is not defined")

        monkeypatch.setattr(main.tomllib, "loads", raise_name_error)
        assert Genie.determine_file_type(f) is None


# ---------------------------------------------------------------------------
# Genie: render_template
# ---------------------------------------------------------------------------


class TestRenderTemplate:
    def _make_genie(self, tmp_path, extra_env=None, var_dict=None):
        env = {}
        if extra_env:
            env.update(extra_env)
        genie = Genie(env)
        genie._osenv = env
        if var_dict:
            genie._var_dict.update(var_dict)
        return genie

    def test_unprotected_render(self, tmp_path):
        template = tmp_path / "tpl.j2"
        template.write_text("Hello {{ name }}!")
        target = tmp_path / "out.txt"

        genie = self._make_genie(
            tmp_path,
            extra_env={
                "INPUT_PROTECT": "",
                "INPUT_TEMPLATE": str(template),
                "INPUT_TARGET": str(target),
                "INPUT_STRICT": "",
            },
            var_dict={"name": "World"},
        )
        genie.render_template()
        assert target.read_text() == "Hello World!\n"

    def test_protected_new_file_renders_and_updates_hashdb(self, tmp_path):
        template = tmp_path / "tpl.j2"
        template.write_text("Value: {{ val }}")
        target = tmp_path / "out.txt"

        genie = self._make_genie(
            tmp_path,
            extra_env={
                "INPUT_PROTECT": "true",
                "INPUT_TEMPLATE": str(template),
                "INPUT_TARGET": str(target),
                "INPUT_STRICT": "",
            },
            var_dict={"val": "42"},
        )
        genie.render_template()

        assert target.read_text() == "Value: 42\n"
        db = Genie.load_file_hash_db()
        assert db[target.name] == Genie.generate_md5_hash(target)

    def test_protected_unmodified_file_rerenders(self, tmp_path):
        template = tmp_path / "tpl.j2"
        template.write_text("Value: {{ val }}")
        target = tmp_path / "out.txt"
        target.write_text("Value: old\n")
        Genie.save_file_hash_db({target.name: Genie.generate_md5_hash(target)})

        genie = self._make_genie(
            tmp_path,
            extra_env={
                "INPUT_PROTECT": "true",
                "INPUT_TEMPLATE": str(template),
                "INPUT_TARGET": str(target),
                "INPUT_STRICT": "",
            },
            var_dict={"val": "new"},
        )
        genie.render_template()
        assert target.read_text() == "Value: new\n"

    def test_protected_modified_file_raises_and_skips_render(self, tmp_path):
        template = tmp_path / "tpl.j2"
        template.write_text("Value: {{ val }}")
        target = tmp_path / "out.txt"
        target.write_text("Value: manually edited\n")
        # Hashdb has a stale hash, so the file appears externally modified.
        Genie.save_file_hash_db({target.name: "stale-hash-value"})

        genie = self._make_genie(
            tmp_path,
            extra_env={
                "INPUT_PROTECT": "true",
                "INPUT_TEMPLATE": str(template),
                "INPUT_TARGET": str(target),
                "INPUT_STRICT": "",
            },
            var_dict={"val": "new"},
        )
        with pytest.raises(ValueError):
            genie.render_template()

        # Template must NOT have been re-rendered over the modified file.
        assert target.read_text() == "Value: manually edited\n"

        # But the hashdb should be refreshed to the (modified) file's hash.
        db = Genie.load_file_hash_db()
        assert db[target.name] == Genie.generate_md5_hash(target)

    def test_strict_undefined_raises_on_missing_variable(self, tmp_path):
        template = tmp_path / "tpl.j2"
        template.write_text("Hello {{ missing_var }}!")
        target = tmp_path / "out.txt"

        genie = self._make_genie(
            tmp_path,
            extra_env={
                "INPUT_PROTECT": "",
                "INPUT_TEMPLATE": str(template),
                "INPUT_TARGET": str(target),
                "INPUT_STRICT": "true",
            },
        )
        with pytest.raises(UndefinedError):
            genie.render_template()

    def test_non_strict_missing_variable_renders_empty(self, tmp_path):
        template = tmp_path / "tpl.j2"
        template.write_text("Hello {{ missing_var }}!")
        target = tmp_path / "out.txt"

        genie = self._make_genie(
            tmp_path,
            extra_env={
                "INPUT_PROTECT": "",
                "INPUT_TEMPLATE": str(template),
                "INPUT_TARGET": str(target),
                "INPUT_STRICT": "",
            },
        )
        genie.render_template()
        assert target.read_text() == "Hello !\n"

    def test_protect_key_entirely_absent_is_noop(self, tmp_path):
        # INPUT_PROTECT missing from osenv -> .get() returns None, which
        # satisfies neither the "protect == true" nor "protect == ''"
        # branches, so nothing is rendered and nothing raises.
        template = tmp_path / "tpl.j2"
        template.write_text("Hello {{ name }}!")
        target = tmp_path / "out.txt"

        genie = self._make_genie(
            tmp_path,
            extra_env={
                "INPUT_TEMPLATE": str(template),
                "INPUT_TARGET": str(target),
                "INPUT_STRICT": "",
            },
            var_dict={"name": "World"},
        )
        genie.render_template()  # should not raise
        assert not target.exists()
