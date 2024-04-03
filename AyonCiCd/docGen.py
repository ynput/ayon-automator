from pprint import pprint
from . import Project
import subprocess
import os


def DoxygenRun(doxyFile, ParentPrj: Project.Project = None):
    DoxyFileName = os.path.basename(doxyFile)
    filePath = os.path.dirname(doxyFile)
    print(DoxyFileName, filePath)
    result = subprocess.run(["doxygen", f"{DoxyFileName}"],cwd=filePath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout
    errors = result.stderr
    print("doxygen output:")
    pprint(output)
    print("doxygen errors:") 
    pprint(errors)
    if len(errors) >= 1:
        print("err_leng:", len(errors))
        ParentPrj.Prj_Run_Errors["doxygen"] = errors
        ParentPrj.Prj_Exec_error = 1

