# SetupProject brunel v46r1

import GaudiPython as GP
from GaudiConf import IOHelper
from Configurables import LHCbApp, ApplicationMgr, DataOnDemandSvc
from Configurables import SimConf, DigiConf, DecodeRawEvent

from LinkerInstances.eventassoc import *
MCParticle = GP.gbl.LHCb.MCParticle
Track = GP.gbl.LHCb.Track
MCHit = GP.gbl.LHCb.MCHit
Cluster = GP.gbl.LHCb.VPCluster

import sys
sys.path.append("/afs/cern.ch/user/t/thead/w/private/velo_sim/")
from velooptionsphotons import set_tags


# Configure all the unpacking, algorithms, tags and input files
appConf = ApplicationMgr()
appConf.ExtSvc+= ['ToolSvc', 'DataOnDemandSvc']
appConf.TopAlg += ["PrPixelTracking", "PrPixelStoreClusters",
                   "VPClusterLinker",
                   ]

s = SimConf()
SimConf().Detectors = ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Ecal', 'Hcal', 'Muon']
SimConf().EnableUnpack = True
SimConf().EnablePack = False

d = DigiConf()
DigiConf().Detectors = ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Ecal', 'Hcal', 'Muon']
DigiConf().EnableUnpack = True
DigiConf().EnablePack = False

dre = DecodeRawEvent()
dre.DataOnDemand = True

lhcbApp = LHCbApp()
lhcbApp.Simulation = True
set_tags()

import sys
inputFiles = [sys.argv[-1]]
IOHelper('ROOT').inputFiles(inputFiles)


def cluster2mc_particles(cluster, event):
    links = event['/Event/Link/Raw/VP/Clusters']
    refs = links.linkReference()
    mc_particles = event['MC/Particles']
    next_idx = -1
    particles = []
    for channel, key in links.keyIndex():
        if channel == cluster.channelID().channelID():
            particles.append(mc_particles.object(refs[key].objectKey()))
            next_idx = refs[key].nextIndex()
            break

    while next_idx != -1:
        particles.append(mc_particles.object(refs[next_idx].objectKey()))
        next_idx = refs[next_idx].nextIndex()

    return particles
    

# Configuration done, run time!
appMgr = GP.AppMgr()
evt = appMgr.evtsvc()

# process to the first event. To process to the next event
# you also run this command
appMgr.run(1)
# The first event is actually empty so let's go to the second one
#appMgr.run(1)

# Get a small print out of what is there in the event
evt.dump()

#for vtx in evt['/Event/MC/Vertices']:
#    if vtx.type() == GP.gbl.LHCb.MCVertex.PairProduction:
#        print vtx
