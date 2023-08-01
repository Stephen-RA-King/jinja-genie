"""Main python script to extract the key, value pairs and render the Jinja2 template.
"""
import configparser
import hashlib
import json
import os
import pickle
import subprocess
import tomllib
from contextlib import suppress
from pathlib import Path

import yaml
from j2cli.context import read_context_data
from jinja2 import StrictUndefined
from jinja2 import Template


class Config:
    """Configuration class"""

    hash_db = "jinja-genie.pkl"


class Genie:
    def __init__(self, env_variables):
        self._var_dict = {}
        self._osenv = env_variables

    @staticmethod
    def save_file_hash_db(data: dict) -> None:
        """Serialize the hashdb dictionary.

        Args:
            data (dict): The file hash data dictionary to serialize.
        """
        with open(Config.hash_db, "wb") as file:
            pickle.dump(data, file)

    @staticmethod
    def load_file_hash_db() -> dict:
        """De-serialize the hashdb file dictionary.

        Returns:
            dict: The file hashdb data dictionary.
        """
        with suppress(FileNotFoundError):
            with open(Config.hash_db, "rb") as file:
                return pickle.load(file)
        return {}

    @staticmethod
    def generate_md5_hash(file_path: Path) -> str | None:
        """Generate MD5 hash for a file.

        Args:
            file_path (Path): The file on which to calculate the MD5 hash.

        Returns:
            str: The generated MD5 hash value.
        """
        with suppress(FileNotFoundError):
            with open(file_path, "rb") as file:
                md5_hash = hashlib.md5()
                while True:
                    data = file.read(4096)
                    if not data:
                        break
                    md5_hash.update(data)
                return md5_hash.hexdigest()

    @staticmethod
    def generate_dir_md5_hash(dir_path: Path) -> str:
        """Generate MD5 hashes for all files within a directory, and the directory.

        Args:
            dir_path (Path): The directory/ contents on which to calculate the MD5 hash.

        Returns:
            str: The generated MD5 hash value.
        """
        package_hash = hashlib.md5()
        for path_object in dir_path.rglob("*"):
            if path_object.is_file():
                file_hash = Genie.generate_md5_hash(path_object)
                package_hash.update(file_hash.encode("utf-8"))
        return package_hash.hexdigest()

    @staticmethod
    def update_hashdb(filename: str) -> None:
        """Given the file update the hashdb dictionary and pickle it.

        Args:
            filename (str): the file for which the MD5 should be calculated
        """
        path = Path(filename)
        new_hash = Genie.generate_md5_hash(path)
        if new_hash is not None:
            hashdb = Genie.load_file_hash_db()
            hashdb[path.name] = new_hash
            Genie.save_file_hash_db(hashdb)

    @staticmethod
    def protected_status(filename: str) -> bool:
        """Given a protected target file determine if it has been changed.

        Args:
            filename (str): The file for which the status should be determined.

        Returns:
            True: If the file has not been changed since last template rendering
            False: If the file has been changed since last template rendering
        """
        path = Path(filename)
        current_hash = Genie.generate_md5_hash(path)
        hashdb = Genie.load_file_hash_db()
        if current_hash is not None:
            if hashdb:
                saved_hash = hashdb.get(path.name, "")
                if saved_hash:
                    if current_hash == saved_hash:
                        return True
                    else:
                        # TODO: backup file
                        return False
                else:
                    # hashdb file exists but file hash is not found
                    return True
            else:
                # hashdb file does not exist
                return True
        else:
            # file does not exist
            return True

    def use_dynamic_variables(self) -> None:
        """Get dynamic script name, run it and get the results from a dotenv file."""
        dynamic_script = self._osenv.get("INPUT_DYNAMIC_SCRIPT")
        if os.path.exists(dynamic_script):
            subprocess.run(["python", dynamic_script])
        env_file = "".join([Path(dynamic_script).stem, ".env"])
        if os.path.exists(env_file):
            with open(env_file) as file:
                contents = read_context_data("env", file, None)
                self._var_dict.update(contents)
                os.remove(env_file)

    def use_env_variables(self) -> None:
        """Add os environ variables to a dictionary"""
        self._var_dict.update({"env": self._osenv})

    def use_manual_variables(self) -> None:
        """Collect manual variables from the workflow and extract into a dictionary."""
        for variable in self._osenv.get("INPUT_VARIABLES", "").split("\n"):
            clean_variable = bytes(variable.strip(), "utf-8").decode("unicode_escape")
            if clean_variable != "":
                name, value = clean_variable.split("=", 1)
                self._var_dict.update({name: value})

    def use_data_source(self) -> None:
        """Process the data source file and extract key, value pairs into dictionary."""
        data_source: str = self._osenv.get("INPUT_DATA_SOURCE")
        data_type: str = self._osenv.get("INPUT_DATA_TYPE")
        if data_source:
            if data_type == "":
                data_type = self.get_extension(data_source) or self.determine_file_type(
                    data_source
                )
                if data_type is None:
                    raise ValueError("Cannot determine data type for data source")
            with suppress(FileNotFoundError):
                with open(data_source) as file:
                    contents = read_context_data(data_type, file, None)
                    self._var_dict.update(contents)

    @staticmethod
    def get_extension(file: str) -> str:
        """Given a file return the file extension if it has one.

        Args:
             file (str): file of which to determine the extension

        Returns:
            str: the extension without the dot.
        """
        path = Path(file)
        extension = path.suffix.lower().lstrip(".")
        if extension in ("toml", "env", "ini", "json", "yml", "yaml"):
            return extension

    @staticmethod
    def determine_file_type(file: str | Path) -> str:
        """Find the file type if missing from the workflow and missing extension.

        Args:
            file (str): the file of which to determine the file type.

        Returns:
            str: the file data type.
        """
        path = Path(file)
        with open(path) as f:
            content = f.read()
        try:
            configparser.ConfigParser().read_string(content)
            return "ini"
        except configparser.Error:
            pass
        try:
            json.loads(content)
            return "json"
        except json.JSONDecodeError:
            pass
        try:
            yaml.safe_load(content)
            return "yaml"
        except yaml.YAMLError:
            pass
        try:
            if "=" in content:  # TOML-specific syntax
                tomllib.loads(content)
                return "toml"
        except NameError:
            pass

    def render_template(self):
        """Render the template with the variables """
        status = ""
        protect = self._osenv.get("INPUT_PROTECT")
        template = self._osenv["INPUT_TEMPLATE"]
        target = self._osenv["INPUT_TARGET"]
        strict = self._osenv.get("INPUT_STRICT")

        if protect == "true":
            status = Genie.protected_status(target)
        if protect == "" or status is True:
            with open(template) as file:
                template_kwargs = {}
                if strict == "true":
                    template_kwargs.update({"undefined": StrictUndefined})
                template = Template(str(file.read()), **template_kwargs)

            with open(target, "w") as file:
                file.write(template.render(**self._var_dict) + "\n")

        if protect == "true":
            Genie.update_hashdb(target)
        if status is False:
            raise ValueError("Target file has been updated since last templating")
