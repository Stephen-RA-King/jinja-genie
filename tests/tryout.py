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
from jinja2 import StrictUndefined, Template



def generate_md5_hash(file_path):
    """
    Generate MD5 hash for a file.
    """
    with open(file_path, "rb") as file:
        md5_hash = hashlib.md5()
        while True:
            data = file.read(4096)
            if not data:
                break
            md5_hash.update(data)
        return md5_hash.hexdigest()

def generate_package_md5_hashes(package_dir):
    """
    Generate MD5 hashes for all files within a package, and the whole package.
    """
    package_hash = hashlib.md5()

    for root, _, files in os.walk(package_dir):
        for file in files:
            print(file)
            file_path = os.path.join(root, file)
            file_hash = self.generate_md5_hash(file_path)
            print(f"MD5 hash of {file_path}: {file_hash}")
            package_hash.update(file_hash.encode("utf-8"))

    print(f"MD5 hash of the entire package: {package_hash.hexdigest()}")


def walk_dir(package_dir):
    for root, dirs, files in os.walk(package_dir):
        path = root.split(os.sep)
        print((len(path) - 1) * "---", os.path.basename(root))
        for file in files:
            print(len(path) * "---", file)


ROOT_DIR = Path(__file__).parents[0]
hash_dir = ROOT_DIR / "resources" / "md5_hash_files"
file_path = hash_dir / "LICENSE"

print(generate_md5_hash(file_path))
