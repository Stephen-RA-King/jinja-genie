"""Main python script to extract the key, value pairs and render the Jinja2 template.
"""
import pickle
from contextlib import suppress


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

