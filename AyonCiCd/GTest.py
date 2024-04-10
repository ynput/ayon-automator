from . import Project
import subprocess
import os
from xml.etree import ElementTree
from pprint import pprint
import re


def list_test_results(xml_file_path):
    import xml.etree.ElementTree as ElementTree
    

    def CleanStr(str):
        l = []
        for i in str.split():
            i =  "".join([char for char in i if char not in ['\\','\n', '\t', '\r', "'", '"']])
            if len(i) > 0:
                l.append(i)
        l = " ".join(l)
        return l



    TestRun = {}


    tree = ElementTree.parse(xml_file_path)
    root = tree.getroot()
    
    TestRun["RunInfo"] = {}
    TestRun["TestSuites"] = {}
   

    for data in root.iter('testsuites'):
        TestRun["RunInfo"] = {key: val for key, val in data.items()}

    for testsuite in root.iter('testsuite'):

        TestSuite = {}
        TestSuite["Head"] = {}
        TestSuite["TestCases"] = {}

        testsuiteData = {key: val for key, val in testsuite.items()}
        TestSuite["Head"] = testsuiteData
        TestRun["TestSuites"][TestSuite["Head"]["name"]] = TestSuite 

        
        for testCase in testsuite.iter('testcase'):
            TestCase = {}
            testCaseData = {key: val for key, val in testCase.items()}
            TestCase["Head"] = testCaseData
            TestCase["Massages"] = {}

            for massage in next(testCase.iter()):
                Massage = {}
                for massagePart in massage.items():
                    key = massagePart[0]
                    val = massagePart[-1]
                    Massage[CleanStr(key)] = CleanStr(val)


                TestCase["Massages"][CleanStr(massage.tag)] = Massage
            
            TestSuite["TestCases"][TestCase["Head"]["name"]] = TestCase

   
    
    return TestRun


    

        

def GTestRun(GtestPath: str,xmlPath , ParentPrj: Project.Project = None, *args):

    GtestPath = os.path.abspath(GtestPath)
    os.makedirs(os.path.dirname(xmlPath), exist_ok=True)
    xmlCommand = f"--gtest_output=xml:{xmlPath}"
    command = [GtestPath] + [xmlCommand] + list(args)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    RunResult = list_test_results(xmlPath)

    t = RunResult["TestSuites"]
    for Suite in t:
        SuiteHead = t[Suite]["Head"]
        Case0 = next(iter(t[Suite]["TestCases"]))
        errorMassage = t[Suite]["TestCases"][Case0]["Massages"]
        
        if SuiteHead.get("failures",0 ) > "0":
            ParentPrj.Prj_Run_Errors["GTestRun"] = errorMassage
            ParentPrj.Prj_Exec_error = 1

    output = result.stdout
    errors = result.stderr
    print("open_software() output:")
    pprint(output)
    print("open_software() errors:")
    print(errors)

