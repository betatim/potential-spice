# SetupProject brunel v47r1
from Brunel.Configuration import *
from Configurables import Brunel, LHCbApp
from GaudiConf import IOHelper


def execute():
    option_files = "$APPCONFIGOPTS/Brunel/DataType-2015.py;$APPCONFIGOPTS/Brunel/MC-WithTruth.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
    option_files = option_files.split(";")
    for option in option_files:
        importOptions(option)

    importOptions("$APPCONFIGOPTS/Brunel/xdst.py")
    
    LHCbApp().Simulation = True
    LHCbApp().DDDBtag = "dddb-20140729"
    LHCbApp().CondDBtag = "sim-20140730-vc-mu100"

    Brunel().DatasetName = "EarlyEvents-Extended-L0-Turbo-Moore-Brunel"
    HistogramPersistencySvc().OutputFile = 'EarlyEvents-BrunelHistos.root'

#input_files = ["EarlyEvents-Extended.digi"]
#IOHelper('ROOT').inputFiles(input_files)
#execute()
