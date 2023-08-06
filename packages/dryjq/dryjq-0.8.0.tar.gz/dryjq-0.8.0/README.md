# Drastically Reduced YAML / JSON Query

Lightweight package providing a subset of
[yq](https://mikefarah.gitbook.io/yq/) or
[jq](https://stedolan.github.io/jq/) functionality:

-   get a single value from a YAML or JSON file
-   change a single value in a YAML or JSON file


## Requirements

[PyYAML](https://pypi.org/project/PyYAML/) (Version 5.4.1 or newer)

## Installation

```
pip install dryjq
```

Installation in a virtual environment or with the `--user` option is recommended.


## Usage

Please see the documentation at <https://blackstream-x.gitlab.io/python-dryjq>
for detailed usage information.

The documentation is generated from the MarkDown files
in this repository’s `docs/` directory.

Output of `dryjq --help` (or `python3 -m dryjq --help`):

```
usage: dryjq [-h] [--version] [-i] [-d | -v | -q] [-o OUTPUT_FORMAT]
             [--indent {2,4,8}] [--sort-keys]
             [query] [input_file]

Drastically Reduced YAML / JSON Query

positional arguments:
  query                 the query (simplest form of yq/jq syntax, default is
                        '.').
  input_file            the input file name (by default, data will be read
                        from standard input)

options:
  -h, --help            show this help message and exit
  --version             print version and exit
  -i, --inplace         modify the input file in place instead of writing the
                        result to standard output

Logging options:
  control log level (default is WARNING)

  -d, --debug           output all messages (log level DEBUG)
  -v, --verbose         be more verbose (log level INFO)
  -q, --quiet           be more quiet (log level ERROR)

Output options:
  control output formatting

  -o OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        output format (choice of 'JSON': set output format to
                        JSON, 'YAML': set output fromat to YAML, 'input': keep
                        input format, 'toggle': change JSON to YAML or vice
                        versa; default: 'input')
  --indent {2,4,8}      indentation depth of blocks, in spaces (default: 2)
  --sort-keys           sort mapping keys (by default, mapping keys are left
                        in input order)
```

## Issues, feature requests

Please open an issue [here](https://gitlab.com/blackstream-x/python-dryjq/-/issues)
if you found a bug or have a feature suggestion.

