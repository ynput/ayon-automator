import subprocess
import sys


def run(command, shell:bool=False):
    """ this function executes sub process run and captures the output to be redirect so that capturing class can capture it

    Args:
        command (): 
    """
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)

    sys.stdout.write(result.stdout.decode('utf8'))
    sys.stderr.write(result.stderr.decode('utf8'))
