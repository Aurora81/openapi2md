# openapi2md
OpenAPI definitions to markdown

## Install

`python3 setup.py install`

## Usage
The package provides a command line tool.

```bash
$ openapi2md -h
usage: openapi2md [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [--locale LOCALE]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        The OpenAPI 3 YAML filepath
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The output filepath of the Markdown file
  --locale LOCALE       Locale to use when generating the Markdown file
```

## Test

### Command

```bash
$ openapi2md -i tests/test.yaml -o tests/test.md
```

### Result

