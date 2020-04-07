#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import traceback
from xml.dom.minidom import Document

LIB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not LIB_PATH in sys.path:
    sys.path.append(LIB_PATH)


class Procjet():
    def gen_plan_file(self, workDir, PLAN=None, TAT_Path=None, script_type="stability"):
        doc = Document()
        Config = doc.createElement('Project')
        doc.appendChild(Config)

        Plan = doc.createElement('Project_Name')
        Config.appendChild(Plan)
        plan = doc.createTextNode(PLAN)
        Plan.appendChild(plan)

        Circle = doc.createElement('Type')
        Config.appendChild(Circle)
        if script_type in ["mpChecklist", "smoke"]:
            circle = doc.createTextNode("Power Consumption")
            Circle.appendChild(circle)
        else:
            circle = doc.createTextNode("STABILITY UIAUTOMATOR")
            Circle.appendChild(circle)

        Plans = doc.createElement('Plans')
        Config.appendChild(Plans)

        Cases = doc.createElement('Cases')
        Config.appendChild(Cases)
        # scripts's path
        StabilityScript = os.path.join(workDir, script_type)
        print "Scripts Path:", StabilityScript
        FileNames = os.listdir(StabilityScript)
        for fileName in FileNames:
            if fileName[0].isdigit():  # only start with digit can be join to test plan
                if fileName == "00_preset_smoke.py":
                    continue
                fullfilename = os.path.join(StabilityScript, fileName)
                print "set scripts path:", fullfilename

                Case_File = doc.createElement('Case_File')
                Cases.appendChild(Case_File)

                fileName = doc.createTextNode(fullfilename)
                Case_File.appendChild(fileName)

        testPlanFilePath = os.path.join(TAT_Path, "Plan")
        print "testPlanFilePath--------->1:", testPlanFilePath
        if not os.path.exists(testPlanFilePath):
            print "create file:", testPlanFilePath
            os.makedirs(testPlanFilePath)
        with open(os.path.join(testPlanFilePath, PLAN + ".xml"), "w") as f:
            # f.write(doc.toprettyxml(indent=''))
            doc.writexml(f, encoding='utf-8')
        print "Create " + PLAN + " successfully!"

        # testPlanFilePath = os.path.join(TAT_Path, "Plan")
        # testPlanFilePath = os.path.join(testPlanFilePath, PLAN + ".xml")
        # print "testPlanFilePath--->:",testPlanFilePath
        # if not os.path.exists(testPlanFilePath):
        #     print "create file:",testPlanFilePath
        #     os.makedirs(testPlanFilePath)
        # with open(testPlanFilePath, "w") as f:
        #     f.write(doc.toprettyxml(indent=''))
        # print "Create " + PLAN + " successfully!"

    def gen_main_config_file(self, serialNumber, planName, TAT_Path, MDEVICE=None, SDEVICE=None, run_circle=20):
        doc = Document()
        Config = doc.createElement('Configs')
        doc.appendChild(Config)

        Plan = doc.createElement('Plan')
        Config.appendChild(Plan)
        PlanPath = os.path.join(TAT_Path, "Plan")
        TestPlanPath = os.path.join(PlanPath, planName + ".xml")

        print "set TestPlanPath:", TestPlanPath

        plan = doc.createTextNode(TestPlanPath)
        Plan.appendChild(plan)

        Circle = doc.createElement('RunCircle')
        Config.appendChild(Circle)
        circle = doc.createTextNode(str(run_circle))
        Circle.appendChild(circle)

        if MDEVICE == None:
            MDevice = doc.createElement('M-Device')
            Config.appendChild(MDevice)
        else:
            MDevice = doc.createElement('M-Device')
            Config.appendChild(MDevice)
            device = doc.createTextNode(MDEVICE)
            MDevice.appendChild(device)

        if SDEVICE == None:
            SDevice = doc.createElement('S-Device')
            Config.appendChild(SDevice)
        else:
            SDevice = doc.createElement('S-Device')
            Config.appendChild(SDevice)
            device = doc.createTextNode(SDEVICE)
            SDevice.appendChild(device)

        IsFailBreak = doc.createElement('IsCatchLog')
        Config.appendChild(IsFailBreak)
        isFailBreak = doc.createTextNode("True")
        IsFailBreak.appendChild(isFailBreak)

        IsFailBreak = doc.createElement('IsFailBreak')
        Config.appendChild(IsFailBreak)
        isFailBreak = doc.createTextNode("False")
        IsFailBreak.appendChild(isFailBreak)

        IsFailBreak = doc.createElement('IsAutoReport')
        Config.appendChild(IsFailBreak)
        isFailBreak = doc.createTextNode("False")
        IsFailBreak.appendChild(isFailBreak)

        mainConfigFile = os.path.join(TAT_Path, "Server\MainConfig")
        if not os.path.exists(mainConfigFile):
            os.makedirs(mainConfigFile)

        mainConfigFileName = serialNumber + "# MainConfig.xml"

        with open(os.path.join(mainConfigFile, mainConfigFileName), "w") as f:
            # f.write(doc.toprettyxml(indent=''))
            doc.writexml(f, encoding='utf-8')
        print "Create  %s successfully!" % mainConfigFileName


if __name__ == '__main__':
    serialNumber = sys.argv[1]
    Script_dir = sys.argv[2]
    TAT_Path = sys.argv[3]
    MDevice = sys.argv[4]
    try:
        SDevice = None if sys.argv[5] == "na" else sys.argv[5]
    except:
        SDevice = None
    script_type = sys.argv[6]

    parentDir = os.path.dirname(os.getcwd())
    print "parentDir:", parentDir
    workDir = os.path.join(parentDir, Script_dir)

    print "MDevice:", MDevice
    # list = sw_download_path.split("-")
    # if list:
    print "SDevice:", SDevice
    print "TAT_Path:", TAT_Path
    print "workDir:", workDir

    planName = MDevice

    try:
        pro = Procjet()
        pro.gen_plan_file(workDir, planName, TAT_Path, script_type)
        run_circle = 1 if script_type == "mpChecklist" or script_type == "smoke" else 20
        pro.gen_main_config_file(serialNumber, planName, TAT_Path, MDevice, SDevice, run_circle)
    except:
        print traceback.format_exc()
