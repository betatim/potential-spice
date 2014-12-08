# SetupProject Moore v23r2
import sys
from Moore.Configuration import *
from Configurables import Moore, HltConf
from Configurables import LHCbApp
from GaudiConf import IOHelper
from Configurables import HltConfigSvc
from Configurables import ConfigTarFileAccessSvc
    

def execute(polarity):
    option_files = "$APPCONFIGOPTS/Moore/MooreSimProductionForSeparateL0AppStep2015.py;$APPCONFIGOPTS/Conditions/TCK-0x40b10033.py;$APPCONFIGOPTS/Moore/DataType-2012.py"
    option_files = option_files.split(";")
    for option in option_files:
        importOptions(option)

    LHCbApp().Simulation = True
    LHCbApp().DDDBtag = "dddb-20140729"
    LHCbApp().CondDBtag = "sim-20140730-vc-m%s100"%polarity

    #inputFiles = ["/tmp/thead/EarlyEvents-Extended-L0.xdst"]
    #IOHelper('ROOT').inputFiles(inputFiles)
    #Moore().EvtMax = 20

    Moore().outputFile = "EarlyEvents-Extended-L0-TurboMoore.xdst"

    # path to private TCK
    ConfigTarFileAccessSvc().File = 'config.tar'
    Moore().TCKData = '.'

    Moore().InitialTCK = "0x40b20033" # your chosen TCK
    Moore().UseTCK = True

#execute()
