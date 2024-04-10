from pprint import pprint
import subprocess
from . import Project

def Command(ParentPrj: Project.Project = None, *args):
    result = subprocess.run(["cmake", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout
    errors = result.stderr
    print("CMake output:")
    pprint(output)
    print("CMake errors:")
    pprint(errors)
    if len(errors) >= 1:
        print("err_leng:", len(errors))
        ParentPrj.Prj_Run_Errors["Cmake"] = errors
        ParentPrj.Prj_Exec_error = 1

