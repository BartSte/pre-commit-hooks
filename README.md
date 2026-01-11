# pre-commit-hooks

A small collection of pre-commit hooks that wrap common project automation tasks.

## Hooks

### `run-third-party-license-generator`

Generates a `THIRDPARTYLICENSES` report by creating a temporary virtual environment, installing `third-party-license-file-generator`, running the tool, and trimming the non-deterministic first and last lines from the output file. Configure it in your project’s `.pre-commit-config.yaml` using the hook ID `run-third-party-license-generator`.
