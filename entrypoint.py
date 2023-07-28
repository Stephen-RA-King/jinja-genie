#!/usr/bin/env python3


import os

from main import Genie


def main():
    genie = Genie(os.environ)
    
    genie.use_dynamic_variables()
    genie.use_env_variables()
    genie.use_manual_variables()
    genie.use_data_source()
    genie.render_template()


if __name__ == "__main__":
    SystemExit(main())

