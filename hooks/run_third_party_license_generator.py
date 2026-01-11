#!/usr/bin/env python3

"""Third-Party License Generator.

Script to run the third-party license generator in a temporary virtual
environment.
"""

import argparse
import subprocess
import sys
import tempfile
from os import path
from typing import Self


def main() -> int:
    """Run the third-party license generator command.

    The head and tail lines are removed from the generated file as it contains
    dates, which are non-deterministic.

    Returns:
        Exit status code from the generator process.
    """
    extra_args: list[str] = sys.argv[1:]
    try:
        return_code: int = run_generator(extra_args)
    except subprocess.CalledProcessError as error:
        return error.returncode
    else:
        name = parse_output_file()
        remove_head_tail(name)
        return return_code


def run_generator(extra_args: list[str] | None = None) -> int:
    """Execute the third-party license generator.

    Args:
        extra_args: Additional command-line arguments to forward to the
        generator.

    Returns:
        Exit status code from the generator invocation.
    """
    extra_args = extra_args or []
    with TempVenv() as tmp_venv:
        cmd: list[str] = [
            tmp_venv.executable,
            "-m",
            "third_party_license_file_generator",
            "--requirements-path",
            "pyproject.toml",
            "--python-path",
            sys.executable,
            "--skip-prefix",
            "fc",
            "--skip-prefix",
            "fr",
            "--skip-prefix",
            "FR",
            "--do-not-skip-not-required-packages",
        ]
        cmd.extend(extra_args)
        return subprocess.check_call(cmd)


class TempVenv:
    """Context manager that creates and tears down a temporary virtual
    environment."""

    _temp_dir: tempfile.TemporaryDirectory[str]
    venv: str
    executable: str

    def __init__(self):
        """Initialize the temporary virtual environment manager."""
        self._temp_dir = tempfile.TemporaryDirectory()
        self.venv = path.join(self._temp_dir.name, ".venv")
        self.executable = self._get_executable_path(self.venv)

    def _get_executable_path(self, venv_path: str) -> str:
        """Compute the Python executable path for the virtual environment.

        Args:
            venv_path: Path to the root of the virtual environment.

        Returns:
            Absolute path to the Python executable within the virtual environment.
        """
        if sys.platform == "win32":
            return path.join(venv_path, "Scripts", "python.exe")
        else:
            return path.join(venv_path, "bin", "python")

    def __enter__(self) -> Self:
        """Create the virtual environment and install dependencies.

        Returns:
            Self: Temporary virtual environment context manager.
        """
        _ = subprocess.check_call(["python", "-m", "venv", self.venv])
        _ = subprocess.check_call(
            [
                self.executable,
                "-m",
                "pip",
                "install",
                "third-party-license-file-generator",
            ]
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Clean up the temporary directory when leaving the context.

        Args:
            exc_type: Exception type raised within the context, if any.
            exc_value: Exception instance raised within the context, if any.
            traceback: Traceback associated with the raised exception, if any.
        """
        self._temp_dir.cleanup()


def parse_output_file() -> str:
    """Parse the output file name from command line arguments.

    Defaults to THIRDPARTYLICENSES if not specified.

    Returns:
        The output file name.
    """
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("-o", "--output-file")
    args, _ = parser.parse_known_args()
    return getattr(args, "output_file", "THIRDPARTYLICENSES")


def remove_head_tail(file_path: str) -> None:
    """Remove the first and last lines from a file.

    Args:
        file_path: Path to the file to modify.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if len(lines) > 2:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines[1:-1])
    else:
        raise ValueError(
            "File must contain more than two lines to remove head and tail."
        )


if __name__ == "__main__":
    sys.exit(main())
