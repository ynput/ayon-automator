import os
from io import StringIO 
from os.path import basename, join
import sys
from pprint import pp, pprint
import shutil
import subprocess
import inspect
from . import pipfuncs
import json
from datetime import datetime

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio 
        sys.stdout = self._stdout


class Project():
    def __init__(self, projectName) -> None:
        self.Stages = []
        self.ProjectName = projectName
        self.baseOutputFoulderPath = os.path.abspath(projectName+"_CiCd")
        self.buildArtefactsPath = os.path.abspath(os.path.join(self.baseOutputFoulderPath, "buildArtefacts"))
        self.venvPath = os.path.abspath(os.path.join(self.baseOutputFoulderPath, (projectName+"_BuildVenv")))
        self.rootExecuterScript = inspect.stack()[1].filename
        self.Prj_Run_Errors = {}
        self.Prj_Exec_error = 0
        self.pipPackages = []
        self.Variables = {}
        self.StageGrps = {}
        self.jsonStorePos = os.path.abspath(os.path.join(self.baseOutputFoulderPath, f"{self.ProjectName}_Variables.json"))
        
        if (self.check_venv(self.ProjectName+"_BuildVenv") != True and not sys.argv[1] == "setup" ):
            callerArgs = " ".join(sys.argv[1:])
            self.activate_venv(self.venvPath, f"{self.rootExecuterScript} {callerArgs}")
            self.stop_execution()
        self.loadJson()
        
    def log(self, TopInfo, *args):
        spacing = int((80 - len(TopInfo))/2)
        print("-"*spacing, TopInfo, "-"*spacing)
        pprint(args)
        print("-"*80, "\n")

    def CreateStageGRP(self, GrpName, *stageInstances) -> None:
        StageGrp = list(stageInstances)
        self.StageGrps[GrpName] = StageGrp

    def runStageGRP(self, stageGRPName:str) -> None:
        stageGrp = self.StageGrps[stageGRPName]
        for stage in stageGrp:
            self.execStage(stage)

    def loadJson(self):
        if not os.path.exists(self.jsonStorePos):
            os.makedirs(os.path.dirname(self.jsonStorePos), exist_ok=True)
            with open(self.jsonStorePos, "w") as json_file:
                json.dump({"CreationTime":datetime.utcnow().isoformat()}, json_file)
        with open(self.jsonStorePos, "r") as jsonVarFile:
            self.Variables = json.load(jsonVarFile)
        self.log("Loading Json Variable's File for ths Project", self.Variables)

    def setVar(self, VarName, VarValue):
        self.Variables[VarName] = VarValue
        self.log("setVar()",f"varName={VarName} VarValue={self.Variables[VarName]}")

    def displayVar(self, VarName):
        self.log("displayVar()",f"varName={VarName} VarValue={self.Variables[VarName]}")

    def getVar(self, VarName):
        return self.Variables[VarName]

    def create_venv(self, venv_name):
        print(f"Creating Venv: {venv_name}")
        subprocess.run([sys.executable, "-m", "venv", venv_name], check=True)

    def activate_venv(self, venv_name, python_script_path):
        if sys.platform.startswith('win'):
            activate_script = os.path.join(venv_name, "Scripts", "activate")
            activate_cmd = f"{activate_script} && python {python_script_path}"
        else:
            activate_script = os.path.join(venv_name, "bin", "activate")
            activate_cmd = f"source {activate_script} && python -m pip install --upgrade pip && python {python_script_path}"

        process = subprocess.Popen(activate_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        print(stdout.decode())
        if len(stderr.decode()) >= 1:
            self.Prj_Exec_error = 1
            self.Prj_Run_Errors = "activate_venv"
            self.log(f"activate_venv() Decoded Errors// {stderr.decode()} // ", "Scrips Errors (Currently activate_venv dose not cast Prj_Run_Errors)")
        process.wait()

    def addPipPackage(self, packageName:str) -> None:
        self.pipPackages.append(packageName)

    def installAllPipPackage(self) -> None:
        for packageName in self.pipPackages:
            pipfuncs.check_and_install_package(packageName)

    def stop_execution(self):
        sys.exit()
    
    def __del__(self):
        self.log("__del__()", f"Finished Execution with code:{self.Prj_Exec_error}, {self.Prj_Run_Errors}")
        if not self.Prj_Exec_error == 0:
            sys.exit(1)
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # self.log("__exit__()", f"Project ExitLog: {exc_type}, {exc_value}, {traceback}")
        if not exc_value == 0 and not exc_value == None:
            self.Prj_Exec_error = 1
            self.Prj_Run_Errors = "__exit__"
        with open(self.jsonStorePos, "w") as json_file:
                json.dump(self.Variables, json_file)

    def check_venv(self, venv_name) -> bool:
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            # Inside a virtual environment
            if os.path.basename(sys.prefix) != venv_name:
                self.log("check_venv()", f"Error: This Script Should be run Within a virtual Environment Named '{venv_name}'.")
                return False
        else:
            self.log("check_venv()", "This script Should be run Within a Virtual Environment. Creationg an Venv and Switching to it")
            return False
        return True

    def addStage(self ,stageInstance) -> None:
        self.Stages.append(stageInstance)
        stageInstance.parentOutputFoulder = self.buildArtefactsPath

    def execStage(self, Stage) -> None:
        fileName = f"{Stage.StageName}.txt"
        filePos = os.path.join(self.buildArtefactsPath, fileName)
        print()
        print("-"*80)
        print("Running Stage: ", Stage.StageName)
        print("Output file path: ", filePos)
        print()
        with open(filePos, "w") as file:
            output = Stage.execStage()
            file.write('\n'.join(output))
            
            pprint(output)
        print("-"*80)

    def execAllStages(self) -> None:
        for index, stage in enumerate(self.Stages):
            self.execStage(stage)

    def execSingleStage(self, stage_Identifier) ->None:
        index = None
        self.log("execSingleStage()", stage_Identifier)
        try: 
            index = self.Stages[self.Stages.index(stage_Identifier)]
        except ValueError:
            for instance in self.Stages:
                if instance.StageName == stage_Identifier:
                    index = instance
        if index:
            self.execStage(index)

    def setup(self):
        if (self.check_venv(self.ProjectName+"_BuildVenv") != True):
            if os.path.exists(self.baseOutputFoulderPath):
                shutil.rmtree(self.baseOutputFoulderPath)
                print("Deleted Root foulder")
            os.mkdir(self.baseOutputFoulderPath)
            os.mkdir(self.buildArtefactsPath)

            self.create_venv(self.venvPath)
            callerArgs = " ".join(sys.argv[1:])
            self.activate_venv(self.venvPath, f"{self.rootExecuterScript} {callerArgs}")
            self.stop_execution()
        print("running")
        self.installAllPipPackage()

    def makeClassCliAvailable(self):
        if len(sys.argv) > 1:
            function_name = sys.argv[1]
            if hasattr(self, function_name) and callable(getattr(self, function_name)):
                params = sys.argv[2:]
                getattr(self, function_name)(*params)
            else:
                print("Function not found or not callable!")




class Stage: 
    def __init__(self, StageName:str) -> None:
        self.funcs = []
        self.artifacts = []
        self.StageName = StageName
        self.parentOutputFoulder = "" 

    def addFunc(self, funcInstance) -> None:
        self.funcs.append(funcInstance)

    def addFuncs(self, *args) -> None:
        for lambda_func in args:
            self.funcs.append(lambda_func)

    def addArtefactFoulder(self, fouderPath) -> None:
        self.artifacts.append(fouderPath)

    def execStage(self):
        with Capturing() as output:
            # exec stage funcs
            for func in self.funcs:
                func()
            # exec stage artefacts 
            for artefactPath in self.artifacts:
                artefactBaseFoulder = os.path.join(self.parentOutputFoulder, (self.StageName + "_Artefact"))

                if not os.path.exists(artefactBaseFoulder):
                    os.makedirs(artefactBaseFoulder)
                artefactDestinationPath = os.path.join(artefactBaseFoulder, os.path.basename(artefactPath))

                if os.path.isfile(artefactPath):
                    try:
                        shutil.copy(os.path.abspath(artefactPath), os.path.abspath(artefactDestinationPath))
                    except shutil.Error:
                        print("No artefacts to Copy")
                else:
                    try:
                        shutil.copytree(os.path.abspath(artefactPath), os.path.join(self.parentOutputFoulder, (self.StageName + "_Artefact")))
                    except shutil.Error:
                        print("No artefacts to Copy")


        return output
