_**A GitHub action that leverages the Jinja2 and j2cli python libraries for templating files in your repository.**_

_**Use dynamic templating to keep your templates up to date with any external source like a scraped item from the web or a database entry etc.**_ 


![](assets/jina-genie.png)

# Contents

-   [Features](#-Features)
-   [Quick Start](#-Quick-Start)
-   [Project Rationale](#-Project-Rationale)
-   [Configuration](#-configuration)
-   [Usage](#-usage)
    -   [A quick word about the Jinja Templating Language](#a-quick-word-about-the-jinja-templating-language)
    -   [Basic Usage](#basic-usage)
        - [1. Using workflow 'env' static variables](#1-using-workflow-env-static-variables)
        - [2. Using static variables with the 'variable' keyword](#2-using-static-variables-with-the-variable-keyword)
        - [3. Using a data source for the variables](#3-using-a-data-source-for-the-variables)
        - [4. Using 'dynamic' variables with a script](#4-using-dynamic-variables-with-a-script)
    -   [Data source file types](#data-source-file-types)
        - [1. Dotenv](#1-dotenv)
        - [2. toml / ini](#2-toml--ini)
        - [3. yaml](#3-yaml)
        - [4. json](#4-json)
    -   [Using a script to template using dynamic variables](#using-a-script-to-template-using-dynamic-variables)
    -   [Protecting a target file](#protecting-a-target-file)
    -   [Using 'Strict' mode](#using-strict-mode)
    -   [Using multiple templating jobs or steps](#using-multiple-templating-jobs-or-steps)
    -   [Completing the Workflow.yaml file](#completing-the-workflowyaml-file)
-   [FAQ](#-faq)
-   [What's new in the next version ](#-whats-new-in-the-next-version-)
-   [License](#-license)
-   [Meta](#ℹ-meta)


## 🌟 Features

---
- Use various sources for variable inputs:
   - Use scripts to scrape dynamic data from various sources
   - Use data source files of various data types
   - Use workflow 'env' variables to source variables
- Data source files can be:
   - dotenv
   - ini
   - toml
   - yaml
   - json
- specify target files to protect from accidental templating
- Leverage the Jinja2 templating language

## 🚀 Quick Start

---
- Create your template file

config.conf.j2
```file
USERNAME = {{ username }}
HOST = {{ host }}
PORT = {{ port }}
```

- Configure your workflow file

```file
...
jobs:
  template:
    runs-on: ubuntu-latest
      - name: Jinja templating with environment variables
        uses: stephen-ra-king/jinja-genie@v1
        with:
          template: config.conf.j2
          target: config.conf
        env:
          USERNAME: sking
          HOST: 192.168.0.1
          PORT: 5432
...
```

## ❓ Project Rationale

---
I have a project with a readme which references the current project count on PyPI.
Obviously this count is very dynamic and changes hour by hour.  Manually updating this reference is out of the question.
I needed a templating solution utilizing the Jinja templating language with an automated solution periodically
running.  None of the GitHub action that I searched for provided for this scenario.

## ⚙️ Configuration

---
### Inputs


| Input          | Description                                                    | Required | Default |
|----------------|----------------------------------------------------------------|----------|---------|
| data_source    | Path, filename for a source file containing key, value pairs  | False    | ""      |
| data_type      | Data type of the data_source - env, toml, yaml, yml, ini, json | False    |   ""    |
| dynamic_script | Path, filename of a script that retrieves dynamic data | False    | "" |
| env | Key, value pairs in yaml format (key: value) | False    | "" |
| protect        | Turns protection from accidental overwrite for a target on | False    | "" |
| template       | Path , filename for the template file that will be rendered with data | **True** | "" |
| target | Target for the rendered template | **True** | "" |
| variables | Key, value pairs in .env file format (key=value) | False    | "" |
| strict | Determines if action will fail on missing values | False    | "" |


## 📝 Usage

---
### A quick word about the Jinja Templating Language
I wont be covering Jinja and will assume that you already some knowledge of the language. And yes it is a language 
which has conditionals and loop structures etc.  Jinja is incredibly useful and used by many well known applications such as:
Django, Flask, Ansible, NAPALM, Pelican etc. Jinja's combination of logic, control structures, and variable interpolation makes 
it highly useful for creating dynamic output based on various input data.

Some Jinja Resources:

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Real Python - "Jinja2: The Python Template Engine](https://realpython.com/primer-on-jinja-templating/)
- [The Flask Mega-Tutorial Part II: Templates](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates)


### Basic Usage

#### 1. Using workflow 'env' static variables

Github workflow environment variable can be utilized in the usual way in the workflow file.
Key, value pairs are specified in the in yaml format (key: value)

```file
jobs:
  template1:
    runs-on: ubuntu-latest
    steps:
      - name: Jinja templating with environment variables
        uses: Stephen-RA-King/jinja-genie@v1
        with:
          template: templates/env_variables.txt.j2
          target: targets/env_variables.txt
        env:
          SERVER_HOST: staging.example.com
          TIMEOUT: 90
```

#### 2. Using static variables with the 'variable' keyword

Key, value pairs can be specified in the dotenv style format (key=value)

```file
jobs:
  template2:
    runs-on: ubuntu-latest
    steps:
      - name: Jinja templating using variables
        uses: Stephen-RA-King/jinja-genie@main
        with:
          template: templates/variables.txt.j2
          target: targets/variables.txt
        variables: |
          server_host=staging.example.com
          timeout=45
```

#### 3. Using a data source for the variables

The variables can be specified in a separate file that can be one of the following formats: dotenv, yaml, json, ini or toml.

create the data source file (e.g. an ini here)

ini_data_file
````file
[APP]
ENVIRONMENT = development
DEBUG = True

[DATABASE]
USERNAME = sking
PASSWORD = ********
HOST = 127.0.0.1
PORT = 5432
DB = database
````

Then in the workflow file specify the data source file name and data type as follows:

```file
jobs:
  template3:
    runs-on: ubuntu-latest
    steps:
      - name: Jinja templating with data file - ini
        uses: Stephen-RA-King/jinja-genie@v1
        with:
          template: templates/ini_template_file
          target: targets/ini_target_file
          data_source: templates/ini_data_file
          data_type: ini
```

#### 4. Using 'dynamic' variables with a script

Create the python script necessary to extract the required data. [(More on this later)](#using-a-script-to-template-using-dynamic-variables)

Then specify the script in the workflow file:

```file
jobs:
  template4:
    runs-on: ubuntu-latest
    steps:
      - name: Jinja templating using dynamic script
        uses: Stephen-RA-King/jinja-genie@v1
        with:
          template: templates/counter.txt
          target: targets/counter.txt
          dynamic_script: scripts/templater.py
```

### Data source file types
Values to use in the workflow file

| File Type                                                       | workflow value to use |
|-----------------------------------------------------------------|-----------------------|
| [Dotenv](https://hexdocs.pm/dotenvy/0.2.0/dotenv-file-format.html)                                                 | env |
| [Tom's Obvious, Minimal Language](https://toml.io/en/)          | toml |
| [YAML Ain't Markup Language](https://yaml.org/spec/1.2.2/)      | yaml or yml |
| [Initialization](https://en.wikipedia.org/wiki/INI_file)   | ini |
| [JavaScript Object Notation](https://www.json.org/json-en.html) | json |


#### 1. Dotenv

```file
ENVIRONMENT=development
DEBUG=True
HOST=127.0.0.1
PORT=5432
```

#### 2. toml / ini

```file
[APP]
ENVIRONMENT = development
DEBUG = True

[DATABASE]
HOST = 127.0.0.1
PORT = 5432
```

#### 3. yaml

```file
---
APP:
  ENVIRONMENT: development
  DEBUG: true

DATABASE:
  HOST: 127.0.0.1
  PORT: 5432
```

#### 4. json

```file
{
  "APP": {
    "DEBUG": true,
    "ENVIRONMENT": "development"
  },
  "DATABASE": {
    "HOST": "127.0.0.1",
    "PORT": 5432,
  }
}
```


### Using a script to template using dynamic variables

For obvious reasons I cannot write these scripts for you. 

However it must follow a pattern and contain certain structures:

e.g.
dynamic_script.py
```python
#!/usr/bin/env python3

from pathlib import Path

env_file = "".join([Path(__file__).stem, ".env"])

def write_to_env_file(key, value):
    entry = "".join([key, "=", value, "\n"])
    with open(env_file, mode="a") as file:
        file.write(entry)

def get_value1():
    # Write the steps necessary to get "value1" here  
    write_to_env_file("KEY1", "value1")

def get_value2():
    # Write the steps necessary to get "value2" here
    write_to_env_file("KEY2", "value2")

def main():
    get_value1()
    get_value2()

if __name__ == "__main__":
    SystemExit(main())
```
Essentially you get as many variables as you like, with whatever methods you like.

The bottom line is that it must create an 'env' file with the same name
as the script (in the same location) except with an 'env' extension and thats it.

### Protecting a target file
Obviously with templating you are accepting the fact that the target will be overwritten each time the template is rendered.
So if you make a change to a target file (commit and push), you will loose those changes the next time the template is rendered.

You can 'protect' a file from a single templating operation using the 'protect' input keyword.

```file
...
jobs:
  template:
    runs-on: ubuntu-latest
      - name: Jinja templating with environment variables
        uses: stephen-ra-king/jinja-genie@v1
        with:
          template: config.conf.j2
          target: config.conf
          protect: true
        env:
          USERNAME: sking
          HOST: 192.168.0.1
          PORT: 5432
...
```
If the action determines that the target has been altered since the last templating the action will fail and you will get a message
similar to the following in the action run log:

```file
***** WARNING: Target file has been altered since last templating.
It is advisable to update the template *****
```

This will give you a chance to revise your work workflow.
The next time the action runs however the target will be overwritten.
The design of this may change in future.


### Using 'Strict' mode
By default, when a variable is undefined in a Jinja2 template, the engine will treat it 
as an empty string ("") and continue rendering the template without raising any errors. 
This behavior can lead to potential bugs and make it harder to detect issues when 
working with templates.

The 'strict' mode helps improve template robustness and prevent silent errors caused by
undefined variables. When StrictUndefined is enabled, Jinja2 raises an exception 
whenever an undefined variable is encountered during template rendering. This makes it 
easier to identify and handle missing or incorrect data in your templates.

```
...
jobs:
  template:
    runs-on: ubuntu-latest
      - name: Jinja templating with environment variables
        uses: stephen-ra-king/jinja-genie@v1
        with:
          template: config.conf.j2
          target: config.conf
          strict: true
        env:
          USERNAME: sking
          HOST: 192.168.0.1
          PORT: 5432
...
```


### Using multiple templating jobs or steps
You can use multiple templating steps in one job. However, if one step fails the all the following steps
will be skipped.  You can avoid this ny using multiple jobs but this has an overhead.

### Completing the Workflow.yaml file
Up until now I've only concentrated on the jinja-genie action.  But to have a fully operation workflow you will need
to utilize other actions as well:

For example you will need to 'checkout' your repository, fetch and merge remote repository changes
and use git to add and commit changed files:

Here is what a fully functional 'jinja-genie.yaml' workflow file looks like:

```file
name: Jinja-Genie templater

on:
  push:
    branches: ["main"]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repo
        uses: actions/checkout@v3

      - name: Fetch and Merge Remote Changes
        run: git pull origin main

      - name: Jinja templating with environment variables
        uses: Stephen-RA-King/jinja-genie@v1
        with:
          template: templates/env_variables.txt.j2
          target: targets/env_variables.txt
        env:
          SERVER_HOST: staging.example.com
          TIMEOUT: 90

      - name: Commit changes
        uses: EndBug/add-and-commit@v9
        with:
          author_name: Jinja Genie
          author_email: JinjaGenie@github.com
          message: "Jinja2 template successfully applied"
          add: .
```

## ❓ FAQ

---
Q. Can I use any other language apart from Python to get 'dynamic' variables?

A. No


## 📰 What's new in the next version 

- Undecided yet


## 📜 License

---
Distributed under the MIT license.


## <ℹ️> Meta

---
[![](assets/linkedin.png)](https://www.linkedin.com/in/sr-king)
[![](assets/github.png)](https://github.com/Stephen-RA-King)
[![](assets/www.png)](https://stephen-ra-king.github.io/justpython/)
[![](assets/email2.png)](mailto:sking.github@gmail.com)


Author: Stephen R A King ([sking.github@gmail.com](mailto:sking.github@gmail.com))



<!-- Markdown link & img dfn's -->

[bandit-image]: https://img.shields.io/badge/security-bandit-yellow.svg
[bandit-url]: https://github.com/PyCQA/bandit
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-url]: https://github.com/psf/black
[codeql-image]: https://github.com/Stephen-RA-King/templatetest/actions/workflows/github-code-scanning/codeql/badge.svg
[codeql-url]: https://github.com/Stephen-RA-King/templatetest/actions/workflows/github-code-scanning/codeql
[isort-image]: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
[isort-url]: https://github.com/pycqa/isort/
[license-image]: https://img.shields.io/pypi/l/templatetest
[license-url]: https://github.com/Stephen-RA-King/templatetest/blob/main/LICENSE
[mypy-image]: http://www.mypy-lang.org/static/mypy_badge.svg
[mypy-url]: http://mypy-lang.org/
[wiki]: https://github.com/Stephen-RA-King/templatetest/wiki
