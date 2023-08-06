"""Module with functions for 'terminal' subpackage."""

from __future__ import annotations
from pathlib import Path
import subprocess
import platform
import importlib.util
import sys

import mylogging

from ..paths import PathLike, WslPath, validate_path


def is_wsl():
    """Check whether script runs in Windows Subsystem for Linux or not.

    Returns:
        bool: True or False based on using wsl.
    """
    return "microsoft-standard" in platform.uname().release


SHELL_AND = " && "
"""If using some nonstandard shell can be edited here globally. ';' can be used if && not working."""
PYTHON = "python" if platform.system() == "Windows" and not is_wsl() else "python3"


def convert_to_wsl_command(command: str) -> str:
    """Convert linux command so it can run on wsl.

    Args:
        command (str): Command to be converted.

    Returns:
        str: Converted command with escaped symbols.

    Note:
        If using `subprocess` with `shell=False`, it should not be converted.
    """
    for i in ["^", "&", "$", "|", "<", ">"]:
        command = command.replace(i, f"^{i}")
    return command


class TerminalCommandError(Exception):
    """Error that function `terminal_do_command` raises.

    Just changing the name of exception, so it's clear where it come from.
    """

    pass


def terminal_do_command(
    command: str,
    shell: bool = True,
    cwd: None | PathLike = None,
    verbose: bool = True,
    error_header: str = "",
    with_wsl: bool = False,
    input_str: None | str = None,
) -> str:
    """Run command in terminal and process output.

    Args:
        command (str): Command to run.
        shell (bool, optional): Same meaning as in ``subprocess.run()``. Defaults to False.
        cwd (None | PathLike, optional): Same meaning as in ``subprocess.run()``. Defaults to None.
        verbose (bool, optional): Whether print output to console. Defaults to True.
        error_header (str, optional): If meet error, message at the beginning of message. Defaults to "".
        with_wsl (bool, optional): Prepend wsl prefix and edit command so it works. Path needs to be edited
            manually (for example with `wsl_pathlib` package). Defaults to False
        input_str (None | str): Input inserted into terminal. It can be answer `y` for example if terminal needs
            an confirmation. Defaults to None.

    Raises:
        RuntimeError: When process fails to finish or return non zero return code.

    Example:
        >>> res = terminal_do_command("python --version")
        <BLANKLINE>
        Python ...
        <BLANKLINE>
    """
    error = "Terminal command crashed internally in subprocess and did not finished."

    if cwd:
        cwd = validate_path(cwd)

    if with_wsl:
        command = "wsl " + command

        if shell:
            command = convert_to_wsl_command(command)
        if cwd:
            cwd = WslPath(cwd)

    if input_str:
        input_bytes = input_str.encode("utf-8")
    else:
        input_bytes = None

    try:
        result = subprocess.run(command, shell=shell, cwd=cwd, capture_output=True, input=input_bytes)
        stdout = result.stdout.decode("utf-8", errors="replace").strip("\r\n")
        if result.returncode == 0:
            if verbose:
                print(f"\n{stdout}\n")
            return stdout
        else:
            stderr = result.stderr.decode("utf-8", errors="replace").strip("\r\n")
            if stderr:
                stderr = "\n\n" + stderr
            else:
                stderr = "\n"

            error = f"\n\nstderr:{stderr}\n\nstdout:\n\n{stdout}\n\n"

            raise TerminalCommandError("Return code is not 0.")

    except Exception as err:  # pylint: disable=broad-except

        header = f"{error_header}\n\n" if error_header else ""
        cwd_str = "on your project root" if cwd is None else f"in '{cwd}' folder"

        raise TerminalCommandError(
            f"{header}"
            "Used command"
            f"\n\n{mylogging.colors.colorize(command)}\n\n"
            f"Command execution in terminal failed. Try command above in the terminal on path {cwd_str} "
            "On windows use cmd so script paths resolved correctly. Try it with administrator rights.\n\n"
            f"Captured error: {error}",
        ) from err


def get_console_str_with_quotes(string: PathLike):
    """In terminal if value or contain spaces, it's not taken as one param.

    This wraps it with quotes to be able to use paths and values as needed. Alternative to this function is to
    use python shlex library, list of commands and 'shlex.join' to get the command string.

    Args:
        string (str, Path): String  to be edited.

    Returns:
        str: Wrapped string that can be used in terminal.

    Example:
        >>> get_console_str_with_quotes("/path to file/file")
        '"/path to file/file"'
    """
    if isinstance(string, (Path)):
        string = string.as_posix()
    if not isinstance(string, str):
        string = str(string)
    string = string.strip("'")
    string = string.strip('"')
    return f'"{string}"'


def which(name) -> None | Path:
    """Return path of defined script.

    It's similar to `whichcraft.which` or `shutil.which` with the difference that it will work also if calling
    with `wsl python code_with_which.py`. If script not available, None is returned. If it's found, pathlib
    Path is returned, not string.

    Args:
        name (str): Name of the script. For example `python`, 'black', or 'pytest'.

    Returns:
        None | Path: Path to script or None if it's not available.

    Example:
        >>> which("pip").exists()
        True
    """
    if is_wsl():
        which = f". {sys.prefix}/bin/activate && which "
    else:
        which = "where " if platform.system() == "Windows" else "which "

    command = which + name

    result = subprocess.run(command, shell=True, capture_output=True)

    output = result.stdout.decode("utf-8", errors="replace").rstrip("\r\n")

    if "\r\n" in output:
        output = output.split("\r\n")[0]

    if result.returncode != 0 or not output or not Path(output).exists():
        return None
    else:
        return Path(output)


def check_script_is_available(name, install_library=None, message="default"):
    """Check if python script is available.

    This doesn't need to be installed in current venv, but anywhere on computer.

    Args:
        name (str): Name of the script. E.g "black'.
        install_library (str, optional): Install script with this library added to default message.
            Defaults to None.
        message (str, optional): Message that will be printed when library not installed.
            Defaults to "default".

    Raises:
        RuntimeError: If module is installed, error is raised.

    Example:
        >>> check_script_is_available("pip")
        >>> check_script_is_available("not_existing_script")
        Traceback (most recent call last):
        RuntimeError: ...
    """
    if message == "default":
        message = f"Python script {name} is necessary and not available. "

    if install_library:
        message = message + f"\nTo get this executable available, do \n\n\tpip install {name}\n\n"

    if not which(name):
        raise RuntimeError(message)


def check_library_is_available(name, message="default", extras: str | None = None):
    """Make one-liner for checking whether some library is installed.

    If running on venv, it checks only this venv, no global site packages.

    Note:
        This function has much worse performance, than simple try with ModuleNotFoundError error. This is
        beneficial only if don't know the name of a package.

    Args:
        name (str): Name of the library.
        message (str, optional): Message that will be printed when library not installed.
            Defaults to "default".
        extras (str, optional): Sometimes there are sections of requirements that are installable with extra
            pip command e.g. `pip install mypythontools[plots]`. If you define a name of a library with name
            of extras, for example 'mypythontools[plots]', it will be printed to the user, so he is able to
            install all libraries at once. Defaults to None.

    Raises:
        ModuleNotFoundError: If module is installed, error is raised.

    Example:
        >>> check_library_is_available("typing_extensions")
        >>> check_library_is_available("not_installed_lib")
        Traceback (most recent call last):
        ModuleNotFoundError: ...
    """
    if message == "default":
        message = (
            f"Library {name} is necessary and not available. Some libraries are used in just for small"
            f"part of module, so not installed by default. Use \n\n\tpip install {name}\n\n"
        )

    if extras:
        message = message + (
            "There may be more libraries you will need for this use case. There are extra requirements to be "
            "installed. You can install it with  \n\n\tpip install {extras}\n\n"
        )

    if not importlib.util.find_spec(name):
        raise ModuleNotFoundError(message)
