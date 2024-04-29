from pprint import pprint
import subprocess
from Project import Project

def cmake_command(ParentPrj: Project, *args):
    """ function for running cmake commands 

    Args
        ParentPrj: parent project instance to register errors against 
        *args: arguments to be costed to cmake CLI
    """
    result = subprocess.run(["cmake", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout
    errors = result.stderr
    print("CMake output:")
    pprint(output)
    print("CMake errors:")
    pprint(errors)
    if len(errors) >= 1:
        print("err_leng:", len(errors))
        ParentPrj._project_runtime_errors["Cmake"] = errors
        ParentPrj._project_execuition_error_int = 1

