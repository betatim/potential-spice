# Import needed files ############################
from Gaudi.Configuration import * 
from Configurables import DaVinci, TupleToolTagging, DecayTreeTuple

from Configurables import DecayTreeTuple, LoKi__Hybrid__TupleTool
from Configurables import TupleToolTrigger, TupleToolTISTOS, TupleToolDecay
from Configurables import TupleToolGeometry, TupleToolMCTruth

#from Configurables import ConfigTarFileAccessSvc
#ConfigTarFileAccessSvc().File='/afs/cern.ch/work/s/sbenson/public/forTeslaExtendedReps/config.tar'

tuple = DecayTreeTuple("TeslaTuple")
tuple.Inputs = ["/Event/Tesla/Particles"]
tuple.ToolList +=  ["TupleToolGeometry"
                    , "TupleToolKinematic"
                    , "TupleToolTISTOS"
                    , "TupleToolTrackInfo"
                    , "TupleToolTrigger"
                    , "TupleToolPid"
                    #, "TupleToolMCTruth"
                    #, "TupleToolMCBackgroundInfo"
                    ]

#tuple.OutputLevel = VERBOSE
# Trigger Lines interested in
tlist = ["L0HadronDecision", "L0MuonDecision", "L0DiMuonDecision", "L0ElectronDecision",
         "L0PhotonDecision",
         "Hlt1DiMuonHighMassDecision", "Hlt1DiMuonLowMassDecision",
         "Hlt1TrackMuonDecision", "Hlt1TrackAllL0Decision",
         "Hlt2DiMuonJPsiDecision", "Hlt2SingleMuonDecision",
         ]


tuple.Decay = "J/psi(1S) -> mu- mu+"
tuple.addTool(TupleToolTrigger, name="TupleToolTrigger")
tuple.addTool(TupleToolTISTOS, name="TupleToolTISTOS")
# Get trigger info
tuple.TupleToolTrigger.Verbose = True
tuple.TupleToolTrigger.TriggerList = tlist
tuple.TupleToolTISTOS.Verbose = True
tuple.TupleToolTISTOS.TriggerList = tlist

#from TeslaTools import TeslaTruthUtils
#seq = TeslaTruthUtils.associateSequence("Tesla",False)
#relations = TeslaTruthUtils.getRelLoc("Tesla")
#TeslaTruthUtils.makeTruth(tuple, relations, [ "MCTupleToolKinematic" , "MCTupleToolHierarchy" , "MCTupleToolPID" ])

# Necessary DaVinci parameters #################
DaVinci().Simulation = True
DaVinci().SkipEvents = 0
DaVinci().EvtMax = -1
DaVinci().Lumi = False
DaVinci().TupleFile = 'TutorialTuple.root'
DaVinci().HistogramFile = "dummy.root"
DaVinci().PrintFreq = 10
DaVinci().DataType      = '2012'
DaVinci().UserAlgorithms = [tuple] 
DaVinci().InputType = 'DST'

from GaudiConf import IOHelper
IOHelper().inputFiles(['EarlyEvents-Extended-L0-Turbo2.xdst'])
