import subprocess
import os
from typing import Optional
from .Project import Project

def cmake_command(ParentPrj: Project, env: Optional[os._Environ] , *args):
    """ function for running cmake commands 

    Args
        ParentPrj: parent project instance to register errors against 
        *args: arguments to be costed to cmake CLI
    """
    if not env:
        env = os.environ.copy()

    result = subprocess.run(["cmake", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    output = result.stdout
    errors = result.stderr
    print("CMake output:")
    print(output)
    
    warnings_clean = []
    errors_clean = []
    for i in errors.split("CMake "):
        if (len(i)>1):
            if("Warning" in i):
                warnings_clean.append(i.strip("\n"))
            else:
                errors_clean.append(i.strip("\n"))

    for warning in warnings_clean:
        if (len(warning)):
            print("CMake warnings:")
            print(warning + "\n")

    for error in errors_clean:
        if(len(error)):
            print("CMake errors:")
            print(error + "\n")
    
    if len(errors_clean):
        ParentPrj._project_runtime_errors["Cmake"] = errors_clean
        ParentPrj._project_execuition_error_int = 1

