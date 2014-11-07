# SetupProject Moore v22r1p1
import sys
from Moore.Configuration import *
from Configurables import Moore, HltConf
from Configurables import LHCbApp
from GaudiConf import IOHelper


def execute():
    option_files = "$APPCONFIGOPTS/Moore/MooreSimProductionForSeparateL0AppStep2015.py;$APPCONFIGOPTS/Conditions/TCK-0x40b10033.py;$APPCONFIGOPTS/Moore/DataType-2012.py"
    option_files = option_files.split(";")
    for option in option_files:
        importOptions(option)

    LHCbApp().Simulation = True
    LHCbApp().DDDBtag = "dddb-20140729"
    LHCbApp().CondDBtag = "sim-20140730-vc-mu100"

    #inputFiles = ["/tmp/thead/early/EarlyEvents-Extended-L0.xdst"]
    #IOHelper('ROOT').inputFiles(inputFiles)
    Moore().outputFile = "EarlyEvents-Extended-L0-TurboMoore.xdst"
    
    #HltConf().ThresholdSettings = "Physics_draftEM2015"
    #Moore().UseTCK = False
    #Moore().generateConfig = True

#execute()
