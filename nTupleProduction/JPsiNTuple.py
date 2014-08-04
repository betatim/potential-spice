# SetupProject DaVinci v35r1
import sys

from GaudiConf import IOHelper
from Configurables import LHCbApp, ApplicationMgr, DataOnDemandSvc
from Configurables import SimConf, DigiConf, DecodeRawEvent
from Configurables import CondDB
from Configurables import LoKiSvc#, DecayTreeTuple
from Configurables import CombineParticles, FilterDesktop
from PhysSelPython.Wrappers import Selection, AutomaticData, SelectionSequence
from DecayTreeTuple.Configuration import *


# Configure all the unpacking, algorithms, tags and input files
appConf = ApplicationMgr()
appConf.ExtSvc+= ['ToolSvc', 'DataOnDemandSvc', LoKiSvc()]

from Configurables import DaVinci
dv = DaVinci()
dv.DataType = "2012"

lhcbApp = LHCbApp()
lhcbApp.Simulation = False
CondDB().Upgrade = False
# don't really need tags for looking around
#LHCbApp().DDDBtag = t['DDDB']
#LHCbApp().CondDBtag  = t['CondDB']


muons = AutomaticData(Location="Phys/StdAllLooseMuons/Particles")

jpsi = CombineParticles('MyJPsi')
jpsi.DecayDescriptors = ['J/psi(1S) -> mu- mu+']
jpsi.CombinationCut = "(AM < 7100.0 *GeV)"
jpsi.DaughtersCuts = {"": "ALL", "mu+": "ALL", "mu-": "ALL"}
jpsi.MotherCut = "(VFASPF(VCHI2/VDOF) < 999999.0)"

code = """
('J/psi(1S)' == ID) &
in_range(2.990*GeV, M, 3.210*GeV) &
DECTREE('J/psi(1S) -> mu+ mu-') &
CHILDCUT(1, HASMUON & ISMUON) &
CHILDCUT(2, HASMUON & ISMUON) &
(MINTREE('mu+' == ABSID, PT) > 700*MeV) &
(MAXTREE(ISBASIC & HASTRACK, TRCHI2DOF) < 5) &
(MINTREE(ISBASIC & HASTRACK, CLONEDIST) > 5000) &
(VFASPF(VPCHI2) > 0.5/100) &
(abs(BPV(VZ)) <  0.5*meter) &
(BPV(vrho2) < (10*mm)**2)
"""
filter_jpsi = FilterDesktop("MyFilterJPsi",
                            Code=code,
                            Preambulo=["vrho2 = VX**2 + VY**2"],
                            ReFitPVs=True)

jpsi_sel = Selection("SelMyJPsi", Algorithm=jpsi, RequiredSelections=[muons])
filter_jpsi_sel = Selection("SelFilterMyJPsi", Algorithm=filter_jpsi, RequiredSelections=[jpsi_sel])
jpsi_seq = SelectionSequence("SeqMyJPsi", TopSelection=filter_jpsi_sel)

dtt = DecayTreeTuple("Early2015")
dtt.Inputs = [jpsi_seq.outputLocation()]
# Overwriting default list of TupleTools
# XXX need to add TisTosTool with sensible lines
dtt.ToolList = ["TupleToolKinematic",
                "TupleToolPid"]
dtt.Decay = "J/psi(1S) -> ^mu- ^mu+"
dtt.addBranches({"X": "^(J/psi(1S) -> mu- mu+)",
                 "muplus": "J/psi(1S) -> mu- ^mu+",
                 "muminus": "J/psi(1S) -> ^mu- mu+",
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

dv.UserAlgorithms = [jpsi_seq.sequence(), dtt]
dv.TupleFile = "DVNtuples.root"

#inputFiles = ["/tmp/thead/early/%i.xdst"%(n) for n in range(35)]
inputFiles = ["/tmp/thead/early/%i.xdst"%(n) for n in range(5)]
IOHelper('ROOT').inputFiles(inputFiles)
