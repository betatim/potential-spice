# SetupProject Gauss v47r0
from Configurables import Gauss, LHCbApp
from Gauss.Configuration import *


def execute(event_type):
    option_files = "$APPCONFIGOPTS/Gauss/Beam6500GeV-mu100-nu1.6.py;$APPCONFIGOPTS/Gauss/DataType-2015.py;$APPCONFIGOPTS/Gauss/RICHRandomHits.py;$DECFILESROOT/options/@{eventType}.py;$LBPYTHIAROOT/options/Pythia.py;$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
    option_files = option_files.replace("@{eventType}", str(event_type))
    option_files = option_files.split(";")
    for option in option_files:
        print option
        importOptions(option)

    LHCbApp().Simulation = True
    LHCbApp().DDDBtag = "dddb-20140729"
    LHCbApp().CondDBtag = "sim-20140730-vc-mu100"
    LHCbApp().EvtMax = 3
    
    GaussGen = GenInit("GaussGen")
    #GaussGen.FirstEventNumber = 1
    GaussGen.RunNumber = 383589
    
    #HistogramPersistencySvc().OutputFile = outpath+'-GaussHistos.root'
    OutputStream("GaussTape").Output = "DATAFILE='PFN:EarlyEvents.sim' TYP='POOL_ROOTTREE' OPT='RECREATE'"

#incl_JPsi = 24142001
#incl_Upsilons = 18112004
#execute(incl_Upsilons)
