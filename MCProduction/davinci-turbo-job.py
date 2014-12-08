# SetupProject DaVinci v36r2
import sys

from GaudiConf import IOHelper
from Configurables import LHCbApp, ApplicationMgr, DataOnDemandSvc
from Configurables import SimConf, DigiConf, DecodeRawEvent
from Configurables import ConfigTarFileAccessSvc
from Configurables import CondDB, DaVinci
from Configurables import LoKiSvc
from Configurables import TupleToolTrigger
from Configurables import TupleToolTISTOS
from Configurables import TupleToolMCBackgroundInfo
from Configurables import CombineParticles, FilterDesktop
from Configurables import TrackAssociator, ChargedPP2MC
from Configurables import PatLHCbID2MCParticle
from TeslaTools import TeslaTruthUtils
        
from PhysSelPython.Wrappers import Selection, AutomaticData, SelectionSequence
from DecayTreeTuple.Configuration import *


def mark(idx, decay_descriptor):
    parts = decay_descriptor.split()
    parts[idx] = "^(%s)"%(parts[idx])
    return " ".join(parts)

def execute(simulation=True,
            turbo=True,
            decay_descriptor="J/psi(1S) -> mu- mu+"):
    # Configure all the unpacking, algorithms, tags and input files
    appConf = ApplicationMgr()
    appConf.ExtSvc+= ['ToolSvc', 'DataOnDemandSvc', LoKiSvc()]

    ConfigTarFileAccessSvc().File = 'config.tar'
    
    dv = DaVinci()
    dv.DataType = "2012"

    lhcbApp = LHCbApp()
    lhcbApp.Simulation = simulation
    CondDB().Upgrade = False
    
    dtt = DecayTreeTuple("Early2015")
    if turbo:
        tesla_prefix = "Hlt2DiMuonJPsi"
        dtt.Inputs = ["/Event/"+tesla_prefix+"/Particles"]
        dtt.InputPrimaryVertices = "/Event/"+tesla_prefix+"/Primary"
        dtt.WriteP2PVRelations = False

    else:
        LHCbApp().DDDBtag = "dddb-20140729"
        polarity = "u"
        LHCbApp().CondDBtag = "sim-20140730-vc-m%s100"%polarity
        muons = AutomaticData(Location="Phys/StdAllLooseMuons/Particles")

        jpsi = CombineParticles('MyJPsi')
        jpsi.DecayDescriptors = [decay_descriptor]
        jpsi.CombinationCut = "(AM < 7100.0 *GeV)"
        jpsi.DaughtersCuts = {"": "ALL", "mu+": "ALL", "mu-": "ALL"}
        jpsi.MotherCut = "(VFASPF(VCHI2/VDOF) < 999999.0)"
        
        code = """
('J/psi(1S)' == ID) &
in_range(2.990*GeV, M, 3.210*GeV) &
DECTREE('%s') &
CHILDCUT(1, HASMUON & ISMUON) &
CHILDCUT(2, HASMUON & ISMUON) &
(MINTREE('mu+' == ABSID, PT) > 700*MeV) &
(MAXTREE(ISBASIC & HASTRACK, TRCHI2DOF) < 5) &
(MINTREE(ISBASIC & HASTRACK, CLONEDIST) > 5000) &
(VFASPF(VPCHI2) > 0.5/100) &
(abs(BPV(VZ)) <  0.5*meter) &
(BPV(vrho2) < (10*mm)**2)
"""%(decay_descriptor)
        # similar to the HLT2 line
        code = """
(ADMASS('J/psi(1S)')< 120*MeV) &
DECTREE('%s') &
(PT>0*MeV) &
(MAXTREE('mu-'==ABSID,TRCHI2DOF) < 4) &
(MINTREE('mu-'==ABSID,PT)> 0*MeV) &
(VFASPF(VCHI2PDOF)< 25)
"""%(decay_descriptor)
        filter_jpsi = FilterDesktop("MyFilterJPsi",
                                    Code=code,
                                    Preambulo=["vrho2 = VX**2 + VY**2"],
                                    ReFitPVs=True,
                                    #IgnoreP2PVFromInputLocations=True,
                                    #WriteP2PVRelations=True
                                    )
        
        jpsi_sel = Selection("SelMyJPsi", Algorithm=jpsi, RequiredSelections=[muons])
        filter_jpsi_sel = Selection("SelFilterMyJPsi",
                                    Algorithm=filter_jpsi,
                                    RequiredSelections=[jpsi_sel])
        jpsi_seq = SelectionSequence("SeqMyJPsi", TopSelection=filter_jpsi_sel)
        dtt.Inputs = [jpsi_seq.outputLocation()]
    
    # Overwriting default list of TupleTools
    dtt.ToolList = ["TupleToolKinematic",
                    "TupleToolPid",
                    "TupleToolEventInfo",
                    "TupleToolMCBackgroundInfo",
                    "TupleToolMCTruth",
                    #"MCTupleToolHierarchy",
                    #"MCTupleToolPID",
                    "TupleToolGeometry",
                    "TupleToolTISTOS",
                    # with turbo this crashes
                    #"TupleToolTrackInfo",
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

    from Configurables import TupleToolMCTruth, MCTupleToolHierarchy
    dtt.addTool(TupleToolMCBackgroundInfo,
                name="TupleToolMCBackgroundInfo")
    dtt.TupleToolMCBackgroundInfo.Verbose = True
    dtt.addTool(MCTupleToolHierarchy,
                name="MCTupleToolHierarchy")
    dtt.MCTupleToolHierarchy.Verbose = True
    dtt.addTool(TupleToolMCTruth,
                name="TupleToolMCTruth")
    dtt.TupleToolMCTruth.Verbose = True

    if turbo:
        assoc_seq = TeslaTruthUtils.associateSequence(tesla_prefix, False)
        ChargedPP2MC(tesla_prefix+"ProtoAssocPP").OutputLevel = 1
        
        assoc_seq.Members.insert(0, PatLHCbID2MCParticle())

        from Configurables import MuonCoord2MCParticleLink
        muon_coords = MuonCoord2MCParticleLink("TeslaMuonCoordLinker")
        assoc_seq.Members.insert(1, muon_coords)
    
        TrackAssociator("TeslaAssocTr").DecideUsingMuons = True
        
        relations = TeslaTruthUtils.getRelLoc(tesla_prefix)

    else:
        relations = "Relations/Rec/ProtoP/Charged"


    TeslaTruthUtils.makeTruth(dtt,
                              relations,
                              ["MCTupleToolKinematic",
                               "MCTupleToolHierarchy",
                               "MCTupleToolPID",
                               ]
                              )
    
    
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
    #dtt.muplus.addTupleTool("TupleToolGeometry")
    
    loki_mum = dtt.muminus.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_MuMinus")
    loki_mum.Variables = muon_vars
    #dtt.muminus.addTupleTool("TupleToolGeometry")
    
    dv.TupleFile = "DVNtuples.root"
    if turbo:
        dv.UserAlgorithms = [assoc_seq, dtt]

    else:
        assocpp = ChargedPP2MC("TimsChargedPP2MC")
        assocpp.OutputLevel = 1
        dv.UserAlgorithms = [jpsi_seq.sequence(), assocpp, dtt]

#import GaudiPython as GP
#inputFiles = ["/tmp/thead/EarlyEvents-Extended-L0-Turbo.xdst"]
#IOHelper('ROOT').inputFiles(inputFiles) 
#execute()
