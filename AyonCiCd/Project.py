import os
import venv
import sys
from pprint import pprint
import shutil
import subprocess
import inspect
import json
from datetime import datetime
import site

class Capturing:
    """a class build to capture stdout and stderr output. 
    target off this class is make the output available as a variable for further use 

    Attributes: 
        stdout: fake stdout to capture + store output  
        stderr: fake stderr to capture + store output
        original_stdout: variable to store the original stdout to reusing it at __exit__
        original_stderr: variable to store the original stderr to reusing it at __exit__
    """
    def __enter__(self):
        self.stdout = ""
        self.stderr = ""
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
        return self

    def get_output(self)->str:
        """ function to retrieve the data captured by this class. 
        this will combine stdout and stderr into one string separated by an escape char. 

        Returns:
            
        """
        return self.stdout + "\n" + self.stderr 
        

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr 
        sys.stdout.write(self.stdout)
        sys.stdout.write(self.stderr)
        return

    def write(self, text):
        """ function for imitating stdout and capturing the data from it

        Args:
            text: input text to we written to stdout 
        """
        self.stdout += text

    def isatty(self):
        """ function for imitating color support info's. 
        currently this function just returns False and dose not actually test

        Returns:
            
        """
        return False


class Project():

    """ class to describe a project for execution usage

    Attributes: 
        ProjectName: Name attribute used to identify and to make cli availability easier 
        baseOutputFoulderPath: auto generated path that describing the base folder for Venv and Artifacts   
        rootExecuterScript:  auto generated variable holding the root off the execution graph (Discontinued)
        VariablesJsonFilePath: path describing the location for the json file used to keep track off variables cross execution
        Variables: a ditc off variables set and made available to every function
        buildArtefactsPath: the base path where the build artifacts will be stored 
        RegisteredStageList: a list off all stages available to the project. (mainly used by executAllStages)
        StageGrps: list off stage groups (used for runStageGRP)
        python_version: variable holding a string representation off the major.minor number describing the python version. (useful for folder actions inside off the venv)
        venvPath: path to the base folder off the build venv
        pipPackages: list off pip packages to be installed by setup()
        Prj_Run_Errors: dict off errors cased by functions while running. useful for debugging 
        Prj_Exec_error: int used for sys.exit() in order to flag a run as failed. 
    """
# Construction / Destruction 
    def __init__(self, projectName:str) -> None:

        """ init will setup variables and call add_venv_path_to_path() and loadJson() the function will also call setup if the venv path dose not exist

        Args:
            projectName:str used to define a name for the project. (will most often be the same as the name off the tool set or project your currently testing) 
        """
       
        # Project 
        self.ProjectName = projectName
        self.baseOutputFoulderPath = os.path.abspath(projectName+"_CiCd")
        self.rootExecuterScript = inspect.stack()[1].filename
        
        #Project vars
        self.VariablesJsonFilePath = os.path.abspath(os.path.join(self.baseOutputFoulderPath, f"{self.ProjectName}_Variables.json"))
        self.Variables = {}

        #artefacts
        self.buildArtefactsPath = os.path.abspath(os.path.join(self.baseOutputFoulderPath, "buildArtefacts"))

        #Stages 
        self.RegisteredStageList = []

        #StageGrps
        self.StageGrps = {}

        #Python infos 

        self.python_version = str(sys.version_info.major) + "." + str(sys.version_info.minor)
        
        #Venv infos
        self.venvPath = os.path.abspath(os.path.join(self.baseOutputFoulderPath, (projectName+"_BuildVenv")))
        self.pipPackages = []

        #Exec Data
        self.Prj_Run_Errors = {}
        self.Prj_Exec_error = 0

        if not os.path.exists(self.venvPath):
            self.setup()
            #TODO what doo i doo when setup has been run // it sould be run seperatly but this allows running it with exec stage (this will error tho)

        self.add_venv_path_to_path()
        self.loadJson()
 
    def __del__(self):
        """function to cast sys.exit(1) if project errors have accrued. this is important as sys.exit(1) will cause github action to flag the run as failed"""

        """it is possible that we are not casing an Error while in the Stage Execution. (this is so we can run multiple tests and get more data in one run)
        we will log this error here and then exit with a non Zero error code so that tools like GitHub actions natively pick up the error and flag the run as Failed"""
        if not self.Prj_Exec_error == 0:

            self.log("__del__()", f"Finished Execution with code:{self.Prj_Exec_error}, {self.Prj_Run_Errors}")
            sys.exit(1)


# While Enter Exit funcs    
    def __enter__(self):
        """enter function to allow for using this class in a with statement. this is needed for the makeClassCliAvailable() func
        this will also call add_venv_path_to_path in order to make sure that the right side packages are available

        Returns: returns class instance reference

            
        """
        self.add_venv_path_to_path()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ function needed for exiting with block. this will also write out the Globally accessible variables to the variable json file.
        the reason why we write out the data after the with is because os module is not available in __del__()

        Args:
            exc_type (): 
            exc_value (): 
            traceback (): 
        """
        if not exc_value == 0 and not exc_value == None:

            self.log("__exit__()", f"Project ExitLog: type: {exc_type}, val: {exc_value}, traceback: {traceback}")
        with open(self.VariablesJsonFilePath, "w") as json_file:
                json.dump(self.Variables, json_file)

# Startup Helpers
    def setup(self):
        """ setup function used to generate the venv and to install all needed packages 
        this should be called in a separate process before running any tests """
        if os.path.exists(self.baseOutputFoulderPath): 
            shutil.rmtree(self.baseOutputFoulderPath)
            print("Deleted Root foulder")
        os.mkdir(self.baseOutputFoulderPath)
        os.mkdir(self.buildArtefactsPath)

        self.create_venv(self.venvPath)
        self.install_pip_packes_in_venv(self.venvPath, self.pipPackages)
        print("finsihed Setup")
        self.add_venv_path_to_path()

    def add_venv_path_to_path(self):
        """function for adding the side packages installed under the venv to the current python accessible path. 
        this allows access to the packages without having to activate the venv"""
        venv_python = None
        if sys.platform.startswith('win'):
            venv_python = os.path.join(self.venvPath, "Scripts", "python.exe")
        elif sys.platform.startswith('linux'):
            venv_python = os.path.join(self.venvPath, "bin", "python")
        else:
            raise RuntimeError("Your platform is not suported")

        command = "import sysconfig; print(sysconfig.get_path('purelib'))"
        output = subprocess.check_output([venv_python, "-c", command])
        venv_site_packages = os.path.abspath(output.decode("utf-8").strip())
        site.addsitedir(venv_site_packages)

         

    def makeClassCliAvailable(self):
        """function used in a with block to make the current class instance availalbe to the cli. (python script.py -arg -arg)
        this allows usage from cli and access to all functions in this class"""
        if len(sys.argv) > 1:
            function_name = sys.argv[1]
            if hasattr(self, function_name) and callable(getattr(self, function_name)):
                params = sys.argv[2:]
                getattr(self, function_name)(*params)
            else:
                print("Function not found or not callable!")


# Helper Funcs 
    def stop_execution(self):
        """helper function that just calls sys.exit(). Exists in order to convey intend"""
        sys.exit()

    def log(self, TopInfo:str, *args):
        """simple logging function that allows to print formatted log outputs to keep output readable and consistent

        Args:
            TopInfo:str name or text to be printed at the top off the log (commonly used to show the function that prints the log)
            *args:str list off things to be printed. (will be printed via pprint())
        """
        spacing = int((80 - len(TopInfo))/2)
        print("-"*spacing, TopInfo, "-"*spacing)
        pprint(args)
        print("-"*80, "\n")


# Variable Funcs
    def loadJson(self):
        """function used to load the variable.json into the project local variable store. This allows for variables to be set by one execution run and consumed by another. """
        if not os.path.exists(self.VariablesJsonFilePath):
            os.makedirs(os.path.dirname(self.VariablesJsonFilePath), exist_ok=True)
            with open(self.VariablesJsonFilePath, "w") as json_file:
                json.dump({"CreationTime":datetime.utcnow().isoformat()}, json_file)
        with open(self.VariablesJsonFilePath, "r") as jsonVarFile:
            self.Variables = json.load(jsonVarFile)
        self.log("Loading Json Variable's File for ths Project", self.Variables)

    def setVar(self, VarName, VarValue):
        """function for setting a variable in the project local variables store. all functions set with this function will be stored in the variables.json. 
        this function also allows for overwriting off variables
        in the end the variable store is a dict and so you will need a key(Name) and a value(Value) pair for setting a variable
        Args:
            VarName: 
            VarValue: 
        """
        self.Variables[VarName] = VarValue
        self.log("setVar()",f"varName={VarName} VarValue={self.Variables[VarName]}")

    def displayVar(self, VarName:str):
        """ function to display what value a variable has at the current time. 

        Args:
            VarName:str 
        """
        self.log("displayVar()",f"varName={VarName} VarValue={self.Variables[VarName]}")

    def getVar(self, VarName:str):
        """function to retrieve the value of a variable 

        Args:
            VarName:str 

        Returns: value off a given varialbe or None if the key is not found via .get()
            
        """
        if self.Variables.get(VarName) != None:
            return self.Variables[VarName]
        return None


# Stage Funcs
    def addStage(self ,stageInstance) -> None:
        """ function to add stage to the project. 
        will append stage instance to RegisteredStageList via append() this allows you to append a stage multiple times. But doing so is consider UB and is thereby not advised.

        Args:
            stageInstance: 
        """
        self.RegisteredStageList.append(stageInstance)
        stageInstance.parentOutputFoulder = self.buildArtefactsPath

    def execStage(self, Stage) -> None:
        """ function for executing a stage and formatting the output. 

        Args:
            Stage: stageInstance 
        """
        fileName = f"{Stage.StageName}.txt"
        filePos = os.path.join(self.buildArtefactsPath, fileName)
        print()
        print("-"*80)
        print("Running Stage: ", Stage.StageName)
        print("Output file path: ", filePos)
        print()

        with open(filePos, "w") as file:
            output = Stage.execStage()
            file.write(output)
            
        print("-"*80)

    def execAllStages(self) -> None:
        """function to execute all stages in order off RegisteredStageList 
        will internally call execStage() in a loop"""
        self.setup()
        for _, stage in enumerate(self.RegisteredStageList):
            self.execStage(stage)

    def execSingleStage(self, stage_Identifier) ->None:
        """function to execute a single stage by identifier
        will internally call execStage()

        Args:
            stage_Identifier: stageInstance  
        """
        index = None
        self.log("execSingleStage()", stage_Identifier)
        try: 
            index = self.RegisteredStageList[self.RegisteredStageList.index(stage_Identifier)]
        except ValueError:
            for instance in self.RegisteredStageList:
                if instance.StageName == stage_Identifier:
                    index = instance
        if not index:
            print("Stage Not Found")
            return

        self.execStage(index)


# StageGRP Funcs
    def CreateStageGRP(self, GrpName, *stageInstances) -> None:
        StageGrp = list(stageInstances)
        self.StageGrps[GrpName] = StageGrp

    def runStageGRP(self, stageGRPName:str) -> None:
        stageGrp = self.StageGrps[stageGRPName]
        for stage in stageGrp:
            self.execStage(stage)


# Venv funcs
    def create_venv(self, venv_path):
        """helper function for creating a python venv 
        will install pip, upgrade deps, clear venv if Existent

        Args:
            venv_path: 
        """
        print(f"Creating Venv: {venv_path}")
        venv.create(env_dir=venv_path, clear=True, with_pip=True, upgrade_deps=True)
        print(f"Venv Creation Complete, Venv_Path: {venv_path}")

    def get_venv_activate_cmd(self, venv_path):
        """ helper function to get the correct venv activate script for win or Linux

        Args:
            venv_path: 

        Returns:
            
        """
        if sys.platform.startswith('win'):
            activate_script = os.path.join(venv_path, "Scripts", "activate")
            activate_cmd = f"{activate_script}"
        else:
            activate_script = os.path.join(venv_path, "bin", "activate")
            activate_cmd = f"source {activate_script}"

        return activate_cmd

    def install_pip_packes_in_venv(self, venv_path:str, pip_package_list:list):
        """helper function that will activate the venv, upgrade pip and install the package list. this will be executed in a subprocess

        Args:
            venv_path: 
            pip_package_list: 
        """
        pip_install_command = ""
        if len(pip_package_list):
            pip_install_list = " ".join(pip_package_list)
            pip_install_command = f"&& pip install {pip_install_list}"
        cmd_command = f"{self.get_venv_activate_cmd(venv_path)} && python -m pip install --upgrade pip {pip_install_command}"
        print(cmd_command)
        process = subprocess.Popen(cmd_command, shell=True)
        process.wait()
        print("installed all packages")

    def addPipPackage(self, packageName:str) -> None:
        """ appends a package name to pipPackages list so that install_pip_packes_in_venv can consume them

        Args:
            packageName: 
        """
        self.pipPackages.append(packageName)

    def check_venv(self) -> bool:
        """Checks if the current script is running in a Venv

        Args:
            venv_name (): 

        Returns:
            Bool: True if in Venv. False if not in Venv
            
        """
        return sys.prefix != sys.base_prefix






class Stage: 
    """ class used to describe a group off functions and artifact's 

    Attributes: 
        funcs: a list off functions to be executed 
        artifacts: a list off artifacts to be copied 
        StageName:str identifier for the current stage 
        parentOutputFoulder: a path set from the parent project 
    """
    def __init__(self, StageName:str) -> None:
        self.funcs = []
        self.artifacts = []
        self.StageName = StageName
        self.parentOutputFoulder = "" 

    def addFunc(self, funcInstance) -> None:
        """append a lambda to the stage function list. 

        Args:
            funcInstance: 
        """
        self.funcs.append(funcInstance)

    def addFuncs(self, *args) -> None:
        """ append a list off lambdas to the stages function list. They will be added via a for loop
            *args: 
        """
        for lambda_func in args:
            self.funcs.append(lambda_func)

    def addArtefactFoulder(self, fouderPath) -> None:
        """ adds an artifact to the stages artifacts list. this function also allows adding files as artifact's and is not yet renamed

        Args:
            fouderPath (): 
        """
        self.artifacts.append(fouderPath)

    def copy_artefact(self, artefactPath) -> None:
        """function to copy an artifact to its appropriate place 

        Args:
            artefactPath (): 
        """
        artefactBaseFoulder = os.path.join(self.parentOutputFoulder, (self.StageName + "_Artefacts"))
        if not os.path.exists(artefactBaseFoulder):
            os.makedirs(artefactBaseFoulder)
        artefactDestinationPath = os.path.join(artefactBaseFoulder, os.path.basename(artefactPath))

        if os.path.isfile(artefactPath):
            try:
                os.makedirs(os.path.dirname(artefactDestinationPath), exist_ok=True)
                shutil.copy(os.path.abspath(artefactPath), os.path.abspath(artefactDestinationPath))
            except shutil.Error:
                print("No artefacts to Copy")
        else:
            try:
                if os.path.exists(artefactDestinationPath):
                    print("dir")
                    shutil.rmtree(artefactDestinationPath)
                shutil.copytree(os.path.abspath(artefactPath), artefactDestinationPath)
            except shutil.Error:
                print("No artefacts to Copy")

    def execStage(self):
        """ this function will be called by every system that intends executing the stage 
        this function will capture output that's running in it and will return it

        Returns: stdout and stderr captured while running stage 
            
        """
        with Capturing() as output:
            for func in self.funcs:
                func()
            for artefactPath in self.artifacts:
                self.copy_artefact(artefactPath)

        return output.get_output()
