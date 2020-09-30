# PowerShell Script to Setup Migration Execution Server

## Prerequisites

- Powershell 4/5

## Execution Server Setup

Install dependencies like python, etc using following script.

```ps1
.\1-install-dependencies.ps1
```

## Parse config.xlsx File

Install dependencies like python, etc using following script.

```ps1
.\2-parse-xlsx-sheet.ps1
```

## Configure AWS Credentials

Configure AWS credentials by running the following. 

```ps1
.\3-aws-credentials.ps1
```

## Defaults

By default, this script installs following:
  -  Python 3.7
     -  boto3
     -  awscli
     -  paramiko
     -  requests

If you want make changes to the defaults, update the following variables in the json file.

### config.json

This file contains defaults in terms of download URLs and locations.

```json
{
    "aws_credentials": "/path/to/aws_credentials.json",
    "intake_form": "automation_scripts\\0-Migration-intake-form.csv",
    "intake_tags": "automation_scripts\\0-import-tags.csv",
    "parameters": "parameters.json",
    "file_copy": null,

    "DOWNLOAD_PYTHON_URL": "https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe",
    "BASE_FOLDER": "C:\\migrations-demo",
    "INSTALL_PYTHON_FOLDER": "C:\\migration_dependencies\\Python37",
}
```
