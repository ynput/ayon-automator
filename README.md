# AyonCiCd-Automator

Automator is a toolkit for setting up build and test Stages to ease your
Development Workflow

## Base Concepts

An Automator Project has 2 Parts to it. The Setup and the Project itself

### Setup

Setup in Automator in made from 2 parts

1. in your project you can define packages that you want installed and a folder
   structure named like your project will be created where everything is stored
2. setup cmd command. Running the setup command will ultimately create the
   output folder structure and the venv used to provide site packages to your
   main python runner.

### Project

A project in Automator is just a named collection off stages and stage Groups
that you can make available to the Cli.

Projects Are build from the following portions.

1. Project definition
   - Describes project Name and required pip packages
   - Also holds all Variables, Stages and StageGrps
2. Stage Definitions
   - A list off functions and Artifact's that will be executed when stage
     execute is called
3. Stage Exec Groups (optional)
   - an optional system that allows you to group stages to run them together,
     this might be useful for tests where you might need a test build and a test
     stage.

### Cli Availability

This portion will describe what the Cli Availability exposes to you and why and
when you might want to use it.

- make_project_cli_available is a function run in a with block that allows you
  to start stages and StageGrps from the cli.
- its run within a with statement so that we can use the **exit** function to
  write out everything that happened to the appropriate artifact file. thees
  will later help when debugging because you will have everything that happened
  available to you in your artifacts.

```py
with ProjectName as PRJ:
    PRJ.make_project_cli_available()
```

Example Usage `python AutomatorScript.py runStageGrp StageGrpName`

- The make_project_cli_available function exposes the following functions

| Variable          | Description                                                                                                                                                                                                        |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `setup`           | Setup will setup the Venv and the output foulder it will also install all the pip packages inside off the venv. you will have to run this once before running annything else. the setup is precistent between runs |
| `execSingleStage` | execSingleStage allows you to only run a single stage. this might be of interest if your rerunning tests and you only change the input data and not your code.                                                     |
| `execAllStages`   | execAllStages will run all stages in the order they where added to the project.                                                                                                                                    |
| `setVar`          | setVar allows you to set Variables from within your script or from the cli. they will also be stored in the Variables.json file and thereby be presisent                                                           |
| `runStageGRP`     | runStageGRP allows you to run a single stage Grp this might be usefull if you need to complie your code without testing it.                                                                                        |

- Theoretically the make_project_cli_available will expose all class functions
  but its not advised to use it this way. But if you want to do so. Do it on
  your own Risk

# How to

1. Clone the Repo into a convenient place in your project. (make sure that the
   folder your copying to has no `-` in it as python dose not like them when
   using `import`)

### Define a Project

```py
from AyonCiCdAutomator import Project # import the Project portion off Automator (there are more functions and classes available)
Project = Project.Project("Project") # Define a project with what ever name you want. (this name will dictate the name off your Output foulder)
Project.addPipPackage("pytest") #(optional) define some packages that will be installed in the Venv that the setup function creats, currently pip is used in a very basic way for installing packages so only pip packages will be available (the venv survives reruns so pip will only run once)
```

### Define a stage

```py
Stage = Project.Stage("StageName") # The stage name is the name that execSingleStage will take in order to run your stage from the CLI
Stage.add_funcs(lambda: someFunc(),) # addFuncs allows you to add functions to your stages. they will be run in sequence in the same order as defined here. you can add as many as you want
BuildStage.addArtefactFoulder("/path/to/artefacts/foulder") # adding artifacts allows you to copy things that e.g your build process created to the Automator Project artifacts folder so you can upload everything together. (this function also allows adding files btw)
Project.add_stage(Stage)
```

### Define a stageGRP (Optional)

```py
Project.CreateStageGRP("StageGrpName", StageInstanceA, StageInstanceB)
```

### Make your project available to the Cli

```py
with ProjectName as PRJ:
    PRJ.make_project_cli_available() # make_project_cli_available should be the last thing in your project file as everything after this will not be available to the CLI
```

## How to use your project

The Setup command will Create your project with an Venv and install all the
packages you added Via addPipPackage.

`python AyonBuild.py setup`

The `execSingleStage` or `runStageGRP` commands allow you to run a single stage
or a StageGrp respectively. both off these functions will append the venv
site-packages to your current site packages and thereby make them available to
your current python instance

`python AyonBuild.py execSingleStage StageName`
`python AyonBuild.py runStageGRP StageGRPName`

The `execAllStages` allows you to run all stages defined in your project. this
might be great if you only defined stages that you want to run together, in this
case you could skip creating a StageGrp and run use this function instead.

`python AyonBuild.py execAllStages`



## Generate Documentation 
Documentatoin is build with sphinx and autogenerated from the source code.
`sphinx-build -b html docs/source docs/build/html`
