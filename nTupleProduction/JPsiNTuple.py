# SetupProject DaVinci v35r1
import sys

from GaudiConf import IOHelper
from Configurables import LHCbApp, ApplicationMgr, DataOnDemandSvc
from Configurables import SimConf, DigiConf, DecodeRawEvent
from Configurables import CondDB, DstConf, PhysConf
from Configurables import LoKiSvc, DecayTreeTuple
from Configurables import CombineParticles, FilterDesktop
from PhysSelPython.Wrappers import Selection, AutomaticData, SelectionSequence



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
dtt.ToolList = ["TupleToolKinematic",
                "TupleToolPid"]
dtt.Decay = "J/psi(1S) -> ^mu- ^mu+"

dv.UserAlgorithms = [jpsi_seq.sequence(), dtt]
dv.TupleFile = "DVNtuples.root"

inputFiles = ["/tmp/thead/early/%i.xdst"%(n) for n in range(4)]
IOHelper('ROOT').inputFiles(inputFiles)
