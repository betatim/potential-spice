from Configurables import Tesla 
from Gaudi.Configuration import *

from Configurables import RecombineRawEvent, DecodeRawEvent


def execute():
    RecombineRawEvent()
    DecodeRawEvent().DataOnDemand = True

    from Configurables import ConfigTarFileAccessSvc
    ConfigTarFileAccessSvc().File = "config.tar"

    #Tesla().OutputLevel = DEBUG
    Tesla().TriggerLine = "Hlt2DiMuonJPsi"
    Tesla().ReportVersion = 2
    #Tesla().EvtMax = -1

    #from GaudiConf.IOHelper import IOHelper
    #ioh = IOHelper()
    #ioh.setupServices()
    #ioh.inputFiles(["EarlyEvents-Extended-L0-Turbo.xdst"])
    Tesla().outputFile = "EarlyEvents-Extended-L0-Turbo.xdst"

    #from Configurables import TeslaReportAlgo
    #TeslaReportAlgo().OutputLevel = 1
