import functools
import os

from typing import Callable, List

# TODO: Decorator type hints????? 
# TODO: Improve clarity when initialising objects
def mutually_exclusive(keyword, *keywords):
    """Decorator raises a TypeError if input function arguments are not mutually
    exclusive."""
    keywords = (keyword,)+keywords
    def _wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if sum(k in keywords for k in kwargs) != 1:
                raise TypeError('You must specify exactly one of {}'.format(', '.join(keywords)))
            return func(*args, **kwargs)
        return inner
    return _wrapper

def get_file_contents(filename: str) -> str:
    """Returns the contents of a file."""
    with open(filename, 'r') as f:
        return f.read()
    
def isdir(fullpath: str) -> bool:
    """Returns true if is a file, and false if otherwise (a directory)."""
    try:
        if os.path.exists(fullpath):
            if os.path.isdir(fullpath):
                return True
            return False
    except FileNotFoundError:
        print(f'{fullpath} does not exist.')

def iterate_files(directory: str, search_subdirs: bool = True) -> List:
    """Iterates over the files in the given directory and returns a list of 
    found files."""
    files = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        fullpath = os.path.join(directory, filename)
        if (isdir(fullpath)):
            if search_subdirs:
                files += iterate_files(fullpath)
        else:
            files.append(fullpath)
    return files

def split_fullpath(fullpath: str) -> tuple[str, str, str]:
    """Splits the full path into the directory, filename, and extension."""
    head, tail = os.path.split(fullpath)
    tail, ext = os.path.splitext(tail)
    return head, tail, ext

def get_subdir_and_file_from_dir(fullpath: str, original_dir: str):
    """Returns the subdirectory and file from the original directory."""
    head, filename = os.path.split(fullpath)
    if fullpath.startswith(original_dir):
        subdirs = head.split(os.path.sep)[len(original_dir.split(os.path.sep)):]
        return subdirs, filename
    else:
        return [''], filename
