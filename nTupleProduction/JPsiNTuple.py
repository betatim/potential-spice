# SetupProject DaVinci v35r1
import sys

import GaudiPython as GP
from GaudiConf import IOHelper
from Configurables import LHCbApp, ApplicationMgr, DataOnDemandSvc
from Configurables import SimConf, DigiConf, DecodeRawEvent
from Configurables import CondDB, DstConf, PhysConf
from Configurables import LoKiSvc, DecayTreeTuple
from Configurables import CombineParticles, FilterDesktop
from PhysSelPython.Wrappers import Selection, AutomaticData, SelectionSequence


# Some name shortcuts
MCParticle = GP.gbl.LHCb.MCParticle
Particle = GP.gbl.LHCb.Particle
Track = GP.gbl.LHCb.Track
MCHit = GP.gbl.LHCb.MCHit


def nodes(evt, node=None):
    nodenames = []
    
    if node is None:
        root = evt.retrieveObject('')
        node = root.registry()

    if node.object():
        nodenames.append(node.identifier())
        for l in evt.leaves(node):
            # skip a location that takes forever to load
            # XXX How to detect these automatically??
            if "Swum" in l.identifier():
                continue
            
            temp = evt[l.identifier()]
            nodenames += nodes(evt, l)
                    
    else:
        nodenames.append(node.identifier())

    return nodenames

def advance(decision='B02DKWSD2HHHBeauty2CharmLine'):
    """Advance until stripping decision is true, returns
    number of events by which we advanced"""
    n = 0
    while True:
        appMgr.run(1)
        n += 1
        dec=evt['/Event/Strip/Phys/DecReports']
        if dec.hasDecisionName("Stripping%sDecision"%decision):
            break

    return n


# Configure all the unpacking, algorithms, tags and input files
appConf = ApplicationMgr()
appConf.ExtSvc+= ['ToolSvc', 'DataOnDemandSvc', LoKiSvc()]

# Seems like you can either use {Sim,Digi,DST}Conf
# together or use DaVinci to get them all in one go
#s = SimConf()
#SimConf().EnableUnpack = True
#SimConf().EnablePack = False

#d = DigiConf()
#DigiConf().EnableUnpack = True
#DigiConf().EnablePack = False

#dst = DstConf()
#dst.EnableUnpack = ["Reconstruction", "Stripping"]
#dst.DataType = "2012"

from Configurables import DaVinci
dv = DaVinci()
dv.DataType = "2012"


# Not sure what PhysConf does, doesn't seem needed
#phys = PhysConf()
#phys.EnableUnpack = ["Reconstruction", "Stripping"]
#phys.DataType = "2012"

# disable for older versions of DV
# generally it seems in older versions of DV
# this whole script 'breaks' at places
# raising exceptions and yet works ...
dre = DecodeRawEvent()
dre.DataOnDemand = True

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
#in_range(2.990*GeV, M, 3.210*GeV) &
DECTREE('J/psi(1S) -> mu+ mu-') &
#CHILDCUT(1, HASMUON & ISMUON) &
#CHILDCUT(2, HASMUON & ISMUON) &
#(MINTREE('mu+' == ABSID, PT) > 700*MeV) &
#(MAXTREE(ISBASIC & HASTRACK, TRCHI2DOF) < 5) &
#(MINTREE(ISBASIC & HASTRACK, CLONEDIST) > 5000) &
#(VFASPF(VPCHI2) > 0.5/100) &
#(abs(BPV(VZ)) <  0.5*meter) &
#(BPV(vrho2) < (10*mm)**2)
"""
#jpsi = FilterDesktop("MyJPsi",
#                     Code=code,
#                     Preambulo=["vrho2 = VX**2 + VY**2"],
#                     ReFitPVs=True)

jpsi_sel = Selection("SelMyJPsi", Algorithm=jpsi, RequiredSelections=[muons])
jpsi_seq = SelectionSequence("SeqMyJPsi", TopSelection=jpsi_sel)

dtt = DecayTreeTuple()
dtt.Inputs = [jpsi_seq.outputLocation()]
dtt.ToolList = ["TupleToolKinematic", "TupleToolPid"]
dtt.Decay = "J/psi(1S) -> mu- mu+"

dv.UserAlgorithms = [jpsi_seq.sequence(), dtt]
dv.TupleFile = "DVNtuples.root"

inputFiles = [sys.argv[-1]]
IOHelper('ROOT').inputFiles(inputFiles)
    

# Configuration done, run time!
appMgr = GP.AppMgr()
evt = appMgr.evtsvc()

print_decay = appMgr.toolsvc().create('PrintDecayTreeTool', interface="IPrintDecayTreeTool")

# New style decay descriptors, also known as LoKi decays
loki_decay_finder = appMgr.toolsvc().create('LoKi::Decay', interface="Decays::IDecay")
# Old style decay descriptors
old_decay_finder = appMgr.toolsvc().create("DecayFinder", interface="IDecayFinder")

# works
#decay_desc = "[[B0]cc -> (^D- => {^K- ^K+ ^pi-, ^K- ^pi+ ^pi-,^pi+ ^pi- ^pi-, ^K- ^K- ^pi+}) ^K-]cc"
# doesn't work
decay_desc = "[[B0]cc -> (^D- => {^K- ^K+ ^pi-, ^K- ^pi+ ^pi-,^pi+ ^pi- ^pi-}) ^K-]cc"
old_decay_finder.setDecay(decay_desc)

# process first event
appMgr.run(1)

# Get a small print out of what is there in the event
evt.dump()

# print out "all" TES locations
# prints out packed locations, so you need to know
# what the unpacked location is called to actually access it
print "-"*80
for node in nodes(evt):
    print node

