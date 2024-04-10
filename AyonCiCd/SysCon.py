import sys
import subprocess
import platform
import os
from . import Project
from pprint import pprint

def open_software(software_path, ParentPrj: Project.Project = None, *args):
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
        ParentPrj.Prj_Run_Errors["Open_Software"] = errors
        ParentPrj.Prj_Exec_error = 1

