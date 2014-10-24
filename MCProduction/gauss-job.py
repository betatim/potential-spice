# SetupProject Gauss v46r7p2
from Configurables import Gauss, LHCbApp
from Gauss.Configuration import *


def execute(event_type):
    option_files = "$APPCONFIGOPTS/Gauss/Beam6500GeV-md100-nu1.5.py;$APPCONFIGOPTS/Gauss/EnableSpillover-25ns.py;$DECFILESROOT/options/@{eventType}.py;$LBPYTHIA8ROOT/options/Pythia8.py;$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
    option_files = option_files.replace("@{eventType}", str(event_type))
    option_files = option_files.split(";")
    for option in option_files:
        print option
        importOptions(option)

    LHCbApp().Simulation = True
    LHCbApp().DDDBtag = "dddb-20130929-1"
    LHCbApp().CondDBtag = "sim-20131023-vc-md100"
    LHCbApp().EvtMax = 3
    
    GaussGen = GenInit("GaussGen")
    #GaussGen.FirstEventNumber = 1
    GaussGen.RunNumber = 1082
    
    #HistogramPersistencySvc().OutputFile = outpath+'-GaussHistos.root'
    OutputStream("GaussTape").Output = "DATAFILE='PFN:EarlyEvents.sim' TYP='POOL_ROOTTREE' OPT='RECREATE'"

#incl_JPsi = 24142001
#incl_Upsilons = 18112004
#execute(incl_Upsilons)
