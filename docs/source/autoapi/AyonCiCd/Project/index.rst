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

   Capture stdout and stderr output.

   Capture the output as a variable for further use.

   .. attribute:: stdout

      fake stdout to capture + store output

   .. attribute:: stderr

      fake stderr to capture + store output

   .. attribute:: original_stdout

      variable to store the original stdout to reusing
      it at ``__exit__``

   .. attribute:: original_stderr

      variable to store the original stderr to reusing
      it at ``__exit__``

   .. py:method:: get_output() -> str

      Retrieve the data captured by this class.

      This will combine stdout and stderr into one string separated by an escape char.

      :returns: stdout + stderr separated by new line.
      :rtype: str


   .. py:method:: write(text: str)

      Imitating stdout and capturing the data from it.

      :param text: input text to be written to stdout
      :type text: str


   .. py:method:: isatty(self)
      :staticmethod:

      Imitating color support info's.

      Currently, this function just returns False and does not actually test.

      :returns: False
      :rtype: bool



.. py:class:: Project(project_name: str)

   Class to describe a project for execution usage.

   .. attribute:: project_name

      Name used to identify and to make CLI
      availability easier.

   .. attribute:: base_output_folder_path

      auto generated path that describing the base
      folder for venv and stage_artefact_list.

   .. attribute:: _root_exec_script

      auto generated variable holding the root of the
      execution graph (deprecated)

   .. attribute:: var_json_file_path

      path describing the location for the json file used to keep track off _project_internal_varialbes cross execution

   .. attribute:: _project_internal_varialbes

      a ditc off variables set and made available to every function

   .. attribute:: _build_artefacts_out_path

      the base path where the build stage_artefact_list will be stored

   .. attribute:: _project_stage_list

      a list off all stages available to the project. (mainly used by executAllStages)

   .. attribute:: _project_stage_groups_list

      list off stage groups (used for runStageGRP)

   .. attribute:: _runtime_python_version_major_minor_str

      variable holding a string representation off the major.minor number describing the python version. (useful for folder actions inside off the venv)

   .. attribute:: _build_venv_abs_path

      path to the base folder off the build venv

   .. attribute:: _project_requested_pip_packes

      list off pip packages to be installed by setup()

   .. attribute:: _project_runtime_errors

      dict off errors cased by functions while running. useful for debugging

   .. attribute:: _project_execuition_error_int

      int used for sys.exit() in order to flag a run as failed.

   .. py:method:: setup()

      setup function used to generate the venv and to install all needed packages
      this should be called in a separate process before running any tests


   .. py:method:: make_project_cli_available()

      function used in a with block to make the current class instance availalbe to the cli. (python script.py -arg -arg)
      this allows usage from cli and access to all functions in this class


   .. py:method:: stop_execution()

      helper function that just calls sys.exit(). Exists in order to convey intend


   .. py:method:: log(TopInfo: str, *args)

      simple logging function that allows to print formatted log outputs to keep output readable and consistent

      :param TopInfo: str name or text to be printed at the top off the log (commonly used to show the function that prints the log)
      :param \*args: str list off things to be printed. (will be printed via pprint())


   .. py:method:: setVar(VarName, VarValue)

      function for setting a variable in the project local _project_internal_varialbes store. all functions set with this function will be stored in the variables.json.
      this function also allows for overwriting off _project_internal_varialbes
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



   .. py:method:: add_stage(stageInstance) -> None

      function to add stage to the project.
      will append stage instance to _project_stage_list via append() this allows you to append a stage multiple times. But doing so is consider UB and is thereby not advised.

      :param stageInstance:


   .. py:method:: execAllStages() -> None

      function to execute all stages in order off _project_stage_list
      will internally call _call_stage_execution() in a loop


   .. py:method:: execSingleStage(stage_Identifier) -> None

      function to execute a single stage by identifier
      will internally call _call_stage_execution()

      :param stage_Identifier: stageInstance


   .. py:method:: runStageGRP(stageGRPName: str) -> None


   .. py:method:: creat_stage_group(GrpName, *stageInstances) -> None


   .. py:method:: add_pip_package(packageName: str) -> None

      appends a package name to _project_requested_pip_packes list so that _install_pip_packages_in_venv can consume them

      :param packageName:


   .. py:method:: check_venv() -> bool

      Checks if the current script is running in a Venv

      :param venv_name ():

      :returns: True if in Venv. False if not in Venv
      :rtype: Bool



.. py:class:: Stage(StageName: str)

   class used to describe a group off functions and artifact's

   .. attribute:: stage_function_list

      a list off functions to be executed

   .. attribute:: stage_artefact_list

      a list off artifacts to be copied

   .. attribute:: StageName

      str identifier for the current stage

   .. attribute:: parentOutputFoulder

      a path set from the parent project

   .. py:method:: add_single_func(funcInstance) -> None

      append a lambda to the stage function list.

      :param funcInstance:


   .. py:method:: add_funcs(*args) -> None

      append a list off lambdas to the stages function list. They will be added via a for loop
      *args:


   .. py:method:: addArtefactFoulder(fouderPath) -> None

      adds an artifact to the stages stage_artefact_list list. this function also allows adding files as artifact's and is not yet renamed

      :param fouderPath ():


   .. py:method:: copy_artefact(artefactPath) -> None

      function to copy an artifact to its appropriate place

      :param artefactPath ():


   .. py:method:: exec_stage()

      this function will be called by every system that intends executing the stage
      this function will capture output that's running in it and will return it

      Returns: stdout and stderr captured while running stage




