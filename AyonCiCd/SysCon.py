import subprocess
import os
from .Project import Project
from pprint import pprint

def open_software(software_path, ParentPrj: Project, *args):
    """ function for running software in a sub process (deprecated its advised to use cmd.py run() Instead)

    Args:
        software_path (): 
        ParentPrj: 
        *args: 
    """
    os.path.abspath(software_path)
    command = [software_path] + list(args)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout
    errors = result.stderr
    print("open_software() output:")
    pprint(output)
    print("open_software() errors:") 
    pprint(errors)
    if len(errors) >= 1:
        print("err_leng:", len(errors))
        ParentPrj._project_runtime_errors["Open_Software"] = errors
        ParentPrj._project_execuition_error_int = 1

