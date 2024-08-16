from collections.abc import Callable
import io
import os
from typing import Any, Dict, List
import venv
import sys
import shutil
import subprocess
import inspect
import json
import site
from contextlib import redirect_stdout, redirect_stderr
from pprint import pprint
from datetime import datetime
from . import helpers


class Func:
    func_name: str
    func: Callable[..., Any]
    args: List[Any]
    kwargs: Dict[Any, Any]

    def __init__(
        self, name: str, in_func_name: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        self.func_name = name
        self.func = in_func_name
        self.args = list(args)
        self.kwargs = dict(kwargs)

    def run(self):
        args = []
        kwargs = {}
        for i in self.args:
            try:
                args.append(i())
            except Exception:
                args.append(i)
        for key, val in self.kwargs.items():
            eval_key: Any
            eval_val: Any
            try:
                eval_key = key()
            except Exception:
                eval_key = key
            try:
                eval_val = val()
            except Exception:
                eval_val = val
            kwargs[eval_key] = eval_val

        self.func(*args, **kwargs)


class Project:
    """Class to describe a project for execution usage.
    Attributes:
        project_name: Name used to identify and to make CLI
            availability easier.
        base_output_folder_path: auto generated path that describing the base
            folder for venv and stage_artefact_list.
        _root_exec_script:  auto generated variable holding the root of the
            execution graph (deprecated)
        var_json_file_path: path describing the location for the json file used to keep track off _project_internal_varialbes cross execution
        _project_internal_varialbes: a ditc off variables set and made available to every function
        _build_artefacts_out_path: the base path where the build stage_artefact_list will be stored
        _project_stage_list: a list off all stages available to the project. (mainly used by executAllStages)
        _project_stage_groups_list: list off stage groups (used for runStageGRP)
        _runtime_python_version_major_minor_str: variable holding a string representation off the major.minor number describing the python version. (useful for folder actions inside off the venv)
        _build_venv_abs_path: path to the base folder off the build venv
        _project_requested_pip_packes: list off pip packages to be installed by setup()
        _project_runtime_errors: dict off errors cased by functions while running. useful for debugging
        _project_execuition_error_int: int used for sys.exit() in order to flag a run as failed.
    """

    # Construction / Destruction
    def __init__(self, project_name: str) -> None:
        """Setup _project_internal_varialbes and env.
        Call meth:`_add_prj_build_venv_path_to_sys_path()` and meth:`_load_vars_from_prj_json_file()`,
        the function will also call setup if the venv path does not exist.
        Args:
            project_name:str used to define a name for the project. (will most often be the same as the name off the tool set or project your currently testing)
        """

        # project
        self.project_name = project_name
        self.base_output_folder_path = os.path.abspath(project_name + "_cicd")
        self._root_exec_script = inspect.stack()[1].filename
        # project vars
        self.var_json_file_path = os.path.abspath(
            os.path.join(
                self.base_output_folder_path,
                f"{self.project_name}__project_internal_varialbes.json",
            )
        )
        self._project_internal_varialbes: Dict[Any, Any] = {}
        # artefacts
        self._build_artefacts_out_path = os.path.abspath(
            os.path.join(self.base_output_folder_path, "artefacts")
        )
        # stages
        self._project_stage_list: List[Any] = []
        # stage groups
        self._project_stage_groups_list: Dict[Any, Any] = (
            {}
        )  # TODO rename to make name a dict
        # python infos
        self._runtime_python_version_major_minor_str = (
            str(sys.version_info.major) + "." + str(sys.version_info.minor)
        )
        # Venv infos
        self._build_venv_abs_path = os.path.abspath(
            os.path.join(self.base_output_folder_path, (project_name + "_BuildVenv"))
        )
        self._project_requested_pip_packes: List[Any] = []
        # Exec Data
        self._project_runtime_errors: Dict[Any, Any] = {}
        self._project_execuition_error_int = 0
        self._is_setup_process = False

        if "setup" in sys.argv:
            self._is_setup_process = True
            self.setup()

    def __del__(self):
        """function to cast sys.exit(1) if project errors have accrued. this is important as sys.exit(1) will cause github action to flag the run as failed"""
        """it is possible that we are not casing an Error while in the Stage Execution. (this is so we can run multiple tests and get more data in one run)
        we will log this error here and then exit with a non Zero error code so that tools like GitHub actions natively pick up the error and flag the run as Failed"""

        if not self._project_execuition_error_int == 0:
            self.log(
                "__del__()",
                f"Finished Execution with code:{self._project_execuition_error_int}, {self._project_runtime_errors}",
            )
            sys.exit(1)

    # While Enter Exit stage_function_list
    def __enter__(self):
        """enter function to allow for using this class in a with statement. this is needed for the make_project_cli_available() func
        this will also call _add_prj_build_venv_path_to_sys_path in order to make sure that the right side packages are available

        Returns: returns class instance reference
        """

        self._add_prj_build_venv_path_to_sys_path()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """function needed for exiting with block. this will also write out the Globally accessible _project_internal_varialbes to the variable json file.
        the reason why we write out the data after the with is because os module is not available in __del__()

        Args:
            exc_type ():
            exc_value ():
            traceback ():
        """

        if not exc_value == 0 and not exc_value is None:
            self.log(
                "__exit__()",
                f"Project ExitLog: type: {exc_type}, val: {exc_value}, traceback: {traceback}",
            )

        with open(self.var_json_file_path, "w") as json_file:
            json.dump(self._project_internal_varialbes, json_file)

    # Startup Helpers
    def setup(self):
        """setup function used to generate the venv and to install all needed packages
        this should be called in a separate process before running any tests"""

        if self._is_setup_process:
            if os.path.exists(self.base_output_folder_path):
                shutil.rmtree(self.base_output_folder_path)
                print("Deleted Root foulder")

            os.mkdir(self.base_output_folder_path)
            os.mkdir(self._build_artefacts_out_path)

            self._creat_venv(self._build_venv_abs_path)

            self._install_pip_packages_in_venv(
                self._build_venv_abs_path, self._project_requested_pip_packes
            )

            print("finsihed Setup")
            sys.exit(0)

        self._add_prj_build_venv_path_to_sys_path()
        self._load_vars_from_prj_json_file()

    def setup_prj(self):
        if "setup" in sys.argv:
            self._is_setup_process = True
            self.setup()

    def _add_prj_build_venv_path_to_sys_path(self):
        """function for adding the side packages installed under the venv to the current python accessible path.
        this allows access to the packages without having to activate the venv"""

        venv_python = None

        if sys.platform.startswith("win"):
            venv_python = os.path.join(
                self._build_venv_abs_path, "Scripts", "python.exe"
            )

        elif sys.platform.startswith("linux"):
            venv_python = os.path.join(self._build_venv_abs_path, "bin", "python")
        else:
            raise RuntimeError("Your platform is not suported")

        command = "import sysconfig; print(sysconfig.get_path('purelib'))"
        output = subprocess.check_output([venv_python, "-c", command])
        venv_site_packages = os.path.abspath(output.decode("utf-8").strip())
        site.addsitedir(venv_site_packages)

    def make_project_cli_available(self):
        """function used in a with block to make the current class instance availalbe to the cli. (python script.py -arg -arg)
        this allows usage from cli and access to all functions in this class"""

        if len(sys.argv) > 1:
            function_name = sys.argv[1]
            if hasattr(self, function_name) and callable(getattr(self, function_name)):
                params = sys.argv[2:]
                getattr(self, function_name)(*params)
            else:
                print("Function not found or not callable!")

    # Helper stage_function_list
    def stop_execution(self):
        """helper function that just calls sys.exit(). Exists in order to convey intend"""
        sys.exit()

    def log(self, TopInfo: str, *args):
        """simple logging function that allows to print formatted log outputs to keep output readable and consistent

        Args:
            TopInfo:str name or text to be printed at the top off the log (commonly used to show the function that prints the log)
            *args:str list off things to be printed. (will be printed via pprint())
        """

        spacing = int((80 - len(TopInfo)) / 2)
        print("-" * spacing, TopInfo, "-" * spacing)
        pprint(args)
        print("-" * 80, "\n")

    # Variable stage_function_list

    def _load_vars_from_prj_json_file(self):
        """function used to load the variable.json into the project local variable store. This allows for _project_internal_varialbes to be set by one execution run and consumed by another."""

        if not os.path.exists(self.var_json_file_path):
            os.makedirs(os.path.dirname(self.var_json_file_path), exist_ok=True)
            with open(self.var_json_file_path, "w") as json_file:
                json.dump({"CreationTime": datetime.utcnow().isoformat()}, json_file)

        with open(self.var_json_file_path, "r") as jsonVarFile:
            self._project_internal_varialbes = json.load(jsonVarFile)

        self.log(
            "Loading Json Variable's File for ths Project",
            self._project_internal_varialbes,
        )

    def setVar(self, VarName, VarValue):
        """function for setting a variable in the project local _project_internal_varialbes store. all functions set with this function will be stored in the variables.json.
        this function also allows for overwriting off _project_internal_varialbes
        in the end the variable store is a dict and so you will need a key(Name) and a value(Value) pair for setting a variable

        Args:
            VarName:
            VarValue:
        """

        self._project_internal_varialbes[VarName] = VarValue
        self.log(
            "setVar()",
            f"varName={VarName} VarValue={self._project_internal_varialbes[VarName]}",
        )

    def displayVar(self, VarName: str):
        """function to display what value a variable has at the current time.

        Args:
            VarName:str
        """
        self.log(
            "displayVar()",
            f"varName={VarName} VarValue={self._project_internal_varialbes[VarName]}",
        )

    def getVar(self, VarName: str):
        """function to retrieve the value of a variable

        Args:
            VarName:str
        Returns: value off a given varialbe or None if the key is not found via .get()
        """

        if self._project_internal_varialbes.get(VarName) is not None:
            return self._project_internal_varialbes[VarName]

        return None

    # Stage stage_function_list
    def add_stage(self, stageInstance) -> None:
        """function to add stage to the project.
        will append stage instance to _project_stage_list via append() this allows you to append a stage multiple times. But doing so is consider UB and is thereby not advised.
        Args:
            stageInstance:
        """

        self._project_stage_list.append(stageInstance)
        stageInstance.parentOutputFoulder = self._build_artefacts_out_path

    def _call_stage_execution(self, Stage) -> None:
        """function for executing a stage and formatting the output.
        Args:
            Stage: stageInstance
        """

        fileName = f"{Stage.StageName}.txt"
        filePos = os.path.join(self._build_artefacts_out_path, fileName)

        print()
        print("-" * 80)
        print("Running Stage: ", Stage.StageName)
        print("Output file path: ", filePos)
        print()

        with open(filePos, "w") as file:
            output = Stage.exec_stage(self)
            file.write(output)

        print("-" * 80)

    # Cli stage_function_list
    def execAllStages(self) -> None:
        """function to execute all stages in order off _project_stage_list
        will internally call _call_stage_execution() in a loop"""

        self.setup()
        for _, stage in enumerate(self._project_stage_list):
            self._call_stage_execution(stage)

    def execSingleStage(self, stage_Identifier) -> None:
        """function to execute a single stage by identifier
        will internally call _call_stage_execution()
        Args:
            stage_Identifier: stageInstance
        """

        index = None
        self.log("execSingleStage()", stage_Identifier)

        try:
            index = self._project_stage_list[
                self._project_stage_list.index(stage_Identifier)
            ]
        except ValueError:
            for instance in self._project_stage_list:
                if instance.StageName == stage_Identifier:
                    index = instance

        if not index:
            print("Stage Not Found")
            return

        self._call_stage_execution(index)

    def runStageGRP(self, stageGRPName: str) -> None:
        stageGrp = self._project_stage_groups_list[stageGRPName]
        for stage in stageGrp:
            self._call_stage_execution(stage)

    # StageGRP stage_function_list
    def creat_stage_group(self, GrpName, *stageInstances) -> None:
        StageGrp = list(stageInstances)
        self._project_stage_groups_list[GrpName] = StageGrp

    # Venv stage_function_list
    def _creat_venv(self, venv_path):
        """helper function for creating a python venv
        will install pip, upgrade deps, clear venv if Existent
        Args:
            venv_path:
        """

        print(f"Creating Venv: {venv_path}")
        venv.create(env_dir=venv_path, clear=True, with_pip=True, upgrade_deps=True)
        print(f"Venv Creation Complete, Venv_Path: {venv_path}")

    def __get_venv_activate_cmd(self, venv_path):
        """helper function to get the correct venv activate script for win or Linux
        Args:
            venv_path:
        Returns:
        """

        if sys.platform.startswith("win"):
            activate_script = os.path.join(venv_path, "Scripts", "activate")
            activate_cmd = f"{activate_script}"
        else:
            activate_script = os.path.join(venv_path, "bin", "activate")
            activate_cmd = f"source {activate_script}"

        return activate_cmd


    def _install_pip_packages_in_venv(self, venv_path: str, pip_package_list: list):
        """helper function that will activate the venv, upgrade pip and install the package list. this will be executed in a subprocess
        Args:
            venv_path:
            pip_package_list:
        """

        pip_install_command = ""
        if len(pip_package_list):
            pip_install_list = " ".join(pip_package_list)
            pip_install_command = f"&& pip install {pip_install_list}"

        command = []

        if sys.platform.lower() == "win32":
            command =  ["cmd","/c"]

            command.extend([
                self.__get_venv_activate_cmd(venv_path),"&&", "python", "-m", "pip" ,"install" ,"--upgrade" ,"pip"
            ])

            if pip_install_command:
                command.append(pip_install_command)
        else:
            command = [
                f"{self.__get_venv_activate_cmd(venv_path)} && pip install --upgrade pip {pip_install_command}"
            ]

        process = subprocess.Popen(
            command,
            shell=True,
        )

        return_code = process.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)

        print("installed all packages")



    def add_pip_package(self, packageName: str) -> None:
        """appends a package name to _project_requested_pip_packes list so that _install_pip_packages_in_venv can consume them
        Args:
            packageName:
        """
        self._project_requested_pip_packes.append(packageName)

    def check_venv(self) -> bool:
        """Checks if the current script is running in a Venv
        Args:
            venv_name ():
        Returns:
            Bool: True if in Venv. False if not in Venv
        """
        return sys.prefix != sys.base_prefix


class Stage:
    """class used to describe a group off functions and artifact's
    Attributes:
        stage_function_list: a list off functions to be executed
        stage_artefact_list: a list off artifacts to be copied
        StageName:str identifier for the current stage
        parentOutputFoulder: a path set from the parent project
    """

    def __init__(self, StageName: str) -> None:
        self.stage_function_list: List[Func] = []
        self.stage_artefact_list: List[Any] = []
        self.StageName: str = StageName
        self.parentOutputFoulder = None

    def add_single_func(self, funcInstance: Func) -> None:
        """append a lambda to the stage function list.
        Args:
            funcInstance:
        """

        self.stage_function_list.append(funcInstance)

    def add_funcs(self, *args: Func) -> None:
        """append a list off lambdas to the stages function list. They will be added via a for loop
        *args:
        """

        for func in args:
            self.stage_function_list.append(func)

    def addArtefactFoulder(self, fouderPath) -> None:
        """adds an artifact to the stages stage_artefact_list list. this function also allows adding files as artifact's and is not yet renamed
        Args:
            fouderPath ():
        """

        self.stage_artefact_list.append(fouderPath)

    def copy_artefact(self, artefact_root, artefact_dest) -> None:
        """function to copy an artifact to its appropriate place
        Args:
            artefactPath ():
        """

        if not os.path.exists(artefact_dest):
            os.makedirs(artefact_dest)

        artefactDestinationPath = os.path.join(
            artefact_dest, os.path.basename(artefact_root)
        )

        if os.path.isfile(artefact_root):
            try:
                os.makedirs(os.path.dirname(artefactDestinationPath), exist_ok=True)
                shutil.copy(
                    os.path.abspath(artefact_root),
                    os.path.abspath(artefactDestinationPath),
                )
            except shutil.Error:
                print("No artefacts to Copy")

        else:
            try:
                if os.path.exists(artefactDestinationPath):
                    print("dir")
                    shutil.rmtree(artefactDestinationPath)
                shutil.copytree(os.path.abspath(artefact_dest), artefactDestinationPath)
            except shutil.Error:
                print("No artefacts to Copy")

    def exec_stage(self, parent_prj: Project):
        """this function will be called by every system that intends executing the stage
        this function will capture output that's running in it and will return it

        Returns: stdout and stderr captured while running stage
        """

        std_out_capture = io.StringIO()
        std_err_capture = io.StringIO()

        with redirect_stderr(std_err_capture):
            with redirect_stdout(std_out_capture):
                for func in self.stage_function_list:
                    print("#" * shutil.get_terminal_size().columns)
                    print(f"FuncName: {func.func_name}")
                    print("*" * shutil.get_terminal_size().columns)
                    try:
                        func.run()
                    except helpers.FaileException as e:
                        print(f"Test FAILED msg({str(e)})")
                        parent_prj._project_runtime_errors[func.func.__name__] = str(e)
                        parent_prj._project_execuition_error_int = 1
                    print("*" * shutil.get_terminal_size().columns)
                    print()

                for artefactPath in self.stage_artefact_list:

                    self.copy_artefact(
                        artefactPath,
                        os.path.join(
                            parent_prj._build_artefacts_out_path,
                            f"{self.StageName}_Artefacts",
                        ),
                    )

        sys.stdout.write(std_out_capture.getvalue())
        sys.stderr.write(std_err_capture.getvalue())

        tab = std_out_capture.getvalue() + " \n " + std_err_capture.getvalue()
        return tab
