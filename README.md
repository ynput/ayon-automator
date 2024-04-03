# AyonCiCd-Automator
Automator is a toolset built to allow the definition and usage of testing Setups / Stages  
The target is to enable a developer to set up his testing setup and use it locally and via GitHub or any other runner system without defining any extra calls. 

## Creat a Project.py
### Define a Project
```
Project = Project.Project("Project")
Project.addPipPackage("pytest")
```
### Define a stage
```
Stage = Project.Stage("StageName")
Stage.addFuncs(
    lambda: someFunc(),
)
BuildStage.addArtefactFoulder("/path/to/artefacts/foulder")
Project.addStage(Stage)
```

### Make your project availalbe to the Cli
```
AyonCppApiPrj.makeClassCliAvailable()
```


## How to use your project

The Setup command will Create your project with an Venv and install all the packages you added Via addPipPackage. 

``python AyonBuild.py setup``

The execSingleStage command allows you to execute a single stage from your project.
This can be useful for GitHub workflows as you can execute stages in different job portions and see what stage failed at first glance. 

``python AyonBuild.py execSingleStage StageName`` 

or you can use the execAllStages to run all stages of your project in the order they were added. 

``python AyonBuild.py execAllStages``

