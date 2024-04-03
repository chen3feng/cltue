"""
File system utility.
"""

import fnmatch
import os
import pathlib


def is_wildcard(text):
    """Check whether a string is a wildcard."""
    for c in text:
        if c in '*?![]':
            return True
    return False


def find_file_bottom_up(pattern, from_dir=None) -> str:
    """Find the specified file/dir from from_dir bottom up until found or failed.
       Returns abspath if found, or empty if failed.
    """
    if from_dir is None:
        from_dir = os.getcwd()
    finding_dir = os.path.abspath(from_dir)
    while True:
        files = os.listdir(finding_dir)
        for file in files:
            if fnmatch.fnmatch(file, pattern):
                return os.path.join(finding_dir, file)
        parent_dir = os.path.dirname(finding_dir)
        if parent_dir == finding_dir:
            return ''
        finding_dir = parent_dir
    return ''


def find_files_under(start_dir, patterns, excluded_dirs=None, relpath=False) -> list:
    """Find files under dir matching pattern."""
    result = []
    for root, dirs, files in os.walk(start_dir):
        if excluded_dirs:
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            for pattern in patterns:
                if fnmatch.fnmatch(file, pattern):
                    path = os.path.join(root, file)
                    if relpath:
                        path = os.path.relpath(path, start_dir)
                    result.append(path)
    return result


def expand_source_files(files, engine_dir) -> list:
    """
    Expand source file patterns to file list.
    files support the following format:
        An absolute path: /Work/MyGame/Source/MyGame/HelloWorldGreeterImpl.cpp
        A relative path: MyGame/HelloWorldGreeterImpl.cpp
        A wildcard pattern: Source/**/*Test.cpp
        A wildcard pattern with the @engine prefix: @engine/**/NetDriver.cpp
    Returns:
        A list of absolute paths of matching files.
    """
    matched_files = []
    patterns = []
    for file in files:
        start_dir = os.getcwd()
        if file.startswith('@engine'):
            file = file.removeprefix('@engine')
            if file.startswith('/') or file.startswith('\\'):
                file = file[1:]
            start_dir = engine_dir
        if not is_wildcard(file):
            matched_files.append(os.path.join(start_dir, file))
        else:
            patterns.append((start_dir, file))

    if patterns:
        for start_dir, pattern in patterns:
            for path in pathlib.Path(start_dir).glob(pattern):
                if 'Intermediate' in path.parts:
                    continue
                matched_files.append(str(path.absolute()))

    return matched_files
