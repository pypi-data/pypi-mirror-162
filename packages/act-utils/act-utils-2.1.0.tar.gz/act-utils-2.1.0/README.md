# ACT Utilities

## Introduction

This repository contains utility scripts for the [ACT Platform](https://github.com/mnemonic-no/act-platform).

## Installation
1. This project requires that you have a running installation of the [act-platform](https://github.com/mnemonic-no/act-platform).
2. Install from pip
```bash
pip install act-utils
```

## act-graph-datamodel usage

Build a graph (graphviz) of the ACT data model.
```bash
act-graph-datamodel --help
usage: act-graph-datamodel [-h] [--uid UID] [--http_username HTTP_USERNAME]
                           [--http_password HTTP_PASSWORD]
                           [--parent_id PARENT_ID]
                           [--confluence_url CONFLUENCE_URL]
                           [--confluence_user CONFLUENCE_USER]
                           [--confluence_password CONFLUENCE_PASSWORD]
                           url
```

# Local development

Use pip to install in [local development mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs). act-utils (and act-api) uses namespacing, so it is not compatible with using `setup.py install` or `setup.py develop`.

In repository, run:

```bash
pip3 install --user -e .
```
