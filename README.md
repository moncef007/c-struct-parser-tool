# Struct Parser Tool

Extract C struct values from binary memory dumps using C header definitions.

## Features

- Parse `typedef struct { ... } name;` definitions from header files
- Extract values at given offset or scan entire dump
- Support for arrays, nested structs, strings, and common C types
- JSON or human-readable output

## Install

```bash
pip install c-struct-parser-tool
```
## How to Build & Install Locally
```bash
pip install -e .
# or
python -m build
pip install dist/*.whl
```

## License
This project is licensed under the GNU General Public License v3.0 or later — see [LICENSE](LICENSE) for details.