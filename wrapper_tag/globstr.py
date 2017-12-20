"""
globstr implements simple glob searching for strings

Example:

    kwarg_url_<int>
    kwargs_args_<string>
"""
import re

__cache__ = {}


def clear():
    """
    clear clears globs cache
    :return:
    """
    global __cache__
    __cache__ = {}


def get(glob: str):
    """
    get returns compiled regex for given glob
    :param glob:
    :return:
    """
    value = __cache__.get(glob, None)
    if value is None:
        value = re.compile(_quote(glob))
        __cache__[glob] = value
    return value


def _quote(glob: str):
    """
    _quote quotes glob as regular expression
    :param glob:
    :return:
    """
    glob = glob.replace("<int>", r"\d+")
    glob = glob.replace("<str>", r"[a-zA-Z]+")
    glob = glob.replace("<ident>", r"[a-zA-Z]{1}[a-zA-Z_\-0-9]+")
    glob = "^{}$".format(glob)
    return glob
