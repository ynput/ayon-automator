from . import Project
import subprocess
import os
from pprint import pprint




def GBnechRun(GBenchPath: str,OutFilePath:str ,ParentPrj: Project.Project = None, *args):

    GBnechPath = os.path.abspath(GBenchPath)
    OutFilePath = os.path.abspath(OutFilePath)
    os.makedirs(os.path.dirname(OutFilePath), exist_ok=True)

    OutCommand = ["--benchmark_time_unit=ms",f"--benchmark_out={OutFilePath}"]

    command = [GBnechPath] + list(OutCommand) + list(args)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


    output = result.stdout
    errors = result.stderr
    print("open_software() output:")
    pprint(output)
    print("open_software() errors:")
    print(errors)

