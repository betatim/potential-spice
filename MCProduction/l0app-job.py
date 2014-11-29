# SetupProject Moore v23r2
import sys
from Moore.Configuration import *
from Configurables import L0App
from Configurables import LHCbApp
from GaudiConf import IOHelper


def execute():
    option_files = "$APPCONFIGOPTS/L0App/L0AppSimProduction.py;$APPCONFIGOPTS/L0App/L0AppTCK-0x0033.py;$APPCONFIGOPTS/L0App/DataType-2012.py"
    option_files = option_files.split(";")
    for option in option_files:
        importOptions(option)

    LHCbApp().Simulation = True
    LHCbApp().DDDBtag = "dddb-20140729"
    LHCbApp().CondDBtag = "sim-20140730-vc-mu100"

    #inputFiles = ["EarlyEvents-Extended.digi"]
    #IOHelper('ROOT').inputFiles(inputFiles)
    L0App.outputFile = "EarlyEvents-Extended-L0.xdst"

#execute()
