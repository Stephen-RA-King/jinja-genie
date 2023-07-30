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

    hash_db = ".jinja-genie.pkl"


class Genie:
    def __init__(self, env_variables):
        self._var_dict = {}
        self._osenv = env_variables

    @staticmethod
    def save_file_hash_db(data: dict) -> None:
        """This function does something.

        Args:
            data (dict): The file hash data dictionary to serialize.

        Returns:
            None:
        """
        with suppress(FileNotFoundError):
            with open(Config.hash_db, "wb") as file:
                pickle.dump(data, file)

    @staticmethod
    def load_file_hash_db() -> dict:
        """This function does something.

        Returns:
            dict: The file hash data dictionary.

        Raises:
            ValueError: If the input is invalid.
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
    def update_hashdb(filename: str):
        print("*****  Updating hashdb file *******")
        path = Path(filename)
        new_hash = Genie.generate_md5_hash(path)
        if new_hash is not None:
            hashdb = Genie.load_file_hash_db()
            hashdb[path.name] = new_hash
            Genie.save_file_hash_db(hashdb)
            print("*****  Successfully Updated hashdb file *******")

    @staticmethod
    def protected_status(filename):
        print("*****  Getting protected status *******")
        path = Path(filename)
        current_hash = Genie.generate_md5_hash(path)
        hashdb = Genie.load_file_hash_db()

        if current_hash is not None:
            if hashdb:
                saved_hash = hashdb.get(filename.name, "")
                if saved_hash:
                    if current_hash == saved_hash:
                        return True
                    else:
                        # backup file
                        print("*****  file changed - backup file *******")
                        return False
                else:
                    # hashdb file exists but file hash is not found
                    return True
            else:
                # hashdb file does not exist
                return True
        else:
            print(f"***** WARNING: Protected file: {filename} cannot be found ****")

    def use_dynamic_variables(self) -> None:
        """Get dynamic script name, run it and get the results from a dotenv file."""
        print("********* run_dynamic_script ************")
        dynamic_script = self._osenv.get("INPUT_DYNAMIC_SCRIPT")
        if os.path.exists(dynamic_script):
            print(f"running dynamic script: {dynamic_script}")
            print(f"files exists: {os.path.exists(dynamic_script)}")
            subprocess.run(["python", dynamic_script])
        env_file = "".join([Path(dynamic_script).stem, ".env"])
        if os.path.exists(env_file):
            with open(env_file) as file:
                contents = read_context_data("env", file, None)
                print(contents)
                self._var_dict.update(contents)
                os.remove(env_file)
        print(self._var_dict)

    def use_env_variables(self) -> None:
        """Add os environ variables to a dictionary"""
        print("********* load from Env ************")
        self._var_dict.update({"env": self._osenv})
        print(self._var_dict)

    def use_manual_variables(self) -> None:
        """Collect manual variables from the workflow and extract into a dictionary."""
        print("********* load from Variables ************")
        for variable in self._osenv.get("INPUT_VARIABLES", "").split("\n"):
            clean_variable = bytes(variable.strip(), "utf-8").decode("unicode_escape")
            if clean_variable != "":
                name, value = clean_variable.split("=", 1)
                self._var_dict.update({name: value})
                print(f"{name}: {value}")
        print(self._var_dict)

    def use_data_source(self) -> None:
        """Process the data source file and extract key, value pairs into dictionary."""
        print("********* load from Data File ************")
        data_source: str = self._osenv.get("INPUT_DATA_SOURCE")
        data_type: str = self._osenv.get("INPUT_DATA_TYPE")
        if data_source:
            print(f"data file {data_source}")
            if data_type == "":
                data_type = self.get_extension(data_source) or self.determine_file_type(
                    data_source
                )
                if data_type is None:
                    raise ValueError("Cannot determine data type for data source")

            print(f"data_type: {data_type}")
            with suppress(FileNotFoundError):
                with open(data_source) as file:
                    contents = read_context_data(data_type, file, None)
                    print(f"data source contents: {contents}")
                    self._var_dict.update(contents)
        print(self._var_dict)

    @staticmethod
    def get_extension(file: str) -> str:
        path = Path(file)
        extension = path.suffix.lower().lstrip(".")
        if extension in ("toml", "env", "ini", "json", "yml", "yaml"):
            return extension

    @staticmethod
    def determine_file_type(file: str | Path) -> str:
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
        print("********** Rendering the template ****************")
        with open(self._osenv["INPUT_TEMPLATE"]) as file:
            template_kwargs = {}
            if self._osenv.get("INPUT_STRICT") == "true":
                template_kwargs.update({"undefined": StrictUndefined})
            template = Template(str(file.read()), **template_kwargs)

        with open(self._osenv["INPUT_TARGET"], "w") as file:
            print("********** writing output file ****************")
            file.write(template.render(**self._var_dict) + "\n")
        print(
            f"********** contents of {self._osenv['INPUT_TARGET']} *************"
        )
        with open(self._osenv["INPUT_TARGET"], "r") as file:
            print(file.read())

        if self._osenv.get("INPUT_PROTECT") == "true":
            Genie.update_hashdb(self._osenv["INPUT_TARGET"])
