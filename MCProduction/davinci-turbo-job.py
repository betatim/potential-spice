# SetupProject DaVinci v36r0
import sys

from GaudiConf import IOHelper
from Configurables import LHCbApp, ApplicationMgr, DataOnDemandSvc
from Configurables import SimConf, DigiConf, DecodeRawEvent
from Configurables import CondDB, DaVinci
from Configurables import LoKiSvc
from DecayTreeTuple.Configuration import *
from Configurables import TupleToolTrigger
from Configurables import TupleToolTISTOS
from Configurables import TupleToolMCBackgroundInfo


def mark(idx, decay_descriptor):
    parts = decay_descriptor.split()
    parts[idx] = "^(%s)"%(parts[idx])
    return " ".join(parts)

def execute(simulation=True,
            decay_descriptor="J/psi(1S) -> mu- mu+"):
    # Configure all the unpacking, algorithms, tags and input files
    appConf = ApplicationMgr()
    appConf.ExtSvc+= ['ToolSvc', 'DataOnDemandSvc', LoKiSvc()]
    
    dv = DaVinci()
    dv.DataType = "2012"

    lhcbApp = LHCbApp()
    lhcbApp.Simulation = simulation
    CondDB().Upgrade = False
    
    dtt = DecayTreeTuple("Early2015")
    dtt.Inputs = ["/Event/Tesla/Particles"]
    # Overwriting default list of TupleTools
    dtt.ToolList = ["TupleToolKinematic",
                    "TupleToolPid",
                    "TupleToolMCBackgroundInfo",
                    "TupleToolMCTruth",
                    "MCTupleToolHierarchy",
                    "TupleToolGeometry",
                    "TupleToolTISTOS",
                    "TupleToolTrackInfo",
                    "TupleToolTrigger",
                    ]
    tlist = ["L0HadronDecision", "L0MuonDecision",
             "L0DiMuonDecision", "L0ElectronDecision",
             "L0PhotonDecision",
             "Hlt1DiMuonHighMassDecision", "Hlt1DiMuonLowMassDecision",
             "Hlt1TrackMuonDecision", "Hlt1TrackAllL0Decision",
             "Hlt2DiMuonJPsiDecision", "Hlt2SingleMuonDecision",
             ]
    
    dtt.addTool(TupleToolTrigger, name="TupleToolTrigger")
    dtt.addTool(TupleToolTISTOS, name="TupleToolTISTOS")
    # Get trigger info
    dtt.TupleToolTrigger.Verbose = True
    dtt.TupleToolTrigger.TriggerList = tlist
    dtt.TupleToolTISTOS.Verbose = True
    dtt.TupleToolTISTOS.TriggerList = tlist

    from TeslaTools import TeslaTruthUtils
    assoc_seq = TeslaTruthUtils.associateSequence("Tesla",False)
    relations = TeslaTruthUtils.getRelLoc("Tesla")
    TeslaTruthUtils.makeTruth(dtt,
                              relations,
                              ["MCTupleToolKinematic",
                               "MCTupleToolHierarchy",
                               "MCTupleToolPID" ])
    dtt.addTool(TupleToolMCBackgroundInfo, name="TupleToolMCBackgroundInfo")
    dtt.TupleToolMCBackgroundInfo.Verbose = True
    
    dtt.Decay = mark(2, mark(3, decay_descriptor)) #"J/psi(1S) -> ^mu- ^mu+"
    dtt.addBranches({"X": "^(%s)"%(decay_descriptor),
                     "muplus": mark(3, decay_descriptor),#"J/psi(1S) -> mu- ^mu+",
                     "muminus": mark(2, decay_descriptor),#"J/psi(1S) -> ^mu- mu+",
                     })
    
    x_preamble = ["DZ = VFASPF(VZ) - BPV(VZ)",
                  ]
    x_vars = {"ETA": "ETA",
              "Y": "Y",
              "PHI": "PHI",
              "VPCHI2": "VFASPF(VPCHI2)",
              "DELTAZ": "DZ",
              # DZ * M / PZ / c with c in units of mm/s
              # XXX should this be the PDG mass or measured mass?
              #"TZ": "DZ*M / PZ / 299792458000.0", #seconds
              "TZ": "DZ*3096.916 / PZ/299792458000.0*(10**12)", #ps
              "minpt": "MINTREE('mu+' == ABSID, PT)",
              "minclonedist": "MINTREE(ISBASIC & HASTRACK, CLONEDIST)",
              "maxtrchi2dof": "MAXTREE(ISBASIC & HASTRACK, TRCHI2DOF)",
              }
    muon_vars = {"ETA": "ETA",
                 "Y": "Y",
                 "PHI": "PHI",
                 "CHARGE": "Q",
                 "CLONEDIST": "CLONEDIST",
                 "TRCHI2DOF": "TRCHI2DOF",
                 }
    
    loki_X = dtt.X.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_X")
    loki_X.Variables = x_vars
    loki_X.Preambulo = x_preamble
    
    loki_mup = dtt.muplus.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_MuPlus")
    loki_mup.Variables = muon_vars
    loki_mum = dtt.muminus.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_MuMinus")
    loki_mum.Variables = muon_vars
    
    dv.UserAlgorithms = [asoc_seq, dtt]
    dv.TupleFile = "DVNtuples.root"
    
