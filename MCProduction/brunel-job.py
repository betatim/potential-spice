# SetupProject brunel v46r1
from Brunel.Configuration import *
from Configurables import Brunel, LHCbApp
from GaudiConf import IOHelper


def execute():
    option_files = "$APPCONFIGOPTS/Brunel/DataType-2012.py;$APPCONFIGOPTS/Brunel/MC-WithTruth.py;$APPCONFIGOPTS/Brunel/patchUpgrade1.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
    option_files = option_files.split(";")
    for option in option_files:
        importOptions(option)

    importOptions("$APPCONFIGOPTS/Brunel/xdst.py")
    
    LHCbApp().Simulation = True
    LHCbApp().DDDBtag = "dddb-20130929-1"
    LHCbApp().CondDBtag = "sim-20131023-vc-md100"

    Brunel().DatasetName = "EarlyEvents"
    HistogramPersistencySvc().OutputFile = 'EarlyEvents-BrunelHistos.root'

#input_files = ["EarlyEvents-Extended.digi"]
#IOHelper('ROOT').inputFiles(input_files)
#execute()
