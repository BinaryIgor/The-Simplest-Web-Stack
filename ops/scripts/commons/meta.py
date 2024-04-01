import sys
import os
from os import path, environ
import subprocess as sp

def print_and_exit(message):
    print(message)
    sys.exit(1)


def current_env():
    env = environ.get("ENV")
    if not env:
        raise Exception("Current ENV is not set!")
    return env


def is_current_env_local():
    return current_env() == 'local'


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


def config_dir():
    return path.join(root_dir(), "config")


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


def execute_bash_script(script, exit_on_failure=True):
    execute_script(f"""
    #!/bin/bash
    set -e

    {script}
    """, exit_on_failure=exit_on_failure)


def execute_script(script, exit_on_failure=True):
    try:
        code = sp.run(script, shell=True).returncode
        if code == 0:
            return

        if exit_on_failure:
            print(f"Fail to execute script, exiting with code: {code}")
            sys.exit(code)
        else:
            raise Exception(f"Fail to execute script, returned code: {code}")
    except KeyboardInterrupt:
        print("Script execution interrupted by the user, exiting")
        sys.exit(0)