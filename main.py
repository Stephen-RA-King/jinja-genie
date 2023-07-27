"""Main python script to extract the key, value pairs and render the Jinja2 template.
"""
import hashlib
import pickle
from contextlib import suppress
from pathlib import Path


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
            dir_path (Path): The directory & contents on which to calculate the MD5 hash.

        Returns:
            str: The generated MD5 hash value.
        """
        package_hash = hashlib.md5()

        for path_object in dir_path.rglob('*'):
            if path_object.is_file():
                file_hash = Genie.generate_md5_hash(path_object)
                package_hash.update(file_hash.encode("utf-8"))

        return package_hash.hexdigest()
