import subprocess
import os
from pprint import pprint
from .Project import Project

def doxygen_run(doxyFile, ParentPrj: Project):
    """ function to run doxygen in shell. 

    Args:
        doxyFile: path to doxy file  
        ParentPrj: parent project instance to register errors against 
    """
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
        ParentPrj._project_runtime_errors["doxygen"] = errors
        ParentPrj._project_execuition_error_int = 1

