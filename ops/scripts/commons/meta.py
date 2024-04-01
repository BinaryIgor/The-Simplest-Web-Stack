import sys
import os
from os import path, environ

def print_and_exit(message):
    print(message)
    sys.exit(1)


def current_env():
    env = environ.get("ENV")
    if not env:
        raise Exception("Current ENV is not set!")
    return env


def root_dir():
    start_cwd = os.getcwd()
    cwd = start_cwd
    root = None

    for _ in range(10):
        files = os.listdir(cwd)
        if 'ops' in files:
            root = cwd
            break

        cwd, _ = os.path.split(cwd)

    if root is None:
        raise Exception(f"Root dir not found, starting from: {start_cwd}")
    
    return root


def file_content(file_path):
    with open(file_path) as f:
        return f.read()


def binary_file_content(file_path):
    with open(file_path, "rb") as f:
        return f.read()


def write_to_file(file_path, content):
    with open(file_path, "w") as f:
        f.write(content)


def write_binary_to_file(file_path, binary):
    with open(file_path, "wb") as f:
        f.write(binary)