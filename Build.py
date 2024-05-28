from AyonCiCd import cmd
from AyonCiCd.Project import Project, Stage

# define a Project that you want to CiCd
AutomatorMain = Project("AyonAutomator")
# add packages to the project
AutomatorMain.add_pip_package("Sphinx")
AutomatorMain.add_pip_package("furo")

AutomatorMain.add_pip_package("sphinx_theme")
AutomatorMain.add_pip_package("https://github.com/revitron/revitron-sphinx-theme/archive/master.zip")
AutomatorMain.add_pip_package("sphinx-autoapi")
AutomatorMain.add_pip_package("myst-parser")
AutomatorMain.add_pip_package("linkify-it-py")
AutomatorMain.add_pip_package("sphinx-rtd-theme") 


TestStage = Stage("Test")
TestStage.add_funcs()
AutomatorMain.add_stage(TestStage)


DocumentationGenStage = Stage("DocGen")
DocumentationGenStage.add_funcs( lambda: cmd.run("cd docs && make html", shell=True)
)
DocumentationGenStage.addArtefactFoulder("docs/build/html")
AutomatorMain.add_stage(DocumentationGenStage)


AutomatorMain.creat_stage_group("TestAndDocument", TestStage, DocumentationGenStage)

with AutomatorMain as PRJ:
    PRJ.make_project_cli_available() 
