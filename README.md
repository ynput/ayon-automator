# AyonCiCd-Automator

Automator is a toolkit built to allow the definition and usage of testing Setups
/ Stages\
The target off this toolkit is to allow a developer to setup his/her build and
test setup all in python while not losing the ability to run it where ever they
want.

## Base Concepts

An Automator project consists off the following portions.

1. The Project definition
2. Stage Definitions
3. Stage Exec Groups (optional)
4. Cli Availability

| Variable           | Description                                                                                                                                                                                                                                                                                          |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Project`          | a Project in Automator is nothing more than an organisational setup that allows you to group all your stages. it will also capture output from your stages and order said output in an easy to follow way                                                                                            |
| `Stage`            | stagesare groups off artefacts and functions that will be run together in the order off definition. this allows you to execute only the steps you want when you want them                                                                                                                            |
| `StageExecGRP`     | stage Exec Groups allow an Dev to define Stages that he might want to run together, they are fully optional and they are great if you have testing setups that might need to start multiple things or have specific build requirement's                                                              |
| `Cli Availability` | Automator delivers a function that makes your project availalbe to the CLI so that you can start stages or StageExecGRPGRPs via `python AutomatorScript.py runStageGrp StageGrpName` this makes it easy to work with your newly build workflows and allows easy acess from e.g Github or Gitlab CiCd |

### Cli Availability

This portion will describe what the Cli Availability exposes to you and why and
when you might want to use it.

- makeClassCliAvailable is a function run in a with block. the reason for that
  is that the function automatically captures all Cli output and writes it down
  insid off files in your build artifact's. this allows you to later view them
  and get a deeper look why things might have failed without having to rerun the
  full test setup

```py
with ProjectName as PRJ:
    PRJ.makeClassCliAvailable()
```

- The makeClassCliAvailable function exposes the following functions

| Variable          | Description                                                                                                                                                                                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `setup`           | Setup will setup the Venv and the output foulders for your later stages (this will also be run by execAllStages)                                                                                                                                                          |
| `execSingleStage` | execSingleStage allows you to only run a single stage. this might be of interest if your rerunning tests and you only change the input data and not your code.                                                                                                            |
| `execAllStages`   | execAllStages will run setup and run all stages                                                                                                                                                                                                                           |
| `setVar`          | setVar allows you to set Variables from within your script or from the cli this might be usefull if you want to pass in variables depending on platform, the variables will be stored in a .json file and survive Rerunning the sciprt so no need to sett them evey time. |
| `runStageGRP`     | runStageGRP allows you to run a single stage Grp this might be usefull if you need to complie your code before testing.                                                                                                                                                   |

- Theoretically the makeClassCliAvailable will expose all class functions but
  its not advised to use it this way. but if you want to do so on your own Risk

# How to

1. Clone the repo into a convinient place in your project. (make sure that the
   foulder your copying to has no `-` in it as python dose not like them when
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
Stage.addFuncs(lambda: someFunc(),) # addFuncs allows you to add functions to your stages. they will be run in sequence in the same order as defined here. you can add as many as you want
BuildStage.addArtefactFoulder("/path/to/artefacts/foulder") # adding artifacts allows you to copy things that e.g your build process created to the Automator Project artifacts folder so you can upload everything together. (this function also allows adding files btw)
Project.addStage(Stage)
```

### Make your project available to the Cli

```py
with ProjectName as PRJ:
    PRJ.makeClassCliAvailable() # makeClassCliAvailable should be the last thing in your project file as everything after this will not be available to the CLI
```

## How to use your project

The Setup command will Create your project with an Venv and install all the
packages you added Via addPipPackage.

`python AyonBuild.py setup`

The `execSingleStage` or `runStageGRP` commands allow you to run a single stage
or a single StageGrp respectively. booth off them will jump into the Project
venv and Thereby have all the Packages Available to them. their output will be
printed to the Cli from withing python so it might arrive delayed. the also
capture the Cli output and thereby allow you revisiting what happened later.
(the files are not named with a time stamp and reruns overwrite old files)

`python AyonBuild.py execSingleStage StageName`
`python AyonBuild.py runStageGRP StageGRPName`

The `execAllStages` allows you to run all stages defined in your project. it
will also run setup. this might be great if you only defined stages that you
want to run together, in this case you could skip creating a StageGrp and run
use this function instead.

`python AyonBuild.py execAllStages`

``
