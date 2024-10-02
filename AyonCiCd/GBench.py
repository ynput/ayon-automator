import os
from . import cmd
from typing import Optional


def run_google_benchmark(
    GBenchPath: str,
    OutFilePath: str,
    time_unit: Optional[str] = "ms",
    env: Optional[os._Environ] = None,
    *args,
):
    """function for running google benchmark (this function will not register errors as benchmarks should not be used for testing)

    Args:
        GBenchPath: path to the Gbnech program that you want to run
        OutFilePath: path to where gbench should output its output file
        time_unit: define the time unit that google bench should output. ns/usd/ms/s
        *args: extra arguments to be passed to google bench
    """
    args = list(args)

    if not time_unit in ["ns", "us", "ms", "s"]:
        time_unit = "ms"

    if not env:
        env = os.environ.copy()

    GBnechPath = os.path.abspath(GBenchPath)
    OutFilePath = os.path.abspath(OutFilePath)
    os.makedirs(os.path.dirname(OutFilePath), exist_ok=True)

    OutCommand = [
        f"--benchmark_time_unit={time_unit}",
        f"--benchmark_out={OutFilePath}",
    ]
    command = [GBnechPath] + OutCommand + args
    cmd.run(command, env=env)
