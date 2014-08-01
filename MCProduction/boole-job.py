# SetupProject Boole v28r2p1
import sys
from Boole.Configuration import *
from Configurables import Boole, LHCbApp
from GaudiConf import IOHelper


def execute():
    option_files = "$APPCONFIGOPTS/Boole/Default.py;$APPCONFIGOPTS/Boole/EnableSpillover.py;$APPCONFIGOPTS/Boole/DataType-2012.py;$APPCONFIGOPTS/Boole/Boole-SiG4EnergyDeposit.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
    option_files = option_files.split(";")
    for option in option_files:
        importOptions(option)

    importOptions("$APPCONFIGOPTS/Boole/xdigi.py")

    LHCbApp().Simulation = True
    LHCbApp().DDDBtag = "dddb-20130929-1"
    LHCbApp().CondDBtag = "sim-20131023-vc-md100"

    Boole().DatasetName = "EarlyEvents"
    HistogramPersistencySvc().OutputFile = "EarlyEvents-BooleHistos.root"
    FileCatalog().Catalogs = [ "xmlcatalog_file:EarlyEvents-BooleCatalog.xml"]

#inputFiles = ["EarlyEvents-24142001.sim"]
#IOHelper('ROOT').inputFiles(inputFiles)
#execute()
