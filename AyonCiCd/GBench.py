import os
from . import cmd



def GBnechRun(GBenchPath: str, OutFilePath:str, *args):
    """ function for running google benchmark (this function will not register errors as benchmarks should not be used for testing)

    Args:
        GBenchPath: path to the Gbnech program that you want to run 
        OutFilePath: path to where gbench should output its output file
        *args: extra arguments to be passed to google bench  
    """
    GBnechPath = os.path.abspath(GBenchPath)
    OutFilePath = os.path.abspath(OutFilePath)
    os.makedirs(os.path.dirname(OutFilePath), exist_ok=True)
    OutCommand = ["--benchmark_time_unit=ms",f"--benchmark_out={OutFilePath}"]
    command = [GBnechPath] + OutCommand + list(args)
    cmd.run(command)
