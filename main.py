"""Main python script to extract the key, value pairs and render the Jinja2 template.
"""
import hashlib
import os
import pickle
import subprocess
from contextlib import suppress
from pathlib import Path

from j2cli.context import read_context_data


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
            with open(Config.hash_db, 'wb') as file:
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
            with open(Config.hash_db, 'rb') as file:
                return pickle.load(file)

    @staticmethod
    def generate_md5_hash(file_path: Path) -> str:
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

        for path_object in dir_path.rglob('*'):
            if path_object.is_file():
                file_hash = Genie.generate_md5_hash(path_object)
                package_hash.update(file_hash.encode("utf-8"))

        return package_hash.hexdigest()

    def use_dynamic_data(self) -> None:
        """Get dynamic script name, run it and get the results from a dotenv file.
        """
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

    def use_os_environ(self):
        print("********* load from Env ************")
        self._var_dict.update({"env": self._osenv})
        print(self._var_dict)
