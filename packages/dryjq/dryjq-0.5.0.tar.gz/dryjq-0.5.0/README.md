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
usage: dryjq [-h] [-v] [-q] [--version] [--modify-in-place] [-of {JSON,YAML}]
             [-oi {2,4,8}] [-osk]
             [query] [input_file]

Drastically Reduced YAML / JSON Query

positional arguments:
  query                 The query (simplest form of yq/jq syntax, default is
                        '.').
  input_file            The input file name. By default, data will be read
                        from standard input.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Output all messages including debug level
  -q, --quiet           Limit message output to errors
  --version             Print version and exit
  --modify-in-place     Modify the input file in place instead of writing the
                        result to standard output.

Output options:
  control how output will be formatted

  -of {JSON,YAML}, --output-format {JSON,YAML}
                        File format. By default, the detected input format is
                        used.
  -oi {2,4,8}, --output-indent {2,4,8}
                        Indentation depth of blocks, in spaces (default: 2).
  -osk, --output-sort-keys
                        Sort mapping keys. By default, mapping keys are left
                        in input order.
```

## Issues, feature requests

Please open an issue [here](https://gitlab.com/blackstream-x/python-dryjq/-/issues)
if you found a bug or have a feature suggestion.

