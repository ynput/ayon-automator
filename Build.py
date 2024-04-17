from AyonCiCd import Project , cmd


# define a Project that you want to CiCd
AutomatorMain = Project.Project("AyonAutomator")
# add packages to the project
AutomatorMain.addPipPackage("Sphinx")
AutomatorMain.addPipPackage("furo")
AutomatorMain.addPipPackage("revitron_sphinx_theme")
AutomatorMain.addPipPackage("sphinx-autoapi")
AutomatorMain.addPipPackage("myst-parser")
AutomatorMain.addPipPackage("linkify-it-py")
AutomatorMain.addPipPackage("sphinx-rtd-theme") 


TestStage = Project.Stage("Test")
TestStage.addFuncs()
AutomatorMain.addStage(TestStage)


DocumentationGenStage = Project.Stage("DocGen")
DocumentationGenStage.addFuncs( lambda: cmd.run("cd docs && make html", shell=True)
)
DocumentationGenStage.addArtefactFoulder("docs/build/html")
AutomatorMain.addStage(DocumentationGenStage)


AutomatorMain.CreateStageGRP("TestAndDocument", TestStage, DocumentationGenStage)

with AutomatorMain as PRJ:
    PRJ.makeClassCliAvailable() 
