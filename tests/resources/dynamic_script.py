import os
from pathlib import Path

ROOT_DIR = Path(__file__).parents[0]
env_file = "".join([Path(__file__).stem, ".env"])


def write_to_env_file(key, value):
    entry = "".join([key, "=", value, "\n"])
    with open(env_file, mode="a") as file:
        file.write(entry)


def counter():
    write_to_env_file("COUNTER", "60")


def hi():
    write_to_env_file("HELLO", "world")


def main():
    counter()
    hi()


if __name__ == "__main__":
    SystemExit(main())
