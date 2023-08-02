#!/usr/bin/env python3
import os

from main import Genie


def main(env_variables):
    genie = Genie(os.environ)
    genie.use_env_variables()

    if env_variables["INPUT_DYNAMIC_SCRIPT"] != "":
        genie.use_dynamic_variables()

    if env_variables["INPUT_VARIABLES"] != "":
        genie.use_manual_variables()

    if env_variables["INPUT_DATA_SOURCE"] != "":
        genie.use_data_source()

    genie.render_template()


if __name__ == "__main__":
    environ_variables = os.environ

    requires = environ_variables["INPUT_REQUIRES"]
    if requires != "":
        with open("requirements.txt", mode="a") as file:
            file.write(requires)

    SystemExit(main(environ_variables))
