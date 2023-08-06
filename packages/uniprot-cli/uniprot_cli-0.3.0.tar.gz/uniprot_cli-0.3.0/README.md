# `uniprot-cli` - An Unofficial client for Uniprot

`uniprot-cli` is an Unofficial client for the Uniprot protein database
written in python.

This project is still in its early stages under heavy development.
Do not expect this to work properly until `v1.0.0`.

## Installation

Installation is done with `pip`:

```{sh}
pip install uniprot-cli
```

## Usage

`uniprot-cli` has two modes of usage, an interactive-mode and a cli-mode.
The interactive-mode can be invoked by simply running:
```{sh}
uniprot-cli
```
And the user will be prompted for relevant input, step by step.

The cli-mode is used by passing arguments to `uniprot-cli` in the terminal:

Example:
```{sh}
uniprot-cli -q B5ZC00
```

This will cause `uniprot-cli` to skip interactive prompts and query Uniprot directly.

## Arguments

The following arguments can be passed to `uniprot-cli` in cli-mode:

| Argument           | Type   | Default | Explaination                     |
| ------------------ | ------ | ------- | -------------------------------- |
| `-q`, `--query`    | `str`  | `None`  | ID to query                      |
| `-m`, `--multiple` | `bool` | `False` | Query multiple results           |
| `-h`, `--help`     |  N/A   |  N/A    | Print help and usage information |
