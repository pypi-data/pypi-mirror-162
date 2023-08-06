# Domain monitoring & registration with AWS route53

![build](https://github.com/MousaZeidBaker/dm53/workflows/Publish/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
![python_version](https://img.shields.io/badge/python-%3E=3.8-blue)
[![pypi_v](https://img.shields.io/pypi/v/dm53)](https://pypi.org/project/dm53)

## Usage

Show help message and exit
```shell
dm53 --help
```

Check availability of a domain
```shell
dm53 check --domain-name example.com
```

> Note: Make sure AWS credentials are configured, following example uses env
> variables
> ```shell
> AWS_ACCESS_KEY_ID=my-access-key \
> AWS_SECRET_ACCESS_KEY=my-secret-access-key \
> dm53 check --domain-name example.com
> ```
> for more details see [boto3
> docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)

Keep checking with a 5 seconds interval until the domain becomes available
```shell
dm53 check --domain-name example.com --monitor --interval 5
```

Register a domain if available

```shell
dm53 check --domain-name example.com --register --path /path/to/registration-details.json
```

> Note: Registration details must be provided through a JSON file, see [this
> example](https://github.com/MousaZeidBaker/dm53/blob/master/example-registration-details.json)
> or read more in [AWS
> docs](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_RegisterDomain.html)

Run in background to ignore hangup signal with
[nohup](https://man7.org/linux/man-pages/man1/nohup.1.html), forward output to
`examplecom.out`
```shell
nohup dm53 check --domain-name example.com --monitor > examplecom.out 2>&1 &
```

> Note: The `nohup` command prints a shell job ID and a process ID. Terminate
> the process with `kill -9 <PID>`.

## Contributing
Contributions are welcome via pull requests.

## Issues
If you encounter any problems, please file an
[issue](https://github.com/MousaZeidBaker/dm53/issues) along with a detailed
description.

## Develop
Activate virtual environment
```shell
poetry shell
```

Install dependencies
```shell
poetry install --remove-untracked
```

Install git hooks
```shell
pre-commit install --hook-type pre-commit
```

Run linter
```shell
flake8 .
```

Format code
```shell
black .
```

Sort imports
```shell
isort .
```

Install current project from branch
```shell
poetry add git+https://github.com/MousaZeidBaker/dm53.git#branch-name
```
