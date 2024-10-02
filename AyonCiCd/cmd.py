import subprocess
import sys
import os
from typing import Optional


def run(
    command,
    shell: bool = False,
    env: Optional[os._Environ] = None,
):
    """this function executes sub process run and captures the output to be redirect so that capturing class can capture it

    Args:
        command ():
    """
    if not env:
        env = os.environ.copy()

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, env=env
    )

    sys.stdout.write(result.stdout.decode("utf8"))
    sys.stderr.write(result.stderr.decode("utf8"))
