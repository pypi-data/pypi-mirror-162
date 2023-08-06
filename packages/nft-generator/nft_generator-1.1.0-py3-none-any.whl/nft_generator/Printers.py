"""
This module include variants of print function. They are necessary to support ``log to file`` feature.
Also, support colored output in console.
"""

from typing import TextIO

COLOR_OK = "\033[92m"
COLOR_FAIL = "\033[91m"
COLOR_WARNING = "\033[93m"
COLOR_NORMAL = "\033[0m"


def print_ok(msg: str = "OK.", fd: TextIO = None) -> None:
    """
    Print in ``green`` color (ASCII code = ``\033[92m``) color. The color will be recovered to normal before this function returns.

    :param msg: The message to be printed.
    :param fd: If given, write the output also to the file. See also :func:`MatrixTestRunner.run() <MatrixTest.MatrixTestRunner.MatrixTestRunner.run>`.
    :return: None
    """
    print(COLOR_OK + msg + COLOR_NORMAL)
    if fd is not None:
        fd.write(msg + '\n')


def print_ok_with_prefix(msg: str, msg_ok: str = "OK.", fd: TextIO = None) -> None:
    """
    Print in ``green`` color (ASCII code = ``\033[92m``) color. The color will be recovered to normal before this function returns.

    :param msg: The message to be printed before the colored part.
    :param msg_ok: The message to be printed after `msg` and colored.
    :param fd: If given, write the output also to the file. See also :func:`MatrixTestRunner.run() <MatrixTest.MatrixTestRunner.MatrixTestRunner.run>`.
    :return: None
    """
    print("INFO: " + msg + COLOR_OK + msg_ok + COLOR_NORMAL)
    if fd is not None:
        fd.write("INFO: " + msg + msg_ok + '\n')


def print_warning(msg: str, fd: TextIO = None):
    """
    Print in ``yellow`` color (ASCII code = ``\033[93m``). The color will be recovered to normal before this function returns.

    :param msg: The message to be printed.
    :param fd: If given, write the output also to the file. See also :func:`MatrixTestRunner.run() <MatrixTest.MatrixTestRunner.MatrixTestRunner.run>`.
    :return: None
    """
    print(COLOR_WARNING + "WARNING: " + COLOR_NORMAL + msg)
    if fd is not None:
        fd.write("WARNING: " + msg + '\n')


def print_error(msg: str, fd: TextIO = None):
    """
    Print in ``red`` color (ASCII code = ``\033[91m``). The color will be recovered to normal before this function returns.

    :param msg: The message to be printed.
    :param fd: If given, write the output also to the file. See also :func:`MatrixTestRunner.run() <MatrixTest.MatrixTestRunner.MatrixTestRunner.run>`.
    :return: None
    """
    print(COLOR_FAIL + "ERROR: " + COLOR_NORMAL + msg)
    if fd is not None:
        fd.write("ERROR: " + msg + '\n')


def print_aborted(fd: TextIO = None):
    """
    Print in ``red`` color (ASCII code = ``\033[91m``) and exit with return code 1.
    The color will be recovered to normal before this function returns.

    :param fd: If given, write the output also to the file. See also :func:`MatrixTestRunner.run() <MatrixTest.MatrixTestRunner.MatrixTestRunner.run>`.
    """
    print(COLOR_FAIL + "Aborted." + COLOR_NORMAL)
    if fd is not None:
        fd.write("Aborted." + '\n')
    exit(1)


def print_info(msg: str, fd: TextIO = None):
    """
    Print with prefix ``INFO:``

    :param msg: The message to be printed.
    :param fd: If given, write the output also to the file. See also :func:`MatrixTestRunner.run() <MatrixTest.MatrixTestRunner.MatrixTestRunner.run>`.
    :return:
    """
    print("INFO: " + msg)
    if fd is not None:
        fd.write("INFO: " + msg + '\n')


def print_plain(msg: str, fd: TextIO = None, end: str = '\n'):
    """
    Just print.

    :param msg: The message to be printed.
    :param fd: If given, write the output also to the file. See also :func:`MatrixTestRunner.run() <MatrixTest.MatrixTestRunner.MatrixTestRunner.run>`.
    :param end: Same as the built-in ``print()``.
    :return:
    """
    print(msg, end=end)
    if fd is not None:
        fd.write(msg + end)