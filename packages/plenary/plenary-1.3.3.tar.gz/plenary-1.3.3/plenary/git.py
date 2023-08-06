# -*- coding: utf-8 -*-
import inspect
import os.path
import subprocess
import typing

__all__ = [
    'CommandNotFoundError',
    'GitCommandError',
    'get_git_hash'
]


class CommandNotFoundError(Exception):
    pass


class GitCommandError(Exception):
    pass


def get_git_hash(path: typing.Optional[str] = None) -> str:
    """ Fetch the current git commit hash of the specified director, optionally truncating the hash to a shorted format.

    Inspired by: https://stackoverflow.com/questions/12826723/possible-to-extract-the-git-repo-revision-hash-via-python-code

    :param path: path of git repository, defaults to callers module file path
    :return: hash as a string
    """
    if path is None:
        # Get caller from stack and get filename
        caller = inspect.getmodule(inspect.stack()[1][0])

        if caller is None or caller.__file__ is None:
            raise FileNotFoundError('Unable to determine path of caller')

        path = os.path.dirname(caller.__file__)

    try:
        git_process = subprocess.Popen(['git', 'rev-parse', 'HEAD'], cwd=path, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    except FileNotFoundError:
        raise CommandNotFoundError('git binary not accessible') from None

    # Read output from process
    (git_process_out, git_process_err) = git_process.communicate()

    # Decode output
    git_process_out_str = git_process_out.decode().strip()
    git_process_err_str = git_process_err.decode().strip()

    if len(git_process_err_str) > 0:
        raise GitCommandError(f"git binary returned error while fetching hash: {git_process_err!r}")

    return git_process_out_str
