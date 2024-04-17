:py:mod:`AyonCiCd.Project`
==========================

.. py:module:: AyonCiCd.Project


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   AyonCiCd.Project.Capturing
   AyonCiCd.Project.Project
   AyonCiCd.Project.Stage




.. py:class:: Capturing

   a class build to capture stdout and stderr output.
   target off this class is make the output available as a variable for further use

   .. attribute:: stdout

      fake stdout to capture + store output

   .. attribute:: stderr

      fake stderr to capture + store output

   .. attribute:: original_stdout

      variable to store the original stdout to reusing it at __exit__

   .. attribute:: original_stderr

      variable to store the original stderr to reusing it at __exit__

   .. py:method:: get_output() -> str

      function to retrieve the data captured by this class.
      this will combine stdout and stderr into one string separated by an escape char.

      Returns:



   .. py:method:: write(text)

      function for imitating stdout and capturing the data from it

      :param text: input text to we written to stdout


   .. py:method:: isatty()

      function for imitating color support info's.
      currently this function just returns False and dose not actually test

      Returns:




.. py:class:: Project(projectName: str)

   class to describe a project for execution usage

   .. attribute:: ProjectName

      Name attribute used to identify and to make cli availability easier

   .. attribute:: baseOutputFoulderPath

      auto generated path that describing the base folder for Venv and Artifacts

   .. attribute:: rootExecuterScript

      auto generated variable holding the root off the execution graph (Discontinued)

   .. attribute:: VariablesJsonFilePath

      path describing the location for the json file used to keep track off variables cross execution

   .. attribute:: Variables

      a ditc off variables set and made available to every function

   .. attribute:: buildArtefactsPath

      the base path where the build artifacts will be stored

   .. attribute:: RegisteredStageList

      a list off all stages available to the project. (mainly used by executAllStages)

   .. attribute:: StageGrps

      list off stage groups (used for runStageGRP)

   .. attribute:: python_version

      variable holding a string representation off the major.minor number describing the python version. (useful for folder actions inside off the venv)

   .. attribute:: venvPath

      path to the base folder off the build venv

   .. attribute:: pipPackages

      list off pip packages to be installed by setup()

   .. attribute:: Prj_Run_Errors

      dict off errors cased by functions while running. useful for debugging

   .. attribute:: Prj_Exec_error

      int used for sys.exit() in order to flag a run as failed.

   .. py:method:: setup()

      setup function used to generate the venv and to install all needed packages
      this should be called in a separate process before running any tests


   .. py:method:: add_venv_path_to_path()

      function for adding the side packages installed under the venv to the current python accessible path.
      this allows access to the packages without having to activate the venv


   .. py:method:: makeClassCliAvailable()

      function used in a with block to make the current class instance availalbe to the cli. (python script.py -arg -arg)
      this allows usage from cli and access to all functions in this class


   .. py:method:: stop_execution()

      helper function that just calls sys.exit(). Exists in order to convey intend


   .. py:method:: log(TopInfo: str, *args)

      simple logging function that allows to print formatted log outputs to keep output readable and consistent

      :param TopInfo: str name or text to be printed at the top off the log (commonly used to show the function that prints the log)
      :param \*args: str list off things to be printed. (will be printed via pprint())


   .. py:method:: loadJson()

      function used to load the variable.json into the project local variable store. This allows for variables to be set by one execution run and consumed by another.


   .. py:method:: setVar(VarName, VarValue)

      function for setting a variable in the project local variables store. all functions set with this function will be stored in the variables.json.
      this function also allows for overwriting off variables
      in the end the variable store is a dict and so you will need a key(Name) and a value(Value) pair for setting a variable
      :param VarName:
      :param VarValue:


   .. py:method:: displayVar(VarName: str)

      function to display what value a variable has at the current time.

      :param VarName: str


   .. py:method:: getVar(VarName: str)

      function to retrieve the value of a variable

      :param VarName: str

      Returns: value off a given varialbe or None if the key is not found via .get()



   .. py:method:: addStage(stageInstance) -> None

      function to add stage to the project.
      will append stage instance to RegisteredStageList via append() this allows you to append a stage multiple times. But doing so is consider UB and is thereby not advised.

      :param stageInstance:


   .. py:method:: execStage(Stage) -> None

      function for executing a stage and formatting the output.

      :param Stage: stageInstance


   .. py:method:: execAllStages() -> None

      function to execute all stages in order off RegisteredStageList
      will internally call execStage() in a loop


   .. py:method:: execSingleStage(stage_Identifier) -> None

      function to execute a single stage by identifier
      will internally call execStage()

      :param stage_Identifier: stageInstance


   .. py:method:: CreateStageGRP(GrpName, *stageInstances) -> None


   .. py:method:: runStageGRP(stageGRPName: str) -> None


   .. py:method:: create_venv(venv_path)

      helper function for creating a python venv
      will install pip, upgrade deps, clear venv if Existent

      :param venv_path:


   .. py:method:: get_venv_activate_cmd(venv_path)

      helper function to get the correct venv activate script for win or Linux

      :param venv_path:

      Returns:



   .. py:method:: install_pip_packes_in_venv(venv_path: str, pip_package_list: list)

      helper function that will activate the venv, upgrade pip and install the package list. this will be executed in a subprocess

      :param venv_path:
      :param pip_package_list:


   .. py:method:: addPipPackage(packageName: str) -> None

      appends a package name to pipPackages list so that install_pip_packes_in_venv can consume them

      :param packageName:


   .. py:method:: check_venv() -> bool

      Checks if the current script is running in a Venv

      :param venv_name ():

      :returns: True if in Venv. False if not in Venv
      :rtype: Bool



.. py:class:: Stage(StageName: str)

   class used to describe a group off functions and artifact's

   .. attribute:: funcs

      a list off functions to be executed

   .. attribute:: artifacts

      a list off artifacts to be copied

   .. attribute:: StageName

      str identifier for the current stage

   .. attribute:: parentOutputFoulder

      a path set from the parent project

   .. py:method:: addFunc(funcInstance) -> None

      append a lambda to the stage function list.

      :param funcInstance:


   .. py:method:: addFuncs(*args) -> None

      append a list off lambdas to the stages function list. They will be added via a for loop
      *args:


   .. py:method:: addArtefactFoulder(fouderPath) -> None

      adds an artifact to the stages artifacts list. this function also allows adding files as artifact's and is not yet renamed

      :param fouderPath ():


   .. py:method:: copy_artefact(artefactPath) -> None

      function to copy an artifact to its appropriate place

      :param artefactPath ():


   .. py:method:: execStage()

      this function will be called by every system that intends executing the stage
      this function will capture output that's running in it and will return it

      Returns: stdout and stderr captured while running stage




