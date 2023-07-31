_**A GitHub action that leverages the Jinja2 and j2cli python libraries for templating files in your repository.**_

_**Use dynamic templating to keep your templates up to date with any external source like a scraped item from the web or a database entry etc.**_ 


![](assets/jina-genie.png)

# Contents

-   [Features](#Features)
-   [Quick Start](#Quick-Start)
-   [Project Rationale](#Project-Rationale)- 
-   [Usage](#Usage)
    -   [Specifying multiple names](#Specifying-multiple-names)
-   [Planned Future improvements](#Planned-Future-improvements)






## 🌟 Features

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

I have a project with a readme which references the current project count on PyPI.
Obviously this count is very dynamic and changes hour by hour.  Manually updating this reference is out of the question.
I needed a templating solution utilizing the Jinja templating language with an automated solution periodically
running.  None of the GitHub action that I searched for provided for this scenario.

## ⚙️ Configuration

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

Create the python script necessary to extract the required data. (More on this later)

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

#### 1. json

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







### Protecting a target file





## ❓ FAQ

Give example of frequently asked questions


## 📰 What's new in version 

- bulleted list of new features


## 📜 License

Distributed under the {{cookiecutter.license}} license. See [![][license-image]][license-url] for more information.



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
