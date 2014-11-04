# Import needed files ############################
from Gaudi.Configuration import * 
from Configurables import DaVinci, TupleToolTagging, DecayTreeTuple, MCDecayTreeTuple, L0Conf

from Configurables import DecayTreeTuple, LoKi__Hybrid__TupleTool
from Configurables import TupleToolTrigger, TupleToolTISTOS, TupleToolDecay
from Configurables import TupleToolGeometry, TupleToolMCTruth

from Configurables import ConfigTarFileAccessSvc
ConfigTarFileAccessSvc().File='/afs/cern.ch/work/s/sbenson/public/forTeslaExtendedReps/config.tar'

tuple = DecayTreeTuple("TeslaTuple")
tuple.Inputs = [ "/Event/Tesla/Particles" ]
tuple.ToolList +=  [
    "TupleToolGeometry"
    , "TupleToolKinematic"
    , "TupleToolTISTOS"
    , "TupleToolTrackInfo"
    , "TupleToolTrigger"
    , "TupleToolPid"
    , "TupleToolMCTruth"
    , "TupleToolMCBackgroundInfo"
]


#tuple.OutputLevel = VERBOSE
# Trigger Lines interested in
#tlist = ["L0HadronDecision","L0MuonDecision","L0DiMuonDecision","L0ElectronDecision","L0PhotonDecision","Hlt1DiMuonHighMassDecision","Hlt1DiMuonLowMassDecision","Hlt1TrackMuonDecision","Hlt1TrackAllL0Decision","Hlt2DiMuonJPsi","Hlt2IncPhiDecision","Hlt2Topo4BodySimpleDecision","Hlt2Topo3BodySimpleDecision","Hlt2Topo3BodyBBDTDecision","Hlt2Topo2BodySimpleDecision","Hlt2Topo2BodyBBDTDecision","Hlt2Topo4BodyBBDTDecision","Hlt2TopoMu4BodyBBDTDecision","Hlt2IncPhiSidebandsDecision","Hlt2B2HHDecision","Hlt2DiPhiDecision"]
tlist = ["Hlt2DiMuonJPsi"]

tuple.Decay = "J/psi(1S) -> ^mu+ ^mu-"
#tuple.Decay = "[D*(2010)+ -> ^(K*(892)0 -> ^K+ ^pi-) ^pi+]CC"

tuple.addTool(TupleToolTrigger, name="TupleToolTrigger")
tuple.addTool(TupleToolTISTOS, name="TupleToolTISTOS")
# Get trigger info
tuple.TupleToolTrigger.Verbose = True
tuple.TupleToolTrigger.TriggerList = tlist
tuple.TupleToolTISTOS.Verbose = True
tuple.TupleToolTISTOS.TriggerList = tlist

from TeslaTools import TeslaTruthUtils
seq = TeslaTruthUtils.associateSequence("Tesla",False)
relations = TeslaTruthUtils.getRelLoc("Tesla")
TeslaTruthUtils.makeTruth(tuple, relations, [ "MCTupleToolKinematic" , "MCTupleToolHierarchy" , "MCTupleToolPID" ])

tuple2 = MCDecayTreeTuple("MCTeslaTuple")
tuple2.Inputs = ['/Event/Tesla/Particles']
tuple2.Decay = tuple.Decay

from Configurables import DataOnDemandSvc, L0SelReportsMaker, L0DecReportsMaker
DataOnDemandSvc().AlgMap["HltLikeL0/DecReports"] = L0DecReportsMaker()
DataOnDemandSvc().AlgMap["HltLikeL0/SelReports"] = L0SelReportsMaker()
from Configurables import L0Conf
L0Conf().FullL0MuonDecoding = True
L0Conf().EnableL0DecodingOnDemand = True
L0Conf().EnsureKnownTCK=False

tuple3 = DecayTreeTuple("StrippingTuple")
tuple3.Inputs = ['/Event/AllStreams/Phys/FullDSTDiMuonJpsi2MuMuDetachedLine/Particles']
tuple3.Decay = tuple.Decay
tuple3.ToolList = tuple.ToolList
tuple3.addTool(TupleToolTrigger, name="TupleToolTrigger")
tuple3.addTool(TupleToolTISTOS, name="TupleToolTISTOS")
tuple3.TupleToolTrigger.Verbose = True
tuple3.TupleToolTrigger.TriggerList = tlist
tuple3.TupleToolTISTOS.Verbose = True
tuple3.TupleToolTISTOS.TriggerList = tlist

tuple4 = MCDecayTreeTuple("MCStrippingTuple")
tuple4.Inputs = ['/Event/AllStreams/Phys/FullDSTDiMuonJpsi2MuMuDetachedLine/Particles']
tuple4.Decay = tuple.Decay

#DaVinci().UserAlgorithms += [ tuple2 ]
#DaVinci().TupleFile = "DVNtuples.root"


# Necessary DaVinci parameters #################
DaVinci().Simulation   = True
DaVinci().SkipEvents = 0
DaVinci().EvtMax = 1000
DaVinci().Lumi = False
DaVinci().TupleFile = 'TutorialTuple.root'
DaVinci().HistogramFile = "dummy.root"
DaVinci().PrintFreq = 1000
DaVinci().DataType      = '2012'
#DaVinci().UserAlgorithms = [seq,tuple] 
DaVinci().UserAlgorithms = []
DaVinci().UserAlgorithms += [tuple, tuple2] 
DaVinci().UserAlgorithms += [tuple3, tuple4] 
DaVinci().InputType = 'DST'



from GaudiConf import IOHelper
#IOHelper().inputFiles(['/tmp/ikomarov/00024923_00000001_1.allstreams.dst'])
IOHelper().inputFiles(['/tmp/ikomarov/Turbo.dst'])
